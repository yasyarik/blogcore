import json
import os
import re
import secrets
import shutil
import socket
import sqlite3
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
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

app = Flask(__name__)
DATA_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)


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
                created_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists social_posts_site_job_channel_idx on social_posts(site_id,job_id,channel,created_at);
            create table if not exists autopublish_settings (
                site_id integer primary key,
                enabled integer not null default 0,
                times_per_day integer not null default 3,
                channels_json text not null default '["linkedin","telegram","twitter","tumblr"]',
                timezone text not null default 'UTC',
                start_hour integer not null default 9,
                end_hour integer not null default 21,
                linkedin_include_link integer not null default 0,
                telegram_include_link integer not null default 0,
                twitter_include_link integer not null default 0,
                tumblr_include_link integer not null default 0,
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
            """
        )
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


def get_content_jobs(site_id):
    with db() as conn:
        return conn.execute(
            "select * from content_jobs where site_id=? order by created_at desc limit 24",
            (site_id,),
        ).fetchall()


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
    providers = ["linkedin", "telegram", "twitter", "tumblr"]
    with db() as conn:
        rows = {r["provider"]: r for r in conn.execute("select * from social_connections where site_id=?", (site_id,)).fetchall()}
    return {provider: rows.get(provider) for provider in providers}


def simple_slug(text):
    slug = re.sub(r"[^a-z0-9\s-]", "", (text or "").lower())
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug[:90] or "article"


def render_jobs(rows):
    if not rows:
        return "<div class='empty'>No publish jobs yet.</div>"
    out = []
    for row in rows:
        out.append(
            f"""
            <div class="job-row">
              <div><strong>{escape(row['kind'])}</strong><span>{escape(row['created_at'])}</span></div>
              <b class="status {escape(row['status'])}">{escape(row['status'])}</b>
              <p>{escape(row['message'] or '')}</p>
            </div>
            """
        )
    return "".join(out)


def render_content_jobs(rows):
    if not rows:
        return "<div class='empty'>No article production jobs yet. Select trend signals and create article ideas to queue jobs.</div>"
    out = []
    for row in rows:
        title = row["title"] or row["topic"]
        social = []
        for channel in ("linkedin", "telegram", "twitter", "tumblr"):
            status = row[f"{channel}_status"] or "not queued"
            social.append(f"<span>{channel}: {escape(status)}</span>")
        out.append(
            f"""
            <div class="job-row production-job">
              <div><strong>{escape(title)}</strong><span>{escape(row['created_at'])} · {escape(row['category'] or 'Uncategorized')}</span></div>
              <div class="actions"><b class="status {escape((row['status'] or '').lower())}">{escape(row['status'])}</b><button class="ghost" type="button" onclick="generateArticleJob('{escape(row['id'], quote=True)}')">Generate draft</button></div>
              <p>{escape(row['description'] or row['topic'] or '')}</p>
              <div class="social-statuses">{''.join(social)}</div>
            </div>
            """
        )
    return "".join(out)


def render_distribution_settings(site_id):
    auto = get_autopublish_settings(site_id)
    disc = get_topic_discovery_settings(site_id)
    connections = get_social_connections(site_id)
    channels = []
    try:
        selected = set(json.loads(auto["channels_json"] or "[]"))
    except Exception:
        selected = {"linkedin", "telegram", "twitter", "tumblr"}
    connection_cards = []
    for provider, label in (("linkedin", "LinkedIn"), ("telegram", "Telegram"), ("twitter", "X / Twitter"), ("tumblr", "Tumblr")):
        row = connections.get(provider)
        status = row["status"] if row else "disconnected"
        checked = "checked" if provider in selected else ""
        channels.append(f"<label class='check compact'><input type='checkbox' name='channels' value='{provider}' {checked}> {label}</label>")
        connection_cards.append(f"<div class='channel-card'><strong>{label}</strong><span>{escape(status)}</span></div>")
    return f"""
    <section class="panel production-panel">
      <div class="panel-title-row"><div><h2>Distribution and autopublish</h2><div class="muted">Same publishing controls as the YAS Wine factory, scoped to this connected site.</div></div></div>
      <form class="form-grid" onsubmit="saveFactorySettings(event)">
        <div class="field"><label>Discovery direction</label><input name="direction" value="{escape(disc['direction'] or '', quote=True)}" placeholder="Core topic or product category"></div>
        <div class="field"><label>Category hint</label><input name="category_hint" value="{escape(disc['category_hint'] or '', quote=True)}" placeholder="Buying Guides, Use Cases, etc."></div>
        <div class="field"><label>Topics per run</label><input name="per_run_limit" type="number" min="1" max="50" value="{int(disc['per_run_limit'] or 15)}"></div>
        <div class="field"><label>Top N to queue</label><input name="top_n" type="number" min="1" max="20" value="{int(disc['top_n'] or 3)}"></div>
        <label class="check"><input type="checkbox" name="discovery_enabled" {'checked' if int(disc['enabled'] or 0) else ''}> Auto-discover topics</label>
        <label class="check"><input type="checkbox" name="autopublish_enabled" {'checked' if int(auto['enabled'] or 0) else ''}> Autopublish approved articles</label>
        <div class="field"><label>Times per day</label><input name="times_per_day" type="number" min="1" max="12" value="{int(auto['times_per_day'] or 3)}"></div>
        <div class="field"><label>Timezone</label><input name="timezone" value="{escape(auto['timezone'] or 'UTC', quote=True)}"></div>
        <div class="field"><label>Start hour</label><input name="start_hour" type="number" min="0" max="23" value="{int(auto['start_hour'] or 9)}"></div>
        <div class="field"><label>End hour</label><input name="end_hour" type="number" min="0" max="23" value="{int(auto['end_hour'] or 21)}"></div>
        <div class="field full"><label>Publish channels</label><div class="channel-checks">{''.join(channels)}</div></div>
        <label class="check"><input type="checkbox" name="linkedin_include_link" {'checked' if int(auto['linkedin_include_link'] or 0) else ''}> LinkedIn includes article link</label>
        <label class="check"><input type="checkbox" name="telegram_include_link" {'checked' if int(auto['telegram_include_link'] or 0) else ''}> Telegram includes article link</label>
        <label class="check"><input type="checkbox" name="twitter_include_link" {'checked' if int(auto['twitter_include_link'] or 0) else ''}> X includes article link</label>
        <label class="check"><input type="checkbox" name="tumblr_include_link" {'checked' if int(auto['tumblr_include_link'] or 0) else ''}> Tumblr includes article link</label>
        <div class="field full"><label>Channel connection status</label><div class="channel-grid">{''.join(connection_cards)}</div><div class="hint">OAuth/connect routes will be wired to the same providers as YAS Wine: LinkedIn, Telegram, X, and Tumblr.</div></div>
        <div class="actions full"><button type="submit">Save factory distribution settings</button></div>
      </form>
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


def render_manage_site_page(site):
    jobs = render_jobs(get_site_jobs(site["id"]))
    content_jobs = render_content_jobs(get_content_jobs(site["id"]))
    distribution_settings = render_distribution_settings(site["id"])
    preview = f"<a class='btn ghost' target='_blank' href='{escape(site['preview_path'])}'>Open preview</a>" if site["preview_path"] else "<span class='muted'>Build preview first</span>"
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
        .replace("__SITE_SWITCHER__", render_site_switcher(site["id"]))
    )


