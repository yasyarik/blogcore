import html
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, abort, redirect, request
from native_site_chrome import LiveSiteChrome


APP_ROOT = Path(__file__).resolve().parent
CONTENT_ROOT = APP_ROOT / "data" / "blog-core"
PUBLISHED_ROOT = CONTENT_ROOT / "published"
DRAFT_ROOT = CONTENT_ROOT / "drafts"
BLOG_CORE_ORIGIN = os.environ.get("BLOG_CORE_ORIGIN", "https://blog.yas.ooo").rstrip("/")
SITE_ORIGIN = "https://georivo.com"
NATIVE_STYLESHEET_FALLBACK = os.environ.get(
    "GEORIVO_NATIVE_STYLESHEET",
    "/assets/index-BzOmagHL.css",
)
NATIVE_STYLESHEET_CACHE_SECONDS = 300
SOURCE_CHROME = LiveSiteChrome(
    SITE_ORIGIN,
    cache_seconds=NATIVE_STYLESHEET_CACHE_SECONDS,
    fallback_stylesheet=NATIVE_STYLESHEET_FALLBACK,
    stylesheet_href_pattern=(
        r'href=["\'](?P<href>/assets/index-[A-Za-z0-9_-]+\.css)["\']'
    ),
)
DEFAULT_LANGUAGE = "en"
LANGUAGES = tuple(
    dict.fromkeys(
        language.strip().lower()
        for language in os.environ.get("GEORIVO_LANGUAGES", "en,de,es,fr,ru").split(",")
        if language.strip()
    )
)
LANGUAGE_LABELS = {
    "en": "EN",
    "de": "DE",
    "es": "ES",
    "fr": "FR",
    "ru": "RU",
}
LANGUAGE_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "ru": "Русский",
}
LANGUAGE_FLAGS = {
    "en": "🇬🇧",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "ru": "🇷🇺",
}
UI = {
    "en": {
        "examples": "Examples", "how": "How it works", "pricing": "Pricing", "blog": "Blog",
        "sign_in": "Sign in", "create": "Create a widget", "product": "Product", "company": "Company",
        "contact": "Contact", "terms": "Terms", "privacy": "Privacy",
        "footer_copy": "Interactive 3D location stories,<br>embedded on real-estate websites.",
        "journal": "Georivo journal", "hero_title": "Location,<br><em>seen clearly.</em>",
        "hero_copy": "Research and practical guidance for turning property context into interactive stories that buyers can understand and explore.",
        "perspective": "A better perspective", "intro": "Stories about place,<br><em>built for real decisions.</em>",
        "latest": "Latest articles", "coming": "Coming to the journal",
        "empty_title": "A clearer way to talk about location.",
        "empty_copy": "New research for real-estate teams using interactive 3D to explain property context, neighborhoods, and arrival.",
        "read": "Read article", "cta_kicker": "Your next listing deserves a better view",
        "cta_title": "Ready to see your<br>property <em>take flight?</em>",
        "cta": "Check an address", "cta_note": "No signup required to check availability.",
        "back": "Journal", "editorial": "Georivo editorial", "minutes": "min read",
        "build": "Build your location story", "build_copy": "Turn a property address into a live 3D journey.",
        "draft": "Draft preview. This page is not public or indexed.",
        "not_found": "This location is not on the map.", "not_found_copy": "The requested journal page does not exist.",
    },
    "de": {
        "examples": "Beispiele", "how": "So funktioniert es", "pricing": "Preise", "blog": "Blog",
        "sign_in": "Anmelden", "create": "Widget erstellen", "product": "Produkt", "company": "Unternehmen",
        "contact": "Kontakt", "terms": "Bedingungen", "privacy": "Datenschutz",
        "footer_copy": "Interaktive 3D-Standortgeschichten,<br>eingebettet in Immobilien-Websites.",
        "journal": "Georivo Journal", "hero_title": "Standorte,<br><em>klar erlebbar.</em>",
        "hero_copy": "Recherche und praktische Hinweise, die Immobilienstandorte in interaktive Geschichten verwandeln.",
        "perspective": "Eine bessere Perspektive", "intro": "Geschichten über Orte,<br><em>für echte Entscheidungen.</em>",
        "latest": "Neueste Artikel", "coming": "Demnächst im Journal",
        "empty_title": "Standorte verständlicher erzählen.",
        "empty_copy": "Neue Analysen für Immobilienteams zu 3D-Kontext, Nachbarschaften und Anreise.",
        "read": "Artikel lesen", "cta_kicker": "Ihr nächstes Objekt verdient eine bessere Perspektive",
        "cta_title": "Bereit, Ihre Immobilie<br><em>abheben zu sehen?</em>",
        "cta": "Adresse prüfen", "cta_note": "Keine Anmeldung für die Verfügbarkeitsprüfung erforderlich.",
        "back": "Journal", "editorial": "Georivo Redaktion", "minutes": "Min. Lesezeit",
        "build": "Standortgeschichte erstellen", "build_copy": "Eine Immobilienadresse in eine interaktive 3D-Reise verwandeln.",
        "draft": "Entwurfsvorschau. Diese Seite ist nicht öffentlich oder indexiert.",
        "not_found": "Dieser Standort ist nicht auf der Karte.", "not_found_copy": "Die angeforderte Journalseite existiert nicht.",
    },
    "es": {
        "examples": "Ejemplos", "how": "Cómo funciona", "pricing": "Precios", "blog": "Blog",
        "sign_in": "Iniciar sesión", "create": "Crear un widget", "product": "Producto", "company": "Empresa",
        "contact": "Contacto", "terms": "Términos", "privacy": "Privacidad",
        "footer_copy": "Historias interactivas de ubicación en 3D,<br>integradas en sitios inmobiliarios.",
        "journal": "Revista Georivo", "hero_title": "La ubicación,<br><em>vista con claridad.</em>",
        "hero_copy": "Análisis y consejos prácticos para convertir el contexto de una propiedad en una historia interactiva.",
        "perspective": "Una perspectiva mejor", "intro": "Historias sobre lugares,<br><em>para decisiones reales.</em>",
        "latest": "Últimos artículos", "coming": "Próximamente en la revista",
        "empty_title": "Una forma más clara de explicar la ubicación.",
        "empty_copy": "Nuevos análisis para equipos inmobiliarios sobre contexto 3D, barrios y recorridos de llegada.",
        "read": "Leer artículo", "cta_kicker": "Tu próximo anuncio merece una vista mejor",
        "cta_title": "¿Listo para ver tu<br>propiedad <em>despegar?</em>",
        "cta": "Comprobar dirección", "cta_note": "No es necesario registrarse para comprobar la disponibilidad.",
        "back": "Revista", "editorial": "Redacción de Georivo", "minutes": "min de lectura",
        "build": "Crea tu historia de ubicación", "build_copy": "Convierte una dirección en un recorrido 3D interactivo.",
        "draft": "Vista previa del borrador. Esta página no es pública ni está indexada.",
        "not_found": "Esta ubicación no aparece en el mapa.", "not_found_copy": "La página solicitada no existe.",
    },
    "fr": {
        "examples": "Exemples", "how": "Fonctionnement", "pricing": "Tarifs", "blog": "Blog",
        "sign_in": "Connexion", "create": "Créer un widget", "product": "Produit", "company": "Entreprise",
        "contact": "Contact", "terms": "Conditions", "privacy": "Confidentialité",
        "footer_copy": "Des histoires de localisation 3D interactives,<br>intégrées aux sites immobiliers.",
        "journal": "Journal Georivo", "hero_title": "Le lieu,<br><em>vu clairement.</em>",
        "hero_copy": "Analyses et conseils pratiques pour transformer le contexte immobilier en récit interactif.",
        "perspective": "Une meilleure perspective", "intro": "Des histoires de lieux,<br><em>pour de vraies décisions.</em>",
        "latest": "Derniers articles", "coming": "Bientôt dans le journal",
        "empty_title": "Une façon plus claire de raconter un lieu.",
        "empty_copy": "De nouvelles analyses pour les équipes immobilières sur le contexte 3D, les quartiers et l'arrivée.",
        "read": "Lire l'article", "cta_kicker": "Votre prochaine annonce mérite une meilleure vue",
        "cta_title": "Prêt à voir votre<br>bien <em>prendre son envol ?</em>",
        "cta": "Vérifier une adresse", "cta_note": "Aucune inscription nécessaire pour vérifier la disponibilité.",
        "back": "Journal", "editorial": "Rédaction Georivo", "minutes": "min de lecture",
        "build": "Créez votre histoire de lieu", "build_copy": "Transformez une adresse en parcours 3D interactif.",
        "draft": "Aperçu du brouillon. Cette page n'est ni publique ni indexée.",
        "not_found": "Ce lieu n'est pas sur la carte.", "not_found_copy": "La page demandée n'existe pas.",
    },
    "ru": {
        "examples": "Примеры", "how": "Как это работает", "pricing": "Цены", "blog": "Блог",
        "sign_in": "Войти", "create": "Создать виджет", "product": "Продукт", "company": "Компания",
        "contact": "Контакты", "terms": "Условия", "privacy": "Конфиденциальность",
        "footer_copy": "Интерактивные 3D-истории о локации,<br>встроенные в сайты недвижимости.",
        "journal": "Журнал Georivo", "hero_title": "Локация,<br><em>понятная сразу.</em>",
        "hero_copy": "Исследования и практические материалы о том, как превращать контекст объекта в интерактивную историю.",
        "perspective": "Новый взгляд", "intro": "Истории о местах,<br><em>для реальных решений.</em>",
        "latest": "Последние статьи", "coming": "Скоро в журнале",
        "empty_title": "Понятный способ рассказать о локации.",
        "empty_copy": "Новые материалы для команд недвижимости о 3D-контексте, районах и маршрутах прибытия.",
        "read": "Читать статью", "cta_kicker": "Ваш следующий объект заслуживает лучшего ракурса",
        "cta_title": "Готовы увидеть объект<br><em>с новой высоты?</em>",
        "cta": "Проверить адрес", "cta_note": "Для проверки доступности регистрация не требуется.",
        "back": "Журнал", "editorial": "Редакция Georivo", "minutes": "мин чтения",
        "build": "Создайте историю локации", "build_copy": "Превратите адрес объекта в интерактивное 3D-путешествие.",
        "draft": "Предпросмотр черновика. Страница не опубликована и не индексируется.",
        "not_found": "Этой локации нет на карте.", "not_found_copy": "Запрошенная страница журнала не существует.",
    },
}

