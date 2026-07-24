#!/usr/bin/env python3
"""Audit Georivo typed drafts and published records against the factory contract."""

import argparse
import html as html_lib
import json
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

from seed_content_plan import all_jobs


LANGUAGES = ("en", "de", "es", "fr", "ru")
MODEL_OUTPUT_ARTIFACT_PATTERN = re.compile(
    r"(?:```(?:json)?|"
    r"\b(?:chain|train)_of_thought\b|"
    r"\bof_thought(?:_and_[a-z0-9_]+)?\b|"
    r"\bjson_block\b|"
    r"\baccording_to_(?:the_)?rules\b|"
    r"\b(?:here is|let(?:'s| us))\s+(?:the\s+)?final\s+(?:json|output)\b|"
    r"\bsingle[- ]line,\s*valid\s+json\b|"
    r"\b(?:assistant|developer|system)\s*(?:message|prompt)\b)",
    re.I,
)


def text_words(markup):
    text = re.sub(r"(?is)<[^>]+>", " ", markup or "")
    return len(re.findall(r"\b[\w'-]+\b", text))


def html_text(markup):
    return re.sub(
        r"\s+",
        " ",
        html_lib.unescape(re.sub(r"(?is)<[^>]+>", " ", markup or "")),
    ).strip()


def has_limitations_heading(markup):
    return bool(
        re.search(
            r"(?is)<h2[^>]*>[^<]*(?:limitation|suitability|not for|when not|"
            r"einschränkung|eignung|límite|límites|limitación|limitaciones|idoneidad|"
            r"limite|limites|adéquation|ограничение|ограничения|применимость|не подходит)",
            markup or "",
        )
    )


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "GeorivoContentAudit/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def audit(db_path, native_root, public_origin, check_public):
    expected = {sources["targetPath"]: (item, content_type) for item, content_type, sources in all_jobs()}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        select * from content_jobs
        where site_id=14 and json_extract(sources_json,'$.contentType') <> 'blog'
        """
    ).fetchall()
    by_path = {}
    for row in rows:
        sources = json.loads(row["sources_json"] or "{}")
        by_path[sources.get("targetPath")] = (row, sources)
    report = {"expected": len(expected), "found": len(by_path), "passed": 0, "failed": 0, "pages": []}
    for target_path, (brief_item, expected_type) in expected.items():
        errors = []
        pair = by_path.get(target_path)
        if not pair:
            report["pages"].append({"path": target_path, "errors": ["missing task"]})
            report["failed"] += 1
            continue
        row, sources = pair
        if sources.get("contentType") != expected_type:
            errors.append(f"content type is {sources.get('contentType')}, expected {expected_type}")
        if row["status"] not in {"DRAFT", "PUBLISHED"}:
            errors.append(f"status is {row['status']}: {row['error'] or ''}".strip())
        brief = sources.get("pageBrief") if isinstance(sources.get("pageBrief"), dict) else {}
        generated = sources.get("generatedContentContract") if isinstance(sources.get("generatedContentContract"), dict) else {}
        editorial = brief.get("editorial") if isinstance(brief.get("editorial"), dict) else {}
        if row["title"] != brief.get("h1"):
            errors.append("EN title does not match the approved H1")
        if row["description"] != brief.get("metaDescription"):
            errors.append("EN description does not match the approved meta description")
        direct_answer = str(brief.get("directAnswer") or "").strip()
        if direct_answer and direct_answer not in html_text(row["draft_html"] or ""):
            errors.append("approved direct answer is missing from EN content")
        for field in ("author", "reviewer", "owner", "reviewDueAt", "reviewCadence", "factCheckedAt"):
            if not str(editorial.get(field) or "").strip():
                errors.append(f"editorial.{field} is missing")
        if not brief.get("sourceReferences"):
            errors.append("source references are missing")
        cta = brief.get("primaryCta") if isinstance(brief.get("primaryCta"), dict) else {}
        if not cta.get("label") or not str(cta.get("url") or "").startswith("/"):
            errors.append("primary CTA contract is incomplete")
        html = row["draft_html"] or ""
        artifact = MODEL_OUTPUT_ARTIFACT_PATTERN.search(html_text(html))
        if artifact:
            errors.append(f"EN contains a model control artifact: {artifact.group(0)[:80]}")
        if text_words(html) < 1200:
            errors.append("EN content is below 1200 words")
        if html.count('class="article-figure"') != 3:
            errors.append("EN must contain exactly 3 inline figures")
        if html.count('class="recommended-card"') != 3:
            errors.append("EN must contain exactly 3 Recommended next cards")
        if html.count("<details>") < 5:
            errors.append("EN must contain at least 5 FAQ items")
        if html.count("<h2") < 6:
            errors.append("EN must contain at least 6 H2 sections")
        if not has_limitations_heading(html):
            errors.append("EN standalone limitations or suitability section is missing")
        internal_links = generated.get("internalLinks") if isinstance(generated.get("internalLinks"), list) else []
        recommended = generated.get("recommendedNext") if isinstance(generated.get("recommendedNext"), list) else []
        if len(internal_links) < 4:
            errors.append("EN generated contract has fewer than 4 contextual internal links")
        if len(recommended) != 3:
            errors.append("EN generated contract must contain exactly 3 Recommended next links")
        approved_urls = {
            str(item.get("url") or "").strip() if isinstance(item, dict) else str(item or "").strip()
            for item in brief.get("approvedInternalLinks", [])
        }
        generated_urls = {
            str(item.get("url") or "").strip()
            for item in internal_links + recommended
            if isinstance(item, dict)
        }
        if approved_urls and not generated_urls.issubset(approved_urls):
            errors.append("generated links contain a URL outside the approved brief")
        if not row["hero_image"]:
            errors.append("hero image is missing")
        localizations = conn.execute(
            "select language,draft_html from content_job_localizations where job_id=? order by language",
            (row["id"],),
        ).fetchall()
        locale_map = {item["language"]: item["draft_html"] or "" for item in localizations}
        for language in LANGUAGES[1:]:
            localized = locale_map.get(language)
            if not localized:
                errors.append(f"{language} localization is missing")
                continue
            artifact = MODEL_OUTPUT_ARTIFACT_PATTERN.search(html_text(localized))
            if artifact:
                errors.append(
                    f"{language} contains a model control artifact: {artifact.group(0)[:80]}"
                )
            if text_words(localized) < 1000:
                errors.append(f"{language} content is below 1000 words")
            if localized.count('class="article-figure"') != 3:
                errors.append(f"{language} must contain exactly 3 inline figures")
            if localized.count('class="recommended-card"') != 3:
                errors.append(f"{language} must contain exactly 3 Recommended next cards")
            if not has_limitations_heading(localized):
                errors.append(f"{language} standalone limitations or suitability section is missing")
        draft_path = native_root / "drafts" / f"{row['id']}.json"
        published_prefix = {
            "guide": "guides",
            "template": "templates",
            "example": "examples",
            "integration_guide": "embed",
        }[expected_type]
        published_path = native_root / "published" / f"{published_prefix}--{row['slug']}.json"
        record_path = published_path if row["status"] == "PUBLISHED" else draft_path
        if not record_path.exists():
            errors.append(f"native record missing: {record_path}")
        else:
            try:
                record = json.loads(record_path.read_text(encoding="utf-8"))
                if record.get("contentType") != expected_type:
                    errors.append("native record contentType mismatch")
                if sorted(record.get("translations", {})) != sorted(LANGUAGES[1:]):
                    errors.append("native record does not contain all translations")
                if record.get("targetPath") != target_path:
                    errors.append("native record targetPath mismatch")
                if not record.get("editorial"):
                    errors.append("native record trust metadata is missing")
                record_editorial = record.get("editorial") if isinstance(record.get("editorial"), dict) else {}
                if not record_editorial.get("sources"):
                    errors.append("native record source references are missing")
                if not record.get("primaryCta"):
                    errors.append("native record primary CTA is missing")
            except (OSError, json.JSONDecodeError) as error:
                errors.append(f"invalid native record: {error}")
        if check_public and row["status"] == "PUBLISHED":
            for language in LANGUAGES:
                prefix = "" if language == "en" else f"/{language}"
                url = f"{public_origin}{prefix}{target_path}"
                try:
                    status, page = fetch(url)
                    if status != 200:
                        errors.append(f"{language} public status is {status}")
                    if 'noindex,nofollow' in page:
                        errors.append(f"{language} published page is noindex")
                    if f'<link rel="canonical" href="{url}">' not in page:
                        errors.append(f"{language} canonical mismatch")
                    if 'hreflang="x-default"' not in page:
                        errors.append(f"{language} x-default missing")
                    if 'data-event="seo_cta_click"' not in page:
                        errors.append(f"{language} CTA analytics attribute missing")
                except (urllib.error.URLError, TimeoutError) as error:
                    errors.append(f"{language} fetch failed: {error}")
        page_result = {
            "id": row["id"],
            "path": target_path,
            "type": expected_type,
            "status": row["status"],
            "errors": errors,
        }
        report["pages"].append(page_result)
        if errors:
            report["failed"] += 1
        else:
            report["passed"] += 1
    conn.close()
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--native-root", default="/var/www/georivo-blog/data/blog-core")
    parser.add_argument("--public-origin", default="https://georivo.com")
    parser.add_argument("--check-public", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.db), Path(args.native_root), args.public_origin.rstrip("/"), args.check_public)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(1 if result["failed"] else 0)
