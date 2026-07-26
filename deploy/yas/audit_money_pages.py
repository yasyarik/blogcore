#!/usr/bin/env python3
"""Fail closed when the generated YAS money-page set is incomplete or generic."""

import argparse
import json
import re
import sqlite3
from html import unescape
from pathlib import Path


EXPECTED = {
    "/shopify-development",
    "/ai-automation",
    "/product-development",
    "/startup-advisory",
    "/method",
    "/research",
    "/systems",
    "/workflows",
    "/build",
}
RANGES = {
    "money_service": (450, 1350),
    "money_hub": (400, 1100),
    "money_tool": (300, 850),
    "money_proof": (350, 1000),
}
BANNED = re.compile(
    r"\b(?:in today'?s (?:fast-paced|digital|ever-changing) world|"
    r"ever-evolving landscape|game[- ]changer|delve into|unlock the power|"
    r"revolutioni[sz]e|seamless(?:ly)? integrate|one-stop solution)\b",
    re.I,
)
AGENCY_VOICE = re.compile(
    r"\b(?:our team|our experts|our methodology|we are committed|"
    r"high-value|solid foundation|robust solution|cutting-edge)\b",
    re.I,
)


def plain(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def audit(db_path: Path, site_id: int):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """select * from content_jobs where site_id=?
           and json_extract(sources_json,'$.contentType')='seo_money_page'""",
        (site_id,),
    ).fetchall()
    errors = []
    found = set()
    summary = []
    for row in rows:
        sources = json.loads(row["sources_json"])
        path = sources.get("targetPath")
        found.add(path)
        brief = sources.get("pageBrief") or {}
        profile = brief.get("contentProfile")
        text = plain(row["draft_html"])
        words = len(re.findall(r"\b[\w'-]+\b", text))
        locales = conn.execute(
            "select language,draft_html from content_job_localizations where job_id=? order by language",
            (row["id"],),
        ).fetchall()
        summary.append({"path": path, "status": row["status"], "profile": profile, "words": words, "locales": [item["language"] for item in locales]})
        if row["status"] not in {"DRAFT", "PUBLISHED"}:
            errors.append(f"{path}: status {row['status']}")
        low, high = RANGES.get(profile, (1200, 2200))
        if not low <= words <= high:
            errors.append(f"{path}: {words} words outside {low}-{high}")
        if len(locales) != 2 or {item["language"] for item in locales} != {"ru", "de"}:
            errors.append(f"{path}: expected RU and DE localizations")
        if (match := BANNED.search(text)):
            errors.append(f"{path}: generic phrase `{match.group(0)}`")
        if (match := AGENCY_VOICE.search(text)):
            errors.append(f"{path}: anonymous agency phrase `{match.group(0)}`")
        if row["draft_html"].count('class="article-figure"') != 3:
            errors.append(f"{path}: expected exactly 3 inline figures")
        if row["draft_html"].count("<h2") < 4:
            errors.append(f"{path}: expected at least 4 H2 sections")
        for localized in locales:
            localized_text = plain(localized["draft_html"])
            if len(localized_text) < 1200:
                errors.append(f"{path}/{localized['language']}: localization is unexpectedly short")
            if (match := BANNED.search(localized_text)):
                errors.append(f"{path}/{localized['language']}: generic phrase `{match.group(0)}`")
    if found != EXPECTED:
        errors.append(f"page set mismatch: missing={sorted(EXPECTED-found)} extra={sorted(found-EXPECTED)}")
    conn.close()
    print(json.dumps({"pages": summary, "errors": errors}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=12)
    args = parser.parse_args()
    audit(Path(args.db), args.site_id)