app = Flask(__name__)


def esc(value):
    return html.escape(str(value or ""), quote=True)


def normalize_language(language):
    language = str(language or DEFAULT_LANGUAGE).strip().lower()
    return language if language in LANGUAGES else DEFAULT_LANGUAGE


def copy_for(language):
    return UI.get(normalize_language(language), UI[DEFAULT_LANGUAGE])


def blog_path(language):
    language = normalize_language(language)
    return "/blog/" if language == DEFAULT_LANGUAGE else f"/{language}/blog/"


def article_path(language, slug):
    return f"{blog_path(language)}{str(slug or '').strip('/')}/"


def localized_record(record, language):
    language = normalize_language(language)
    base_language = normalize_language(record.get("language") or DEFAULT_LANGUAGE)
    if language == base_language:
        return dict(record)
    translations = record.get("translations") if isinstance(record.get("translations"), dict) else {}
    localized = translations.get(language)
    if not isinstance(localized, dict):
        return None
    return {**record, **localized, "activeLanguage": language}


def record_languages(record):
    available = [normalize_language(record.get("language") or DEFAULT_LANGUAGE)]
    translations = record.get("translations") if isinstance(record.get("translations"), dict) else {}
    available.extend(language for language in LANGUAGES if isinstance(translations.get(language), dict))
    return list(dict.fromkeys(available))


