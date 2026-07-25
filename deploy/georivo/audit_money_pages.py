#!/usr/bin/env python3
"""Audit public Georivo SEO money pages after Blog Core deployment."""

from html.parser import HTMLParser
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


SLUGS = ("how-it-works", "coverage", "pricing")
LANGUAGES = ("en", "de", "es", "fr", "ru")


def page_path(language, slug):
    return f"/{slug}" if language == "en" else f"/{language}/{slug}"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1_count = 0
        self.h2_count = 0
        self.figure_count = 0
        self.table_count = 0
        self.details_count = 0
        self.content_depth = 0
        self.content_text = []
        self.canonical = ""
        self.alternates = {}
        self.hero = ""
        self.has_header = False
        self.has_footer = False
        self.money_page = ""
        self.has_checker = False
        self.has_checkout = False
        self.in_hero_media = False
        self.has_editorial = False
        self.has_toc_rail = False
        self.hero_depth = 0
        self.has_toc_in_hero = False
        self.story_section_count = 0
        self.primary_story_classes = []
        self.supporting_visual_count = 0
        self.supporting_visual_images = []
        self.in_supporting_visual = False
        self.recommendation_card_count = 0
        self.has_mid_cta = False
        self.main_depth = 0
        self.main_images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if self.hero_depth:
            self.hero_depth += 1
        elif tag == "section" and "money-hero" in classes:
            self.hero_depth = 1
        if tag == "h1":
            self.h1_count += 1
        elif tag == "h2":
            self.h2_count += 1
        elif tag == "figure":
            self.figure_count += 1
        elif tag == "table":
            self.table_count += 1
        elif tag == "details":
            self.details_count += 1
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        elif tag == "link" and attrs.get("rel") == "alternate":
            self.alternates[attrs.get("hreflang", "")] = attrs.get("href", "")
        elif tag == "header":
            self.has_header = True
        elif tag == "footer":
            self.has_footer = True
        elif tag == "main" and attrs.get("data-money-page"):
            self.money_page = attrs["data-money-page"]
            self.main_depth = 1
        elif tag == "div" and "money-editorial" in classes:
            self.has_editorial = True
        elif tag == "aside" and "money-toc-rail" in classes:
            self.has_toc_rail = True
            self.has_toc_in_hero = bool(self.hero_depth)
        elif tag == "section" and "money-story-section" in classes:
            self.story_section_count += 1
            if "money-story-utility" not in classes:
                self.primary_story_classes.append(set(classes))
        elif tag == "div" and "money-section-visual" in classes:
            self.supporting_visual_count += 1
            self.in_supporting_visual = True
        elif tag == "a" and "money-recommendation-card" in classes:
            self.recommendation_card_count += 1
        elif tag == "aside" and "money-inline-cta" in classes:
            self.has_mid_cta = True
        elif tag == "div" and "money-hero-media" in classes:
            self.in_hero_media = True
        if tag == "div" and "money-content-inner" in classes:
            self.content_depth = 1
        elif tag == "div" and self.content_depth:
            self.content_depth += 1
        elif tag == "img" and self.in_hero_media and not self.hero:
            self.hero = attrs.get("src", "")
        if tag == "img" and self.in_supporting_visual:
            self.supporting_visual_images.append(attrs.get("src", ""))
        if tag == "img" and self.main_depth:
            source = attrs.get("src", "")
            if source:
                self.main_images.append(source)
        if "data-money-checker" in attrs:
            self.has_checker = True
        if attrs.get("data-money-action") == "checkout":
            self.has_checkout = True

    def handle_endtag(self, tag):
        if self.hero_depth:
            self.hero_depth -= 1
        if tag == "div" and self.in_hero_media:
            self.in_hero_media = False
        if tag == "div" and self.in_supporting_visual:
            self.in_supporting_visual = False
        if tag == "div" and self.content_depth:
            self.content_depth -= 1
        if tag == "main" and self.main_depth:
            self.main_depth = 0

    def handle_data(self, data):
        if self.content_depth:
            self.content_text.append(data)

    @property
    def content_words(self):
        return len(re.findall(r"\b[\wÀ-žА-яЁё'-]+\b", " ".join(self.content_text)))


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "GeorivoMoneyPageAudit/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.read().decode("utf-8")


