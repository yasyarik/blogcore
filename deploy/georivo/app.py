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
        "examples": "Beispiele", "how": "So funktioniert es", "pricing": "Preise", "blog": "Magazin",
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
        "examples": "Ejemplos", "how": "Cómo funciona", "pricing": "Precios", "blog": "Revista",
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
        "examples": "Exemples", "how": "Fonctionnement", "pricing": "Tarifs", "blog": "Journal",
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

CONTENT_TYPE_ALIASES = {
    "article": "blog",
    "blog": "blog",
    "blog_post": "blog",
    "blog-post": "blog",
    "guide": "guide",
    "guides": "guide",
    "template": "template",
    "templates": "template",
    "example": "example",
    "examples": "example",
    "integration": "integration_guide",
    "integration-guide": "integration_guide",
    "integration_guide": "integration_guide",
    "embed": "integration_guide",
    "use_case": "use_case",
    "use-case": "use_case",
    "use-cases": "use_case",
    "money_page": "money_page",
    "money-page": "money_page",
    "seo_money_page": "money_page",
    "seo-money-page": "money_page",
}
CONTENT_SECTIONS = {
    "blog": "blog",
    "guide": "guides",
    "template": "templates",
    "example": "examples",
    "integration_guide": "embed",
    "use_case": "use-cases",
}
SECTION_CONTENT_TYPES = {section: content_type for content_type, section in CONTENT_SECTIONS.items()}
MONEY_PAGE_SLUGS = ("how-it-works", "coverage", "pricing")
SECTION_LABELS = {
    "en": {
        "blog": "Georivo journal", "guides": "Guides", "templates": "Templates",
        "examples": "Examples", "embed": "Embed guides", "use-cases": "Use cases",
    },
    "de": {
        "blog": "Georivo Journal", "guides": "Leitfäden", "templates": "Vorlagen",
        "examples": "Beispiele", "embed": "Einbettungsanleitungen", "use-cases": "Anwendungsfälle",
    },
    "es": {
        "blog": "Revista Georivo", "guides": "Guías", "templates": "Plantillas",
        "examples": "Ejemplos", "embed": "Guías de integración", "use-cases": "Casos de uso",
    },
    "fr": {
        "blog": "Journal Georivo", "guides": "Guides", "templates": "Modèles",
        "examples": "Exemples", "embed": "Guides d'intégration", "use-cases": "Cas d'usage",
    },
    "ru": {
        "blog": "Журнал Georivo", "guides": "Руководства", "templates": "Шаблоны",
        "examples": "Примеры", "embed": "Инструкции по встраиванию", "use-cases": "Сценарии использования",
    },
}
TRUST_LABELS = {
    "en": {"author": "Written by", "reviewer": "Reviewed by", "updated": "Updated", "sources": "Sources"},
    "de": {"author": "Verfasst von", "reviewer": "Geprüft von", "updated": "Aktualisiert", "sources": "Quellen"},
    "es": {"author": "Escrito por", "reviewer": "Revisado por", "updated": "Actualizado", "sources": "Fuentes"},
    "fr": {"author": "Rédigé par", "reviewer": "Relu par", "updated": "Mis à jour", "sources": "Sources"},
    "ru": {"author": "Автор", "reviewer": "Проверено", "updated": "Обновлено", "sources": "Источники"},
}
CONTENT_NOTICE = {
    "en": {
        "demo": "Demonstration, not a customer case. It does not claim current property condition, legal boundaries, exact routes, distances, or availability.",
        "checked": "Platform instructions checked",
        "change": "Platform interfaces and plan rules can change. Verify the public page after publishing.",
    },
    "de": {
        "demo": "Demonstration, kein Kundenfall. Sie macht keine Aussagen zu aktuellem Objektzustand, rechtlichen Grenzen, exakten Routen, Entfernungen oder Verfügbarkeit.",
        "checked": "Plattformanleitung geprüft",
        "change": "Plattformoberflächen und Tarifregeln können sich ändern. Prüfen Sie die öffentliche Seite nach der Veröffentlichung.",
    },
    "es": {
        "demo": "Demostración, no caso de cliente. No afirma el estado actual, límites legales, rutas o distancias exactas ni disponibilidad.",
        "checked": "Instrucciones de la plataforma comprobadas",
        "change": "La interfaz y las reglas del plan pueden cambiar. Verifica la página pública después de publicar.",
    },
    "fr": {
        "demo": "Démonstration, pas un cas client. Elle ne garantit ni l'état actuel, ni les limites légales, ni les itinéraires, distances ou disponibilités exacts.",
        "checked": "Instructions de la plateforme vérifiées",
        "change": "L'interface et les règles d'abonnement peuvent changer. Vérifiez la page publique après publication.",
    },
    "ru": {
        "demo": "Демонстрация, а не клиентский кейс. Она не подтверждает текущее состояние объекта, юридические границы, точные маршруты, расстояния или доступность.",
        "checked": "Инструкция платформы проверена",
        "change": "Интерфейс и правила тарифа могут измениться. После публикации проверьте публичную страницу.",
    },
}
HUB_COPY = {
    "en": {
        "guide": ("Decision guides", "Choose the right location-story approach for the property, audience, and publishing workflow."),
        "template": ("Story templates", "Compare reusable story structures, then choose the sequence that matches the property and buyer question."),
        "example": ("Location-story examples", "See clearly labelled demonstrations of how different property contexts can be explained."),
        "integration_guide": ("Embed guides", "Publish and verify a responsive Georivo widget on the website platform you already use."),
        "use_case": ("Real-estate use cases", "Match a location-story workflow to a concrete marketing or buyer-information problem."),
    },
}
HUB_COPY["de"] = HUB_COPY["en"]
HUB_COPY["es"] = HUB_COPY["en"]
HUB_COPY["fr"] = HUB_COPY["en"]
HUB_COPY["ru"] = HUB_COPY["en"]

