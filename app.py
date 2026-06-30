import json
import os
import re
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PREVIEW_DIR = BASE_DIR / "previews"
DB_PATH = DATA_DIR / "blog_core.sqlite3"
PORT = int(os.environ.get("PORT", "3299"))

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


class HeadBodyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.title = ""
        self.description = ""
        self.css_urls = []
        self.body_class = ""
        self._in_title = False
        self._capture = None
        self._depth = 0
        self._chunks = []
        self.header_html = ""
        self.footer_html = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "")[:300]
        if tag == "link" and attrs_dict.get("rel") and "stylesheet" in str(attrs_dict.get("rel")):
            href = attrs_dict.get("href")
            if href:
                self.css_urls.append(href)
        if tag == "body":
            self.body_class = attrs_dict.get("class", "")
        if tag in ("header", "footer") and self._capture is None:
            self._capture = tag
            self._depth = 0
            self._chunks = []
        if self._capture:
            self._depth += 1
            self._chunks.append(self._format_start(tag, attrs))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self._capture:
            self._chunks.append(f"</{tag}>")
            self._depth -= 1
            if self._depth == 0:
                html = "".join(self._chunks)
                if self._capture == "header" and not self.header_html:
                    self.header_html = html
                if self._capture == "footer" and not self.footer_html:
                    self.footer_html = html
                self._capture = None
                self._chunks = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
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
        "header_html": parser.header_html[:50000],
        "footer_html": parser.footer_html[:50000],
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
.blog-core-page {{font-family: var(--blog-font); color: var(--blog-text); background: #fff;}}
.blog-core-wrap {{max-width: 1120px; margin: 0 auto; padding: 64px 24px;}}
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
@media (max-width: 820px) {{.blog-core-grid{{grid-template-columns:1fr;}} .blog-core-wrap{{padding:42px 18px;}}}}
""".strip()


def render_shell(title, header, footer, body, css_href="/blog/blog-core.css"):
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{escape(title)}</title>
<link rel=\"stylesheet\" href=\"{escape(css_href, quote=True)}\">
</head>
<body class=\"blog-core-page\">
{header}
{body}
{footer}
</body>
</html>
"""


def render_blog_index(brand, header, footer, css_href="/blog/blog-core.css"):
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
    return render_shell(f"Blog - {brand}", header, footer, body, css_href)


def render_sample_article(brand, header, footer, css_href="/blog/blog-core.css"):
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
    return render_shell(f"Visual chaos in AI product cards - {brand}", header, footer, body, css_href)


def build_preview(site, profile):
    site_id = site["id"]
    preview_root = PREVIEW_DIR / str(site_id) / "blog"
    article_root = preview_root / "visual-chaos-in-ai-product-cards"
    preview_root.mkdir(parents=True, exist_ok=True)
    article_root.mkdir(parents=True, exist_ok=True)
    css = theme_css(profile)
    header = profile["header_html"] if profile and profile["header_html"] else ""
    footer = profile["footer_html"] if profile and profile["footer_html"] else ""
    brand = site["brand_name"] or site["domain"]
    index_html = render_blog_index(brand, header, footer, "./blog-core.css")
    article_html = render_sample_article(brand, header, footer, "../blog-core.css")
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
    brand = site["brand_name"] or site["domain"]
    (blog_dir / "blog-core.css").write_text(css, encoding="utf-8")
    (blog_dir / "index.html").write_text(render_blog_index(brand, header, footer), encoding="utf-8")
    (article_dir / "index.html").write_text(render_sample_article(brand, header, footer), encoding="utf-8")
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
    with db() as conn:
        sites = conn.execute("select s.*, p.scanned_at, t.preview_path from sites s left join site_theme_profiles p on p.site_id=s.id left join blog_templates t on t.site_id=s.id order by s.updated_at desc").fetchall()
    rows = "".join(render_site_row(s) for s in sites) or "<div class='empty'>No sites connected yet.</div>"
    return DASHBOARD_HTML.replace("__ROWS__", rows)


def render_site_row(s):
    preview = f"<a class='btn ghost' target='_blank' href='{escape(s['preview_path'])}'>Open preview</a>" if s["preview_path"] else "<span class='muted'>No preview</span>"
    scanned = escape(s["scanned_at"] or "Not scanned")
    return f"""
<div class=\"site-card\">
  <div>
    <div class=\"site-domain\">{escape(s['domain'])}</div>
    <div class=\"site-url\">{escape(s['homepage_url'])}</div>
    <div class=\"site-meta\">root: {escape(s['root_path'] or 'not set')} · scanned: {scanned}</div>
  </div>
  <div class=\"actions\">
    <button onclick=\"runAction({s['id']}, 'scan')\">Scan design</button>
    <button onclick=\"runAction({s['id']}, 'bootstrap-preview')\">Build preview</button>
    <button onclick=\"runAction({s['id']}, 'install-blog')\">Install /blog</button>
    {preview}
  </div>
</div>
"""


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
            "insert into sites(domain, homepage_url, access_type, root_path, brand_name, content_context, created_at, updated_at) values(?,?,?,?,?,?,?,?) on conflict(domain) do update set homepage_url=excluded.homepage_url, root_path=excluded.root_path, brand_name=excluded.brand_name, content_context=excluded.content_context, updated_at=excluded.updated_at",
            (domain, homepage, payload.get("access_type") or "local_path", root_path, brand, payload.get("content_context") or "", now, now),
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
                "insert into site_theme_profiles(site_id,title,description,colors_json,fonts_json,css_urls_json,header_html,footer_html,body_class,scanned_at) values(?,?,?,?,?,?,?,?,?,?) on conflict(site_id) do update set title=excluded.title, description=excluded.description, colors_json=excluded.colors_json, fonts_json=excluded.fonts_json, css_urls_json=excluded.css_urls_json, header_html=excluded.header_html, footer_html=excluded.footer_html, body_class=excluded.body_class, scanned_at=excluded.scanned_at",
                (site_id, theme["title"], theme["description"], json.dumps(theme["colors"]), json.dumps(theme["fonts"]), json.dumps(theme["css_urls"]), theme["header_html"], theme["footer_html"], theme["body_class"], now_iso()),
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


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog Core</title>
<style>
:root{--bg:#0b1020;--panel:rgba(255,255,255,.08);--line:rgba(255,255,255,.15);--text:#f8fafc;--muted:#a6b0c3;--accent:#8b5cf6;--accent2:#22c55e}
*{box-sizing:border-box} body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 0,#3b1a75 0,transparent 38%),radial-gradient(circle at 78% 15%,#0d7a65 0,transparent 28%),#0b1020;color:var(--text);min-height:100vh} a{color:inherit}.shell{max-width:1180px;margin:0 auto;padding:44px 22px 90px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:28px}.title{font-size:clamp(42px,7vw,78px);letter-spacing:-.055em;line-height:.92;margin:0}.sub{color:var(--muted);font-size:18px;line-height:1.55;max-width:720px;margin:18px 0 0}.badge{border:1px solid var(--line);background:rgba(255,255,255,.07);border-radius:999px;padding:10px 14px;color:#d8cdfd;font-weight:800;white-space:nowrap}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.11),rgba(255,255,255,.06));box-shadow:0 22px 90px rgba(0,0,0,.32);backdrop-filter:blur(22px);border-radius:24px;padding:22px;margin:18px 0}.form{display:grid;grid-template-columns:1.2fr 1fr 1fr auto;gap:12px}.form input{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.55);color:#fff;padding:14px 15px;font-size:14px;outline:none}.form input:focus{border-color:rgba(139,92,246,.9);box-shadow:0 0 0 4px rgba(139,92,246,.18)}button,.btn{border:0;border-radius:14px;background:linear-gradient(135deg,#8b5cf6,#22c55e);color:#fff;font-weight:900;padding:13px 16px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;min-height:42px}.btn.ghost{background:rgba(255,255,255,.08);border:1px solid var(--line)}.site-card{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;border:1px solid var(--line);border-radius:20px;background:rgba(8,13,29,.58);padding:18px;margin-top:14px}.site-domain{font-size:22px;font-weight:900;letter-spacing:-.02em}.site-url,.site-meta,.muted{color:var(--muted);font-size:13px;margin-top:5px}.actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}.actions button{background:rgba(255,255,255,.1);border:1px solid var(--line)}.empty{color:var(--muted);padding:26px;text-align:center}.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111827;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:16px;padding:14px 18px;box-shadow:0 20px 80px rgba(0,0,0,.4);display:none;max-width:min(720px,calc(100vw - 32px));z-index:10}.toast.show{display:block}@media(max-width:900px){.top,.site-card{display:block}.form{grid-template-columns:1fr}.actions{justify-content:flex-start;margin-top:16px}.badge{display:inline-block;margin-top:18px}}
</style>
</head>
<body>
<main class="shell">
  <section class="top">
    <div><h1 class="title">Universal Blog Core</h1><p class="sub">Connect any site, scan its public design, generate a matching /blog/ shell, then install it into the site root. This is the base for the future multi-site article factory dashboard.</p></div>
    <div class="badge">blog.yas.ooo · MVP</div>
  </section>
  <section class="panel">
    <form class="form" method="post" action="/api/sites">
      <input name="homepage_url" placeholder="Homepage URL, e.g. https://yas.wine/" required>
      <input name="brand_name" placeholder="Brand name">
      <input name="root_path" placeholder="Local webroot, e.g. /var/www/yaswine">
      <button type="submit">Connect site</button>
    </form>
  </section>
  <section class="panel">
    <h2 style="margin:0 0 8px;font-size:24px;letter-spacing:-.03em">Connected sites</h2>
    <div class="muted">Flow: Scan design → Build preview → Install /blog. Install only writes into the configured local root path.</div>
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
</script>
</body>
</html>"""


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT)