def language_switcher(language, slug=None, preview_job_id=None):
    options = []
    for item in LANGUAGES:
        if preview_job_id:
            target = f"/content-preview/{preview_job_id}?lang={item}"
        else:
            target = article_path(item, slug) if slug else blog_path(item)
        selected = " selected" if item == language else ""
        options.append(
            f'<option value="{esc(target)}"{selected}>{esc(LANGUAGE_LABELS.get(item, item.upper()))}</option>'
        )
    return f"""
    <label class="language-select">
      <span class="sr-only">Language</span>
      <select aria-label="Language" onchange="window.location.href=this.value">{''.join(options)}</select>
    </label>
    """


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


def native_chrome():
    snapshot = SOURCE_CHROME.get()
    return snapshot["header"], snapshot["footer"]


def native_language_options(language, slug=None, preview_job_id=None):
    options = []
    for item in LANGUAGES:
        if preview_job_id:
            target = f"/content-preview/{preview_job_id}?lang={item}"
        else:
            target = article_path(item, slug) if slug else blog_path(item)
        selected = " selected" if item == language else ""
        options.append(
            f'<option value="{esc(target)}" aria-label="{esc(LANGUAGE_NAMES[item])}"'
            f'{selected}>{LANGUAGE_FLAGS[item]}</option>'
        )
    return "".join(options)