GUIDE_GROUPS = {
    "en": {
        "understand": ("Understand", "Start with the core format and what it can explain."),
        "compare": ("Compare", "Choose between location-story and alternative media formats."),
        "plan": ("Plan", "Match the story to buyer questions, listing context, and media needs."),
        "implement": ("Implement", "Put the selected location story into a working publishing flow."),
    },
    "de": {
        "understand": ("Verstehen", "Beginnen Sie mit dem Format und seinem Erklärungswert."),
        "compare": ("Vergleichen", "Vergleichen Sie Location Storys mit anderen Medienformaten."),
        "plan": ("Planen", "Stimmen Sie die Story auf Käuferfragen und das Objekt ab."),
        "implement": ("Umsetzen", "Integrieren Sie die gewählte Story in den Veröffentlichungsablauf."),
    },
    "es": {
        "understand": ("Comprender", "Empieza por el formato y lo que puede explicar."),
        "compare": ("Comparar", "Compara la historia de ubicación con otros formatos."),
        "plan": ("Planificar", "Adapta la historia a las preguntas del comprador y al inmueble."),
        "implement": ("Implementar", "Integra la historia elegida en el flujo de publicación."),
    },
    "fr": {
        "understand": ("Comprendre", "Commencez par le format et ce qu'il permet d'expliquer."),
        "compare": ("Comparer", "Comparez le récit de localisation aux autres formats."),
        "plan": ("Planifier", "Adaptez le récit aux questions des acheteurs et au bien."),
        "implement": ("Mettre en œuvre", "Intégrez le récit choisi au flux de publication."),
    },
    "ru": {
        "understand": ("Разобраться", "Начните с формата и задач, которые он помогает объяснить."),
        "compare": ("Сравнить", "Сопоставьте историю локации с другими форматами."),
        "plan": ("Спланировать", "Свяжите историю с вопросами покупателя и объектом."),
        "implement": ("Внедрить", "Добавьте выбранную историю локации в процесс публикации."),
    },
}
GUIDE_SLUG_GROUPS = {
    "what-is-a-3d-property-flyover": "understand",
    "3d-property-flyover-vs-drone-video": "compare",
    "3d-property-flyover-vs-virtual-tour": "compare",
    "how-to-show-nearby-amenities-on-a-property-listing": "plan",
    "how-to-market-a-property-to-remote-buyers": "plan",
    "which-property-listings-need-an-aerial-view": "plan",
    "real-estate-listing-media-checklist": "plan",
    "how-to-add-a-3d-map-to-a-real-estate-website": "implement",
}

app = Flask(__name__)


def esc(value):
    return html.escape(str(value or ""), quote=True)


def normalize_language(language):
    language = str(language or DEFAULT_LANGUAGE).strip().lower()
    return language if language in LANGUAGES else DEFAULT_LANGUAGE


def copy_for(language):
    return UI.get(normalize_language(language), UI[DEFAULT_LANGUAGE])


def normalize_content_type(value):
    return CONTENT_TYPE_ALIASES.get(str(value or "blog").strip().lower(), "blog")


def record_content_type(record):
    return normalize_content_type(record.get("contentType") or record.get("pageType") or "blog")


def content_path(language, content_type="blog", slug=None):
    language = normalize_language(language)
    content_type = normalize_content_type(content_type)
    prefix = "" if language == DEFAULT_LANGUAGE else f"/{language}"
    if content_type == "money_page":
        if not slug:
            return f"{prefix}/"
        return f"{prefix}/{str(slug or '').strip('/')}"
    section = CONTENT_SECTIONS[content_type]
    path = f"{prefix}/{section}/"
    return f"{path}{str(slug or '').strip('/')}/" if slug else path


def blog_path(language):
    return content_path(language, "blog")


def article_path(language, slug, content_type="blog"):
    return content_path(language, content_type, slug)


def section_label(language, content_type):
    language = normalize_language(language)
    content_type = normalize_content_type(content_type)
    if content_type == "money_page":
        return "Georivo"
    section = CONTENT_SECTIONS[content_type]
    return SECTION_LABELS.get(language, SECTION_LABELS[DEFAULT_LANGUAGE]).get(section, section.title())


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


def language_switcher(language, slug=None, preview_job_id=None, content_type="blog"):
    options = []
    for item in LANGUAGES:
        if preview_job_id:
            target = f"/content-preview/{preview_job_id}?lang={item}"
        else:
            target = article_path(item, slug, content_type) if slug else content_path(item, content_type)
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


def load_content_record(directory, content_type, slug):
    content_type = normalize_content_type(content_type)
    for record in load_records(directory):
        if record_content_type(record) != content_type:
            continue
        if str(record.get("slug") or "").strip("/") == str(slug or "").strip("/"):
            return record
    return None


def is_money_page_record(record):
    slug = str(record.get("slug") or "").strip("/")
    content_type = record_content_type(record)
    return (
        slug in MONEY_PAGE_SLUGS
        and (
            content_type == "money_page"
            or (
                content_type == "use_case"
                and record.get("canonicalRootPage") is True
            )
        )
    )


def load_money_page_record(directory, slug):
    slug = str(slug or "").strip("/")
    if slug not in MONEY_PAGE_SLUGS:
        return None
    for record in load_records(directory):
        if is_money_page_record(record) and str(record.get("slug") or "").strip("/") == slug:
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
    def stabilize_image(match):
        tag = match.group(0)
        if not re.search(r"\bwidth=", tag, re.I):
            tag = re.sub(r"\s*/?>$", ' width="1376" height="768" loading="lazy" decoding="async">', tag)
        return tag
    cleaned = re.sub(r"(?is)<img\b[^>]*>", stabilize_image, cleaned)
    return absolute_article_assets(cleaned)


def native_chrome():
    snapshot = SOURCE_CHROME.get()
    return snapshot["header"], snapshot["footer"]


def native_language_options(language, slug=None, preview_job_id=None, content_type="blog"):
    options = []
    for item in LANGUAGES:
        if preview_job_id:
            target = f"/content-preview/{preview_job_id}?lang={item}"
        else:
            target = article_path(item, slug, content_type) if slug else content_path(item, content_type)
        selected = " selected" if item == language else ""
        options.append(
            f'<option value="{esc(target)}" aria-label="{esc(LANGUAGE_NAMES[item])}"'
            f'{selected}>{LANGUAGE_FLAGS[item]}</option>'
        )
    return "".join(options)


