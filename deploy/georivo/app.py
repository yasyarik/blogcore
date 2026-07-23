import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, abort, redirect


APP_ROOT = Path(__file__).resolve().parent
CONTENT_ROOT = APP_ROOT / "data" / "blog-core"
PUBLISHED_ROOT = CONTENT_ROOT / "published"
DRAFT_ROOT = CONTENT_ROOT / "drafts"
BLOG_CORE_ORIGIN = os.environ.get("BLOG_CORE_ORIGIN", "https://blog.yas.ooo").rstrip("/")
SITE_ORIGIN = "https://georivo.com"

app = Flask(__name__)


def esc(value):
    return html.escape(str(value or ""), quote=True)


def load_records(directory):
    records = []
    if not directory.exists():
        return records
    for path in directory.glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(record, dict):
            records.append(record)
    return sorted(
        records,
        key=lambda item: item.get("publishedAt") or item.get("updatedAt") or "",
        reverse=True,
    )


def load_record(directory, key, field):
    for record in load_records(directory):
        if str(record.get(field) or "") == key:
            return record
    return None


def absolute_article_assets(markup):
    return re.sub(
        r'(?P<attr>\b(?:src|href)=["\'])(?P<path>/sites/\d+/article-assets/)',
        rf"\g<attr>{BLOG_CORE_ORIGIN}\g<path>",
        markup or "",
        flags=re.I,
    )


def clean_article_markup(markup):
    cleaned = re.sub(r"(?is)<script\b[^>]*>.*?</script>", "", markup or "")
    cleaned = re.sub(r"(?is)<style\b[^>]*>.*?</style>", "", cleaned)
    return absolute_article_assets(cleaned)


def site_header():
    return """
    <header class="nav glass">
      <a class="brand" href="/" aria-label="Georivo home">
        <span class="brand-logo light" aria-hidden="true"><img src="/brand/georivo-on-light.png" alt=""></span>Georivo
      </a>
      <button class="menu-button" type="button" aria-label="Toggle navigation" aria-expanded="false">Menu</button>
      <nav class="nav-links" aria-label="Main navigation">
        <a href="/#movements">Examples</a>
        <a href="/#how">How it works</a>
        <a href="/#plans">Pricing</a>
        <a href="/blog/" aria-current="page">Blog</a>
        <a href="/login">Sign in</a>
        <a class="nav-cta" href="/#create">Create a widget <span>↗</span></a>
      </nav>
    </header>
    """


def site_footer():
    return """
    <footer id="footer">
      <div class="footer-top">
        <a class="brand" href="/">
          <span class="brand-logo dark" aria-hidden="true"><img src="/brand/georivo-on-dark.png" alt=""></span>Georivo
        </a>
        <p>Interactive 3D location stories,<br>embedded on real-estate websites.</p>
        <div class="footer-links">
          <div><b>Product</b><a href="/#movements">Examples</a><a href="/#how">How it works</a><a href="/#plans">Pricing</a><a href="/blog/">Blog</a></div>
          <div><b>Company</b><a href="/contact">Contact</a><a href="/terms">Terms</a><a href="/privacy">Privacy</a></div>
        </div>
      </div>
      <div class="footer-bottom"><span>© 2026 Georivo. All rights reserved.</span><span>3D visualization generated from available licensed geospatial imagery.</span></div>
    </footer>
    """