def fetch_without_redirect(url):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, file_pointer, code, message, headers, new_url):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": "GeorivoMoneyPageAudit/1.0"})
    try:
        with opener.open(request, timeout=20) as response:
            return response.status, response.headers.get("Location", "")
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Location", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="https://georivo.com")
    parser.add_argument(
        "--canonical-origin",
        default="",
        help="Expected public origin when requests use a loopback staging origin.",
    )
    args = parser.parse_args()
    origin = args.origin.rstrip("/")
    canonical_origin = (args.canonical_origin or origin).rstrip("/")
    failures = []
    heroes = {}
    page_images = {}
    checked = []

    for language in LANGUAGES:
        for slug in SLUGS:
            path = page_path(language, slug)
            url = origin + path
            try:
                status, markup = fetch(url)
            except Exception as exc:
                failures.append(f"{url}: request failed: {exc}")
                continue
            parsed = PageParser()
            parsed.feed(markup)
            expected_canonical = canonical_origin + path
            expected_alternates = {
                lang: canonical_origin + page_path(lang, slug) for lang in LANGUAGES
            }
            expected_alternates["x-default"] = expected_alternates["en"]
            alternating_media = all(
                "money-story-media" in classes
                and (("money-story-reverse" in classes) == (index % 2 == 0))
                for index, classes in enumerate(parsed.primary_story_classes, start=1)
            )
            checks = {
                "http_200": status == 200,
                "one_h1": parsed.h1_count == 1,
                "canonical": parsed.canonical == expected_canonical,
                "hreflang": all(
                    parsed.alternates.get(lang) == target
                    for lang, target in expected_alternates.items()
                ),
                "shared_header": parsed.has_header,
                "shared_footer": parsed.has_footer,
                "money_template": parsed.money_page == slug,
                "commercial_sections": (
                    parsed.has_editorial
                    and parsed.has_toc_rail
                    and parsed.has_toc_in_hero
                    and parsed.story_section_count >= 7
                    and parsed.supporting_visual_count >= 4
                    and len(parsed.supporting_visual_images)
                    == len(set(parsed.supporting_visual_images))
                    and alternating_media
                    and parsed.recommendation_card_count >= 3
                    and "article-related" not in markup
                    and "article-recommended" not in markup
                    and parsed.has_mid_cta
                ),
                "hero": bool(parsed.hero),
                "long_form": parsed.content_words >= 1200,
                "sections": parsed.h2_count >= 7,
                "editorial_images": parsed.figure_count == 3,
                "comparison_table": parsed.table_count >= 1,
                "faq": parsed.details_count >= 5,
                "coverage_checker": slug != "coverage" or parsed.has_checker,
                "pricing_checkout": slug != "pricing" or parsed.has_checkout,
            }
            for name, ok in checks.items():
                if not ok:
                    failures.append(f"{url}: {name} failed")
            heroes.setdefault(slug, parsed.hero)
            page_images[(language, slug)] = set(parsed.main_images)
            checked.append({"url": url, **checks})

            legacy_path = (
                f"/use-cases/{slug}/"
                if language == "en"
                else f"/{language}/use-cases/{slug}/"
            )
            legacy_url = origin + legacy_path
            try:
                legacy_status, legacy_location = fetch_without_redirect(legacy_url)
                resolved_location = urllib.parse.urljoin(legacy_url, legacy_location)
                if legacy_status != 301 or resolved_location != expected_canonical:
                    failures.append(
                        f"{legacy_url}: expected 301 to {expected_canonical}, "
                        f"got {legacy_status} to {resolved_location}"
                    )
            except Exception as exc:
                failures.append(f"{legacy_url}: redirect check failed: {exc}")

    if len(set(heroes.values())) != len(SLUGS):
        failures.append(f"Money-page heroes are not unique: {heroes}")
    for language in LANGUAGES:
        for index, slug in enumerate(SLUGS):
            for other_slug in SLUGS[index + 1:]:
                overlap = (
                    page_images.get((language, slug), set())
                    & page_images.get((language, other_slug), set())
                )
                if overlap:
                    failures.append(
                        f"{language}: {slug} and {other_slug} reuse money-page images: "
                        f"{sorted(overlap)}"
                    )

    try:
        _, sitemap = fetch(origin + "/sitemap.xml")
        root = ET.fromstring(sitemap)
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [item.text for item in root.findall(".//s:loc", namespace)]
        for language in LANGUAGES:
            for slug in SLUGS:
                expected = canonical_origin + page_path(language, slug)
                if locations.count(expected) != 1:
                    failures.append(
                        f"sitemap: expected exactly one {expected}, found {locations.count(expected)}"
                    )
    except Exception as exc:
        failures.append(f"sitemap: {exc}")

    print(json.dumps(
        {"ok": not failures, "checked": checked, "heroes": heroes, "failures": failures},
        indent=2,
    ))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
