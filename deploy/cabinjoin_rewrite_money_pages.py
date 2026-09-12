#!/usr/bin/env python3
"""Rewrite text in CabinJoin's existing Blog Core money pages without regenerating them."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from urllib import error, request

MODEL = "gemini-3.5-flash"
PROMPT_VERSION = "cabinjoin-money-copy-v1"
SITE_ID = 15
SLUGS = ("how-it-works", "for-organizers", "for-boat-owners")
LANGUAGES = ("en", "ru", "fr", "es", "de")
TAG_RE = re.compile(r"<[^>]+>")
TOKEN_RE = re.compile(r"(<[^>]+>)")
SRC_RE = re.compile(r"""<img[^>]+src=["']([^"']+)""", re.I)

FACTS = """
CabinJoin is a Polish yacht marketplace operated by YAS SPÓLKA Z OGRANICZONA
ODPOWIEDZIALNOSCIA, NIP/VAT PL6793327784, KRS 0001166122, REGON 541401303,
UL. SZLAK 77-222, 31-153 Kraków, Poland.

Four audiences:
1. Solo travellers or pairs request a place or cabin in an organiser-led trip.
2. Private groups request the whole yacht.
3. An organiser first obtains and pays for a confirmed charter, then creates
   one public trip on that yacht and dates, sets rules and approves participants.
4. A boat owner/operator lists verified supply and confirms requests.

Participation is request first, organiser approval, supported secure payment,
then crew chat. External supplier yacht listings are managed requests with
indicative stored prices; dates, final price, conditions and authorised payment
route require supplier confirmation. Direct owner/organiser payments can use
verified Stripe connected accounts where supported. CabinJoin records its
disclosed platform fee. Owner and organiser verification requires evidence.
Imported supplier publication confirms source-record integrity, not live
availability. Reviews require a confirmed booking, completed trip and moderation.

Never invent testimonials, customer counts, supplier performance, live
availability, final prices, insurance cover, legal conclusions, safety
guarantees or compatibility promises. Keep CabinJoin's calm, emotional,
editorial maritime voice. Avoid dry instruction-manual language and generic
luxury clichés.
""".strip()


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def tag_hash(value: str) -> str:
    return sha("".join(TAG_RE.findall(value)))


def image_sources(value: str) -> list[str]:
    return SRC_RE.findall(value)


def text_manifest(value: str) -> list[dict[str, str]]:
    manifest: list[dict[str, str]] = []
    for index, token in enumerate(TOKEN_RE.split(value)):
        if not token or token.startswith("<") or not html.unescape(token).strip():
            continue
        manifest.append({"id": f"body.{index}", "text": html.unescape(token).strip()})
    return manifest


def apply_manifest(value: str, replacements: dict[str, str]) -> str:
    tokens = TOKEN_RE.split(value)
    expected = {item["id"] for item in text_manifest(value)}
    if set(replacements) != expected:
        raise RuntimeError("Gemini replacement IDs do not match the existing HTML text nodes")
    for item_id, text in replacements.items():
        index = int(item_id.split(".", 1)[1])
        if not text.strip():
            raise RuntimeError(f"Empty replacement for {item_id}")
        tokens[index] = html.escape(text.strip(), quote=False)
    return "".join(tokens)


def parse_json_text(value: str):
    cleaned = re.sub(r"^```(?:json)?\s*", "", value.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        starts = [position for position in (cleaned.find("{"), cleaned.find("[")) if position >= 0]
        if not starts:
            raise
        start = min(starts)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        return json.loads(cleaned[start : end + 1])


def gemini_json(system: str, prompt: str):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY must be configured")
    if os.environ.get("GEMINI_CONTENT_MODEL", MODEL) != MODEL:
        raise RuntimeError(f"Gemini content model must be {MODEL}")
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        f"?key={key}"
    )
    schema = {
        "type": "object",
        "required": ["title", "description", "replacements"],
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "replacements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "text"],
                    "additionalProperties": False,
                    "properties": {"id": {"type": "string"}, "text": {"type": "string"}},
                },
            },
        },
    }
    payload = json.dumps(
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
                "responseJsonSchema": schema,
            },
        }
    ).encode()
    last = None
    for attempt in range(1, 5):
        try:
            req = request.Request(
                endpoint, data=payload, headers={"Content-Type": "application/json"}
            )
            with request.urlopen(req, timeout=300) as response:
                body = json.load(response)
            candidate = body["candidates"][0]
            if candidate.get("finishReason") != "STOP":
                raise RuntimeError("Gemini returned an incomplete response")
            text = "".join(
                part.get("text", "") for part in candidate["content"].get("parts", [])
            )
            return parse_json_text(text)
        except error.HTTPError as exc:
            last = RuntimeError(f"Gemini request failed with HTTP {exc.code}")
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise last
        except TimeoutError:
            last = RuntimeError("Gemini request timed out")
            if attempt == 4:
                raise last
        time.sleep(attempt * 2.5)
    raise last or RuntimeError("Gemini request failed")