def localize_native_content_link(fragment, language, content_type):
    content_type = normalize_content_type(content_type)
    section = CONTENT_SECTIONS[content_type]
    target = content_path(language, content_type)
    label = copy_for(language)["blog"] if content_type == "blog" else section_label(language, content_type)
    pattern = re.compile(
        rf'(?is)<a\b(?P<before>[^>]*?)href=(?P<quote>["\'])'
        rf'/(?:[a-z]{{2}}/)?{re.escape(section)}/?(?P=quote)'
        rf'(?P<after>[^>]*)>.*?</a>'
    )

    def replace(match):
        return (
            f'<a{match.group("before")}href={match.group("quote")}{esc(target)}'
            f'{match.group("quote")}{match.group("after")}>{esc(label)}</a>'
        )

    return pattern.sub(replace, fragment)


def adapt_native_chrome(fragment, language, slug=None, preview_job_id=None, footer=False, content_type="blog"):
    if not fragment:
        return ""
    labels = copy_for(language)
    fragment = re.sub(r'href=(["\'])#', r'href=\1/#', fragment)
    fragment = fragment.replace('href="/#top"', 'href="/"')
    fragment = fragment.replace("href='/#top'", "href='/'")
    select = (
        f'<select aria-label="Language" title="{esc(LANGUAGE_NAMES[language])}" '
        f'onchange="window.location.href=this.value">'
        f'{native_language_options(language, slug, preview_job_id, content_type)}</select>'
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
    prefix = "" if language == DEFAULT_LANGUAGE else f"/{language}"
    fragment = re.sub(
        r'href=(["\'])/(?:[a-z]{2}/)?how-it-works/?\1',
        f'href="{prefix}/how-it-works"',
        fragment,
    )
    fragment = re.sub(
        r'href=(["\'])/(?:[a-z]{2}/)?pricing/?\1',
        f'href="{prefix}/pricing"',
        fragment,
    )
    for native_content_type in CONTENT_SECTIONS:
        fragment = localize_native_content_link(fragment, language, native_content_type)
    current = "" if footer or normalize_content_type(content_type) != "blog" else ' aria-current="page"'
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


def fallback_site_header(language=DEFAULT_LANGUAGE, slug=None, preview_job_id=None, content_type="blog"):
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
        <a href="{esc(blog_path(language))}"{' aria-current="page"' if normalize_content_type(content_type) == "blog" else ""}>{esc(labels["blog"])}</a>
        {language_switcher(language, slug, preview_job_id, content_type)}
        <a href="/login">{esc(labels["sign_in"])}</a>
        <a class="nav-cta" href="/#create">{esc(labels["create"])} <span>↗</span></a>
      </nav>
    </header>
    """


def site_header(language=DEFAULT_LANGUAGE, slug=None, preview_job_id=None, content_type="blog"):
    language = normalize_language(language)
    header, _ = native_chrome()
    return adapt_native_chrome(
        header,
        language,
        slug=slug,
        preview_job_id=preview_job_id,
        content_type=content_type,
    ) or fallback_site_header(language, slug, preview_job_id, content_type)


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


def site_footer(language=DEFAULT_LANGUAGE, slug=None, preview_job_id=None, content_type="blog"):
    language = normalize_language(language)
    _, footer = native_chrome()
    return adapt_native_chrome(
        footer,
        language,
        slug=slug,
        preview_job_id=preview_job_id,
        footer=True,
        content_type=content_type,
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
    content_type="blog",
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
  <link rel="icon" href="/brand/georivo-on-light.webp" type="image/webp">
  <link rel="stylesheet" href="{esc(native_stylesheet)}">
  <link rel="stylesheet" href="/blog-assets/georivo-blog.css?v=20260726d">
  {structured}
</head>
<body class="blog-shell">
  {site_header(language, slug, preview_job_id, content_type)}
  {body}
  {site_footer(language, slug, preview_job_id, content_type)}
  <script src="/georivo-blog-nav.js?v=20260725a" defer></script>
</body>
</html>"""


def article_schema(record, canonical):
    schema_types = {
        "blog": "Article",
        "guide": "Article",
        "template": "CreativeWork",
        "example": "Article",
        "integration_guide": "TechArticle",
        "use_case": "Article",
        "money_page": "WebPage",
    }
    article = {
        "@id": f"{canonical}#content",
        "@type": schema_types[record_content_type(record)],
        "headline": record.get("title") or "",
        "description": record.get("description") or "",
        "mainEntityOfPage": {"@id": canonical},
        "author": {"@type": "Organization", "name": "Georivo"},
        "publisher": {"@type": "Organization", "name": "Georivo"},
        "dateModified": record.get("updatedAt") or datetime.now(timezone.utc).isoformat(),
    }
    if record.get("publishedAt"):
        article["datePublished"] = record["publishedAt"]
    if record.get("heroImage"):
        image_url = str(record["heroImage"])
        article["image"] = BLOG_CORE_ORIGIN + image_url if image_url.startswith("/sites/") else image_url
    content_type = record_content_type(record)
    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Georivo", "item": f"{SITE_ORIGIN}/"},
    ]
    if content_type != "money_page":
        breadcrumb_items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": section_label(DEFAULT_LANGUAGE, content_type),
                "item": f"{SITE_ORIGIN}{content_path(DEFAULT_LANGUAGE, content_type)}",
            }
        )
    breadcrumb_items.append(
        {
            "@type": "ListItem",
            "position": len(breadcrumb_items) + 1,
            "name": record.get("title") or "",
            "item": canonical,
        }
    )
    breadcrumb = {
        "@id": f"{canonical}#breadcrumb",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items,
    }
    article["breadcrumb"] = {"@id": breadcrumb["@id"]}
    return {"@context": "https://schema.org", "@graph": [article, breadcrumb]}


def editorial_trust_html(record, language):
    editorial = record.get("editorial") if isinstance(record.get("editorial"), dict) else {}
    if not editorial:
        return ""
    labels = TRUST_LABELS.get(language, TRUST_LABELS[DEFAULT_LANGUAGE])
    author = str(editorial.get("author") or "").strip()
    reviewer = str(editorial.get("reviewer") or "").strip()
    updated = str(record.get("updatedAt") or "").strip()[:10]
    meta = []
    if author:
        meta.append(f'<span><b>{esc(labels["author"])}</b> {esc(author)}</span>')
    if reviewer:
        meta.append(f'<span><b>{esc(labels["reviewer"])}</b> {esc(reviewer)}</span>')
    if updated:
        meta.append(f'<span><b>{esc(labels["updated"])}</b> <time datetime="{esc(updated)}">{esc(updated)}</time></span>')
    source_items = []
    for source in editorial.get("sources") if isinstance(editorial.get("sources"), list) else []:
        if not isinstance(source, dict):
            continue
        title = str(source.get("title") or source.get("publisher") or "").strip()
        url = str(source.get("publicUrl") or "").strip()
        if not title:
            continue
        source_items.append(
            f'<li><a href="{esc(url)}" rel="noopener noreferrer">{esc(title)}</a></li>'
            if url.startswith("https://")
            else f"<li>{esc(title)}</li>"
        )
    source_html = (
        f'<div class="trust-sources"><b>{esc(labels["sources"])}</b><ul>{"".join(source_items)}</ul></div>'
        if source_items else ""
    )
    return f'<aside class="article-trust">{"".join(meta)}{source_html}</aside>' if meta or source_html else ""