def site_topic_seed(site):
    profile = get_profile(site["id"]) if site and "id" in site.keys() else None
    profile_text = ""
    if profile:
        profile_text = " ".join([profile["title"] or "", profile["description"] or ""])
    brand_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", ((site["brand_name"] or "") + " " + (site["domain"] or "")).lower()))
    pieces = [site["content_context"] or "", site["topic_strategy"] or "", profile_text, site["brand_name"] or "", site["domain"] or ""]
    full = " ".join(pieces).lower()
    stop = {"www", "com", "https", "http", "blog", "site", "content", "topics", "brand", "with", "from", "that", "this", "and", "the", "for", "guide", "guides", "buying", "choose", "clear", "help", "helps", "understand", "plan"}
    words = []
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", full):
        if word in stop:
            continue
        if word in brand_tokens and word not in {"wine", "wines", "food", "pairing", "travel", "fashion", "beauty", "pets", "home"}:
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
    "how", "into", "site", "that", "the", "this", "tips", "topics", "what", "when", "with", "your",
}


def timeframe_to_reddit(range_key):
    return {"week": "week", "month": "month", "3m": "year", "6m": "year"}.get(range_key, "week")


def timeframe_to_days(range_key):
    return {"week": 7, "month": 30, "3m": 90, "6m": 180}.get(range_key, 7)


def signal_keywords(query):
    words = []
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", (query or "").lower()):
        if word in SIGNAL_STOP_WORDS:
            continue
        if word not in words:
            words.append(word)
    return words


def signal_relevance_score(title, query):
    haystack = (title or "").lower()
    score = 0
    for word in signal_keywords(query):
        if re.search(rf"\b{re.escape(word)}\b", haystack):
            score += 2
        elif word in haystack:
            score += 1
    return score