def validate_response(source_html: str, response: dict) -> dict[str, str]:
    if not isinstance(response, dict):
        raise RuntimeError("Gemini response is not an object")
    title = str(response.get("title") or "").strip()
    description = str(response.get("description") or "").strip()
    items = response.get("replacements")
    if not title or not description or not isinstance(items, list):
        raise RuntimeError("Gemini response misses title, description or replacements")
    replacements: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("Invalid replacement item")
        item_id = str(item.get("id") or "")
        text = str(item.get("text") or "").strip()
        if not item_id or not text or item_id in replacements:
            raise RuntimeError("Invalid or duplicate replacement")
        replacements[item_id] = text
    updated_html = apply_manifest(source_html, replacements)
    if tag_hash(source_html) != tag_hash(updated_html):
        raise RuntimeError("HTML structure changed")
    if image_sources(source_html) != image_sources(updated_html):
        raise RuntimeError("Image references changed")
    return {"title": title, "description": description, "html": updated_html}


def generate_page(slug: str, language: str, source: dict, english_final: dict | None):
    manifest = text_manifest(source["html"])
    language_name = {
        "en": "English",
        "ru": "Russian",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
    }[language]
    if language == "en":
        instruction = (
            "Rewrite the existing English text nodes. Keep one replacement for every supplied ID. "
            "Do not add, remove or combine nodes."
        )
        semantic_source = ""
    else:
        instruction = (
            f"Translate directly from FINAL ENGLISH into natural {language_name}. "
            "Use the existing localized nodes only as slot/context guidance. "
            "Keep one replacement for every existing target ID."
        )
        semantic_source = f"\nFINAL ENGLISH:\n{json.dumps(english_final, ensure_ascii=False)}\n"
    system = (
        f"You are CabinJoin's senior {language_name} product editor. {instruction} "
        "Preserve links, HTML, images and design by returning text replacements only. "
        "Keep labels concise and body prose emotionally intelligent, specific and factual. "
        "Never claim booking, confirmation or payment before the documented product step."
    )
    prompt = (
        f"PAGE: {slug}\nLANGUAGE: {language}\n\nFACTS:\n{FACTS}\n"
        f"{semantic_source}\nCURRENT TITLE: {source['title']}\n"
        f"CURRENT DESCRIPTION: {source['description']}\n"
        f"TARGET TEXT NODES:\n{json.dumps(manifest, ensure_ascii=False)}"
    )
    draft = validate_response(source["html"], gemini_json(system, prompt))
    review_manifest = text_manifest(draft["html"])
    review = validate_response(
        source["html"],
        gemini_json(
            (
                f"You are the final CabinJoin {language_name} fact-checker. Correct the draft "
                "against the facts and final English meaning. Remove generic AI language, "
                "literal translation, unsupported promises and dry manual-style copy. "
                "Return every target ID exactly once; preserve all HTML and image structure."
            ),
            (
                f"PAGE: {slug}\nLANGUAGE: {language}\n\nFACTS:\n{FACTS}\n"
                f"{semantic_source}\nDRAFT TITLE: {draft['title']}\n"
                f"DRAFT DESCRIPTION: {draft['description']}\n"
                f"DRAFT TEXT NODES:\n{json.dumps(review_manifest, ensure_ascii=False)}"
            ),
        ),
    )
    return review


