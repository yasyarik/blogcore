import re
import time
import urllib.request
from html.parser import HTMLParser


class FirstElementExtractor(HTMLParser):
    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self, target):
        super().__init__(convert_charrefs=False)
        self.target = target
        self.depth = 0
        self.parts = []
        self.complete = False

    def handle_starttag(self, tag, attrs):
        if self.complete:
            return
        if self.depth or tag == self.target:
            self.parts.append(self.get_starttag_text())
            if tag not in self.VOID_ELEMENTS:
                self.depth += 1

    def handle_startendtag(self, tag, attrs):
        if self.depth:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if not self.depth:
            return
        self.parts.append(f"</{tag}>")
        self.depth -= 1
        if self.depth == 0:
            self.complete = True

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)

    def handle_entityref(self, name):
        if self.depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name):
        if self.depth:
            self.parts.append(f"&#{name};")

    def markup(self):
        return "".join(self.parts) if self.complete else ""


class HeadAssetsExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        values = dict(attrs)
        rel = str(values.get("rel") or "").lower()
        href = str(values.get("href") or "").strip()
        if "stylesheet" in rel and href and href not in self.stylesheets:
            self.stylesheets.append(href)


def extract_first_element(markup, tag):
    parser = FirstElementExtractor(tag)
    parser.feed(markup or "")
    return parser.markup()


class LiveSiteChrome:
    def __init__(
        self,
        origin,
        cache_seconds=300,
        fallback_stylesheet="",
        stylesheet_href_pattern="",
    ):
        self.origin = str(origin or "").rstrip("/")
        self.cache_seconds = max(30, int(cache_seconds))
        self.fallback_stylesheet = fallback_stylesheet
        self.stylesheet_href_pattern = stylesheet_href_pattern
        self._cache = {
            "header": "",
            "footer": "",
            "stylesheets": [],
            "stylesheet": fallback_stylesheet,
            "checked_at": 0.0,
        }

    def get(self):
        now = time.monotonic()
        if (
            self._cache["header"]
            and self._cache["footer"]
            and now - self._cache["checked_at"] < self.cache_seconds
        ):
            return dict(self._cache)
        try:
            source_request = urllib.request.Request(
                f"{self.origin}/",
                headers={"User-Agent": "BlogCoreNativeChrome/1.0"},
            )
            with urllib.request.urlopen(source_request, timeout=5) as response:
                homepage = response.read(1_000_000).decode("utf-8", errors="ignore")
            header = extract_first_element(homepage, "header")
            footer = extract_first_element(homepage, "footer")
            assets = HeadAssetsExtractor()
            assets.feed(homepage)
            stylesheet = self.fallback_stylesheet
            if self.stylesheet_href_pattern:
                match = re.search(self.stylesheet_href_pattern, homepage)
                if match:
                    stylesheet = match.group("href")
            elif assets.stylesheets:
                stylesheet = assets.stylesheets[0]
            if header and footer:
                self._cache.update(
                    {
                        "header": header,
                        "footer": footer,
                        "stylesheets": assets.stylesheets,
                        "stylesheet": stylesheet,
                        "checked_at": now,
                    }
                )
        except (OSError, ValueError):
            pass
        return dict(self._cache)
