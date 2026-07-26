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
EDITORIAL_CORRECTIONS = {
    "/ai-automation": {
        "The YAS control architecture wraps AI models with input validation, confidence scoring, and human review queues.": "A controlled AI workflow needs validated inputs, an explicit review boundary, an exception queue, and a human decision owner.",
        "When evaluating a starting point, select processes with structured inputs. For example, classifying incoming support tickets or extracting key details from supplier invoices are illustrative candidates that permit clear input validation.": "Start with one recurring task whose input and acceptable output can be written down. A document or incoming request is only an illustrative candidate; the real task still needs its own boundary and review owner.",
        "Classification of incoming customer inquiries and support tickets": "Classification of a bounded incoming request",
        "Information extraction from unstructured documents and invoices": "Information extraction from an approved document type",
        "Third, the system runs a quality review to generate a confidence score.": "Third, the system applies the review rule defined for that task.",
        "Fourth, items meeting the confidence threshold proceed to draft preparation, while low-confidence items are sent to the exception queue.": "Fourth, accepted items continue while ambiguous or invalid items move to the exception queue.",
        "Step 3: Quality review and confidence scoring": "Step 3: Quality review against the task rule",
        "These software examples run on custom web architectures and native-first Shopify development to support operator handoffs.": "They show that I build working product and publishing surfaces. The control pattern on this page is a design contract, not a claim about every YAS product.",
        "Requires structured fallback when confidence scores drop": "Requires a defined fallback when the review rule is not met",
        "Fully logged steps and confidence scoring": "Traceable output required by the workflow contract",
        "Establish the explicit input contract and define the confidence threshold for automated approval.": "Establish the input contract and define the review rule for acceptance.",
        "What happens when the AI model returns a low confidence score?": "What happens when the output does not meet the review rule?",
        "Can these workflows integrate with a Shopify store?": "Can this workflow connect to an existing business system?",
        "Yes. I use native-first Shopify development to integrate custom AI-assisted workflows directly with store databases and admin interfaces.": "Possibly. The connection is scoped only after the required data, permissions, review step, and fallback are confirmed.",
    },
    "/product-development": {
        "I apply this loop-first principle to internal products and client projects. For My UGC Studio, development focused on the core loop of matching creators with brand briefs before expanding the platform scope. For BellB and SoloCruz, the initial development cycles were constrained to verifying the primary transaction and data flow. These public products prove that I build working software; they do not prove that every product uses the identical workflow.": "My UGC Studio, BellB, SoloCruz, Georivo, and Blog Core are public evidence that I ship working software across different product surfaces. They are not presented here as proof of one identical development sequence or of a client outcome.",
        "For Georivo and Blog Core, development avoided broad feature sets in favor of establishing an explicit source of truth and a reliable release path. This approach allowed these products to become operational through active use rather than theoretical planning.": "The product pages and live interfaces are the evidence to inspect. The specific source of truth, release path, and operating constraints must be verified separately for every new build.",
        "I apply this loop-first principle to internal products and client projects.": "I apply this loop-first principle to products I build.",
    },
    "/build": {
        "I apply these engineering principles to my own products and client systems.": "I apply these engineering principles to products I build.",
        "These real-world products serve as technical evidence of my ability to build systems that address direct business needs. I use these live environments to test and refine the architectural patterns applied to client systems.": "These public products are evidence of shipped interfaces and working software. They are not presented as evidence that one architecture fits every business or that a specific outcome is guaranteed.",
        "<td>Georivo</td>": "<td>YAS product portfolio</td>",
        "<td>Scalable customer-facing software applications</td>": "<td>Bounded customer-facing product workflows</td>",
        "<td>SoloCruz</td>": "<td>YAS Shopify client work</td>",
        "Understand my approach for developing high-performance transactional storefronts.": "Understand how I scope transactional storefronts around real commerce rules.",
        "Explore how I build custom internal applications to streamline team collaboration and data management.": "Explore how I scope internal tools around state, ownership, and handoffs.",
        "Discover my approach to engineering scalable software-as-a-service platforms and digital products.": "See how I bound the first working loop of a digital product.",
    },
    "/shopify-development": {
        "No. Custom storefront elements are designed to be fully compatible with the Shopify Online Store 2.0 architecture. This allows marketing and operations teams to update layouts and content using the native editor without developer assistance.": "It depends on the theme architecture and the custom surface. Editor compatibility must be defined and verified during the implementation audit.",
        "I map existing subscription states and customer payment tokens directly to native Shopify subscription APIs. This process migrates recurring customers without requiring them to re-enter payment details, avoiding disruption to recurring revenue.": "Subscription migration depends on the existing provider, stored state, payment permissions, and Shopify's supported migration path. I do not promise a no-interruption migration before those constraints are verified.",
        "I run load testing and simulate high-volume checkout scenarios on staging environments. By isolating custom logic in serverless environments or using native Shopify Functions, the integration scales automatically with Shopify's core infrastructure.": "The verification plan depends on the integration. It may include staging scenarios, regression checks, and load testing, but no custom integration is assumed safe until its actual failure paths are tested.",
        "Optimize storefront performance and verify integration stability under simulated high-traffic conditions.": "Measure storefront performance and test the actual integration failure paths before release.",
    },
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


def edit_prompt(brief, title, description, segments, low, high):
    facts = {
        "directAnswer": brief.get("directAnswer"),
        "contentDetails": brief.get("contentDetails"),
        "sourceReferences": brief.get("sourceReferences"),
        "voiceContract": brief.get("voiceContract"),
    }
    return f"""
You are the final editorial reviewer for Iaroslav YAS.
Return JSON with the unchanged title, unchanged description, and an edited `segments` array.

VERIFIED FACT BOUNDARY:
{json.dumps(facts, ensure_ascii=False)}

TITLE:
{title}

DESCRIPTION:
{description}

VISIBLE TEXT SEGMENTS IN DOCUMENT ORDER:
{json.dumps(segments, ensure_ascii=False)}

EDITING CONTRACT:
- Return exactly {len(segments)} edited text segments in the same order. Do not combine,
  split, omit, or add a segment. HTML is restored deterministically outside the model.
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


def apply_editorial_corrections(path, html):
    corrected = html
    for source, replacement in EDITORIAL_CORRECTIONS.get(path, {}).items():
        corrected = corrected.replace(source, replacement)
    return corrected


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


def run(db_path: Path, site_id: int, localize_only=False):
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
        corrected_html = apply_editorial_corrections(sources["targetPath"], row["draft_html"])
        if localize_only:
            edited_html = corrected_html
        else:
            source_segments = visible_segments(corrected_html)
            edited = blog_core._gemini_text_json(
                edit_prompt(brief, row["title"], row["description"], source_segments, low, high),
                response_schema=LOCALIZATION_SCHEMA,
                repair=False,
            )
            if edited["title"].strip() != row["title"].strip() or edited["description"].strip() != row["description"].strip():
                raise ValueError(f"{sources['targetPath']}: editor changed approved title or description")
            edited_html = restore_segments(corrected_html, edited["segments"])
        validate_revision(row["draft_html"], edited_html, low, high, sources["targetPath"])
        conn.execute("update content_jobs set draft_html=?,updated_at=? where id=?", (edited_html, blog_core.now_iso(), row["id"]))
        for language in ("ru", "de"):
            localized_row = conn.execute(
                "select * from content_job_localizations where job_id=? and language=?",
                (row["id"], language),
            ).fetchone()
            source_segments = visible_segments(edited_html)
            localized = blog_core._gemini_text_json(
                localization_prompt(language, row["title"], row["description"], source_segments),
                response_schema=LOCALIZATION_SCHEMA,
                repair=False,
            )
            localized_html = restore_segments(edited_html, localized["segments"])
            validate_revision(edited_html, localized_html, max(250, int(low * 0.55)), int(high * 1.35), f"{sources['targetPath']}/{language}")
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
    parser.add_argument("--localize-only", action="store_true")
    args = parser.parse_args()
    run(Path(args.db), args.site_id, localize_only=args.localize_only)