def load_rows(connection):
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        """
        select id,slug,status,title,description,hero_image,draft_html,sources_json
        from content_jobs
        where site_id=? and slug in (?,?,?)
        order by slug
        """,
        (SITE_ID, *SLUGS),
    ).fetchall()
    if len(rows) != len(SLUGS) or any(row["status"] != "PUBLISHED" for row in rows):
        raise RuntimeError("All three existing CabinJoin money pages must be published")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--blog-root", default="/var/www/blog.yas.ooo")
    parser.add_argument(
        "--published-root", default="/var/www/cabinjoin-content/data/blog-core/published"
    )
    parser.add_argument("--output", default="/var/lib/cabinjoin/gemini-money-pages.json")
    args = parser.parse_args()
    blog_root = Path(args.blog_root).resolve()
    database = blog_root / "data/blog_core.sqlite3"
    published_root = Path(args.published_root).resolve()
    output_path = Path(args.output).resolve()
    connection = sqlite3.connect(database)
    rows = load_rows(connection)
    result = {
        "model": MODEL,
        "promptVersion": PROMPT_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "pages": {},
    }
    for row in rows:
        slug = row["slug"]
        print(f"Gemini money page: {slug} English", flush=True)
        english_source = {
            "title": row["title"],
            "description": row["description"] or "",
            "html": row["draft_html"],
        }
        english = generate_page(slug, "en", english_source, None)
        localized_rows = connection.execute(
            """
            select language,title,description,draft_html
            from content_job_localizations
            where site_id=? and job_id=?
            order by language
            """,
            (SITE_ID, row["id"]),
        ).fetchall()
        by_language = {localized["language"]: localized for localized in localized_rows}
        if set(by_language) != set(LANGUAGES[1:]):
            raise RuntimeError(f"{slug} does not have exactly RU/FR/ES/DE localizations")
        translations = {}
        for language in LANGUAGES[1:]:
            print(f"Gemini money page: {slug} {language}", flush=True)
            localized = by_language[language]
            translations[language] = generate_page(
                slug,
                language,
                {
                    "title": localized["title"],
                    "description": localized["description"] or "",
                    "html": localized["draft_html"],
                },
                english,
            )
        result["pages"][slug] = {
            "id": row["id"],
            "heroImage": row["hero_image"],
            "english": english,
            "translations": translations,
            "audit": {
                "englishTagHashBefore": tag_hash(row["draft_html"]),
                "englishTagHashAfter": tag_hash(english["html"]),
                "englishImagesBefore": image_sources(row["draft_html"]),
                "englishImagesAfter": image_sources(english["html"]),
                "localizedTagHashesBefore": {
                    language: tag_hash(by_language[language]["draft_html"])
                    for language in LANGUAGES[1:]
                },
                "localizedTagHashesAfter": {
                    language: tag_hash(translations[language]["html"])
                    for language in LANGUAGES[1:]
                },
            },
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(output_path, 0o600)
    if not args.apply:
        print(f"Dry run complete: {output_path}", flush=True)
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = Path("/var/backups/blog-core") / f"cabinjoin-money-copy-{timestamp}"
    backup_root.mkdir(parents=True, mode=0o700)
    shutil.copy2(database, backup_root / database.name)
    for slug in SLUGS:
        source = published_root / f"use-cases--{slug}.json"
        shutil.copy2(source, backup_root / source.name)

    now = datetime.now(timezone.utc).isoformat()
    with connection:
        for slug, page in result["pages"].items():
            connection.execute(
                """
                update content_jobs
                set title=?,description=?,draft_html=?,updated_at=?
                where site_id=? and id=? and slug=? and status='PUBLISHED'
                """,
                (
                    page["english"]["title"],
                    page["english"]["description"],
                    page["english"]["html"],
                    now,
                    SITE_ID,
                    page["id"],
                    slug,
                ),
            )
            for language, localized in page["translations"].items():
                connection.execute(
                    """
                    update content_job_localizations
                    set title=?,description=?,draft_html=?
                    where site_id=? and job_id=? and language=?
                    """,
                    (
                        localized["title"],
                        localized["description"],
                        localized["html"],
                        SITE_ID,
                        page["id"],
                        language,
                    ),
                )

    for slug, page in result["pages"].items():
        target = published_root / f"use-cases--{slug}.json"
        payload = json.loads(target.read_text(encoding="utf-8"))
        original_hero = payload.get("heroImage")
        original_images = {
            "en": image_sources(payload.get("draftHtml", "")),
            **{
                language: image_sources(localized.get("draftHtml", ""))
                for language, localized in payload.get("translations", {}).items()
            },
        }
        payload["title"] = page["english"]["title"]
        payload["description"] = page["english"]["description"]
        payload["draftHtml"] = page["english"]["html"]
        payload["updatedAt"] = now
        payload["publishedAt"] = now
        for language, localized in page["translations"].items():
            payload["translations"][language]["title"] = localized["title"]
            payload["translations"][language]["description"] = localized["description"]
            payload["translations"][language]["draftHtml"] = localized["html"]
        if payload.get("heroImage") != original_hero:
            raise RuntimeError("Hero image changed unexpectedly")
        updated_images = {
            "en": image_sources(payload.get("draftHtml", "")),
            **{
                language: image_sources(localized.get("draftHtml", ""))
                for language, localized in payload.get("translations", {}).items()
            },
        }
        if updated_images != original_images:
            raise RuntimeError("Money-page image references changed unexpectedly")
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(target)
    print(f"Applied text-only updates; backup: {backup_root}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
