#!/usr/bin/env python3
"""Final founder-voice edit and intelligent RU/DE HTML localization for YAS pages."""

import argparse
import json
import re
import sqlite3
import sys
from html import escape, unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import app as blog_core


HTML_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "description": {"type": "STRING"},
        "html": {"type": "STRING"},
    },
    "required": ["title", "description", "html"],
}
LOCALIZATION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "description": {"type": "STRING"},
        "segments": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["title", "description", "segments"],
}


def plain(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def tokens(html, attribute):
    return sorted(re.findall(rf'{attribute}="([^"]+)"', html or ""))


def restore_attributes(before, after):
    restored = after
    for attribute in ("href", "src"):
        approved = re.findall(rf'{attribute}="([^"]+)"', before or "")
        seen = re.findall(rf'{attribute}="([^"]+)"', restored or "")
        if len(approved) != len(seen):
            raise ValueError(f"{attribute} count changed")
        iterator = iter(approved)
        restored = re.sub(
            rf'{attribute}="[^"]+"',
            lambda _match: f'{attribute}="{next(iterator)}"',
            restored,
        )
    return restored


def validate_revision(before, after, low, high, label):
    words = len(re.findall(r"\b[\w'-]+\b", plain(after)))
    if not low <= words <= high:
        raise ValueError(f"{label}: {words} words outside {low}-{high}")
    for attribute in ("href", "src"):
        if tokens(before, attribute) != tokens(after, attribute):
            raise ValueError(f"{label}: {attribute} contract changed")
    if before.count('class="article-figure"') != after.count('class="article-figure"'):
        raise ValueError(f"{label}: figure contract changed")
    if before.count("<h2") != after.count("<h2"):
        raise ValueError(f"{label}: H2 contract changed")


def edit_prompt(brief, title, description, html, low, high):
    facts = {
        "directAnswer": brief.get("directAnswer"),
        "contentDetails": brief.get("contentDetails"),
        "sourceReferences": brief.get("sourceReferences"),
        "voiceContract": brief.get("voiceContract"),
    }
    return f"""
You are the final editorial reviewer for Iaroslav YAS.
Return JSON with the unchanged title, unchanged description, and fully edited HTML.

VERIFIED FACT BOUNDARY:
{json.dumps(facts, ensure_ascii=False)}

TITLE:
{title}

DESCRIPTION:
{description}

HTML:
{html}

EDITING CONTRACT:
- Preserve the exact HTML structure, tag count, class attributes, href values, src values,
  image dimensions, and section order. Edit visible prose only.
- Keep {low}-{high} words. Prefer shorter, denser copy.
- Use Iaroslav's working voice: direct, specific, calm, practical, accountable.
- Use I only for a practice or decision supported by the verified facts. Never use our
  team, our experts, our methodology, agency superlatives, or anonymous authority.
- Remove generic introductions, filler, repeated explanations, recap paragraphs, and
  text written only for SEO length.
- Every paragraph must help the reader understand, compare, verify, decide, or act.
- Do not invent a client, anecdote, metric, result, product behavior, integration,
  workflow implementation, database connection, interface, confidence score, threshold,
  or guarantee.
- Clearly label a general scenario as illustrative. Do not present it as YAS production
  evidence.
- Public YAS products prove that I build working software. They do not prove that every
  product uses the exact workflow discussed on this page.
- Preserve the approved direct answer at the beginning and all limitations.
- No em dash, en dash, smart quotes, markdown, or code fences.
""".strip()


def visible_segments(html):
    return [
        part.strip()
        for part in re.split(r"(<[^>]+>)", html or "")
        if part and not part.startswith("<") and part.strip()
    ]


def restore_segments(html, translated):
    parts = re.split(r"(<[^>]+>)", html or "")
    expected = visible_segments(html)
    if len(expected) != len(translated):
        raise ValueError(f"visible segment count changed: {len(expected)} to {len(translated)}")
    iterator = iter(translated)
    output = []
    for part in parts:
        if part and not part.startswith("<") and part.strip():
            value = str(next(iterator)).strip()
            if "<" in value or ">" in value:
                raise ValueError("localized visible segment contains markup")
            output.append(escape(value, quote=False))
        else:
            output.append(part)
    return "".join(output)


def localization_prompt(language, title, description, segments):
    language_name = {"ru": "Russian", "de": "German"}[language]
    return f"""
Translate and editorially localize this YAS commercial page into fluent {language_name}.
Return JSON containing the translated title, description, and `segments` array.

TITLE:
{title}

DESCRIPTION:
{description}

VISIBLE TEXT SEGMENTS IN DOCUMENT ORDER:
{json.dumps(segments, ensure_ascii=False)}

LOCALIZATION CONTRACT:
- Return exactly {len(segments)} translated text segments in the same order. Do not
  combine, split, omit, or add a segment. HTML is restored deterministically outside
  the model.
- Preserve every fact, qualification, limitation, and illustrative label. Do not add,
  remove, strengthen, or generalize claims.
- Write as a native editor in Iaroslav's direct, specific, calm, practical voice. Avoid
  literal machine syntax, anonymous agency language, inflated marketing, and filler.
- Keep all YAS, product, platform, route, and technical names unchanged where they are
  proper names.
- No em dash, en dash, smart quotes, markdown, or code fences.
""".strip()


def run(db_path: Path, site_id: int):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """select * from content_jobs where site_id=? and status='DRAFT'
           and json_extract(sources_json,'$.contentType')='seo_money_page'
           order by json_extract(sources_json,'$.targetPath')""",
        (site_id,),
    ).fetchall()
    for row in rows:
        sources = json.loads(row["sources_json"])
        brief = sources["pageBrief"]
        profile = blog_core.MONEY_PAGE_CONTENT_PROFILES[brief["contentProfile"]]
        low, high = profile["min_words"], profile["max_words"]
        edited = blog_core._gemini_text_json(
            edit_prompt(brief, row["title"], row["description"], row["draft_html"], low, high),
            response_schema=HTML_SCHEMA,
            repair=False,
        )
        if edited["title"].strip() != row["title"].strip() or edited["description"].strip() != row["description"].strip():
            raise ValueError(f"{sources['targetPath']}: editor changed approved title or description")
        edited["html"] = restore_attributes(row["draft_html"], edited["html"])
        validate_revision(row["draft_html"], edited["html"], low, high, sources["targetPath"])
        conn.execute("update content_jobs set draft_html=?,updated_at=? where id=?", (edited["html"], blog_core.now_iso(), row["id"]))
        for language in ("ru", "de"):
            localized_row = conn.execute(
                "select * from content_job_localizations where job_id=? and language=?",
                (row["id"], language),
            ).fetchone()
            source_segments = visible_segments(edited["html"])
            localized = blog_core._gemini_text_json(
                localization_prompt(language, row["title"], row["description"], source_segments),
                response_schema=LOCALIZATION_SCHEMA,
                repair=False,
            )
            localized_html = restore_segments(edited["html"], localized["segments"])
            validate_revision(edited["html"], localized_html, max(250, int(low * 0.55)), int(high * 1.35), f"{sources['targetPath']}/{language}")
            conn.execute(
                """update content_job_localizations set title=?,description=?,draft_html=?,updated_at=?
                   where job_id=? and language=?""",
                (localized["title"], localized["description"], localized_html, blog_core.now_iso(), row["id"], language),
            )
        conn.commit()
        print(json.dumps({"path": sources["targetPath"], "status": "edited", "locales": ["ru", "de"]}), flush=True)
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=12)
    args = parser.parse_args()
    run(Path(args.db), args.site_id)