def fetch_google_trend_signals(site, range_key):
    query = site_topic_seed(site)
    days = timeframe_to_days(range_key)
    warnings = []
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f"{query} when:{days}d", "hl": "en-US", "gl": "US", "ceid": "US:en"})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 BlogCore topic discovery"})
        with urllib.request.urlopen(req, timeout=18) as resp:
            xml = resp.read(1200000).decode("utf-8", errors="replace")
        root = ET.fromstring(xml)
    except Exception as e:
        return [], [f"Google topic signals unavailable: {e}"]

    ranked = []
    seen = set()
    for index, item in enumerate(root.findall(".//item")[:60]):
        title = re.sub(r"\s+-\s+[^-]+$", "", (item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if not title:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        score = signal_relevance_score(title, query)
        ranked.append((score, -index, {"source": "google_trends", "title": title, "url": link, "meta": pub, "range": range_key, "score": score}))
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    positive = [item for score, _, item in ranked if score > 0]
    signals = positive[:SIGNALS_PER_SOURCE]
    if not signals and ranked:
        warnings.append("No strongly relevant Google topic signals found for this site topic and period.")
    return signals, warnings


def fetch_reddit_signals(site, range_key):
    query = site_topic_seed(site)
    reddit_t = timeframe_to_reddit(range_key)
    warnings = []
    if range_key in {"3m", "6m"}:
        warnings.append("Reddit RSS supports week/month/year buckets; using year bucket for this range.")
    url = "https://www.reddit.com/search.rss?" + urllib.parse.urlencode({"q": query, "sort": "top", "t": reddit_t})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BlogCoreTopicDiscovery/1.0 (+https://blog.yas.ooo)"})
        with urllib.request.urlopen(req, timeout=18) as resp:
            xml = resp.read(1200000).decode("utf-8", errors="replace")
        root = ET.fromstring(xml)
    except Exception as e:
        return [], [f"Reddit temporarily unavailable: {e}"]

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    signals = []
    seen = set()
    for entry in root.findall("atom:entry", ns)[:80]:
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        link_node = entry.find("atom:link", ns)
        link = link_node.attrib.get("href", "") if link_node is not None else ""
        updated = (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip()
        if not title or "/comments/" not in link:
            continue
        key = (title.lower(), link)
        if key in seen:
            continue
        seen.add(key)
        score = signal_relevance_score(title, query)
        if score <= 0:
            continue
        signals.append({"source": "reddit", "title": title, "url": link, "meta": updated, "range": range_key, "score": score})
        if len(signals) >= SIGNALS_PER_SOURCE:
            break
    if not signals:
        warnings.append("No relevant Reddit top discussions found for this site topic and period.")
    return signals, warnings

def generate_article_ideas(site, signals):
    seed = site_topic_seed(site)
    brand = site["brand_name"] or site["domain"]
    ideas = []
    for signal in signals[:12]:
        title = re.sub(r"\s+", " ", signal.get("title", "")).strip()
        if not title or signal.get("disabled"):
            continue
        ideas.append({
            "title": title,
            "angle": f"Use this signal as the hook, answer the underlying buyer or reader question, then connect the solution to {brand}'s offer, expertise, or editorial point of view around {seed}.",
            "source": signal.get("source"),
            "source_title": title,
            "source_url": signal.get("url", ""),
        })
    return ideas


def _parse_json_text(text):
    raw = (text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start:end + 1]
    return json.loads(raw)


def _gemini_text_json(prompt):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    model = os.environ.get("GEMINI_TEXT_MODEL") or os.environ.get("GEMINI_MODEL_TEXT") or os.environ.get("GEMINI_MODEL") or "gemini-3.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.55},
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response: {data}")
    return _parse_json_text(text)


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
- Output STRICT JSON only.
- Write like a specialist editor for this exact site, not a generic AI assistant.
- Start contentHtml with a practical lead paragraph before the first H2.
- Use 6-10 H2 sections; at least half should answer concrete buyer/reader questions.
- Include at least one table, one ordered list, and one blockquote.
- Include 5-7 FAQ items.
- Include exactly 3 image placeholders as <figure><img src="filename.jpg" alt="..." /><figcaption>...</figcaption></figure>.
- Image src must be filename only, not absolute URL.
- Include natural internal links only to URLs that are safe for this site: homepage, blog path, and existing canonical paths if provided in source context. Do not invent product claims.
- No markdown. HTML fragment only in contentHtml.
- No em dash, no en dash, no asterisks, no smart quotes.
- Avoid fluff and vague marketing language.
- Make the article clearly connect the problem/question to why {brand} is useful, but do not turn every section into an ad.

RETURN JSON SHAPE:
{{
  "slug": "lowercase-url-slug",
  "title": "specific article title",
  "description": "155-160 character meta description as a complete thought",
  "category": "category",
  "heroImage": "filename.jpg",
  "contentHtml": "HTML fragment",
  "faq": [{{"question":"...","answer":"..."}}]
}}
""".strip()


def generate_content_job(site_id, job_id):
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        job = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
        if not site or not job:
            raise KeyError("job not found")
        conn.execute("update content_jobs set status='GENERATING', error=NULL, updated_at=? where site_id=? and id=?", (now_iso(), site_id, job_id))
        conn.execute("insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)", (site_id, job_id, now_iso(), "INFO", "generate", "Starting article draft generation"))
    try:
        draft = _gemini_text_json(build_universal_article_prompt(site, job))
        slug = simple_slug(draft.get("slug") or draft.get("title") or job["topic"])
        faq = draft.get("faq") if isinstance(draft.get("faq"), list) else []
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
                    draft.get("heroImage") or f"{slug}-hero.jpg",
                    draft.get("contentHtml") or "",
                    json.dumps(faq, ensure_ascii=False),
                    now_iso(),
                    site_id,
                    job_id,
                ),
            )
            conn.execute("insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)", (site_id, job_id, now_iso(), "INFO", "generate", "Draft generated"))
        return {"ok": True, "jobId": job_id, "status": "DRAFT", "slug": slug}
    except Exception as e:
        with db() as conn:
            conn.execute("update content_jobs set status='ERROR', error=?, updated_at=? where site_id=? and id=?", (str(e), now_iso(), site_id, job_id))
            conn.execute("insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)", (site_id, job_id, now_iso(), "ERROR", "generate", str(e)))
        raise


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
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'  <url><loc>{base}/blog/</loc></url>\n'
            f'  <url><loc>{base}/blog/visual-chaos-in-ai-product-cards/</loc></url>\n'
            '</urlset>\n'
        )
        return Response(xml, mimetype="application/xml")
    if path in ("", "blog"):
        html = render_blog_index(brand, header, footer, "/blog-core.css", source_css, source_css_urls)
        return Response(html, mimetype="text/html")
    if path in ("blog/visual-chaos-in-ai-product-cards", "visual-chaos-in-ai-product-cards"):
        html = render_sample_article(brand, header, footer, "/blog-core.css", source_css, source_css_urls)
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
        sites = conn.execute("select s.*, p.scanned_at, t.preview_path from sites s left join site_theme_profiles p on p.site_id=s.id left join blog_templates t on t.site_id=s.id order by s.updated_at desc").fetchall()
    rows = "".join(render_site_row(s) for s in sites) or "<div class='empty'>No sites connected yet.</div>"
    return DASHBOARD_HTML.replace("__ROWS__", rows)


def render_site_row(s):
    preview = f"<a class='btn ghost' target='_blank' href='{escape(s['preview_path'])}'>Open preview</a>" if s["preview_path"] else "<span class='muted'>No preview</span>"
    scanned = escape(s["scanned_at"] or "Not scanned")
    return f"""
<div class="site-card">
  <div>
    <div class="site-domain">{escape(s['domain'])}</div>
    <div class="site-url">{escape(s['homepage_url'])}</div>
    <div class="site-meta">root: {escape(s['root_path'] or 'not set')} · scanned: {scanned}</div>
  </div>
  <div class="actions">
    <a class="btn ghost" href="/sites/{s['id']}">Manage</a>
    <button onclick="runAction({s['id']}, 'scan')">Scan design</button>
    <button onclick="runAction({s['id']}, 'bootstrap-preview')">Build preview</button>
    <button onclick="runAction({s['id']}, 'install-blog')">Install /blog</button>
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


@app.get("/api/sites/<int:site_id>/topic-signals")
def topic_signals(site_id):
    site = get_site(site_id)
    if not site:
        return jsonify({"error": "site not found"}), 404
    range_key = request.args.get("range") or "week"
    if range_key not in {"week", "month", "3m", "6m"}:
        range_key = "week"
    google, google_warnings = fetch_google_trend_signals(site, range_key)
    reddit, reddit_warnings = fetch_reddit_signals(site, range_key)
    signals = google + reddit
    return jsonify({
        "ok": True,
        "range": range_key,
        "query": site_topic_seed(site),
        "signals": signals,
        "warnings": google_warnings + reddit_warnings,
        "counts": {"google": len(google), "reddit": len(reddit), "total": len(signals)},
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
    ideas = generate_article_ideas(site, signals)
    if not ideas:
        return jsonify({"error": "no usable selected signals"}), 400
    message = json.dumps({"range": payload.get("range") or "week", "signals": signals, "ideas": ideas}, ensure_ascii=False)
    created_jobs = []
    with db() as conn:
        conn.execute(
            "insert into publish_jobs(site_id,kind,status,message,created_at) values(?,?,?,?,?)",
            (site_id, "article-ideas", "queued", message, now_iso()),
        )
        for idea in ideas:
            title = idea.get("title") or "Article idea"
            job_id = secrets.token_hex(12)
            slug = simple_slug(title)
            now = now_iso()
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
                    "Article Ideas",
                    json.dumps(idea, ensure_ascii=False),
                    "public",
                    now,
                    now,
                ),
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (site_id, job_id, now, "INFO", "queue", "Created from selected topic signal"),
            )
            created_jobs.append({"id": job_id, "title": title, "slug": slug})
    return jsonify({"ok": True, "ideas": ideas, "jobs": created_jobs})


@app.get("/api/sites/<int:site_id>/factory-settings")
def get_factory_settings(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    auto = get_autopublish_settings(site_id)
    disc = get_topic_discovery_settings(site_id)
    social = get_social_connections(site_id)
    return jsonify({
        "ok": True,
        "autopublish": dict(auto),
        "topicDiscovery": dict(disc),
        "social": {k: (dict(v) if v else {"provider": k, "status": "disconnected"}) for k, v in social.items()},
    })


@app.put("/api/sites/<int:site_id>/factory-settings")
def update_factory_settings(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    payload = request.get_json(silent=True) or {}
    channels = payload.get("channels") or []
    if not isinstance(channels, list):
        channels = []
    allowed_channels = [c for c in channels if c in {"linkedin", "telegram", "twitter", "tumblr"}]
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
                linkedin_include_link, telegram_include_link, twitter_include_link, tumblr_include_link, updated_at
            ) values(?,?,?,?,?,?,?,?,?,?,?,?)
            on conflict(site_id) do update set
                enabled=excluded.enabled, times_per_day=excluded.times_per_day, channels_json=excluded.channels_json,
                timezone=excluded.timezone, start_hour=excluded.start_hour, end_hour=excluded.end_hour,
                linkedin_include_link=excluded.linkedin_include_link, telegram_include_link=excluded.telegram_include_link,
                twitter_include_link=excluded.twitter_include_link, tumblr_include_link=excluded.tumblr_include_link,
                updated_at=excluded.updated_at
            """,
            (
                site_id,
                1 if auto.get("enabled") else 0,
                int(auto.get("timesPerDay") or 3),
                json.dumps(allowed_channels or ["linkedin", "telegram", "twitter", "tumblr"]),
                auto.get("timezone") or "UTC",
                int(auto.get("startHour") or 9),
                int(auto.get("endHour") or 21),
                1 if auto.get("linkedinIncludeLink") else 0,
                1 if auto.get("telegramIncludeLink") else 0,
                1 if auto.get("twitterIncludeLink") else 0,
                1 if auto.get("tumblrIncludeLink") else 0,
                now,
            ),
        )
    return jsonify({"ok": True})


@app.get("/api/sites/<int:site_id>/content-jobs")
def list_content_jobs(site_id):
    if not get_site(site_id):
        return jsonify({"error": "site not found"}), 404
    return jsonify({"ok": True, "jobs": [dict(r) for r in get_content_jobs(site_id)]})


@app.get("/api/sites/<int:site_id>/content-jobs/<job_id>")
def get_content_job(site_id, job_id):
    with db() as conn:
        row = conn.execute("select * from content_jobs where site_id=? and id=?", (site_id, job_id)).fetchone()
        logs = conn.execute("select * from content_job_logs where site_id=? and job_id=? order by ts asc", (site_id, job_id)).fetchall()
    if not row:
        return jsonify({"error": "job not found"}), 404
    return jsonify({"ok": True, "job": dict(row), "logs": [dict(r) for r in logs]})


@app.post("/api/sites/<int:site_id>/content-jobs/<job_id>/generate")
def generate_content_job_route(site_id, job_id):
    try:
        return jsonify(generate_content_job(site_id, job_id))
    except KeyError:
        return jsonify({"error": "job not found"}), 404
    except Exception as e:
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
        return jsonify({"ok": True, "theme": theme})
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
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 0,#3b1a75 0,transparent 38%),radial-gradient(circle at 78% 15%,#0d7a65 0,transparent 28%),#0b1020;color:var(--text);min-height:100vh}a{color:inherit}.shell{max-width:1180px;margin:0 auto;padding:38px 22px 90px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}.top-actions{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;justify-content:flex-end}.site-switcher{display:flex;flex-direction:column;gap:6px;min-width:260px}.site-switcher span{font-size:12px;color:#d8cdfd;text-transform:uppercase;letter-spacing:.08em;font-weight:900}.site-switcher select{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.75);color:#fff;padding:13px 14px;font-size:14px;outline:none}.back{color:#d8cdfd;text-decoration:none;font-weight:900}.title{font-size:clamp(36px,5vw,64px);letter-spacing:-.05em;line-height:.95;margin:14px 0 8px}.sub,.muted{color:var(--muted);font-size:14px;line-height:1.5}.grid{display:grid;grid-template-columns:1fr;gap:18px}.settings-head{display:flex;justify-content:space-between;gap:16px;align-items:center}.settings-toggle{width:48px;height:48px;border-radius:999px;font-size:22px;padding:0}.settings-panel[hidden]{display:none}.compact-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:18px}.signal-toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 18px}.signal-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.signal-card{display:grid;grid-template-columns:auto 1fr;gap:10px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.45);padding:14px}.signal-card input{width:18px;height:18px;margin-top:2px}.signal-card strong{display:block;font-size:15px;line-height:1.25}.signal-card span{display:block;color:var(--muted);font-size:12px;margin-top:5px}.source-pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:4px 8px;margin-bottom:7px;color:#d8cdfd;font-size:11px;font-weight:900;text-transform:uppercase}.loading{color:var(--muted);padding:18px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.38)}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.11),rgba(255,255,255,.06));box-shadow:0 22px 90px rgba(0,0,0,.32);backdrop-filter:blur(22px);border-radius:24px;padding:22px;margin:18px 0}.panel h2{margin:0 0 14px;font-size:22px;letter-spacing:-.03em}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.field.full{grid-column:1 / -1}.field label{display:block;font-size:12px;color:#d8cdfd;text-transform:uppercase;letter-spacing:.08em;font-weight:900;margin:0 0 7px}.field input,.field textarea,.field select{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.55);color:#fff;padding:13px 14px;font-size:14px;outline:none}.field textarea{min-height:108px;resize:vertical}.hint{color:var(--muted);font-size:12px;margin-top:6px}.field input:focus,.field textarea:focus,.field select:focus{border-color:rgba(139,92,246,.9);box-shadow:0 0 0 4px rgba(139,92,246,.18)}.check{display:flex;align-items:center;gap:10px;padding:12px 0;color:#fff;font-weight:800}.check input{width:18px;height:18px}.actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.btn,button{border:0;border-radius:14px;background:linear-gradient(135deg,#8b5cf6,#22c55e);color:#fff;font-weight:900;padding:13px 16px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;min-height:42px}.btn.ghost,button.ghost{background:rgba(255,255,255,.08);border:1px solid var(--line)}.danger{background:rgba(239,68,68,.16);border:1px solid rgba(239,68,68,.45);color:#fecaca}.stat{border:1px solid var(--line);border-radius:18px;background:rgba(8,13,29,.48);padding:16px;margin-top:12px}.stat strong{display:block;font-size:15px;margin-bottom:6px}.swatches{display:flex;gap:7px;flex-wrap:wrap}.swatch{display:inline-block;width:28px;height:28px;border-radius:999px;border:1px solid rgba(255,255,255,.35)}.job-row{display:grid;grid-template-columns:1fr auto;gap:8px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.45);padding:14px;margin-top:10px}.job-row span{display:block;color:var(--muted);font-size:12px;margin-top:3px}.production-panel{border-color:rgba(139,92,246,.35)}.panel-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.channel-checks{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.check.compact{padding:10px 12px;border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.38)}.channel-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.channel-card{border:1px solid var(--line);border-radius:14px;background:rgba(8,13,29,.45);padding:12px}.channel-card strong{display:block}.channel-card span{display:block;color:var(--muted);font-size:12px;margin-top:4px}.social-statuses{grid-column:1 / -1;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.social-statuses span{border:1px solid var(--line);border-radius:999px;padding:6px 8px;background:rgba(255,255,255,.06)}.job-row p{grid-column:1 / -1;margin:0;color:var(--muted);font-size:13px;word-break:break-word}.status{border-radius:999px;padding:6px 9px;background:rgba(255,255,255,.1);font-size:12px}.status.completed{background:rgba(34,197,94,.18);color:#bbf7d0}.status.failed{background:rgba(239,68,68,.18);color:#fecaca}.status.queued{background:rgba(139,92,246,.18);color:#ddd6fe}.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111827;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:16px;padding:14px 18px;box-shadow:0 20px 80px rgba(0,0,0,.4);display:none;max-width:min(720px,calc(100vw - 32px));z-index:10}.toast.show{display:block}@media(max-width:900px){.top,.grid,.compact-grid{display:block}.channel-checks,.channel-grid,.social-statuses{grid-template-columns:1fr}.top-actions{justify-content:flex-start;margin-top:18px}.site-switcher{min-width:0;width:100%}.form-grid,.signal-list{grid-template-columns:1fr}.shell{padding:28px 16px 70px}}
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

  <section class="panel">
    <div class="settings-head">
      <div>
        <h2 style="margin:0">Site factory</h2>
        <div class="muted">Topic discovery, article ideas, publishing jobs, and blog settings for this site.</div>
      </div>
      <button class="settings-toggle ghost" type="button" onclick="toggleSettings()" aria-label="Open settings">⚙</button>
    </div>
    <div id="settingsPanel" class="settings-panel" hidden>
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
    </div>
  </section>

  <section class="panel production-panel">
    <h2>Article production queue</h2>
    <div class="muted">Generated article jobs, publish state, and social channel status for this site.</div>
    __CONTENT_JOBS__
  </section>

  __DISTRIBUTION_SETTINGS__

  <section class="panel">
    <h2 style="margin:0">Google Trends and Reddit discussions</h2>
    <div class="muted">Choose live signals related to this site's topic, then generate article ideas from them.</div>
    <div class="signal-toolbar">
      <button class="ghost" data-range="week" onclick="loadSignals('week')">Last week</button>
      <button class="ghost" data-range="month" onclick="loadSignals('month')">Month</button>
      <button class="ghost" data-range="3m" onclick="loadSignals('3m')">3 months</button>
      <button class="ghost" data-range="6m" onclick="loadSignals('6m')">6 months</button>
      <button onclick="createIdeasFromSignals()">Create article ideas</button>
    </div>
    <div id="signalQuery" class="muted"></div>
    <div id="signals" class="loading">Loading topic signals...</div>
  </section>

  <section class="panel">
    <h2>Factory jobs</h2>
    __JOBS__
  </section>
</main>
<div id="toast" class="toast"></div>
<script>
const SITE_ID=__SITE_ID__;let currentSignals=[];let currentRange='week';
function showToast(text){const toast=document.getElementById('toast');toast.textContent=text;toast.className='toast show';}
function toggleSettings(){const panel=document.getElementById('settingsPanel');panel.hidden=!panel.hidden;}
async function runAction(id, action){showToast('Running '+action+'...');try{const res=await fetch('/api/sites/'+id+'/'+action,{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast(action+' completed');setTimeout(()=>location.reload(),700);}catch(e){showToast(action+' failed: '+e.message);}}
async function queueTopicPlan(id){showToast('Queueing topic plan...');try{const res=await fetch('/api/sites/'+id+'/queue-topic-plan',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Topic plan queued');setTimeout(()=>location.reload(),700);}catch(e){showToast('Queue failed: '+e.message);}}
async function checkCname(id){showToast('Checking CNAME...');try{const res=await fetch('/api/sites/'+id+'/check-cname',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('CNAME status: '+data.status);setTimeout(()=>location.reload(),900);}catch(e){showToast('CNAME check failed: '+e.message);}}
async function deleteSite(id, domain){if(!confirm('Remove '+domain+' from Blog Core? Installed /blog files on the site will not be deleted.')) return;showToast('Deleting '+domain+'...');try{const res=await fetch('/api/sites/'+id+'/delete',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);location.href='/';}catch(e){showToast('Delete failed: '+e.message);}}
function sourceLabel(source){return source==='google_trends'?'Google topic signals':'Reddit top discussions';}
function renderSignals(items){const box=document.getElementById('signals');currentSignals=(items||[]).filter(item=>!item.disabled);if(!currentSignals.length){box.className='loading';box.textContent='No usable signals found for this site topic.';return;}box.className='signal-list';box.innerHTML=currentSignals.map((item,index)=>`<label class="signal-card"><input type="checkbox" data-index="${index}"><div><em class="source-pill">${sourceLabel(item.source)}</em><strong>${item.title}</strong><span>${item.meta||''}</span></div></label>`).join('');}
async function loadSignals(range){currentRange=range||'week';const box=document.getElementById('signals');box.className='loading';box.textContent='Loading Google topic signals and Reddit top discussions...';try{const res=await fetch('/api/sites/'+SITE_ID+'/topic-signals?range='+encodeURIComponent(currentRange));const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);const counts=data.counts||{};const warnings=(data.warnings||[]).length?' · Notes: '+data.warnings.join(' · '):'';document.getElementById('signalQuery').textContent='Topic query: '+data.query+' · range: '+data.range+' · signals: '+(counts.total??(data.signals||[]).length)+warnings;renderSignals(data.signals);}catch(e){box.className='loading';box.textContent='Topic discovery failed: '+e.message;}}
async function createIdeasFromSignals(){const selected=[...document.querySelectorAll('#signals input[type="checkbox"]:checked')].map(input=>currentSignals[Number(input.dataset.index)]).filter(Boolean);if(!selected.length){showToast('Select at least one trend or discussion');return;}showToast('Creating article jobs...');try{const res=await fetch('/api/sites/'+SITE_ID+'/article-ideas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({range:currentRange,signals:selected})});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Article jobs queued: '+(data.jobs||[]).length);setTimeout(()=>location.reload(),900);}catch(e){showToast('Article ideas failed: '+e.message);}}
async function generateArticleJob(jobId){showToast('Generating draft...');try{const res=await fetch('/api/sites/'+SITE_ID+'/content-jobs/'+encodeURIComponent(jobId)+'/generate',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Draft generated: '+(data.slug||jobId));setTimeout(()=>location.reload(),900);}catch(e){showToast('Generation failed: '+e.message);}}
async function saveFactorySettings(event){event.preventDefault();const form=event.currentTarget;const fd=new FormData(form);const channels=fd.getAll('channels');const body={channels,topicDiscovery:{enabled:fd.has('discovery_enabled'),direction:fd.get('direction')||'',categoryHint:fd.get('category_hint')||'',perRunLimit:Number(fd.get('per_run_limit')||15),topN:Number(fd.get('top_n')||3),timezone:fd.get('timezone')||'UTC'},autopublish:{enabled:fd.has('autopublish_enabled'),timesPerDay:Number(fd.get('times_per_day')||3),timezone:fd.get('timezone')||'UTC',startHour:Number(fd.get('start_hour')||9),endHour:Number(fd.get('end_hour')||21),linkedinIncludeLink:fd.has('linkedin_include_link'),telegramIncludeLink:fd.has('telegram_include_link'),twitterIncludeLink:fd.has('twitter_include_link'),tumblrIncludeLink:fd.has('tumblr_include_link')}};showToast('Saving factory settings...');try{const res=await fetch('/api/sites/'+SITE_ID+'/factory-settings',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Factory settings saved');setTimeout(()=>location.reload(),700);}catch(e){showToast('Save failed: '+e.message);}}
loadSignals('week');
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
*{box-sizing:border-box} body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 0,#3b1a75 0,transparent 38%),radial-gradient(circle at 78% 15%,#0d7a65 0,transparent 28%),#0b1020;color:var(--text);min-height:100vh} a{color:inherit}.shell{max-width:1180px;margin:0 auto;padding:44px 22px 90px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:28px}.title{font-size:clamp(42px,7vw,78px);letter-spacing:-.055em;line-height:.92;margin:0}.sub{color:var(--muted);font-size:18px;line-height:1.55;max-width:720px;margin:18px 0 0}.badge{border:1px solid var(--line);background:rgba(255,255,255,.07);border-radius:999px;padding:10px 14px;color:#d8cdfd;font-weight:800;white-space:nowrap}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.11),rgba(255,255,255,.06));box-shadow:0 22px 90px rgba(0,0,0,.32);backdrop-filter:blur(22px);border-radius:24px;padding:22px;margin:18px 0}.form{display:grid;grid-template-columns:1.2fr 1fr 1fr auto;gap:12px}.form input{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.55);color:#fff;padding:14px 15px;font-size:14px;outline:none}.form input:focus{border-color:rgba(139,92,246,.9);box-shadow:0 0 0 4px rgba(139,92,246,.18)}button,.btn{border:0;border-radius:14px;background:linear-gradient(135deg,#8b5cf6,#22c55e);color:#fff;font-weight:900;padding:13px 16px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;min-height:42px}.btn.ghost{background:rgba(255,255,255,.08);border:1px solid var(--line)}.site-card{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;border:1px solid var(--line);border-radius:20px;background:rgba(8,13,29,.58);padding:18px;margin-top:14px}.site-domain{font-size:22px;font-weight:900;letter-spacing:-.02em}.site-url,.site-meta,.muted{color:var(--muted);font-size:13px;margin-top:5px}.actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}.actions button{background:rgba(255,255,255,.1);border:1px solid var(--line)}.actions .danger{background:rgba(239,68,68,.16);border-color:rgba(239,68,68,.45);color:#fecaca}.empty{color:var(--muted);padding:26px;text-align:center}.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111827;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:16px;padding:14px 18px;box-shadow:0 20px 80px rgba(0,0,0,.4);display:none;max-width:min(720px,calc(100vw - 32px));z-index:10}.toast.show{display:block}@media(max-width:900px){.top,.site-card{display:block}.form{grid-template-columns:1fr}.actions{justify-content:flex-start;margin-top:16px}.badge{display:inline-block;margin-top:18px}}
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