def adapt_native_chrome(fragment, language, slug=None, preview_job_id=None, footer=False):
    if not fragment:
        return ""
    labels = copy_for(language)
    fragment = re.sub(r'href=(["\'])#', r'href=\1/#', fragment)
    fragment = fragment.replace('href="/#top"', 'href="/"')
    fragment = fragment.replace("href='/#top'", "href='/'")
    select = (
        f'<select aria-label="Language" title="{esc(LANGUAGE_NAMES[language])}" '
        f'onchange="window.location.href=this.value">'
        f'{native_language_options(language, slug, preview_job_id)}</select>'
    )
    fragment = re.sub(
        r'(?is)<select\b[^>]*aria-label=(["\'])Language\1[^>]*>.*?</select>',
        select,
        fragment,
        count=1,
    )
    replacements = {
        "Examples": labels["examples"],
        "How it works": labels["how"],
        "Pricing": labels["pricing"],
        "Sign in": labels["sign_in"],
        "Create a widget": labels["create"],
        "Product": labels["product"],
        "Company": labels["company"],
        "Contact": labels["contact"],
        "Terms": labels["terms"],
        "Privacy": labels["privacy"],
    }
    for source, translated in replacements.items():
        fragment = fragment.replace(f">{source}</a>", f">{esc(translated)}</a>")
        fragment = fragment.replace(f">{source}</b>", f">{esc(translated)}</b>")
    current = "" if footer else ' aria-current="page"'
    blog_link = (
        f'<a href="{esc(blog_path(language))}"{current}>'
        f'{esc(labels["blog"])}</a>'
    )
    if not re.search(r'href=(["\'])/(?:[a-z]{2}/)?blog/?\1', fragment):
        if footer:
            fragment = re.sub(
                r'(?is)(<a\b[^>]*href=(["\'])/#plans\2[^>]*>.*?</a>)',
                rf"\1{blog_link}",
                fragment,
                count=1,
            )
        else:
            fragment = fragment.replace(
                '<a class="nav-account"',
                f'{blog_link}<a class="nav-account"',
                1,
            )
    return fragment


def fallback_site_header(language=DEFAULT_LANGUAGE, slug=None, preview_job_id=None):
    language = normalize_language(language)
    labels = copy_for(language)
    return f"""
    <header class="nav glass">
      <a class="brand" href="/" aria-label="Georivo home">
        <span class="brand-logo light" aria-hidden="true"><img src="/brand/georivo-on-light.png" alt=""></span>Georivo
      </a>
      <button class="menu-button" type="button" aria-label="Toggle navigation" aria-expanded="false">Menu</button>
      <nav class="nav-links" aria-label="Main navigation">
        <a href="/#movements">{esc(labels["examples"])}</a>
        <a href="/#how">{esc(labels["how"])}</a>
        <a href="/#plans">{esc(labels["pricing"])}</a>
        <a href="{esc(blog_path(language))}" aria-current="page">{esc(labels["blog"])}</a>
        {language_switcher(language, slug, preview_job_id)}
        <a href="/login">{esc(labels["sign_in"])}</a>
        <a class="nav-cta" href="/#create">{esc(labels["create"])} <span>↗</span></a>
      </nav>
    </header>
    """


def site_header(language=DEFAULT_LANGUAGE, slug=None, preview_job_id=None):
    language = normalize_language(language)
    header, _ = native_chrome()
    return adapt_native_chrome(
        header,
        language,
        slug=slug,
        preview_job_id=preview_job_id,
    ) or fallback_site_header(language, slug, preview_job_id)