def content_notice_html(record, language):
    details = record.get("contentDetails") if isinstance(record.get("contentDetails"), dict) else {}
    labels = CONTENT_NOTICE.get(language, CONTENT_NOTICE[DEFAULT_LANGUAGE])
    content_type = record_content_type(record)
    if content_type == "example" and details.get("exampleType") == "demo":
        return f'<aside class="content-notice" role="note">{esc(labels["demo"])}</aside>'
    if content_type == "integration_guide" and details.get("versionCheckedAt"):
        return (
            f'<aside class="content-notice" role="note"><strong>{esc(labels["checked"])}: '
            f'{esc(details["versionCheckedAt"])}</strong> {esc(labels["change"])}</aside>'
        )
    return ""


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
    content_type = record_content_type(record)
    canonical = f"{SITE_ORIGIN}{article_path(language, slug, content_type)}"
    alternate_urls = {
        item: f"{SITE_ORIGIN}{article_path(item, slug, content_type)}"
        for item in record_languages(record)
    }
    hero = str(record.get("heroImage") or "")
    if hero.startswith("/sites/"):
        hero = BLOG_CORE_ORIGIN + hero
    hero_html = ""
    if hero:
        hero_html = (
            f'<figure class="article-hero"><img src="{esc(hero)}" alt="{esc(title)}" '
            'width="1376" height="768" fetchpriority="high"></figure>'
        )
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
    trust_html = editorial_trust_html(record, language)
    notice_html = content_notice_html(record, language)
    primary_cta = record.get("primaryCta") if isinstance(record.get("primaryCta"), dict) else {}
    cta_label = str(primary_cta.get("label") or labels["cta"]).strip()
    cta_url = str(primary_cta.get("url") or "/#create").strip()
    if not cta_url.startswith("/"):
        cta_url = "/#create"
    body = f"""
    {preview_badge}
    <main class="article-layout">
      <article>
        <a class="back-link" href="{esc(content_path(language, content_type))}">← {esc(section_label(language, content_type))}</a>
        <div class="eyebrow">{esc(category)}</div>
        <h1>{esc(title)}</h1>
        <p class="dek">{esc(description)}</p>
        <div class="article-meta">{esc(labels["editorial"])} · {esc(read_minutes)} {esc(labels["minutes"])}</div>
        {notice_html}
        {toc_html}
        {hero_html}
        <div class="article-copy">{article_body}</div>
        {trust_html}
        <aside class="article-cta">
          <div><span>{esc(labels["build"])}</span><strong>{esc(labels["build_copy"])}</strong></div>
          <a href="{esc(cta_url)}" data-event="seo_cta_click" data-page-type="{esc(content_type)}"
             data-content-id="{esc(record.get("id") or slug)}" data-cta-location="article-end">{esc(cta_label)} <span>↗</span></a>
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
        content_type=content_type,
    )


VOID_HTML_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


def top_level_html_blocks(markup):
    """Split trusted, sanitised article HTML into complete top-level elements."""
    blocks = []
    start = None
    depth = 0
    token_pattern = re.compile(r"(?is)<\s*(/?)\s*([a-z][a-z0-9:-]*)\b[^>]*>")
    for match in token_pattern.finditer(markup):
        closing, tag = match.group(1), match.group(2).lower()
        token = match.group(0)
        self_closing = token.rstrip().endswith("/>") or tag in VOID_HTML_TAGS
        if not closing:
            if depth == 0:
                start = match.start()
            if not self_closing:
                depth += 1
            elif depth == 0 and start is not None:
                blocks.append(markup[start:match.end()].strip())
                start = None
        elif depth:
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(markup[start:match.end()].strip())
                start = None
    return [block for block in blocks if block]


def block_has_class(block, class_name):
    opening = re.match(r"(?is)\s*<[^>]+>", block)
    return bool(
        opening
        and re.search(
            rf"""(?is)\bclass\s*=\s*(["'])[^"']*\b{re.escape(class_name)}\b[^"']*\1""",
            opening.group(0),
        )
    )


MONEY_EXPLORE_LABELS = {
    "en": "Explore Georivo",
    "de": "Georivo entdecken",
    "es": "Descubre Georivo",
    "fr": "Découvrez Georivo",
    "ru": "Откройте Georivo",
}

MONEY_HERO_OVERRIDES = {
    "coverage": "/brand/georivo-money-coverage.webp",
    "pricing": "/brand/georivo-money-pricing.webp",
}


def money_plain_text(markup):
    return html.unescape(re.sub(r"(?is)<[^>]+>", " ", str(markup or ""))).strip()


def money_asset_url(value):
    value = str(value or "").strip()
    return BLOG_CORE_ORIGIN + value if value.startswith("/sites/") else value


def money_image_from_block(block):
    match = re.search(r"""(?is)<img\b[^>]*\bsrc\s*=\s*(["'])(.*?)\1""", block)
    return money_asset_url(match.group(2)) if match else ""


def money_image_for_href(href, language, fallbacks, index):
    path = str(href or "").split("?", 1)[0].split("#", 1)[0]
    normalized = "/" + path.strip("/")
    for candidate in load_records(PUBLISHED_ROOT):
        localized = localized_record(candidate, language)
        if not localized:
            continue
        slug = str(localized.get("slug") or candidate.get("slug") or "").strip("/")
        content_type = (
            "money_page" if is_money_page_record(candidate)
            else record_content_type(candidate)
        )
        candidate_path = article_path(language, slug, content_type).rstrip("/") or "/"
        if normalized.rstrip("/") != candidate_path:
            continue
        image = money_asset_url(
            localized.get("heroImage") or candidate.get("heroImage") or ""
        )
        if image:
            return image
    return fallbacks[index % len(fallbacks)] if fallbacks else ""


def money_published_asset_pool(language, excluded, money_slug):
    """Allocate a non-overlapping media library to each root money page."""
    excluded = {money_asset_url(item) for item in excluded if item}
    global_pool = []
    type_order = {
        "example": 0,
        "template": 1,
        "guide": 2,
        "integration_guide": 3,
        "blog": 4,
        "use_case": 5,
        "money_page": 6,
    }
    candidates = []
    for candidate in load_records(PUBLISHED_ROOT):
        localized = localized_record(candidate, language)
        if not localized:
            continue
        candidate_slug = str(
            localized.get("slug") or candidate.get("slug") or ""
        ).strip("/")
        if candidate_slug in MONEY_PAGE_SLUGS:
            # A root money page owns its factory figures. They must not leak
            # into either of the other two pages.
            continue
        content_type = (
            "money_page" if is_money_page_record(candidate)
            else record_content_type(candidate)
        )
        record_images = [
            localized.get("heroImage") or candidate.get("heroImage") or ""
        ]
        record_images.extend(
            match[1]
            for match in re.findall(
                r"""(?is)<img\b[^>]*\bsrc\s*=\s*(["'])(.*?)\1""",
                str(localized.get("draftHtml") or candidate.get("draftHtml") or ""),
            )
        )
        for asset_index, raw_image in enumerate(record_images):
            image = money_asset_url(raw_image)
            if not image or image in excluded:
                continue
            candidates.append(
                (
                    type_order.get(content_type, 9),
                    candidate_slug,
                    asset_index,
                    image,
                )
            )
    for _, _, _, image in sorted(candidates):
        if image not in global_pool:
            global_pool.append(image)

    page_index = MONEY_PAGE_SLUGS.index(money_slug)
    return [
        image
        for index, image in enumerate(global_pool)
        if index % len(MONEY_PAGE_SLUGS) == page_index
    ]


def money_recommendations_html(blocks, images, language):
    links = []
    seen = set()
    faq = []
    for block in blocks:
        if block_has_class(block, "article-faq"):
            faq.append(block)
            continue
        for item in re.findall(r"(?is)<li\b[^>]*>(.*?)</li>", block):
            anchor = re.search(
                r"""(?is)<a\b[^>]*\bhref\s*=\s*(["'])(.*?)\1[^>]*>(.*?)</a>""",
                item,
            )
            if not anchor:
                continue
            href = anchor.group(2).strip()
            if not href or href in seen:
                continue
            description_match = re.search(r"(?is)<span\b[^>]*>(.*?)</span>", item)
            links.append(
                (
                    href,
                    money_plain_text(anchor.group(3)),
                    money_plain_text(description_match.group(1)) if description_match else "",
                    "",
                )
            )
            seen.add(href)
        for anchor_match in re.finditer(
            r"""(?is)<a\b([^>]*\brecommended-card\b[^>]*)>(.*?)</a>""",
            block,
        ):
            opening, content = anchor_match.groups()
            href_match = re.search(r"""\bhref\s*=\s*(["'])(.*?)\1""", opening)
            if not href_match:
                continue
            href = href_match.group(2).strip()
            if not href or href in seen:
                continue
            title_match = re.search(r"(?is)<strong\b[^>]*>(.*?)</strong>", content)
            label_match = re.search(r"(?is)<span\b[^>]*>(.*?)</span>", content)
            links.append(
                (
                    href,
                    money_plain_text(title_match.group(1) if title_match else content),
                    "",
                    money_plain_text(label_match.group(1)) if label_match else "",
                )
            )
            seen.add(href)

    cards = []
    for index, (href, title, description, label) in enumerate(links[:6]):
        title = title[:1].upper() + title[1:] if title else "Georivo"
        image = images[index] if index < len(images) else ""
        media = (
            '<span class="money-recommendation-media" aria-hidden="true">'
            f'<img src="{esc(image)}" alt="" loading="lazy" decoding="async"></span>'
            if image else ""
        )
        cards.append(
            f'<a class="money-recommendation-card" href="{esc(href)}">'
            f'{media}<span class="money-recommendation-copy">'
            f'<small>{esc(label or "Georivo")}</small>'
            f'<strong>{esc(title)}</strong>'
            f'{f"<span>{esc(description)}</span>" if description else ""}'
            '<b aria-hidden="true">↗</b></span></a>'
        )

    explore = ""
    if cards:
        explore = (
            '<section class="money-recommendations">'
            '<span class="money-recommendations-kicker">Georivo</span>'
            f'<h2>{esc(MONEY_EXPLORE_LABELS.get(language, MONEY_EXPLORE_LABELS["en"]))}</h2>'
            f'<div class="money-recommendation-grid">{"".join(cards)}</div>'
            '</section>'
        )
    return explore + "".join(faq)


def money_editorial_html(
    markup, cta_label, cta_url, action, content_id, mid_copy, language, hero, money_slug
):
    """Turn factory article markup into a sales-page section system."""
    blocks = top_level_html_blocks(markup)
    lead = ""
    toc = ""
    intro = []
    groups = []
    current = []
    extras = []

    for block in blocks:
        if block_has_class(block, "article-lead") and not lead:
            lead = block
            continue
        if block_has_class(block, "article-toc") and not toc:
            toc = block
            continue
        if (
            block_has_class(block, "article-related")
            or block_has_class(block, "article-recommended")
            or block_has_class(block, "article-faq")
        ):
            if current:
                groups.append(current)
                current = []
            extras.append(block)
            continue
        if re.match(r"(?is)\s*<h2\b", block):
            if current:
                groups.append(current)
            current = [block]
        elif current:
            current.append(block)
        else:
            intro.append(block)
    if current:
        groups.append(current)

    visual_pool = []
    for block in intro + [item for group in groups for item in group]:
        image = money_image_from_block(block)
        if image and image not in visual_pool:
            visual_pool.append(image)
    hero = money_asset_url(hero)
    if hero and hero not in visual_pool:
        visual_pool.append(hero)
    supporting_pool = money_published_asset_pool(
        language, visual_pool, money_slug
    )

    section_html = []
    if lead or intro:
        section_html.append(
            '<section class="money-opening" data-money-section="opening">'
            f'<div class="money-opening-copy">{lead}</div>'
            f'<div class="money-opening-media">{"".join(intro)}</div>'
            '</section>'
        )

    mid_point = min(3, max(1, len(groups) // 2))
    decorative_index = 0
    for index, group in enumerate(groups, start=1):
        classes = ["money-story-section"]
        if index % 4 == 2:
            classes.append("money-tone-dark")
        elif index % 4 == 0:
            classes.append("money-tone-soft")
        media_blocks = [
            item for item in group if block_has_class(item, "article-figure")
        ]
        copy_blocks = [
            item for item in group if not block_has_class(item, "article-figure")
        ]
        if not media_blocks and decorative_index < len(supporting_pool):
            image = supporting_pool[decorative_index]
            decorative_index += 1
            media_blocks = [
                '<div class="money-section-visual" aria-hidden="true">'
                f'<img src="{esc(image)}" alt="" loading="lazy" decoding="async"></div>'
            ]
            classes.append("money-story-generated-media")
        if media_blocks:
            classes.append("money-story-media")
            if index % 2 == 0:
                classes.append("money-story-reverse")
        heading_blocks = [
            item for item in copy_blocks if re.match(r"(?is)\s*<h2\b", item)
        ]
        text_blocks = [
            item for item in copy_blocks if not re.match(r"(?is)\s*<h2\b", item)
        ]
        section_html.append(
            f'<section class="{" ".join(classes)}" data-money-section="{index:02d}">'
            f'<div class="money-section-number" aria-hidden="true">{index:02d}</div>'
            '<div class="money-section-body">'
            '<div class="money-section-copy">'
            f'<div class="money-section-heading">{"".join(heading_blocks)}</div>'
            f'<div class="money-section-text">{"".join(text_blocks)}</div>'
            '</div>'
            f'<div class="money-section-media">{"".join(media_blocks)}</div>'
            '</div>'
            '</section>'
        )
        if index == mid_point:
            section_html.append(
                '<aside class="money-inline-cta">'
                '<div><span>Georivo</span>'
                f'<strong>{esc(mid_copy)}</strong></div>'
                f'<a href="{esc(cta_url)}"{action} data-event="seo_cta_click" '
                'data-page-type="money_page" '
                f'data-content-id="{esc(content_id)}" data-cta-location="article-middle">'
                f'{esc(cta_label)} <span>↗</span></a></aside>'
            )

    if extras:
        section_html.append(
            '<section class="money-story-section money-story-utility" '
            'data-money-section="resources">'
            '<div class="money-section-number" aria-hidden="true">+</div>'
            '<div class="money-section-body">'
            f'<div class="money-utility-body">'
            f'{money_recommendations_html(extras, supporting_pool[decorative_index:], language)}</div>'
            '</div>'
            '</section>'
        )

    return toc, f'<div class="money-sections">{"".join(section_html)}</div>'


def money_page(record, language=DEFAULT_LANGUAGE, preview=False):
    language = normalize_language(language)
    labels = copy_for(language)
    localized = localized_record(record, language)
    if not localized:
        abort(404)
    record = localized
    slug = str(record.get("slug") or "").strip("/")
    if slug not in MONEY_PAGE_SLUGS:
        abort(404)
    title = str(record.get("title") or "Georivo").strip()
    description = str(record.get("description") or "").strip()
    eyebrow = str(record.get("category") or "Georivo").strip()
    canonical = f"{SITE_ORIGIN}{article_path(language, slug, 'money_page')}"
    alternate_urls = {
        item: f"{SITE_ORIGIN}{article_path(item, slug, 'money_page')}"
        for item in record_languages(record)
    }
    hero = MONEY_HERO_OVERRIDES.get(slug) or str(record.get("heroImage") or "")
    if hero.startswith("/sites/"):
        hero = BLOG_CORE_ORIGIN + hero
    hero_html = (
        f'<img src="{esc(hero)}" alt="" width="1376" height="768" fetchpriority="high">'
        if hero else ""
    )
    body_html = clean_article_markup(record.get("draftHtml") or "")
    primary_cta = record.get("primaryCta") if isinstance(record.get("primaryCta"), dict) else {}
    cta_label = str(primary_cta.get("label") or labels["cta"]).strip()
    cta_url = str(primary_cta.get("url") or "/#create").strip()
    if not cta_url.startswith("/"):
        cta_url = "/#create"
    action = ' data-money-action="checkout"' if slug == "pricing" else ""
    content_id = str(record.get("id") or slug)
    toc_html, editorial_html = money_editorial_html(
        body_html,
        cta_label,
        cta_url,
        action,
        content_id,
        labels["build_copy"],
        language,
        hero,
        slug,
    )
    checker = ""
    if slug == "coverage":
        checker = f"""
        <form class="money-checker" data-money-checker data-locale="{esc(language)}">
          <label for="money-page-address">{esc(record.get("checkerLabel") or "Property address")}</label>
          <div>
            <input id="money-page-address" name="address" type="text" autocomplete="street-address"
                   placeholder="{esc(record.get("checkerPlaceholder") or "Enter a street, city and country")}" required>
            <button type="submit">{esc(record.get("checkerButton") or labels["cta"])} <span>↗</span></button>
          </div>
          <p class="money-checker-result" role="status" aria-live="polite"></p>
          <small>{esc(record.get("checkerNote") or "Real provider response. No raw address is sent to analytics.")}</small>
        </form>
        """
    preview_badge = f'<div class="preview-banner">{esc(labels["draft"])}</div>' if preview else ""
    body = f"""
    {preview_badge}
    <main class="money-page" id="top" data-money-page="{esc(slug)}">
      <section class="money-hero">
        <div class="money-hero-media">{hero_html}</div>
        <div class="money-hero-wash" aria-hidden="true"></div>
        <div class="money-hero-frame">
          <div class="money-hero-copy">
            <div class="section-tag">{esc(eyebrow)}</div>
            <h1>{esc(title)}</h1>
            <p>{esc(description)}</p>
            <a class="money-primary" href="{esc(cta_url)}"{action}
               data-event="seo_cta_click" data-page-type="money_page"
               data-content-id="{esc(record.get("id") or slug)}" data-cta-location="hero">{esc(cta_label)} <span>↗</span></a>
          </div>
          <aside class="money-toc-rail">{toc_html}</aside>
        </div>
      </section>
      {checker}
      <section class="money-content">
        <div class="money-content-inner">
          <div class="money-editorial">{editorial_html}</div>
        </div>
      </section>
      <section class="money-final">
        <span>{esc(record.get("finalEyebrow") or labels["build"])}</span>
        <h2>{esc(record.get("finalTitle") or labels["build_copy"])}</h2>
        <a href="{esc(cta_url)}"{action}
           data-event="seo_cta_click" data-page-type="money_page"
           data-content-id="{esc(record.get("id") or slug)}" data-cta-location="page-end">{esc(cta_label)} <span>↗</span></a>
      </section>
    </main>
    """
    schema_record = {**record, "contentType": "money_page", "pageType": "seo_money_page"}
    return shell(
        f"{title} | Georivo",
        description,
        body,
        canonical,
        article_schema(schema_record, canonical),
        noindex=preview,
        language=language,
        alternate_urls=alternate_urls,
        slug=slug,
        preview_job_id=record.get("id") if preview else None,
        content_type="money_page",
    )


@app.get("/health")
def health():
    return {"ok": True, "service": "georivo-blog", "published": len(load_records(PUBLISHED_ROOT))}


def render_content_index(language=DEFAULT_LANGUAGE, content_type="blog"):
    language = normalize_language(language)
    content_type = normalize_content_type(content_type)
    labels = copy_for(language)
    section_name = section_label(language, content_type)
    posts = [
        record for record in load_records(PUBLISHED_ROOT)
        if record_content_type(record) == content_type
        and not is_money_page_record(record)
    ]
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
        media = (
            f'<img src="{esc(hero)}" alt="{esc(title)}" loading="lazy" width="1376" height="768">'
            if hero else '<div class="card-placeholder">G</div>'
        )
        url = article_path(language, slug, content_type)
        cards.append((slug, f"""
          <article class="post-card">
            <a class="post-media" href="{esc(url)}">{media}</a>
            <div class="post-card-copy">
              <span>{esc(localized.get("category") or labels["journal"])}</span>
              <h2><a href="{esc(url)}">{esc(title)}</a></h2>
              <p>{esc(description)}</p>
              <a class="read-link" href="{esc(url)}">{esc(labels["read"])} <span>↗</span></a>
            </div>
          </article>
        """))
    if not cards:
        cards.append(("", f"""
          <div class="empty-state">
            <span>{esc(labels["coming"])}</span>
            <h2>{esc(labels["empty_title"])}</h2>
            <p>{esc(labels["empty_copy"])}</p>
          </div>
        """))
    hub_title, hub_intro = HUB_COPY.get(language, HUB_COPY["en"]).get(
        content_type,
        (section_name, labels["hero_copy"]),
    )
    template_comparison = ""
    if content_type == "template" and posts:
        template_comparison = f"""
        <section class="hub-comparison section-pad">
          <div class="section-tag">{esc(section_name)}</div>
          <h2>{esc(hub_title)}</h2>
          <p>{esc(hub_intro)}</p>
          <div class="table-scroll"><table>
            <thead><tr><th>Template</th><th>Best for</th><th>Story sequence</th></tr></thead>
            <tbody>
              <tr><td>Property Showcase</td><td>One property and its immediate setting</td><td>Approach, identify, orbit</td></tr>
              <tr><td>Neighborhood Story</td><td>Nearby places and area context</td><td>Places, arrival, property</td></tr>
              <tr><td>Arrival Guide</td><td>A route from a selected place</td><td>Departure, journey, arrival</td></tr>
            </tbody>
          </table></div>
        </section>
        """
    cards_html = "".join(card for _, card in cards)
    if content_type == "guide" and posts:
        grouped = {key: [] for key in ("understand", "compare", "plan", "implement")}
        for slug, card in cards:
            grouped[GUIDE_SLUG_GROUPS.get(slug, "plan")].append(card)
        group_copy = GUIDE_GROUPS.get(language, GUIDE_GROUPS["en"])
        cards_html = "".join(
            f"""
            <section class="guide-group">
              <div class="guide-group-heading">
                <span>{esc(group_copy[key][0])}</span>
                <p>{esc(group_copy[key][1])}</p>
              </div>
              <div class="journal-grid">{''.join(grouped[key])}</div>
            </section>
            """
            for key in ("understand", "compare", "plan", "implement")
            if grouped[key]
        )
        cards_html = f'<div class="guide-groups section-pad">{cards_html}</div>'
    else:
        cards_html = f'<section class="journal-grid section-pad" aria-label="{esc(labels["latest"])}">{cards_html}</section>'
    body = f"""
    <main id="top">
      <section class="journal-hero">
        <div class="journal-hero-image" aria-hidden="true"></div>
        <div class="journal-hero-wash" aria-hidden="true"></div>
        <div class="journal-hero-content">
          <div class="section-tag">{esc(section_name)}</div>
          <h1>{labels["hero_title"] if content_type == "blog" else esc(section_name)}</h1>
          <p>{esc(labels["hero_copy"])}</p>
        </div>
      </section>
      <section class="journal-intro">
        <div class="section-tag">{esc(labels["perspective"])}</div>
        <h2>{labels["intro"] if content_type == "blog" else esc(hub_title)}</h2>
        {f'<p>{esc(hub_intro)}</p>' if content_type != "blog" else ''}
      </section>
      {template_comparison}
      {cards_html}
      <section class="journal-cta">
        <div class="journal-cta-image" aria-hidden="true"></div>
        <div class="journal-cta-wash" aria-hidden="true"></div>
        <div class="journal-cta-copy">
          <span>{esc(labels["cta_kicker"])}</span>
          <h2>{labels["cta_title"]}</h2>
          <a href="/#create" data-event="seo_cta_click" data-page-type="{esc(content_type)}"
             data-content-id="{esc(content_type)}-hub" data-cta-location="hub-end">{esc(labels["cta"])} <span>↗</span></a>
          <p>{esc(labels["cta_note"])}</p>
        </div>
      </section>
    </main>
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Blog" if content_type == "blog" else "CollectionPage",
        "name": section_name,
        "url": f"{SITE_ORIGIN}{content_path(language, content_type)}",
        "description": labels["hero_copy"],
    }
    canonical = f"{SITE_ORIGIN}{content_path(language, content_type)}"
    alternate_urls = {item: f"{SITE_ORIGIN}{content_path(item, content_type)}" for item in LANGUAGES}
    return shell(
        f"{section_name} | Georivo",
        labels["hero_copy"],
        body,
        canonical,
        schema,
        noindex=(len(posts) < 3 if content_type == "integration_guide" else not bool(posts)),
        language=language,
        alternate_urls=alternate_urls,
        content_type=content_type,
    )


def content_index_redirect(section):
    content_type = SECTION_CONTENT_TYPES.get(str(section or "").strip().lower())
    if not content_type:
        abort(404)
    return redirect(content_path(DEFAULT_LANGUAGE, content_type), code=308)


def content_index(section):
    content_type = SECTION_CONTENT_TYPES.get(str(section or "").strip().lower())
    if not content_type:
        abort(404)
    return render_content_index(DEFAULT_LANGUAGE, content_type)


def localized_content_index_redirect(language, section):
    language = str(language or "").strip().lower()
    content_type = SECTION_CONTENT_TYPES.get(str(section or "").strip().lower())
    if language not in LANGUAGES or not content_type:
        abort(404)
    if language == DEFAULT_LANGUAGE:
        return redirect(content_path(DEFAULT_LANGUAGE, content_type), code=308)
    return redirect(content_path(language, content_type), code=308)


def localized_content_index(language, section):
    content_type = SECTION_CONTENT_TYPES.get(str(section or "").strip().lower())
    if language not in LANGUAGES or language == DEFAULT_LANGUAGE or not content_type:
        abort(404)
    return render_content_index(language, content_type)


def published_article(section, slug):
    content_type = SECTION_CONTENT_TYPES.get(str(section or "").strip().lower())
    if not content_type:
        abort(404)
    record = load_content_record(PUBLISHED_ROOT, content_type, slug)
    if not record:
        abort(404)
    if is_money_page_record(record):
        return redirect(article_path(DEFAULT_LANGUAGE, slug, "money_page"), code=301)
    return article_page(record, DEFAULT_LANGUAGE)


def localized_published_article(language, section, slug):
    content_type = SECTION_CONTENT_TYPES.get(str(section or "").strip().lower())
    if language not in LANGUAGES or language == DEFAULT_LANGUAGE or not content_type:
        abort(404)
    record = load_content_record(PUBLISHED_ROOT, content_type, slug)
    if not record:
        abort(404)
    if is_money_page_record(record):
        return redirect(article_path(language, slug, "money_page"), code=301)
    return article_page(record, language)


@app.get("/<money_slug>")
def published_money_page(money_slug):
    if money_slug not in MONEY_PAGE_SLUGS:
        abort(404)
    record = load_money_page_record(PUBLISHED_ROOT, money_slug)
    if not record:
        abort(404)
    return money_page(record, DEFAULT_LANGUAGE)


@app.get("/<language>/<money_slug>")
def localized_published_money_page(language, money_slug):
    if language not in LANGUAGES or language == DEFAULT_LANGUAGE or money_slug not in MONEY_PAGE_SLUGS:
        abort(404)
    record = load_money_page_record(PUBLISHED_ROOT, money_slug)
    if not record:
        abort(404)
    return money_page(record, language)


for _section in SECTION_CONTENT_TYPES:
    app.add_url_rule(
        f"/{_section}",
        endpoint=f"{_section}_index_redirect",
        view_func=content_index_redirect,
        defaults={"section": _section},
    )
    app.add_url_rule(
        f"/{_section}/",
        endpoint=f"{_section}_index",
        view_func=content_index,
        defaults={"section": _section},
    )
    app.add_url_rule(
        f"/{_section}/<slug>/",
        endpoint=f"{_section}_article",
        view_func=published_article,
        defaults={"section": _section},
    )
    app.add_url_rule(
        f"/<language>/{_section}",
        endpoint=f"localized_{_section}_index_redirect",
        view_func=localized_content_index_redirect,
        defaults={"section": _section},
    )
    app.add_url_rule(
        f"/<language>/{_section}/",
        endpoint=f"localized_{_section}_index",
        view_func=localized_content_index,
        defaults={"section": _section},
    )
    app.add_url_rule(
        f"/<language>/{_section}/<slug>/",
        endpoint=f"localized_{_section}_article",
        view_func=localized_published_article,
        defaults={"section": _section},
    )


@app.get("/content-preview/<job_id>")
def draft_preview(job_id):
    record = load_record(DRAFT_ROOT, job_id, "id")
    if not record:
        abort(404)
    language = normalize_language(request.args.get("lang"))
    return (
        money_page(record, language, preview=True)
        if is_money_page_record(record)
        else article_page(record, language, preview=True)
    )


@app.get("/sitemap.xml")
def sitemap():
    groups = [
        (f"{SITE_ORIGIN}/", "1.0", {}),
        (f"{SITE_ORIGIN}/contact", "0.6", {}),
        (f"{SITE_ORIGIN}/terms", "0.3", {}),
        (f"{SITE_ORIGIN}/privacy", "0.3", {}),
    ]
    records = load_records(PUBLISHED_ROOT)
    for slug in MONEY_PAGE_SLUGS:
        record = load_money_page_record(PUBLISHED_ROOT, slug)
        if not record:
            continue
        alternates = {
            language: f"{SITE_ORIGIN}{article_path(language, slug, 'money_page')}"
            for language in record_languages(record)
        }
        groups.extend((url, "0.9", alternates) for url in alternates.values())
    type_counts = {
        content_type: sum(
            1 for record in records
            if record_content_type(record) == content_type and not is_money_page_record(record)
        )
        for content_type in CONTENT_SECTIONS
    }
    available_types = {content_type for content_type, count in type_counts.items() if count}
    available_types.add("blog")
    for content_type in CONTENT_SECTIONS:
        if content_type not in available_types:
            continue
        if content_type == "integration_guide" and type_counts.get(content_type, 0) < 3:
            continue
        section_alternates = {
            item: f"{SITE_ORIGIN}{content_path(item, content_type)}"
            for item in LANGUAGES
        }
        groups.extend((url, "0.8", section_alternates) for url in section_alternates.values())
    for record in records:
        slug = str(record.get("slug") or "").strip("/")
        if slug and not is_money_page_record(record):
            content_type = record_content_type(record)
            article_alternates = {
                language: f"{SITE_ORIGIN}{article_path(language, slug, content_type)}"
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
    match = re.match(r"^/([a-z]{2})/(?:blog|guides|templates|examples|embed|use-cases)(?:/|$)", request.path)
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
