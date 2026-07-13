import json
import math
import os
import re
import secrets
import shutil
import socket
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from base64 import b64decode, b64encode
from hashlib import sha1
from hmac import new as hmac_new
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from flask import Flask, Response, abort, jsonify, redirect, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PREVIEW_DIR = BASE_DIR / "previews"
DB_PATH = DATA_DIR / "blog_core.sqlite3"
PORT = int(os.environ.get("PORT", "3299"))
ADMIN_HOSTS = {h.strip().lower() for h in os.environ.get("ADMIN_HOSTS", "blog.yas.ooo,127.0.0.1,localhost").split(",") if h.strip()}
CNAME_TARGET = os.environ.get("CNAME_TARGET", "blog.yas.ooo").strip().lower()
EXPECTED_HOSTED_IPS = {ip.strip() for ip in os.environ.get("HOSTED_BLOG_IPS", "72.61.1.109").split(",") if ip.strip()}
ZERNIO_API_BASE = os.environ.get("ZERNIO_API_BASE", "https://zernio.com/api/v1").rstrip("/")
BLOG_CORE_PUBLIC_URL = os.environ.get("BLOG_CORE_PUBLIC_URL", "https://blog.yas.ooo").rstrip("/")
LEGACY_FACTORY_ENDPOINTS = {
    "content-factory-airep24": os.environ.get("LEGACY_FACTORY_AIREP24_URL", "http://127.0.0.1:12631").rstrip("/"),
    "content-factory-yaswine": os.environ.get("LEGACY_FACTORY_YASWINE_URL", "http://127.0.0.1:3199").rstrip("/"),
    "content-factory-solocruz": os.environ.get("LEGACY_FACTORY_SOLOCRUZ_URL", "http://127.0.0.1:12838").rstrip("/"),
    "content-factory-laycanmatch": os.environ.get("LEGACY_FACTORY_LAYCANMATCH_URL", "http://127.0.0.1:13157").rstrip("/"),
}
LEGACY_STATUS_CHECKS = {}
LINKEDIN_OAUTH_STATES = {}

app = Flask(__name__)
DATA_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)
SOCIAL_ASSET_DIR = DATA_DIR / "social_assets"
SOCIAL_ASSET_DIR.mkdir(exist_ok=True)
ARTICLE_ASSET_DIR = DATA_DIR / "article_assets"
ARTICLE_ASSET_DIR.mkdir(exist_ok=True)
PODCAST_ASSET_DIR = DATA_DIR / "podcast_assets"
PODCAST_ASSET_DIR.mkdir(exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.executescript(
            """
            create table if not exists sites (
                id integer primary key autoincrement,
                domain text not null unique,
                homepage_url text not null,
                access_type text not null default 'local_path',
                root_path text,
                blog_path text default '/blog/',
                languages text default '["en"]',
                brand_name text,
                content_context text,
                created_at text not null,
                updated_at text not null
            );
            create table if not exists site_theme_profiles (
                site_id integer primary key,
                title text,
                description text,
                colors_json text not null default '[]',
                fonts_json text not null default '[]',
                css_urls_json text not null default '[]',
                head_css text,
                header_html text,
                footer_html text,
                body_class text,
                scanned_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists blog_templates (
                site_id integer primary key,
                preview_path text not null,
                template_html text not null,
                css text not null,
                created_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists publish_jobs (
                id integer primary key autoincrement,
                site_id integer not null,
                kind text not null,
                status text not null,
                message text,
                created_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            """
        )
        try:
            conn.execute("alter table site_theme_profiles add column head_css text")
        except sqlite3.OperationalError:
            pass
        for statement in (
            "alter table sites add column factory_enabled integer not null default 0",
            "alter table sites add column publishing_cadence text not null default 'manual'",
            "alter table sites add column topic_strategy text",
            "alter table sites add column custom_blog_domain text",
            "alter table sites add column hosted_blog_enabled integer not null default 0",
            "alter table sites add column cname_status text not null default 'not_configured'",
            "alter table sites add column cname_checked_at text",
        ):
            try:
                conn.execute(statement)
            except sqlite3.OperationalError:
                pass
        conn.execute("create unique index if not exists idx_sites_custom_blog_domain on sites(custom_blog_domain) where custom_blog_domain is not null and custom_blog_domain <> ''")
        conn.executescript(
            """
            create table if not exists content_jobs (
                id text primary key,
                site_id integer not null,
                topic text not null,
                slug text,
                status text not null,
                title text,
                description text,
                category text,
                hero_image text,
                draft_html text,
                faq_json text,
                error text,
                sources_json text,
                visibility text not null default 'public',
                published_url text,
                product_mode integer not null default 0,
                engagement_mode integer not null default 0,
                lead_magnet_mode integer not null default 0,
                linkedin_status text,
                linkedin_post_url text,
                linkedin_posted_at text,
                linkedin_error text,
                telegram_status text,
                telegram_post_url text,
                telegram_posted_at text,
                telegram_error text,
                twitter_status text,
                twitter_post_url text,
                twitter_posted_at text,
                twitter_error text,
                tumblr_status text,
                tumblr_post_url text,
                tumblr_posted_at text,
                tumblr_error text,
                pinterest_status text,
                pinterest_post_url text,
                pinterest_posted_at text,
                pinterest_error text,
                instagram_status text,
                instagram_post_url text,
                instagram_posted_at text,
                instagram_error text,
                threads_status text,
                threads_post_url text,
                threads_posted_at text,
                threads_error text,
                reddit_status text,
                reddit_post_url text,
                reddit_posted_at text,
                reddit_error text,
                created_at text not null,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists content_jobs_site_status_created_idx on content_jobs(site_id,status,created_at);
            create table if not exists content_job_logs (
                id integer primary key autoincrement,
                site_id integer not null,
                job_id text not null,
                ts text not null,
                level text not null,
                step text not null,
                message text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists content_job_logs_site_job_ts_idx on content_job_logs(site_id,job_id,ts);
            create table if not exists source_scanner_drafts (
                scanner_article_id text primary key,
                site_id integer not null,
                job_id text not null unique,
                received_at text not null,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade,
                foreign key(job_id) references content_jobs(id) on delete cascade
            );
            create index if not exists source_scanner_drafts_site_job_idx on source_scanner_drafts(site_id,job_id);
            create table if not exists social_connections (
                site_id integer not null,
                provider text not null,
                status text not null default 'disconnected',
                display_name text,
                credentials_json text,
                settings_json text,
                connected_at text,
                updated_at text not null,
                primary key(site_id, provider),
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists social_posts (
                id integer primary key autoincrement,
                site_id integer not null,
                job_id text not null,
                channel text not null,
                content_text text,
                content_json text,
                remote_url text,
                status text not null,
                language text,
                max_chars integer,
                char_count integer,
                include_link integer not null default 0,
                validation_json text,
                created_at text not null,
                updated_at text,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists social_posts_site_job_channel_idx on social_posts(site_id,job_id,channel,created_at);
            create table if not exists autopublish_settings (
                site_id integer primary key,
                enabled integer not null default 0,
                times_per_day integer not null default 3,
                channels_json text not null default '["linkedin","telegram","twitter","tumblr","pinterest","instagram","threads","reddit"]',
                timezone text not null default 'UTC',
                start_hour integer not null default 9,
                end_hour integer not null default 21,
                linkedin_include_link integer not null default 0,
                telegram_include_link integer not null default 0,
                twitter_include_link integer not null default 0,
                tumblr_include_link integer not null default 0,
                pinterest_include_link integer not null default 0,
                instagram_include_link integer not null default 0,
                threads_include_link integer not null default 0,
                reddit_include_link integer not null default 0,
                last_slot_key text,
                last_run_at text,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists autopublish_runs (
                id integer primary key autoincrement,
                site_id integer not null,
                started_at text not null,
                finished_at text,
                trigger text not null,
                job_id text,
                status text not null,
                result_json text,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists autopublish_runs_site_started_idx on autopublish_runs(site_id,started_at);
            create table if not exists topic_discovery_settings (
                site_id integer primary key,
                enabled integer not null default 0,
                timezone text not null default 'UTC',
                run_hour integer not null default 6,
                direction text,
                category_hint text,
                per_run_limit integer not null default 15,
                min_score real not null default 55.0,
                top_n integer not null default 3,
                product_mode integer not null default 0,
                engagement_mode integer not null default 0,
                lead_magnet_mode integer not null default 0,
                last_run_key text,
                last_run_at text,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists topic_discovery_runs (
                id integer primary key autoincrement,
                site_id integer not null,
                started_at text not null,
                finished_at text,
                trigger text not null,
                direction text,
                status text not null,
                found_count integer not null default 0,
                queued_count integer not null default 0,
                result_json text,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists topic_discovery_runs_site_started_idx on topic_discovery_runs(site_id,started_at);
            create table if not exists podcast_settings (
                site_id integer primary key,
                enabled integer not null default 0,
                host_name text,
                voice_name text not null default 'Kore',
                voice_direction text,
                target_minutes integer not null default 8,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists podcast_episodes (
                id text primary key,
                site_id integer not null,
                job_id text not null,
                status text not null default 'DRAFT',
                title text not null,
                description text,
                language text not null default 'en',
                script_text text,
                audio_filename text,
                duration_seconds integer,
                published_url text,
                error text,
                created_at text not null,
                updated_at text not null,
                published_at text,
                foreign key(site_id) references sites(id) on delete cascade,
                foreign key(job_id) references content_jobs(id) on delete cascade
            );
            create index if not exists podcast_episodes_site_created_idx on podcast_episodes(site_id,created_at desc);
            create index if not exists podcast_episodes_site_job_idx on podcast_episodes(site_id,job_id);
            """
        )
        for statement in (
            "alter table social_posts add column language text",
            "alter table social_posts add column max_chars integer",
            "alter table social_posts add column char_count integer",
            "alter table social_posts add column include_link integer not null default 0",
            "alter table social_posts add column validation_json text",
            "alter table social_posts add column updated_at text",
            "alter table content_jobs add column pinterest_status text",
            "alter table content_jobs add column pinterest_post_url text",
            "alter table content_jobs add column pinterest_posted_at text",
            "alter table content_jobs add column pinterest_error text",
            "alter table content_jobs add column instagram_status text",
            "alter table content_jobs add column instagram_post_url text",
            "alter table content_jobs add column instagram_posted_at text",
            "alter table content_jobs add column instagram_error text",
            "alter table content_jobs add column threads_status text",
            "alter table content_jobs add column threads_post_url text",
            "alter table content_jobs add column threads_posted_at text",
            "alter table content_jobs add column threads_error text",
            "alter table content_jobs add column reddit_status text",
            "alter table content_jobs add column reddit_post_url text",
            "alter table content_jobs add column reddit_posted_at text",
            "alter table content_jobs add column reddit_error text",
            "alter table autopublish_settings add column pinterest_include_link integer not null default 0",
            "alter table autopublish_settings add column instagram_include_link integer not null default 0",
            "alter table autopublish_settings add column threads_include_link integer not null default 0",
            "alter table autopublish_settings add column reddit_include_link integer not null default 0",
        ):
            try:
                conn.execute(statement)
            except sqlite3.OperationalError:
                pass
        for site_row in conn.execute("select id from sites").fetchall():
            sid = site_row[0]
            conn.execute(
                """
                insert into autopublish_settings(site_id, updated_at)
                values(?, ?)
                on conflict(site_id) do nothing
                """,
                (sid, now_iso()),
            )
            conn.execute(
                """
                insert into topic_discovery_settings(site_id, direction, updated_at)
                values(?, (select coalesce(topic_strategy, content_context, domain) from sites where id=?), ?)
                on conflict(site_id) do nothing
                """,
                (sid, sid, now_iso()),
            )
            conn.execute(
                """insert into podcast_settings(site_id, host_name, updated_at) values(?,?,?)
                   on conflict(site_id) do nothing""",
                (sid, "", now_iso()),
            )



class ExistingArticleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.og_image = ""
        self.links = []
        self._in_title = False
        self._capture_tag = None
        self._capture_depth = 0
        self._capture_chunks = []
        self.article_html = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description":
                self.description = attrs_dict.get("content", "")[:320]
            if prop in {"og:image", "twitter:image"} and not self.og_image:
                self.og_image = attrs_dict.get("content", "")[:900]
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            if "canonical" in rel and href:
                self.canonical = href[:900]
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                self.links.append(href[:900])
        if self._capture_tag is None and tag in {"article", "main"}:
            self._capture_tag = tag
            self._capture_depth = 0
            self._capture_chunks = []
        if self._capture_tag:
            self._capture_depth += 1
            self._capture_chunks.append(self._format_start(tag, attrs))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self._capture_tag:
            self._capture_chunks.append(f"</{tag}>")
            self._capture_depth -= 1
            if self._capture_depth == 0:
                html = "".join(self._capture_chunks)
                if not self.article_html:
                    self.article_html = html
                self._capture_tag = None
                self._capture_chunks = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._capture_tag:
            self._capture_chunks.append(escape(data))

    def handle_entityref(self, name):
        if self._capture_tag:
            self._capture_chunks.append(f"&{name};")

    def handle_charref(self, name):
        if self._capture_tag:
            self._capture_chunks.append(f"&#{name};")

    def _format_start(self, tag, attrs):
        rendered = []
        for key, value in attrs:
            if value is None:
                rendered.append(escape(key))
            else:
                rendered.append(f'{escape(key)}="{escape(value, quote=True)}"')
        return "<" + tag + (" " + " ".join(rendered) if rendered else "") + ">"

class HeadBodyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.title = ""
        self.description = ""
        self.css_urls = []
        self.body_class = ""
        self.head_styles = []
        self._in_title = False
        self._in_style = False
        self._capture = None
        self._depth = 0
        self._chunks = []
        self.nav_html = ""
        self.header_html = ""
        self.footer_html = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "style":
            self._in_style = True
        if tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "")[:300]
        if tag == "link" and attrs_dict.get("rel") and "stylesheet" in str(attrs_dict.get("rel")):
            href = attrs_dict.get("href")
            if href:
                self.css_urls.append(href)
        if tag == "body":
            self.body_class = attrs_dict.get("class", "")
        if tag in ("nav", "header", "footer") and self._capture is None:
            self._capture = tag
            self._depth = 0
            self._chunks = []
        if self._capture:
            self._depth += 1
            self._chunks.append(self._format_start(tag, attrs))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "style":
            self._in_style = False
        if self._capture:
            self._chunks.append(f"</{tag}>")
            self._depth -= 1
            if self._depth == 0:
                html = "".join(self._chunks)
                if self._capture == "nav" and not self.nav_html:
                    self.nav_html = html
                if self._capture == "header" and not self.header_html:
                    self.header_html = html
                if self._capture == "footer" and not self.footer_html:
                    self.footer_html = html
                self._capture = None
                self._chunks = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_style:
            self.head_styles.append(data)
        if self._capture:
            self._chunks.append(escape(data))

    def handle_entityref(self, name):
        if self._capture:
            self._chunks.append(f"&{name};")

    def handle_charref(self, name):
        if self._capture:
            self._chunks.append(f"&#{name};")

    def _format_start(self, tag, attrs):
        rendered = []
        for key, value in attrs:
            if value is None:
                rendered.append(escape(key))
            else:
                rendered.append(f'{escape(key)}="{escape(value, quote=True)}"')
        return "<" + tag + (" " + " ".join(rendered) if rendered else "") + ">"


def normalize_url(url):
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/") + "/"


def clean_host(value):
    host = (value or "").strip().lower()
    host = re.sub(r"^https?://", "", host)
    host = host.split("/")[0].split(":")[0].strip()
    return host.rstrip(".")


def request_host():
    return clean_host(request.headers.get("Host") or "")


def is_admin_host(host):
    return host in ADMIN_HOSTS or host.endswith(".localhost")


def resolve_host_ips(host):
    if not host:
        return []
    try:
        return sorted({item[4][0] for item in socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)})
    except OSError:
        return []


def check_cname_status(custom_domain):
    host = clean_host(custom_domain)
    if not host:
        return {"status": "not_configured", "ips": [], "expected_ips": sorted(EXPECTED_HOSTED_IPS), "target": CNAME_TARGET}
    ips = resolve_host_ips(host)
    target_ips = resolve_host_ips(CNAME_TARGET)
    allowed = EXPECTED_HOSTED_IPS or set(target_ips)
    if ips and allowed.intersection(ips):
        status = "active"
    elif ips:
        status = "wrong_target"
    else:
        status = "dns_pending"
    return {"status": status, "ips": ips, "target_ips": target_ips, "expected_ips": sorted(allowed), "target": CNAME_TARGET}


def domain_from_url(url):
    return urllib.parse.urlparse(url).netloc.lower().replace("www.", "")


def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "YASBlogCore/0.1 (+https://blog.yas.ooo)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        raw = resp.read(900000)
        return raw.decode(charset, errors="replace"), dict(resp.headers)


def fetch_json_request(url, headers=None, data=None, method="GET", timeout=25):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request_headers = {"User-Agent": "YASBlogCore/0.1 (+https://blog.yas.ooo)", **(headers or {})}
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(300000).decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw[:500]}
        return parsed, resp.status


def fetch_form_json_request(url, fields, headers=None, timeout=25):
    body = urllib.parse.urlencode(fields).encode("utf-8")
    request_headers = {
        "User-Agent": "YASBlogCore/0.1 (+https://blog.yas.ooo)",
        "Content-Type": "application/x-www-form-urlencoded",
        **(headers or {}),
    }
    req = urllib.request.Request(url, data=body, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(300000).decode("utf-8", errors="replace")
        try:
            return json.loads(raw), resp.status
        except Exception:
            return {"raw": raw[:500]}, resp.status


def linkedin_oauth_configured():
    return bool(os.environ.get("LINKEDIN_CLIENT_ID") and os.environ.get("LINKEDIN_CLIENT_SECRET"))


def linkedin_oauth_redirect_uri():
    return os.environ.get("LINKEDIN_OAUTH_REDIRECT_URI", "https://blog.yas.ooo/oauth/linkedin/callback").strip()


def oauth1_header(method, url, consumer_key, consumer_secret, token, token_secret, params=None):
    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(12),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(datetime.now(timezone.utc).timestamp())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }
    all_params = {**(params or {}), **oauth_params}
    encoded_pairs = []
    for key, value in sorted(all_params.items()):
        encoded_pairs.append(f"{urllib.parse.quote(str(key), safe='')}={urllib.parse.quote(str(value), safe='')}")
    param_string = "&".join(encoded_pairs)
    base = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=""),
        urllib.parse.quote(param_string, safe=""),
    ])
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    signature = b64encode(hmac_new(signing_key.encode("utf-8"), base.encode("utf-8"), sha1).digest()).decode("ascii")
    oauth_params["oauth_signature"] = signature
    header_value = ", ".join(f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items()))
    return "OAuth " + header_value


def test_social_connection(provider, credentials):
    if not social_credentials_complete(provider, credentials):
        return {"ok": False, "status": "disconnected", "message": "Missing required credentials."}
    try:
        if provider == "zernio":
            api_key = str(credentials.get("api_key") or os.environ.get("ZERNIO_API_KEY") or "").strip()
            data, _ = fetch_json_request(
                f"{ZERNIO_API_BASE}/accounts",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            accounts = data.get("accounts") if isinstance(data, dict) else None
            if not isinstance(accounts, list):
                return {"ok": False, "status": "failed", "message": data.get("message") or data.get("error") or "Zernio account lookup failed."}
            configured = [channel for channel in ZERNIO_SOCIAL_CHANNELS if credentials.get(f"{channel}_account_id")]
            return {
                "ok": True,
                "status": "connected",
                "displayName": f"Zernio: {len(accounts)} connected account(s)",
                "message": f"Zernio connected. {len(accounts)} account(s) available; mapped channels: {', '.join(sorted(configured)) or 'none'}.",
            }

        if provider == "telegram":
            token = credentials["bot_token"]
            chat_id = credentials["chat_id"]
            bot, _ = fetch_json_request(f"https://api.telegram.org/bot{urllib.parse.quote(token, safe=':')}/getMe")
            if not bot.get("ok"):
                return {"ok": False, "status": "failed", "message": bot.get("description") or "Telegram bot token rejected."}
            chat, _ = fetch_json_request(f"https://api.telegram.org/bot{urllib.parse.quote(token, safe=':')}/getChat?chat_id={urllib.parse.quote(str(chat_id))}")
            if not chat.get("ok"):
                return {"ok": False, "status": "failed", "message": chat.get("description") or "Telegram chat is not reachable."}
            username = bot.get("result", {}).get("username") or bot.get("result", {}).get("first_name") or "Telegram bot"
            return {"ok": True, "status": "connected", "displayName": username, "message": f"Connected to Telegram as {username}."}

        if provider == "linkedin":
            data, _ = fetch_json_request("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {credentials['access_token']}"})
            name = data.get("name") or data.get("localizedFirstName") or data.get("sub") or "LinkedIn account"
            if data.get("serviceErrorCode") or data.get("status") in {401, 403}:
                return {"ok": False, "status": "failed", "message": data.get("message") or "LinkedIn token rejected."}
            return {"ok": True, "status": "connected", "displayName": name, "message": f"Connected to LinkedIn as {name}."}

        if provider == "twitter":
            data, _ = fetch_json_request("https://api.twitter.com/2/users/me", headers={"Authorization": f"Bearer {credentials['bearer_token']}"})
            user = data.get("data") or {}
            if not user:
                return {"ok": False, "status": "failed", "message": data.get("detail") or data.get("title") or "X / Twitter token rejected."}
            name = user.get("username") or user.get("name") or "X account"
            return {"ok": True, "status": "connected", "displayName": name, "message": f"Connected to X / Twitter as {name}."}

        if provider == "tumblr":
            url = "https://api.tumblr.com/v2/user/info"
            auth = oauth1_header(
                "GET",
                url,
                credentials["consumer_key"],
                credentials["consumer_secret"],
                credentials["oauth_token"],
                credentials["oauth_token_secret"],
            )
            data, _ = fetch_json_request(url, headers={"Authorization": auth})
            user = (data.get("response") or {}).get("user") or {}
            name = user.get("name") or credentials.get("blog_hostname") or "Tumblr account"
            if not user:
                return {"ok": False, "status": "failed", "message": (data.get("meta") or {}).get("msg") or "Tumblr credentials rejected."}
            return {"ok": True, "status": "connected", "displayName": name, "message": f"Connected to Tumblr as {name}."}

        if provider == "pinterest":
            data, _ = fetch_json_request("https://api.pinterest.com/v5/user_account", headers={"Authorization": f"Bearer {credentials['access_token']}"})
            username = data.get("username") or data.get("account_type") or "Pinterest account"
            if data.get("code") or data.get("message") and not data.get("username"):
                return {"ok": False, "status": "failed", "message": data.get("message") or "Pinterest token rejected."}
            return {"ok": True, "status": "connected", "displayName": username, "message": f"Connected to Pinterest as {username}."}

        if provider == "instagram":
            return {
                "ok": True,
                "status": "configured",
                "displayName": credentials.get("instagram_profile") or "Instagram intermediary",
                "message": "Instagram intermediary credentials are saved. Full publish test requires the intermediary API contract.",
            }

        if provider == "threads":
            params = urllib.parse.urlencode({"fields": "id,username", "access_token": credentials["access_token"]})
            data, _ = fetch_json_request(f"https://graph.threads.net/v1.0/me?{params}")
            username = data.get("username") or data.get("id") or "Threads account"
            if data.get("error"):
                return {"ok": False, "status": "failed", "message": (data.get("error") or {}).get("message") or "Threads token rejected."}
            return {"ok": True, "status": "connected", "displayName": username, "message": f"Connected to Threads as {username}."}
    except urllib.error.HTTPError as e:
        detail = e.read(500).decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        return {"ok": False, "status": "failed", "message": f"HTTP {e.code}: {detail[:220]}"}
    except Exception as e:
        return {"ok": False, "status": "failed", "message": str(e)[:260]}
    return {"ok": False, "status": "failed", "message": "Unsupported provider."}


def absolutize(base, maybe_url):
    return urllib.parse.urljoin(base, maybe_url)


def absolutize_html_attrs(base, html):
    if not html:
        return ""

    def replace_attr(match):
        attr, quote, value = match.group(1), match.group(2), match.group(3)
        clean = value.strip()
        lower = clean.lower()
        if not clean or lower.startswith(("http://", "https://", "//", "#", "mailto:", "tel:", "javascript:", "data:")):
            return match.group(0)
        return f'{attr}={quote}{escape(absolutize(base, clean), quote=True)}{quote}'

    return re.sub(r"\b(src|href|poster|action)=(['\"])(.*?)\2", replace_attr, html, flags=re.I)


def choose_site_chrome_header(parser):
    candidate = parser.nav_html or parser.header_html
    if not candidate:
        return ""
    lower = candidate.lower()
    if 'class="hero' in lower or "class='hero" in lower or "<h1" in lower:
        return ""
    return candidate


def extract_theme(homepage_url):
    html, headers = fetch_url(homepage_url)
    parser = HeadBodyParser()
    parser.feed(html)
    colors = []
    fonts = []
    for color in re.findall(r"#[0-9a-fA-F]{3,8}|rgba?\([^\)]+\)", html):
        if color not in colors:
            colors.append(color)
        if len(colors) >= 16:
            break
    for font in re.findall(r"font-family\s*:\s*([^;}{]+)", html, flags=re.I):
        clean = re.sub(r"[\"']", "", font).strip()
        if clean and clean not in fonts:
            fonts.append(clean[:120])
        if len(fonts) >= 8:
            break
    css_urls = [absolutize(homepage_url, u) for u in parser.css_urls[:12]]
    return {
        "title": parser.title.strip()[:180],
        "description": parser.description.strip(),
        "colors": colors,
        "fonts": fonts,
        "css_urls": css_urls,
        "head_css": "\n".join(parser.head_styles)[:200000],
        "header_html": absolutize_html_attrs(homepage_url, choose_site_chrome_header(parser))[:50000],
        "footer_html": absolutize_html_attrs(homepage_url, parser.footer_html)[:50000],
        "body_class": parser.body_class[:300],
        "headers": headers,
        "html_bytes": len(html.encode("utf-8", errors="ignore")),
    }


def strip_html_text(html, limit=1400):
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html or "")
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def clean_inferred_text(value, limit=180):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = text.strip(" .;:-")
    return text[:limit]


def fallback_site_topic_profile(site, theme):
    brand = site["brand_name"] or site["domain"]
    title = clean_inferred_text(theme.get("title") or brand, 120)
    description = clean_inferred_text(theme.get("description") or "", 220)
    combined = f"{brand} {title} {description}".lower()
    if any(word in combined for word in ("wine", "winery", "wineries", "sommelier", "grape", "champagne", "bordeaux")):
        return {
            "direction": "Wine pairing, regions, grape guides, and buying advice",
            "categoryHint": "Pairing Guides, Wine Regions, Grape Guides, Buying Advice",
            "contentContext": description or f"{brand} publishes wine guides and buying advice.",
            "topicStrategy": "Create evergreen wine guides that answer pairing, region, grape, serving, and buying questions.",
            "source": "fallback",
        }
    if any(word in combined for word in ("ai", "automation", "software", "saas", "platform", "app", "tool")):
        return {
            "direction": f"{brand} product use cases, automation, and buyer education",
            "categoryHint": "Use Cases, How-to Guides, Comparisons, Buyer Guides",
            "contentContext": description or f"{brand} is a software/product website.",
            "topicStrategy": "Create practical articles around user problems, workflows, comparisons, and implementation questions.",
            "source": "fallback",
        }
    seed = description or title or site["domain"]
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", seed) if w.lower() not in {"the", "and", "for", "with", "from", "that", "this", "your", "our"}]
    direction = " ".join(words[:8]) or site["domain"]
    return {
        "direction": direction,
        "categoryHint": "Guides, How-to Articles, Comparisons, Buying Advice",
        "contentContext": description or title or f"{brand} website.",
        "topicStrategy": "Create evergreen articles from the site's core product, audience, and search intent.",
        "source": "fallback",
    }


def theme_css(profile):
    colors = json.loads(profile["colors_json"] or "[]") if profile else []
    fonts = json.loads(profile["fonts_json"] or "[]") if profile else []
    bg = colors[0] if colors else "#0f1020"
    accent = colors[1] if len(colors) > 1 else "#7c4dff"
    text = "#111827"
    font = fonts[0] if fonts else "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    return f"""
:root {{--blog-bg:{bg};--blog-accent:{accent};--blog-text:{text};--blog-font:{font};}}
.blog-core-page {{font-family: var(--blog-font); color: var(--text, var(--blog-text)); background: var(--bg-dark, transparent); min-height: 100vh;}}
.blog-core-wrap {{max-width: 1120px; margin: 0 auto; padding: 132px 24px 64px;}}
.blog-core-hero {{padding: 72px 0 44px; border-bottom: 1px solid rgba(17,24,39,.12);}}
.blog-core-kicker {{color: var(--blog-accent); font-weight: 800; letter-spacing: .08em; text-transform: uppercase; font-size: 12px;}}
.blog-core-title {{font-size: clamp(40px, 7vw, 84px); line-height: .95; letter-spacing: -0.04em; margin: 14px 0 18px; max-width: 900px;}}
.blog-core-subtitle {{font-size: clamp(18px, 2.2vw, 24px); line-height: 1.45; color: rgba(17,24,39,.68); max-width: 760px;}}
.blog-core-grid {{display:grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 22px; margin-top: 38px;}}
.blog-core-card {{border:1px solid rgba(17,24,39,.12); border-radius: 22px; overflow:hidden; background:#fff; box-shadow:0 18px 50px rgba(15,16,32,.08);}}
.blog-core-card-media {{aspect-ratio: 16 / 10; background: linear-gradient(135deg, var(--blog-bg), var(--blog-accent));}}
.blog-core-card-body {{padding: 22px;}}
.blog-core-card h2 {{font-size: 22px; line-height:1.15; letter-spacing:-.02em; margin:0 0 10px;}}
.blog-core-card p {{font-size: 15px; line-height:1.55; color:rgba(17,24,39,.66); margin:0 0 16px;}}
.blog-core-card a {{color: var(--blog-accent); font-weight: 800; text-decoration:none;}}
.blog-core-article {{max-width: 780px; margin:0 auto; font-size: 19px; line-height:1.75; color:rgba(17,24,39,.78);}}
.blog-core-article h1 {{font-size:clamp(38px,6vw,70px); line-height:1; letter-spacing:-.04em; color:#111827;}}
.blog-core-article h2 {{font-size:30px; line-height:1.15; letter-spacing:-.025em; color:#111827; margin-top:42px;}}
.blog-core-article a {{color:var(--blog-accent); font-weight:800;}}
@media (max-width: 820px) {{.blog-core-grid{{grid-template-columns:1fr;}} .blog-core-wrap{{padding:112px 18px 42px;}}}}
""".strip()


def shell_behavior_script(source_css):
    if not source_css:
        return ""
    scripts = []
    if "nav.nav-scrolled" in source_css or ".nav-scrolled" in source_css:
        scripts.append("""
<script>
(function(){
  function updateNavScrollState(){
    document.querySelectorAll('nav').forEach(function(nav){
      nav.classList.toggle('nav-scrolled', window.scrollY > 20);
    });
  }
  updateNavScrollState();
  window.addEventListener('scroll', updateNavScrollState, {passive:true});
})();
</script>
""".strip())
    return "\n".join(scripts)


def render_shell(title, header, footer, body, css_href="/blog/blog-core.css", source_css="", source_css_urls=None):
    source_css_urls = source_css_urls or []
    source_links = "\n".join(f'<link rel="stylesheet" href="{escape(url, quote=True)}">' for url in source_css_urls)
    source_style = f"<style>\n{source_css}\n</style>" if source_css else ""
    behavior_script = shell_behavior_script(source_css)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
{source_links}
{source_style}
<link rel="stylesheet" href="{escape(css_href, quote=True)}">
</head>
<body class="blog-core-page">
{header}
{body}
{footer}
{behavior_script}
</body>
</html>
"""


def uses_native_blog_pattern(source_css):
    return all(token in (source_css or "") for token in (".section", ".blog-card", ".blog-carousel", ".container"))


def native_card(title, summary, image_url, pill="Wine Guide", href="/blog/visual-chaos-in-ai-product-cards/"):
    return f"""
<a class=\"blog-card\" href=\"{escape(href, quote=True)}\">
  <div class=\"img\" style=\"background-image:url('{escape(image_url, quote=True)}')\"></div>
  <div class=\"body\">
    <span class=\"pill\">{escape(pill)}</span>
    <h3>{escape(title)}</h3>
    <p>{escape(summary)}</p>
    <span class=\"read\">Read guide</span>
  </div>
</a>
"""


def render_native_blog_index(brand, header, footer, css_href, source_css, source_css_urls):
    cards = "".join([
        native_card(
            "How to remove visual chaos from product pages",
            "A practical guide to keeping catalog visuals consistent so shoppers trust what they see.",
            "https://yas.wine/blog/wine-region-napa-valley-united-states-hero-opt.webp",
            "Strategy",
        ),
        native_card(
            "Wine pairing basics for confident buying",
            "Simple pairing rules that help readers choose bottles by meal, occasion, and taste.",
            "https://yas.wine/blog/wine-pairing-guide-hero-icon.webp",
            "Pairing",
            "#",
        ),
        native_card(
            "How to choose wine without guessing",
            "A beginner-friendly framework for regions, grapes, labels, budget, and bottle styles.",
            "https://yas.wine/blog/how-to-choose-wine-hero-icon.webp",
            "Buying Guide",
            "#",
        ),
    ])
    body = f"""
<div class=\"fixed-bg\"></div>
<main class=\"container\" style=\"padding-top:120px;padding-bottom:80px\">
  <section class=\"section\">
    <h2>{escape(brand)} Blog</h2>
    <p class=\"lead\">Practical wine guides for pairing, regions, grapes, bottle choice, and winery travel.</p>
    <a class=\"btn btn-primary\" href=\"#latest-guides\">Explore latest guides</a>
  </section>
  <section id=\"latest-guides\" class=\"section\">
    <h2>Latest wine guides</h2>
    <p class=\"lead\">Useful articles built in the same visual system as the main site, ready for the content factory to publish into.</p>
    <div class=\"blog-carousel\">{cards}</div>
  </section>
</main>
"""
    return render_shell(f"Blog - {brand}", header, footer, body, css_href, source_css, source_css_urls)


def render_blog_index(brand, header, footer, css_href="/blog/blog-core.css", source_css="", source_css_urls=None):
    if uses_native_blog_pattern(source_css):
        return render_native_blog_index(brand, header, footer, css_href, source_css, source_css_urls)
    body = f"""
<main class=\"blog-core-wrap\">
<section class=\"blog-core-hero\">
<div class=\"blog-core-kicker\">{escape(brand)} Blog</div>
<h1 class=\"blog-core-title\">Practical guides, ideas, and field notes.</h1>
<p class=\"blog-core-subtitle\">A blog section generated from the site design profile. It can be filled by the content factory, localized, linked to sitemap, and published without rebuilding the original website.</p>
</section>
<section class=\"blog-core-grid\">
<article class=\"blog-core-card\"><div class=\"blog-core-card-media\"></div><div class=\"blog-core-card-body\"><h2>How to remove visual chaos from product pages</h2><p>A sample article template for commercial SEO content.</p><a href=\"/blog/visual-chaos-in-ai-product-cards/\">Read article</a></div></article>
<article class=\"blog-core-card\"><div class=\"blog-core-card-media\"></div><div class=\"blog-core-card-body\"><h2>Use cases and buyer objections</h2><p>Turn product questions into useful blog and landing content.</p><a href=\"#\">Coming soon</a></div></article>
<article class=\"blog-core-card\"><div class=\"blog-core-card-media\"></div><div class=\"blog-core-card-body\"><h2>Content engine status</h2><p>Connect the publisher queue when the site shell is approved.</p><a href=\"#\">Coming soon</a></div></article>
</section>
</main>
"""
    return render_shell(f"Blog - {brand}", header, footer, body, css_href, source_css, source_css_urls)


def render_sample_article(brand, header, footer, css_href="/blog/blog-core.css", source_css="", source_css_urls=None):
    if uses_native_blog_pattern(source_css):
        body = f"""
<div class=\"fixed-bg\"></div>
<main class=\"container\" style=\"padding-top:120px;padding-bottom:80px\">
  <article class=\"section\" style=\"max-width:880px;margin-left:auto;margin-right:auto\">
    <span class=\"pill\">Ecommerce Visuals</span>
    <h2 style=\"margin-top:18px\">Why AI product pages start looking chaotic and how to fix it</h2>
    <p class=\"lead\">When every product is photographed or generated with a different light, angle, crop, and background, buyers read the page as inconsistent. In ecommerce, inconsistent visuals often feel like risk.</p>
    <h3 style=\"font-size:24px;margin:28px 0 10px\">The actual conversion problem</h3>
    <p class=\"lead\">Visual mismatch forces shoppers to compare photography quality instead of product value. A clean catalog needs repeatable rules for lighting, scale, camera distance, context, and product emphasis.</p>
    <h3 style=\"font-size:24px;margin:28px 0 10px\">The system-level fix</h3>
    <p class=\"lead\">The blog core can publish articles that connect the search problem to the product workflow: style-locked visuals, product-specific proof shots, and consistent creative direction across a catalog.</p>
    <a class=\"btn btn-primary\" href=\"/blog/\">Back to blog</a>
  </article>
</main>
"""
        return render_shell(f"Visual chaos in AI product cards - {brand}", header, footer, body, css_href, source_css, source_css_urls)
    body = f"""
<main class=\"blog-core-wrap\">
<article class=\"blog-core-article\">
<p class=\"blog-core-kicker\">Ecommerce Visuals</p>
<h1>Why AI product pages start looking chaotic and how to fix it</h1>
<p>When every product is photographed or generated with a different light, angle, crop, and background, buyers read the page as inconsistent. In ecommerce, inconsistent visuals often feel like risk.</p>
<h2>The actual conversion problem</h2>
<p>Visual mismatch forces shoppers to compare photography quality instead of product value. A clean catalog needs repeatable rules for lighting, scale, camera distance, context, and product emphasis.</p>
<h2>The system-level fix</h2>
<p>The blog core can publish articles that connect the search problem to the product workflow: style-locked visuals, product-specific proof shots, and consistent creative direction across a catalog.</p>
<p><a href=\"/blog/\">Back to blog</a></p>
</article>
</main>
"""
    return render_shell(f"Visual chaos in AI product cards - {brand}", header, footer, body, css_href, source_css, source_css_urls)




def get_public_content_jobs(site_id, limit=200):
    with db() as conn:
        return conn.execute(
            """
            select * from content_jobs
            where site_id=? and status in ('IMPORTED','DRAFT','PUBLISHED') and slug is not null and slug <> ''
            order by created_at desc limit ?
            """,
            (site_id, limit),
        ).fetchall()


def render_blog_index_from_jobs(brand, header, footer, jobs, css_href="/blog/blog-core.css", source_css="", source_css_urls=None):
    if not jobs:
        return render_blog_index(brand, header, footer, css_href, source_css, source_css_urls)
    if uses_native_blog_pattern(source_css):
        cards = []
        for row in jobs[:24]:
            href = f"/blog/{row['slug'].strip('/')}/"
            cards.append(native_card(row['title'] or row['topic'], row['description'] or "Imported article", row['hero_image'] or "", row['category'] or "Article", href))
        body = f"""
<div class=\"fixed-bg\"></div>
<main class=\"container\" style=\"padding-top:120px;padding-bottom:80px\">
  <section class=\"section\">
    <h2>{escape(brand)} Blog</h2>
    <p class=\"lead\">Imported and generated articles managed by Blog Core.</p>
  </section>
  <section id=\"latest-guides\" class=\"section\">
    <h2>Latest articles</h2>
    <div class=\"blog-carousel\">{''.join(cards)}</div>
  </section>
</main>
"""
        return render_shell(f"Blog - {brand}", header, footer, body, css_href, source_css, source_css_urls)
    cards = []
    for row in jobs[:48]:
        href = f"/blog/{row['slug'].strip('/')}/"
        media = f"<img src=\"{escape(row['hero_image'], quote=True)}\" alt=\"\" loading=\"lazy\">" if row['hero_image'] else ""
        cards.append(f"""
<article class=\"blog-core-card\"><div class=\"blog-core-card-media\">{media}</div><div class=\"blog-core-card-body\"><h2>{escape(row['title'] or row['topic'])}</h2><p>{escape(row['description'] or 'Imported article')}</p><a href=\"{escape(href, quote=True)}\">Read article</a></div></article>
""")
    body = f"""
<main class=\"blog-core-wrap\">
<section class=\"blog-core-hero\">
<div class=\"blog-core-kicker\">{escape(brand)} Blog</div>
<h1 class=\"blog-core-title\">Latest articles and guides.</h1>
<p class=\"blog-core-subtitle\">Imported and generated articles managed by Blog Core while preserving original URLs and slugs.</p>
</section>
<section class=\"blog-core-grid\">{''.join(cards)}</section>
</main>
"""
    return render_shell(f"Blog - {brand}", header, footer, body, css_href, source_css, source_css_urls)


def render_content_job_article(brand, header, footer, job, css_href="/blog/blog-core.css", source_css="", source_css_urls=None):
    title = job['title'] or job['topic'] or brand
    content = job['draft_html'] or ""
    if uses_native_blog_pattern(source_css):
        body = f"""
<div class=\"fixed-bg\"></div>
<main class=\"container\" style=\"padding-top:120px;padding-bottom:80px\">
  <article class=\"section\" style=\"max-width:880px;margin-left:auto;margin-right:auto\">
    <span class=\"pill\">{escape(job['category'] or 'Article')}</span>
    <h2 style=\"margin-top:18px\">{escape(title)}</h2>
    {content}
    <a class=\"btn btn-primary\" href=\"/blog/\">Back to blog</a>
  </article>
</main>
"""
    else:
        body = f"""
<main class=\"blog-core-wrap\">
<article class=\"blog-core-article\">
<p class=\"blog-core-kicker\">{escape(job['category'] or 'Article')}</p>
<h1>{escape(title)}</h1>
{content}
<p><a href=\"/blog/\">Back to blog</a></p>
</article>
</main>
"""
    return render_shell(title, header, footer, body, css_href, source_css, source_css_urls)


def public_site_base_url(site):
    homepage = site["homepage_url"] if site and "homepage_url" in site.keys() else ""
    if homepage:
        parsed = urllib.parse.urlsplit(homepage)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}/"
    domain = site["domain"] if site and "domain" in site.keys() else ""
    return f"https://{domain.strip('/')}/" if domain else "/"


def content_job_target_path(row):
    sources = content_job_sources(row)
    target_path = str(sources.get("targetPath") or "").strip()
    if not target_path and row["published_url"]:
        target_path = urllib.parse.urlsplit(row["published_url"]).path or ""
    if not target_path and row["slug"]:
        target_path = f"/blog/{str(row['slug']).strip('/')}/"
    return target_path or "/blog/"


def source_authoritative_content_job(row):
    sources = content_job_sources(row)
    return bool(sources.get("migratedFrom") and sources.get("oldFactoryJobId") and sources.get("ownership") == "source_site_authoritative")


def native_content_store_job(row):
    """A site-owned Next content store accepts generated drafts and publishes them natively."""
    mode = str(content_job_sources(row).get("publicationMode") or "").strip().lower()
    return mode in {"native_next_content_store", "native_yas_publisher"}


def native_content_store_root(site, row):
    sources = content_job_sources(row)
    root = Path(str(sources.get("nativeProjectRoot") or site["root_path"] or "")).resolve()
    if not root.is_dir():
        raise RuntimeError("Native content store requires an existing local project root")
    return root / "data" / "blog-core"


def native_content_store_payload(site, row, published=False):
    sources = content_job_sources(row)
    try:
        faq = json.loads(row["faq_json"] or "[]")
    except Exception:
        faq = []
    word_count = len(strip_html_text(row["draft_html"] or "").split())
    raw_content_type = str(sources.get("contentType") or sources.get("pageType") or "blog").strip().lower()
    content_type = "use_case" if raw_content_type in {"use_case", "use-cases", "seo_money_page", "seo-money-page"} else "blog"
    return {
        "id": row["id"],
        "slug": row["slug"],
        "title": row["title"] or row["topic"],
        "description": row["description"] or "",
        "category": row["category"] or "Insights",
        "heroImage": row["hero_image"] or "",
        "draftHtml": row["draft_html"] or "",
        "faq": faq if isinstance(faq, list) else [],
        "readMinutes": max(1, math.ceil(word_count / 220)),
        "targetPath": content_job_target_path(row),
        "contentType": content_type,
        "updatedAt": now_iso(),
        "publishedAt": now_iso() if published else None,
    }


def write_native_content_store(site, row, state):
    if state not in {"drafts", "published"}:
        raise ValueError("Native content store state must be drafts or published")
    if not (row["draft_html"] or "").strip():
        raise ValueError("A native content record requires a generated draft")
    directory = native_content_store_root(site, row) / state
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{row['id']}.json" if state == "drafts" else f"{row['slug']}.json"
    target = directory / filename
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(native_content_store_payload(site, row, published=state == "published"), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)
    return target


def content_job_source_url(site, row):
    sources = content_job_sources(row)
    raw = str(sources.get("sourcePublishedUrl") or row["published_url"] or content_job_target_path(row) or "").strip()
    if not raw:
        return ""
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme and parsed.netloc:
        return raw
    return urllib.parse.urljoin(public_site_base_url(site), raw.lstrip("/"))


def local_html_path_for_url_path(root_path, url_path):
    root = Path(root_path).resolve()
    clean = urllib.parse.unquote((url_path or "/").split("?", 1)[0].split("#", 1)[0]).strip("/")
    candidate = root / clean
    if not clean:
        candidate = root / "index.html"
    elif str(url_path).endswith("/") or candidate.suffix == "":
        candidate = candidate / "index.html"
    resolved = candidate.resolve()
    if root == resolved or root in resolved.parents:
        return resolved
    return None


def find_sibling_article_template(root_path, target_path):
    clean = urllib.parse.unquote((target_path or "/").split("?", 1)[0].split("#", 1)[0]).strip("/")
    parts = [part for part in clean.split("/") if part]
    if not parts:
        return None
    section_dir = (root_path / parts[0]).resolve()
    try:
        root_resolved = root_path.resolve()
    except Exception:
        return None
    if not section_dir.exists() or not section_dir.is_dir() or root_resolved not in section_dir.parents:
        return None
    candidates = []
    for file_path in sorted(section_dir.rglob("*.html")):
        rel = file_path.relative_to(section_dir).as_posix()
        if rel == "index.html" or rel.count("/") > 1:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"<section\b[^>]*class=[\"'][^\"']*\barticle-layout\b[^\"']*[\"']", text, flags=re.I):
            tail = extract_source_post_article_sections(text)
            score = 0
            if re.search(r"\bfaq-grid\b|\bfaq-card\b", text, flags=re.I):
                score += 2
            if tail:
                score += 3
            if re.search(r"\brecommend(?:ed|ations?|s)?\b|\brelated\b|\bnext\b|\bnewsletter\b|\bsubscribe\b|\bwaitlist\b|\bupdates?\b", tail, flags=re.I):
                score += 10
            score += min(len(tail) // 1000, 5)
            candidates.append((score, file_path))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[0], item[1].as_posix()))
    return candidates[0][1]


def find_local_preview_template(site, job):
    root = (site["root_path"] or "").strip()
    if not root:
        return None
    root_path = Path(root)
    target = local_html_path_for_url_path(root, content_job_target_path(job))
    if target and target.exists() and target.is_file():
        return target
    sibling_template = find_sibling_article_template(root_path, content_job_target_path(job))
    if sibling_template:
        return sibling_template
    sources = content_job_sources(job)
    page_type = str(sources.get("pageType") or sources.get("contentType") or job["category"] or "").lower()
    fallbacks = []
    if "blog" in page_type:
        fallbacks.extend(["/blog/index.html", "/blog/"])
    target_path = content_job_target_path(job)
    if target_path.startswith("/use-cases/"):
        fallbacks.extend(["/use-cases/index.html", "/use-cases/"])
    if target_path.startswith("/features/"):
        fallbacks.extend(["/features/index.html", "/features/"])
    fallbacks.append("/index.html")
    for path in fallbacks:
        candidate = local_html_path_for_url_path(root, path)
        if candidate and candidate.exists() and candidate.is_file():
            return candidate
    return None


def inject_preview_head_metadata(html, site, job):
    title = escape(job["title"] or job["topic"] or site["brand_name"] or site["domain"])
    description = escape(job["description"] or strip_html_text(job["draft_html"] or "", limit=180))
    base_url = escape(public_site_base_url(site), quote=True)
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.I | re.S)
    html = re.sub(
        r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>',
        f'<meta name="description" content="{description}" />',
        html,
        count=1,
        flags=re.I,
    )
    if re.search(r'<meta\s+name=["\']robots["\']', html, flags=re.I):
        html = re.sub(
            r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
            '<meta name="robots" content="noindex,nofollow" />',
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = re.sub(r"(<head[^>]*>)", rf'\1\n    <meta name="robots" content="noindex,nofollow" />', html, count=1, flags=re.I)
    if not re.search(r"<base\s+", html, flags=re.I):
        html = re.sub(r"(<head[^>]*>)", rf'\1\n    <base href="{base_url}">', html, count=1, flags=re.I)
    return html


def find_matching_closing_tag(html, open_start, tag_name):
    tag_pattern = re.compile(rf"</?{re.escape(tag_name)}\b[^>]*>", re.I)
    depth = 0
    for match in tag_pattern.finditer(html, open_start):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        elif not token.rstrip().endswith("/>"):
            depth += 1
    return None


def extract_source_post_article_sections(html):
    main_match = re.search(r"<main\b[^>]*>", html or "", flags=re.I)
    if not main_match:
        return ""
    main_end_match = re.search(r"</main\s*>", html[main_match.end():], flags=re.I)
    if not main_end_match:
        return ""
    main_end = main_match.end() + main_end_match.start()
    content = html[main_match.end():main_end]
    article_section = re.search(r"<section\b[^>]*class=[\"'][^\"']*\barticle-layout\b[^\"']*[\"'][^>]*>", content, flags=re.I)
    if not article_section:
        return ""
    section_start = main_match.end() + article_section.start()
    section_end = find_matching_closing_tag(html, section_start, "section")
    if not section_end or section_end > main_end:
        return ""
    tail = html[section_end:main_end].strip()
    return tail if re.search(r"<(?:section|aside|nav|div)\b", tail, flags=re.I) else ""


def remove_source_faq_sections(html):
    output = html or ""
    for pattern in (
        r'<section\b[^>]*(?:aria-labelledby=["\']faq-title["\']|class=["\'][^"\']*\bfaq\b[^"\']*["\'])[^>]*>.*?</section>',
        r'<section\b(?=[^>]*>)(?:(?!</section>).)*\bfaq-grid\b.*?</section>',
    ):
        output = re.sub(pattern, "", output, flags=re.I | re.S)
    return output.strip()


def faq_items_from_article_faq(block):
    items = []
    for match in re.finditer(r"<details\b[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>", block or "", flags=re.I | re.S):
        question = re.sub(r"\s+", " ", match.group(1)).strip()
        answer = re.sub(r"\s+", " ", match.group(2)).strip()
        if question and answer:
            items.append((question, answer))
    return items


def adapt_faq_to_source_template(content, template_html):
    if not content or "article-faq" not in content:
        return content
    if "faq-grid" not in (template_html or "") or "faq-card" not in (template_html or ""):
        return content

    def replace_faq(match):
        items = faq_items_from_article_faq(match.group(0))
        if not items:
            return match.group(0)
        cards = "".join(
            f'<details class="faq-card"><summary>{question}</summary><div class="faq-answer"><div class="faq-answer-inner"><p>{answer}</p></div></div></details>'
            for question, answer in items
        )
        return f'<section class="section" aria-labelledby="faq-title"><p class="section-kicker">FAQ</p><h2 id="faq-title">Questions</h2><div class="faq-grid">{cards}</div></section>'

    return re.sub(r'<section\b[^>]*class=["\'][^"\']*\barticle-faq\b[^"\']*["\'][^>]*>.*?</section>', replace_faq, content, flags=re.I | re.S)


def prepare_local_draft_content(content, template_html=""):
    base = public_base_url().rstrip("/")
    current_url = request.base_url if request else ""
    content = adapt_faq_to_source_template(content or "", template_html or "")
    content = re.sub(r'(<(?:img|source)\b[^>]*\s(?:src|srcset)=["\'])/sites/', rf'\1{base}/sites/', content or "", flags=re.I)
    content = re.sub(r'(<a\b[^>]*\shref=["\'])#([^"\']+)', rf'\1{escape(current_url, quote=True)}#\2', content, flags=re.I)
    return content


def local_site_draft_body(site, job, template_html=""):
    title = escape(job["title"] or job["topic"] or site["brand_name"] or site["domain"])
    description = escape(job["description"] or "")
    category = escape(job["category"] or "Blog")
    content = prepare_local_draft_content(job["draft_html"] or "", template_html)
    post_article_sections = prepare_local_draft_content(remove_source_faq_sections(extract_source_post_article_sections(template_html)), template_html)
    return f"""
<section class="hero hero-no-media"><div class="hero-inner"><div><span class="eyebrow">{category}</span><h1>{title}</h1>{f'<p>{description}</p>' if description else ''}</div></div></section>
<main class="site-main">
<section class="section article-layout factory-article-layout"><div class="article-body blog-core-draft-body">{content}</div></section>
{post_article_sections}
</main>
"""


def replace_source_site_content(html, replacement):
    main_match = re.search(r"<main\b[^>]*>", html, flags=re.I)
    if not main_match:
        body_end = re.search(r"</body\s*>", html, flags=re.I)
        if body_end:
            return html[:body_end.start()] + replacement + html[body_end.start():]
        return html + replacement
    hero_match = None
    for match in re.finditer(r"<section\b[^>]*class=[\"'][^\"']*\bhero\b[^\"']*[\"'][^>]*>", html, flags=re.I):
        if match.start() < main_match.start():
            hero_match = match
    start = hero_match.start() if hero_match else main_match.start()
    end_match = re.search(r"</main\s*>", html[main_match.end():], flags=re.I)
    if not end_match:
        return html[:start] + replacement + html[main_match.start():]
    end = main_match.end() + end_match.end()
    return html[:start] + replacement + html[end:]


def render_local_site_draft_preview(site, job):
    template_path = find_local_preview_template(site, job)
    if not template_path:
        return None
    html = template_path.read_text(encoding="utf-8", errors="ignore")
    html = inject_preview_head_metadata(html, site, job)
    return replace_source_site_content(html, local_site_draft_body(site, job, html))


def get_content_job_by_slug(site_id, slug):
    slug = simple_slug(slug)
    with db() as conn:
        return conn.execute(
            """
            select * from content_jobs
            where site_id=? and slug=? and status in ('IMPORTED','DRAFT','PUBLISHED')
            order by updated_at desc limit 1
            """,
            (site_id, slug),
        ).fetchone()

def build_preview(site, profile):
    site_id = site["id"]
    preview_root = PREVIEW_DIR / str(site_id) / "blog"
    article_root = preview_root / "visual-chaos-in-ai-product-cards"
    preview_root.mkdir(parents=True, exist_ok=True)
    article_root.mkdir(parents=True, exist_ok=True)
    css = theme_css(profile)
    header = profile["header_html"] if profile and profile["header_html"] else ""
    footer = profile["footer_html"] if profile and profile["footer_html"] else ""
    source_css = profile["head_css"] if profile and "head_css" in profile.keys() and profile["head_css"] else ""
    source_css_urls = json.loads(profile["css_urls_json"] or "[]") if profile else []
    brand = site["brand_name"] or site["domain"]
    index_html = render_blog_index(brand, header, footer, "./blog-core.css", source_css, source_css_urls)
    article_html = render_sample_article(brand, header, footer, "../blog-core.css", source_css, source_css_urls)
    (preview_root / "blog-core.css").write_text(css, encoding="utf-8")
    (preview_root / "index.html").write_text(index_html, encoding="utf-8")
    (article_root / "index.html").write_text(article_html, encoding="utf-8")
    rel = f"/previews/{site_id}/blog/"
    with db() as conn:
        conn.execute(
            "insert into blog_templates(site_id, preview_path, template_html, css, created_at) values(?,?,?,?,?) on conflict(site_id) do update set preview_path=excluded.preview_path, template_html=excluded.template_html, css=excluded.css, created_at=excluded.created_at",
            (site_id, rel, index_html, css, now_iso()),
        )
    return rel


def install_blog(site, profile):
    root = (site["root_path"] or "").strip()
    if not root:
        raise ValueError("root_path is required for local_path install")
    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"root_path does not exist: {root_path}")
    blog_dir = root_path / "blog"
    article_dir = blog_dir / "visual-chaos-in-ai-product-cards"
    blog_dir.mkdir(parents=True, exist_ok=True)
    article_dir.mkdir(parents=True, exist_ok=True)
    css = theme_css(profile)
    header = profile["header_html"] if profile and profile["header_html"] else ""
    footer = profile["footer_html"] if profile and profile["footer_html"] else ""
    source_css = profile["head_css"] if profile and "head_css" in profile.keys() and profile["head_css"] else ""
    source_css_urls = json.loads(profile["css_urls_json"] or "[]") if profile else []
    brand = site["brand_name"] or site["domain"]
    (blog_dir / "blog-core.css").write_text(css, encoding="utf-8")
    (blog_dir / "index.html").write_text(render_blog_index(brand, header, footer, "/blog/blog-core.css", source_css, source_css_urls), encoding="utf-8")
    (article_dir / "index.html").write_text(render_sample_article(brand, header, footer, "/blog/blog-core.css", source_css, source_css_urls), encoding="utf-8")
    sitemap = root_path / "sitemap-blog.xml"
    base = normalize_url(site["homepage_url"]).rstrip("/")
    sitemap.write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        f"  <url><loc>{base}/blog/</loc></url>\n"
        f"  <url><loc>{base}/blog/visual-chaos-in-ai-product-cards/</loc></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    robots = root_path / "robots.txt"
    line = f"Sitemap: {base}/sitemap-blog.xml"
    if robots.exists():
        current = robots.read_text(encoding="utf-8", errors="ignore")
        if line not in current:
            robots.write_text(current.rstrip() + "\n" + line + "\n", encoding="utf-8")
    else:
        robots.write_text("User-agent: *\nAllow: /\n\n" + line + "\n", encoding="utf-8")
    return {"installed": True, "blog_dir": str(blog_dir), "sitemap": str(sitemap)}


def get_site(site_id):
    with db() as conn:
        return conn.execute("select * from sites where id=?", (site_id,)).fetchone()


def get_profile(site_id):
    with db() as conn:
        return conn.execute("select * from site_theme_profiles where site_id=?", (site_id,)).fetchone()


def form_bool(value):
    return 1 if str(value or "").lower() in ("1", "true", "on", "yes") else 0


def languages_to_text(value):
    try:
        parsed = json.loads(value or "[]")
        if isinstance(parsed, list):
            return ", ".join(str(item) for item in parsed)
    except Exception:
        pass
    return value or "en"


def parse_languages(value):
    try:
        parsed = json.loads(value or "[]")
        if isinstance(parsed, list):
            items = [str(item).strip().lower() for item in parsed if str(item).strip()]
            return items or ["en"]
    except Exception:
        pass
    items = [item.strip().lower() for item in re.split(r"[,\n]", value or "") if item.strip()]
    return items or ["en"]


def text_to_languages(value):
    items = [item.strip() for item in re.split(r"[,\n]", value or "") if item.strip()]
    return json.dumps(items or ["en"])


def get_site_full(site_id):
    with db() as conn:
        return conn.execute(
            """
            select s.*, p.scanned_at, p.title as scanned_title, p.description as scanned_description,
                   p.colors_json, p.fonts_json, p.css_urls_json, t.preview_path
            from sites s
            left join site_theme_profiles p on p.site_id=s.id
            left join blog_templates t on t.site_id=s.id
            where s.id=?
            """,
            (site_id,),
        ).fetchone()


def get_site_jobs(site_id):
    with db() as conn:
        return conn.execute(
            "select * from publish_jobs where site_id=? order by created_at desc limit 12",
            (site_id,),
        ).fetchall()


def content_job_language(row):
    try:
        sources = json.loads(row["sources_json"] or "{}")
    except Exception:
        sources = {}
    language = str(sources.get("language") or "").strip().lower()
    if language:
        return language
    path = urllib.parse.urlsplit(row["published_url"] or "").path or ""
    first = path.strip("/").split("/", 1)[0]
    return first if first in {"ru", "es", "de", "fr"} else "en"


def content_job_base_path(row):
    path = urllib.parse.urlsplit(row["published_url"] or "").path or ""
    parts = [part for part in path.strip("/").split("/") if part]
    if parts and parts[0] in {"ru", "es", "de", "fr"}:
        parts = parts[1:]
    if not parts:
        return row["slug"] or row["title"] or row["topic"] or ""
    return "/".join(parts)


def content_job_sort_key(row):
    base_path = content_job_base_path(row)
    section_order = 0
    if base_path.startswith("blog/"):
        section_order = 0
    elif base_path.startswith("wine-countries/"):
        section_order = 1
    elif base_path.startswith("wine-regions/"):
        section_order = 2
    else:
        section_order = 3
    return (section_order, base_path, row["title"] or row["topic"] or "", row["id"])


def content_job_page_type(row):
    try:
        sources = json.loads(row["sources_json"] or "{}")
    except Exception:
        sources = {}
    page_type = str(sources.get("pageType") or "").strip().lower()
    category = (row["category"] or "").strip().lower()
    if page_type in {"blog", "seo_money_page", "home"}:
        return page_type
    if "seo money" in category:
        return "seo_money_page"
    if "blog" in category:
        return "blog"
    if "homepage" in category:
        return "home"
    return "other"


def get_content_jobs(site_id, page=1, per_page=24, hide_hubs=True, language="en", content_type="all"):
    try:
        page = max(1, int(page or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(1, min(100, int(per_page or 24)))
    except (TypeError, ValueError):
        per_page = 24
    with db() as conn:
        rows = conn.execute(
            "select * from content_jobs where site_id=? order by created_at desc, id desc",
            (site_id,),
        ).fetchall()
    if hide_hubs:
        rows = [row for row in rows if not is_imported_content_hub(row)]
    language_order = ["en", "ru", "es", "de", "fr"]
    language_set = {content_job_language(row) for row in rows if content_job_language(row)}
    available_languages = [lang for lang in language_order if lang in language_set] + sorted(language_set - set(language_order))
    language = (language or "en").strip().lower()
    if language != "all" and available_languages and language not in available_languages:
        language = available_languages[0]
    if language != "all":
        rows = [row for row in rows if content_job_language(row) == language]
    type_order = ["blog", "seo_money_page", "home", "other"]
    type_set = {content_job_page_type(row) for row in rows}
    available_content_types = [type_name for type_name in type_order if type_name in type_set] + sorted(type_set - set(type_order))
    content_type = (content_type or "all").strip().lower()
    if content_type not in {"all", *set(available_content_types)}:
        content_type = "all"
    if content_type != "all":
        rows = [row for row in rows if content_job_page_type(row) == content_type]
    rows = sorted(rows, key=content_job_sort_key)
    total = len(rows)
    total_pages = max(1, math.ceil(total / per_page)) if total else 1
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    page_rows = rows[offset:offset + per_page]
    return {
        "rows": page_rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "language": language,
        "available_languages": available_languages,
        "content_type": content_type,
        "available_content_types": available_content_types,
    }


def get_planned_content_jobs(site_id, limit=200):
    with db() as conn:
        rows = conn.execute(
            """
            select * from content_jobs
            where site_id=? and status in ('QUEUED','GENERATING','DRAFT','ERROR')
            order by created_at desc, id desc
            limit ?
            """,
            (site_id, int(limit or 200)),
        ).fetchall()
    return rows


def get_autopublish_settings(site_id):
    with db() as conn:
        row = conn.execute("select * from autopublish_settings where site_id=?", (site_id,)).fetchone()
        if row:
            return row
        conn.execute("insert into autopublish_settings(site_id, updated_at) values(?, ?)", (site_id, now_iso()))
        return conn.execute("select * from autopublish_settings where site_id=?", (site_id,)).fetchone()


def get_topic_discovery_settings(site_id):
    with db() as conn:
        row = conn.execute("select * from topic_discovery_settings where site_id=?", (site_id,)).fetchone()
        if row:
            return row
        conn.execute("insert into topic_discovery_settings(site_id, updated_at) values(?, ?)", (site_id, now_iso()))
        return conn.execute("select * from topic_discovery_settings where site_id=?", (site_id,)).fetchone()


def get_social_connections(site_id):
    providers = ["zernio", "linkedin", "telegram", "tumblr", "twitter", "pinterest", "instagram", "threads", "reddit"]
    with db() as conn:
        rows = {r["provider"]: r for r in conn.execute("select * from social_connections where site_id=?", (site_id,)).fetchall()}
    return {provider: rows.get(provider) for provider in providers}


def active_social_channels(site_id, requested_channels=None):
    auto = get_autopublish_settings(site_id)
    try:
        selected = set(json.loads(auto["channels_json"] or "[]"))
    except Exception:
        selected = set()
    if requested_channels is not None:
        selected &= {channel for channel in requested_channels if channel in SOCIAL_CHANNEL_LIMITS}
    connections = get_social_connections(site_id)
    zernio = connections.get("zernio")
    zernio_credentials = get_social_credentials(zernio)
    zernio_ready = bool(zernio and zernio["status"] in {"configured", "connected"} and social_credentials_complete("zernio", zernio_credentials))
    active = []
    for channel in SOCIAL_CHANNEL_LIMITS:
        if channel in ZERNIO_SOCIAL_CHANNELS:
            if channel in selected and zernio_ready and zernio_credentials.get(f"{channel}_account_id"):
                active.append(channel)
            continue
        row = connections.get(channel)
        status = row["status"] if row else "disconnected"
        if channel in selected and status in {"configured", "connected"}:
            active.append(channel)
    return active


def social_channel_connection_state(site_id, channel, connections=None):
    connections = connections or get_social_connections(site_id)
    if channel in ZERNIO_SOCIAL_CHANNELS:
        zernio = connections.get("zernio")
        credentials = get_social_credentials(zernio)
        ready = bool(zernio and zernio["status"] in {"configured", "connected"} and credentials.get(f"{channel}_account_id"))
        return ("connected" if ready else "disconnected", "Zernio" if ready else "Configure Zernio in Setup")
    row = connections.get(channel)
    status = row["status"] if row else "disconnected"
    return status, ("Connected" if status == "connected" else ("Ready to test" if status == "configured" else "Configure in Setup"))


SOCIAL_PROVIDER_CONFIG = {
    "zernio": {
        "label": "Zernio publishing transport",
        "fields": [
            ("api_key", "Zernio API key", "password", "Uses server default when blank"),
            ("profile_id", "Zernio profile ID", "text", "Optional profile id"),
            ("twitter_account_id", "X account ID", "text", "acc_..."),
            ("pinterest_account_id", "Pinterest account ID", "text", "acc_..."),
            ("instagram_account_id", "Instagram account ID", "text", "acc_..."),
            ("threads_account_id", "Threads account ID", "text", "acc_..."),
            ("reddit_account_id", "Reddit account ID", "text", "acc_..."),
            ("pinterest_board_id", "Pinterest board ID", "text", "Required for Pin publication"),
            ("reddit_subreddit", "Default subreddit", "text", "Without r/ prefix"),
            ("reddit_rules", "Subreddit tone and rules", "text", "Optional: e.g. no links in title; disclose affiliation"),
        ],
    },
    "linkedin": {
        "label": "LinkedIn",
        "fields": [
            ("access_token", "Access token", "password", "LinkedIn OAuth access token"),
            ("author_urn", "Author / organization URN", "text", "urn:li:organization:123 or urn:li:person:abc"),
        ],
    },
    "telegram": {
        "label": "Telegram",
        "fields": [
            ("bot_token", "Bot token", "password", "123456:ABC..."),
            ("chat_id", "Chat ID / channel", "text", "@channelname or numeric chat id"),
        ],
    },
    "twitter": {
        "label": "X / Twitter",
        "fields": [
            ("bearer_token", "Bearer token", "password", "OAuth 2.0 bearer token"),
            ("user_id", "User ID / handle", "text", "Optional posting identity"),
        ],
    },
    "tumblr": {
        "label": "Tumblr",
        "fields": [
            ("consumer_key", "Consumer key", "password", "Tumblr OAuth consumer key"),
            ("consumer_secret", "Consumer secret", "password", "Tumblr OAuth consumer secret"),
            ("oauth_token", "OAuth token", "password", "Tumblr OAuth token"),
            ("oauth_token_secret", "OAuth token secret", "password", "Tumblr OAuth token secret"),
            ("blog_hostname", "Blog hostname", "text", "example.tumblr.com"),
        ],
    },
    "pinterest": {
        "label": "Pinterest",
        "fields": [
            ("access_token", "Access token", "password", "Pinterest OAuth access token"),
            ("board_id", "Board ID", "text", "Pinterest board id for publishing pins"),
        ],
    },
    "instagram": {
        "label": "Instagram",
        "fields": [
            ("api_key", "Intermediary API key", "password", "Third-party publishing server API key"),
            ("api_base_url", "Intermediary API base URL", "text", "https://publisher.example.com"),
            ("instagram_profile", "Instagram profile / route", "text", "@brand or profile id used by the intermediary"),
        ],
    },
    "threads": {
        "label": "Threads",
        "fields": [
            ("access_token", "Access token", "password", "Threads API access token"),
            ("threads_user_id", "Threads user ID", "text", "Optional; /me is used for connection test"),
        ],
    },
}

SOCIAL_CHANNEL_LIMITS = {
    "linkedin": 3000,
    "telegram": 4096,
    "twitter": 280,
    "tumblr": 4096,
    "pinterest": 500,
    "instagram": 2200,
    "threads": 500,
    "reddit": 40000,
}

ZERNIO_SOCIAL_CHANNELS = {"twitter", "pinterest", "instagram", "threads", "reddit"}
SOCIAL_CHANNEL_LABELS = {
    "linkedin": "LinkedIn", "telegram": "Telegram", "twitter": "X / Twitter", "tumblr": "Tumblr",
    "pinterest": "Pinterest", "instagram": "Instagram", "threads": "Threads", "reddit": "Reddit",
}

SOCIAL_CHANNEL_TARGET_CHARS = {
    "instagram": 700,
    "linkedin": 1200,
    "telegram": 900,
    "twitter": 240,
    "tumblr": 700,
    "pinterest": 320,
    "threads": 360,
    "reddit": 1800,
}

SOCIAL_CHANNEL_STYLE = {
    "linkedin": "professional insight post with a clear hook, practical takeaways, and no clickbait",
    "telegram": "direct channel post with short paragraphs and a practical reason to open the article",
    "twitter": "single concise X post, no thread, no hashtags unless essential",
    "tumblr": "short editorial micro-post with a natural blog-style intro",
    "pinterest": "native Pinterest pin description with a visual hook, useful caption, and no clickbait",
    "instagram": "native Instagram carousel caption with concise context, no clickbait, and a clear save/share cue",
    "threads": "native Threads post: conversational, opinionated or question-led, not promotional copy, at most one hashtag",
    "reddit": "community-first Reddit post that asks or answers a concrete problem without marketing language or a generic CTA",
}


def social_channel_editorial_rules(channel):
    rules = {
        "linkedin": "Use 4 to 7 short paragraphs: a specific work situation, one contrarian or useful insight, a practical framework, and a genuine question. Do not use empty thought-leadership language, engagement bait, or more than 3 hashtags.",
        "telegram": "Write a channel-native post: one strong lead line, then 3 to 5 compact practical points. Keep it scannable. End with one calm reason to open the article, never a loud sales CTA.",
        "twitter": "Choose one format that fits the article: sharp observation, contrarian take, micro-framework, or concise question. One post only. No thread, no generic summary, no more than 2 hashtags.",
        "tumblr": "Write an editorial micro-post with a personal but brand-safe voice. It should stand on its own as a small blog note, with a natural transition to the full article.",
        "pinterest": "Use evergreen search language and a clear practical result. The first sentence must state what the reader will get. Avoid time-sensitive promotions, prices, and empty inspiration language.",
        "reddit": "Write as a helpful community member. Lead with the concrete problem or answer, disclose the product/article connection only when relevant, never use sales language, and include a link only when it genuinely answers the question. Do not imitate a subreddit unless its rules are explicitly configured.",
    }
    return rules.get(channel, "Write a concise native post that adds value before asking for attention.")

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "es": "Spanish",
    "de": "German",
    "fr": "French",
}


def social_provider_label(provider):
    return SOCIAL_PROVIDER_CONFIG.get(provider, {}).get("label", provider)


def parse_json_object(value):
    try:
        data = json.loads(value or "{}")
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def get_social_credentials(row):
    return parse_json_object(row["credentials_json"] if row else "{}")


def social_credentials_complete(provider, credentials):
    config = SOCIAL_PROVIDER_CONFIG.get(provider)
    if not config:
        return False
    required = [field[0] for field in config["fields"] if field[2] == "password"]
    if provider == "telegram":
        required = ["bot_token", "chat_id"]
    if provider == "linkedin":
        required = ["access_token"]
    if provider == "zernio":
        return bool(str(credentials.get("api_key") or os.environ.get("ZERNIO_API_KEY") or "").strip())
    if provider == "twitter":
        required = ["bearer_token"]
    if provider == "tumblr":
        required = ["consumer_key", "consumer_secret", "oauth_token", "oauth_token_secret"]
    if provider == "pinterest":
        required = ["access_token", "board_id"]
    if provider == "instagram":
        required = ["api_key", "api_base_url"]
    if provider == "threads":
        required = ["access_token"]
    return all(str(credentials.get(key) or "").strip() for key in required)


def content_job_sources(row):
    return parse_json_object(row["sources_json"] if row and "sources_json" in row.keys() else "{}")


def content_job_language(row, site=None):
    sources = content_job_sources(row)
    language = str(sources.get("language") or "").strip().lower()
    if language:
        return language
    site_languages = []
    if site and "languages" in site.keys():
        site_languages = parse_languages(site["languages"])
    return site_languages[0] if site_languages else "en"


def social_post_url(row):
    return row["published_url"] if row["published_url"] else ""


def social_source_text(row, limit=7000):
    parts = [
        row["title"] if "title" in row.keys() else "",
        row["description"] if "description" in row.keys() else "",
        strip_html_text(row["draft_html"] or "", limit=limit),
    ]
    text = " ".join(part for part in parts if part)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def social_normalize_text(text):
    text = str(text or "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def social_shorten_to_limit(text, max_chars):
    text = social_normalize_text(text)
    if len(text) <= max_chars:
        return text
    if max_chars <= 1:
        return text[:max_chars]
    candidate = text[:max_chars].rstrip()
    sentence_cut = max(candidate.rfind("."), candidate.rfind("!"), candidate.rfind("?"), candidate.rfind("\n"))
    if sentence_cut >= max(40, int(max_chars * 0.55)):
        candidate = candidate[: sentence_cut + 1].rstrip()
    else:
        space_cut = candidate.rfind(" ")
        if space_cut >= max(20, int(max_chars * 0.65)):
            candidate = candidate[:space_cut].rstrip()
    return candidate[:max_chars].rstrip()


def social_utf8_len(text):
    return len(str(text or "").encode("utf-8"))


def social_shorten_to_utf8_limit(text, max_bytes):
    text = social_normalize_text(text)
    if social_utf8_len(text) <= max_bytes:
        return text
    candidate = text
    while candidate and social_utf8_len(candidate) > max_bytes:
        candidate = candidate[:-1].rstrip()
    if not candidate:
        return ""
    sentence_cut = max(candidate.rfind("."), candidate.rfind("!"), candidate.rfind("?"), candidate.rfind("\n"))
    if sentence_cut >= max(20, int(len(candidate) * 0.55)):
        trimmed = candidate[: sentence_cut + 1].rstrip()
        if social_utf8_len(trimmed) <= max_bytes:
            return trimmed
    space_cut = candidate.rfind(" ")
    if space_cut >= max(15, int(len(candidate) * 0.65)):
        trimmed = candidate[:space_cut].rstrip()
        if social_utf8_len(trimmed) <= max_bytes:
            return trimmed
    return candidate


def social_text_with_optional_link(text, article_url, include_link, max_chars):
    text = social_normalize_text(text)
    article_url = (article_url or "").strip()
    if not include_link or not article_url:
        return social_shorten_to_limit(text, max_chars)
    separator = "\n\n"
    link_budget = len(separator) + len(article_url)
    if link_budget >= max_chars:
        return social_shorten_to_limit(article_url, max_chars)
    body = social_shorten_to_limit(text, max_chars - link_budget)
    return social_normalize_text(body + separator + article_url)


def threads_text_with_optional_link(text, article_url, include_link, max_bytes):
    text = social_normalize_text(text)
    article_url = (article_url or "").strip()
    if not include_link or not article_url:
        return social_shorten_to_utf8_limit(text, max_bytes)
    separator = "\n\n"
    link_budget = social_utf8_len(separator + article_url)
    if link_budget >= max_bytes:
        return social_shorten_to_utf8_limit(article_url, max_bytes)
    body = social_shorten_to_utf8_limit(text, max_bytes - link_budget)
    return social_normalize_text(body + separator + article_url)


def fallback_social_post_text(site, job, channel, language, max_chars, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    title = job["title"] or job["topic"] or "New article"
    description = job["description"] or ""
    if language == "ru":
        templates = {
            "linkedin": f"{title}\n\nКоротко о главном: {description}\n\nМатериал от {brand} для тех, кто хочет разобраться в теме без лишней воды.",
            "telegram": f"{title}\n\n{description}\n\nОткрывайте материал, если тема сейчас актуальна.",
            "twitter": f"{title}. {description}",
            "tumblr": f"{title}\n\n{description}\n\nЗаметка от {brand}.",
            "threads": f"{title}\n\n{description}\n\nСохраните, если тема актуальна.",
        }
    elif language == "es":
        templates = {
            "linkedin": f"{title}\n\nIdea clave: {description}\n\nUna guia de {brand} para entender el tema con mas contexto.",
            "telegram": f"{title}\n\n{description}\n\nLee el articulo si este tema es relevante para ti.",
            "twitter": f"{title}. {description}",
            "tumblr": f"{title}\n\n{description}\n\nUna nota de {brand}.",
            "threads": f"{title}\n\n{description}\n\nGuardalo si este tema te resulta util.",
        }
    elif language == "de":
        templates = {
            "linkedin": f"{title}\n\nKurz gesagt: {description}\n\nEin Beitrag von {brand} mit praktischem Kontext.",
            "telegram": f"{title}\n\n{description}\n\nZum Artikel, wenn das Thema gerade relevant ist.",
            "twitter": f"{title}. {description}",
            "tumblr": f"{title}\n\n{description}\n\nEin kurzer Beitrag von {brand}.",
            "threads": f"{title}\n\n{description}\n\nSpeichern, wenn das Thema gerade relevant ist.",
        }
    elif language == "fr":
        templates = {
            "linkedin": f"{title}\n\nPoint cle: {description}\n\nUn guide de {brand} pour replacer le sujet dans son contexte.",
            "telegram": f"{title}\n\n{description}\n\nA lire si le sujet vous concerne.",
            "twitter": f"{title}. {description}",
            "tumblr": f"{title}\n\n{description}\n\nUne note de {brand}.",
            "threads": f"{title}\n\n{description}\n\nA garder si le sujet vous concerne.",
        }
    else:
        templates = {
            "linkedin": f"{title}\n\nKey idea: {description}\n\nA practical guide from {brand} for readers who want the useful context before making a decision.",
            "telegram": f"{title}\n\n{description}\n\nOpen the article if this is on your radar.",
            "twitter": f"{title}. {description}",
            "tumblr": f"{title}\n\n{description}\n\nA short note from {brand}.",
            "threads": f"{title}\n\n{description}\n\nSave this if it is on your radar.",
        }
    fallback = templates.get(channel, templates["linkedin"])
    if channel == "threads":
        return threads_text_with_optional_link(fallback, article_url, include_link, max_chars)
    return social_text_with_optional_link(fallback, article_url, include_link, max_chars)


def build_social_post_prompt(site, job, channel, language, max_chars, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    source_text = social_source_text(job)
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    link_rule = "Include the article URL exactly once at the end." if include_link and article_url else "Do not include any URL."
    return f"""
You are adapting an article into a social media post for {brand}.

CHANNEL:
- channel: {social_provider_label(channel)}
- style: {SOCIAL_CHANNEL_STYLE.get(channel, 'concise social post')}
- hard maximum length: {max_chars} characters, including spaces, punctuation, line breaks, and URL if present
- preferred working length: {SOCIAL_CHANNEL_TARGET_CHARS.get(channel, max_chars)} characters or less when possible
- article URL: {article_url or 'none'}
- link rule: {link_rule}

LANGUAGE:
- Write in {language_name}.
- The social post must use the same language as the article.

ARTICLE:
- title: {job['title'] or job['topic']}
- description: {job['description'] or ''}
- source excerpt: {source_text[:6000]}

RULES:
- Output STRICT JSON only.
- Return one finished post, not variants.
- Stay under the hard maximum. Do not rely on platform truncation.
- For Threads, stay under 500 UTF-8 bytes and use at most one hashtag.
- Do not say "read more" if no URL is included.
- No markdown headings.
- No invented claims, prices, guarantees, statistics, or hashtags unless the article explicitly supports them.
- No em dash or en dash.
- Channel editorial contract: {social_channel_editorial_rules(channel)}

RETURN JSON SHAPE:
{{"text":"final social post text"}}
""".strip()


def validate_social_post_text(text, max_chars):
    char_count = len(text)
    return {
        "ok": char_count <= max_chars,
        "charCount": char_count,
        "maxChars": max_chars,
        "remaining": max_chars - char_count,
    }


def validate_threads_post_text(text, max_bytes):
    byte_count = social_utf8_len(text)
    return {
        "ok": byte_count <= max_bytes,
        "charCount": len(text or ""),
        "byteCount": byte_count,
        "maxBytes": max_bytes,
        "remainingBytes": max_bytes - byte_count,
    }


def build_threads_post_prompt(site, job, language, max_bytes, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    source_text = social_source_text(job, limit=4500)
    link_rule = "Include the article URL only if it still fits naturally." if include_link and article_url else "Do not include any URL."
    return f"""
You are writing a native Threads post for {brand}.

This is not LinkedIn, not an ad, and not a summary paragraph.

LANGUAGE:
- Write in {language_name}.

ARTICLE:
- title: {job['title'] or job['topic']}
- description: {job['description'] or ''}
- source excerpt: {source_text[:4500]}
- article URL: {article_url or 'none'}
- link rule: {link_rule}

THREADS STYLE:
- Choose one conversationFormat: question, observation, contrarian, micro_story, or objection_answer. Pick the one that best fits the article; do not default to a question.
- Hard limit: {max_bytes} UTF-8 bytes.
- Start with the chosen format's strongest natural opening.
- Make it feel like a human thought that invites replies.
- Use 1 to 3 short sentences.
- Do not list benefits.
- Do not sound like paid ad copy.
- Do not say "boost conversions" unless the article context makes it unavoidable.
- Use at most one hashtag, and only if it feels natural.
- No markdown. No variants.

RETURN STRICT JSON ONLY:
{{"text":"final Threads post text","conversationFormat":"observation"}}
""".strip()


def fallback_threads_post_text(site, job, language, include_link, article_url):
    title = job["title"] or job["topic"] or "this"
    if language == "ru":
        text = f"UGC для магазина все еще выглядит как реклама, если в нем нет ощущения реального человека. Что вы проверяете первым: картинку товара или контекст вокруг нее?"
    elif language == "es":
        text = "El UGC generado con IA solo funciona si parece una decision real de compra, no otro anuncio pulido. Que miras primero: el producto o el contexto?"
    elif language == "de":
        text = "AI-UGC funktioniert nur, wenn es nach echter Kaufentscheidung aussieht, nicht nach noch einer glatten Anzeige. Was pruefst du zuerst: Produkt oder Kontext?"
    elif language == "fr":
        text = "L'UGC genere par IA marche seulement s'il ressemble a une vraie decision d'achat, pas a une pub de plus. Vous regardez d'abord le produit ou le contexte?"
    else:
        text = "AI-generated UGC only works when it feels like a real buying moment, not another polished ad. What do you check first: the product or the context around it?"
    return threads_text_with_optional_link(text, article_url, include_link, SOCIAL_CHANNEL_LIMITS["threads"])


def build_threads_image_prompt(site, job, language, text):
    brand = site["brand_name"] or site["domain"]
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    source_text = social_source_text(job, limit=2500)
    return f"""
Create one natural image for a Threads post.

FORMAT:
- Real raster JPEG image.
- Portrait 4:5.
- Looks like a candid/simple social photo, not an ad creative.
- No text overlay, no headline, no logo, no UI screenshot, no poster design.
- No readable text anywhere in the image: no labels, captions, spreadsheet text, app UI words, package text, or phone-screen text.
- If screens or packaging are present, keep them blank, blurred, turned away, or too out-of-focus to read.
- No collage, no infographic, no polished marketing banner.

BRAND AND ARTICLE CONTEXT:
- brand: {brand}
- language context: {language_name}
- article title: {job['title'] or job['topic']}
- article description: {job['description'] or ''}
- Threads post text: {text}
- article excerpt: {source_text[:2500]}

VISUAL DIRECTION:
- Make it feel like a real moment related to the post's question or observation.
- Prefer a simple desk, product-planning, ecommerce workflow, creator workspace, phone/laptop, or behind-the-scenes setup when relevant.
- Keep it understated, useful, and believable for a feed conversation.
""".strip()


def generate_threads_media_image(site_id, job_id, site, job, language, text):
    target_dir = social_asset_job_dir(site_id, job_id, "threads")
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = "image-01.jpg"
    prompt = build_threads_image_prompt(site, job, language, text)
    image_bytes = _gemini_image_jpeg(prompt, aspect_ratio="4:5")
    if not image_bytes.startswith(b"\xff\xd8"):
        raise RuntimeError("Gemini image for Threads media was not JPEG")
    (target_dir / filename).write_bytes(image_bytes)
    return {
        "mediaUrls": [social_asset_url(site_id, job_id, "threads", filename)],
        "mediaSource": "threadsGenerated",
        "mediaMimeType": "image/jpeg",
        "generatedAt": now_iso(),
    }


def generate_threads_post_draft(site_id, job_id, site, job, language, include_link, article_url):
    max_bytes = SOCIAL_CHANNEL_LIMITS["threads"]
    try:
        data = _gemini_text_json(build_threads_post_prompt(site, job, language, max_bytes, include_link, article_url))
        text = social_normalize_text(data.get("text") or "")
    except Exception:
        text = ""
    if not text:
        text = fallback_threads_post_text(site, job, language, include_link, article_url)
    text = threads_text_with_optional_link(text, article_url, include_link, max_bytes)
    validation = validate_threads_post_text(text, max_bytes)
    if not validation["ok"]:
        text = social_shorten_to_utf8_limit(text, max_bytes)
        validation = validate_threads_post_text(text, max_bytes)
    if not validation["ok"]:
        raise ValueError("Threads post exceeds 500 UTF-8 bytes")
    media = generate_threads_media_image(site_id, job_id, site, job, language, text)
    conversation_format = str(data.get("conversationFormat") or "observation").strip().lower().replace("-", "_") if isinstance(data, dict) else "observation"
    if conversation_format not in {"question", "observation", "contrarian", "micro_story", "objection_answer"}:
        conversation_format = "observation"
    return text, validation, {"threads": {**media, "conversationFormat": conversation_format}}


def generate_reddit_post_draft(site, job, language, include_link, article_url, subreddit_rules=""):
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    source_text = social_source_text(job, limit=6000)
    prompt = f"""
You are preparing a useful Reddit post based on an article for {site['brand_name'] or site['domain']}.

LANGUAGE: {language_name}
ARTICLE: {job['title'] or job['topic']}
DESCRIPTION: {job['description'] or ''}
EXCERPT: {source_text}
URL: {article_url or 'none'}
SITE-SPECIFIC SUBREDDIT RULES: {subreddit_rules or 'No additional rules configured. Do not invent any.'}

RULES:
- Write for a community, not as a brand announcement.
- The title must state a real problem or useful question, not promote the company.
- The body must give a self-contained answer, framework, or experience in 3 to 7 short paragraphs.
- Do not use hype, sales language, fake neutrality, or generic "read more" wording.
- Mention the article/source relationship transparently only if it adds context.
- Include the URL at most once, at the end, only when it materially helps.
- Do not invent subreddit rules, statistics, or personal experience.
- Title <= 300 characters. Body <= 8000 characters.
- Return strict JSON only.

{{"title":"...","body":"...","format":"discussion|question|guide"}}
""".strip()
    try:
        data = _gemini_text_json(prompt)
    except Exception:
        data = {}
    title = social_shorten_to_limit(social_normalize_text(data.get("title") or job["title"] or job["topic"] or "Discussion"), 300)
    body = social_normalize_text(data.get("body") or job["description"] or social_source_text(job, limit=1200))
    body = social_text_with_optional_link(body, article_url, include_link, 8000)
    validation = {
        "ok": len(title) <= 300 and len(body) <= 8000,
        "title": {"charCount": len(title), "maxChars": 300},
        "body": {"charCount": len(body), "maxChars": 8000},
    }
    if not validation["ok"]:
        raise ValueError("Reddit draft exceeds title or body limits")
    return body, validation, {"reddit": {"title": title, "body": body, "format": social_shorten_to_limit(data.get("format") or "discussion", 32)}}


def generate_twitter_post_draft(site, job, language, include_link, article_url):
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    source_text = social_source_text(job, limit=4500)
    prompt = f"""
Create a native X post from this article for {site['brand_name'] or site['domain']} in {language_name}.

ARTICLE: {job['title'] or job['topic']}
DESCRIPTION: {job['description'] or ''}
EXCERPT: {source_text}
URL: {article_url or 'none'}

Choose one format: sharp_insight, contrarian_take, micro_framework, statistic_observation, or thread.
- Use statistic_observation only when the article itself provides the exact statistic and source context.
- Use thread only when the article contains a genuinely sequential framework; otherwise one post.
- Each post must be <= 280 characters including any URL.
- No generic summary, no engagement bait, no more than 2 hashtags, and no invented claim.
- Link, when requested, belongs only in the final post.
- Return strict JSON only.

{{"format":"sharp_insight","posts":["..."]}}
""".strip()
    try:
        data = _gemini_text_json(prompt)
    except Exception:
        data = {}
    fmt = str(data.get("format") or "sharp_insight").strip().lower().replace("-", "_") if isinstance(data, dict) else "sharp_insight"
    if fmt not in {"sharp_insight", "contrarian_take", "micro_framework", "statistic_observation", "thread"}:
        fmt = "sharp_insight"
    raw_posts = data.get("posts") if isinstance(data, dict) and isinstance(data.get("posts"), list) else []
    posts = [social_normalize_text(item) for item in raw_posts if social_normalize_text(item)][:5]
    if not posts:
        fallback, _ = generate_social_post_text(site, job, "twitter", language, SOCIAL_CHANNEL_LIMITS["twitter"], include_link, article_url)
        posts = [fallback]
    if fmt != "thread":
        posts = posts[:1]
    if len(posts) < 2:
        fmt = "sharp_insight" if fmt == "thread" else fmt
    normalized = []
    for index, text in enumerate(posts):
        final_link = include_link and index == len(posts) - 1
        normalized.append(social_text_with_optional_link(text, article_url, final_link, SOCIAL_CHANNEL_LIMITS["twitter"]))
    validation = {"ok": all(len(item) <= 280 for item in normalized), "posts": [{"charCount": len(item), "maxChars": 280} for item in normalized], "format": fmt}
    if not validation["ok"]:
        raise ValueError("X draft exceeds 280 characters")
    return normalized[0], validation, {"twitter": {"format": fmt, "threadItems": normalized}}


def generate_editorial_social_image(site_id, job_id, site, job, channel, aspect_ratio, visual_rule):
    target_dir = social_asset_job_dir(site_id, job_id, channel)
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = "image-01.jpg"
    prompt = f"""
Create one finished raster JPEG for a {channel} post.
FORMAT: {aspect_ratio}. {visual_rule}
BRAND: {site['brand_name'] or site['domain']}
ARTICLE: {job['title'] or job['topic']}
DESCRIPTION: {job['description'] or ''}
RULES: Native editorial image, not a generic ad. No logo, fake UI, unreadable microtext, invented statistics, awards, or promotional badges.
""".strip()
    image_bytes = _gemini_image_jpeg(prompt, aspect_ratio=aspect_ratio)
    if not image_bytes.startswith(b"\xff\xd8"):
        raise RuntimeError(f"Gemini image for {channel} was not JPEG")
    (target_dir / filename).write_bytes(image_bytes)
    return {"mediaUrls": [social_asset_url(site_id, job_id, channel, filename)], "mediaMimeType": "image/jpeg", "generatedAt": now_iso()}


def generate_telegram_post_draft(site_id, job_id, site, job, language, include_link, article_url):
    text, validation = generate_social_post_text(site, job, "telegram", language, SOCIAL_CHANNEL_LIMITS["telegram"], include_link, article_url)
    media = generate_editorial_social_image(site_id, job_id, site, job, "telegram", "16:9", "Use a clear editorial scene with no text overlay.")
    return text, validation, {"telegram": {**media, "button": {"label": "Open article", "url": article_url} if include_link and article_url else None}}


def generate_tumblr_post_draft(site_id, job_id, site, job, language, include_link, article_url):
    text, validation = generate_social_post_text(site, job, "tumblr", language, SOCIAL_CHANNEL_LIMITS["tumblr"], include_link, article_url)
    tags = [tag for tag in re.findall(r"[a-z0-9]+", (job["category"] or job["title"] or "").lower()) if len(tag) > 2][:5]
    media = generate_editorial_social_image(site_id, job_id, site, job, "tumblr", "4:5", "Use an expressive editorial/lifestyle visual that feels like an independent blog post, with no text overlay.")
    return text, validation, {"tumblr": {**media, "tags": tags}}


def generate_social_post_text(site, job, channel, language, max_chars, include_link, article_url):
    try:
        data = _gemini_text_json(build_social_post_prompt(site, job, channel, language, max_chars, include_link, article_url))
        text = social_normalize_text(data.get("text") or "")
    except Exception:
        text = ""
    if not text:
        text = fallback_social_post_text(site, job, channel, language, max_chars, include_link, article_url)
    if channel == "threads":
        text = threads_text_with_optional_link(text, article_url, include_link, max_chars)
        validation = validate_threads_post_text(text, max_chars)
        if not validation["ok"]:
            text = social_shorten_to_utf8_limit(text, max_chars)
            validation = validate_threads_post_text(text, max_chars)
        if not validation["ok"]:
            raise ValueError(f"{channel} social post exceeds {max_chars} UTF-8 bytes")
        return text, validation
    text = social_text_with_optional_link(text, article_url, include_link, max_chars)
    validation = validate_social_post_text(text, max_chars)
    if not validation["ok"]:
        text = social_shorten_to_limit(text, max_chars)
        validation = validate_social_post_text(text, max_chars)
    if not validation["ok"]:
        raise ValueError(f"{channel} social post exceeds {max_chars} characters")
    return text, validation


def fallback_pinterest_pin(site, job, language, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    title = social_shorten_to_limit(job["title"] or job["topic"] or "New article", 100)
    description = social_shorten_to_limit(job["description"] or f"A practical guide from {brand}.", SOCIAL_CHANNEL_LIMITS["pinterest"])
    overlay = social_shorten_to_limit(title, 80)
    alt_text = social_shorten_to_limit(f"Pinterest-style vertical image for {title}", 250)
    image_prompt = social_shorten_to_limit(
        f"Create a native Pinterest vertical 2:3 editorial photo for an article titled '{title}' by {brand}. "
        "Use a polished lifestyle/editorial composition, readable visual hierarchy, and space for a short overlay caption. "
        "Avoid logos, UI screenshots, tiny text, and misleading claims.",
        1000,
    )
    pin = {
        "pinTitle": title,
        "description": description,
        "overlayText": overlay,
        "altText": alt_text,
        "imagePrompt": image_prompt,
        "imageAspectRatio": "2:3",
        "recommendedSize": "1000x1500",
        "destinationUrl": article_url if include_link and article_url else "",
    }
    return pin


def build_pinterest_pin_prompt(site, job, language, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    source_text = social_source_text(job, limit=5000)
    link_rule = "Use the article URL as destinationUrl." if include_link and article_url else "Leave destinationUrl empty."
    return f"""
You are adapting an article into a native Pinterest pin creative for {brand}.

GOAL:
- Create one Pinterest-ready pin concept based on the article.
- This is not a generic social text post. It needs a vertical image concept plus native Pinterest title/description/caption text.

LANGUAGE:
- Write pinTitle, description, overlayText, and altText in {language_name}.

ARTICLE:
- title: {job['title'] or job['topic']}
- description: {job['description'] or ''}
- source excerpt: {source_text[:5000]}
- article URL: {article_url or 'none'}
- link rule: {link_rule}

PINTEREST REQUIREMENTS:
- pinTitle max 100 characters.
- description max 500 characters.
- overlayText max 80 characters, designed to sit on the image.
- altText max 250 characters.
- imagePrompt max 1000 characters.
- image must be a native Pinterest vertical 2:3 editorial/lifestyle image concept, recommended 1000x1500.
- imagePrompt must describe the actual visual content to generate: scene, subject, composition, mood, colors, and where overlay text can fit.
- Do not request logos, screenshots, cluttered text, fake UI, false before/after claims, or unsupported statistics.
- No markdown. No variants.

RETURN STRICT JSON ONLY:
{{"pinTitle":"...","description":"...","overlayText":"...","altText":"...","imagePrompt":"...","imageAspectRatio":"2:3","recommendedSize":"1000x1500","destinationUrl":"{article_url if include_link and article_url else ''}"}}
""".strip()


def validate_pinterest_pin(pin):
    limits = {"pinTitle": 100, "description": 500, "overlayText": 80, "altText": 250, "imagePrompt": 1000}
    result = {"ok": True, "limits": limits, "fields": {}}
    for key, limit in limits.items():
        value = social_normalize_text(pin.get(key) or "")
        count = len(value)
        result["fields"][key] = {"charCount": count, "maxChars": limit, "remaining": limit - count}
        if count > limit:
            result["ok"] = False
    return result


def normalize_pinterest_pin(pin, site, job, language, include_link, article_url):
    fallback = fallback_pinterest_pin(site, job, language, include_link, article_url)
    clean = {}
    for key in ("pinTitle", "description", "overlayText", "altText", "imagePrompt"):
        clean[key] = social_normalize_text(pin.get(key) or fallback.get(key) or "")
    clean["pinTitle"] = social_shorten_to_limit(clean["pinTitle"], 100)
    clean["description"] = social_shorten_to_limit(clean["description"], SOCIAL_CHANNEL_LIMITS["pinterest"])
    clean["overlayText"] = social_shorten_to_limit(clean["overlayText"], 80)
    clean["altText"] = social_shorten_to_limit(clean["altText"], 250)
    clean["imagePrompt"] = social_shorten_to_limit(clean["imagePrompt"], 1000)
    clean["imageAspectRatio"] = "2:3"
    clean["recommendedSize"] = "1000x1500"
    clean["destinationUrl"] = article_url if include_link and article_url else ""
    return clean


def generate_pinterest_pin_draft(site, job, language, include_link, article_url):
    try:
        data = _gemini_text_json(build_pinterest_pin_prompt(site, job, language, include_link, article_url))
    except Exception:
        data = {}
    pin = normalize_pinterest_pin(data if isinstance(data, dict) else {}, site, job, language, include_link, article_url)
    validation = validate_pinterest_pin(pin)
    if not validation["ok"]:
        pin = normalize_pinterest_pin(pin, site, job, language, include_link, article_url)
        validation = validate_pinterest_pin(pin)
    if not validation["ok"]:
        raise ValueError("Pinterest pin draft exceeds field limits")
    return pin["description"], validation, {"pin": pin}


def generate_pinterest_pin_image(site_id, job_id, site, job, pin):
    target_dir = social_asset_job_dir(site_id, job_id, "pinterest")
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = "pin-01.jpg"
    prompt = f"""
Create one finished Pinterest image as a real raster JPEG.

FORMAT:
- Vertical 2:3, 1000x1500 composition.
- Editorial, useful and evergreen, not a generic ad.
- Use clear high-contrast typography with safe margins.
- Include this exact short overlay text once: {pin['overlayText']}
- Do not add other readable text, fake UI, unsupported claims, prices, badges, logos, or clutter.

ARTICLE CONTEXT:
- brand: {site['brand_name'] or site['domain']}
- article: {job['title'] or job['topic']}
- visual brief: {pin['imagePrompt']}
""".strip()
    image_bytes = _gemini_image_jpeg(prompt, aspect_ratio="2:3")
    if not image_bytes.startswith(b"\xff\xd8"):
        raise RuntimeError("Gemini image for Pinterest pin was not JPEG")
    (target_dir / filename).write_bytes(image_bytes)
    return {
        "imageUrl": social_asset_url(site_id, job_id, "pinterest", filename),
        "imageMimeType": "image/jpeg",
        "generatedAt": now_iso(),
    }


def fallback_instagram_carousel(site, job, language, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    title = social_shorten_to_limit(job["title"] or job["topic"] or "New article", 90)
    description = social_shorten_to_limit(job["description"] or "", 240)
    caption = social_text_with_optional_link(
        f"{title}\n\n{description}\n\nSave this carousel for later.",
        article_url,
        include_link,
        SOCIAL_CHANNEL_TARGET_CHARS["instagram"],
    )
    slide_templates = [
        ("cover", title, "Swipe for the practical breakdown."),
        ("problem", "The core question", description or "What readers need to understand before they decide."),
        ("insight", "What matters first", "Start with the decision criteria, not generic advice."),
        ("insight", "What to compare", "Look at tradeoffs, timing, cost, and practical fit."),
        ("checklist", "Quick checklist", "Use these points before taking the next step."),
        ("cta", f"Read the full guide", f"More context from {brand}."),
    ]
    slides = []
    for index, (role, headline, subtext) in enumerate(slide_templates, start=1):
        headline = social_shorten_to_limit(headline, 70)
        subtext = social_shorten_to_limit(subtext, 140)
        slides.append({
            "index": index,
            "role": role,
            "headline": headline,
            "subtext": subtext,
            "imagePrompt": social_shorten_to_limit(
                f"Create an Instagram carousel slide background for '{headline}'. "
                f"Brand: {brand}. Editorial, polished, high-contrast, mobile-first 4:5 layout with room for text.",
                700,
            ),
            "altText": social_shorten_to_limit(f"Instagram carousel slide: {headline}. {subtext}", 250),
        })
    return {
        "caption": caption,
        "slides": slides,
        "visualSpec": {"aspectRatio": "4:5", "recommendedSize": "1080x1350", "maxSlides": 10},
        "destinationUrl": article_url if include_link and article_url else "",
    }


def build_instagram_carousel_prompt(site, job, language, include_link, article_url):
    brand = site["brand_name"] or site["domain"]
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    source_text = social_source_text(job, limit=6500)
    link_rule = "Include the article URL exactly once at the end of caption." if include_link and article_url else "Do not include any URL."
    target_chars = SOCIAL_CHANNEL_TARGET_CHARS["instagram"]
    hard_limit = SOCIAL_CHANNEL_LIMITS["instagram"]
    return f"""
You are turning an article into a native Instagram carousel for {brand}.

GOAL:
- Create one Instagram carousel draft with 5 to 8 slides.
- This must feel native to Instagram: short slide text, visual storytelling, useful saveable content.
- Do not copy long article paragraphs onto slides.

LANGUAGE:
- Write caption and all slide text in {language_name}.

ARTICLE:
- title: {job['title'] or job['topic']}
- description: {job['description'] or ''}
- source excerpt: {source_text[:6500]}
- article URL: {article_url or 'none'}
- link rule: {link_rule}

CAROUSEL RULES:
- Choose exactly one carouselType: checklist, myth_reality, framework, before_after, mistakes, or decision_guide.
- Use 4:5 portrait format, recommended 1080x1350.
- Make 5 to 8 slides, never more than 10.
- Slide 1 must be a cover.
- Slide 1 must state a specific tension, outcome, or decision. It cannot merely repeat the article title.
- Each following slide must carry one distinct claim. Do not restate the cover or another slide.
- Order slides so the reader gets increasing value: context, insight/framework, application, then CTA.
- Last slide must be a soft CTA or save/share cue.
- The final CTA must not repeat the caption wording.
- Every slide headline <= 70 characters.
- Every slide subtext <= 140 characters.
- Every slide imagePrompt <= 700 characters and must describe the visual background/scene for that slide.
- Every slide altText <= 250 characters.
- Caption target <= {target_chars} characters.
- Caption hard maximum <= {hard_limit} characters.
- Keep caption compact: 1 short hook, 1-2 useful context lines, 1 save/share CTA, and at most 3 hashtags.
- Do not summarize every slide in the caption; the slides already carry the detail.
- No unsupported claims, fake statistics, fake screenshots, tiny text, or cluttered UI.
- No markdown. No variants.

RETURN STRICT JSON ONLY:
{{
  "caption":"...",
  "carouselType":"checklist",
  "visualSpec":{{"aspectRatio":"4:5","recommendedSize":"1080x1350","maxSlides":10}},
  "destinationUrl":"{article_url if include_link and article_url else ''}",
  "slides":[
    {{"index":1,"role":"cover","headline":"...","subtext":"...","imagePrompt":"...","altText":"..."}}
  ]
}}
""".strip()


def normalize_instagram_carousel(carousel, site, job, language, include_link, article_url):
    fallback = fallback_instagram_carousel(site, job, language, include_link, article_url)
    if not isinstance(carousel, dict):
        carousel = {}
    caption = social_normalize_text(carousel.get("caption") or fallback["caption"])
    caption = social_text_with_optional_link(caption, article_url, include_link, SOCIAL_CHANNEL_TARGET_CHARS["instagram"])
    raw_slides = carousel.get("slides") if isinstance(carousel.get("slides"), list) else fallback["slides"]
    slides = []
    for idx, raw in enumerate(raw_slides[:10], start=1):
        if not isinstance(raw, dict):
            continue
        headline = social_shorten_to_limit(raw.get("headline") or fallback["slides"][min(idx - 1, len(fallback["slides"]) - 1)]["headline"], 70)
        subtext = social_shorten_to_limit(raw.get("subtext") or "", 140)
        image_prompt = social_shorten_to_limit(raw.get("imagePrompt") or raw.get("visualPrompt") or "", 700)
        if not image_prompt:
            image_prompt = social_shorten_to_limit(
                f"Instagram carousel 4:5 editorial slide for '{headline}', clean mobile composition, strong contrast, room for overlay text.",
                700,
            )
        slides.append({
            "index": len(slides) + 1,
            "role": social_shorten_to_limit(raw.get("role") or ("cover" if idx == 1 else "insight"), 32).lower(),
            "headline": headline,
            "subtext": subtext,
            "imagePrompt": image_prompt,
            "altText": social_shorten_to_limit(raw.get("altText") or f"{headline}. {subtext}", 250),
        })
    if len(slides) < 5:
        for raw in fallback["slides"][len(slides):]:
            slides.append({**raw, "index": len(slides) + 1})
            if len(slides) >= 5:
                break
    return {
        "caption": caption,
        "carouselType": str(carousel.get("carouselType") or "framework").strip().lower().replace("-", "_")[:32],
        "slides": slides[:10],
        "visualSpec": {"aspectRatio": "4:5", "recommendedSize": "1080x1350", "maxSlides": 10},
        "destinationUrl": article_url if include_link and article_url else "",
    }


def validate_instagram_carousel(carousel):
    result = {
        "ok": True,
        "caption": {
            "charCount": len(carousel.get("caption") or ""),
            "maxChars": SOCIAL_CHANNEL_LIMITS["instagram"],
            "targetChars": SOCIAL_CHANNEL_TARGET_CHARS["instagram"],
        },
        "slides": [],
        "slideCount": len(carousel.get("slides") or []),
        "maxSlides": 10,
        "carouselType": carousel.get("carouselType") or "",
    }
    if result["caption"]["charCount"] > SOCIAL_CHANNEL_LIMITS["instagram"]:
        result["ok"] = False
    if result["slideCount"] < 2 or result["slideCount"] > 10:
        result["ok"] = False
    if result["carouselType"] not in {"checklist", "myth_reality", "framework", "before_after", "mistakes", "decision_guide"}:
        result["ok"] = False
    slides = carousel.get("slides") or []
    if slides and str(slides[0].get("role") or "").lower() != "cover":
        result["ok"] = False
    if slides and str(slides[-1].get("role") or "").lower() not in {"cta", "save", "share"}:
        result["ok"] = False
    normalized_claims = []
    for slide in slides:
        claim = re.sub(r"[^a-z0-9]+", " ", (slide.get("headline") or "").lower()).strip()
        if claim and claim in normalized_claims:
            result["ok"] = False
        normalized_claims.append(claim)
    if slides and re.sub(r"\W+", "", slides[-1].get("headline") or "").lower() in re.sub(r"\W+", "", carousel.get("caption") or "").lower():
        result["ok"] = False
    for slide in carousel.get("slides") or []:
        row = {
            "index": slide.get("index"),
            "headline": {"charCount": len(slide.get("headline") or ""), "maxChars": 70},
            "subtext": {"charCount": len(slide.get("subtext") or ""), "maxChars": 140},
            "imagePrompt": {"charCount": len(slide.get("imagePrompt") or ""), "maxChars": 700},
            "altText": {"charCount": len(slide.get("altText") or ""), "maxChars": 250},
        }
        if any(item["charCount"] > item["maxChars"] for key, item in row.items() if isinstance(item, dict)):
            result["ok"] = False
        result["slides"].append(row)
    return result


def generate_instagram_carousel_draft(site, job, language, include_link, article_url):
    try:
        data = _gemini_text_json(build_instagram_carousel_prompt(site, job, language, include_link, article_url))
    except Exception:
        data = {}
    carousel = normalize_instagram_carousel(data if isinstance(data, dict) else {}, site, job, language, include_link, article_url)
    validation = validate_instagram_carousel(carousel)
    if not validation["ok"]:
        carousel = normalize_instagram_carousel(carousel, site, job, language, include_link, article_url)
        validation = validate_instagram_carousel(carousel)
    if not validation["ok"]:
        raise ValueError("Instagram carousel draft exceeds slide or caption limits")
    return carousel["caption"], validation, {"instagramCarousel": carousel}


def social_asset_job_dir(site_id, job_id, channel):
    safe_job = re.sub(r"[^A-Za-z0-9_.-]", "_", str(job_id))
    safe_channel = re.sub(r"[^A-Za-z0-9_.-]", "_", str(channel))
    return SOCIAL_ASSET_DIR / str(int(site_id)) / safe_job / safe_channel


def social_asset_url(site_id, job_id, channel, filename):
    return f"/sites/{int(site_id)}/social-assets/{urllib.parse.quote(str(job_id), safe='')}/{urllib.parse.quote(channel, safe='')}/{urllib.parse.quote(filename, safe='')}"


def build_instagram_slide_image_prompt(site, job, language, slide, slide_count):
    brand = site["brand_name"] or site["domain"]
    language_name = LANGUAGE_NAMES.get(language, language.upper())
    title = job["title"] or job["topic"] or "Article"
    headline = slide.get("headline") or title
    subtext = slide.get("subtext") or ""
    image_prompt = slide.get("imagePrompt") or ""
    return f"""
Create one finished Instagram carousel slide as a real raster JPEG image.

FORMAT:
- Portrait 4:5 Instagram carousel slide.
- Clean editorial/mobile composition, not a website screenshot.
- The image itself must include readable overlay text.
- No SVG, no wireframe, no placeholder, no fake UI.

BRAND AND ARTICLE:
- brand: {brand}
- article title: {title}
- language for visible text: {language_name}
- slide: {slide.get('index')} of {slide_count}
- slide role: {slide.get('role') or 'insight'}

VISIBLE TEXT TO PLACE ON THE IMAGE:
- headline, exactly: {headline}
- supporting line, exactly: {subtext}

VISUAL DIRECTION:
{image_prompt}

QUALITY RULES:
- Keep text large, sharp, high-contrast, and centered or aligned with clear safe margins.
- Do not add extra small paragraphs or unreadable microtext.
- Do not invent logos, statistics, prices, awards, UI screenshots, or people endorsements.
- Make it ready to publish as one Instagram carousel slide.
""".strip()


def generate_instagram_carousel_images(site_id, job_id, site, job, language, carousel):
    slides = carousel.get("slides") or []
    if not slides:
        return carousel
    target_dir = social_asset_job_dir(site_id, job_id, "instagram")
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    for index, slide in enumerate(slides, start=1):
        filename = f"slide-{index:02d}.jpg"
        prompt = build_instagram_slide_image_prompt(site, job, language, slide, len(slides))
        image_bytes = _gemini_image_jpeg(prompt, aspect_ratio="4:5")
        if not image_bytes.startswith(b"\xff\xd8"):
            raise RuntimeError(f"Gemini image for Instagram slide {index} was not JPEG")
        (target_dir / filename).write_bytes(image_bytes)
        slide["imageStatus"] = "generated"
        slide["imageMimeType"] = "image/jpeg"
        slide["imageUrl"] = social_asset_url(site_id, job_id, "instagram", filename)
        slide["generatedAt"] = now_iso()
    carousel["visualSpec"] = {
        **(carousel.get("visualSpec") if isinstance(carousel.get("visualSpec"), dict) else {}),
        "aspectRatio": "4:5",
        "recommendedSize": "1080x1350",
        "assetFormat": "jpeg",
        "generator": os.environ.get("GEMINI_IMAGE_MODEL") or "gemini-3.1-flash-image",
    }
    return carousel


def generate_social_drafts(site_id, job_id, channels=None):
    site = get_site(site_id)
    if not site:
        raise KeyError("site not found")
    with db() as conn:
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
    if not job:
        raise KeyError("job not found")
    auto = get_autopublish_settings(site_id)
    allowed_channels = active_social_channels(site_id, channels)
    if not allowed_channels:
        raise ValueError("No social channels are configured and selected for this site. Configure and test channels in Setup, then select them in Distribution.")
    language = content_job_language(job, site)
    article_url = social_post_url(job)
    now = now_iso()
    results = []
    status_updates = {}
    with db() as conn:
        for channel in allowed_channels:
            include_link = bool(auto[f"{channel}_include_link"] if f"{channel}_include_link" in auto.keys() else 0)
            max_chars = SOCIAL_CHANNEL_LIMITS[channel]
            extra_payload = {}
            if channel == "pinterest":
                text, validation, extra_payload = generate_pinterest_pin_draft(site, job, language, include_link, article_url)
                extra_payload["pin"].update(generate_pinterest_pin_image(site_id, job_id, site, job, extra_payload["pin"]))
                char_count = validation["fields"]["description"]["charCount"]
            elif channel == "instagram":
                text, validation, extra_payload = generate_instagram_carousel_draft(site, job, language, include_link, article_url)
                extra_payload["instagramCarousel"] = generate_instagram_carousel_images(
                    site_id,
                    job_id,
                    site,
                    job,
                    language,
                    extra_payload["instagramCarousel"],
                )
                char_count = validation["caption"]["charCount"]
            elif channel == "threads":
                text, validation, extra_payload = generate_threads_post_draft(site_id, job_id, site, job, language, include_link, article_url)
                char_count = validation["byteCount"]
            elif channel == "reddit":
                zernio_credentials = get_social_credentials(get_social_connections(site_id).get("zernio"))
                text, validation, extra_payload = generate_reddit_post_draft(site, job, language, include_link, article_url, zernio_credentials.get("reddit_rules") or "")
                char_count = validation["body"]["charCount"]
            elif channel == "twitter":
                text, validation, extra_payload = generate_twitter_post_draft(site, job, language, include_link, article_url)
                char_count = validation["posts"][0]["charCount"]
            elif channel == "telegram":
                text, validation, extra_payload = generate_telegram_post_draft(site_id, job_id, site, job, language, include_link, article_url)
                char_count = validation["charCount"]
            elif channel == "tumblr":
                text, validation, extra_payload = generate_tumblr_post_draft(site_id, job_id, site, job, language, include_link, article_url)
                char_count = validation["charCount"]
            else:
                text, validation = generate_social_post_text(site, job, channel, language, max_chars, include_link, article_url)
                char_count = validation["charCount"]
            payload = {
                "source": "gemini_or_fallback",
                "channel": channel,
                "language": language,
                "maxChars": max_chars,
                "includeLink": include_link,
                "articleUrl": article_url,
                "validation": validation,
                **extra_payload,
            }
            cursor = conn.execute(
                """
                insert into social_posts(
                    site_id, job_id, channel, content_text, content_json, remote_url, status,
                    language, max_chars, char_count, include_link, validation_json, created_at, updated_at
                ) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    site_id,
                    job_id,
                    channel,
                    text,
                    json.dumps(payload, ensure_ascii=False),
                    "",
                    "DRAFT",
                    language,
                    max_chars,
                    char_count,
                    1 if include_link else 0,
                    json.dumps(validation, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            status_updates[f"{channel}_status"] = "drafted"
            result = {"channel": channel, "language": language, "charCount": char_count, "maxChars": max_chars, "text": text}
            if channel == "pinterest":
                result.update(extra_payload)
            if channel == "instagram":
                result.update(extra_payload)
                result["previewUrl"] = f"/sites/{int(site_id)}/social-posts/{int(cursor.lastrowid)}/instagram-carousel"
            if channel == "threads":
                result.update(extra_payload)
            results.append(result)
        if status_updates:
            assignments = ", ".join(f"{key}=?" for key in status_updates)
            conn.execute(
                f"update content_jobs set {assignments}, updated_at=? where site_id=? and id=?",
                [*status_updates.values(), now, site_id, job_id],
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (site_id, job_id, now, "INFO", "social-drafts", f"Prepared social drafts for {', '.join(allowed_channels)}"),
            )
    return {"ok": True, "jobId": job_id, "language": language, "drafts": results}


def absolute_social_asset_url(value):
    value = str(value or "").strip()
    if not value:
        return ""
    return value if value.startswith(("https://", "http://")) else f"{BLOG_CORE_PUBLIC_URL}{value}"


def zernio_media_items(channel, payload):
    if channel == "instagram":
        carousel = payload.get("instagramCarousel") or {}
        return [{"type": "image", "url": absolute_social_asset_url(slide.get("imageUrl"))} for slide in carousel.get("slides") or [] if slide.get("imageUrl")]
    if channel == "threads":
        return [{"type": "image", "url": absolute_social_asset_url(url)} for url in ((payload.get("threads") or {}).get("mediaUrls") or []) if url]
    if channel == "pinterest":
        image_url = (payload.get("pin") or {}).get("imageUrl")
        return [{"type": "image", "url": absolute_social_asset_url(image_url)}] if image_url else []
    return []


def publish_zernio_social_drafts(site_id, job_id, scheduled_for=None):
    connections = get_social_connections(site_id)
    zernio = connections.get("zernio")
    credentials = get_social_credentials(zernio)
    if not zernio or zernio["status"] not in {"configured", "connected"} or not social_credentials_complete("zernio", credentials):
        raise ValueError("Configure and test Zernio in Setup before publishing these channels.")
    api_key = str(credentials.get("api_key") or os.environ.get("ZERNIO_API_KEY") or "").strip()
    with db() as conn:
        rows = conn.execute(
            """select * from social_posts where site_id=? and job_id=? and status='DRAFT'
               and channel in ('twitter','pinterest','instagram','threads','reddit') order by id asc""",
            (site_id, job_id),
        ).fetchall()
    if not rows:
        raise ValueError("No unpublished Zernio social drafts are ready for this content task.")
    results = []
    for row in rows:
        channel = row["channel"]
        account_id = str(credentials.get(f"{channel}_account_id") or "").strip()
        if not account_id:
            results.append({"channel": channel, "ok": False, "error": "Missing Zernio account mapping."})
            continue
        payload = parse_json_object(row["content_json"])
        platform = {"channel": channel, "accountId": account_id}
        if channel == "twitter":
            thread_items = ((payload.get("twitter") or {}).get("threadItems") or [])
            if len(thread_items) > 1:
                platform["platformSpecificData"] = {"threadItems": [{"content": item} for item in thread_items]}
        if channel == "pinterest" and credentials.get("pinterest_board_id"):
            platform["platformSpecificData"] = {"boardId": credentials["pinterest_board_id"]}
        if channel == "reddit":
            subreddit = str(credentials.get("reddit_subreddit") or "").strip().removeprefix("r/")
            if not subreddit:
                results.append({"channel": channel, "ok": False, "error": "Missing default subreddit."})
                continue
            platform["platformSpecificData"] = {
                "subreddit": subreddit,
                "title": ((payload.get("reddit") or {}).get("title") or row["content_text"] or "Discussion")[:300],
            }
        request_payload = {
            "content": row["content_text"] or "",
            "platforms": [platform],
            "publishNow": not bool(scheduled_for),
        }
        if scheduled_for:
            request_payload["scheduledFor"] = scheduled_for
        media_items = zernio_media_items(channel, payload)
        if media_items:
            request_payload["mediaItems"] = media_items
        try:
            response, _ = fetch_json_request(
                f"{ZERNIO_API_BASE}/posts",
                headers={"Authorization": f"Bearer {api_key}"},
                data=request_payload,
                method="POST",
                timeout=60,
            )
            post = response.get("post") if isinstance(response, dict) else {}
            remote_url = str((post or {}).get("url") or (post or {}).get("permalink") or "")
            remote_id = str((post or {}).get("_id") or (post or {}).get("id") or "")
            if not remote_id and isinstance(response, dict) and response.get("error"):
                raise RuntimeError(str(response.get("error")))
            status = "SCHEDULED" if scheduled_for else "SENT"
            with db() as conn:
                conn.execute("update social_posts set status=?, remote_url=?, updated_at=? where id=?", (status, remote_url or remote_id, now_iso(), row["id"]))
            results.append({"channel": channel, "ok": True, "status": status, "remoteUrl": remote_url or remote_id})
        except Exception as e:
            with db() as conn:
                conn.execute("update social_posts set status='ERROR', updated_at=? where id=?", (now_iso(), row["id"]))
            results.append({"channel": channel, "ok": False, "error": str(e)[:300]})
    successful = [item for item in results if item.get("ok")]
    with db() as conn:
        for item in successful:
            channel = item["channel"]
            conn.execute(
                f"update content_jobs set {channel}_status=?, {channel}_post_url=?, {channel}_posted_at=?, updated_at=? where site_id=? and id=?",
                (item["status"].lower(), item.get("remoteUrl") or "", now_iso(), now_iso(), site_id, job_id),
            )
        conn.execute(
            "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
            (site_id, job_id, now_iso(), "INFO" if successful else "ERROR", "zernio-publish", f"Zernio sent/scheduled {len(successful)} of {len(results)} social drafts"),
        )
    return {"ok": bool(successful), "jobId": job_id, "results": results}


def upsert_social_connection(site_id, provider, credentials=None, status=None, display_name=None, settings=None):
    if provider not in SOCIAL_PROVIDER_CONFIG:
        raise ValueError("unsupported provider")
    now = now_iso()
    with db() as conn:
        current = conn.execute("select * from social_connections where site_id=? and provider=?", (site_id, provider)).fetchone()
        current_credentials = get_social_credentials(current)
        merged_credentials = dict(current_credentials)
        if credentials:
            for key, value in credentials.items():
                if value is not None and str(value).strip() != "":
                    merged_credentials[key] = str(value).strip()
        current_settings = parse_json_object(current["settings_json"] if current else "{}")
        merged_settings = {**current_settings, **(settings or {})}
        final_status = status or (current["status"] if current else None)
        if not final_status:
            final_status = "configured" if social_credentials_complete(provider, merged_credentials) else "disconnected"
        conn.execute(
            """
            insert into social_connections(site_id, provider, status, display_name, credentials_json, settings_json, connected_at, updated_at)
            values(?,?,?,?,?,?,?,?)
            on conflict(site_id, provider) do update set
                status=excluded.status,
                display_name=coalesce(excluded.display_name, social_connections.display_name),
                credentials_json=excluded.credentials_json,
                settings_json=excluded.settings_json,
                connected_at=case when excluded.status='connected' then coalesce(social_connections.connected_at, excluded.connected_at) else social_connections.connected_at end,
                updated_at=excluded.updated_at
            """,
            (
                site_id,
                provider,
                final_status,
                display_name,
                json.dumps(merged_credentials, ensure_ascii=False),
                json.dumps(merged_settings, ensure_ascii=False),
                now if final_status == "connected" else None,
                now,
            ),
        )
    return {"provider": provider, "status": final_status, "configured": social_credentials_complete(provider, merged_credentials)}


def simple_slug(text):
    slug = re.sub(r"[^a-z0-9\s-]", "", (text or "").lower())
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug[:90] or "article"


def path_slug(text):
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:120] or "article"


def normalize_public_article_url(url):
    clean = (url or "").strip()
    if not clean:
        return ""
    parsed = urllib.parse.urlsplit(clean)
    path = parsed.path or "/"
    if path != "/" and not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, "", ""))


def is_probable_article_url(url, site):
    if not url:
        return False
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if domain_from_url(url) != site["domain"]:
        return False
    blog_path = (site["blog_path"] or "/blog/").strip() or "/blog/"
    if not blog_path.startswith("/"):
        blog_path = "/" + blog_path
    if not blog_path.endswith("/"):
        blog_path += "/"
    path = parsed.path or "/"
    if not path.startswith(blog_path):
        return False
    if path.rstrip("/") == blog_path.rstrip("/"):
        return False
    last = path.rsplit("/", 1)[-1].lower()
    if re.search(r"\.(xml|css|js|json|png|jpe?g|webp|gif|svg|pdf|zip|mp4|mov)$", last):
        return False
    return True


IMPORT_CONTENT_PREFIXES = (
    "/blog/",
    "/ru/blog/",
    "/es/blog/",
    "/de/blog/",
    "/fr/blog/",
    "/wine-countries/",
    "/ru/wine-countries/",
    "/es/wine-countries/",
    "/de/wine-countries/",
    "/fr/wine-countries/",
    "/wine-regions/",
    "/ru/wine-regions/",
    "/es/wine-regions/",
    "/de/wine-regions/",
    "/fr/wine-regions/",
)

CONTENT_HUB_PATHS = {prefix for prefix in IMPORT_CONTENT_PREFIXES}


def normalized_url_path(url):
    path = urllib.parse.urlsplit(url or "").path or "/"
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def is_imported_content_hub(row):
    status = row["status"] if "status" in row.keys() else ""
    if status != "IMPORTED":
        return False
    published_path = normalized_url_path(row["published_url"] if "published_url" in row.keys() else "")
    if published_path in CONTENT_HUB_PATHS:
        return True
    try:
        sources = json.loads(row["sources_json"] or "{}")
    except Exception:
        sources = {}
    relative_path = str(sources.get("relativePath") or "").lstrip("/")
    return relative_path in {path.lstrip("/") + "index.html" for path in CONTENT_HUB_PATHS}


def import_page_type(path):
    if "/blog/" in path or path.startswith("/blog/"):
        return "blog"
    return "seo_money_page"


def import_page_language(path):
    first = path.strip("/").split("/", 1)[0]
    return first if first in {"ru", "es", "de", "fr"} else "en"


def is_importable_existing_content_url(url, site):
    if not url:
        return False
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if domain_from_url(url) != site["domain"]:
        return False
    path = parsed.path or "/"
    if re.search(r"\.(xml|css|js|json|png|jpe?g|webp|gif|svg|pdf|zip|mp4|mov)$", path.rsplit("/", 1)[-1].lower()):
        return False
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in IMPORT_CONTENT_PREFIXES)


def parse_sitemap_locs(xml_text):
    locs = []
    try:
        root = ET.fromstring(xml_text)
        for node in root.findall(".//{*}loc"):
            loc = (node.text or "").strip()
            if loc:
                locs.append(loc)
    except Exception:
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", xml_text or "", flags=re.I | re.S):
            locs.append(re.sub(r"\s+", "", loc))
    return locs


def site_base_url(site):
    return normalize_url(site["homepage_url"]).rstrip("/")


def local_file_to_public_url(site, root_path, file_path, parser=None):
    rel = file_path.relative_to(root_path).as_posix()
    if rel == "index.html":
        route = "/"
    elif rel.endswith("/index.html"):
        route = "/" + rel[: -len("index.html")]
    elif rel.endswith(".html"):
        route = "/" + rel[:-5] + "/"
    else:
        route = "/" + rel
    fallback = site_base_url(site) + route
    canonical = (parser.canonical if parser else "") or ""
    if canonical.startswith(site_base_url(site)):
        return normalize_public_article_url(canonical)
    return normalize_public_article_url(fallback)


def candidate_local_import_file(root_path, url):
    parsed = urllib.parse.urlsplit(url)
    route = urllib.parse.unquote(parsed.path or "/")
    rel = route.lstrip("/")
    candidates = []
    if not rel:
        candidates.append(root_path / "index.html")
    if route.endswith("/"):
        candidates.append(root_path / rel / "index.html")
        if rel:
            candidates.append(root_path / f"{rel.rstrip('/')}.html")
    else:
        candidates.append(root_path / rel)
        candidates.append(root_path / f"{rel}.html")
        candidates.append(root_path / rel / "index.html")
    try:
        root_resolved = root_path.resolve()
    except OSError:
        return None
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if root_resolved == resolved or root_resolved in resolved.parents:
            if resolved.is_file() and resolved.suffix.lower() in {".html", ".htm"}:
                return resolved
    return None


def discover_existing_content_from_webroot(site, limit=2000):
    root_value = (site["root_path"] or "").strip()
    if not root_value:
        return None
    root_path = Path(root_value)
    if not root_path.exists() or not root_path.is_dir():
        return None
    candidates = []
    duplicate_files = []
    warnings = []
    for file_path in sorted(root_path.rglob("*.html")):
        try:
            rel = file_path.relative_to(root_path).as_posix()
        except ValueError:
            continue
        if not any(rel.startswith(prefix.lstrip("/")) for prefix in IMPORT_CONTENT_PREFIXES):
            continue
        try:
            html = file_path.read_text(errors="ignore")
            parser = ExistingArticleParser()
            parser.feed(html[:250000])
            url = local_file_to_public_url(site, root_path, file_path, parser)
            if not is_importable_existing_content_url(url, site):
                continue
            current = next((item for item in candidates if item["url"] == url), None)
            item = {
                "url": url,
                "slug": path_slug(urllib.parse.urlsplit(url).path.strip("/") or parser.title or rel),
                "path": rel,
                "pageType": import_page_type("/" + rel),
                "language": import_page_language("/" + rel),
            }
            if current:
                duplicate_files.append({"url": url, "kept": current["path"], "duplicate": rel})
                if current["path"].endswith("/index.html") and not rel.endswith("/index.html"):
                    current.update(item)
                continue
            candidates.append(item)
        except Exception as e:
            warnings.append(f"{rel}: {e}")
        if len(candidates) >= limit:
            break
    return {"articles": candidates[:limit], "warnings": warnings[:5], "source": "local_webroot", "duplicates": duplicate_files[:20]}


def discover_existing_blog_articles(site, limit=2000):
    local_result = discover_existing_content_from_webroot(site, limit=limit)
    if local_result:
        return local_result
    base = normalize_url(site["homepage_url"]).rstrip("/")
    candidates = []
    warnings = []
    sitemap_urls = [f"{base}/sitemap_index.xml", f"{base}/sitemap.xml", f"{base}/sitemap-blog.xml", f"{base}/blog/sitemap.xml"]
    seen_sitemaps = set()
    for sitemap_url in sitemap_urls:
        if sitemap_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sitemap_url)
        try:
            xml, _ = fetch_url(sitemap_url)
            for loc in parse_sitemap_locs(xml):
                absolute = normalize_public_article_url(absolutize(base + "/", loc))
                if absolute.endswith(".xml") and absolute not in seen_sitemaps and len(seen_sitemaps) < 20:
                    sitemap_urls.append(absolute)
                    continue
                if is_importable_existing_content_url(absolute, site) and absolute not in candidates:
                    candidates.append(absolute)
        except Exception as e:
            warnings.append(f"{sitemap_url}: {e}")
        if len(candidates) >= limit:
            break
    if len(candidates) < limit:
        try:
            blog_url = urllib.parse.urljoin(base + "/", (site["blog_path"] or "/blog/").lstrip("/"))
            html, _ = fetch_url(blog_url)
            parser = ExistingArticleParser()
            parser.feed(html)
            for href in parser.links:
                absolute = normalize_public_article_url(absolutize(blog_url, href))
                if is_importable_existing_content_url(absolute, site) and absolute not in candidates:
                    candidates.append(absolute)
                if len(candidates) >= limit:
                    break
        except Exception as e:
            warnings.append(f"blog index: {e}")
    articles = []
    for url in candidates[:limit]:
        path = urllib.parse.urlsplit(url).path or "/"
        articles.append({
            "url": url,
            "slug": path_slug(path.strip("/") or urllib.parse.urlsplit(url).netloc),
            "pageType": import_page_type(path),
            "language": import_page_language(path),
        })
    return {"articles": articles, "warnings": warnings[:5], "source": "public_fetch"}


def extract_existing_article(url):
    html, headers = fetch_url(url)
    parser = ExistingArticleParser()
    parser.feed(html)
    canonical = normalize_public_article_url(absolutize(url, parser.canonical or url))
    title = re.sub(r"\s+", " ", (parser.title or "").strip())[:220]
    description = re.sub(r"\s+", " ", (parser.description or "").strip())[:320]
    article_html = absolutize_html_attrs(url, parser.article_html or "")[:500000]
    if not article_html:
        body_match = re.search(r"(?is)<body[^>]*>(.*?)</body>", html)
        article_html = absolutize_html_attrs(url, body_match.group(1) if body_match else html)[:500000]
    return {
        "url": normalize_public_article_url(url),
        "canonical": canonical,
        "title": title or urllib.parse.urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title(),
        "description": description,
        "heroImage": absolutize(url, parser.og_image) if parser.og_image else "",
        "contentHtml": article_html,
        "contentType": headers.get("content-type", ""),
    }


def extract_existing_article_from_webroot(site, url):
    root_value = (site["root_path"] or "").strip()
    if not root_value:
        return None
    root_path = Path(root_value)
    file_path = candidate_local_import_file(root_path, url)
    if not file_path:
        return None
    html = file_path.read_text(errors="ignore")
    parser = ExistingArticleParser()
    parser.feed(html)
    canonical = normalize_public_article_url(absolutize(url, parser.canonical or url))
    if domain_from_url(canonical) != site["domain"]:
        canonical = normalize_public_article_url(url)
    title = re.sub(r"\s+", " ", (parser.title or "").strip())[:220]
    description = re.sub(r"\s+", " ", (parser.description or "").strip())[:320]
    article_html = absolutize_html_attrs(canonical, parser.article_html or "")[:500000]
    if not article_html:
        body_match = re.search(r"(?is)<body[^>]*>(.*?)</body>", html)
        article_html = absolutize_html_attrs(canonical, body_match.group(1) if body_match else html)[:500000]
    rel = file_path.relative_to(root_path).as_posix()
    return {
        "url": normalize_public_article_url(url),
        "canonical": canonical,
        "title": title or urllib.parse.urlsplit(canonical).path.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title(),
        "description": description,
        "heroImage": absolutize(canonical, parser.og_image) if parser.og_image else "",
        "contentHtml": article_html,
        "contentType": "text/html; charset=utf-8",
        "importMethod": "direct_webroot",
        "webrootPath": str(file_path),
        "relativePath": rel,
        "pageType": import_page_type("/" + rel),
        "language": import_page_language("/" + rel),
    }


def import_existing_articles(site_id, urls):
    site = get_site(site_id)
    if not site:
        raise KeyError("site not found")
    imported = []
    skipped = []
    errors = []
    unique_urls = []
    for url in urls:
        clean = normalize_public_article_url(absolutize(site["homepage_url"], str(url or "")))
        if is_importable_existing_content_url(clean, site) and clean not in unique_urls:
            unique_urls.append(clean)
    with db() as conn:
        existing = {
            normalize_public_article_url(r["published_url"] or "")
            for r in conn.execute("select published_url from content_jobs where site_id=? and published_url is not null and published_url <> ''", (site_id,)).fetchall()
        }
    for url in unique_urls[:2000]:
        if url in existing:
            skipped.append({"url": url, "reason": "already imported"})
            continue
        try:
            article = extract_existing_article_from_webroot(site, url) or extract_existing_article(url)
            path_for_slug = urllib.parse.urlsplit(article["canonical"] or article["url"]).path.strip("/")
            slug = path_slug(path_for_slug or article["title"])
            job_id = secrets.token_hex(12)
            now = now_iso()
            source = {
                "imported": True,
                "importMethod": article.get("importMethod", "public_fetch"),
                "sourceUrl": article["url"],
                "canonical": article["canonical"],
                "contentType": article["contentType"],
                "webrootPath": article.get("webrootPath", ""),
                "relativePath": article.get("relativePath", ""),
                "pageType": article.get("pageType", import_page_type(urllib.parse.urlsplit(article["canonical"] or article["url"]).path)),
                "language": article.get("language", import_page_language(urllib.parse.urlsplit(article["canonical"] or article["url"]).path)),
                "ownership": "source_site_authoritative",
            }
            page_type = source["pageType"]
            with db() as conn:
                conn.execute(
                    """
                    insert into content_jobs(
                        id, site_id, topic, slug, status, title, description, category,
                        hero_image, draft_html, sources_json, visibility, published_url, created_at, updated_at
                    ) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        job_id,
                        site_id,
                        article["title"],
                        slug,
                        "IMPORTED",
                        article["title"],
                        article["description"],
                        "Imported Blog" if page_type == "blog" else "Imported SEO Money Page",
                        article["heroImage"],
                        article["contentHtml"],
                        json.dumps(source, ensure_ascii=False),
                        "public",
                        article["canonical"] or article["url"],
                        now,
                        now,
                    ),
                )
                conn.execute(
                    "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                    (site_id, job_id, now, "INFO", "import", f"Imported existing article from {url}"),
                )
            imported.append({"id": job_id, "url": url, "title": article["title"], "slug": slug})
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
    return {"imported": imported, "skipped": skipped, "errors": errors}


def summarize_job_message(kind, message):
    raw = message or ""
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except Exception:
        text = re.sub(r"\s+", " ", raw).strip()
        return text[:500] + ("..." if len(text) > 500 else "")

    if kind in {"import-existing-blog", "import-existing-blog-direct-webroot"}:
        imported = data.get("imported", [])
        skipped = data.get("skipped", [])
        errors = data.get("errors", [])
        parts = []
        if "candidates" in data:
            parts.append(f"candidates {data.get('candidates')}")
        if "distinct_urls" in data:
            parts.append(f"distinct URLs {data.get('distinct_urls')}")
        if "inserted" in data:
            parts.append(f"inserted {data.get('inserted')}")
        else:
            parts.append(f"imported {len(imported)}")
        if "skipped_existing" in data:
            parts.append(f"skipped existing {data.get('skipped_existing')}")
        else:
            parts.append(f"skipped {len(skipped)}")
        parts.append(f"errors {len(errors)}")
        if "duplicate_files" in data:
            parts.append(f"duplicate files {data.get('duplicate_files')}")
        detail = "; ".join(parts) + "."
        sample = []
        for item in imported[:3]:
            sample.append(item.get("url") or item.get("rel") or item.get("title") or "")
        for item in errors[:3]:
            sample.append((item.get("url") or "") + ": " + (item.get("error") or "error"))
        sample = [s for s in sample if s]
        if sample:
            detail += " Sample: " + " | ".join(sample)
        return detail

    if kind == "article-ideas":
        signals = data.get("signals", [])
        ideas = data.get("ideas", [])
        titles = [idea.get("title") for idea in ideas[:3] if idea.get("title")]
        detail = f"range {data.get('range', 'unknown')}; signals {len(signals)}; ideas {len(ideas)}."
        if titles:
            detail += " " + " | ".join(titles)
        return detail

    if isinstance(data, dict):
        return "; ".join(f"{k}={v}" for k, v in data.items() if not isinstance(v, (list, dict)))[:500]
    return raw[:500]


def render_jobs(rows):
    if not rows:
        return "<div class='empty'>No publish jobs yet.</div>"
    out = []
    for row in rows:
        message = summarize_job_message(row["kind"], row["message"])
        out.append(
            f"""
            <div class="job-row">
              <div><strong>{escape(row['kind'])}</strong><span>{escape(row['created_at'])}</span></div>
              <b class="status {escape(row['status'])}">{escape(row['status'])}</b>
              <p>{escape(message)}</p>
            </div>
            """
        )
    return "".join(out)


def render_content_pagination(meta):
    total = int(meta.get("total") or 0)
    page = int(meta.get("page") or 1)
    total_pages = int(meta.get("total_pages") or 1)
    language = meta.get("language") or "all"
    content_type = meta.get("content_type") or "all"
    lang_q = "" if language == "all" else f"&content_lang={escape(language, quote=True)}"
    type_q = "" if content_type == "all" else f"&content_type={escape(content_type, quote=True)}"
    if not total or total_pages <= 1:
        return ""
    links = []
    if page > 1:
        links.append(f"<a class='page-link nav' href='?content_page={page - 1}{lang_q}{type_q}#content'>‹</a>")
    window_start = max(1, page - 2)
    window_end = min(total_pages, page + 2)
    for page_number in range(window_start, window_end + 1):
        active = " active" if page_number == page else ""
        links.append(f"<a class='page-link{active}' href='?content_page={page_number}{lang_q}{type_q}#content'>{page_number}</a>")
    if page < total_pages:
        links.append(f"<a class='page-link nav' href='?content_page={page + 1}{lang_q}{type_q}#content'>›</a>")
    return f"""
    <nav class="content-pagination" aria-label="Content pages">{''.join(links)}</nav>
    """


def render_content_filter_toolbar(meta):
    current = meta.get("language") or "en"
    languages = meta.get("available_languages") or []
    content_type = meta.get("content_type") or "all"
    content_types = meta.get("available_content_types") or []
    labels = {"en": "EN", "ru": "RU", "es": "ES", "de": "DE", "fr": "FR"}
    type_labels = {
        "all": "All",
        "blog": "Blog",
        "seo_money_page": "SEO money",
        "home": "Home",
        "other": "Other",
    }
    language_links = []
    for lang in languages:
        active = " active" if lang == current else ""
        type_q = "" if content_type == "all" else f"&content_type={escape(content_type, quote=True)}"
        href = f"?content_page=1&content_lang={escape(lang, quote=True)}{type_q}#content"
        language_links.append(f"<a class='lang-chip{active}' href='{href}'>{escape(labels.get(lang, lang.upper()))}</a>")
    type_links = []
    for type_name in ["all", *content_types]:
        active = " active" if type_name == content_type else ""
        lang_q = "" if current == "all" else f"&content_lang={escape(current, quote=True)}"
        href = f"?content_page=1{lang_q}&content_type={escape(type_name, quote=True)}#content"
        if type_name == "all":
            href = f"?content_page=1{lang_q}#content"
        type_links.append(f"<a class='type-chip{active}' href='{href}'>{escape(type_labels.get(type_name, type_name.replace('_', ' ').title()))}</a>")
    return (
        "<div class='content-toolbar'>"
        "<div class='language-switcher' aria-label='Content language'>" + "".join(language_links) + "</div>"
        "<div class='type-switcher' aria-label='Content type'>" + "".join(type_links) + "</div>"
        "</div>"
    )


def social_icon_label(channel):
    return {
        "linkedin": "in",
        "telegram": "tg",
        "twitter": "X",
        "tumblr": "t",
        "pinterest": "P",
        "instagram": "ig",
        "threads": "th",
        "reddit": "rd",
    }.get(channel, channel[:2])


def social_status_class(status):
    normalized = (status or "not queued").strip().lower().replace("_", " ").replace("-", " ")
    if normalized in {"published", "posted", "sent", "done", "completed", "success"}:
        return "published"
    if normalized in {"queued", "scheduled", "pending", "processing", "drafted", "draft"}:
        return "queued"
    if normalized in {"failed", "error"}:
        return "failed"
    return "muted"


def render_social_statuses(row):
    items = []
    for channel in ("linkedin", "telegram", "twitter", "tumblr", "pinterest", "instagram", "threads", "reddit"):
        status = row[f"{channel}_status"] or "not queued"
        status_class = social_status_class(status)
        label = social_icon_label(channel)
        title = f"{channel}: {status}"
        items.append(
            f"<span class='social-icon {escape(channel)} {status_class}' title='{escape(title, quote=True)}' aria-label='{escape(title, quote=True)}'>{escape(label)}</span>"
        )
    return "<div class='social-statuses' aria-label='Social publishing status'>" + "".join(items) + "</div>"


def render_content_type_badge(row):
    category = (row["category"] or "").strip().lower()
    try:
        sources = json.loads(row["sources_json"] or "{}")
    except Exception:
        sources = {}
    page_type = str(sources.get("pageType") or "").strip().lower()
    if "seo money" in category or page_type == "seo_money_page":
        return "<span class='content-type-badge seo'>SEO money page</span>"
    if "blog" in category or page_type == "blog":
        return "<span class='content-type-badge blog'>Blog</span>"
    return f"<span class='content-type-badge other'>{escape(row['category'] or 'Content')}</span>"


def planned_job_meta(row):
    try:
        sources = json.loads(row["sources_json"] or "{}")
    except Exception:
        sources = {}
    language = str(sources.get("language") or sources.get("locale") or "").strip().upper()
    target_path = str(sources.get("targetPath") or "").strip()
    if not target_path and row["published_url"]:
        target_path = normalized_url_path(row["published_url"])
    parts = []
    if language:
        parts.append(f"<span class='planned-chip'>{escape(language)}</span>")
    if target_path:
        parts.append(f"<span class='planned-target'>{escape(target_path)}</span>")
    return "".join(parts)


def planned_group_key(row):
    sources = content_job_sources(row)
    canonical = str(sources.get("canonicalGroup") or "").strip()
    content_type = str(sources.get("contentType") or "").strip()
    page_kind = str(sources.get("pageKind") or "").strip()
    if canonical:
        return (content_type, page_kind, canonical)
    return (content_type, page_kind, content_job_base_path(row) or row["slug"] or row["id"])


def planned_group_id_from_key(key):
    raw = json.dumps(list(key), ensure_ascii=False, sort_keys=True)
    return sha1(raw.encode("utf-8")).hexdigest()[:16]


def planned_group_id(row):
    return planned_group_id_from_key(planned_group_key(row))


def planned_row_language(row):
    sources = content_job_sources(row)
    language = str(sources.get("language") or sources.get("locale") or "").strip().lower()
    return language or content_job_language(row)


def group_planned_rows(rows, site_languages):
    groups = []
    by_key = {}
    site_languages = site_languages or ["en"]
    for row in rows:
        key = planned_group_key(row)
        group = by_key.get(key)
        if not group:
            group = {"id": planned_group_id_from_key(key), "key": key, "rows": [], "languages": set(), "primary": row}
            by_key[key] = group
            groups.append(group)
        group["rows"].append(row)
        language = planned_row_language(row)
        if language:
            group["languages"].add(language)
        primary_language = planned_row_language(group["primary"])
        if language in site_languages and primary_language not in site_languages:
            group["primary"] = row
        elif language == site_languages[0] and primary_language != site_languages[0]:
            group["primary"] = row
    return groups


def planned_group_status(rows):
    statuses = {row["status"] for row in rows}
    for status in ("ERROR", "GENERATING", "DRAFT", "QUEUED"):
        if status in statuses:
            return status
    return rows[0]["status"] or "UNKNOWN"


def planned_group_meta(group, site_languages):
    primary = group["primary"]
    active_languages = [lang.upper() for lang in site_languages if lang]
    legacy_languages = sorted(lang.upper() for lang in group["languages"] if lang and lang not in set(site_languages))
    parts = []
    if active_languages:
        parts.append(f"<span class='planned-chip'>Generates: {escape(', '.join(active_languages))}</span>")
    if legacy_languages:
        parts.append(f"<span class='planned-chip muted-chip'>Legacy variants: {escape(', '.join(legacy_languages))}</span>")
    primary_meta = planned_job_meta(primary)
    return "".join(parts) + primary_meta


def live_page_icon(url):
    if not url:
        return ""
    return f"<a class='icon-btn external-link' target='_blank' href='{escape(url, quote=True)}' title='Open live page' aria-label='Open live page'>↗</a>"


def social_draft_button(site_id, job_id):
    if not active_social_channels(site_id):
        return ""
    return f"<button class='ghost mini-action social-draft-action' type='button' onclick=\"generateSocialDrafts('{escape(job_id, quote=True)}')\" title='Prepare social posts for configured channels'>Social drafts</button>"


def zernio_publish_button(site_id, job_id):
    with db() as conn:
        row = conn.execute(
            """select 1 from social_posts where site_id=? and job_id=? and status='DRAFT'
               and channel in ('twitter','pinterest','instagram','threads','reddit') limit 1""",
            (site_id, job_id),
        ).fetchone()
    if not row:
        return ""
    return f"<button class='ghost mini-action publish-action' type='button' onclick=\"publishZernioSocial('{escape(job_id, quote=True)}')\" title='Publish ready social drafts through Zernio'>Publish social</button>"


def social_review_button(site_id, job_id):
    with db() as conn:
        row = conn.execute(
            "select id from social_posts where site_id=? and job_id=? order by id desc limit 1",
            (site_id, job_id),
        ).fetchone()
    return f"<a class='ghost mini-action social-preview-action' target='_blank' href='/sites/{int(site_id)}/social-posts/{int(row['id'])}'>Social review</a>" if row else ""


def instagram_carousel_preview_button(site_id, job_id):
    with db() as conn:
        row = conn.execute(
            "select id from social_posts where site_id=? and job_id=? and channel='instagram' and status='DRAFT' order by id desc limit 1",
            (site_id, job_id),
        ).fetchone()
    if not row:
        return ""
    return f"<a class='ghost mini-action social-preview-action' target='_blank' href='/sites/{int(site_id)}/social-posts/{int(row['id'])}/instagram-carousel'>IG carousel</a>"


def threads_post_preview_button(site_id, job_id):
    with db() as conn:
        row = conn.execute(
            "select id from social_posts where site_id=? and job_id=? and channel='threads' and status='DRAFT' order by id desc limit 1",
            (site_id, job_id),
        ).fetchone()
    if not row:
        return ""
    return f"<a class='ghost mini-action social-preview-action' target='_blank' href='/sites/{int(site_id)}/social-posts/{int(row['id'])}/threads'>Threads</a>"


def draft_preview_button(site_id, job_id):
    return f"<a class='ghost mini-action draft-preview-action' target='_blank' href='/sites/{int(site_id)}/content-jobs/{escape(job_id, quote=True)}/preview'>Preview draft</a>"


def regenerate_draft_button(job_id):
    return f"<button class='ghost mini-action' type='button' onclick=\"generateArticleJob('{escape(job_id, quote=True)}', 'Regenerating draft')\">Regenerate draft</button>"


def publish_draft_button(job_id):
    return f"<button class='ghost mini-action publish-action' type='button' onclick=\"publishArticleJob('{escape(job_id, quote=True)}')\">Publish</button>"


def generating_progress_panel(job_id):
    safe_id = escape(job_id, quote=True)
    return f"""
    <div class="generation-progress" data-generating-job-id="{safe_id}">
      <div class="generation-progress-head">
        <span class="generation-spinner" aria-hidden="true"></span>
        <span class="generation-progress-title">Generating draft</span>
        <span class="generation-progress-time" data-generation-elapsed>working...</span>
      </div>
      <div class="generation-progress-bar"><span></span></div>
      <div class="generation-progress-note" data-generation-note>Source factory is generating this task. Keep this page open or come back later.</div>
    </div>
    """


def render_social_credentials_setup(site_id):
    connections = get_social_connections(site_id)
    cards = []
    for provider in ("zernio", "linkedin", "telegram", "tumblr"):
        config = SOCIAL_PROVIDER_CONFIG[provider]
        row = connections.get(provider)
        credentials = get_social_credentials(row)
        status = row["status"] if row else "disconnected"
        display_name = row["display_name"] if row and row["display_name"] else ""
        status_class = "connected" if status == "connected" else ("configured" if status == "configured" else "disconnected")
        fields = []
        for key, label, input_type, placeholder in config["fields"]:
            saved = bool(credentials.get(key))
            effective_placeholder = "Saved. Leave blank to keep." if saved and input_type == "password" else placeholder
            value = "" if input_type == "password" else escape(credentials.get(key, ""), quote=True)
            fields.append(
                f"""
                <div class="field">
                  <label>{escape(label)}</label>
                  <input type="{escape(input_type)}" name="{escape(key)}" value="{value}" placeholder="{escape(effective_placeholder, quote=True)}" autocomplete="off">
                </div>
                """
            )
        meta = f" · {escape(display_name)}" if display_name else ""
        connect_action = ""
        if provider == "linkedin" and linkedin_oauth_configured():
            connect_action = f"<button class='ghost mini-action' type='button' onclick=\"connectLinkedIn({int(site_id)})\">Connect LinkedIn</button>"
        cards.append(
            f"""
            <form class="social-credentials-card" data-provider="{escape(provider)}" onsubmit="saveSocialCredentials(event, '{escape(provider)}')">
              <div class="channel-head">
                <div><strong>{escape(config['label'])}</strong><span class="channel-state {status_class}">{escape(status)}{meta}</span></div>
                {connect_action}<button class="ghost mini-action" type="button" onclick="testSocialConnection('{escape(provider)}')">Test connect</button>
              </div>
              <div class="social-credential-fields">{''.join(fields)}</div>
              <div class="actions">
                <button type="submit">Save credentials</button>
              </div>
            </form>
            """
        )
    return f"""
    <section class="stat social-credentials-panel">
      <h2>Social channel credentials</h2>
      <div class="muted">Zernio connects X, Pinterest, Instagram, Threads, and Reddit. LinkedIn, Telegram, and Tumblr remain separate direct connections. Secrets are stored locally and never rendered back into the page.</div>
      <div class="social-credentials-grid">{''.join(cards)}</div>
    </section>
    """


def render_planned_publications(rows, site_languages=None):
    if not rows:
        return "<div class='planned-empty'>No planned Blog Core publications yet.</div>"
    site_languages = site_languages or ["en"]
    groups = group_planned_rows(rows, site_languages)
    items = [
        """
        <div class="planned-bulkbar">
          <label class="planned-select-all"><input type="checkbox" onchange="togglePlannedSelection(this.checked)"> Select all</label>
          <div class="actions">
            <button class="ghost mini-action" type="button" onclick="bulkPlannedAction('generate')">Generate / regenerate selected</button>
            <button class="ghost mini-action danger-lite" type="button" onclick="bulkPlannedAction('delete')">Delete selected</button>
          </div>
          <div id="bulkProgress" class="bulk-progress" hidden></div>
        </div>
        """
    ]
    for group in groups:
        row = group["primary"]
        status = planned_group_status(group["rows"])
        status_class = escape(status.lower())
        title = row["title"] or row["topic"] or "Untitled"
        source = "Discovery idea" if row["category"] == "Article Ideas" else (row["category"] or "Content task")
        duplicate_note = f" · {len(group['rows'])} language variants collapsed" if len(group["rows"]) > 1 else ""
        meta = planned_group_meta(group, site_languages)
        errors = [r["error"] for r in group["rows"] if "error" in r.keys() and r["error"]]
        error_note = f"<div class='planned-error'>{escape(errors[0])}</div>" if status == "ERROR" and errors else ""
        action = ""
        if status in {"QUEUED", "ERROR"}:
            action = f"<button class='ghost mini-action' type='button' onclick=\"generateArticleJob('{escape(row['id'], quote=True)}', 'Generating draft')\">Generate</button>"
        elif status == "GENERATING":
            action = generating_progress_panel(row["id"])
        elif status == "DRAFT":
            action = regenerate_draft_button(row["id"]) + draft_preview_button(row["site_id"], row["id"]) + publish_draft_button(row["id"]) + instagram_carousel_preview_button(row["site_id"], row["id"]) + threads_post_preview_button(row["site_id"], row["id"]) + social_draft_button(row["site_id"], row["id"]) + social_review_button(row["site_id"], row["id"]) + zernio_publish_button(row["site_id"], row["id"])
        items.append(
            f"""
            <div class="planned-row {status_class}" data-group-id="{escape(group['id'], quote=True)}" data-job-id="{escape(row['id'], quote=True)}" data-status="{status_class}">
              <label class="planned-check"><input type="checkbox" class="planned-select" value="{escape(group['id'], quote=True)}" data-job-id="{escape(row['id'], quote=True)}" aria-label="Select planned task"></label>
              <div><strong>{escape(title)}</strong><span>{escape(source)} · {escape(row['created_at'] or '')}{escape(duplicate_note)}</span><div class="planned-meta">{render_content_type_badge(row)}{meta}</div>{error_note}</div>
              <div class="actions"><b class="status {status_class}">{escape(status)}</b>{action}</div>
            </div>
            """
        )
    return "".join(items)


def render_content_jobs(content_page):
    rows = content_page["rows"]
    toolbar = render_content_filter_toolbar(content_page)
    if not rows:
        return toolbar + "<div class='empty'>No content records found for these filters.</div>"
    out = []
    for row in rows:
        title = row["title"] or row["topic"]
        social_statuses = render_social_statuses(row)
        status = row["status"] or ""
        status_class = escape(status.lower())
        if status == "IMPORTED":
            status_label = "LIVE / IMPORTED"
            action = instagram_carousel_preview_button(row["site_id"], row["id"]) + threads_post_preview_button(row["site_id"], row["id"]) + social_draft_button(row["site_id"], row["id"]) + live_page_icon(row["published_url"])
            descriptor = "Already published on the source site"
        elif status in {"QUEUED", "ERROR"}:
            status_label = status
            action = f"<button class='ghost' type='button' onclick=\"generateArticleJob('{escape(row['id'], quote=True)}', 'Generating draft')\">Generate draft</button>"
            descriptor = "New Blog Core task"
        elif status == "GENERATING":
            status_label = "GENERATING"
            action = generating_progress_panel(row["id"])
            descriptor = "Generation in progress"
        elif status == "DRAFT":
            status_label = "DRAFT"
            action = regenerate_draft_button(row["id"]) + draft_preview_button(row["site_id"], row["id"]) + publish_draft_button(row["id"]) + instagram_carousel_preview_button(row["site_id"], row["id"]) + threads_post_preview_button(row["site_id"], row["id"]) + social_draft_button(row["site_id"], row["id"]) + social_review_button(row["site_id"], row["id"]) + zernio_publish_button(row["site_id"], row["id"])
            descriptor = "Draft ready for review"
        elif status == "PUBLISHED":
            status_label = "PUBLISHED"
            action = instagram_carousel_preview_button(row["site_id"], row["id"]) + threads_post_preview_button(row["site_id"], row["id"]) + social_draft_button(row["site_id"], row["id"]) + live_page_icon(row["published_url"])
            descriptor = "Published by Blog Core"
        else:
            status_label = status or "UNKNOWN"
            action = ""
            descriptor = "Content record"
        out.append(
            f"""
            <div class="job-row production-job">
              <div><strong>{escape(title)}</strong><span>{escape(descriptor)} · {escape(row['published_url'] or 'not published yet')}</span></div>
              <div class="actions">{render_content_type_badge(row)}<b class="status {status_class}">{escape(status_label)}</b>{action}</div>
              <p>{escape(row['description'] or row['topic'] or '')}</p>
              {social_statuses}
            </div>
            """
        )
    return toolbar + "".join(out) + render_content_pagination(content_page)


def render_distribution_settings(site_id):
    site = get_site(site_id)
    site_languages = parse_languages(site["languages"] if site else "[]")
    auto = get_autopublish_settings(site_id)
    disc = get_topic_discovery_settings(site_id)
    connections = get_social_connections(site_id)
    planned_publications = render_planned_publications(get_planned_content_jobs(site_id), site_languages)
    try:
        selected = set(json.loads(auto["channels_json"] or "[]"))
    except Exception:
        selected = {"linkedin", "telegram", "twitter", "tumblr", "pinterest", "instagram", "threads"}
    channel_cards = []
    for provider in SOCIAL_CHANNEL_LIMITS:
        label = SOCIAL_CHANNEL_LABELS.get(provider, provider)
        status, setup_label = social_channel_connection_state(site_id, provider, connections)
        checked = "checked" if provider in selected else ""
        include_field = f"{provider}_include_link"
        include_checked = "checked" if int(auto[include_field] or 0) else ""
        status_class = "connected" if status == "connected" else ("configured" if status == "configured" else "disconnected")
        channel_cards.append(
            f"""
            <div class="channel-card unified-channel">
              <div class="channel-head">
                <div><strong>{label}</strong><span class="channel-state {status_class}">{escape(status)}</span></div>
                <span class="connect-placeholder" title="Open Setup to enter credentials and test this channel">{escape(setup_label)}</span>
              </div>
              <label class="check compact"><input type="checkbox" name="channels" value="{provider}" {checked}> Use for autopublish</label>
              <label class="check compact"><input type="checkbox" name="{include_field}" {include_checked}> Include article link</label>
            </div>
            """
        )
    return f"""
    <section class="panel production-panel">
      <div class="panel-title-row"><div><h2>Distribution and autopublish</h2><div class="muted">Same publishing controls as the YAS Wine factory, scoped to this connected site.</div></div></div>
      <form class="form-grid" onsubmit="saveFactorySettings(event)">
        <div class="field"><label>Discovery direction</label><input name="direction" value="{escape(disc['direction'] or '', quote=True)}" placeholder="Auto-detected from site scan"><div class="hint">Gemini fills this from the scanned site; edit only to override.</div></div>
        <div class="field"><label>Category hint</label><input name="category_hint" value="{escape(disc['category_hint'] or '', quote=True)}" placeholder="Auto-detected editorial categories"><div class="hint">Used to steer topic discovery and article categories.</div></div>
        <div class="field"><label>Topics per run</label><input name="per_run_limit" type="number" min="1" max="50" value="{int(disc['per_run_limit'] or 15)}"></div>
        <div class="field"><label>Top N to queue</label><input name="top_n" type="number" min="1" max="20" value="{int(disc['top_n'] or 3)}"></div>
        <label class="check"><input type="checkbox" name="discovery_enabled" {'checked' if int(disc['enabled'] or 0) else ''}> Auto-discover topics</label>
        <label class="check"><input type="checkbox" name="autopublish_enabled" {'checked' if int(auto['enabled'] or 0) else ''}> Autopublish approved articles</label>
        <div class="field"><label>Times per day</label><input name="times_per_day" type="number" min="1" max="12" value="{int(auto['times_per_day'] or 3)}"></div>
        <div class="field"><label>Timezone</label><input name="timezone" value="{escape(auto['timezone'] or 'UTC', quote=True)}"></div>
        <div class="field"><label>Start hour</label><input name="start_hour" type="number" min="0" max="23" value="{int(auto['start_hour'] or 9)}"></div>
        <div class="field"><label>End hour</label><input name="end_hour" type="number" min="0" max="23" value="{int(auto['end_hour'] or 21)}"></div>
        <div class="field full"><label>Channels</label><div class="channel-grid unified-channels">{''.join(channel_cards)}</div><div class="hint">Enter and test per-site credentials in Setup. Distribution controls decide which connected channels autopublish uses.</div></div>
        <div class="actions full"><button type="submit">Save factory distribution settings</button></div>
      </form>
      <div class="planned-publications-block">
        <h3>Planned publications</h3>
        <div class="hint">Queued drafts and generated article tasks waiting for the publishing pipeline.</div>
        <div class="planned-list">{planned_publications}</div>
      </div>
    </section>
    """


PODCAST_VOICES = ("Kore", "Puck", "Aoede", "Charon", "Fenrir", "Leda", "Orus", "Zephyr")


def get_podcast_settings(site_id):
    with db() as conn:
        row = conn.execute("select * from podcast_settings where site_id=?", (site_id,)).fetchone()
    return row


def podcast_asset_dir(site_id, episode_id):
    return PODCAST_ASSET_DIR / str(int(site_id)) / re.sub(r"[^A-Za-z0-9_.-]", "_", str(episode_id))


def podcast_audio_url(site_id, episode_id, filename):
    return f"/sites/{int(site_id)}/podcasts/{urllib.parse.quote(str(episode_id), safe='')}/audio/{urllib.parse.quote(str(filename), safe='')}"


def podcast_public_url(site_id, episode_id):
    return f"{BLOG_CORE_PUBLIC_URL}/podcasts/{int(site_id)}/{urllib.parse.quote(str(episode_id), safe='')}"


def podcast_rss_url(site_id):
    return f"{BLOG_CORE_PUBLIC_URL}/podcasts/{int(site_id)}/feed.xml"


def render_podcast_panel(site_id):
    settings = get_podcast_settings(site_id)
    enabled = "checked" if settings and int(settings["enabled"] or 0) else ""
    voice = (settings["voice_name"] if settings else "Kore") or "Kore"
    voice_options = "".join(f"<option value='{name}' {'selected' if name == voice else ''}>{name}</option>" for name in PODCAST_VOICES)
    with db() as conn:
        episodes = conn.execute(
            """select pe.*, cj.title as article_title from podcast_episodes pe
               left join content_jobs cj on cj.id=pe.job_id and cj.site_id=pe.site_id
               where pe.site_id=? order by pe.created_at desc limit 40""",
            (site_id,),
        ).fetchall()
        source_jobs = conn.execute(
            """select id, title, topic, status from content_jobs
               where site_id=? and status in ('DRAFT','PUBLISHED','IMPORTED')
               order by updated_at desc limit 100""",
            (site_id,),
        ).fetchall()
    source_options = "".join(
        f"<option value='{escape(row['id'], quote=True)}'>{escape(row['title'] or row['topic'] or row['id'])} · {escape(row['status'])}</option>"
        for row in source_jobs
    ) or "<option value=''>No generated or imported articles available</option>"
    rows = []
    for episode in episodes:
        audio = podcast_audio_url(site_id, episode["id"], episode["audio_filename"]) if episode["audio_filename"] else ""
        review = f"<audio controls preload='none' src='{escape(audio, quote=True)}'></audio>" if audio else "<span class='muted'>Audio not ready</span>"
        publish = ""
        if episode["status"] == "READY":
            publish = f"<button class='ghost mini-action' type='button' onclick=\"publishPodcast('{escape(episode['id'], quote=True)}')\">Publish episode</button>"
        public = f"<a class='ghost mini-action' target='_blank' href='{escape(episode['published_url'], quote=True)}'>Open episode</a>" if episode["published_url"] else ""
        error = f"<div class='planned-error'>{escape(episode['error'])}</div>" if episode["error"] else ""
        rows.append(f"""
        <article class='podcast-row'>
          <div><strong>{escape(episode['title'])}</strong><span>{escape(episode['article_title'] or 'Source article unavailable')} · {escape(episode['language'])} · {escape(episode['status'])}</span>{error}</div>
          <div class='podcast-actions'>{review}{publish}{public}</div>
        </article>""")
    episode_list = "".join(rows) or "<div class='planned-empty'>No podcast episodes yet. Select an article to create the first reviewable episode.</div>"
    return f"""
    <section class='panel production-panel podcast-panel'>
      <div class='panel-title-row'><div><h2>Podcast production</h2><div class='muted'>Turn a finished article into a narrated episode. Script, audio, review, and publishing remain separate actions.</div></div></div>
      <form id='podcastSettingsForm' class='form-grid' onsubmit='savePodcastSettings(event)'>
        <label class='check full'><input type='checkbox' name='enabled' {enabled}> Enable podcasts for this site</label>
        <div class='field'><label>Host name</label><input name='host_name' value='{escape((settings['host_name'] if settings else '') or '', quote=True)}' placeholder='Brand podcast host'></div>
        <div class='field'><label>Gemini voice</label><select name='voice_name'>{voice_options}</select><div class='hint'>A per-site Gemini voice profile. This is a supported Gemini voice, not voice cloning.</div></div>
        <div class='field'><label>Target minutes</label><input name='target_minutes' type='number' min='3' max='20' value='{int(settings['target_minutes'] if settings else 8)}'></div>
        <div class='field'><label>Voice direction</label><input name='voice_direction' value='{escape((settings['voice_direction'] if settings else '') or '', quote=True)}' placeholder='Warm, confident, deliberate, conversational'></div>
        <div class='actions full'><button type='submit'>Save podcast settings</button></div>
      </form>
      <div class='podcast-create'>
        <div class='field'><label>Source article</label><select id='podcastSourceJob'>{source_options}</select></div>
        <div class='actions'><button type='button' onclick='generatePodcast()'>Generate podcast episode</button></div>
        <div id='podcastProgress' class='podcast-progress' hidden></div>
      </div>
      <div class='podcast-list'>{episode_list}</div>
      <div class='hint'>Published episodes are hosted by Blog Core at stable episode URLs and included in <a target='_blank' href='{escape(podcast_rss_url(site_id), quote=True)}'>the podcast RSS feed</a>. Native source-site embedding requires that site's own factory adapter.</div>
    </section>
    """


def render_site_switcher(current_site_id):
    with db() as conn:
        rows = conn.execute("select id, domain, brand_name from sites order by updated_at desc").fetchall()
    if len(rows) <= 1:
        return ""
    options = []
    for row in rows:
        label = row["brand_name"] or row["domain"]
        selected = " selected" if row["id"] == current_site_id else ""
        options.append(f'<option value="/sites/{row["id"]}"{selected}>{escape(label)} · {escape(row["domain"])}</option>')
    return "<label class=\"site-switcher\"><span>Switch site</span><select onchange=\"if(this.value) location.href=this.value\">" + "".join(options) + "</select></label>"


def imported_inventory_count(site_id):
    with db() as conn:
        row = conn.execute(
            "select count(*) as count from content_jobs where site_id=? and status='IMPORTED'",
            (site_id,),
        ).fetchone()
    return int(row["count"] or 0) if row else 0


def site_live_blog_url(site):
    blog_path = (site["blog_path"] or "/blog/").strip() or "/blog/"
    if not blog_path.startswith("/"):
        blog_path = "/" + blog_path
    if not blog_path.endswith("/"):
        blog_path += "/"
    return urllib.parse.urljoin(site_base_url(site) + "/", blog_path.lstrip("/"))


def render_primary_site_link(site):
    if imported_inventory_count(site["id"]):
        return f"<a class='btn ghost' target='_blank' href='{escape(site_live_blog_url(site), quote=True)}'>Open live blog</a>"
    if site["preview_path"]:
        return f"<a class='btn ghost' target='_blank' href='{escape(site['preview_path'], quote=True)}'>Open preview</a>"
    return "<span class='muted'>Build preview first</span>"


def render_manage_site_page(site):
    jobs = render_jobs(get_site_jobs(site["id"]))
    content_page = get_content_jobs(
        site["id"],
        page=request.args.get("content_page", 1),
        language=request.args.get("content_lang", "en"),
        content_type=request.args.get("content_type", "all"),
    )
    content_jobs = render_content_jobs(content_page)
    distribution_settings = render_distribution_settings(site["id"])
    social_credentials_setup = render_social_credentials_setup(site["id"])
    podcast_panel = render_podcast_panel(site["id"])
    preview = render_primary_site_link(site)
    colors = []
    fonts = []
    css_count = 0
    try:
        colors = json.loads(site["colors_json"] or "[]")
        fonts = json.loads(site["fonts_json"] or "[]")
        css_count = len(json.loads(site["css_urls_json"] or "[]"))
    except Exception:
        pass
    color_swatches = "".join(f"<span class='swatch' style='background:{escape(c, quote=True)}'></span>" for c in colors[:10]) or "<span class='muted'>No colors scanned</span>"
    factory_checked = "checked" if int(site["factory_enabled"] or 0) else ""
    cadence = site["publishing_cadence"] or "manual"
    cadence_options = "".join(
        f"<option value='{v}' {'selected' if cadence == v else ''}>{label}</option>"
        for v, label in (("manual", "Manual"), ("weekly", "Weekly"), ("twice-weekly", "Twice weekly"), ("daily", "Daily"))
    )
    return (
        MANAGE_SITE_HTML.replace("__SITE_ID__", str(site["id"]))
        .replace("__DOMAIN__", escape(site["domain"]))
        .replace("__HOMEPAGE__", escape(site["homepage_url"], quote=True))
        .replace("__BRAND__", escape(site["brand_name"] or "", quote=True))
        .replace("__ROOT__", escape(site["root_path"] or "", quote=True))
        .replace("__BLOG_PATH__", escape(site["blog_path"] or "/blog/", quote=True))
        .replace("__CUSTOM_BLOG_DOMAIN__", escape(site["custom_blog_domain"] or "", quote=True))
        .replace("__HOSTED_CHECKED__", "checked" if int(site["hosted_blog_enabled"] or 0) else "")
        .replace("__CNAME_STATUS__", escape(site["cname_status"] or "not_configured"))
        .replace("__CNAME_CHECKED_AT__", escape(site["cname_checked_at"] or "Never checked"))
        .replace("__LANGUAGES__", escape(languages_to_text(site["languages"]), quote=True))
        .replace("__CONTENT_CONTEXT__", escape(site["content_context"] or ""))
        .replace("__TOPIC_STRATEGY__", escape(site["topic_strategy"] or ""))
        .replace("__FACTORY_CHECKED__", factory_checked)
        .replace("__CADENCE_OPTIONS__", cadence_options)
        .replace("__PREVIEW__", preview)
        .replace("__SCANNED_AT__", escape(site["scanned_at"] or "Not scanned"))
        .replace("__SCANNED_TITLE__", escape(site["scanned_title"] or "No title captured"))
        .replace("__CSS_COUNT__", str(css_count))
        .replace("__FONTS__", escape(", ".join(fonts[:4]) or "No fonts scanned"))
        .replace("__SWATCHES__", color_swatches)
        .replace("__JOBS__", jobs)
        .replace("__CONTENT_JOBS__", content_jobs)
        .replace("__DISTRIBUTION_SETTINGS__", distribution_settings)
        .replace("__SOCIAL_CREDENTIALS_SETUP__", social_credentials_setup)
        .replace("__PODCAST_PANEL__", podcast_panel)
        .replace("__SITE_SWITCHER__", render_site_switcher(site["id"]))
    )


def normalize_topic_text(text):
    clean = (text or "").lower()
    clean = clean.replace("ai-generated", "ai generated")
    clean = clean.replace("ai generated user generated content", "ai ugc")
    clean = clean.replace("user-generated content", "ugc")
    clean = clean.replace("user generated content", "ugc")
    clean = clean.replace("e-commerce", "ecommerce")
    clean = clean.replace("e commerce", "ecommerce")
    clean = clean.replace("shopify & tech", "shopify tech")
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


DISCOVERY_TOPIC_STOP_WORDS = {
    "about", "after", "all", "also", "and", "are", "automated", "best", "blog", "boost", "brand", "brands",
    "build", "buying", "category", "com", "complete", "content", "cost", "costs", "create", "customer",
    "customers", "domain", "ecommerce", "for", "from", "generated", "guide", "guides", "help", "helps",
    "hint", "how", "html", "imported", "into", "looking", "management", "online", "platform", "product", "products", "scale",
    "service", "services", "shopify", "site", "smart", "solution", "solutions", "store", "stores", "that",
    "the", "their", "this", "through", "tips", "tool", "tools", "topic", "topics", "using", "what", "when",
    "with", "your", "cluster", "couvrez", "cruciales", "les", "pour", "taux", "croisi",
}

DISCOVERY_TOPIC_KEEP_WORDS = {
    "ai", "ugc", "assistant", "assistants", "chat", "chatbot", "chatbots", "commerce", "conversion",
    "conversions", "creative", "creatives", "cruise", "cruises", "cabin", "cabins", "chartering", "cargo",
    "vessel", "vessels", "maritime", "shipbroking", "ship", "shipping", "logistics", "email", "emails",
    "experience", "handoff", "handoffs", "knowledge", "marketing", "models", "optimization",
    "personalization", "photography", "questions", "recommendation",
    "recommendations", "sales", "search", "support", "upsell", "upsells", "video", "videos", "visual",
    "voice", "solo", "supplement", "supplements", "budget", "female", "travel", "traveler", "travelers",
    "reviews", "sharing",
}


def discovery_tokens(text):
    tokens = []
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{1,}", normalize_topic_text(text or "")):
        if len(word) < 3 and word not in {"ai"}:
            continue
        if word in DISCOVERY_TOPIC_STOP_WORDS and word not in DISCOVERY_TOPIC_KEEP_WORDS:
            continue
        if word not in tokens:
            tokens.append(word)
    return tokens


def content_topic_documents(site, limit=180):
    docs = []
    english_docs = []
    if not site or "id" not in site.keys():
        return docs
    with db() as conn:
        rows = conn.execute(
            """
            select title, topic, description, category, slug, published_url, sources_json, created_at
            from content_jobs
            where site_id=?
            order by
              case when status in ('IMPORTED','PUBLISHED','DRAFT','QUEUED') then 0 else 1 end,
              created_at desc
            limit ?
            """,
            (site["id"], limit),
        ).fetchall()
    for row in rows:
        sources = parse_json_object(row["sources_json"])
        path_text = " ".join(urllib.parse.urlsplit(row["published_url"] or "").path.replace("-", " ").replace("/", " ").split())
        text = " ".join([
            row["title"] or "",
            row["topic"] or "",
            row["description"] or "",
            row["category"] or "",
            row["slug"] or "",
            sources.get("title") or "",
            sources.get("description") or "",
            sources.get("category") or "",
            path_text,
        ])
        docs.append(text)
        lang = str(sources.get("language") or sources.get("lang") or "").lower()
        path = urllib.parse.urlsplit(row["published_url"] or "").path.lower()
        if lang in {"", "en", "eng"} and not re.match(r"^/(ru|de|es|fr|it|pt)/", path):
            english_docs.append(text)
    return english_docs if len(english_docs) >= 6 else docs


def site_topic_text(site):
    profile = get_profile(site["id"]) if site and "id" in site.keys() else None
    profile_text = ""
    if profile:
        profile_text = " ".join([profile["title"] or "", profile["description"] or ""])
    discovery_text = ""
    if site and "id" in site.keys():
        try:
            disc = get_topic_discovery_settings(site["id"])
            discovery_text = " ".join([disc["category_hint"] or "", disc["direction"] or ""])
        except Exception:
            discovery_text = ""
    return " ".join([
        discovery_text,
        site["topic_strategy"] or "",
        site["content_context"] or "",
        profile_text,
        site["brand_name"] or "",
        site["domain"] or "",
    ])


def content_topic_phrases(site):
    docs = [(site_topic_text(site), 3)] + [(doc, 1) for doc in content_topic_documents(site)]
    scores = {}
    doc_hits = {}
    for doc, weight in docs:
        tokens = discovery_tokens(doc)
        seen_in_doc = set()
        for n in (2, 3):
            for i in range(0, max(0, len(tokens) - n + 1)):
                phrase_tokens = tokens[i:i + n]
                if len(set(phrase_tokens)) < n:
                    continue
                phrase = " ".join(phrase_tokens)
                if not any(token in DISCOVERY_TOPIC_KEEP_WORDS for token in phrase_tokens):
                    continue
                scores[phrase] = scores.get(phrase, 0) + weight * (6 if n == 2 else 7)
                seen_in_doc.add(phrase)
        for phrase in seen_in_doc:
            doc_hits[phrase] = doc_hits.get(phrase, 0) + weight
    for phrase, hits in doc_hits.items():
        scores[phrase] = scores.get(phrase, 0) + min(hits, 8) * 3
    ranked = sorted(scores.items(), key=lambda item: (item[1], len(item[0])), reverse=True)
    phrases = []
    for phrase, score in ranked:
        if score < 6:
            continue
        if len(phrase.split()) < 2:
            continue
        if any(phrase != existing and phrase in existing for existing in phrases[:18]):
            continue
        phrases.append(phrase)
        if len(phrases) >= 24:
            break
    return phrases


def site_topic_seed(site):
    content_phrases = content_topic_phrases(site)
    if content_phrases:
        return " ".join(content_phrases[:3])
    brand_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", ((site["brand_name"] or "") + " " + (site["domain"] or "")).lower()))
    full = normalize_topic_text(site_topic_text(site))
    stop = {
        "www", "com", "https", "http", "blog", "site", "content", "topics", "brand", "brands", "with", "from",
        "that", "this", "and", "the", "for", "guide", "guides", "buying", "choose", "clear", "help", "helps",
        "understand", "plan", "upcoming", "platform", "compatible", "paying", "costs", "generated", "looking",
        "scale", "their", "custom", "category", "hint",
    }
    words = []
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{1,}", full):
        if word in stop:
            continue
        if len(word) < 3 and word not in {"ai"}:
            continue
        if word in brand_tokens and word not in {
            "ai", "ugc", "ecommerce", "marketing", "photography", "visual", "wine", "wines", "food", "pairing",
            "travel", "fashion", "beauty", "pets", "home",
        }:
            continue
        if word not in words:
            words.append(word)
        if len(words) >= 5:
            break
    if not words and site["domain"]:
        words = [site["domain"].split(".")[0].replace("-", " ")]
    return " ".join(words[:5]) or "ecommerce"

SIGNALS_PER_SOURCE = int(os.environ.get("SIGNALS_PER_SOURCE", "20"))
SIGNAL_STOP_WORDS = {
    "about", "after", "and", "are", "blog", "brand", "buying", "content", "for", "from", "guide", "guides",
    "generated", "how", "into", "site", "that", "the", "this", "tips", "topics", "what", "when", "with", "your",
}

REDDIT_WEAK_MATCH_TERMS = {
    "article", "articles", "best", "business", "buy", "buyer", "buyers", "commerce", "content", "customer",
    "customers", "ecommerce", "example", "examples", "food", "general", "help", "helps", "idea", "ideas",
    "online", "practical", "product", "products", "region", "regions", "review", "reviews", "shop", "shopping",
    "store", "stores", "topic", "topics", "travel", "use", "uses", "visual", "visuals",
}

LOCAL_EVENT_SIGNAL_TERMS = {
    "agenda", "announces", "announced", "awards", "calendar", "conference", "convention", "expo", "fair",
    "fest", "fests", "festival", "festivals", "grand opening", "lineup", "market", "near me", "opens", "opening", "parade",
    "pop-up", "popup", "show", "summit", "tickets", "tour", "tours", "weekend",
    "city", "cities", "village", "villages", "visit", "visiting",
    "increase", "increases", "increased", "raises", "raised",
}

LOCAL_SIGNAL_PLACE_TERMS = {
    "atlanta", "austin", "boston", "brooklyn", "chicago", "dallas", "denver", "houston", "las vegas",
    "london", "los angeles", "miami", "nashville", "new york", "orlando", "paris", "philadelphia",
    "phoenix", "portland", "san diego", "san francisco", "seattle", "toronto", "vancouver", "washington",
}

GLOBAL_SIGNAL_TERMS = {
    "consumer", "consumers", "global", "industry", "markets", "online",
    "people", "report", "research", "search", "shoppers", "study", "trend", "trends", "worldwide",
}

PROMO_TRADE_SIGNAL_TERMS = {
    "£", "$", "€", "campaign", "discount", "grant", "indie", "indies", "month", "promo", "promotion",
    "receive", "receives", "retail", "retailer", "retailers", "stockist", "stockists", "trade", "voucher",
}

SEARCH_NAVIGATION_SIGNAL_TERMS = {
    "amazon", "costco", "facebook", "instagram", "pinterest", "reddit", "tiktok", "wikipedia", "youtube",
}

CAREER_VENDOR_NOISE_TERMS = {
    "agency", "agencies", "career", "careers", "companies", "company", "developer", "developers",
    "development", "engineer", "engineering", "jobs", "salary", "salaries",
}

AI_NEWS_DRIFT_TERMS = {
    "actor", "actors", "artist", "artists", "backlash", "construction", "copyright", "data center",
    "hollywood", "movie", "pope", "power", "real artists", "teenagers", "water", "workers",
}


def timeframe_to_reddit(range_key):
    return {"week": "week", "month": "month", "3m": "year", "6m": "year"}.get(range_key, "week")


def signal_keywords(query):
    words = []
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{1,}", normalize_topic_text(query or "")):
        if word in SIGNAL_STOP_WORDS:
            continue
        if len(word) < 3 and word not in {"ai"}:
            continue
        if word not in words:
            words.append(word)
    return words


def topic_query_candidates(site):
    seed = site_topic_seed(site)
    keywords = signal_keywords(seed)
    content_phrases = content_topic_phrases(site)
    settings_tokens = discovery_tokens(site_topic_text(site))
    candidates = []

    def add(value):
        clean = re.sub(r"\s+", " ", normalize_topic_text(value)).strip()
        if clean and clean not in candidates:
            candidates.append(clean)

    if "ai" in settings_tokens and "support" in settings_tokens:
        add("ai customer support")
        add("ai support chatbot")
    if "assistant" in settings_tokens or "assistants" in settings_tokens:
        add("ai sales assistant")
        add("ai shopping assistant")
    if "conversion" in settings_tokens or "conversions" in settings_tokens:
        add("ecommerce conversion optimization")
    if "search" in settings_tokens:
        add("ecommerce smart search")
        add("ai product search")
    if "upsell" in settings_tokens or "upsells" in settings_tokens:
        add("ai upsell recommendations")
    if "voice" in settings_tokens:
        add("voice commerce")
        add("voice product questions")
    if "ugc" in settings_tokens or "ugc" in keywords:
        add("ugc ecommerce")
        add("ai ugc")
        add("ugc product photography")
        add("ugc ads ecommerce")
    if "ecommerce" in settings_tokens and "photography" in settings_tokens:
        add("ecommerce product photography")
        add("product images ecommerce")
    if "shopify" in settings_tokens and "ugc" in settings_tokens:
        add("shopify ugc ads")
    if "ai" in settings_tokens and "visual" in settings_tokens:
        add("ai visual content")
    if "cruise" in settings_tokens or "cruises" in settings_tokens:
        add("solo cruise")
        add("cruise cabin sharing")
        add("single supplement cruise")
        add("solo cruise travel")
    if "maritime" in settings_tokens or "cargo" in settings_tokens or "chartering" in settings_tokens:
        add("maritime cargo matching")
        add("maritime software")
        add("cargo matching software")
        add("shipbroking automation")
        add("shipbroking software")
        add("chartering email workflow")
        add("chartering software")
        add("ai email parsing shipping")
        add("shipping workflow automation")
    for phrase in content_phrases[:10]:
        add(phrase)
    add(" ".join(keywords[:4]) or seed)
    if len(keywords) >= 2:
        add(" ".join(keywords[:2]))
    return candidates[:12]


def broad_topic_signal_query(site):
    candidates = topic_query_candidates(site)
    return candidates[0] if candidates else site_topic_seed(site)


def signal_term_matches(title, query):
    haystack = (title or "").lower()
    matches = []
    for word in signal_keywords(query):
        if re.search(rf"\b{re.escape(word)}\b", haystack):
            matches.append((word, 2))
    return matches


def signal_relevance_score(title, query):
    return sum(weight for _, weight in signal_term_matches(title, query))


def is_global_topic_signal(title):
    text = re.sub(r"\s+", " ", (title or "").lower()).strip()
    if not text:
        return False, "empty"
    if any(term in text for term in LOCAL_EVENT_SIGNAL_TERMS):
        return False, "local/event-specific"
    if any(term in text for term in PROMO_TRADE_SIGNAL_TERMS):
        return False, "promotion/trade-specific"
    if any(re.search(rf"\b{re.escape(term)}\b", text) for term in CAREER_VENDOR_NOISE_TERMS):
        return False, "career/vendor-specific"
    if any(re.search(rf"\b{re.escape(term)}\b", text) for term in SEARCH_NAVIGATION_SIGNAL_TERMS):
        return False, "navigation/source-specific"
    if any(re.search(rf"\b{re.escape(place)}\b", text) for place in LOCAL_SIGNAL_PLACE_TERMS):
        return False, "place-specific"
    if re.search(r"\b(in|near|around)\s+[A-Z][a-z]+", title or ""):
        return False, "place-specific"
    if re.search(r"\b(20[2-9][0-9])\b", text) and any(term in text for term in {"festival", "expo", "conference", "summit", "awards"}):
        return False, "dated event"
    if any(term in text for term in GLOBAL_SIGNAL_TERMS):
        return True, ""
    return True, ""


def reddit_signal_is_relevant(title, query):
    is_global, _ = is_global_topic_signal(title)
    if not is_global:
        return False, 0, []
    keywords = signal_keywords(query)
    matches = signal_term_matches(title, query)
    matched_words = {word for word, _ in matches}
    strong_keywords = [word for word in keywords if word not in REDDIT_WEAK_MATCH_TERMS]
    anchor_terms = strong_keywords[:3] or keywords[:2]
    text = (title or "").lower()

    if "ai" in matched_words and any(term in text for term in AI_NEWS_DRIFT_TERMS):
        creative_query = any(term in keywords for term in {"ugc", "creative", "creatives", "video", "visual", "photography"})
        if not creative_query:
            return False, 0, sorted(matched_words)

    if not matches or not anchor_terms:
        return False, 0, []

    has_anchor = any(word in matched_words for word in anchor_terms)
    strong_match_count = sum(1 for word in strong_keywords if word in matched_words)
    total_match_count = len(matched_words)

    # Reddit search often returns broad posts for generic words like "food" or "product".
    # Keep only discussions that match the site's core topic, then require another contextual match
    # when the site profile provides enough terms.
    if not has_anchor:
        return False, 0, sorted(matched_words)
    if len(keywords) >= 3 and total_match_count < 2:
        return False, 0, sorted(matched_words)
    if "ai" in matched_words and total_match_count < 3 and any(term in keywords for term in {"customer", "support", "assistant", "chatbot", "sales", "shopping", "ecommerce"}):
        return False, 0, sorted(matched_words)
    if len(strong_keywords) >= 2 and strong_match_count < 1:
        return False, 0, sorted(matched_words)

    score = sum(weight for _, weight in matches) + (3 if has_anchor else 0) + strong_match_count
    return True, score, sorted(matched_words)


def popular_search_queries(site):
    query = broad_topic_signal_query(site)
    keywords = signal_keywords(query)
    cores = topic_query_candidates(site) or [" ".join(keywords[:4]) or query]
    variants = []
    for core in cores:
        variants.extend([
            core,
            f"{core} guide",
            f"{core} examples",
            f"{core} problems",
            f"{core} mistakes",
            f"{core} comparison",
            f"{core} workflow",
            f"{core} strategy",
            f"{core} software",
            f"{core} automation",
            f"how to {core}",
            f"best {core}",
            f"{core} alternatives",
            f"{core} roi",
            f"{core} checklist",
            f"{core} implementation",
            f"{core} use cases",
            f"{core} benchmarks",
        ])
    clean = []
    for variant in variants:
        variant = re.sub(r"\s+", " ", variant).strip()
        if variant and variant not in clean:
            clean.append(variant)
    return clean[:48]


def popular_search_signal_is_relevant(title, query):
    is_global, _ = is_global_topic_signal(title)
    if not is_global:
        return False, 0, []
    keywords = signal_keywords(query)
    matches = signal_term_matches(title, query)
    matched_words = {word for word, _ in matches}
    strong_keywords = [word for word in keywords if word not in REDDIT_WEAK_MATCH_TERMS]
    anchor_terms = strong_keywords[:3] or keywords[:2]
    if not matches or not anchor_terms:
        return False, 0, []
    if not any(word in matched_words for word in anchor_terms):
        return False, 0, sorted(matched_words)
    strong_match_count = sum(1 for word in strong_keywords if word in matched_words)
    if len(keywords) >= 3 and len(matched_words) < 2:
        return False, 0, sorted(matched_words)
    if len(strong_keywords) >= 2 and strong_match_count < 2:
        return False, 0, sorted(matched_words)
    score = sum(weight for _, weight in matches) + len(matched_words)
    return True, score, sorted(matched_words)


def fetch_popular_search_signals(site, range_key):
    query = broad_topic_signal_query(site)
    warnings = []
    ranked = []
    seen = set()
    raw_count = 0
    filtered_global = 0
    filtered_relevance = 0
    duplicate_count = 0
    suggest_failures = 0
    queries = popular_search_queries(site)
    for query_index, suggest_query in enumerate(queries):
        url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "hl": "en", "q": suggest_query})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 BlogCore topic discovery"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read(300000).decode("utf-8", errors="replace"))
            suggestions = data[1] if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list) else []
        except Exception:
            suggest_failures += 1
            continue
        for suggestion_index, suggestion in enumerate(suggestions[:12]):
            title = re.sub(r"\s+", " ", str(suggestion or "")).strip()
            if not title:
                continue
            raw_count += 1
            key = title.lower()
            if key in seen:
                duplicate_count += 1
                continue
            seen.add(key)
            is_global, _ = is_global_topic_signal(title)
            if not is_global:
                filtered_global += 1
                continue
            is_relevant, score, matched_terms = popular_search_signal_is_relevant(title, suggest_query)
            if not is_relevant:
                filtered_relevance += 1
                continue
            rank_hint = -(query_index * 100 + suggestion_index)
            ranked.append((
                score,
                rank_hint,
                {
                    "source": "popular_search",
                    "title": title,
                    "url": "https://www.google.com/search?" + urllib.parse.urlencode({"q": title}),
                    "meta": "Popular search suggestion",
                    "range": range_key,
                    "score": score,
                    "matchedTerms": matched_terms,
                },
            ))
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    signals = [item for _, _, item in ranked[:SIGNALS_PER_SOURCE]]
    meta = {
        "raw": raw_count,
        "kept": len(signals),
        "filteredGlobal": filtered_global,
        "filteredRelevance": filtered_relevance,
        "deduped": duplicate_count,
        "limit": SIGNALS_PER_SOURCE,
        "rangeApplies": False,
        "queries": queries,
        "queryCount": len(queries),
        "failedQueries": suggest_failures,
    }
    if suggest_failures and suggest_failures == len(queries):
        warnings.append("Popular search suggestions are temporarily unavailable.")
    if filtered_global:
        warnings.append(f"Filtered {filtered_global} local, city-specific, or event-specific search suggestions.")
    if not signals and not suggest_failures:
        warnings.append("No strongly relevant popular search suggestions found for this site topic.")
    return signals, warnings, meta


def fetch_reddit_signals(site, range_key):
    query = broad_topic_signal_query(site)
    reddit_t = timeframe_to_reddit(range_key)
    warnings = []
    if range_key in {"3m", "6m"}:
        warnings.append("Reddit RSS supports week/month/year buckets; using year bucket for this range.")
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    signals = []
    seen = set()
    raw_count = 0
    filtered_global = 0
    filtered_relevance = 0
    duplicate_count = 0
    query_failures = []
    query_candidates = topic_query_candidates(site)[:5] or [query]
    for reddit_query in query_candidates:
        url = "https://www.reddit.com/search.rss?" + urllib.parse.urlencode({"q": reddit_query, "sort": "top", "t": reddit_t})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BlogCoreTopicDiscovery/1.0 (+https://blog.yas.ooo)"})
            with urllib.request.urlopen(req, timeout=18) as resp:
                xml = resp.read(1200000).decode("utf-8", errors="replace")
            root = ET.fromstring(xml)
        except Exception as e:
            query_failures.append(str(e))
            continue
        for entry in root.findall("atom:entry", ns)[:60]:
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
            link_node = entry.find("atom:link", ns)
            link = link_node.attrib.get("href", "") if link_node is not None else ""
            updated = (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip()
            if not title or "/comments/" not in link:
                continue
            raw_count += 1
            key = (title.lower(), link)
            if key in seen:
                duplicate_count += 1
                continue
            seen.add(key)
            is_global, reason = is_global_topic_signal(title)
            if not is_global:
                filtered_global += 1
                continue
            is_relevant, score, matched_terms = reddit_signal_is_relevant(title, reddit_query)
            if not is_relevant:
                filtered_relevance += 1
                continue
            signals.append({
                "source": "reddit",
                "title": title,
                "url": link,
                "meta": updated,
                "range": range_key,
                "score": score,
                "matchedTerms": matched_terms,
                "query": reddit_query,
            })
            if len(signals) >= SIGNALS_PER_SOURCE:
                break
        if len(signals) >= SIGNALS_PER_SOURCE:
            break
    meta = {
        "raw": raw_count,
        "kept": len(signals),
        "filteredGlobal": filtered_global,
        "filteredRelevance": filtered_relevance,
        "deduped": duplicate_count,
        "limit": SIGNALS_PER_SOURCE,
        "rangeApplies": True,
        "bucket": reddit_t,
        "queries": query_candidates,
        "failedQueries": len(query_failures),
    }
    if query_failures and not raw_count:
        return [], [f"Reddit temporarily unavailable: {query_failures[0]}"], meta
    if query_failures:
        warnings.append(f"Reddit skipped {len(query_failures)} query variants because of temporary source errors.")
    if filtered_global:
        warnings.append(f"Filtered {filtered_global} local, city-specific, or event-specific Reddit discussions.")
    if not signals:
        warnings.append("No relevant Reddit top discussions found for this site topic and period.")
    return signals, warnings, meta

IDEA_DUPLICATE_THRESHOLD = 0.68


def idea_tokens(text):
    stop = {
        "about", "after", "and", "are", "best", "blog", "for", "from", "guide", "guides", "how", "into",
        "the", "this", "tips", "to", "using", "what", "when", "with", "your", "you",
    }
    words = []
    for word in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9-]{2,}", (text or "").lower()):
        if word in stop:
            continue
        if word.endswith("s") and len(word) > 4:
            word = word[:-1]
        if word not in words:
            words.append(word)
    return words


def idea_similarity(left, right):
    left_tokens = set(idea_tokens(left))
    right_tokens = set(idea_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = left_tokens & right_tokens
    jaccard = len(overlap) / len(left_tokens | right_tokens)
    coverage = len(overlap) / min(len(left_tokens), len(right_tokens))
    return max(jaccard, coverage * 0.82)


def existing_topic_index(site_id):
    with db() as conn:
        rows = conn.execute(
            """
            select id, status, topic, slug, title, description, category, published_url, sources_json
            from content_jobs
            where site_id=?
            """,
            (site_id,),
        ).fetchall()
    index = []
    for row in rows:
        sources = parse_json_object(row["sources_json"])
        page_type = content_job_page_type(row)
        title = row["title"] or row["topic"] or sources.get("title") or ""
        slug_text = " ".join((row["slug"] or "").replace("-", " ").split("/"))
        url_text = " ".join(urllib.parse.urlsplit(row["published_url"] or "").path.replace("-", " ").split("/"))
        comparable = " ".join([title, row["topic"] or "", slug_text, url_text]).strip()
        if comparable:
            index.append({
                "id": row["id"],
                "title": title or row["topic"] or row["slug"] or row["id"],
                "status": row["status"],
                "url": row["published_url"] or "",
                "pageType": page_type,
                "comparable": comparable,
            })
    return index


def find_similar_existing_topic(idea, existing_index):
    comparables = [idea.get("title") or "", idea.get("source_title") or ""]
    best = None
    for existing in existing_index:
        score = max(idea_similarity(text, existing["comparable"]) for text in comparables if text)
        if best is None or score > best["score"]:
            best = {**existing, "score": round(score, 3)}
    if best and best["score"] >= IDEA_DUPLICATE_THRESHOLD:
        return best
    return None


def title_case_phrase(text):
    small = {"a", "an", "and", "as", "at", "for", "in", "of", "on", "or", "the", "to", "vs", "with"}
    words = re.split(r"(\s+)", (text or "").strip())
    cased = []
    word_index = 0
    for part in words:
        if not part or part.isspace():
            cased.append(part)
            continue
        lower = part.lower()
        if word_index > 0 and lower in small:
            cased.append(lower)
        else:
            cased.append(lower[:1].upper() + lower[1:])
        word_index += 1
    return "".join(cased).strip()


ARTICLE_IDEA_SAFETY_CAP = int(os.environ.get("ARTICLE_IDEA_SAFETY_CAP", "50"))
ARTICLE_IDEA_SIGNAL_CAP = int(os.environ.get("ARTICLE_IDEA_SIGNAL_CAP", "40"))
ARTICLE_IDEA_MAX_PASSES = int(os.environ.get("ARTICLE_IDEA_MAX_PASSES", "4"))


def current_content_year():
    return datetime.now(timezone.utc).year


def site_editorial_policy(site):
    policy_text = normalize_topic_text(site_topic_text(site))
    comparison_terms = {
        "comparison", "comparisons", "compare", "compares", "versus", "alternatives", "alternative",
        "roundup", "roundups", "rankings", "ranking", "cost-benefit",
    }
    review_editorial_phrases = {
        "review site", "comparison site", "reviews of", "reviewing", "ship reviews", "cruise reviews",
        "product reviews", "software reviews", "platform reviews",
    }
    tutorial_terms = {
        "tutorial", "tutorials", "developer", "developers", "technical education", "step-by-step",
        "implementation guide", "platform-specific tutorials",
    }
    review_site_terms = {"review site", "comparison site", "reviews of", "reviewing"}
    training_site_terms = {"academy", "training", "course", "courses", "lessons", "curriculum"}
    allows_comparisons = any(re.search(r"\b" + re.escape(term).replace(r"\ ", r"\s+") + r"\b", policy_text) for term in comparison_terms)
    allows_comparisons = allows_comparisons or any(phrase in policy_text for phrase in review_editorial_phrases)
    allows_tutorials = any(phrase in policy_text for phrase in tutorial_terms | training_site_terms)
    is_review_site = any(term in policy_text for term in review_site_terms)
    is_training_site = any(term in policy_text for term in training_site_terms)
    return {
        "currentYear": current_content_year(),
        "allowsComparisons": allows_comparisons,
        "allowsTutorials": allows_tutorials,
        "isReviewSite": is_review_site,
        "isTrainingSite": is_training_site,
        "preferredTopicShape": [
            "audience problem",
            "business impact",
            "decision context",
            "product category relevance",
            "site-specific expertise",
            "non-commodity useful page",
        ],
    }


EDITORIAL_SERP_CLONE_RE = re.compile(
    r"(^\s*\d+\b)|\b("
    r"best|top|tools?|platforms?|generators?|apps?|roundups?|rank(?:ed|ing)?|reviews?|"
    r"alternatives?|comparison|compare|versus|vs\.?|examples?|"
    r"(?:buyer|merchant|customer)'?s?\s+(?:guide|framework)|"
    r"guide\s+to\s+(?:evaluat|choos|select)|evaluation\s+framework"
    r")\b",
    re.I,
)

EDITORIAL_TUTORIAL_RE = re.compile(
    r"\b("
    r"how\s+to\s+(?:build|set\s*up|setup|configure|implement|create|make|develop|train|design)|"
    r"building\s+the|blueprint|step[-\s]?by[-\s]?step|best\s+practices|"
    r"configure|configuration|training|designing\s+(?:an?\s+)?(?:ai\s+)?(?:support\s+)?automation\s+workflow|"
    r"workflows?|frameworks?"
    r")\b",
    re.I,
)


QUERY_CLUSTER_DIRTY_RE = re.compile(
    r"\b(20[0-9]{2}|best|top|review|reviews|comparison|compare|alternatives?|"
    r"buyer'?s?\s+(?:guide|framework)|guide\s+to\s+(?:evaluat|choos|select)|"
    r"evaluation\s+framework)\b",
    re.I,
)


ARTICLE_IDEA_INTERNAL_DUPLICATE_THRESHOLD = 0.62


def clean_article_query_phrase(text):
    phrase = normalize_topic_text(text or "")
    if not phrase:
        return ""
    phrase = re.sub(r"\b20[0-9]{2}\b", " ", phrase)
    phrase = re.sub(r"\b(best|top|review|reviews|comparison|compare|alternatives?|buyer'?s?|guide|framework)\b", " ", phrase)
    phrase = re.sub(r"\b(evaluating|evaluate|evaluation|choosing|choose|selecting|select|finding|find)\b", " ", phrase)
    phrase = re.sub(r"\b(customer|shopper|buyer|user)\s+support\b", "customer support", phrase)
    phrase = re.sub(r"\b(ecommerce|e-commerce)\b", "ecommerce", phrase)
    phrase = re.sub(r"\b(software|platforms?|tools?|apps?|solutions?)\b$", " ", phrase)
    phrase = re.sub(r"\bfor\b", " ", phrase)
    phrase = re.sub(r"\s+", " ", phrase).strip(" -:")
    tokens = []
    for token in phrase.split():
        if token in {"the", "and", "or", "with", "from", "that", "this", "your"}:
            continue
        if token not in tokens:
            tokens.append(token)
    return " ".join(tokens[:7]).strip()


def clean_article_query_cluster(raw_cluster, title="", source_title="", seed=""):
    values = []
    if isinstance(raw_cluster, list):
        values.extend(str(item or "") for item in raw_cluster)
    elif raw_cluster:
        values.append(str(raw_cluster))
    values.append(source_title or "")
    fallback_values = [title or "", seed or ""]
    cleaned = []
    for value in values + fallback_values:
        if len(cleaned) >= 2 and value in fallback_values:
            continue
        phrase = clean_article_query_phrase(value)
        if len(phrase) < 4:
            continue
        if phrase not in cleaned:
            cleaned.append(phrase)
        if len(cleaned) >= 4:
            break
    return cleaned


def normalize_editorial_axis(text):
    raw = normalize_topic_text(text or "")
    if not raw:
        return ""
    replacements = {
        "cart recovery": "cart abandonment",
        "abandoned cart": "cart abandonment",
        "checkout friction": "cart abandonment",
        "support tickets": "support cost",
        "ticket deflection": "support cost",
        "delayed support": "response latency",
        "human escalation": "human handoff",
        "live escalation": "human handoff",
        "operator handoff": "human handoff",
        "technical questions": "technical product questions",
        "product questions": "technical product questions",
        "product specification": "technical product questions",
        "variant selection": "product fit",
        "returns": "return reduction",
        "return rates": "return reduction",
        "conversational selling": "sales assistant",
        "support as revenue": "sales assistant",
        "support and sales": "sales assistant",
        "customer memory": "conversational memory",
        "shopper history": "conversational memory",
        "live data": "live store data",
        "data freshness": "live store data",
        "static ai": "live store data",
        "rule based": "generative understanding",
        "scripted responses": "generative understanding",
        "frustrated shoppers": "emotional escalation",
        "angry customers": "emotional escalation",
    }
    for old, new in replacements.items():
        raw = raw.replace(old, new)
    raw = re.sub(
        r"\b(ai|ecommerce|e-commerce|shopify|customer|customers|support|article|guide|store|stores|"
        r"business|problem|problems|assistant|assistants|chatbot|chatbots|automation|automated|commerce)\b",
        " ",
        raw,
    )
    tokens = []
    for token in raw.split():
        if len(token) < 3:
            continue
        if token not in tokens:
            tokens.append(token)
    return " ".join(tokens[:7]).strip()


def article_idea_comparable_text(idea):
    pieces = [
        idea.get("topic_axis") or "",
        idea.get("audience_problem") or "",
        idea.get("title") or "",
        idea.get("angle") or "",
        idea.get("business_relevance") or "",
        " ".join(idea.get("target_query_cluster") or []),
    ]
    text = normalize_topic_text(" ".join(pieces))
    text = re.sub(
        r"\b(ai|ecommerce|e-commerce|shopify|customer|customers|support|article|guide|store|stores|"
        r"business|problem|problems|assistant|assistants|chatbot|chatbots)\b",
        " ",
        text,
    )
    return re.sub(r"\s+", " ", text).strip()


def find_similar_accepted_idea(idea, accepted_ideas):
    title = idea.get("title") or ""
    comparable = article_idea_comparable_text(idea)
    axis = normalize_editorial_axis(idea.get("topic_axis") or idea.get("audience_problem") or title)
    best = None
    for accepted in accepted_ideas:
        accepted_axis = normalize_editorial_axis(accepted.get("topic_axis") or accepted.get("audience_problem") or accepted.get("title") or "")
        score = max(
            idea_similarity(title, accepted.get("title") or ""),
            idea_similarity(comparable, article_idea_comparable_text(accepted)),
            idea_similarity(axis, accepted_axis) if axis and accepted_axis else 0,
        )
        if best is None or score > best["score"]:
            best = {"title": accepted.get("title") or "", "score": round(score, 3)}
    if best and best["score"] >= ARTICLE_IDEA_INTERNAL_DUPLICATE_THRESHOLD:
        return best
    return None


def editorial_policy_rejection_reason(idea, policy):
    title = idea.get("title") or ""
    angle = idea.get("angle") or ""
    rationale = idea.get("seo_rationale") or ""
    query_text = " ".join(idea.get("target_query_cluster") or [])
    source_title = idea.get("source_title") or ""
    text = " ".join([title, angle, rationale, query_text])
    current_year = int(policy.get("currentYear") or current_content_year())
    years = [int(year) for year in re.findall(r"\b20\d{2}\b", text)]
    if any(year < current_year for year in years):
        return "Rejected: outdated year in article idea"
    if re.search(r"\b20\d{2}\b", source_title) and any(int(year) < current_year for year in re.findall(r"\b20\d{2}\b", source_title)):
        return "Rejected: outdated year in source signal"
    if QUERY_CLUSTER_DIRTY_RE.search(query_text):
        return "Rejected: dirty SERP modifier in target query cluster"
    if not policy.get("allowsComparisons") and QUERY_CLUSTER_DIRTY_RE.search(rationale):
        return "Rejected: dirty SERP modifier in SEO rationale"
    if EDITORIAL_SERP_CLONE_RE.search(title) and not policy.get("allowsComparisons"):
        return "Rejected: generic review/comparison/listicle format is not allowed for this site"
    if EDITORIAL_TUTORIAL_RE.search(title) and not policy.get("allowsTutorials"):
        return "Rejected: build/setup/tutorial format is not allowed for this site"
    return ""


def build_journalist_article_ideas_prompt(site, signals, existing_index, accepted_titles=None, second_pass=False):
    brand = site["brand_name"] or site["domain"]
    topic_seed = site_topic_seed(site)
    policy = site_editorial_policy(site)
    signal_rows = []
    for signal in signals[:ARTICLE_IDEA_SIGNAL_CAP]:
        if signal.get("disabled"):
            continue
        signal_rows.append({
            "source": signal.get("source"),
            "title": signal.get("title"),
            "meta": signal.get("meta"),
            "matchedTerms": signal.get("matchedTerms", []),
        })
    existing_rows = [
        {
            "title": item.get("title"),
            "status": item.get("status"),
            "url": item.get("url"),
            "pageType": item.get("pageType"),
        }
        for item in existing_index[:160]
    ]
    content_context = re.sub(r"\s+", " ", site["content_context"] or "").strip()
    topic_strategy = re.sub(r"\s+", " ", site["topic_strategy"] or "").strip()
    site_profile = re.sub(r"\s+", " ", site_topic_text(site)).strip()
    content_summary = []
    for doc in content_topic_documents(site, limit=24)[:16]:
        compact = re.sub(r"\s+", " ", doc or "").strip()
        if compact:
            content_summary.append(compact[:260])
    return f"""
You are a senior SEO editor and content strategist for a commercial website.

Your task is to generate article topic ideas from trend/search-demand signals, but the final ideas must be based on the website's actual business, audience, expertise, existing content, and SEO opportunity.

Follow Google Search Central 2026 guidance for generative AI search:
- Create unique, valuable, non-commodity, people-first content.
- Do not recycle generic SERP titles or copy trend/search signal wording directly.
- Do not create pages only to target every keyword variation.
- Build topics that provide useful context, original perspective, clear user value, and commercial relevance.
- Each topic must make sense as a page this specific website is qualified to publish.
- Each topic should help Google understand the site's topical authority and business context.

Site:
- Brand: {brand}
- Domain: {site['domain']}
- Topic seed: {topic_seed}
- Business/product context: {content_context or 'Infer from site profile and existing content.'}
- Topic/editorial strategy: {topic_strategy or 'Infer from site profile and existing content.'}
- Full site profile: {site_profile[:1400]}
- Current year: {policy['currentYear']}
- Editorial policy: {json.dumps(policy, ensure_ascii=False)}

Existing site content summary:
{json.dumps(content_summary, ensure_ascii=False, indent=2)}

Audience/search/discussion signals:
{json.dumps(signal_rows, ensure_ascii=False, indent=2)}

Existing imported/published/planned content to avoid duplicating:
{json.dumps(existing_rows, ensure_ascii=False, indent=2)}

Already accepted ideas in this generation run, also avoid duplicating:
{json.dumps(accepted_titles or [], ensure_ascii=False, indent=2)}

Generate article topics using this process:
1. Understand the site first. Determine what this website actually does, who it serves, what problems it solves, and what type of expertise it can credibly provide.
2. Interpret the signals. Treat search trends and Reddit/community discussions as audience-interest signals, not article titles. Cluster related signals into broader user needs, business problems, objections, decision moments, or product-use contexts.
3. Create SEO-relevant editorial topics. For each topic, connect a real audience need, a relevant search-demand signal, the site's business/product context, a useful informational angle, and a reason this page should exist on this website.
4. Avoid generic content. Do not generate generic "Best tools/platforms/software", "Top X", reviews, comparisons, or buyer frameworks unless the editorial policy explicitly allows comparisons. Do not generate build/setup/configuration/tutorial topics unless the editorial policy explicitly allows tutorials. Do not teach users how to replace the site's own product/service with a DIY alternative.
5. For product/commercial sites that are not explicitly review or training sites, avoid numbered listicles, "examples" compilations, "guide to choosing/evaluating", "evaluation framework", "how to train/configure/build", and workflow/blueprint/tutorial framing. Instead, create pages about a concrete audience problem, decision moment, business risk, adoption blocker, buyer objection, product-category value, ROI/efficiency context, or misconception.
6. Preferred topic types for commercial/product sites: audience problem, business cost/risk, adoption blocker, decision context, product-category value, use-case scenario, objection handling, ROI/efficiency context, or misconception correction.
7. Title rules: natural editorial titles, not keyword-stuffed titles; serious 2026 SEO style; no obsolete years; no copied autocomplete phrases; no hype; no generic SERP clone framing; no title starting with a number unless the site is explicitly a media/listicle publication.
8. SEO value: every idea must explain search intent, target query cluster, site-specific business relevance, unique context the site can add, and why it is not a duplicate.
9. Topic diversity: every idea must have a distinct `topic_axis` and `audience_problem`. Do not create several ideas that differ only by title but all solve the same problem, funnel stage, objection, or business outcome.
10. Choose `contentType` deliberately: use `blog` for editorial information pages. Use `seo_money_page` only for a durable, commercially relevant use-case or solution page that maps directly to the site's own service/product and deserves a canonical landing page. Do not create a money page merely because a keyword is commercial, and do not duplicate an existing service page.

Generation rules:
- Generate every distinct article idea that is editorially justified by the selected signals and useful for this site.
- Do not stop at an arbitrary fixed count. If 3 ideas are genuinely valid, return 3; if 30 are genuinely valid, return 30.
- Respect the technical safety cap of {ARTICLE_IDEA_SAFETY_CAP} ideas in one response.
- Do not write local city/event/news/campaign topics.
- `target_query_cluster` must contain normalized SEO clusters, not raw autocomplete strings. Remove obsolete years and modifiers like "best", "top", "review", "comparison", "alternatives", and "buyer framework" unless the site explicitly allows that format.
- `seo_rationale` must explain durable SEO/business value without quoting dirty raw queries such as "best ... 2025".
- Do not produce near-duplicate ideas across the same business problem. If several signals point to agentic AI, technical product support, human handoff, or conversational memory, consolidate each cluster into the strongest single article idea.
- For each idea, set `topic_axis` to a compact editorial axis such as `response latency`, `cart abandonment`, `technical product questions`, `return reduction`, `human handoff`, `conversational memory`, `live store data`, `emotional escalation`, or another site-appropriate axis.
- Set `audience_problem` to the concrete user/business problem the page solves. Two ideas with the same audience problem should be merged unless they target clearly different funnel stages or outcomes.
- Cover different clusters from the selected signals instead of producing only one cluster.
- If many signals are near-duplicates, consolidate them into one stronger idea and use other signals for separate ideas.
- {'This is a second pass. Focus only on valid ideas missing from the accepted list above.' if second_pass else 'Prefer breadth across all selected signal clusters before depth inside one cluster.'}
- Return only JSON with this shape:
{{
  "ideas": [
    {{
      "title": "Specific article title",
      "angle": "Editorial angle and why readers care",
      "seo_intent": "informational|commercial|comparison|transactional",
      "seo_rationale": "Why this can rank and why it supports the site",
      "target_query_cluster": ["query 1", "query 2"],
      "business_relevance": "How this connects to this site's offer and audience",
      "unique_site_context": "What this website can credibly add that generic content cannot",
      "duplicate_check": "Why this is not already covered by the existing content list",
      "topic_axis": "Compact distinct editorial axis",
      "audience_problem": "Concrete audience/business problem this page solves",
      "source_title": "The audience signal that inspired the idea",
      "source": "popular_search|reddit",
      "contentType": "blog|seo_money_page"
    }}
  ]
}}
""".strip()


def sanitize_article_idea(raw_idea, signals, policy=None):
    if not isinstance(raw_idea, dict):
        return None
    title = re.sub(r"\s+", " ", str(raw_idea.get("title") or "")).strip()
    angle = re.sub(r"\s+", " ", str(raw_idea.get("angle") or "")).strip()
    seo_intent = re.sub(r"\s+", " ", str(raw_idea.get("seo_intent") or raw_idea.get("seoIntent") or "")).strip().lower()
    seo_rationale = re.sub(r"\s+", " ", str(raw_idea.get("seo_rationale") or raw_idea.get("seoRationale") or "")).strip()
    target_query_cluster = raw_idea.get("target_query_cluster") or raw_idea.get("targetQueryCluster") or []
    business_relevance = re.sub(r"\s+", " ", str(raw_idea.get("business_relevance") or raw_idea.get("businessRelevance") or "")).strip()
    unique_site_context = re.sub(r"\s+", " ", str(raw_idea.get("unique_site_context") or raw_idea.get("uniqueSiteContext") or "")).strip()
    duplicate_check = re.sub(r"\s+", " ", str(raw_idea.get("duplicate_check") or raw_idea.get("duplicateCheck") or "")).strip()
    topic_axis = re.sub(r"\s+", " ", str(raw_idea.get("topic_axis") or raw_idea.get("topicAxis") or "")).strip()
    audience_problem = re.sub(r"\s+", " ", str(raw_idea.get("audience_problem") or raw_idea.get("audienceProblem") or "")).strip()
    requested_content_type = str(raw_idea.get("contentType") or "blog").strip().lower()
    content_type = "seo_money_page" if requested_content_type in {"use_case", "use-cases", "seo_money_page", "seo-money-page"} else "blog"
    if len(title) < 28 or len(angle) < 30 or len(seo_rationale) < 35:
        return None
    if seo_intent not in {"informational", "commercial", "comparison", "transactional"}:
        return None
    source_title = re.sub(r"\s+", " ", str(raw_idea.get("source_title") or raw_idea.get("sourceTitle") or "")).strip()
    matched_signal = None
    for signal in signals:
        signal_title = re.sub(r"\s+", " ", str(signal.get("title") or "")).strip()
        if source_title and signal_title and source_title.lower() == signal_title.lower():
            matched_signal = signal
            break
    if not matched_signal and signals:
        matched_signal = signals[0]
    direct_copy = any(idea_similarity(title, signal.get("title") or "") > 0.9 for signal in signals)
    if direct_copy:
        return None
    raw_source_title = source_title or (matched_signal or {}).get("title") or ""
    cleaned_cluster = clean_article_query_cluster(
        target_query_cluster,
        title=title,
        source_title=raw_source_title,
    )
    if not cleaned_cluster:
        return None
    source_display = cleaned_cluster[0]
    idea = {
        "title": title,
        "angle": angle,
        "seo_intent": seo_intent,
        "seo_rationale": seo_rationale,
        "target_query_cluster": cleaned_cluster,
        "business_relevance": business_relevance,
        "unique_site_context": unique_site_context,
        "duplicate_check": duplicate_check,
        "topic_axis": topic_axis or title,
        "audience_problem": audience_problem or angle,
        "source": raw_idea.get("source") or (matched_signal or {}).get("source") or "popular_search",
        "source_title": source_display,
        "raw_source_title": raw_source_title,
        "source_url": (matched_signal or {}).get("url") or raw_idea.get("source_url") or "",
        "contentType": content_type,
    }
    if editorial_policy_rejection_reason(idea, policy or {"currentYear": current_content_year()}):
        return None
    return idea


def article_idea_candidates_for_signal(signal, brand, seed):
    raw = re.sub(r"\s+", " ", signal.get("title", "")).strip()
    if not raw:
        return []
    clean = re.sub(r"\b(202[0-9]|reddit|youtube)\b", "", raw, flags=re.I)
    clean = re.sub(r"\s+", " ", clean).strip(" -:")
    if not clean:
        return []
    base = title_case_phrase(clean)
    lower = clean.lower()
    candidates = []
    if lower.startswith(("how to ", "what ", "why ", "is ", "are ")):
        candidates.append(base)
    else:
        candidates.append(f"Why {base} Matters for {brand}'s Audience")
    if len(idea_tokens(clean)) >= 2:
        candidates.append(f"When {base} Becomes a Business Problem")
    if "risk" not in lower and "cost" not in lower:
        candidates.append(f"The Hidden Cost of Ignoring {base}")
    ideas = []
    for title in candidates:
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            continue
        ideas.append({
            "title": title,
            "angle": f"Use the selected topic signal as an audience-interest clue, then explain the business problem, decision context, and practical value through {brand}'s offer, expertise, or editorial point of view around {seed}.",
            "seo_intent": "informational",
            "seo_rationale": f"This topic can capture non-news search demand around {seed} while adding site-specific context instead of copying the raw search phrase.",
            "target_query_cluster": [raw],
            "business_relevance": f"The topic connects audience demand to {brand}'s category and commercial problem space.",
            "unique_site_context": f"{brand} can frame the topic through its own product/service context and existing expertise.",
            "duplicate_check": "Fallback candidate still requires duplicate and editorial validation before it can be shown.",
            "topic_axis": clean_article_query_phrase(raw),
            "audience_problem": clean,
            "source": signal.get("source"),
            "source_title": raw,
            "source_url": signal.get("url", ""),
            "contentType": "blog",
        })
    return ideas


def generate_article_ideas(site, signals, existing_index=None):
    seed = site_topic_seed(site)
    brand = site["brand_name"] or site["domain"]
    policy = site_editorial_policy(site)
    ideas = []
    rejected = []
    seen_titles = set()
    existing_index = existing_index if existing_index is not None else existing_topic_index(site["id"])
    usable_signals = [signal for signal in signals[:ARTICLE_IDEA_SIGNAL_CAP] if not signal.get("disabled")]
    generated_count = 0
    generation_passes = 0

    def accept_payload_ideas(payload):
        nonlocal generated_count
        accepted_before = len(ideas)
        for raw_idea in payload.get("ideas") or []:
            if len(ideas) >= ARTICLE_IDEA_SAFETY_CAP:
                break
            generated_count += 1
            idea = sanitize_article_idea(raw_idea, usable_signals, policy)
            if not idea:
                rejected.append({"idea": {"title": str(raw_idea.get("title") or "Invalid idea")[:140]}, "similar": {"title": "Rejected by idea quality/SEO validation", "score": 0}})
                continue
            key = simple_slug(idea["title"])
            if key in seen_titles:
                rejected.append({"idea": idea, "similar": {"title": "Duplicate idea in this generation run", "score": 1}})
                continue
            similar_accepted = find_similar_accepted_idea(idea, ideas)
            if similar_accepted:
                rejected.append({"idea": idea, "similar": similar_accepted})
                continue
            seen_titles.add(key)
            similar = find_similar_existing_topic(idea, existing_index)
            if similar:
                rejected.append({"idea": idea, "similar": similar})
                continue
            ideas.append(idea)
        return len(ideas) - accepted_before

    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        try:
            generation_passes += 1
            payload = _gemini_text_json(build_journalist_article_ideas_prompt(site, usable_signals, existing_index))
            accepted_this_pass = accept_payload_ideas(payload)
            while ideas and accepted_this_pass > 0 and len(ideas) < ARTICLE_IDEA_SAFETY_CAP and generation_passes < ARTICLE_IDEA_MAX_PASSES:
                generation_passes += 1
                retry_payload = _gemini_text_json(build_journalist_article_ideas_prompt(
                    site,
                    usable_signals,
                    existing_index,
                    [idea["title"] for idea in ideas],
                    second_pass=True,
                ))
                accepted_this_pass = accept_payload_ideas(retry_payload)
            if ideas:
                return ideas, rejected, {"generated": generated_count, "accepted": len(ideas), "rejected": len(rejected), "signals": len(usable_signals), "safetyCap": ARTICLE_IDEA_SAFETY_CAP, "passes": generation_passes}
        except Exception as e:
            rejected.append({"idea": {"title": "Gemini article idea generation failed"}, "similar": {"title": str(e), "score": 0}})
    for signal in usable_signals:
        if signal.get("disabled"):
            continue
        for raw_idea in article_idea_candidates_for_signal(signal, brand, seed):
            if len(ideas) >= ARTICLE_IDEA_SAFETY_CAP:
                break
            idea = sanitize_article_idea(raw_idea, usable_signals, policy)
            if not idea:
                continue
            if not idea.get("seo_rationale") or not idea.get("seo_intent"):
                continue
            key = simple_slug(idea["title"])
            if key in seen_titles:
                continue
            similar_accepted = find_similar_accepted_idea(idea, ideas)
            if similar_accepted:
                rejected.append({"idea": idea, "similar": similar_accepted})
                continue
            seen_titles.add(key)
            similar = find_similar_existing_topic(idea, existing_index)
            if similar:
                rejected.append({"idea": idea, "similar": similar})
                continue
            ideas.append(idea)
        if len(ideas) >= ARTICLE_IDEA_SAFETY_CAP:
            break
    return ideas, rejected, {"generated": generated_count, "accepted": len(ideas), "rejected": len(rejected), "signals": len(usable_signals), "safetyCap": ARTICLE_IDEA_SAFETY_CAP, "passes": generation_passes}


def _parse_json_text(text):
    raw = (text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start:end + 1]
    return json.loads(raw)


def _gemini_generate_text(prompt, temperature=0.55, timeout=180, response_schema=None):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    model = os.environ.get("GEMINI_TEXT_MODEL") or os.environ.get("GEMINI_MODEL_TEXT") or os.environ.get("GEMINI_MODEL") or "gemini-3.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    generation_config = {"responseMimeType": "application/json", "temperature": temperature}
    if response_schema:
        generation_config["responseSchema"] = response_schema
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response: {data}")


def _repair_json_text(text, error):
    repair_prompt = f"""
Return valid JSON only. Repair the malformed JSON below without changing the data model or adding commentary.

Original parser error:
{str(error)}

Malformed JSON:
{(text or '')[:50000]}
""".strip()
    repaired = _gemini_generate_text(repair_prompt, temperature=0, timeout=180)
    return _parse_json_text(repaired)


def _gemini_text_json(prompt, response_schema=None, temperature=0.55, timeout=180, repair=True):
    text = _gemini_generate_text(prompt, temperature=temperature, timeout=timeout, response_schema=response_schema)
    try:
        return _parse_json_text(text)
    except json.JSONDecodeError as e:
        if not repair:
            raise
        try:
            return _repair_json_text(text, e)
        except Exception as repair_error:
            raise RuntimeError(f"Model returned invalid JSON and repair failed: {repair_error}") from e


def _extract_interaction_image_b64(data):
    output_image = data.get("output_image") or data.get("outputImage") or {}
    if isinstance(output_image, dict) and output_image.get("data"):
        return output_image["data"]
    for step in data.get("steps") or []:
        blocks = []
        if isinstance(step, dict):
            blocks.extend(step.get("content") or [])
            blocks.extend(step.get("summary") or [])
        for block in blocks:
            if isinstance(block, dict) and block.get("type") == "image" and block.get("data"):
                return block["data"]
    candidates = data.get("candidates") or []
    for candidate in candidates:
        for part in ((candidate.get("content") or {}).get("parts") or []):
            inline = part.get("inlineData") or part.get("inline_data") or {}
            if inline.get("data"):
                return inline["data"]
    raise RuntimeError(f"Gemini image response did not include image data: {str(data)[:500]}")


def _gemini_image_jpeg(prompt, aspect_ratio="4:5"):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    model = os.environ.get("GEMINI_IMAGE_MODEL") or "gemini-3.1-flash-image"
    response_format = {"type": "image", "mime_type": "image/jpeg", "aspect_ratio": aspect_ratio}
    image_size = os.environ.get("GEMINI_IMAGE_SIZE")
    if image_size:
        response_format["image_size"] = image_size
    payload = {
        "model": model,
        "input": [{"type": "text", "text": prompt}],
        "response_format": response_format,
    }
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read(1000).decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        raise RuntimeError(f"Gemini image HTTP {e.code}: {detail[:900]}")
    return b64decode(_extract_interaction_image_b64(data))


def _gemini_tts_pcm(transcript, voice_name, timeout=240):
    """Generate mono 24 kHz PCM through Gemini TTS and return raw frames."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    model = os.environ.get("GEMINI_TTS_MODEL") or "gemini-3.1-flash-tts-preview"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": transcript}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}},
        },
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model, safe='.-')}:generateContent?key={urllib.parse.quote(api_key, safe='')}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        inline = data["candidates"][0]["content"]["parts"][0].get("inlineData") or {}
        raw = inline.get("data")
        if not raw:
            raise RuntimeError(f"Gemini TTS response did not include audio: {str(data)[:500]}")
        return b64decode(raw)
    except urllib.error.HTTPError as e:
        detail = e.read(1200).decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        raise RuntimeError(f"Gemini TTS HTTP {e.code}: {detail[:1000]}")


PODCAST_SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "script": {"type": "string"},
    },
    "required": ["title", "description", "script"],
}


def podcast_transcript_chunks(script, limit=5200):
    paragraphs = [re.sub(r"\s+", " ", item).strip() for item in re.split(r"\n\s*\n", script or "") if item.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if current and len(candidate) > limit:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def build_podcast_script_prompt(site, job, settings):
    article_text = strip_html_text(job["draft_html"] or "", 30000)
    language = content_job_language(job, site)
    minutes = max(3, min(20, int(settings["target_minutes"] or 8)))
    host = (settings["host_name"] or site["brand_name"] or site["domain"]).strip()
    return f"""
Create a single-host podcast script from a finished website article.

The script will be synthesized directly to audio. Return JSON only, following the supplied schema.

Podcast settings:
- site: {site['brand_name'] or site['domain']}
- host: {host}
- language: {LANGUAGE_NAMES.get(language, language)}
- target duration: about {minutes} minutes
- voice direction: {(settings['voice_direction'] or 'warm, clear, confident, conversational').strip()}

Editorial rules:
- Build a self-contained episode, not a reading of the article and not a promotional ad.
- Start with a specific listener problem or surprising observation. Explain why it matters, provide the useful reasoning from the article, and end with a calm invitation to explore the original article.
- Preserve facts from the source. Do not invent statistics, customer stories, or claims.
- Use short spoken paragraphs and natural transitions. Avoid headings, bullets, markdown, URLs, citations, stage directions, and voice tags in the spoken script.
- Do not read the title twice. Do not mention that this was generated by AI.
- Keep the final script within roughly {minutes * 115 - 120} to {minutes * 145} words.

Source article title: {job['title'] or job['topic']}
Source article description: {job['description'] or ''}
Source article:
{article_text}
""".strip()


def generate_podcast_episode(site_id, job_id):
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
        settings = conn.execute("select * from podcast_settings where site_id=?", (site_id,)).fetchone()
    if not site or not job:
        raise KeyError("article not found")
    if not settings or not int(settings["enabled"] or 0):
        raise ValueError("Enable podcasts for this site before generating an episode")
    if not (job["draft_html"] or "").strip():
        raise ValueError("The selected article has no readable draft content")
    episode_id = secrets.token_hex(12)
    created = now_iso()
    with db() as conn:
        conn.execute(
            """insert into podcast_episodes(id,site_id,job_id,status,title,language,created_at,updated_at)
               values(?,?,?,?,?,?,?,?)""",
            (episode_id, site_id, job_id, "GENERATING", job["title"] or job["topic"] or "Podcast episode", content_job_language(job, site), created, created),
        )
    try:
        script_data = _gemini_text_json(build_podcast_script_prompt(site, job, settings), response_schema=PODCAST_SCRIPT_SCHEMA, temperature=0.45, repair=False)
        script = re.sub(r"\s+", " ", str(script_data.get("script") or "")).strip()
        words = len(re.findall(r"\b[\w'-]+\b", script))
        if words < 300:
            raise ValueError("Podcast script is too short")
        if words > 3200:
            raise ValueError("Podcast script is too long")
        chunks = podcast_transcript_chunks(script)
        if not chunks:
            raise ValueError("Podcast script is empty")
        pcm_parts = []
        voice_name = settings["voice_name"] if settings["voice_name"] in PODCAST_VOICES else "Kore"
        for index, chunk in enumerate(chunks):
            prompt = f"Synthesize the following podcast transcript naturally. Do not read this instruction aloud.\n\nSpoken transcript:\n{chunk}"
            try:
                pcm_parts.append(_gemini_tts_pcm(prompt, voice_name))
            except RuntimeError:
                # Gemini TTS preview can sporadically return a transient 500. Retry once per chunk.
                if index < len(chunks):
                    pcm_parts.append(_gemini_tts_pcm(prompt, voice_name))
                else:
                    raise
        pcm = b"".join(pcm_parts)
        asset_dir = podcast_asset_dir(site_id, episode_id)
        asset_dir.mkdir(parents=True, exist_ok=True)
        filename = "episode.wav"
        with wave.open(str(asset_dir / filename), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(24000)
            output.writeframes(pcm)
        duration_seconds = max(1, len(pcm) // (24000 * 2))
        with db() as conn:
            conn.execute(
                """update podcast_episodes set status='READY',title=?,description=?,script_text=?,audio_filename=?,duration_seconds=?,error=NULL,updated_at=?
                   where id=? and site_id=?""",
                (str(script_data.get("title") or job["title"] or job["topic"]), str(script_data.get("description") or ""), script, filename, duration_seconds, now_iso(), episode_id, site_id),
            )
        return {"ok": True, "episodeId": episode_id, "status": "READY", "durationSeconds": duration_seconds}
    except Exception as e:
        with db() as conn:
            conn.execute("update podcast_episodes set status='ERROR',error=?,updated_at=? where id=? and site_id=?", (str(e), now_iso(), episode_id, site_id))
        raise


def publish_podcast_episode(site_id, episode_id):
    with db() as conn:
        episode = conn.execute("select * from podcast_episodes where id=? and site_id=?", (episode_id, site_id)).fetchone()
    if not episode:
        raise KeyError("episode not found")
    if episode["status"] not in {"READY", "PUBLISHED"} or not episode["audio_filename"]:
        raise ValueError("Generate a ready audio episode before publishing")
    url = podcast_public_url(site_id, episode_id)
    with db() as conn:
        conn.execute("update podcast_episodes set status='PUBLISHED',published_url=?,published_at=?,updated_at=? where id=? and site_id=?", (url, now_iso(), now_iso(), episode_id, site_id))
    return {"ok": True, "episodeId": episode_id, "status": "PUBLISHED", "publishedUrl": url}


def build_site_topic_profile_prompt(site, theme):
    brand = site["brand_name"] or site["domain"]
    nav_text = strip_html_text(theme.get("header_html") or "", 900)
    footer_text = strip_html_text(theme.get("footer_html") or "", 600)
    return f"""
You are configuring an automated content factory for a connected website.
Infer the site's durable editorial direction from its homepage metadata and navigation.

SITE:
- brand: {brand}
- domain: {site['domain']}
- homepage: {site['homepage_url']}
- existing site context: {site['content_context'] or ''}
- existing topic strategy: {site['topic_strategy'] or ''}

SCANNED HOMEPAGE:
- title: {theme.get('title') or ''}
- meta description: {theme.get('description') or ''}
- navigation/header text: {nav_text}
- footer text: {footer_text}

RULES:
- Return STRICT JSON only.
- Use English.
- Infer what this site should publish about globally, not a one-off local event.
- Do not copy placeholder text.
- Keep "direction" concise: the core topic/product category and audience intent.
- Keep "categoryHint" as comma-separated editorial categories.
- Keep "contentContext" as a short factual description of the site.
- Keep "topicStrategy" as a short evergreen strategy for topic discovery.

RETURN JSON SHAPE:
{{
  "direction": "core topic or product category",
  "categoryHint": "Category One, Category Two, Category Three",
  "contentContext": "one sentence factual site context",
  "topicStrategy": "one sentence topic strategy"
}}
""".strip()


def infer_site_topic_profile(site, theme):
    fallback = fallback_site_topic_profile(site, theme)
    try:
        inferred = _gemini_text_json(build_site_topic_profile_prompt(site, theme))
        profile = {
            "direction": clean_inferred_text(inferred.get("direction"), 180),
            "categoryHint": clean_inferred_text(inferred.get("categoryHint"), 180),
            "contentContext": clean_inferred_text(inferred.get("contentContext"), 260),
            "topicStrategy": clean_inferred_text(inferred.get("topicStrategy"), 260),
            "source": "gemini",
        }
        if not profile["direction"] or not profile["categoryHint"]:
            raise ValueError("Gemini returned incomplete topic profile")
        return profile
    except Exception as e:
        fallback["warning"] = str(e)
        return fallback


def apply_site_topic_profile(site_id, profile, overwrite=False):
    now = now_iso()
    with db() as conn:
        conn.execute(
            """
            insert into topic_discovery_settings(site_id, direction, category_hint, updated_at)
            values(?, ?, ?, ?)
            on conflict(site_id) do nothing
            """,
            (site_id, profile.get("direction") or "", profile.get("categoryHint") or "", now),
        )
        conn.execute(
            """
            update topic_discovery_settings
            set
              direction=case when ? or coalesce(direction,'')='' then ? else direction end,
              category_hint=case when ? or coalesce(category_hint,'')='' then ? else category_hint end,
              updated_at=?
            where site_id=?
            """,
            (
                1 if overwrite else 0,
                profile.get("direction") or "",
                1 if overwrite else 0,
                profile.get("categoryHint") or "",
                now,
                site_id,
            ),
        )
        conn.execute(
            """
            update sites
            set
              content_context=case when ? or coalesce(content_context,'')='' then ? else content_context end,
              topic_strategy=case when ? or coalesce(topic_strategy,'')='' then ? else topic_strategy end,
              updated_at=?
            where id=?
            """,
            (
                1 if overwrite else 0,
                profile.get("contentContext") or "",
                1 if overwrite else 0,
                profile.get("topicStrategy") or "",
                now,
                site_id,
            ),
        )
    return profile


ARTICLE_DRAFT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "slug": {"type": "STRING"},
        "title": {"type": "STRING"},
        "description": {"type": "STRING"},
        "category": {"type": "STRING"},
        "heroImage": {"type": "STRING"},
        "lead": {"type": "STRING"},
        "sections": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "heading": {"type": "STRING"},
                    "paragraphs": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "bullets": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "required": ["heading", "paragraphs"],
            },
        },
        "table": {
            "type": "OBJECT",
            "properties": {
                "headers": {"type": "ARRAY", "items": {"type": "STRING"}},
                "rows": {
                    "type": "ARRAY",
                    "items": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
            "required": ["headers", "rows"],
        },
        "orderedListTitle": {"type": "STRING"},
        "orderedList": {"type": "ARRAY", "items": {"type": "STRING"}},
        "quote": {"type": "STRING"},
        "images": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "src": {"type": "STRING"},
                    "alt": {"type": "STRING"},
                    "caption": {"type": "STRING"},
                },
                "required": ["src", "alt", "caption"],
            },
        },
        "faq": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "question": {"type": "STRING"},
                    "answer": {"type": "STRING"},
                },
                "required": ["question", "answer"],
            },
        },
    },
    "required": ["slug", "title", "description", "category", "heroImage", "lead", "sections", "table", "orderedList", "quote", "images", "faq"],
}


def clean_image_filename(value, fallback):
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "").strip())
    name = name.strip("-._")
    if not name:
        name = fallback
    if "/" in name or "\\" in name:
        name = fallback
    if not re.search(r"\.(?:jpg|jpeg|png|webp)$", name, re.I):
        name = f"{name}.jpg"
    return name


def render_structured_article_html(draft, slug, asset_prefix=""):
    parts = []
    lead = re.sub(r"\s+", " ", str(draft.get("lead") or "")).strip()
    if lead:
        parts.append(f'<p class="article-lead">{escape(lead)}</p>')
    images = draft.get("images") if isinstance(draft.get("images"), list) else []
    normalized_images = []
    for index, image in enumerate(images[:3]):
        if not isinstance(image, dict):
            continue
        src = clean_image_filename(image.get("src"), f"{slug}-image-{index + 1}.jpg")
        alt = re.sub(r"\s+", " ", str(image.get("alt") or "")).strip() or f"{slug} image {index + 1}"
        caption = re.sub(r"\s+", " ", str(image.get("caption") or "")).strip() or alt
        normalized_images.append((src, alt, caption))
    while len(normalized_images) < 3:
        index = len(normalized_images) + 1
        normalized_images.append((f"{slug}-image-{index}.jpg", f"{slug} image {index}", f"Illustration for {slug.replace('-', ' ')}"))

    def image_html(image_tuple):
        src, alt, caption = image_tuple
        if asset_prefix and not re.match(r"^(?:https?:)?/", src):
            src = f"{asset_prefix.rstrip('/')}/{src}"
        return f'<figure class="article-figure"><img src="{escape(src, quote=True)}" alt="{escape(alt, quote=True)}" /><figcaption>{escape(caption)}</figcaption></figure>'

    inserted_images = set()
    sections = draft.get("sections") if isinstance(draft.get("sections"), list) else []
    used_anchors = set()
    toc_items = []
    section_anchors = {}
    for index, section in enumerate(sections[:10]):
        if not isinstance(section, dict):
            continue
        heading = re.sub(r"\s+", " ", str(section.get("heading") or "")).strip()
        if not heading:
            continue
        base = simple_slug(heading)[:80] or f"section-{index + 1}"
        anchor = base
        suffix = 2
        while anchor in used_anchors:
            anchor = f"{base}-{suffix}"
            suffix += 1
        used_anchors.add(anchor)
        section_anchors[index] = anchor
        toc_items.append((anchor, heading))
    if len(toc_items) >= 3:
        toc_html = "".join(
            f'<li><a href="#{escape(anchor, quote=True)}">{escape(heading)}</a></li>'
            for anchor, heading in toc_items[:10]
        )
        parts.append(f'<nav class="article-toc" aria-label="Contents"><h2>Contents</h2><ol>{toc_html}</ol></nav>')
    if normalized_images:
        parts.append(image_html(normalized_images[0]))
        inserted_images.add(0)
    for index, section in enumerate(sections[:10]):
        if not isinstance(section, dict):
            continue
        heading = re.sub(r"\s+", " ", str(section.get("heading") or "")).strip()
        if heading:
            anchor_attr = f' id="{escape(section_anchors[index], quote=True)}"' if index in section_anchors else ""
            parts.append(f"<h2{anchor_attr}>{escape(heading)}</h2>")
        paragraphs = section.get("paragraphs") if isinstance(section.get("paragraphs"), list) else []
        for paragraph in paragraphs[:4]:
            text = re.sub(r"\s+", " ", str(paragraph or "")).strip()
            if text:
                parts.append(f"<p>{escape(text)}</p>")
        bullets = section.get("bullets") if isinstance(section.get("bullets"), list) else []
        clean_bullets = [re.sub(r"\s+", " ", str(item or "")).strip() for item in bullets[:8]]
        clean_bullets = [item for item in clean_bullets if item]
        if clean_bullets:
            parts.append("<ul>" + "".join(f"<li>{escape(item)}</li>" for item in clean_bullets) + "</ul>")
        if index == 1 and len(normalized_images) > 1:
            parts.append(image_html(normalized_images[1]))
            inserted_images.add(1)
        if index == 3 and len(normalized_images) > 2:
            parts.append(image_html(normalized_images[2]))
            inserted_images.add(2)
    for index, image in enumerate(normalized_images):
        if index not in inserted_images:
            parts.append(image_html(image))

    table = draft.get("table") if isinstance(draft.get("table"), dict) else {}
    headers = table.get("headers") if isinstance(table.get("headers"), list) else []
    rows = table.get("rows") if isinstance(table.get("rows"), list) else []
    if headers and rows:
        head_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers[:5])
        row_html = []
        for row in rows[:8]:
            cells = row if isinstance(row, list) else []
            row_html.append("<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in cells[:len(headers[:5])]) + "</tr>")
        parts.append(f'<table class="article-table"><thead><tr>{head_html}</tr></thead><tbody>{"".join(row_html)}</tbody></table>')
    ordered = draft.get("orderedList") if isinstance(draft.get("orderedList"), list) else []
    clean_ordered = [re.sub(r"\s+", " ", str(item or "")).strip() for item in ordered[:10]]
    clean_ordered = [item for item in clean_ordered if item]
    if clean_ordered:
        title = re.sub(r"\s+", " ", str(draft.get("orderedListTitle") or "Practical next steps")).strip()
        parts.append(f"<h2>{escape(title)}</h2>")
        parts.append("<ol>" + "".join(f"<li>{escape(item)}</li>" for item in clean_ordered) + "</ol>")
    quote = re.sub(r"\s+", " ", str(draft.get("quote") or "")).strip()
    if quote:
        parts.append(f'<blockquote class="article-quote">{escape(quote)}</blockquote>')
    faq = draft.get("faq") if isinstance(draft.get("faq"), list) else []
    faq_items = []
    for item in faq[:7]:
        if not isinstance(item, dict):
            continue
        question = re.sub(r"\s+", " ", str(item.get("question") or "")).strip()
        answer = re.sub(r"\s+", " ", str(item.get("answer") or "")).strip()
        if question and answer:
            faq_items.append((question, answer))
    if faq_items:
        details = "".join(
            f"<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>"
            for question, answer in faq_items
        )
        parts.append(f'<section class="article-faq"><h2>FAQ</h2>{details}</section>')
    return "\n".join(parts)


def structured_article_plain_text(draft):
    chunks = [
        draft.get("title"),
        draft.get("description"),
        draft.get("lead"),
        draft.get("quote"),
        draft.get("orderedListTitle"),
    ]
    sections = draft.get("sections") if isinstance(draft.get("sections"), list) else []
    for section in sections:
        if not isinstance(section, dict):
            continue
        chunks.append(section.get("heading"))
        chunks.extend(section.get("paragraphs") if isinstance(section.get("paragraphs"), list) else [])
        chunks.extend(section.get("bullets") if isinstance(section.get("bullets"), list) else [])
    table = draft.get("table") if isinstance(draft.get("table"), dict) else {}
    chunks.extend(table.get("headers") if isinstance(table.get("headers"), list) else [])
    for row in table.get("rows") if isinstance(table.get("rows"), list) else []:
        chunks.extend(row if isinstance(row, list) else [])
    chunks.extend(draft.get("orderedList") if isinstance(draft.get("orderedList"), list) else [])
    for item in draft.get("faq") if isinstance(draft.get("faq"), list) else []:
        if isinstance(item, dict):
            chunks.append(item.get("question"))
            chunks.append(item.get("answer"))
    return " ".join(re.sub(r"\s+", " ", str(chunk or "")).strip() for chunk in chunks if str(chunk or "").strip())


def validate_structured_article_draft(draft):
    errors = []
    title = re.sub(r"\s+", " ", str(draft.get("title") or "")).strip()
    description = re.sub(r"\s+", " ", str(draft.get("description") or "")).strip()
    lead = re.sub(r"\s+", " ", str(draft.get("lead") or "")).strip()
    sections = draft.get("sections") if isinstance(draft.get("sections"), list) else []
    usable_sections = [
        section for section in sections
        if isinstance(section, dict)
        and re.sub(r"\s+", " ", str(section.get("heading") or "")).strip()
        and len([p for p in (section.get("paragraphs") if isinstance(section.get("paragraphs"), list) else []) if str(p or "").strip()]) >= 1
    ]
    images = [image for image in (draft.get("images") if isinstance(draft.get("images"), list) else []) if isinstance(image, dict)]
    faq = [
        item for item in (draft.get("faq") if isinstance(draft.get("faq"), list) else [])
        if isinstance(item, dict) and str(item.get("question") or "").strip() and str(item.get("answer") or "").strip()
    ]
    table = draft.get("table") if isinstance(draft.get("table"), dict) else {}
    table_rows = table.get("rows") if isinstance(table.get("rows"), list) else []
    ordered = [item for item in (draft.get("orderedList") if isinstance(draft.get("orderedList"), list) else []) if str(item or "").strip()]
    word_count = len(re.findall(r"\b[\w'-]+\b", structured_article_plain_text(draft)))
    if len(title) < 18:
        errors.append("title is too short")
    if description and lead and normalize_topic_text(description) == normalize_topic_text(lead):
        errors.append("description duplicates lead")
    if title and lead and normalize_topic_text(title) in normalize_topic_text(lead[:180]):
        errors.append("lead repeats the title")
    if len(usable_sections) < 6:
        errors.append("draft must include at least 6 usable sections")
    if len(images) != 3:
        errors.append("draft must include exactly 3 image specs")
    if len(faq) < 5:
        errors.append("draft must include at least 5 FAQ items")
    if not table.get("headers") or len(table_rows) < 3:
        errors.append("draft must include a useful table")
    if len(ordered) < 5:
        errors.append("draft must include at least 5 ordered-list items")
    if word_count < 1200:
        errors.append(f"draft is too short: {word_count} words, expected at least 1200")
    if errors:
        raise ValueError("Article draft failed validation: " + "; ".join(errors))
    return {"word_count": word_count, "sections": len(usable_sections), "images": len(images), "faq": len(faq)}


def article_asset_job_dir(site_id, job_id):
    safe_job = re.sub(r"[^A-Za-z0-9_.-]", "_", str(job_id))
    return ARTICLE_ASSET_DIR / str(int(site_id)) / safe_job


def article_asset_url(site_id, job_id, filename):
    return f"/sites/{int(site_id)}/article-assets/{urllib.parse.quote(str(job_id), safe='')}/{urllib.parse.quote(filename, safe='')}"


def build_article_image_prompt(site, job, draft, image, role):
    brand = site["brand_name"] or site["domain"]
    title = draft.get("title") or job["topic"] or "Article"
    description = draft.get("description") or job["description"] or ""
    alt = image.get("alt") if isinstance(image, dict) else ""
    caption = image.get("caption") if isinstance(image, dict) else ""
    source_text = structured_article_plain_text(draft)[:2500]
    return f"""
Create one editorial raster JPEG image for a business article.

FORMAT:
- Real JPEG image, 16:9 aspect ratio.
- Editorial/photo-realistic or polished editorial illustration, suitable for a serious website article.
- No text overlay, no headline, no logo, no watermark, no UI screenshot, no readable text.
- If screens, documents, labels, dashboards, packaging, or phones appear, keep them blank, blurred, turned away, or too out-of-focus to read.
- Do not create a social media ad, poster, infographic, meme, collage, or slide.

SITE AND ARTICLE:
- brand: {brand}
- domain: {site['domain']}
- article title: {title}
- article description: {description}
- image role: {role}
- requested alt text: {alt}
- requested caption: {caption}
- article context: {source_text}

VISUAL DIRECTION:
- Make the image specific to the article's business problem and audience.
- Prefer believable environments, people, products, workflows, or abstracted business scenes that support the article.
- Keep it premium, natural, and non-generic.
""".strip()


def generate_article_image_assets(site_id, job_id, site, job, draft, slug):
    target_dir = article_asset_job_dir(site_id, job_id)
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    hero_filename = clean_image_filename(draft.get("heroImage"), f"{slug}-hero.jpg")
    image_specs = draft.get("images") if isinstance(draft.get("images"), list) else []
    assets_to_generate = [("hero", hero_filename, {"alt": draft.get("title") or job["topic"], "caption": draft.get("description") or ""})]
    normalized_images = []
    for index, image in enumerate(image_specs[:3]):
        if not isinstance(image, dict):
            continue
        filename = clean_image_filename(image.get("src"), f"{slug}-image-{index + 1}.jpg")
        normalized = {**image, "src": filename}
        normalized_images.append(normalized)
        assets_to_generate.append((f"body image {index + 1}", filename, normalized))
    draft["images"] = normalized_images
    draft["heroImage"] = hero_filename
    for role, filename, image in assets_to_generate:
        prompt = build_article_image_prompt(site, job, draft, image, role)
        image_bytes = _gemini_image_jpeg(prompt, aspect_ratio="16:9")
        if not image_bytes.startswith(b"\xff\xd8"):
            raise RuntimeError(f"Gemini image for article {role} was not JPEG")
        (target_dir / filename).write_bytes(image_bytes)
    return article_asset_url(site_id, job_id, hero_filename), f"/sites/{int(site_id)}/article-assets/{urllib.parse.quote(str(job_id), safe='')}"


def build_universal_article_prompt(site, job):
    brand = site["brand_name"] or site["domain"]
    context = site["content_context"] or ""
    strategy = site["topic_strategy"] or ""
    languages = languages_to_text(site["languages"])
    source_context = ""
    try:
        source_context = json.dumps(json.loads(job["sources_json"] or "{}"), ensure_ascii=False)
    except Exception:
        source_context = job["sources_json"] or ""
    return f"""
You are an expert SEO and editorial writer for a real business website.
Write a useful, human, expert article for the connected site.

SITE:
- brand: {brand}
- domain: {site['domain']}
- homepage: {site['homepage_url']}
- blog path: {site['blog_path'] or '/blog/'}
- enabled languages: {languages}
- site context: {context}
- topic strategy: {strategy}

ARTICLE JOB:
- topic: {job['topic']}
- category hint: {job['category'] or ''}
- source context: {source_context[:4000]}

QUALITY RULES:
- Output valid JSON matching the provided schema only.
- Write like a specialist editor for this exact site, not a generic AI assistant.
- The article must be a complete long-form page, not a short summary. Target 1400-2200 words across the structured fields.
- Do not repeat `title` inside `lead`, `description`, section headings, or FAQ questions.
- `description` is SEO meta copy. `lead` is the first article paragraph. They must be different.
- Put only the opening article paragraph in `lead`; Blog Core renders the page title separately.
- Use 7-10 section objects; headings must be useful TOC entries and each section must contain 2-4 substantial paragraphs.
- Include at least one useful table object with 3-5 columns and 4-8 rows.
- Include one orderedList with at least 5 practical items and one concise quote.
- Include 5-7 FAQ items with direct answers.
- Include exactly 3 image objects. Image src must be filename only, not absolute URL.
- Image `alt` and `caption` must describe article-specific editorial visuals. Do not leave generic placeholders.
- Do not write raw HTML. Blog Core will render HTML from your structured fields, including the page title, TOC, figures, table, ordered list, quote, and FAQ.
- No em dash, no en dash, no asterisks, no smart quotes.
- Avoid fluff and vague marketing language.
- Make the article clearly connect the problem/question to why {brand} is useful, but do not turn every section into an ad.
""".strip()


def generate_content_job(site_id, job_id):
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
        if not site or not job:
            raise KeyError("job not found")
        sources = content_job_sources(job)
    if sources.get("migratedFrom") and sources.get("oldFactoryJobId"):
        return generate_legacy_factory_content_job(site, job, sources)
    with db() as conn:
        conn.execute("update content_jobs set status='GENERATING', error=NULL, updated_at=? where site_id=? and id=?", (now_iso(), site_id, job_id))
        conn.execute("insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)", (site_id, job_id, now_iso(), "INFO", "generate", "Starting article draft generation"))
    try:
        draft = _gemini_text_json(build_universal_article_prompt(site, job), response_schema=ARTICLE_DRAFT_SCHEMA, repair=False)
        validation = validate_structured_article_draft(draft)
        # Imported/migrated URL paths can carry existing search value. A queued job
        # may lock that canonical slug while still allowing its title and draft to be rewritten.
        preserved_slug = str(job["slug"] or "").strip() if sources.get("preserveSlug") else ""
        slug = preserved_slug or simple_slug(draft.get("slug") or draft.get("title") or job["topic"])
        faq = draft.get("faq") if isinstance(draft.get("faq"), list) else []
        hero_image_url, article_asset_prefix = generate_article_image_assets(site_id, job_id, site, job, draft, slug)
        draft_html = render_structured_article_html(draft, slug, asset_prefix=article_asset_prefix)
        with db() as conn:
            conn.execute(
                """
                update content_jobs set status='DRAFT', slug=?, title=?, description=?, category=?, hero_image=?,
                    draft_html=?, faq_json=?, error=NULL, updated_at=? where site_id=? and id=?
                """,
                (
                    slug,
                    draft.get("title") or job["topic"],
                    draft.get("description") or "",
                    draft.get("category") or job["category"] or "Article",
                    hero_image_url,
                    draft_html,
                    json.dumps(faq, ensure_ascii=False),
                    now_iso(),
                    site_id,
                    job_id,
                ),
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (
                    site_id,
                    job_id,
                    now_iso(),
                    "INFO",
                    "generate",
                    f"Draft generated and validated: {validation['word_count']} words, {validation['sections']} sections, {validation['images']} images, {validation['faq']} FAQ items, 4 article images",
                ),
            )
        if native_content_store_job(job):
            with db() as conn:
                generated_job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
            write_native_content_store(site, generated_job, "drafts")
        return {"ok": True, "jobId": job_id, "status": "DRAFT", "slug": slug}
    except Exception as e:
        with db() as conn:
            conn.execute("update content_jobs set status='ERROR', error=?, updated_at=? where site_id=? and id=?", (str(e), now_iso(), site_id, job_id))
            conn.execute("insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)", (site_id, job_id, now_iso(), "ERROR", "generate", str(e)))
        raise


def legacy_factory_url(factory_name):
    env_name = f"LEGACY_FACTORY_URL_{re.sub(r'[^A-Z0-9]+', '_', factory_name.upper()).strip('_')}"
    explicit = os.environ.get(env_name)
    if explicit:
        return explicit.rstrip("/")
    return LEGACY_FACTORY_ENDPOINTS.get(factory_name)


def legacy_factory_request_json(url, method="GET", timeout=900):
    req = urllib.request.Request(url, method=method, headers={"accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def legacy_factory_request_html(url, timeout=240):
    req = urllib.request.Request(url, headers={"accept": "text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def legacy_job_payload(data):
    if isinstance(data, dict) and isinstance(data.get("job"), dict):
        return data["job"]
    return data if isinstance(data, dict) else {}


def iso_age_seconds(value):
    if not value:
        return 0
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return max(0, int((datetime.now(timezone.utc) - parsed).total_seconds()))
    except Exception:
        return 0


def sync_ready_legacy_factory_job(site_id, job_id, factory_name, old_job_id, legacy):
    draft_html = legacy.get("draftHtml") or legacy.get("draft_html") or ""
    if not draft_html.strip():
        raise RuntimeError(f"Legacy factory returned no draft HTML for {old_job_id}")
    with db() as conn:
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
    if not job:
        raise RuntimeError(f"Blog Core job {job_id} no longer exists")
    merged_sources = content_job_sources(job)
    merged_sources["legacyFactoryResult"] = {
        "factory": factory_name,
        "jobId": old_job_id,
        "status": legacy.get("status"),
        "sources": legacy.get("sources"),
        "queries": legacy.get("queries"),
    }
    faq = legacy.get("faq") or []
    if isinstance(faq, str):
        try:
            faq = json.loads(faq)
        except Exception:
            faq = []
    update_time = now_iso()
    slug = legacy.get("slug") or job["slug"] or simple_slug(legacy.get("title") or job["topic"])
    with db() as conn:
        conn.execute(
            """
            update content_jobs set status='DRAFT', slug=?, title=?, description=?, category=?, hero_image=?,
                draft_html=?, faq_json=?, sources_json=?, error=NULL, updated_at=? where site_id=? and id=?
            """,
            (
                slug,
                legacy.get("title") or job["title"] or job["topic"],
                legacy.get("description") or job["description"] or "",
                legacy.get("category") or job["category"] or "Article",
                legacy.get("heroImage") or legacy.get("hero_image") or job["hero_image"] or "",
                draft_html,
                json.dumps(faq if isinstance(faq, list) else [], ensure_ascii=False),
                json.dumps(merged_sources, ensure_ascii=False),
                update_time,
                site_id,
                job["id"],
            ),
        )
        conn.execute(
            "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
            (site_id, job["id"], update_time, "INFO", "legacy-generate", f"Synced validated draft from {factory_name}"),
        )
    return True


def maybe_sync_legacy_factory_status(site_id, job_id, force=False):
    key = f"{int(site_id)}:{job_id}"
    now_ts = time.time()
    if not force and now_ts - LEGACY_STATUS_CHECKS.get(key, 0) < 12:
        return False
    LEGACY_STATUS_CHECKS[key] = now_ts
    with db() as conn:
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
    if not job or job["status"] != "GENERATING":
        return False
    sources = content_job_sources(job)
    factory_name = str(sources.get("migratedFrom") or "").strip()
    old_job_id = str(sources.get("oldFactoryJobId") or "").strip()
    if not factory_name or not old_job_id:
        return False
    base_url = legacy_factory_url(factory_name)
    if not base_url:
        return False
    try:
        quoted_job_id = urllib.parse.quote(old_job_id)
        detail = legacy_factory_request_json(f"{base_url}/api/jobs/{quoted_job_id}", timeout=30)
        legacy = legacy_job_payload(detail)
        legacy_status = str(legacy.get("status") or "").upper()
        if legacy_status in {"READY", "PUBLISHED"}:
            return sync_ready_legacy_factory_job(site_id, job_id, factory_name, old_job_id, legacy)
        if legacy_status == "ERROR":
            message = legacy.get("error") or f"Legacy factory job {old_job_id} failed"
            with db() as conn:
                conn.execute("update content_jobs set status='ERROR', error=?, updated_at=? where site_id=? and id=?", (message, now_iso(), site_id, job_id))
                conn.execute(
                    "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                    (site_id, job_id, now_iso(), "ERROR", "legacy-generate", message),
                )
            return True
        if legacy_status == "GENERATING" and iso_age_seconds(job["updated_at"]) > 45 * 60:
            message = f"Legacy factory job {old_job_id} is still GENERATING after more than 45 minutes; retry generation from Blog Core."
            with db() as conn:
                conn.execute("update content_jobs set status='ERROR', error=?, updated_at=? where site_id=? and id=?", (message, now_iso(), site_id, job_id))
                conn.execute(
                    "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                    (site_id, job_id, now_iso(), "ERROR", "legacy-generate", message),
                )
            return True
    except Exception as e:
        message = f"Legacy factory status check failed: {e}"
        with db() as conn:
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (site_id, job_id, now_iso(), "WARNING", "legacy-status", message),
            )
    return False


def generate_legacy_factory_content_job(site, job, sources):
    factory_name = str(sources.get("migratedFrom") or "").strip()
    old_job_id = str(sources.get("oldFactoryJobId") or "").strip()
    base_url = legacy_factory_url(factory_name)
    if not base_url:
        raise RuntimeError(f"No legacy factory endpoint configured for {factory_name}")
    now = now_iso()
    with db() as conn:
        conn.execute("update content_jobs set status='GENERATING', error=NULL, updated_at=? where site_id=? and id=?", (now, site["id"], job["id"]))
        conn.execute(
            "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
            (site["id"], job["id"], now, "INFO", "legacy-generate", f"Queued legacy factory generation via {factory_name} job {old_job_id}"),
        )
    thread = threading.Thread(target=legacy_factory_generate_and_sync, args=(site["id"], job["id"], factory_name, old_job_id, base_url), daemon=True)
    thread.start()
    return {"ok": True, "jobId": job["id"], "status": "GENERATING", "legacyFactory": factory_name, "legacyJobId": old_job_id}


def legacy_factory_generate_and_sync(site_id, job_id, factory_name, old_job_id, base_url):
    try:
        quoted_job_id = urllib.parse.quote(old_job_id)
        detail = legacy_factory_request_json(f"{base_url}/api/jobs/{quoted_job_id}")
        legacy = legacy_job_payload(detail)
        if str(legacy.get("status") or "").upper() not in {"GENERATING", "READY", "PUBLISHED"}:
            result = legacy_factory_request_json(f"{base_url}/api/jobs/{quoted_job_id}/generate", method="POST")
            if result.get("success") is False:
                raise RuntimeError(result.get("error") or json.dumps(result, ensure_ascii=False)[:500])
        deadline = time.time() + 1800
        while time.time() < deadline:
            detail = legacy_factory_request_json(f"{base_url}/api/jobs/{quoted_job_id}")
            legacy = legacy_job_payload(detail)
            status = str(legacy.get("status") or "").upper()
            if status in {"READY", "PUBLISHED"}:
                break
            if status == "ERROR":
                raise RuntimeError(legacy.get("error") or f"Legacy factory job {old_job_id} failed")
            time.sleep(5)
        else:
            raise RuntimeError(f"Legacy factory job {old_job_id} did not finish within 30 minutes")
        sync_ready_legacy_factory_job(site_id, job_id, factory_name, old_job_id, legacy)
    except Exception as e:
        with db() as conn:
            conn.execute("update content_jobs set status='ERROR', error=?, updated_at=? where site_id=? and id=?", (str(e), now_iso(), site_id, job_id))
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (site_id, job_id, now_iso(), "ERROR", "legacy-generate", str(e)),
            )


def publish_content_job(site_id, job_id):
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
    if not site or not job:
        raise KeyError("job not found")
    if job["status"] not in {"DRAFT", "PUBLISHED"}:
        raise ValueError(f"Job status must be DRAFT or PUBLISHED before publish, got {job['status']}")
    sources = content_job_sources(job)
    if native_content_store_job(job):
        published_path = write_native_content_store(site, job, "published")
        published_url = content_job_source_url(site, job)
        now = now_iso()
        with db() as conn:
            conn.execute(
                "update content_jobs set status='PUBLISHED', published_url=?, error=NULL, updated_at=? where site_id=? and id=?",
                (published_url, now, site_id, job_id),
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (site_id, job_id, now, "INFO", "native-publish", f"Published native content record: {published_path}"),
            )
        return {"ok": True, "jobId": job_id, "status": "PUBLISHED", "publishedUrl": published_url, "publisher": "native-content-store"}
    factory_name = str(sources.get("migratedFrom") or "").strip()
    old_job_id = str(sources.get("oldFactoryJobId") or "").strip()
    if not factory_name or not old_job_id or sources.get("ownership") != "source_site_authoritative":
        raise ValueError("Publish is currently available only for source-authoritative imported factory jobs")
    base_url = legacy_factory_url(factory_name)
    if not base_url:
        raise RuntimeError(f"No legacy factory endpoint configured for {factory_name}")
    quoted_job_id = urllib.parse.quote(old_job_id)
    now = now_iso()
    with db() as conn:
        conn.execute(
            "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
            (site_id, job_id, now, "INFO", "legacy-publish", f"Publishing via {factory_name} job {old_job_id}"),
        )
    try:
        result = legacy_factory_request_json(f"{base_url}/api/jobs/{quoted_job_id}/publish", method="POST", timeout=900)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Legacy factory publish failed: HTTP {e.code}: {body}") from e
    if isinstance(result, dict) and result.get("success") is False:
        raise RuntimeError(result.get("error") or json.dumps(result, ensure_ascii=False)[:1000])
    try:
        detail = legacy_factory_request_json(f"{base_url}/api/jobs/{quoted_job_id}", timeout=30)
        legacy = legacy_job_payload(detail)
    except Exception:
        legacy = {}
    source_url = result.get("url") if isinstance(result, dict) else ""
    path = result.get("path") if isinstance(result, dict) else ""
    published_url = source_url or legacy.get("publishedUrl") or legacy.get("published_url") or path or content_job_source_url(site, job)
    if published_url and not urllib.parse.urlsplit(str(published_url)).scheme:
        published_url = urllib.parse.urljoin(public_site_base_url(site), str(published_url).lstrip("/"))
    merged_sources = content_job_sources(job)
    merged_sources["legacyFactoryResult"] = {
        "factory": factory_name,
        "jobId": old_job_id,
        "status": legacy.get("status") or "PUBLISHED",
        "publishResult": result,
    }
    with db() as conn:
        conn.execute(
            "update content_jobs set status='PUBLISHED', published_url=?, sources_json=?, error=NULL, updated_at=? where site_id=? and id=?",
            (published_url, json.dumps(merged_sources, ensure_ascii=False), now_iso(), site_id, job_id),
        )
        conn.execute(
            "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
            (site_id, job_id, now_iso(), "INFO", "legacy-publish", f"Published via {factory_name}: {published_url}"),
        )
    return {"ok": True, "jobId": job_id, "status": "PUBLISHED", "publishedUrl": published_url, "legacyFactory": factory_name, "legacyJobId": old_job_id, "result": result}


def get_site_by_custom_host(host):
    host = clean_host(host)
    if not host:
        return None
    with db() as conn:
        return conn.execute(
            "select * from sites where hosted_blog_enabled=1 and lower(custom_blog_domain)=?",
            (host,),
        ).fetchone()


def public_base_url():
    proto = request.headers.get("X-Forwarded-Proto") or request.scheme or "https"
    return f"{proto}://{request_host()}"


def render_hosted_blog_response(site, public_path):
    profile = get_profile(site["id"])
    if not profile:
        return Response("Blog design is not published yet. Scan design and build preview first.", status=503, mimetype="text/plain")
    path = (public_path or "").strip("/")
    source_css = profile["head_css"] if profile and "head_css" in profile.keys() and profile["head_css"] else ""
    source_css_urls = json.loads(profile["css_urls_json"] or "[]") if profile else []
    header = profile["header_html"] if profile and profile["header_html"] else ""
    footer = profile["footer_html"] if profile and profile["footer_html"] else ""
    brand = site["brand_name"] or site["domain"]
    if path in ("blog-core.css", "blog/blog-core.css"):
        return Response(theme_css(profile), mimetype="text/css")
    if path in ("robots.txt",):
        base = public_base_url()
        return Response(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", mimetype="text/plain")
    if path in ("sitemap.xml",):
        base = public_base_url().rstrip("/")
        jobs = get_public_content_jobs(site["id"], limit=1000)
        urls = [f"  <url><loc>{base}/blog/</loc></url>"]
        if jobs:
            urls.extend(f"  <url><loc>{base}/blog/{escape(row['slug'].strip('/'))}/</loc></url>" for row in jobs)
        else:
            urls.append(f"  <url><loc>{base}/blog/visual-chaos-in-ai-product-cards/</loc></url>")
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
        return Response(xml, mimetype="application/xml")
    if path in ("", "blog"):
        jobs = get_public_content_jobs(site["id"])
        html = render_blog_index_from_jobs(brand, header, footer, jobs, "/blog-core.css", source_css, source_css_urls)
        return Response(html, mimetype="text/html")
    if path in ("blog/visual-chaos-in-ai-product-cards", "visual-chaos-in-ai-product-cards"):
        html = render_sample_article(brand, header, footer, "/blog-core.css", source_css, source_css_urls)
        return Response(html, mimetype="text/html")
    if path.startswith("blog/"):
        slug = path.split("/", 1)[1].strip("/")
        job = get_content_job_by_slug(site["id"], slug)
        if job:
            html = render_content_job_article(brand, header, footer, job, "/blog-core.css", source_css, source_css_urls)
            return Response(html, mimetype="text/html")
    abort(404)


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "blog-core", "time": now_iso()})


@app.get("/previews/<path:path>")
def previews(path):
    target = PREVIEW_DIR / path
    if target.is_dir():
        return send_from_directory(target, "index.html")
    return send_from_directory(PREVIEW_DIR, path)


@app.get("/")
def index():
    host = request_host()
    if not is_admin_host(host):
        site = get_site_by_custom_host(host)
        if site:
            return render_hosted_blog_response(site, "")
        abort(404)
    with db() as conn:
        sites = conn.execute(
            """
            select s.*, p.scanned_at, t.preview_path,
                   (select count(*) from content_jobs cj where cj.site_id=s.id and cj.status='IMPORTED') as imported_count
            from sites s
            left join site_theme_profiles p on p.site_id=s.id
            left join blog_templates t on t.site_id=s.id
            order by s.updated_at desc
            """
        ).fetchall()
    rows = "".join(render_site_row(s) for s in sites) or "<div class='empty'>No sites connected yet.</div>"
    return DASHBOARD_HTML.replace("__ROWS__", rows)


def render_site_row(s):
    preview = render_primary_site_link(s)
    scanned = escape(s["scanned_at"] or "Not scanned")
    imported_count = int(s["imported_count"] or 0) if "imported_count" in s.keys() else 0
    if imported_count:
        technical_actions = f"<span class='site-state imported'>Imported live site · {imported_count} pages</span>"
    else:
        technical_actions = f"""
    <button onclick="runAction({s['id']}, 'scan')">Scan design</button>
    <button onclick="runAction({s['id']}, 'bootstrap-preview')">Build preview</button>
    <button onclick="runAction({s['id']}, 'install-blog')">Install /blog</button>
"""
    return f"""
<div class="site-card">
  <div>
    <div class="site-domain">{escape(s['domain'])}</div>
    <div class="site-url">{escape(s['homepage_url'])}</div>
    <div class="site-meta">root: {escape(s['root_path'] or 'not set')} · scanned: {scanned}</div>
  </div>
  <div class="actions">
    <a class="btn ghost" href="/sites/{s['id']}">Manage</a>
    {technical_actions}
    {preview}
    <button class="danger" onclick="deleteSite({s['id']}, '{escape(s['domain'], quote=True)}')">Delete</button>
  </div>
</div>
"""


@app.get("/sites/<int:site_id>")
def manage_site(site_id):
    site = get_site_full(site_id)
    if not site:
        return redirect("/")
    return render_manage_site_page(site)


@app.post("/sites/<int:site_id>/settings")
def update_site_settings(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    payload = request.form.to_dict()
    homepage = normalize_url(payload.get("homepage_url") or site["homepage_url"])
    if not homepage:
        return jsonify({"error": "homepage_url is required"}), 400
    domain = domain_from_url(homepage)
    now = now_iso()
    with db() as conn:
        conn.execute(
            """
            update sites
            set domain=?, homepage_url=?, root_path=?, blog_path=?, custom_blog_domain=?, hosted_blog_enabled=?,
                languages=?, brand_name=?, content_context=?, factory_enabled=?, publishing_cadence=?,
                topic_strategy=?, updated_at=?
            where id=?
            """,
            (
                domain,
                homepage,
                payload.get("root_path") or "",
                payload.get("blog_path") or "/blog/",
                clean_host(payload.get("custom_blog_domain")),
                form_bool(payload.get("hosted_blog_enabled")),
                text_to_languages(payload.get("languages")),
                payload.get("brand_name") or domain.split(".")[0].replace("-", " ").title(),
                payload.get("content_context") or "",
                form_bool(payload.get("factory_enabled")),
                payload.get("publishing_cadence") or "manual",
                payload.get("topic_strategy") or "",
                now,
                site_id,
            ),
        )
    return redirect(f"/sites/{site_id}")


@app.post("/api/sites/<int:site_id>/queue-topic-plan")
def queue_topic_plan(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    with db() as conn:
        conn.execute(
            "insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)",
            (site_id, "topic-plan", "queued", "Topic planning queued from site factory settings", now_iso()),
        )
    return jsonify({"ok": True})


@app.post("/api/sites/<int:site_id>/delete")
def delete_site(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    with db() as conn:
        conn.execute("delete from site_theme_profiles where site_id=?", (site_id,))
        conn.execute("delete from blog_templates where site_id=?", (site_id,))
        conn.execute("delete from publish_jobs where site_id=?", (site_id,))
        conn.execute("delete from sites where id=?", (site_id,))
    shutil.rmtree(PREVIEW_DIR / str(site_id), ignore_errors=True)
    return jsonify({"ok": True, "deleted": site_id, "note": "Installed /blog files were not removed from the target site root."})


@app.put("/api/sites/<int:site_id>/social-connections/<provider>")
def update_social_connection(site_id, provider):
    if provider not in SOCIAL_PROVIDER_CONFIG:
        return jsonify({"error": "unsupported provider"}), 404
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    credentials = payload.get("credentials") or {}
    if not isinstance(credentials, dict):
        credentials = {}
    allowed = {field[0] for field in SOCIAL_PROVIDER_CONFIG[provider]["fields"]}
    clean_credentials = {key: str(value).strip() for key, value in credentials.items() if key in allowed and str(value or "").strip()}
    with db() as conn:
        current = conn.execute("select * from social_connections where site_id=? and provider=?", (site_id, provider)).fetchone()
    merged = {**get_social_credentials(current), **clean_credentials}
    status = "configured" if social_credentials_complete(provider, merged) else "disconnected"
    result = upsert_social_connection(site_id, provider, clean_credentials, status=status)
    return jsonify({"ok": True, "provider": provider, "status": result["status"], "configured": result["configured"]})


@app.post("/api/sites/<int:site_id>/social-connections/<provider>/test")
def test_social_connection_route(site_id, provider):
    if provider not in SOCIAL_PROVIDER_CONFIG:
        return jsonify({"error": "unsupported provider"}), 404
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    inline_credentials = payload.get("credentials") or {}
    if not isinstance(inline_credentials, dict):
        inline_credentials = {}
    allowed = {field[0] for field in SOCIAL_PROVIDER_CONFIG[provider]["fields"]}
    inline_credentials = {key: str(value).strip() for key, value in inline_credentials.items() if key in allowed and str(value or "").strip()}
    with db() as conn:
        current = conn.execute("select * from social_connections where site_id=? and provider=?", (site_id, provider)).fetchone()
    credentials = {**get_social_credentials(current), **inline_credentials}
    if inline_credentials:
        upsert_social_connection(site_id, provider, inline_credentials, status="configured")
    result = test_social_connection(provider, credentials)
    upsert_social_connection(
        site_id,
        provider,
        {},
        status=result["status"],
        display_name=result.get("displayName") if result.get("ok") else None,
        settings={"lastTestMessage": result.get("message", "")},
    )
    code = 200 if result.get("ok") else 400
    return jsonify({"ok": bool(result.get("ok")), "provider": provider, "status": result["status"], "message": result.get("message", "")}), code


@app.post("/api/sites/<int:site_id>/social-connections/linkedin/connect")
def linkedin_connect_route(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    if not linkedin_oauth_configured():
        return jsonify({"error": "LinkedIn OAuth is not configured on this server."}), 503
    state = secrets.token_urlsafe(32)
    now = time.time()
    for key, value in list(LINKEDIN_OAUTH_STATES.items()):
        if value.get("expiresAt", 0) < now:
            LINKEDIN_OAUTH_STATES.pop(key, None)
    LINKEDIN_OAUTH_STATES[state] = {"siteId": site_id, "expiresAt": now + 600}
    query = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": os.environ["LINKEDIN_CLIENT_ID"],
        "redirect_uri": linkedin_oauth_redirect_uri(),
        "state": state,
        "scope": "openid profile w_member_social",
    })
    return jsonify({"ok": True, "authUrl": f"https://www.linkedin.com/oauth/v2/authorization?{query}"})


@app.get("/oauth/linkedin/callback")
def linkedin_oauth_callback():
    error = request.args.get("error")
    state = request.args.get("state") or ""
    record = LINKEDIN_OAUTH_STATES.pop(state, None)
    if error:
        return Response(f"LinkedIn authorization was not completed: {escape(error)}", status=400, mimetype="text/html")
    if not record or record.get("expiresAt", 0) < time.time():
        return Response("LinkedIn authorization expired. Start Connect LinkedIn again.", status=400, mimetype="text/html")
    code = request.args.get("code") or ""
    if not code or not linkedin_oauth_configured():
        return Response("LinkedIn authorization is missing a code or server configuration.", status=400, mimetype="text/html")
    try:
        token_data, _ = fetch_form_json_request(
            "https://www.linkedin.com/oauth/v2/accessToken",
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": linkedin_oauth_redirect_uri(),
                "client_id": os.environ["LINKEDIN_CLIENT_ID"],
                "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
            },
        )
        access_token = str(token_data.get("access_token") or "").strip()
        if not access_token:
            raise ValueError(token_data.get("error_description") or token_data.get("error") or "LinkedIn did not return an access token.")
        user, _ = fetch_json_request("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        person_id = str(user.get("sub") or "").strip()
        if not person_id:
            raise ValueError(user.get("message") or "LinkedIn did not return the personal profile id.")
        site_id = int(record["siteId"])
        display_name = str(user.get("name") or "LinkedIn member").strip()
        upsert_social_connection(
            site_id,
            "linkedin",
            {"access_token": access_token, "author_urn": f"urn:li:person:{person_id}"},
            status="connected",
            display_name=display_name,
            settings={"oauthConnectedAt": now_iso(), "authorType": "person"},
        )
        return redirect(f"/sites/{site_id}#setup", code=302)
    except Exception as exc:
        return Response(f"LinkedIn connection failed: {escape(str(exc))}", status=502, mimetype="text/html")


@app.get("/api/sites/<int:site_id>/topic-signals")
def topic_signals(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    range_key = request.args.get("range") or "week"
    if range_key not in {"week", "month", "3m", "6m"}:
        range_key = "week"
    popular_search, popular_search_warnings, popular_search_meta = fetch_popular_search_signals(site, range_key)
    reddit, reddit_warnings, reddit_meta = fetch_reddit_signals(site, range_key)
    signals = popular_search + reddit
    return jsonify({
        "ok": True,
        "range": range_key,
        "query": broad_topic_signal_query(site),
        "signals": signals,
        "sources": {
            "popularSearches": {
                "label": "Search demand signals",
                "description": "Autocomplete demand signals. The selected period does not apply to this source.",
                "rangeApplies": False,
                "signals": popular_search,
                "warnings": popular_search_warnings,
                "meta": popular_search_meta,
            },
            "reddit": {
                "label": "Reddit discussions",
                "description": "Top Reddit discussions for the selected period bucket.",
                "rangeApplies": True,
                "range": range_key,
                "bucket": reddit_meta.get("bucket"),
                "signals": reddit,
                "warnings": reddit_warnings,
                "meta": reddit_meta,
            },
        },
        "warnings": popular_search_warnings + reddit_warnings,
        "counts": {
            "popularSearches": len(popular_search),
            "reddit": len(reddit),
            "total": len(signals),
            "popularSearchesRaw": popular_search_meta.get("raw", 0),
            "popularSearchesFiltered": popular_search_meta.get("filteredGlobal", 0) + popular_search_meta.get("filteredRelevance", 0) + popular_search_meta.get("deduped", 0),
            "redditRaw": reddit_meta.get("raw", 0),
            "redditFiltered": reddit_meta.get("filteredGlobal", 0) + reddit_meta.get("filteredRelevance", 0) + reddit_meta.get("deduped", 0),
        },
    })


@app.post("/api/sites/<int:site_id>/article-ideas")
def create_article_ideas(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    signals = payload.get("signals") or []
    if not isinstance(signals, list) or not signals:
        return jsonify({"error": "select at least one trend or discussion"}), 400
    ideas, rejected, stats = generate_article_ideas(site, signals)
    if not ideas:
        return jsonify({"error": "no new usable article ideas after duplicate checks", "rejectedSimilar": rejected, "counts": stats}), 400
    return jsonify({"ok": True, "ideas": ideas, "rejectedSimilar": rejected, "counts": {**stats, "ideas": len(ideas), "rejectedSimilar": len(rejected)}})


@app.post("/api/sites/<int:site_id>/article-ideas/queue")
def queue_article_ideas(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    ideas = payload.get("ideas") or []
    if not isinstance(ideas, list) or not ideas:
        return jsonify({"error": "select at least one article idea"}), 400
    existing_index = existing_topic_index(site_id)
    clean_ideas = []
    rejected = []
    seen = set()
    for idea in ideas[:50]:
        if not isinstance(idea, dict):
            continue
        title = re.sub(r"\s+", " ", str(idea.get("title") or "")).strip()
        if not title:
            continue
        key = simple_slug(title)
        if key in seen:
            continue
        seen.add(key)
        clean = {
            "title": title,
            "angle": re.sub(r"\s+", " ", str(idea.get("angle") or "")).strip(),
            "source": idea.get("source") or "discovery",
            "source_title": idea.get("source_title") or "",
            "source_url": idea.get("source_url") or "",
            "contentType": "seo_money_page" if str(idea.get("contentType") or "").lower() in {"use_case", "use-cases", "seo_money_page", "seo-money-page"} else "blog",
        }
        similar = find_similar_existing_topic(clean, existing_index)
        if similar:
            rejected.append({"idea": clean, "similar": similar})
            continue
        clean_ideas.append(clean)
    if not clean_ideas:
        return jsonify({"error": "all selected ideas are too similar to existing site content", "rejectedSimilar": rejected}), 400
    message = json.dumps({"range": payload.get("range") or "week", "signals": payload.get("signals") or [], "ideas": clean_ideas, "rejectedSimilar": rejected}, ensure_ascii=False)
    created_jobs = []
    with db() as conn:
        conn.execute(
            "insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)",
            (site_id, "article-ideas", "queued", message, now_iso()),
        )
        for idea in clean_ideas:
            title = idea.get("title") or "Article idea"
            job_id = secrets.token_hex(12)
            slug = simple_slug(title)
            now = now_iso()
            is_money_page = idea.get("contentType") == "seo_money_page"
            target_path = f"/use-cases/{slug}/" if is_money_page else f"/blog/{slug}/"
            sources = {
                **idea,
                "contentType": "seo_money_page" if is_money_page else "blog",
                "pageType": "seo_money_page" if is_money_page else "blog",
                "targetPath": target_path,
                "canonicalGroup": target_path,
            }
            conn.execute(
                """
                insert into content_jobs(
                    id, site_id, topic, slug, status, title, description, category,
                    sources_json, visibility, created_at, updated_at
                ) values(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    job_id,
                    site_id,
                    title,
                    slug,
                    "QUEUED",
                    title,
                    idea.get("angle") or "",
                    "SEO Money Page" if is_money_page else "Article Ideas",
                    json.dumps(sources, ensure_ascii=False),
                    "public",
                    now,
                    now,
                ),
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (site_id, job_id, now, "INFO", "queue", "Created from selected Discovery article idea"),
            )
            created_jobs.append({"id": job_id, "title": title, "slug": slug})
    return jsonify({"ok": True, "ideas": clean_ideas, "jobs": created_jobs, "rejectedSimilar": rejected})


@app.get("/api/sites/<int:site_id>/factory-settings")
def get_factory_settings(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    auto = get_autopublish_settings(site_id)
    disc = get_topic_discovery_settings(site_id)
    social = get_social_connections(site_id)
    safe_social = {}
    for provider, row in social.items():
        if not row:
            safe_social[provider] = {"provider": provider, "status": "disconnected", "configured": False}
            continue
        item = dict(row)
        item.pop("credentials_json", None)
        item["configured"] = social_credentials_complete(provider, get_social_credentials(row))
        safe_social[provider] = item
    return jsonify({
        "ok": True,
        "autopublish": dict(auto),
        "topicDiscovery": dict(disc),
        "social": safe_social,
    })


@app.put("/api/sites/<int:site_id>/factory-settings")
def update_factory_settings(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    channels = payload.get("channels") or []
    if not isinstance(channels, list):
        channels = []
    allowed_channels = [c for c in channels if c in SOCIAL_CHANNEL_LIMITS]
    topic = payload.get("topicDiscovery") or {}
    auto = payload.get("autopublish") or {}
    now = now_iso()
    with db() as conn:
        conn.execute(
            """
            insert into topic_discovery_settings(
                site_id, enabled, timezone, run_hour, direction, category_hint,
                per_run_limit, min_score, top_n, product_mode, engagement_mode, lead_magnet_mode, updated_at
            ) values(?,?,?,?,?,?,?,?,?,?,?,?,?)
            on conflict(site_id) do update set
                enabled=excluded.enabled, timezone=excluded.timezone, run_hour=excluded.run_hour,
                direction=excluded.direction, category_hint=excluded.category_hint,
                per_run_limit=excluded.per_run_limit, min_score=excluded.min_score, top_n=excluded.top_n,
                product_mode=excluded.product_mode, engagement_mode=excluded.engagement_mode,
                lead_magnet_mode=excluded.lead_magnet_mode, updated_at=excluded.updated_at
            """,
            (
                site_id,
                1 if topic.get("enabled") else 0,
                topic.get("timezone") or "UTC",
                int(topic.get("runHour") or 6),
                topic.get("direction") or "",
                topic.get("categoryHint") or "",
                int(topic.get("perRunLimit") or 15),
                float(topic.get("minScore") or 55.0),
                int(topic.get("topN") or 3),
                1 if topic.get("productMode") else 0,
                1 if topic.get("engagementMode") else 0,
                1 if topic.get("leadMagnetMode") else 0,
                now,
            ),
        )
        conn.execute(
            """
            insert into autopublish_settings(
                site_id, enabled, times_per_day, channels_json, timezone, start_hour, end_hour,
                linkedin_include_link, telegram_include_link, twitter_include_link, tumblr_include_link,
                pinterest_include_link, instagram_include_link, threads_include_link, reddit_include_link, updated_at
            ) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            on conflict(site_id) do update set
                enabled=excluded.enabled, times_per_day=excluded.times_per_day, channels_json=excluded.channels_json,
                timezone=excluded.timezone, start_hour=excluded.start_hour, end_hour=excluded.end_hour,
                linkedin_include_link=excluded.linkedin_include_link, telegram_include_link=excluded.telegram_include_link,
                twitter_include_link=excluded.twitter_include_link, tumblr_include_link=excluded.tumblr_include_link,
                pinterest_include_link=excluded.pinterest_include_link,
                instagram_include_link=excluded.instagram_include_link,
                threads_include_link=excluded.threads_include_link,
                reddit_include_link=excluded.reddit_include_link,
                updated_at=excluded.updated_at
            """,
            (
                site_id,
                1 if auto.get("enabled") else 0,
                int(auto.get("timesPerDay") or 3),
                json.dumps(allowed_channels or ["linkedin", "telegram", "twitter", "tumblr", "pinterest", "instagram", "threads", "reddit"]),
                auto.get("timezone") or "UTC",
                int(auto.get("startHour") or 9),
                int(auto.get("endHour") or 21),
                1 if auto.get("linkedinIncludeLink") else 0,
                1 if auto.get("telegramIncludeLink") else 0,
                1 if auto.get("twitterIncludeLink") else 0,
                1 if auto.get("tumblrIncludeLink") else 0,
                1 if auto.get("pinterestIncludeLink") else 0,
                1 if auto.get("instagramIncludeLink") else 0,
                1 if auto.get("threadsIncludeLink") else 0,
                1 if auto.get("redditIncludeLink") else 0,
                now,
            ),
        )
    return jsonify({"ok": True})


@app.get("/api/sites/<int:site_id>/content-jobs")
def list_content_jobs(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    content_page = get_content_jobs(
        site_id,
        page=request.args.get("page", 1),
        per_page=request.args.get("per_page", 24),
        language=request.args.get("language", "en"),
        content_type=request.args.get("content_type", "all"),
    )
    return jsonify({
        "ok": True,
        "jobs": [dict(r) for r in content_page["rows"]],
        "page": content_page["page"],
        "per_page": content_page["per_page"],
        "total": content_page["total"],
        "total_pages": content_page["total_pages"],
        "language": content_page["language"],
        "available_languages": content_page["available_languages"],
        "content_type": content_page["content_type"],
        "available_content_types": content_page["available_content_types"],
    })


@app.put("/api/sites/<int:site_id>/podcast-settings")
def update_podcast_settings(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    voice_name = str(payload.get("voiceName") or "Kore").strip()
    if voice_name not in PODCAST_VOICES:
        return jsonify({"error": "unsupported Gemini voice"}), 400
    try:
        target_minutes = max(3, min(20, int(payload.get("targetMinutes") or 8)))
    except (TypeError, ValueError):
        return jsonify({"error": "target minutes must be a number"}), 400
    with db() as conn:
        conn.execute(
            """insert into podcast_settings(site_id,enabled,host_name,voice_name,voice_direction,target_minutes,updated_at)
               values(?,?,?,?,?,?,?)
               on conflict(site_id) do update set enabled=excluded.enabled,host_name=excluded.host_name,
                 voice_name=excluded.voice_name,voice_direction=excluded.voice_direction,target_minutes=excluded.target_minutes,
                 updated_at=excluded.updated_at""",
            (site_id, 1 if payload.get("enabled") else 0, str(payload.get("hostName") or "").strip(), voice_name,
             str(payload.get("voiceDirection") or "").strip(), target_minutes, now_iso()),
        )
    return jsonify({"ok": True})


@app.post("/api/sites/<int:site_id>/podcast-episodes")
def create_podcast_episode(site_id):
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(generate_podcast_episode(site_id, str(payload.get("jobId") or "").strip()))
    except KeyError:
        return jsonify({"error": "article not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/podcast-episodes/<episode_id>/publish")
def publish_podcast_episode_route(site_id, episode_id):
    try:
        return jsonify(publish_podcast_episode(site_id, episode_id))
    except KeyError:
        return jsonify({"error": "episode not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/sites/<int:site_id>/content-jobs/<job_id>")
def get_content_job(site_id, job_id):
    maybe_sync_legacy_factory_status(site_id, job_id)
    with db() as conn:
        row = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
        logs = conn.execute("select * from content_job_logs where site_id=? and job_id=? order by ts asc", (site_id, job_id)).fetchall()
    if not row:
        return jsonify({"error": "job not found"}), 404
    return jsonify({"ok": True, "job": dict(row), "logs": [dict(r) for r in logs]})


@app.get("/sites/<int:site_id>/blog-core.css")
def site_blog_core_css(site_id):
    profile = get_profile(site_id)
    if not profile:
        return Response("/* no profile */", mimetype="text/css")
    return Response(theme_css(profile), mimetype="text/css")


@app.get("/sites/<int:site_id>/content-jobs/<job_id>/preview")
def preview_content_job(site_id, job_id):
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
    if not site or not job:
        return Response("Draft not found.", status=404, mimetype="text/plain")
    if job["status"] not in {"DRAFT", "PUBLISHED", "IMPORTED"} or not (job["draft_html"] or "").strip():
        return Response("Draft is not generated yet.", status=409, mimetype="text/plain")
    if native_content_store_job(job):
        if job["status"] == "PUBLISHED":
            return redirect(content_job_source_url(site, job), code=302)
        try:
            write_native_content_store(site, job, "drafts")
            return redirect(urllib.parse.urljoin(public_site_base_url(site), f"content-preview/{job_id}"), code=302)
        except Exception as e:
            return Response(f"Native content preview is unavailable: {e}", status=502, mimetype="text/plain")
    if source_authoritative_content_job(job):
        source_url = content_job_source_url(site, job)
        if job["status"] in {"PUBLISHED", "IMPORTED"} and source_url:
            return redirect(source_url, code=302)
        sources = content_job_sources(job)
        factory_name = str(sources.get("migratedFrom") or "").strip()
        old_job_id = str(sources.get("oldFactoryJobId") or "").strip()
        base_url = legacy_factory_url(factory_name)
        if factory_name and old_job_id and base_url:
            try:
                draft_html = legacy_factory_request_html(
                    f"{base_url}/preview/{urllib.parse.quote(old_job_id)}",
                    timeout=240,
                )
                if source_url:
                    parsed = urllib.parse.urlsplit(source_url)
                    asset_base = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "/", "", ""))
                    if not re.search(r"<base\b", draft_html, flags=re.IGNORECASE):
                        draft_html = re.sub(
                            r"<head(\s[^>]*)?>",
                            lambda m: m.group(0) + f'<base href="{escape(asset_base, quote=True)}">',
                            draft_html,
                            count=1,
                            flags=re.IGNORECASE,
                        )
                return Response(draft_html, mimetype="text/html")
            except Exception as e:
                return Response(
                    f"Native source-factory draft preview is unavailable: {e}",
                    status=502,
                    mimetype="text/plain",
                )
        return Response(
            "Native source-factory draft preview is unavailable because this imported task has no connected source factory.",
            status=409,
            mimetype="text/plain",
        )
    if (site["access_type"] or "") == "local_path" and (site["root_path"] or "").strip():
        html = render_local_site_draft_preview(site, job)
        if html:
            return Response(html, mimetype="text/html")
    profile = get_profile(site_id)
    brand = site["brand_name"] or site["domain"]
    if profile:
        source_css = profile["head_css"] if "head_css" in profile.keys() and profile["head_css"] else ""
        source_css_urls = json.loads(profile["css_urls_json"] or "[]")
        html = render_content_job_article(
            brand,
            profile["header_html"] or "",
            profile["footer_html"] or "",
            job,
            f"/sites/{site_id}/blog-core.css",
            source_css,
            source_css_urls,
        )
    else:
        html = f"""
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(job['title'] or job['topic'] or 'Draft')}</title>
<style>body{{font-family:Inter,system-ui,sans-serif;max-width:860px;margin:0 auto;padding:42px 20px;line-height:1.6;color:#111827}}h1{{line-height:1.1}}img{{max-width:100%;height:auto}}</style></head>
<body><p><a href="/sites/{site_id}#distribution">Back to dashboard</a></p><h1>{escape(job['title'] or job['topic'] or 'Draft')}</h1>{job['draft_html']}</body></html>
"""
    return Response(html, mimetype="text/html")


@app.post("/api/sites/<int:site_id>/content-jobs/<job_id>/generate")
def generate_content_job_route(site_id, job_id):
    try:
        return jsonify(generate_content_job(site_id, job_id))
    except KeyError:
        return jsonify({"error": "job not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/content-jobs/<job_id>/publish")
def publish_content_job_route(site_id, job_id):
    try:
        return jsonify(publish_content_job(site_id, job_id))
    except KeyError:
        return jsonify({"error": "job not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/content-jobs/<job_id>/social-drafts")
def generate_social_drafts_route(site_id, job_id):
    payload = request.get_json(silent=True) or {}
    channels = payload.get("channels")
    if channels is not None and not isinstance(channels, list):
        return jsonify({"error": "channels must be a list"}), 400
    try:
        return jsonify(generate_social_drafts(site_id, job_id, channels=channels))
    except KeyError:
        return jsonify({"error": "job not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/content-jobs/<job_id>/social-publish/zernio")
def publish_zernio_social_drafts_route(site_id, job_id):
    payload = request.get_json(silent=True) or {}
    scheduled_for = str(payload.get("scheduledFor") or "").strip() or None
    try:
        result = publish_zernio_social_drafts(site_id, job_id, scheduled_for=scheduled_for)
        return jsonify(result), (200 if result.get("ok") else 400)
    except KeyError:
        return jsonify({"error": "job not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/sites/<int:site_id>/social-assets/<job_id>/<channel>/<filename>")
def serve_social_asset(site_id, job_id, channel, filename):
    if channel not in SOCIAL_CHANNEL_LIMITS:
        abort(404)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", filename or ""):
        abort(404)
    directory = social_asset_job_dir(site_id, job_id, channel)
    if not (directory / filename).is_file():
        abort(404)
    return send_from_directory(directory, filename)


@app.get("/sites/<int:site_id>/article-assets/<job_id>/<filename>")
def serve_article_asset(site_id, job_id, filename):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", filename or ""):
        abort(404)
    directory = article_asset_job_dir(site_id, job_id)
    if not (directory / filename).is_file():
        abort(404)
    return send_from_directory(directory, filename)


@app.get("/sites/<int:site_id>/podcasts/<episode_id>/audio/<filename>")
def serve_podcast_audio(site_id, episode_id, filename):
    if filename != "episode.wav" or not re.fullmatch(r"[A-Za-z0-9_.-]+", episode_id or ""):
        abort(404)
    directory = podcast_asset_dir(site_id, episode_id)
    if not (directory / filename).is_file():
        abort(404)
    return send_from_directory(directory, filename, mimetype="audio/wav", as_attachment=False)


@app.get("/podcasts/<int:site_id>/<episode_id>")
def public_podcast_episode(site_id, episode_id):
    with db() as conn:
        episode = conn.execute(
            """select pe.*, s.brand_name, s.domain from podcast_episodes pe join sites s on s.id=pe.site_id
               where pe.site_id=? and pe.id=? and pe.status='PUBLISHED'""",
            (site_id, episode_id),
        ).fetchone()
    if not episode:
        abort(404)
    audio = podcast_audio_url(site_id, episode_id, episode["audio_filename"])
    html = f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{escape(episode['title'])}</title><meta name=\"description\" content=\"{escape(episode['description'] or '', quote=True)}\"><style>body{{margin:0;background:#0b1020;color:#f8fafc;font:17px/1.6 Inter,system-ui,sans-serif}}main{{max-width:760px;margin:auto;padding:52px 20px}}a{{color:#a7f3d0}}.eyebrow{{color:#a7f3d0;font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:.08em}}h1{{font-size:clamp(34px,7vw,64px);line-height:1;letter-spacing:-.04em}}p{{color:#cbd5e1}}audio{{width:100%;margin:24px 0}}.note{{margin-top:32px;padding-top:18px;border-top:1px solid #334155;font-size:13px}}</style></head><body><main><div class=\"eyebrow\">{escape(episode['brand_name'] or episode['domain'])} podcast</div><h1>{escape(episode['title'])}</h1><p>{escape(episode['description'] or '')}</p><audio controls preload=\"metadata\" src=\"{escape(audio, quote=True)}\"></audio><p class=\"note\">Generated episode. <a href=\"{escape(podcast_rss_url(site_id), quote=True)}\">Podcast RSS feed</a></p></main></body></html>"""
    return Response(html, mimetype="text/html")


@app.get("/podcasts/<int:site_id>/feed.xml")
def public_podcast_feed(site_id):
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        episodes = conn.execute("select * from podcast_episodes where site_id=? and status='PUBLISHED' order by published_at desc", (site_id,)).fetchall()
    if not site:
        abort(404)
    channel_title = (site["brand_name"] or site["domain"]) + " Podcast"
    items = []
    for episode in episodes:
        audio = urllib.parse.urljoin(BLOG_CORE_PUBLIC_URL + "/", podcast_audio_url(site_id, episode["id"], episode["audio_filename"]).lstrip("/"))
        page = episode["published_url"] or podcast_public_url(site_id, episode["id"])
        items.append(f"<item><title>{escape(episode['title'])}</title><description>{escape(episode['description'] or '')}</description><guid>{escape(page)}</guid><link>{escape(page)}</link><pubDate>{escape(episode['published_at'] or episode['updated_at'])}</pubDate><enclosure url=\"{escape(audio, quote=True)}\" type=\"audio/wav\" length=\"0\"/></item>")
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><rss version=\"2.0\"><channel><title>{escape(channel_title)}</title><link>{escape(BLOG_CORE_PUBLIC_URL)}</link><description>{escape(channel_title)}</description>{''.join(items)}</channel></rss>"
    return Response(xml, mimetype="application/rss+xml")


@app.get("/sites/<int:site_id>/social-posts/<int:post_id>")
def social_post_review(site_id, post_id):
    with db() as conn:
        post = conn.execute(
            """select sp.*, cj.title, cj.topic, s.domain, s.brand_name
               from social_posts sp join content_jobs cj on cj.id=sp.job_id and cj.site_id=sp.site_id
               join sites s on s.id=sp.site_id where sp.site_id=? and sp.id=?""",
            (site_id, post_id),
        ).fetchone()
    if not post:
        abort(404)
    payload = parse_json_object(post["content_json"])
    pin = payload.get("pin") if isinstance(payload.get("pin"), dict) else {}
    reddit = payload.get("reddit") if isinstance(payload.get("reddit"), dict) else {}
    image_url = pin.get("imageUrl") or ""
    media = f'<img src="{escape(image_url, quote=True)}" alt="{escape(pin.get("altText") or "Pinterest draft", quote=True)}">' if image_url else ""
    title = reddit.get("title") or pin.get("pinTitle") or post["title"] or post["topic"] or "Social draft"
    details = ""
    if pin:
        details = f"<dl><dt>Overlay</dt><dd>{escape(pin.get('overlayText') or '')}</dd><dt>Destination</dt><dd>{escape(pin.get('destinationUrl') or 'none')}</dd></dl>"
    if reddit:
        details = f"<dl><dt>Reddit title</dt><dd>{escape(reddit.get('title') or '')}</dd><dt>Format</dt><dd>{escape(reddit.get('format') or 'discussion')}</dd></dl>"
    validation = parse_json_object(post["validation_json"])
    html = f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"robots\" content=\"noindex,nofollow\"><title>{escape(post['channel'])} social review</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#0b1020;color:#f8fafc;font:16px/1.55 Inter,system-ui,sans-serif}}main{{max-width:760px;margin:auto;padding:32px 18px 70px}}a{{color:#c4b5fd}}article{{margin-top:18px;padding:22px;border:1px solid #334155;border-radius:16px;background:#111827}}h1{{line-height:1.1}}pre{{white-space:pre-wrap;font:inherit;margin:0}}img{{width:min(100%,460px);display:block;margin:18px auto;border-radius:12px}}dl{{display:grid;grid-template-columns:120px 1fr;gap:8px;margin:18px 0 0}}dt{{color:#94a3b8}}dd{{margin:0}}</style></head><body><main><a href=\"/sites/{int(site_id)}#content\">Back to dashboard</a><h1>{escape(str(post['channel']).title())} review</h1><p>{escape(post['brand_name'] or post['domain'])} · {escape(post['language'] or '')} · {escape(post['status'])}</p><article><h2>{escape(title)}</h2>{media}<pre>{escape(post['content_text'] or '')}</pre>{details}<p>Validation: {escape(json.dumps(validation, ensure_ascii=False))}</p></article></main></body></html>"""
    return Response(html, mimetype="text/html")


@app.get("/sites/<int:site_id>/social-posts/<int:post_id>/instagram-carousel")
def instagram_carousel_preview(site_id, post_id):
    with db() as conn:
        post = conn.execute(
            """
            select sp.*, cj.title, cj.topic, cj.description, s.domain, s.brand_name
            from social_posts sp
            join content_jobs cj on cj.id=sp.job_id and cj.site_id=sp.site_id
            join sites s on s.id=sp.site_id
            where sp.site_id=? and sp.id=? and sp.channel='instagram'
            """,
            (site_id, post_id),
        ).fetchone()
    if not post:
        abort(404)
    payload = parse_json_object(post["content_json"])
    carousel = payload.get("instagramCarousel") if isinstance(payload.get("instagramCarousel"), dict) else {}
    slides = carousel.get("slides") if isinstance(carousel.get("slides"), list) else []
    if not slides:
        abort(404)
    caption = post["content_text"] or carousel.get("caption") or ""
    slide_html = []
    for slide in slides:
        image_url = slide.get("imageUrl") or ""
        slide_html.append(
            f"""
            <article class="slide">
              <img src="{escape(image_url, quote=True)}" alt="{escape(slide.get('altText') or '', quote=True)}">
              <div class="slide-meta">Slide {escape(str(slide.get('index') or ''))} · overlay text is baked into the image</div>
            </article>
            """
        )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Instagram carousel · {escape(post['title'] or post['topic'] or post['domain'])}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#0b1020;color:#f8fafc;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.shell{{max-width:1180px;margin:0 auto;padding:34px 18px 70px}}a{{color:#c4b5fd}}.top{{display:flex;justify-content:space-between;gap:14px;align-items:flex-start;margin-bottom:22px}}h1{{font-size:clamp(28px,5vw,54px);line-height:1;margin:8px 0 10px;letter-spacing:-.04em}}.muted{{color:#a6b0c3;line-height:1.5}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px;margin-top:22px}}.slide{{border:1px solid rgba(255,255,255,.14);border-radius:18px;background:rgba(255,255,255,.06);overflow:hidden}}.slide img{{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;background:#111827}}.slide-meta{{padding:10px 12px;color:#a6b0c3;font-size:12px;line-height:1.35}}.caption-wrap{{margin-top:24px}}.caption-wrap h2{{font-size:18px;margin:0 0 10px}}.caption{{white-space:pre-wrap;border:1px solid rgba(255,255,255,.14);border-radius:18px;background:rgba(255,255,255,.06);padding:18px;line-height:1.5}}@media(max-width:720px){{.top{{display:block}}}}
</style>
</head>
<body>
<main class="shell">
  <div class="top"><div><a href="/sites/{int(site_id)}#distribution">Back to dashboard</a><h1>{escape(post['title'] or post['topic'] or 'Instagram carousel')}</h1><div class="muted">{escape(post['brand_name'] or post['domain'])} · {escape(post['language'] or '')} · {len(slides)} real JPEG slides</div></div></div>
  <section class="grid">{''.join(slide_html)}</section>
  <section class="caption-wrap"><h2>Single Instagram carousel caption</h2><div class="caption">{escape(caption)}</div></section>
</main>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@app.get("/sites/<int:site_id>/social-posts/<int:post_id>/threads")
def threads_post_preview(site_id, post_id):
    with db() as conn:
        post = conn.execute(
            """
            select sp.*, cj.title, cj.topic, s.domain, s.brand_name
            from social_posts sp
            join content_jobs cj on cj.id=sp.job_id and cj.site_id=sp.site_id
            join sites s on s.id=sp.site_id
            where sp.site_id=? and sp.id=? and sp.channel='threads'
            """,
            (site_id, post_id),
        ).fetchone()
    if not post:
        abort(404)
    payload = parse_json_object(post["content_json"])
    threads = payload.get("threads") if isinstance(payload.get("threads"), dict) else {}
    media_urls = threads.get("mediaUrls") if isinstance(threads.get("mediaUrls"), list) else []
    media_html = "".join(f'<img src="{escape(url, quote=True)}" alt="Threads media preview">' for url in media_urls[:1])
    validation = parse_json_object(post["validation_json"])
    byte_count = validation.get("byteCount") or post["char_count"] or 0
    max_bytes = validation.get("maxBytes") or post["max_chars"] or 500
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Threads draft · {escape(post['title'] or post['topic'] or post['domain'])}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#101010;color:#f5f5f5;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.shell{{max-width:760px;margin:0 auto;padding:34px 18px 70px}}a{{color:#ddd}}.post{{border:1px solid rgba(255,255,255,.14);border-radius:22px;background:#181818;padding:18px;margin-top:20px}}.brand{{color:#a3a3a3;font-size:13px;margin-bottom:12px}}.text{{white-space:pre-wrap;font-size:20px;line-height:1.35}}img{{display:block;width:100%;border-radius:18px;margin-top:16px;background:#222}}.meta{{color:#a3a3a3;font-size:13px;margin-top:12px}}h1{{letter-spacing:-.04em;line-height:1;margin:10px 0}}
</style>
</head>
<body>
<main class="shell">
  <a href="/sites/{int(site_id)}#content">Back to dashboard</a>
  <h1>Threads draft</h1>
  <div class="post">
    <div class="brand">{escape(post['brand_name'] or post['domain'])} · {escape(post['language'] or '')}</div>
    <div class="text">{escape(post['content_text'] or '')}</div>
    {media_html}
    <div class="meta">{int(byte_count)} / {int(max_bytes)} UTF-8 bytes · {len(media_urls[:1])} image</div>
  </div>
</main>
</body>
</html>"""
    return Response(html, mimetype="text/html")


def planned_groups_for_site(site_id):
    site = get_site(site_id)
    if not site:
        return None, []
    groups = group_planned_rows(get_planned_content_jobs(site_id, limit=1000), parse_languages(site["languages"]))
    return site, groups


@app.post("/api/sites/<int:site_id>/planned-groups/bulk")
def bulk_planned_groups_route(site_id):
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action") or "").strip().lower()
    group_ids = payload.get("groupIds") or []
    if action not in {"generate", "delete"}:
        return jsonify({"error": "unsupported action"}), 400
    if not isinstance(group_ids, list) or not group_ids:
        return jsonify({"error": "select at least one planned task"}), 400
    group_ids = [str(group_id) for group_id in group_ids if str(group_id or "").strip()]
    site, groups = planned_groups_for_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    groups_by_id = {group["id"]: group for group in groups}
    selected = [groups_by_id[group_id] for group_id in group_ids if group_id in groups_by_id]
    if not selected:
        return jsonify({"error": "no selected planned tasks found"}), 404
    if action == "generate":
        results = []
        for group in selected:
            job_id = group["primary"]["id"]
            try:
                results.append(generate_content_job(site_id, job_id))
            except Exception as e:
                results.append({"ok": False, "jobId": job_id, "error": str(e)})
        failed = [item for item in results if not item.get("ok")]
        return jsonify({"ok": not failed, "action": action, "groups": len(selected), "results": results}), (207 if failed else 200)
    deleted_jobs = []
    now = now_iso()
    with db() as conn:
        for group in selected:
            job_ids = [row["id"] for row in group["rows"]]
            for job_id in job_ids:
                conn.execute("delete from social_posts where site_id=? and job_id=?", (site_id, job_id))
                conn.execute("delete from content_job_logs where site_id=? and job_id=?", (site_id, job_id))
                conn.execute("delete from content_jobs where site_id=? and id=?", (site_id, job_id))
            deleted_jobs.extend(job_ids)
        conn.execute(
            "insert into publish_jobs(site_id, kind, status, message, created_at) values(?,?,?,?,?)",
            (
                site_id,
                "planned-groups-bulk-delete",
                "completed",
                json.dumps({"groups": len(selected), "deletedJobIds": deleted_jobs}, ensure_ascii=False),
                now,
            ),
        )
    return jsonify({"ok": True, "action": action, "groups": len(selected), "deletedJobs": len(deleted_jobs)})



@app.post("/api/sites/<int:site_id>/import-blog/scan")
def scan_existing_blog_route(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    try:
        result = discover_existing_blog_articles(site)
        return jsonify({"ok": True, **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/import-blog/import")
def import_existing_blog_route(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    urls = payload.get("urls") or []
    if not isinstance(urls, list) or not urls:
        return jsonify({"error": "urls list is required"}), 400
    try:
        result = import_existing_articles(site_id, urls)
        with db() as conn:
            conn.execute(
                "insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)",
                (site_id, "import-existing-blog", "completed", json.dumps(result, ensure_ascii=False), now_iso()),
            )
        return jsonify({"ok": True, **result})
    except KeyError:
        return jsonify({"error": "site not found"}), 404
    except Exception as e:
        with db() as conn:
            conn.execute(
                "insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)",
                (site_id, "import-existing-blog", "failed", str(e), now_iso()),
            )
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/check-cname")
def check_site_cname(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    result = check_cname_status(site["custom_blog_domain"])
    with db() as conn:
        conn.execute(
            "update sites set cname_status=?, cname_checked_at=?, updated_at=? where id=?",
            (result["status"], now_iso(), now_iso(), site_id),
        )
    return jsonify({"ok": True, **result})


@app.post("/api/sites")
def create_site():
    payload = request.get_json(silent=True) or request.form.to_dict()
    homepage = normalize_url(payload.get("homepage_url") or payload.get("domain"))
    if not homepage:
        return jsonify({"error": "homepage_url is required"}), 400
    domain = (payload.get("domain") or domain_from_url(homepage)).strip().lower()
    brand = payload.get("brand_name") or domain.split(".")[0].replace("-", " ").title()
    root_path = payload.get("root_path") or ""
    now = now_iso()
    with db() as conn:
        conn.execute(
            """
            insert into sites(domain, homepage_url, access_type, root_path, brand_name, content_context, custom_blog_domain, hosted_blog_enabled, created_at, updated_at)
            values(?,?,?,?,?,?,?,?,?,?)
            on conflict(domain) do update set
                homepage_url=excluded.homepage_url, root_path=excluded.root_path, brand_name=excluded.brand_name,
                content_context=excluded.content_context, custom_blog_domain=excluded.custom_blog_domain,
                hosted_blog_enabled=excluded.hosted_blog_enabled, updated_at=excluded.updated_at
            """,
            (
                domain,
                homepage,
                payload.get("access_type") or "local_path",
                root_path,
                brand,
                payload.get("content_context") or "",
                clean_host(payload.get("custom_blog_domain")),
                form_bool(payload.get("hosted_blog_enabled")),
                now,
                now,
            ),
        )
    return redirect("/") if request.form else jsonify({"ok": True})


def source_scanner_request_authorized():
    configured = os.environ.get("SOURCE_SCANNER_HANDOFF_TOKEN", "")
    supplied = request.headers.get("X-Source-Scanner-Token", "")
    return bool(configured and supplied and secrets.compare_digest(configured, supplied))


def source_scanner_unique_slug(conn, site_id, title, scanner_article_id, current_job_id=None):
    base = simple_slug(title)
    candidate = base
    suffix = scanner_article_id[:8]
    attempt = 0
    while True:
        row = conn.execute("select id from content_jobs where site_id=? and slug=?", (site_id, candidate)).fetchone()
        if not row or row["id"] == current_job_id:
            return candidate
        attempt += 1
        candidate = f"{base[:max(1, 90 - len(suffix) - len(str(attempt)) - 2)]}-{suffix}-{attempt}"


@app.post("/api/integrations/source-scanner/sites/<int:site_id>/drafts")
def receive_source_scanner_draft(site_id):
    """Receive a finished project Studio article as a reviewable Blog Core draft, never as a publication."""
    if not source_scanner_request_authorized():
        return jsonify({"error": "unauthorized source scanner handoff"}), 401
    payload = request.get_json(silent=True) or {}
    scanner_article_id = str(payload.get("scannerArticleId") or "").strip()
    title = re.sub(r"\s+", " ", str(payload.get("title") or "")).strip()
    content_html = str(payload.get("contentHtml") or "").strip()
    if not re.fullmatch(r"[a-f0-9]{24}", scanner_article_id):
        return jsonify({"error": "scannerArticleId is invalid"}), 400
    if not title or len(title) > 220:
        return jsonify({"error": "title is required and must be at most 220 characters"}), 400
    if len(content_html) < 300 or len(content_html) > 500000:
        return jsonify({"error": "contentHtml must be a complete article"}), 400
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        if not site:
            return jsonify({"error": "site not found"}), 404
        mapping = conn.execute("select * from source_scanner_drafts where scanner_article_id=?", (scanner_article_id,)).fetchone()
        now = now_iso()
        faq = payload.get("faq") if isinstance(payload.get("faq"), list) else []
        faq = faq[:12]
        sources = {
            "origin": "source_scanner_studio",
            "scannerArticleId": scanner_article_id,
            "scannerProjectId": str(payload.get("scannerProjectId") or "")[:80],
            "scannerBriefId": str(payload.get("scannerBriefId") or "")[:80],
            "sourceUrl": str(payload.get("sourceUrl") or "")[:2000],
            "sourceName": str(payload.get("sourceName") or "")[:240],
            "sourceNotes": str(payload.get("sourceNotes") or "")[:4000],
            "language": str(payload.get("language") or "en")[:12],
            "contentType": "blog",
            "pageType": "blog",
        }
        if str(site["domain"] or "").lower().strip("/") == "yas.ooo":
            sources.update({"publicationMode": "native_next_content_store", "nativeProjectRoot": site["root_path"] or ""})
        created = mapping is None
        if mapping:
            if int(mapping["site_id"]) != site_id:
                return jsonify({"error": "scanner article belongs to another Blog Core site"}), 409
            job = conn.execute("select * from content_jobs where id=? and site_id=?", (mapping["job_id"], site_id)).fetchone()
            if not job:
                return jsonify({"error": "existing scanner task is missing"}), 409
            if job["status"] == "PUBLISHED":
                return jsonify({"error": "This scanner draft is already published. Create a new editorial draft before replacing live content."}), 409
            job_id = job["id"]
            slug = source_scanner_unique_slug(conn, site_id, title, scanner_article_id, current_job_id=job_id)
            sources.update({"targetPath": f"/blog/{slug}/", "canonicalGroup": f"/blog/{slug}/"})
            conn.execute(
                """update content_jobs set topic=?,slug=?,status='DRAFT',title=?,description=?,category=?,hero_image=?,draft_html=?,faq_json=?,sources_json=?,error=null,updated_at=? where id=? and site_id=?""",
                (title, slug, title, str(payload.get("subtitle") or "")[:360], "YAS Editorial Studio", str(payload.get("heroImage") or "")[:2000], content_html, json.dumps(faq, ensure_ascii=False), json.dumps(sources, ensure_ascii=False), now, job_id, site_id),
            )
            conn.execute("update source_scanner_drafts set updated_at=? where scanner_article_id=?", (now, scanner_article_id))
            log_message = "Updated draft from Source Scanner Studio"
        else:
            job_id = secrets.token_hex(12)
            slug = source_scanner_unique_slug(conn, site_id, title, scanner_article_id)
            sources.update({"targetPath": f"/blog/{slug}/", "canonicalGroup": f"/blog/{slug}/"})
            conn.execute(
                """insert into content_jobs(id,site_id,topic,slug,status,title,description,category,hero_image,draft_html,faq_json,sources_json,visibility,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (job_id, site_id, title, slug, "DRAFT", title, str(payload.get("subtitle") or "")[:360], "YAS Editorial Studio", str(payload.get("heroImage") or "")[:2000], content_html, json.dumps(faq, ensure_ascii=False), json.dumps(sources, ensure_ascii=False), "public", now, now),
            )
            conn.execute("insert into source_scanner_drafts(scanner_article_id,site_id,job_id,received_at,updated_at) values(?,?,?,?,?)", (scanner_article_id, site_id, job_id, now, now))
            log_message = "Received finished draft from Source Scanner Studio"
        conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (site_id, job_id, now, "INFO", "source-scanner", log_message))
        job = conn.execute("select * from content_jobs where id=?", (job_id,)).fetchone()
    if str(site["domain"] or "").lower().strip("/") == "yas.ooo":
        try:
            write_native_content_store(site, job, "drafts")
        except Exception as error:
            return jsonify({"error": f"Draft was queued but native preview could not be prepared: {error}", "job": {"id": job_id}}), 502
    return jsonify({"ok": True, "created": created, "updated": not created, "job": {"id": job_id, "siteId": site_id, "status": "DRAFT", "slug": slug}})


@app.get("/api/sites")
def list_sites():
    with db() as conn:
        rows = [dict(r) for r in conn.execute("select * from sites order by updated_at desc").fetchall()]
    return jsonify(rows)


@app.post("/api/sites/<int:site_id>/scan")
def scan_site(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    try:
        theme = extract_theme(site["homepage_url"])
        with db() as conn:
            conn.execute(
                "insert into site_theme_profiles(site_id,title,description,colors_json,fonts_json,css_urls_json,head_css,header_html,footer_html,body_class,scanned_at) values(?,?,?,?,?,?,?,?,?,?,?) on conflict(site_id) do update set title=excluded.title, description=excluded.description, colors_json=excluded.colors_json, fonts_json=excluded.fonts_json, css_urls_json=excluded.css_urls_json, head_css=excluded.head_css, header_html=excluded.header_html, footer_html=excluded.footer_html, body_class=excluded.body_class, scanned_at=excluded.scanned_at",
                (site_id, theme["title"], theme["description"], json.dumps(theme["colors"]), json.dumps(theme["fonts"]), json.dumps(theme["css_urls"]), theme["head_css"], theme["header_html"], theme["footer_html"], theme["body_class"], now_iso()),
            )
        topic_profile = apply_site_topic_profile(site_id, infer_site_topic_profile(site, theme), overwrite=False)
        return jsonify({"ok": True, "theme": theme, "topicProfile": topic_profile})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/sites/<int:site_id>/bootstrap-preview")
def bootstrap_preview(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    profile = get_profile(site_id)
    if not profile:
        return jsonify({"error": "scan the site first"}), 400
    path = build_preview(site, profile)
    return jsonify({"ok": True, "preview_path": path})


@app.post("/api/sites/<int:site_id>/install-blog")
def install(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    profile = get_profile(site_id)
    if not profile:
        return jsonify({"error": "scan the site first"}), 400
    try:
        result = install_blog(site, profile)
        with db() as conn:
            conn.execute("insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)", (site_id, "install-blog", "completed", json.dumps(result), now_iso()))
        return jsonify({"ok": True, **result})
    except Exception as e:
        with db() as conn:
            conn.execute("insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)", (site_id, "install-blog", "failed", str(e), now_iso()))
        return jsonify({"error": str(e)}), 500


@app.get("/api/sites/<int:site_id>/theme")
def site_theme(site_id):
    profile = get_profile(site_id)
    if not profile:
        return jsonify({"error": "theme not found"}), 404
    return jsonify(dict(profile))


@app.get("/<path:public_path>")
def public_host_route(public_path):
    host = request_host()
    if is_admin_host(host):
        abort(404)
    site = get_site_by_custom_host(host)
    if not site:
        abort(404)
    return render_hosted_blog_response(site, public_path)


MANAGE_SITE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manage __DOMAIN__ · Blog Core</title>
<style>
:root{--bg:#0b1020;--panel:rgba(255,255,255,.08);--line:rgba(255,255,255,.15);--text:#f8fafc;--muted:#a6b0c3;--accent:#8b5cf6;--accent2:#22c55e;--danger:#ef4444}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 0,#3b1a75 0,transparent 38%),radial-gradient(circle at 78% 15%,#0d7a65 0,transparent 28%),#0b1020;color:var(--text);min-height:100vh}a{color:inherit}.shell{max-width:1180px;margin:0 auto;padding:38px 22px 90px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}.top-actions{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;justify-content:flex-end}.site-switcher{display:flex;flex-direction:column;gap:6px;min-width:260px}.site-switcher span{font-size:12px;color:#d8cdfd;text-transform:uppercase;letter-spacing:.08em;font-weight:900}.site-switcher select{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.75);color:#fff;padding:13px 14px;font-size:14px;outline:none}.back{color:#d8cdfd;text-decoration:none;font-weight:900}.title{font-size:clamp(36px,5vw,64px);letter-spacing:-.05em;line-height:.95;margin:14px 0 8px}.sub,.muted{color:var(--muted);font-size:14px;line-height:1.5}.grid{display:grid;grid-template-columns:1fr;gap:18px}.settings-head{display:flex;justify-content:space-between;gap:16px;align-items:center}.settings-toggle{width:48px;height:48px;border-radius:999px;font-size:22px;padding:0}.settings-panel[hidden]{display:none}.compact-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:18px}.signal-toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 18px}.signal-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.signal-card{display:grid;grid-template-columns:auto 1fr;gap:10px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.45);padding:14px}.signal-card input{width:18px;height:18px;margin-top:2px}.import-list{display:grid;gap:10px;margin-top:14px}.import-row{display:grid;grid-template-columns:auto 1fr;gap:10px;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.38);padding:12px}.import-row input{width:18px;height:18px;margin-top:2px}.import-row strong{display:block;font-size:14px}.import-row span{display:block;color:var(--muted);font-size:12px;margin-top:4px;word-break:break-all}.signal-card strong{display:block;font-size:15px;line-height:1.25}.signal-card span{display:block;color:var(--muted);font-size:12px;margin-top:5px}.source-pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:4px 8px;margin-bottom:7px;color:#d8cdfd;font-size:11px;font-weight:900;text-transform:uppercase}.loading{color:var(--muted);padding:18px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.38)}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.11),rgba(255,255,255,.06));box-shadow:0 22px 90px rgba(0,0,0,.32);backdrop-filter:blur(22px);border-radius:24px;padding:22px;margin:18px 0}.panel h2{margin:0 0 14px;font-size:22px;letter-spacing:-.03em}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.field.full{grid-column:1 / -1}.field label{display:block;font-size:12px;color:#d8cdfd;text-transform:uppercase;letter-spacing:.08em;font-weight:900;margin:0 0 7px}.field input,.field textarea,.field select{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.55);color:#fff;padding:13px 14px;font-size:14px;outline:none}.field textarea{min-height:108px;resize:vertical}.hint{color:var(--muted);font-size:12px;margin-top:6px}.field input:focus,.field textarea:focus,.field select:focus{border-color:rgba(139,92,246,.9);box-shadow:0 0 0 4px rgba(139,92,246,.18)}.check{display:flex;align-items:center;gap:10px;padding:12px 0;color:#fff;font-weight:800}.check input{width:18px;height:18px}.actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.btn,button{border:0;border-radius:14px;background:linear-gradient(135deg,#8b5cf6,#22c55e);color:#fff;font-weight:900;padding:13px 16px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;min-height:42px}.btn.ghost,button.ghost{background:rgba(255,255,255,.08);border:1px solid var(--line)}.danger{background:rgba(239,68,68,.16);border:1px solid rgba(239,68,68,.45);color:#fecaca}.stat{border:1px solid var(--line);border-radius:18px;background:rgba(8,13,29,.48);padding:16px;margin-top:12px}.stat strong{display:block;font-size:15px;margin-bottom:6px}.swatches{display:flex;gap:7px;flex-wrap:wrap}.swatch{display:inline-block;width:28px;height:28px;border-radius:999px;border:1px solid rgba(255,255,255,.35)}.job-row{display:grid;grid-template-columns:1fr auto;gap:8px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.45);padding:14px;margin-top:10px}.job-row span{display:block;color:var(--muted);font-size:12px;margin-top:3px}.production-panel{border-color:rgba(139,92,246,.35)}.panel-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.channel-checks{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.check.compact{padding:10px 12px;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.38)}.channel-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.channel-card{border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.45);padding:12px}.channel-card strong{display:block}.channel-card span{display:block;color:var(--muted);font-size:12px;margin-top:4px}.social-statuses{grid-column:1 / -1;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.social-statuses span{border:1px solid var(--line);border-radius:999px;padding:6px 8px;background:rgba(255,255,255,.06)}.job-row p{grid-column:1 / -1;margin:0;color:var(--muted);font-size:13px;line-height:1.45;overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow-wrap:anywhere}.status{border-radius:999px;padding:6px 9px;background:rgba(255,255,255,.1);font-size:12px}.status.completed{background:rgba(34,197,94,.18);color:#bbf7d0}.status.failed{background:rgba(239,68,68,.18);color:#fecaca}.status.queued{background:rgba(139,92,246,.18);color:#ddd6fe}.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111827;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:16px;padding:14px 18px;box-shadow:0 20px 80px rgba(0,0,0,.4);display:none;max-width:min(720px,calc(100vw - 32px));z-index:10}.toast.show{display:block}@media(max-width:900px){.top,.grid,.compact-grid{display:block}.channel-checks,.channel-grid,.social-statuses{grid-template-columns:1fr}.top-actions{justify-content:flex-start;margin-top:18px}.site-switcher{min-width:0;width:100%}.form-grid,.signal-list{grid-template-columns:1fr}.shell{padding:28px 16px 70px}}
</style>
<style>
.idea-stage{margin-top:18px}
.idea-stage h3{margin:0 0 6px;font-size:18px}
.discovery-control{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:16px 0 0;flex-wrap:wrap}
.analysis-state{display:flex;align-items:center;gap:10px;color:var(--muted);font-size:13px;line-height:1.45}
.analysis-dot{width:18px;height:18px;border-radius:999px;border:2px solid rgba(255,255,255,.18);border-top-color:#8b5cf6;display:inline-block;animation:spin .85s linear infinite}
.analysis-state.ready .analysis-dot{animation:none;border-color:rgba(34,197,94,.7);background:rgba(34,197,94,.28)}
.analysis-state.failed .analysis-dot{animation:none;border-color:rgba(239,68,68,.75);background:rgba(239,68,68,.18)}
.signal-summary{margin-top:12px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.32);padding:14px;color:var(--muted);font-size:13px;line-height:1.5}
.signal-summary[hidden]{display:none}
.idea-progress{border:1px solid rgba(139,92,246,.38);border-radius:18px;background:rgba(8,13,29,.48);padding:18px;margin-top:18px}
.idea-progress-head{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:12px}
.idea-progress-title{display:flex;align-items:center;gap:10px;font-weight:900;color:#fff}
.idea-progress-time{color:#d8cdfd;font-size:12px;font-weight:900}
.idea-progress-bar{height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;border:1px solid rgba(255,255,255,.08)}
.idea-progress-fill{height:100%;width:0%;border-radius:999px;background:linear-gradient(90deg,#8b5cf6,#22c55e);transition:width .55s ease}
.idea-progress-step{margin-top:10px;color:var(--muted);font-size:13px;line-height:1.45}
@keyframes spin{to{transform:rotate(360deg)}}
.idea-list{display:grid;gap:10px;margin-top:14px}
.idea-row{display:grid;grid-template-columns:auto 1fr;gap:10px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.48);padding:14px}
.idea-row input{width:18px;height:18px;margin-top:2px}
.idea-row strong{display:block;font-size:15px;line-height:1.25}
.idea-row span{display:block;color:var(--muted);font-size:12px;line-height:1.4;margin-top:5px}
.idea-row em{display:block;color:#d8cdfd;font-size:11px;font-style:normal;margin-top:7px}
.content-toolbar{display:flex;justify-content:space-between;gap:12px;align-items:center;margin:14px 0 8px;flex-wrap:wrap}
.language-switcher,.type-switcher{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.type-switcher{justify-content:flex-end}
.lang-chip,.type-chip{min-width:42px;min-height:32px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.06);display:inline-flex;align-items:center;justify-content:center;text-decoration:none;color:#d8cdfd;font-size:12px;font-weight:900;padding:0 11px;white-space:nowrap}
.type-chip{min-width:auto}
.lang-chip.active,.type-chip.active{background:rgba(139,92,246,.7);border-color:transparent;color:#fff}
.content-pagination{display:flex;justify-content:center;gap:8px;align-items:center;margin:18px 0 0}
.content-pagination strong{display:block;font-size:16px;color:#fff;margin-bottom:3px}
.content-pagination span{display:block;color:var(--muted);font-size:13px;line-height:1.4}
.pagination-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.page-link{min-width:34px;min-height:34px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.07);display:inline-flex;align-items:center;justify-content:center;text-decoration:none;font-weight:900;color:#d8cdfd;padding:0 10px}
.page-link.active{background:rgba(139,92,246,.7);color:#fff;border-color:transparent}
.page-link.nav{font-size:18px;padding-bottom:2px}
.production-job .social-statuses{grid-column:1 / -1;display:flex;gap:8px;align-items:center;margin-top:2px}
.production-job .social-icon{width:30px;height:30px;border-radius:999px;border:1px solid rgba(255,255,255,.18);display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,.08);color:#fff;font-size:11px;font-weight:900;line-height:1;text-transform:uppercase}
.production-job .social-icon.muted{opacity:.32;filter:grayscale(1);background:rgba(255,255,255,.04)}
.production-job .social-icon.queued{opacity:.72;border-color:rgba(139,92,246,.45);background:rgba(139,92,246,.14)}
.production-job .social-icon.published{opacity:1;border-color:rgba(34,197,94,.75);background:rgba(34,197,94,.18)}
.production-job .social-icon.failed{opacity:1;border-color:rgba(239,68,68,.75);background:rgba(239,68,68,.18)}
.production-job .social-icon.linkedin{text-transform:none;font-size:13px}
.production-job .social-icon.twitter{font-size:13px}
.production-job .social-icon.pinterest{font-size:13px}
.production-job .social-icon.telegram,.production-job .social-icon.tumblr{text-transform:lowercase}
.production-job .icon-btn{width:34px;height:34px;border-radius:12px;border:1px solid var(--line);background:rgba(255,255,255,.08);display:inline-flex;align-items:center;justify-content:center;text-decoration:none;color:#fff;font-weight:900;font-size:17px}
.production-job .icon-btn:hover{border-color:rgba(34,197,94,.75);background:rgba(34,197,94,.16);transform:translateY(-1px)}
.production-job .content-type-badge,.planned-row .content-type-badge{display:inline-flex;align-items:center;min-height:28px;border-radius:999px;padding:5px 9px;border:1px solid var(--line);background:rgba(255,255,255,.07);color:#d8cdfd;font-size:11px;font-weight:900;text-transform:uppercase;white-space:nowrap}
.production-job .content-type-badge.blog,.planned-row .content-type-badge.blog{border-color:rgba(96,165,250,.45);background:rgba(96,165,250,.13);color:#bfdbfe}
.production-job .content-type-badge.seo,.planned-row .content-type-badge.seo{border-color:rgba(245,158,11,.5);background:rgba(245,158,11,.14);color:#fde68a}
.status.imported{background:rgba(34,197,94,.2);color:#bbf7d0;border:1px solid rgba(34,197,94,.38)}
.unified-channels{grid-template-columns:repeat(2,minmax(0,1fr))}
.unified-channel{display:grid;gap:10px}
.channel-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.channel-state{display:inline-flex;margin-top:5px;border-radius:999px;padding:4px 8px;font-size:11px;font-weight:900;text-transform:uppercase;border:1px solid var(--line);color:var(--muted)}
.channel-state.connected{border-color:rgba(34,197,94,.45);background:rgba(34,197,94,.14);color:#bbf7d0}
.channel-state.configured{border-color:rgba(245,158,11,.48);background:rgba(245,158,11,.13);color:#fde68a}
.channel-state.disconnected{opacity:.72}
.connect-placeholder{display:inline-flex;align-items:center;min-height:30px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--muted);font-size:11px;font-weight:900;text-transform:uppercase;padding:6px 9px;white-space:nowrap}
.social-credentials-panel{margin-top:18px}
.social-credentials-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
.social-credentials-card{display:grid;gap:12px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.38);padding:14px}
.social-credential-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.planned-publications-block{margin-top:18px;border-top:1px solid var(--line);padding-top:18px}
.planned-publications-block h3{margin:0 0 4px;color:#efe9ff;font-size:15px;text-transform:uppercase;letter-spacing:.08em}
.planned-bulkbar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.28);padding:10px 12px;margin-top:12px}
.planned-select-all,.planned-check{display:inline-flex;align-items:center;gap:8px;color:#d8cdfd;font-size:12px;font-weight:900}
.planned-select-all input,.planned-check input{width:16px;height:16px}
.danger-lite{border-color:rgba(239,68,68,.45)!important;color:#fecaca!important}
.bulk-progress{flex-basis:100%;border:1px solid rgba(139,92,246,.38);border-radius:12px;background:rgba(139,92,246,.14);color:#ddd6fe;padding:9px 11px;font-size:12px;font-weight:900}
button[disabled]{opacity:.55;cursor:not-allowed}
.planned-row{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.38);padding:12px;margin-top:10px}
.planned-row.generating,.production-job:has(.generation-progress){border-color:rgba(139,92,246,.55);box-shadow:0 0 0 1px rgba(139,92,246,.14),0 0 34px rgba(139,92,246,.1)}
.planned-row strong{display:block;font-size:14px}
.planned-row span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.planned-meta{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:8px}
.planned-row .planned-chip,.planned-row .planned-target{display:inline-flex;align-items:center;min-height:26px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.05);padding:4px 8px;color:#d8cdfd;font-size:11px;font-weight:800}
.planned-row .muted-chip{opacity:.7;filter:grayscale(.35)}
.planned-row .planned-target{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;text-transform:none;max-width:520px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.planned-error{margin-top:8px;color:#fecaca;font-size:12px;line-height:1.35;max-width:820px}
.mini-action{min-height:34px;padding:8px 11px;font-size:12px}
.status.generating{background:rgba(139,92,246,.22);color:#ddd6fe;border:1px solid rgba(139,92,246,.45);animation:statusPulse 1.25s ease-in-out infinite}
.generation-progress{grid-column:1 / -1;min-width:min(360px,80vw);border:1px solid rgba(139,92,246,.42);border-radius:14px;background:linear-gradient(180deg,rgba(139,92,246,.16),rgba(8,13,29,.58));padding:10px 12px;color:#ddd6fe}
.generation-progress-head{display:flex;align-items:center;gap:9px;font-size:12px;font-weight:900}
.generation-progress-title{color:#fff}
.generation-progress-time{margin-left:auto;color:#a7f3d0;font-size:11px}
.generation-spinner{width:14px;height:14px;border-radius:999px;border:2px solid rgba(216,205,253,.32);border-top-color:#a78bfa;animation:spin 1s linear infinite;flex:0 0 auto}
.generation-progress-bar{height:5px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;margin:9px 0 7px}
.generation-progress-bar span{display:block;width:42%;height:100%;border-radius:999px;background:linear-gradient(90deg,#8b5cf6,#22c55e,#60a5fa);animation:progressSweep 1.45s ease-in-out infinite}
.generation-progress-note{font-size:11px;line-height:1.35;color:var(--muted);max-width:540px}
.planned-row .actions .generation-progress,.production-job .actions .generation-progress{margin-top:6px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes progressSweep{0%{transform:translateX(-110%)}50%{transform:translateX(70%)}100%{transform:translateX(260%)}}
@keyframes statusPulse{0%,100%{box-shadow:0 0 0 rgba(139,92,246,0)}50%{box-shadow:0 0 18px rgba(139,92,246,.32)}}
.planned-empty{margin-top:10px;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.28);color:var(--muted);font-size:13px;padding:12px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px;border-bottom:1px solid var(--line);padding-bottom:10px}
.tab{background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:999px;color:#d8cdfd;min-height:38px;padding:9px 14px}
.tab.active{background:linear-gradient(135deg,rgba(139,92,246,.95),rgba(34,197,94,.78));color:#fff;border-color:transparent}
.tab-panel[hidden]{display:none}
.tab-panel{display:grid;gap:18px}
.tab-panel>.panel:first-child{margin-top:0}
.podcast-create{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:end;margin:20px 0 16px;padding-top:18px;border-top:1px solid var(--line)}.podcast-progress{grid-column:1 / -1;border:1px solid rgba(139,92,246,.42);border-radius:14px;background:rgba(139,92,246,.14);color:#ddd6fe;padding:10px 12px;font-size:13px;font-weight:800}.podcast-list{display:grid;gap:10px}.podcast-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;align-items:center;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.38);padding:12px}.podcast-row strong{display:block;font-size:14px}.podcast-row span{display:block;color:var(--muted);font-size:12px;margin-top:4px}.podcast-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}.podcast-actions audio{height:34px;max-width:260px}
@media(max-width:900px){.content-toolbar{justify-content:flex-start;align-items:flex-start}.type-switcher{justify-content:flex-start}.content-pagination{flex-wrap:wrap}.social-credentials-grid,.social-credential-fields,.podcast-create{grid-template-columns:1fr}.podcast-row{grid-template-columns:1fr}.podcast-actions{justify-content:flex-start}}
</style>
</head>
<body>
<main class="shell">
  <section class="top">
    <div>
      <a class="back" href="/">← All sites</a>
      <h1 class="title">__DOMAIN__</h1>
      <div class="sub">Manage the blog shell, design scan, install target, and article factory settings for this connected site.</div>
    </div>
    <div class="top-actions">__SITE_SWITCHER__<div class="actions">__PREVIEW__</div></div>
  </section>

  <nav class="tabs" role="tablist" aria-label="Site factory sections">
    <button class="tab active" type="button" role="tab" aria-selected="true" data-tab="content">Content</button>
    <button class="tab" type="button" role="tab" aria-selected="false" data-tab="discovery">Discovery</button>
    <button class="tab" type="button" role="tab" aria-selected="false" data-tab="distribution">Distribution</button>
    <button class="tab" type="button" role="tab" aria-selected="false" data-tab="podcasts">Podcasts</button>
    <button class="tab" type="button" role="tab" aria-selected="false" data-tab="activity">Activity</button>
    <button class="tab" type="button" role="tab" aria-selected="false" data-tab="setup">Setup</button>
  </nav>

  <div class="tab-panel" data-panel="setup" hidden>
  <section class="panel">
    <div class="settings-head">
      <div>
        <h2 style="margin:0">Site factory</h2>
        <div class="muted">Topic discovery, article ideas, publishing jobs, and blog settings for this site.</div>
      </div>
      <button class="settings-toggle ghost" type="button" onclick="toggleSettings()" aria-label="Open settings">⚙</button>
    </div>
    <div id="settingsPanel" class="settings-panel">
      <div class="compact-grid">
        <section class="stat">
          <h2>Site setup</h2>
          <form method="post" action="/sites/__SITE_ID__/settings" class="form-grid">
            <div class="field full"><label>Homepage URL</label><input name="homepage_url" value="__HOMEPAGE__" required></div>
            <div class="field"><label>Brand name</label><input name="brand_name" value="__BRAND__"></div>
            <div class="field"><label>Blog path</label><input name="blog_path" value="__BLOG_PATH__"></div>
            <div class="field full"><label>Custom blog domain</label><input name="custom_blog_domain" value="__CUSTOM_BLOG_DOMAIN__" placeholder="blog.client.com"><div class="hint">Client DNS: CNAME this host to blog.yas.ooo</div></div>
            <label class="check full"><input type="checkbox" name="hosted_blog_enabled" __HOSTED_CHECKED__> Enable hosted CNAME blog for this site</label>
            <div class="field full"><label>Local webroot</label><input name="root_path" value="__ROOT__" placeholder="/var/www/site-root"></div>
            <div class="field"><label>Languages</label><input name="languages" value="__LANGUAGES__" placeholder="en, ru, de"></div>
            <div class="field"><label>Publishing cadence</label><select name="publishing_cadence">__CADENCE_OPTIONS__</select></div>
            <div class="field full"><label>Site/product context</label><textarea name="content_context" placeholder="What this site sells, audience, positioning, internal links...">__CONTENT_CONTEXT__</textarea></div>
            <div class="field full"><label>Topic strategy</label><textarea name="topic_strategy" placeholder="Topics, clusters, tone, forbidden claims, CTA rules...">__TOPIC_STRATEGY__</textarea></div>
            <label class="check full"><input type="checkbox" name="factory_enabled" __FACTORY_CHECKED__> Enable article factory for this site</label>
            <div class="actions full"><button type="submit">Save settings</button></div>
          </form>
        </section>
        <section class="stat">
          <h2>Design and publishing</h2>
          <div class="actions">
            <button onclick="runAction(__SITE_ID__, 'scan')">Scan design</button>
            <button onclick="runAction(__SITE_ID__, 'bootstrap-preview')">Build preview</button>
            <button onclick="runAction(__SITE_ID__, 'install-blog')">Install /blog</button>
            <button class="ghost" onclick="queueTopicPlan(__SITE_ID__)">Queue topic plan</button>
            <button class="ghost" onclick="checkCname(__SITE_ID__)">Check CNAME</button>
          </div>
          <div class="stat"><strong>CNAME status</strong><div class="muted">__CNAME_STATUS__ · checked: __CNAME_CHECKED_AT__</div><div class="muted">Expected DNS: CNAME custom domain → blog.yas.ooo</div></div>
          <div class="stat"><strong>Last scan</strong><div class="muted">__SCANNED_AT__</div><div class="muted">__SCANNED_TITLE__</div></div>
          <div class="stat"><strong>Captured design</strong><div class="muted">__CSS_COUNT__ stylesheets · __FONTS__</div><div class="swatches">__SWATCHES__</div></div>
          <div class="stat"><strong>Delete connected site</strong><div class="muted">Removes it from Blog Core and generated previews only. It does not remove installed /blog files.</div><div style="margin-top:12px"><button class="danger" onclick="deleteSite(__SITE_ID__, '__DOMAIN__')">Delete from dashboard</button></div></div>
        </section>
      </div>
      __SOCIAL_CREDENTIALS_SETUP__
    </div>
  </section>
  </div>

  <div class="tab-panel" data-panel="content">
  <section class="panel production-panel">
    <div class="panel-title-row"><div><h2>Import existing blog</h2><div class="muted">Scan the current public /blog/ and import existing articles into Blog Core without changing live URLs or deleting files.</div></div><div class="actions"><button class="ghost" type="button" onclick="scanExistingBlog()">Scan existing blog</button><button type="button" onclick="importSelectedBlogArticles()">Import selected</button></div></div>
    <div id="importBlogResult" class="loading">Scan first to review existing article URLs before importing.</div>
  </section>

  <section class="panel production-panel">
    <h2>Content inventory</h2>
    <div class="muted">Existing imported live pages and new Blog Core article tasks. Imported pages are already published on the source site; queued items are future work. Section listing pages such as /blog/ are stored as import metadata and hidden from this work list.</div>
    __CONTENT_JOBS__
  </section>
  </div>

  <div class="tab-panel" data-panel="distribution" hidden>
  __DISTRIBUTION_SETTINGS__
  </div>

  <div class="tab-panel" data-panel="podcasts" hidden>
  __PODCAST_PANEL__
  </div>

  <div class="tab-panel" data-panel="discovery" hidden>
  <section class="panel">
    <h2 style="margin:0">Discovery inputs</h2>
    <div class="muted">Blog Core analyzes the site, search demand, and discussions in the background. All usable signals are used automatically for the journalist prompt.</div>
    <div class="discovery-control">
      <div id="analysisState" class="analysis-state"><span class="analysis-dot" aria-hidden="true"></span><span>Deep analysis in progress: reading site context and filtering audience signals...</span></div>
      <button id="generateIdeasButton" type="button" onclick="createIdeasFromSignals()" disabled>Generate SEO article ideas</button>
    </div>
    <div id="signalQuery" class="signal-summary" hidden></div>
    <div id="signals" hidden></div>
    <div id="articleIdeaResult" class="idea-stage" hidden></div>
  </section>
  </div>

  <div class="tab-panel" data-panel="activity" hidden>
  <section class="panel">
    <h2>Factory jobs</h2>
    __JOBS__
  </section>
  </div>
</main>
<div id="toast" class="toast"></div>
<script>
const SITE_ID=__SITE_ID__;let currentSignals=[];let currentIdeas=[];let currentRange='week';let ideaProgressTimer=null;let ideaProgressStartedAt=0;let draftProgressTimer=null;let draftProgressStartedAt=0;
function showToast(text){const toast=document.getElementById('toast');toast.textContent=text;toast.className='toast show';}
function escapeHtml(text){return String(text||'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function toggleSettings(){const panel=document.getElementById('settingsPanel');panel.hidden=!panel.hidden;}
function showTab(name){document.querySelectorAll('.tab').forEach(tab=>{const active=tab.dataset.tab===name;tab.classList.toggle('active',active);tab.setAttribute('aria-selected',active?'true':'false');});document.querySelectorAll('.tab-panel').forEach(panel=>{panel.hidden=panel.dataset.panel!==name;});if(location.hash!=='#'+name){history.replaceState(null,'','#'+name);}}
document.querySelectorAll('.tab').forEach(tab=>tab.addEventListener('click',()=>showTab(tab.dataset.tab)));
showTab((location.hash||'#content').slice(1));
async function runAction(id, action){showToast('Running '+action+'...');try{const res=await fetch('/api/sites/'+id+'/'+action,{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast(action+' completed');setTimeout(()=>location.reload(),700);}catch(e){showToast(action+' failed: '+e.message);}}
async function queueTopicPlan(id){showToast('Queueing topic plan...');try{const res=await fetch('/api/sites/'+id+'/queue-topic-plan',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Topic plan queued');setTimeout(()=>location.reload(),700);}catch(e){showToast('Queue failed: '+e.message);}}
async function checkCname(id){showToast('Checking CNAME...');try{const res=await fetch('/api/sites/'+id+'/check-cname',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('CNAME status: '+data.status);setTimeout(()=>location.reload(),900);}catch(e){showToast('CNAME check failed: '+e.message);}}
async function deleteSite(id, domain){if(!confirm('Remove '+domain+' from Blog Core? Installed /blog files on the site will not be deleted.')) return;showToast('Deleting '+domain+'...');try{const res=await fetch('/api/sites/'+id+'/delete',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);location.href='/';}catch(e){showToast('Delete failed: '+e.message);}}
function sourceLabel(source){return source==='popular_search'||source==='google_trends'?'Search demand':'Reddit discussion';}
function signalStatText(source){const meta=source.meta||{};const filtered=(Number(meta.filteredGlobal||0)+Number(meta.filteredRelevance||0)+Number(meta.deduped||0));const raw=Number(meta.raw||0);const kept=Number(meta.kept||(source.signals||[]).length);const limit=meta.limit?' · cap '+meta.limit:'';return 'kept '+kept+' / raw '+raw+' · filtered '+filtered+limit;}
function signalWarnings(source){return (source.warnings||[]).map(item=>`<div class="hint">${escapeHtml(item)}</div>`).join('');}
function renderSignalGroup(key,source,startIndex){const items=(source.signals||[]).filter(item=>!item.disabled);const applies=source.rangeApplies?'Period: '+escapeHtml(source.range||currentRange)+(source.bucket?' · Reddit bucket: '+escapeHtml(source.bucket):''):'No date filter';const empty=items.length?'':'<div class="loading">No usable signals found from this source.</div>';let index=startIndex;const cards=items.map(item=>{const cardIndex=index++;return `<label class="signal-card"><input type="checkbox" data-index="${cardIndex}" checked><div><em class="source-pill">${escapeHtml(sourceLabel(item.source))}</em><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.meta||'Audience signal, not an article title')}</span></div></label>`;}).join('');return {html:`<div class="signal-source-block" data-source="${escapeHtml(key)}"><div class="panel-title-row" style="margin:16px 0 10px"><div><h3 style="margin:0;font-size:18px">${escapeHtml(source.label||key)}</h3><div class="muted">${escapeHtml(source.description||'')}</div></div><div class="muted" style="text-align:right">${applies}<br>${escapeHtml(signalStatText(source))}</div></div>${signalWarnings(source)}${empty||'<div class="signal-list">'+cards+'</div>'}</div>`,nextIndex:index,items};}
function setAnalysisState(status,text){const state=document.getElementById('analysisState');if(!state) return;state.className='analysis-state '+(status||'');state.innerHTML='<span class="analysis-dot" aria-hidden="true"></span><span>'+escapeHtml(text||'')+'</span>';}
function setGenerateIdeasEnabled(enabled){const button=document.getElementById('generateIdeasButton');if(button) button.disabled=!enabled;}
function renderSignals(data){const sources=(data&&data.sources)||null;if(!sources){currentSignals=(data&&data.signals||data||[]).filter(item=>!item.disabled);return currentSignals;}currentSignals=[];['popularSearches','reddit'].forEach(key=>{const source=sources[key];if(!source) return;const items=(source.signals||[]).filter(item=>!item.disabled);currentSignals=currentSignals.concat(items);});return currentSignals;}
async function loadSignals(range){currentRange=range||'week';currentSignals=[];setGenerateIdeasEnabled(false);setAnalysisState('', 'Deep analysis in progress: reading site context and filtering audience signals...');const summary=document.getElementById('signalQuery');if(summary){summary.hidden=true;summary.textContent='';}try{const res=await fetch('/api/sites/'+SITE_ID+'/topic-signals?range='+encodeURIComponent(currentRange));const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);const counts=data.counts||{};renderSignals(data);const searchText='Search demand '+(counts.popularSearches||0)+' kept / '+(counts.popularSearchesRaw||0)+' raw, '+(counts.popularSearchesFiltered||0)+' filtered';const redditText='Reddit '+(counts.reddit||0)+' kept / '+(counts.redditRaw||0)+' raw, '+(counts.redditFiltered||0)+' filtered';if(summary){summary.hidden=false;summary.textContent='Analysis ready: '+currentSignals.length+' usable audience signals selected automatically. '+searchText+' · '+redditText+'.';}if(currentSignals.length){setAnalysisState('ready','Deep analysis complete. '+currentSignals.length+' usable signals will be used automatically.');setGenerateIdeasEnabled(true);}else{setAnalysisState('failed','Deep analysis finished, but no usable audience signals were found for this site.');setGenerateIdeasEnabled(false);}}catch(e){setAnalysisState('failed','Topic discovery failed: '+e.message);setGenerateIdeasEnabled(false);if(summary){summary.hidden=false;summary.textContent='Topic discovery failed: '+e.message;}}}
function renderArticleIdeas(ideas,rejected,counts){const box=document.getElementById('articleIdeaResult');currentIdeas=ideas||[];box.hidden=false;if(!currentIdeas.length){box.className='loading idea-stage';box.textContent='No new article ideas after checking existing content.';return;}counts=counts||{};const generated=counts.generated||currentIdeas.length;const passes=counts.passes?' across '+counts.passes+' pass'+(counts.passes===1?'':'es'):'';const safety=counts.safetyCap?' · safety cap '+counts.safetyCap:'';const statNote='<div class="hint">Accepted '+currentIdeas.length+' valid ideas from '+(counts.signals||'selected')+' signals. Model candidates checked: '+generated+passes+'. Rejected: '+((rejected&&rejected.length)||0)+safety+'.</div>';const rejectedNote=(rejected&&rejected.length)?'<div class="hint">Filtered '+rejected.length+' ideas because they were too similar, duplicated, or failed SEO/editorial validation.</div>':'';box.className='idea-stage';box.innerHTML='<div class="panel-title-row"><div><h3>SEO article ideas to add</h3><div class="muted">Generated by the journalist prompt from selected audience interests. Only checked ideas will be added to Planned publications.</div></div><div class="actions"><button type="button" onclick="queueSelectedArticleIdeas()">Add selected to queue</button></div></div>'+statNote+rejectedNote+'<div class="idea-list">'+currentIdeas.map((idea,index)=>`<label class="idea-row"><input type="checkbox" data-index="${index}" checked><div><strong>${escapeHtml(idea.title)}</strong><span>${escapeHtml(idea.angle||'')}</span><span>${escapeHtml(idea.seo_intent||'seo')}: ${escapeHtml(idea.seo_rationale||'')}</span><em>${escapeHtml(idea.source_title||'')}</em></div></label>`).join('')+'</div>';}
function formatElapsed(ms){const total=Math.max(0,Math.floor(ms/1000));const m=Math.floor(total/60);const s=String(total%60).padStart(2,'0');return m+':'+s;}
function ideaProgressStep(elapsed){if(elapsed<8)return ['Preparing site context and selected audience signals',18];if(elapsed<24)return ['Running the journalist SEO prompt through the model',42];if(elapsed<48)return ['Expanding missing clusters and checking the next model pass',64];if(elapsed<82)return ['Filtering duplicates, obsolete years, and weak SERP-style ideas',78];return ['Still working: final validation can take a bit on larger signal sets',88];}
function startIdeaProgress(signalCount){stopIdeaProgress(false);ideaProgressStartedAt=Date.now();const box=document.getElementById('articleIdeaResult');box.hidden=false;box.className='idea-stage';box.innerHTML='<div class="idea-progress"><div class="idea-progress-head"><div class="idea-progress-title"><span class="analysis-dot" aria-hidden="true"></span><span>Generating SEO article ideas</span></div><div id="ideaProgressTime" class="idea-progress-time">0:00</div></div><div class="idea-progress-bar"><div id="ideaProgressFill" class="idea-progress-fill"></div></div><div id="ideaProgressStep" class="idea-progress-step">Preparing '+signalCount+' audience signals for the journalist prompt...</div></div>';const fill=document.getElementById('ideaProgressFill');const step=document.getElementById('ideaProgressStep');const time=document.getElementById('ideaProgressTime');function tick(){const elapsed=Math.floor((Date.now()-ideaProgressStartedAt)/1000);const current=ideaProgressStep(elapsed);if(fill)fill.style.width=current[1]+'%';if(step)step.textContent=current[0];if(time)time.textContent=formatElapsed(Date.now()-ideaProgressStartedAt);}tick();ideaProgressTimer=setInterval(tick,1000);}
function stopIdeaProgress(complete){if(ideaProgressTimer){clearInterval(ideaProgressTimer);ideaProgressTimer=null;}if(complete){const fill=document.getElementById('ideaProgressFill');const step=document.getElementById('ideaProgressStep');if(fill)fill.style.width='100%';if(step)step.textContent='Finalizing accepted ideas...';}}
async function createIdeasFromSignals(){const selected=currentSignals.slice();if(!selected.length){showToast('Deep analysis is not ready yet');return;}setGenerateIdeasEnabled(false);startIdeaProgress(selected.length);showToast('Generating article ideas...');try{const res=await fetch('/api/sites/'+SITE_ID+'/article-ideas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({range:currentRange,signals:selected})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);stopIdeaProgress(true);renderArticleIdeas(data.ideas||[],data.rejectedSimilar||[],data.counts||{});showToast('Article ideas ready: '+((data.ideas||[]).length)+' valid ideas');}catch(e){stopIdeaProgress(false);const box=document.getElementById('articleIdeaResult');box.className='loading idea-stage';box.textContent='Article ideas failed: '+e.message;showToast('Article ideas failed: '+e.message);}finally{setGenerateIdeasEnabled(currentSignals.length>0);}}
async function queueSelectedArticleIdeas(){const selected=[...document.querySelectorAll('#articleIdeaResult input[type="checkbox"]:checked')].map(input=>currentIdeas[Number(input.dataset.index)]).filter(Boolean);if(!selected.length){showToast('Select at least one article idea');return;}showToast('Adding selected ideas to queue...');try{const signalSelection=currentSignals.slice();const res=await fetch('/api/sites/'+SITE_ID+'/article-ideas/queue',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({range:currentRange,signals:signalSelection,ideas:selected})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);const rejected=(data.rejectedSimilar||[]).length;showToast('Queued '+(data.jobs||[]).length+' article ideas'+(rejected?' · skipped '+rejected+' similar':'')+'. Reloading...');setTimeout(()=>{location.hash='#distribution';location.reload();},1200);}catch(e){showToast('Queue failed: '+e.message);}}
function draftProgressStep(elapsed){if(elapsed<8)return 'Preparing article context and source-site rules';if(elapsed<24)return 'Generating the draft body and metadata';if(elapsed<55)return 'Validating HTML, FAQ, images, and SEO fields';if(elapsed<95)return 'Still working: long articles and legacy factories can take a bit';return 'Still running. Keep this tab open while the factory finishes.';}
function startDraftProgress(label){stopDraftProgress(false);draftProgressStartedAt=Date.now();const startMessage=(label||'Generating draft')+' · 0:00 · Preparing article context and source-site rules';setBulkProgress(startMessage);showToast(startMessage);draftProgressTimer=setInterval(()=>{const elapsed=Date.now()-draftProgressStartedAt;const message=(label||'Generating draft')+' · '+formatElapsed(elapsed)+' · '+draftProgressStep(Math.floor(elapsed/1000));setBulkProgress(message);showToast(message);},1000);}
function stopDraftProgress(complete){if(draftProgressTimer){clearInterval(draftProgressTimer);draftProgressTimer=null;}if(complete){setBulkProgress('Finalizing draft status...', false);}}
async function generateArticleJob(jobId,label){const progressLabel=label||'Generating draft';showToast(progressLabel+'...');startDraftProgress(progressLabel);try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(jobId)+'/generate',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);stopDraftProgress(true);if(data.status==='GENERATING'){showToast('Generation started in source factory. Refreshing status...');setBulkProgress('Generation started in source factory. Reloading status...', false);setTimeout(()=>location.reload(),1800);}else{showToast('Draft generated: '+(data.slug||jobId));setBulkProgress('Draft generated. Reloading...', false);setTimeout(()=>location.reload(),900);}}catch(e){stopDraftProgress(false);setBulkProgress('Generation failed: '+e.message, false);clearBulkProgress();showToast('Generation failed: '+e.message);}}
async function publishArticleJob(jobId){if(!confirm('Publish this draft to the source site now?'))return;showToast('Publishing to source site...');setBulkProgress('Publishing to source site...', true);try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(jobId)+'/publish',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);setBulkProgress('Published. Reloading...', false);showToast('Published: '+(data.publishedUrl||jobId));setTimeout(()=>location.reload(),1200);}catch(e){setBulkProgress('Publish failed: '+e.message, false);clearBulkProgress();showToast('Publish failed: '+e.message);}}
function generationRuntimeLabel(startedAt){const started=startedAt?Date.parse(startedAt):NaN;if(!Number.isFinite(started))return 'working...';return formatElapsed(Date.now()-started);}
function updateGenerationElapsed(panel){const elapsed=panel.querySelector('[data-generation-elapsed]');if(elapsed)elapsed.textContent=generationRuntimeLabel(panel.dataset.generationStartedAt);}
function updateGenerationPanel(panel,data){const job=data.job||{};const logs=data.logs||[];const latest=logs.length?logs[logs.length-1]:null;const note=panel.querySelector('[data-generation-note]');panel.dataset.generationStartedAt=job.updated_at||job.created_at||panel.dataset.generationStartedAt||'';updateGenerationElapsed(panel);if(note&&latest)note.textContent=(latest.step?latest.step+': ':'')+(latest.message||'Generation is still running.');}
async function pollGeneratingJob(panel){const jobId=panel.dataset.generatingJobId;if(!jobId)return;try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(jobId));const data=await res.json();if(!res.ok)throw new Error(data.error||res.statusText);updateGenerationPanel(panel,data);const status=String((data.job&&data.job.status)||'').toUpperCase();if(status&&status!=='GENERATING'){const message=status==='DRAFT'?'Draft is ready. Reloading...':('Generation finished with status '+status+'. Reloading...');setBulkProgress(message,false);showToast(message);setTimeout(()=>location.reload(),900);return;}}catch(e){const note=panel.querySelector('[data-generation-note]');if(note)note.textContent='Status check failed: '+e.message;}}
function initGeneratingPollers(){const panels=[...document.querySelectorAll('[data-generating-job-id]')];if(!panels.length)return;panels.forEach(panel=>{pollGeneratingJob(panel);setInterval(()=>pollGeneratingJob(panel),5000);setInterval(()=>updateGenerationElapsed(panel),1000);});showToast(panels.length+' generation task'+(panels.length===1?' is':'s are')+' still running...');}
function selectedPlannedTasks(){return [...document.querySelectorAll('.planned-select:checked')].map(input=>({groupId:input.value,jobId:input.dataset.jobId})).filter(item=>item.groupId);}
function selectedPlannedGroupIds(){return selectedPlannedTasks().map(item=>item.groupId);}
function togglePlannedSelection(checked){document.querySelectorAll('.planned-select').forEach(input=>{input.checked=checked;});}
function setBulkProgress(text, active=true){const box=document.getElementById('bulkProgress');if(!box) return;box.hidden=false;box.textContent=text;document.querySelectorAll('.planned-bulkbar button,.planned-select,.planned-select-all input').forEach(el=>{el.disabled=active;});}
function clearBulkProgress(){document.querySelectorAll('.planned-bulkbar button,.planned-select,.planned-select-all input').forEach(el=>{el.disabled=false;});}
async function bulkPlannedAction(action){const tasks=selectedPlannedTasks();const groupIds=tasks.map(item=>item.groupId);if(!groupIds.length){showToast('Select at least one planned task');return;}if(action==='generate'){if(!confirm('Generate '+tasks.length+' selected planned task groups now?')) return;let ok=0;let failed=0;for(let i=0;i<tasks.length;i++){const task=tasks[i];setBulkProgress('Generating '+(i+1)+'/'+tasks.length+'. Keep this tab open.');showToast('Generating '+(i+1)+'/'+tasks.length+'...');try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(task.jobId)+'/generate',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);ok++;}catch(e){failed++;}}setBulkProgress('Bulk generation finished: '+ok+' ok, '+failed+' failed. Reloading...', false);showToast('Bulk generation finished: '+ok+' ok, '+failed+' failed');setTimeout(()=>location.reload(),1800);return;}if(action==='delete'&&!confirm('Delete '+groupIds.length+' selected planned task groups from Blog Core? This does not delete live site files.')) return;setBulkProgress('Deleting '+groupIds.length+' planned task groups...');showToast('Deleting '+groupIds.length+' planned task groups...');try{const res=await fetch('/api/sites/'+SITE_ID+'/planned-groups/bulk',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,groupIds})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);setBulkProgress('Deleted '+(data.deletedJobs||0)+' job rows. Reloading...', false);showToast('Deleted '+(data.deletedJobs||0)+' job rows in '+(data.groups||groupIds.length)+' groups');setTimeout(()=>location.reload(),1200);}catch(e){clearBulkProgress();showToast('Bulk delete failed: '+e.message);}}
async function generateSocialDrafts(jobId){showToast('Preparing social drafts...');try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(jobId)+'/social-drafts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);const summary=(data.drafts||[]).map(d=>d.channel+': '+d.charCount+'/'+d.maxChars).join(' · ');showToast('Social drafts ready: '+summary);setTimeout(()=>location.reload(),1200);}catch(e){showToast('Social drafts failed: '+e.message);}}
async function publishZernioSocial(jobId){if(!confirm('Publish ready X, Pinterest, Instagram, Threads, and Reddit drafts now through Zernio?'))return;showToast('Sending social drafts through Zernio...');try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(jobId)+'/social-publish/zernio',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})});const data=await res.json();if(!res.ok)throw new Error(data.error||res.statusText);const summary=(data.results||[]).map(item=>item.channel+': '+(item.ok?item.status:'failed')).join(' · ');showToast('Zernio result: '+summary);setTimeout(()=>location.reload(),1200);}catch(e){showToast('Zernio publish failed: '+e.message);}}
async function saveFactorySettings(event){event.preventDefault();const form=event.currentTarget;const fd=new FormData(form);const channels=fd.getAll('channels');const body={channels,topicDiscovery:{enabled:fd.has('discovery_enabled'),direction:fd.get('direction')||'',categoryHint:fd.get('category_hint')||'',perRunLimit:Number(fd.get('per_run_limit')||15),topN:Number(fd.get('top_n')||3),timezone:fd.get('timezone')||'UTC'},autopublish:{enabled:fd.has('autopublish_enabled'),timesPerDay:Number(fd.get('times_per_day')||3),timezone:fd.get('timezone')||'UTC',startHour:Number(fd.get('start_hour')||9),endHour:Number(fd.get('end_hour')||21),linkedinIncludeLink:fd.has('linkedin_include_link'),telegramIncludeLink:fd.has('telegram_include_link'),twitterIncludeLink:fd.has('twitter_include_link'),tumblrIncludeLink:fd.has('tumblr_include_link'),pinterestIncludeLink:fd.has('pinterest_include_link'),instagramIncludeLink:fd.has('instagram_include_link'),threadsIncludeLink:fd.has('threads_include_link'),redditIncludeLink:fd.has('reddit_include_link')}};showToast('Saving factory settings...');try{const res=await fetch('/api/sites/'+SITE_ID+'/factory-settings',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Factory settings saved');setTimeout(()=>location.reload(),700);}catch(e){showToast('Save failed: '+e.message);}}
function socialCredentialsFromForm(form){const fd=new FormData(form);const credentials={};for(const [key,value] of fd.entries()){const clean=String(value||'').trim();if(clean) credentials[key]=clean;}return credentials;}
async function saveSocialCredentials(event,provider){event.preventDefault();const form=event.currentTarget;const credentials=socialCredentialsFromForm(form);showToast('Saving '+provider+' credentials...');try{const res=await fetch('/api/sites/'+SITE_ID+'/social-connections/'+encodeURIComponent(provider),{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({credentials})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast(provider+' credentials saved: '+data.status);setTimeout(()=>location.reload(),700);}catch(e){showToast('Save failed: '+e.message);}}
async function testSocialConnection(provider){const form=document.querySelector('.social-credentials-card[data-provider="'+provider+'"]');const credentials=form?socialCredentialsFromForm(form):{};showToast('Testing '+provider+' connection...');try{const res=await fetch('/api/sites/'+SITE_ID+'/social-connections/'+encodeURIComponent(provider)+'/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({credentials})});const data=await res.json();if(!res.ok) throw new Error(data.message||data.error||res.statusText);showToast(data.message||provider+' connected');setTimeout(()=>location.reload(),900);}catch(e){showToast('Connection test failed: '+e.message);}}
async function connectLinkedIn(siteId){showToast('Opening LinkedIn authorization...');try{const res=await fetch('/api/sites/'+siteId+'/social-connections/linkedin/connect',{method:'POST'});const data=await res.json();if(!res.ok)throw new Error(data.error||res.statusText);window.location.assign(data.authUrl);}catch(e){showToast('LinkedIn connection failed: '+e.message);}}
function setPodcastProgress(text){const box=document.getElementById('podcastProgress');if(!box)return;box.hidden=false;box.textContent=text;}
async function savePodcastSettings(event){event.preventDefault();const form=event.currentTarget;const fd=new FormData(form);const body={enabled:fd.has('enabled'),hostName:fd.get('host_name')||'',voiceName:fd.get('voice_name')||'Kore',voiceDirection:fd.get('voice_direction')||'',targetMinutes:Number(fd.get('target_minutes')||8)};showToast('Saving podcast settings...');try{const res=await fetch('/api/sites/'+SITE_ID+'/podcast-settings',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await res.json();if(!res.ok)throw new Error(data.error||res.statusText);showToast('Podcast settings saved');setTimeout(()=>location.reload(),700);}catch(e){showToast('Podcast settings failed: '+e.message);}}
async function generatePodcast(){const jobId=document.getElementById('podcastSourceJob')?.value||'';if(!jobId){showToast('Select an article first');return;}if(!confirm('Generate a podcast script and Gemini audio for this article? It will remain unpublished for review.'))return;let seconds=0;setPodcastProgress('Generating podcast script and audio. This can take several minutes. 0:00');const timer=setInterval(()=>{seconds++;setPodcastProgress('Generating podcast script and audio. Long episodes are synthesized in reliable audio chunks. '+Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0'));},1000);showToast('Generating podcast episode...');try{const res=await fetch('/api/sites/'+SITE_ID+'/podcast-episodes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jobId})});const data=await res.json();if(!res.ok)throw new Error(data.error||res.statusText);setPodcastProgress('Episode ready for review. Reloading...');showToast('Podcast episode ready');setTimeout(()=>location.reload(),900);}catch(e){setPodcastProgress('Podcast generation failed: '+e.message);showToast('Podcast generation failed: '+e.message);}finally{clearInterval(timer);}}
async function publishPodcast(episodeId){if(!confirm('Publish this reviewed podcast episode to the Blog Core podcast feed now?'))return;showToast('Publishing podcast episode...');try{const res=await fetch('/api/sites/'+SITE_ID+'/podcast-episodes/'+encodeURIComponent(episodeId)+'/publish',{method:'POST'});const data=await res.json();if(!res.ok)throw new Error(data.error||res.statusText);showToast('Podcast published');setTimeout(()=>location.reload(),800);}catch(e){showToast('Podcast publishing failed: '+e.message);}}
let currentImportArticles=[];
function renderImportArticles(items,warnings){const box=document.getElementById('importBlogResult');currentImportArticles=items||[];const note=(warnings&&warnings.length)?'<div class="hint">Notes: '+warnings.map(w=>String(w)).join(' · ')+'</div>':'';if(!currentImportArticles.length){box.className='loading';box.innerHTML='No importable article URLs found.'+note;return;}box.className='import-list';box.innerHTML='<div class="muted">Found '+currentImportArticles.length+' article URLs. Review and import only the ones that should remain live.</div>'+note+currentImportArticles.map((item,index)=>`<label class="import-row"><input type="checkbox" data-index="${index}" checked><div><strong>${item.slug||item.url}</strong><span>${item.url}</span></div></label>`).join('');}
async function scanExistingBlog(){const box=document.getElementById('importBlogResult');box.className='loading';box.textContent='Scanning sitemap and /blog/ links...';try{const res=await fetch('/api/sites/'+SITE_ID+'/import-blog/scan',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);renderImportArticles(data.articles||[],data.warnings||[]);showToast('Found '+(data.articles||[]).length+' importable URLs');}catch(e){box.className='loading';box.textContent='Import scan failed: '+e.message;showToast('Import scan failed: '+e.message);}}
async function importSelectedBlogArticles(){const selected=[...document.querySelectorAll('#importBlogResult input[type="checkbox"]:checked')].map(input=>currentImportArticles[Number(input.dataset.index)]?.url).filter(Boolean);if(!selected.length){showToast('Select at least one article URL');return;}if(!confirm('Import '+selected.length+' existing articles into Blog Core? Live files and URLs will not be changed.')) return;showToast('Importing existing articles...');try{const res=await fetch('/api/sites/'+SITE_ID+'/import-blog/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({urls:selected})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Imported '+(data.imported||[]).length+' articles, skipped '+(data.skipped||[]).length+', errors '+(data.errors||[]).length);setTimeout(()=>location.reload(),1200);}catch(e){showToast('Import failed: '+e.message);}}
loadSignals('week');
initGeneratingPollers();
</script>
</body>
</html>"""

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog Core</title>
<style>
:root{--bg:#0b1020;--panel:rgba(255,255,255,.08);--line:rgba(255,255,255,.15);--text:#f8fafc;--muted:#a6b0c3;--accent:#8b5cf6;--accent2:#22c55e}
*{box-sizing:border-box} body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 0,#3b1a75 0,transparent 38%),radial-gradient(circle at 78% 15%,#0d7a65 0,transparent 28%),#0b1020;color:var(--text);min-height:100vh} a{color:inherit}.shell{max-width:1180px;margin:0 auto;padding:44px 22px 90px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:28px}.title{font-size:clamp(42px,7vw,78px);letter-spacing:-.055em;line-height:.92;margin:0}.sub{color:var(--muted);font-size:18px;line-height:1.55;max-width:720px;margin:18px 0 0}.badge{border:1px solid var(--line);background:rgba(255,255,255,.07);border-radius:999px;padding:10px 14px;color:#d8cdfd;font-weight:800;white-space:nowrap}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.11),rgba(255,255,255,.06));box-shadow:0 22px 90px rgba(0,0,0,.32);backdrop-filter:blur(22px);border-radius:24px;padding:22px;margin:18px 0}.form{display:grid;grid-template-columns:1.2fr 1fr 1fr auto;gap:12px}.form input{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.55);color:#fff;padding:14px 15px;font-size:14px;outline:none}.form input:focus{border-color:rgba(139,92,246,.9);box-shadow:0 0 0 4px rgba(139,92,246,.18)}button,.btn{border:0;border-radius:14px;background:linear-gradient(135deg,#8b5cf6,#22c55e);color:#fff;font-weight:900;padding:13px 16px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;min-height:42px}.btn.ghost{background:rgba(255,255,255,.08);border:1px solid var(--line)}.site-card{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;border:1px solid var(--line);border-radius:20px;background:rgba(8,13,29,.58);padding:18px;margin-top:14px}.site-domain{font-size:22px;font-weight:900;letter-spacing:-.02em}.site-url,.site-meta,.muted{color:var(--muted);font-size:13px;margin-top:5px}.actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;align-items:center}.actions button{background:rgba(255,255,255,.1);border:1px solid var(--line)}.actions .danger{background:rgba(239,68,68,.16);border-color:rgba(239,68,68,.45);color:#fecaca}.site-state{display:inline-flex;align-items:center;min-height:38px;border:1px solid rgba(34,197,94,.28);background:rgba(34,197,94,.1);border-radius:999px;padding:0 13px;color:#a7f3d0;font-size:12px;font-weight:900;white-space:nowrap}.empty{color:var(--muted);padding:26px;text-align:center}.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111827;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:16px;padding:14px 18px;box-shadow:0 20px 80px rgba(0,0,0,.4);display:none;max-width:min(720px,calc(100vw - 32px));z-index:10}.toast.show{display:block}@media(max-width:900px){.top,.site-card{display:block}.form{grid-template-columns:1fr}.actions{justify-content:flex-start;margin-top:16px}.badge{display:inline-block;margin-top:18px}.site-state{white-space:normal}}
</style>
</head>
<body>
<main class="shell">
  <section class="top">
    <div><h1 class="title">Universal Blog Core</h1><p class="sub">Connect any site, scan its public design, generate a matching blog shell, then either install into a local root or host it through a CNAME custom blog domain. This is the base for the future multi-site article factory dashboard.</p></div>
    <div class="badge">blog.yas.ooo · MVP</div>
  </section>
  <section class="panel">
    <form class="form" method="post" action="/api/sites">
      <input name="homepage_url" placeholder="Homepage URL, e.g. https://yas.wine/" required>
      <input name="brand_name" placeholder="Brand name">
      <input name="root_path" placeholder="Local webroot or leave empty for CNAME hosted blog">
      <button type="submit">Connect site</button>
    </form>
  </section>
  <section class="panel">
    <h2 style="margin:0 0 8px;font-size:24px;letter-spacing:-.03em">Connected sites</h2>
    <div class="muted">Flow: Scan design → Build preview → use Local install for sites on this server, or CNAME hosting for external sites.</div>
    __ROWS__
  </section>
</main>
<div id="toast" class="toast"></div>
<script>
async function runAction(id, action){
  const toast=document.getElementById('toast');
  toast.textContent='Running '+action+'...'; toast.className='toast show';
  try{
    const res=await fetch('/api/sites/'+id+'/'+action,{method:'POST'});
    const data=await res.json();
    if(!res.ok) throw new Error(data.error||res.statusText);
    toast.textContent=action+' completed';
    setTimeout(()=>location.reload(),700);
  }catch(e){toast.textContent=action+' failed: '+e.message;}
}
async function deleteSite(id, domain){
  if(!confirm('Remove '+domain+' from Blog Core? Installed /blog files on the site will not be deleted.')) return;
  const toast=document.getElementById('toast');
  toast.textContent='Deleting '+domain+'...'; toast.className='toast show';
  try{
    const res=await fetch('/api/sites/'+id+'/delete',{method:'POST'});
    const data=await res.json();
    if(!res.ok) throw new Error(data.error||res.statusText);
    toast.textContent='Site removed';
    setTimeout(()=>location.reload(),500);
  }catch(e){toast.textContent='Delete failed: '+e.message;}
}
</script>
</body>
</html>"""


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT)