def schema_markup(payload):
    return '<script type="application/ld+json">' + json.dumps(payload, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def shell(title, description, body, canonical, schema=None, noindex=False):
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    structured = schema_markup(schema) if schema else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  {robots}
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="icon" href="/favicon.ico">
  <link rel="preload" as="image" href="/brand/georivo-on-light.png">
  <link rel="stylesheet" href="/assets/index-22jNjtDO.css">
  <link rel="stylesheet" href="/blog-assets/georivo-blog.css?v=20260723b">
  {structured}
</head>
<body class="blog-shell">
  {site_header()}
  {body}
  {site_footer()}
  <script src="/georivo-blog-nav.js?v=20260723c" defer></script>
</body>
</html>"""


def article_schema(record, canonical):
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": record.get("title") or "",
        "description": record.get("description") or "",
        "mainEntityOfPage": canonical,
        "author": {"@type": "Organization", "name": "Georivo"},
        "publisher": {"@type": "Organization", "name": "Georivo"},
        "dateModified": record.get("updatedAt") or datetime.now(timezone.utc).isoformat(),
    }
    if record.get("publishedAt"):
        payload["datePublished"] = record["publishedAt"]
    if record.get("heroImage"):
        image_url = str(record["heroImage"])
        payload["image"] = BLOG_CORE_ORIGIN + image_url if image_url.startswith("/sites/") else image_url
    return payload


def article_page(record, preview=False):
    title = record.get("title") or "Georivo insight"
    description = record.get("description") or "Practical guidance for presenting real estate locations with interactive 3D."
    slug = record.get("slug") or ""
    canonical = f"{SITE_ORIGIN}/blog/{slug}/"
    hero = str(record.get("heroImage") or "")
    if hero.startswith("/sites/"):
        hero = BLOG_CORE_ORIGIN + hero
    hero_html = ""
    if hero:
        hero_html = f'<figure class="article-hero"><img src="{esc(hero)}" alt="{esc(title)}"></figure>'
    preview_badge = '<div class="preview-banner">Draft preview. This page is not public or indexed.</div>' if preview else ""
    article_body = clean_article_markup(record.get("draftHtml") or "")
    category = record.get("category") or "Georivo journal"
    read_minutes = record.get("readMinutes") or 7
    body = f"""
    {preview_badge}
    <main class="article-layout">
      <article>
        <a class="back-link" href="/blog/">← Journal</a>
        <div class="eyebrow">{esc(category)}</div>
        <h1>{esc(title)}</h1>
        <p class="dek">{esc(description)}</p>
        <div class="article-meta">Georivo editorial · {esc(read_minutes)} min read</div>
        {hero_html}
        <div class="article-copy">{article_body}</div>
        <aside class="article-cta">
          <div><span>Build your location story</span><strong>Turn a property address into a live 3D journey.</strong></div>
          <a href="/#create">Check an address <span>↗</span></a>
        </aside>
      </article>
    </main>
    """
    return shell(
        f"{title} | Georivo",
        description,
        body,
        canonical,
        article_schema(record, canonical),
        noindex=preview,
    )


@app.get("/health")
def health():
    return {"ok": True, "service": "georivo-blog", "published": len(load_records(PUBLISHED_ROOT))}


@app.get("/blog")
def blog_redirect():
    return redirect("/blog/", code=308)


@app.get("/blog/")
def blog_index():
    posts = load_records(PUBLISHED_ROOT)
    cards = []
    for post in posts:
        title = post.get("title") or "Georivo insight"
        description = post.get("description") or ""
        slug = post.get("slug") or ""
        hero = str(post.get("heroImage") or "")
        if hero.startswith("/sites/"):
            hero = BLOG_CORE_ORIGIN + hero
        media = f'<img src="{esc(hero)}" alt="{esc(title)}" loading="lazy">' if hero else '<div class="card-placeholder">G</div>'
        cards.append(f"""
          <article class="post-card">
            <a class="post-media" href="/blog/{esc(slug)}/">{media}</a>
            <div class="post-card-copy">
              <span>{esc(post.get("category") or "Georivo journal")}</span>
              <h2><a href="/blog/{esc(slug)}/">{esc(title)}</a></h2>
              <p>{esc(description)}</p>
              <a class="read-link" href="/blog/{esc(slug)}/">Read article <span>↗</span></a>
            </div>
          </article>
        """)
    if not cards:
        cards.append("""
          <div class="empty-state">
            <span>Coming to the journal</span>
            <h2>A clearer way to talk about location.</h2>
            <p>New research for real-estate teams using interactive 3D to explain property context, neighborhoods, and arrival.</p>
          </div>
        """)
    body = f"""
    <main id="top">
      <section class="journal-hero">
        <div class="journal-hero-image" aria-hidden="true"></div>
        <div class="journal-hero-wash" aria-hidden="true"></div>
        <div class="journal-hero-content">
          <div class="section-tag">Georivo journal</div>
          <h1>Location,<br><em>seen clearly.</em></h1>
          <p>Research and practical guidance for turning property context into interactive stories that buyers can understand and explore.</p>
        </div>
      </section>
      <section class="journal-intro">
        <div class="section-tag">A better perspective</div>
        <h2>Stories about place,<br><em>built for real decisions.</em></h2>
      </section>
      <section class="journal-grid section-pad" aria-label="Latest articles">{''.join(cards)}</section>
      <section class="journal-cta">
        <div class="journal-cta-image" aria-hidden="true"></div>
        <div class="journal-cta-wash" aria-hidden="true"></div>
        <div class="journal-cta-copy">
          <span>Your next listing deserves a better view</span>
          <h2>Ready to see your<br>property <em>take flight?</em></h2>
          <a href="/#create">Check an address <span>↗</span></a>
          <p>No signup required to check availability.</p>
        </div>
      </section>
    </main>
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Georivo Journal",
        "url": f"{SITE_ORIGIN}/blog/",
        "description": "Research and practical guidance about interactive 3D location stories for real estate.",
    }
    return shell(
        "Georivo Journal | Interactive 3D for Real Estate",
        "Research and practical guidance for presenting properties, neighborhoods, and arrival context with interactive 3D location stories.",
        body,
        f"{SITE_ORIGIN}/blog/",
        schema,
    )


@app.get("/blog/<slug>/")
def published_article(slug):
    record = load_record(PUBLISHED_ROOT, slug, "slug")
    if not record:
        abort(404)
    return article_page(record)


@app.get("/content-preview/<job_id>")
def draft_preview(job_id):
    record = load_record(DRAFT_ROOT, job_id, "id")
    if not record:
        abort(404)
    return article_page(record, preview=True)


@app.get("/sitemap.xml")
def sitemap():
    urls = [
        (f"{SITE_ORIGIN}/", "1.0"),
        (f"{SITE_ORIGIN}/contact", "0.6"),
        (f"{SITE_ORIGIN}/terms", "0.3"),
        (f"{SITE_ORIGIN}/privacy", "0.3"),
        (f"{SITE_ORIGIN}/blog/", "0.8"),
    ]
    for record in load_records(PUBLISHED_ROOT):
        slug = str(record.get("slug") or "").strip("/")
        if slug:
            urls.append((f"{SITE_ORIGIN}/blog/{slug}/", "0.7"))
    today = datetime.now(timezone.utc).date().isoformat()
    items = "".join(
        f"<url><loc>{esc(url)}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>"
        for url, priority in urls
    )
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>',
        content_type="application/xml; charset=utf-8",
    )


@app.errorhandler(404)
def not_found(_error):
    body = """
    <main class="not-found"><span>404</span><h1>This location is not on the map.</h1>
    <p>The requested journal page does not exist.</p><a href="/blog/">Open the journal</a></main>
    """
    return shell("Page not found | Georivo", "The requested Georivo page was not found.", body, f"{SITE_ORIGIN}/blog/", noindex=True), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "13340")))
