import json
import os
import re
import shutil
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
        ):
            try:
                conn.execute(statement)
            except sqlite3.OperationalError:
                pass


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


def render_manage_site_page(site):
    jobs = render_jobs(get_site_jobs(site["id"]))
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
    )


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
            set domain=?, homepage_url=?, root_path=?, blog_path=?, languages=?, brand_name=?,
                content_context=?, factory_enabled=?, publishing_cadence=?, topic_strategy=?, updated_at=?
            where id=?
            """,
            (
                domain,
                homepage,
                payload.get("root_path") or "",
                payload.get("blog_path") or "/blog/",
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


MANAGE_SITE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manage __DOMAIN__ · Blog Core</title>
<style>
:root{--bg:#0b1020;--panel:rgba(255,255,255,.08);--line:rgba(255,255,255,.15);--text:#f8fafc;--muted:#a6b0c3;--accent:#8b5cf6;--accent2:#22c55e;--danger:#ef4444}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 0,#3b1a75 0,transparent 38%),radial-gradient(circle at 78% 15%,#0d7a65 0,transparent 28%),#0b1020;color:var(--text);min-height:100vh}a{color:inherit}.shell{max-width:1180px;margin:0 auto;padding:38px 22px 90px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}.back{color:#d8cdfd;text-decoration:none;font-weight:900}.title{font-size:clamp(36px,5vw,64px);letter-spacing:-.05em;line-height:.95;margin:14px 0 8px}.sub,.muted{color:var(--muted);font-size:14px;line-height:1.5}.grid{display:grid;grid-template-columns:1.05fr .95fr;gap:18px}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.11),rgba(255,255,255,.06));box-shadow:0 22px 90px rgba(0,0,0,.32);backdrop-filter:blur(22px);border-radius:24px;padding:22px;margin:18px 0}.panel h2{margin:0 0 14px;font-size:22px;letter-spacing:-.03em}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.field.full{grid-column:1 / -1}.field label{display:block;font-size:12px;color:#d8cdfd;text-transform:uppercase;letter-spacing:.08em;font-weight:900;margin:0 0 7px}.field input,.field textarea,.field select{width:100%;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,18,.55);color:#fff;padding:13px 14px;font-size:14px;outline:none}.field textarea{min-height:108px;resize:vertical}.field input:focus,.field textarea:focus,.field select:focus{border-color:rgba(139,92,246,.9);box-shadow:0 0 0 4px rgba(139,92,246,.18)}.check{display:flex;align-items:center;gap:10px;padding:12px 0;color:#fff;font-weight:800}.check input{width:18px;height:18px}.actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.btn,button{border:0;border-radius:14px;background:linear-gradient(135deg,#8b5cf6,#22c55e);color:#fff;font-weight:900;padding:13px 16px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;min-height:42px}.btn.ghost,button.ghost{background:rgba(255,255,255,.08);border:1px solid var(--line)}.danger{background:rgba(239,68,68,.16);border:1px solid rgba(239,68,68,.45);color:#fecaca}.stat{border:1px solid var(--line);border-radius:18px;background:rgba(8,13,29,.48);padding:16px;margin-top:12px}.stat strong{display:block;font-size:15px;margin-bottom:6px}.swatches{display:flex;gap:7px;flex-wrap:wrap}.swatch{display:inline-block;width:28px;height:28px;border-radius:999px;border:1px solid rgba(255,255,255,.35)}.job-row{display:grid;grid-template-columns:1fr auto;gap:8px;border:1px solid var(--line);border-radius:16px;background:rgba(8,13,29,.45);padding:14px;margin-top:10px}.job-row span{display:block;color:var(--muted);font-size:12px;margin-top:3px}.job-row p{grid-column:1 / -1;margin:0;color:var(--muted);font-size:13px;word-break:break-word}.status{border-radius:999px;padding:6px 9px;background:rgba(255,255,255,.1);font-size:12px}.status.completed{background:rgba(34,197,94,.18);color:#bbf7d0}.status.failed{background:rgba(239,68,68,.18);color:#fecaca}.status.queued{background:rgba(139,92,246,.18);color:#ddd6fe}.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111827;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:16px;padding:14px 18px;box-shadow:0 20px 80px rgba(0,0,0,.4);display:none;max-width:min(720px,calc(100vw - 32px));z-index:10}.toast.show{display:block}@media(max-width:900px){.top,.grid{display:block}.form-grid{grid-template-columns:1fr}.shell{padding:28px 16px 70px}}
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
    <div class="actions">__PREVIEW__</div>
  </section>

  <div class="grid">
    <section class="panel">
      <h2>Site setup</h2>
      <form method="post" action="/sites/__SITE_ID__/settings" class="form-grid">
        <div class="field full"><label>Homepage URL</label><input name="homepage_url" value="__HOMEPAGE__" required></div>
        <div class="field"><label>Brand name</label><input name="brand_name" value="__BRAND__"></div>
        <div class="field"><label>Blog path</label><input name="blog_path" value="__BLOG_PATH__"></div>
        <div class="field full"><label>Local webroot</label><input name="root_path" value="__ROOT__" placeholder="/var/www/site-root"></div>
        <div class="field"><label>Languages</label><input name="languages" value="__LANGUAGES__" placeholder="en, ru, de"></div>
        <div class="field"><label>Publishing cadence</label><select name="publishing_cadence">__CADENCE_OPTIONS__</select></div>
        <div class="field full"><label>Site/product context</label><textarea name="content_context" placeholder="What this site sells, audience, positioning, internal links...">__CONTENT_CONTEXT__</textarea></div>
        <div class="field full"><label>Topic strategy</label><textarea name="topic_strategy" placeholder="Topics, clusters, tone, forbidden claims, CTA rules...">__TOPIC_STRATEGY__</textarea></div>
        <label class="check full"><input type="checkbox" name="factory_enabled" __FACTORY_CHECKED__> Enable article factory for this site</label>
        <div class="actions full"><button type="submit">Save settings</button></div>
      </form>
    </section>

    <section class="panel">
      <h2>Design and publishing</h2>
      <div class="actions">
        <button onclick="runAction(__SITE_ID__, 'scan')">Scan design</button>
        <button onclick="runAction(__SITE_ID__, 'bootstrap-preview')">Build preview</button>
        <button onclick="runAction(__SITE_ID__, 'install-blog')">Install /blog</button>
        <button class="ghost" onclick="queueTopicPlan(__SITE_ID__)">Queue topic plan</button>
      </div>
      <div class="stat"><strong>Last scan</strong><div class="muted">__SCANNED_AT__</div><div class="muted">__SCANNED_TITLE__</div></div>
      <div class="stat"><strong>Captured design</strong><div class="muted">__CSS_COUNT__ stylesheets · __FONTS__</div><div class="swatches">__SWATCHES__</div></div>
      <div class="stat"><strong>Delete connected site</strong><div class="muted">Removes it from Blog Core and deletes generated previews only. It does not remove installed /blog files from the target webroot.</div><div style="margin-top:12px"><button class="danger" onclick="deleteSite(__SITE_ID__, '__DOMAIN__')">Delete from dashboard</button></div></div>
    </section>
  </div>

  <section class="panel">
    <h2>Factory jobs</h2>
    __JOBS__
  </section>
</main>
<div id="toast" class="toast"></div>
<script>
function showToast(text){const toast=document.getElementById('toast');toast.textContent=text;toast.className='toast show';}
async function runAction(id, action){showToast('Running '+action+'...');try{const res=await fetch('/api/sites/'+id+'/'+action,{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast(action+' completed');setTimeout(()=>location.reload(),700);}catch(e){showToast(action+' failed: '+e.message);}}
async function queueTopicPlan(id){showToast('Queueing topic plan...');try{const res=await fetch('/api/sites/'+id+'/queue-topic-plan',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);showToast('Topic plan queued');setTimeout(()=>location.reload(),700);}catch(e){showToast('Queue failed: '+e.message);}}
async function deleteSite(id, domain){if(!confirm('Remove '+domain+' from Blog Core? Installed /blog files on the site will not be deleted.')) return;showToast('Deleting '+domain+'...');try{const res=await fetch('/api/sites/'+id+'/delete',{method:'POST'});const data=await res.json();if(!res.ok) throw new Error(data.error||res.statusText);location.href='/';}catch(e){showToast('Delete failed: '+e.message);}}
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