def fallback_site_footer(language=DEFAULT_LANGUAGE):
    labels = copy_for(language)
    return f"""
    <footer id="footer">
      <div class="footer-top">
        <a class="brand" href="/">
          <span class="brand-logo dark" aria-hidden="true"><img src="/brand/georivo-on-dark.png" alt=""></span>Georivo
        </a>
        <p>{labels["footer_copy"]}</p>
        <div class="footer-links">
          <div><b>{esc(labels["product"])}</b><a href="/#movements">{esc(labels["examples"])}</a><a href="/#how">{esc(labels["how"])}</a><a href="/#plans">{esc(labels["pricing"])}</a><a href="{esc(blog_path(language))}">{esc(labels["blog"])}</a></div>
          <div><b>{esc(labels["company"])}</b><a href="/contact">{esc(labels["contact"])}</a><a href="/terms">{esc(labels["terms"])}</a><a href="/privacy">{esc(labels["privacy"])}</a></div>
        </div>
      </div>
      <div class="footer-bottom"><span>© 2026 Georivo. All rights reserved.</span><span>3D visualization generated from available licensed geospatial imagery.</span></div>
    </footer>
    """


def site_footer(language=DEFAULT_LANGUAGE, slug=None, preview_job_id=None):
    language = normalize_language(language)
    _, footer = native_chrome()
    return adapt_native_chrome(
        footer,
        language,
        slug=slug,
        preview_job_id=preview_job_id,
        footer=True,
    ) or fallback_site_footer(language)


def schema_markup(payload):
    return '<script type="application/ld+json">' + json.dumps(payload, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def native_stylesheet_url():
    return SOURCE_CHROME.get()["stylesheet"] or NATIVE_STYLESHEET_FALLBACK


def shell(
    title,
    description,
    body,
    canonical,
    schema=None,
    noindex=False,
    language=DEFAULT_LANGUAGE,
    alternate_urls=None,
    slug=None,
    preview_job_id=None,
):
    language = normalize_language(language)
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    structured = schema_markup(schema) if schema else ""
    native_stylesheet = native_stylesheet_url()
    alternates = alternate_urls or {}
    alternate_markup = "".join(
        f'<link rel="alternate" hreflang="{esc(code)}" href="{esc(url)}">'
        for code, url in alternates.items()
    )
    if DEFAULT_LANGUAGE in alternates:
        alternate_markup += f'<link rel="alternate" hreflang="x-default" href="{esc(alternates[DEFAULT_LANGUAGE])}">'
    return f"""<!doctype html>
<html lang="{esc(language)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  {robots}
  <link rel="canonical" href="{esc(canonical)}">
  {alternate_markup}
  <link rel="icon" href="/favicon.ico">
  <link rel="preload" as="image" href="/brand/georivo-on-light.png">
  <link rel="stylesheet" href="{esc(native_stylesheet)}">
  <link rel="stylesheet" href="/blog-assets/georivo-blog.css?v=20260723b">
  {structured}
</head>
<body class="blog-shell">
  {site_header(language, slug, preview_job_id)}
  {body}
  {site_footer(language, slug, preview_job_id)}
  <script src="/georivo-blog-nav.js?v=20260724d" defer></script>
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


def article_page(record, language=DEFAULT_LANGUAGE, preview=False):
    language = normalize_language(language)
    labels = copy_for(language)
    localized = localized_record(record, language)
    if not localized:
        abort(404)
    record = localized
    title = record.get("title") or "Georivo insight"
    description = record.get("description") or "Practical guidance for presenting real estate locations with interactive 3D."
    slug = record.get("slug") or ""
    canonical = f"{SITE_ORIGIN}{article_path(language, slug)}"
    alternate_urls = {
        item: f"{SITE_ORIGIN}{article_path(item, slug)}"
        for item in record_languages(record)
    }
    hero = str(record.get("heroImage") or "")
    if hero.startswith("/sites/"):
        hero = BLOG_CORE_ORIGIN + hero
    hero_html = ""
    if hero:
        hero_html = f'<figure class="article-hero"><img src="{esc(hero)}" alt="{esc(title)}"></figure>'
    preview_badge = f'<div class="preview-banner">{esc(labels["draft"])}</div>' if preview else ""
    article_body = clean_article_markup(record.get("draftHtml") or "")
    toc_match = re.search(
        r'(?is)<nav\b[^>]*class=(["\'])[^"\']*\barticle-toc\b[^"\']*\1[^>]*>.*?</nav>',
        article_body,
    )
    toc_html = toc_match.group(0) if toc_match else ""
    if toc_match:
        article_body = article_body[:toc_match.start()] + article_body[toc_match.end():]
    category = record.get("category") or "Georivo journal"
    read_minutes = record.get("readMinutes") or 7
    body = f"""
    {preview_badge}
    <main class="article-layout">
      <article>
        <a class="back-link" href="{esc(blog_path(language))}">← {esc(labels["back"])}</a>
        <div class="eyebrow">{esc(category)}</div>
        <h1>{esc(title)}</h1>
        <p class="dek">{esc(description)}</p>
        <div class="article-meta">{esc(labels["editorial"])} · {esc(read_minutes)} {esc(labels["minutes"])}</div>
        {toc_html}
        {hero_html}
        <div class="article-copy">{article_body}</div>
        <aside class="article-cta">
          <div><span>{esc(labels["build"])}</span><strong>{esc(labels["build_copy"])}</strong></div>
          <a href="/#create">{esc(labels["cta"])} <span>↗</span></a>
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
        language=language,
        alternate_urls=alternate_urls,
        slug=slug,
        preview_job_id=record.get("id") if preview else None,
    )


