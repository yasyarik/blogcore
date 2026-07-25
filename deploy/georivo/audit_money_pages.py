#!/usr/bin/env python3
"""Audit public Georivo SEO money pages after Blog Core deployment."""

from html.parser import HTMLParser
import argparse
import json
import sys
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
        self.canonical = ""
        self.alternates = {}
        self.hero = ""
        self.has_header = False
        self.has_footer = False
        self.money_page = ""
        self.has_checker = False
        self.has_checkout = False
        self.in_hero_media = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "h1":
            self.h1_count += 1
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
        elif tag == "div" and "money-hero-media" in classes:
            self.in_hero_media = True
        elif tag == "img" and self.in_hero_media and not self.hero:
            self.hero = attrs.get("src", "")
        if "data-money-checker" in attrs:
            self.has_checker = True
        if attrs.get("data-money-action") == "checkout":
            self.has_checkout = True

    def handle_endtag(self, tag):
        if tag == "div" and self.in_hero_media:
            self.in_hero_media = False


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "GeorivoMoneyPageAudit/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.read().decode("utf-8")


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
                "hero": bool(parsed.hero),
                "coverage_checker": slug != "coverage" or parsed.has_checker,
                "pricing_checkout": slug != "pricing" or parsed.has_checkout,
            }
            for name, ok in checks.items():
                if not ok:
                    failures.append(f"{url}: {name} failed")
            heroes.setdefault(slug, parsed.hero)
            checked.append({"url": url, **checks})

    if len(set(heroes.values())) != len(SLUGS):
        failures.append(f"Money-page heroes are not unique: {heroes}")

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