@app.get("/health")
def health():
    return {"ok": True, "service": "georivo-blog", "published": len(load_records(PUBLISHED_ROOT))}


@app.get("/blog")
def blog_redirect():
    return redirect("/blog/", code=308)


def render_blog_index(language=DEFAULT_LANGUAGE):
    language = normalize_language(language)
    labels = copy_for(language)
    posts = load_records(PUBLISHED_ROOT)
    cards = []
    for post in posts:
        localized = localized_record(post, language)
        if not localized:
            continue
        title = localized.get("title") or "Georivo insight"
        description = localized.get("description") or ""
        slug = localized.get("slug") or post.get("slug") or ""
        hero = str(localized.get("heroImage") or post.get("heroImage") or "")
        if hero.startswith("/sites/"):
            hero = BLOG_CORE_ORIGIN + hero
        media = f'<img src="{esc(hero)}" alt="{esc(title)}" loading="lazy">' if hero else '<div class="card-placeholder">G</div>'
        url = article_path(language, slug)
        cards.append(f"""
          <article class="post-card">
            <a class="post-media" href="{esc(url)}">{media}</a>
            <div class="post-card-copy">
              <span>{esc(localized.get("category") or labels["journal"])}</span>
              <h2><a href="{esc(url)}">{esc(title)}</a></h2>
              <p>{esc(description)}</p>
              <a class="read-link" href="{esc(url)}">{esc(labels["read"])} <span>↗</span></a>
            </div>
          </article>
        """)
    if not cards:
        cards.append(f"""
          <div class="empty-state">
            <span>{esc(labels["coming"])}</span>
            <h2>{esc(labels["empty_title"])}</h2>
            <p>{esc(labels["empty_copy"])}</p>
          </div>
        """)
    body = f"""
    <main id="top">
      <section class="journal-hero">
        <div class="journal-hero-image" aria-hidden="true"></div>
        <div class="journal-hero-wash" aria-hidden="true"></div>
        <div class="journal-hero-content">
          <div class="section-tag">{esc(labels["journal"])}</div>
          <h1>{labels["hero_title"]}</h1>
          <p>{esc(labels["hero_copy"])}</p>
        </div>
      </section>
      <section class="journal-intro">
        <div class="section-tag">{esc(labels["perspective"])}</div>
        <h2>{labels["intro"]}</h2>
      </section>
      <section class="journal-grid section-pad" aria-label="{esc(labels["latest"])}">{''.join(cards)}</section>
      <section class="journal-cta">
        <div class="journal-cta-image" aria-hidden="true"></div>
        <div class="journal-cta-wash" aria-hidden="true"></div>
        <div class="journal-cta-copy">
          <span>{esc(labels["cta_kicker"])}</span>
          <h2>{labels["cta_title"]}</h2>
          <a href="/#create">{esc(labels["cta"])} <span>↗</span></a>
          <p>{esc(labels["cta_note"])}</p>
        </div>
      </section>
    </main>
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": labels["journal"],
        "url": f"{SITE_ORIGIN}{blog_path(language)}",
        "description": labels["hero_copy"],
    }
    canonical = f"{SITE_ORIGIN}{blog_path(language)}"
    alternate_urls = {item: f"{SITE_ORIGIN}{blog_path(item)}" for item in LANGUAGES}
    return shell(
        f"{labels['journal']} | Georivo",
        labels["hero_copy"],
        body,
        canonical,
        schema,
        language=language,
        alternate_urls=alternate_urls,
    )


@app.get("/blog/")
def blog_index():
    return render_blog_index(DEFAULT_LANGUAGE)


@app.get("/<language>/blog")
def localized_blog_redirect(language):
    language = str(language or "").strip().lower()
    if language not in LANGUAGES:
        abort(404)
    if language == DEFAULT_LANGUAGE:
        return redirect("/blog/", code=308)
    return redirect(blog_path(language), code=308)


@app.get("/<language>/blog/")
def localized_blog_index(language):
    if language not in LANGUAGES or language == DEFAULT_LANGUAGE:
        abort(404)
    return render_blog_index(language)


@app.get("/blog/<slug>/")
def published_article(slug):
    record = load_record(PUBLISHED_ROOT, slug, "slug")
    if not record:
        abort(404)
    return article_page(record, DEFAULT_LANGUAGE)


@app.get("/<language>/blog/<slug>/")
def localized_published_article(language, slug):
    if language not in LANGUAGES or language == DEFAULT_LANGUAGE:
        abort(404)
    record = load_record(PUBLISHED_ROOT, slug, "slug")
    if not record:
        abort(404)
    return article_page(record, language)


@app.get("/content-preview/<job_id>")
def draft_preview(job_id):
    record = load_record(DRAFT_ROOT, job_id, "id")
    if not record:
        abort(404)
    language = normalize_language(request.args.get("lang"))
    return article_page(record, language, preview=True)


@app.get("/sitemap.xml")
def sitemap():
    groups = [
        (f"{SITE_ORIGIN}/", "1.0", {}),
        (f"{SITE_ORIGIN}/contact", "0.6", {}),
        (f"{SITE_ORIGIN}/terms", "0.3", {}),
        (f"{SITE_ORIGIN}/privacy", "0.3", {}),
    ]
    blog_alternates = {item: f"{SITE_ORIGIN}{blog_path(item)}" for item in LANGUAGES}
    groups.extend((url, "0.8", blog_alternates) for url in blog_alternates.values())
    for record in load_records(PUBLISHED_ROOT):
        slug = str(record.get("slug") or "").strip("/")
        if slug:
            article_alternates = {
                language: f"{SITE_ORIGIN}{article_path(language, slug)}"
                for language in record_languages(record)
            }
            groups.extend((url, "0.7", article_alternates) for url in article_alternates.values())
    today = datetime.now(timezone.utc).date().isoformat()
    items = []
    for url, priority, alternates in groups:
        links = "".join(
            f'<xhtml:link rel="alternate" hreflang="{esc(language)}" href="{esc(alternate)}"/>'
            for language, alternate in alternates.items()
        )
        if DEFAULT_LANGUAGE in alternates:
            links += (
                f'<xhtml:link rel="alternate" hreflang="x-default" '
                f'href="{esc(alternates[DEFAULT_LANGUAGE])}"/>'
            )
        items.append(
            f"<url><loc>{esc(url)}</loc>{links}<lastmod>{today}</lastmod>"
            f"<changefreq>weekly</changefreq><priority>{priority}</priority></url>"
        )
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        f'{"".join(items)}</urlset>',
        content_type="application/xml; charset=utf-8",
    )


@app.errorhandler(404)
def not_found(_error):
    match = re.match(r"^/([a-z]{2})/blog(?:/|$)", request.path)
    language = normalize_language(match.group(1) if match else DEFAULT_LANGUAGE)
    labels = copy_for(language)
    body = f"""
    <main class="not-found"><span>404</span><h1>{esc(labels["not_found"])}</h1>
    <p>{esc(labels["not_found_copy"])}</p><a href="{esc(blog_path(language))}">{esc(labels["back"])}</a></main>
    """
    return shell(
        f"404 | Georivo",
        labels["not_found_copy"],
        body,
        f"{SITE_ORIGIN}{blog_path(language)}",
        noindex=True,
        language=language,
    ), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "13340")))
