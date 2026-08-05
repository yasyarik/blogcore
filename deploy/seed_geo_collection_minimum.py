#!/usr/bin/env python3
"""Queue the remaining approved GEO collection pages without duplicating URLs.

The three briefs below come from the approved AI-visibility demand research:
visibility checking, AI readiness/GEO audit, and citation readiness.  They are
deliberately distinct from the existing crawler, llms.txt, tracking, and
remediation pages.
"""

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


SITE_ID = 16
SITE_DOMAIN = "geo.yas.ooo"


def page(
    content_type,
    slug,
    title,
    description,
    primary_intent,
    direct_answer,
    outline,
    links,
    source_references,
):
    prefix = {"tool": "tools", "use_case": "use-cases"}[content_type]
    target_path = f"/{prefix}/{slug}/"
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "contentType": content_type,
        "targetPath": target_path,
        "pageBrief": {
            "primaryIntent": primary_intent,
            "seoTitle": title,
            "metaDescription": description,
            "h1": title,
            "directAnswer": direct_answer,
            "outline": outline,
            "approvedInternalLinks": links,
            "sourceReferences": source_references,
            "editorial": {
                "author": "YAS AI Visibility Editorial",
                "reviewer": "YAS AI Visibility Product Review",
                "owner": "YAS AI Visibility Content",
                "reviewDueAt": (datetime.now(timezone.utc).date() + timedelta(days=90)).isoformat(),
                "reviewCadence": "every 90 days or after a material AI-search platform change",
                "factCheckedAt": datetime.now(timezone.utc).date().isoformat(),
            },
            "primaryCta": {
                "label": "Start an AI visibility audit",
                "url": "/",
            },
            "contentDetails": {
                "researchBasis": "Approved GEO demand map: AI visibility checker, AI readiness/GEO audit, and AI citation readiness clusters.",
                "editorialBoundary": "Explain the evidence a real audit can collect. Do not invent a score, a citation, an engine result, or a ranking for a visitor who has not run an audit.",
            },
            "approvals": {
                "editorialReview": False,
                "productFactCheck": False,
                "seoReview": False,
                "browserQa": False,
            },
        },
    }


PAGES = [
    page(
        "tool",
        "ai-visibility-checker-check-mentions-recommendations-and-citations-across-ai-answers",
        "AI Visibility Checker: Check Mentions, Recommendations, and Citations Across AI Answers",
        "Use an AI visibility check to separate brand mentions, recommendations, and citations across selected AI-search questions before deciding what to improve.",
        "AI visibility checker; website AI visibility checker; ChatGPT visibility checker; check brand visibility in ChatGPT.",
        "An AI visibility check tests a defined set of buyer questions and separates three different observations: whether a brand is mentioned, recommended, or cited. Those observations are not interchangeable and do not prove a stable ranking. The useful next step is to inspect the prompts, sources, page evidence, and technical conditions behind the result.",
        [
            "What an AI visibility check can and cannot establish",
            "Choose buyer questions before measuring visibility",
            "Separate mentions, recommendations, and citations",
            "Read the answer and source evidence behind each observation",
            "Why a single AI score is not a decision",
            "Turn the findings into an ordered website investigation",
            "Limitations: provider variation, freshness, geography, and prompt wording",
        ],
        [
            "/tools/ai-crawler-checker-test-whether-search-and-answer-engines-can-access-your-site/",
            "/use-cases/ai-search-tracking-measure-mentions-citations-and-visibility-by-question/",
            "/use-cases/ai-visibility-audit-and-remediation-turn-evidence-into-an-ordered-fix-plan/",
            "/solutions/generative-engine-optimization-build-evidence-ai-search-can-use/",
            "/",
        ],
        [
            "https://ahrefs.com/ai-visibility-checker",
            "https://developers.google.com/search/docs/appearance/ai-features",
        ],
    ),
    page(
        "tool",
        "ai-readiness-checker-audit-whether-ai-search-can-access-understand-and-cite-your-website",
        "AI Readiness Checker: Audit Whether AI Search Can Access, Understand, and Cite Your Website",
        "Review the technical, structural, entity, language, and content evidence that affects whether AI-search systems can access and use a website.",
        "AI readiness checker; AI search readiness test; AI website audit; GEO audit; is my website visible to AI; how does AI see my website.",
        "AI readiness is not one file or a synthetic score. A useful audit reviews whether important pages can be accessed, rendered, understood in context, connected to clear entities, and supported by content evidence that an answer system can use. It identifies controllable gaps but cannot guarantee citation or recommendation behavior.",
        [
            "What AI-search readiness means in practice",
            "Access and crawl conditions to verify first",
            "Page structure, entities, and supporting evidence",
            "Language, canonical, and duplicate-content signals",
            "Where llms.txt and schema fit, and where they do not",
            "Prioritize fixes by evidence and page importance",
            "Limitations: readiness is not a citation guarantee",
        ],
        [
            "/tools/ai-crawler-checker-test-whether-search-and-answer-engines-can-access-your-site/",
            "/tools/llmstxt-checker-review-an-experimental-ai-discovery-file-in-context/",
            "/solutions/google-ai-overviews-seo-diagnose-the-signals-your-website-controls/",
            "/use-cases/ai-visibility-audit-and-remediation-turn-evidence-into-an-ordered-fix-plan/",
            "/",
        ],
        [
            "https://developers.google.com/search/docs/appearance/ai-features",
            "https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers",
        ],
    ),
    page(
        "use_case",
        "ai-citation-readiness-prepare-your-website-to-be-cited-in-chatgpt-and-google-ai-overviews",
        "AI Citation Readiness: Prepare Your Website to Be Cited in ChatGPT and Google AI Overviews",
        "Use a citation-readiness workflow to identify which pages, evidence, and technical conditions give AI-search systems material they can responsibly use.",
        "How to get ChatGPT to cite my website; how to get ChatGPT to recommend my business; AI Overview citations; how to get cited in AI Overviews.",
        "Citation readiness is a workflow for improving the material an AI answer can inspect and use: clear pages for real questions, credible supporting evidence, accessible technical delivery, and a way to review source patterns. It cannot force ChatGPT or Google AI Overviews to cite a site, but it makes the underlying evidence testable and actionable.",
        [
            "When citation readiness is the right problem to solve",
            "Map the questions your buyers actually ask",
            "Identify the pages and evidence an answer would need",
            "Remove access, context, and entity ambiguity",
            "Compare cited sources without inventing a rank",
            "Create a remediation sequence for priority questions",
            "Limitations: no system can promise an AI citation",
        ],
        [
            "/solutions/chatgpt-seo-how-to-make-your-website-easier-to-find-understand-and-cite/",
            "/solutions/google-ai-overviews-seo-diagnose-the-signals-your-website-controls/",
            "/tools/ai-visibility-checker-check-mentions-recommendations-and-citations-across-ai-answers/",
            "/use-cases/ai-search-tracking-measure-mentions-citations-and-visibility-by-question/",
            "/",
        ],
        [
            "https://developers.google.com/search/docs/appearance/ai-features",
            "https://ahrefs.com/blog/ai-search-trends/",
        ],
    ),
]


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def seed(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    created = []
    skipped = []
    try:
        site = conn.execute("select id, domain from sites where id=?", (SITE_ID,)).fetchone()
        if not site or site["domain"] != SITE_DOMAIN:
            raise SystemExit(f"site {SITE_ID} is not {SITE_DOMAIN}")
        for item in PAGES:
            existing = conn.execute(
                "select id, status from content_jobs where site_id=? and json_extract(sources_json, '$.targetPath')=?",
                (SITE_ID, item["targetPath"]),
            ).fetchone()
            sources = {
                "source": "approved-demand-map",
                "source_title": "Approved English-language AI visibility demand map",
                "contentType": item["contentType"],
                "pageType": item["contentType"],
                "targetPath": item["targetPath"],
                "canonicalGroup": item["targetPath"],
                "preserveSlug": True,
                "publicationMode": "native_content_store",
                # GEO runs beside YAS but has an independent content store.
                # This is the project root expected by native_content_store_root(),
                # which appends ``data/blog-core`` below it.
                "nativeProjectRoot": "/opt/yas-ooo/data/geo-content-store",
                "pageBrief": item["pageBrief"],
            }
            now = now_iso()
            if existing:
                if existing["status"] != "QUEUED":
                    skipped.append({"targetPath": item["targetPath"], "id": existing["id"], "status": existing["status"]})
                    continue
                conn.execute(
                    """
                    update content_jobs
                    set topic=?, slug=?, title=?, description=?, category=?, sources_json=?, updated_at=?
                    where site_id=? and id=?
                    """,
                    (
                        item["title"], item["slug"], item["title"], item["description"], "SEO Money Page",
                        json.dumps(sources, ensure_ascii=False), now, SITE_ID, existing["id"],
                    ),
                )
                conn.execute(
                    "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                    (SITE_ID, existing["id"], now, "INFO", "approved-demand-map", f"Refreshed approved {item['contentType']} brief at {item['targetPath']}"),
                )
                skipped.append({"targetPath": item["targetPath"], "id": existing["id"], "status": existing["status"], "refreshed": True})
                continue
            job_id = hashlib.sha256(f"geo:{item['targetPath']}".encode()).hexdigest()[:24]
            conn.execute(
                """
                insert into content_jobs(
                    id, site_id, topic, slug, status, title, description, category,
                    sources_json, visibility, created_at, updated_at
                ) values(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    job_id, SITE_ID, item["title"], item["slug"], "QUEUED", item["title"],
                    item["description"], "SEO Money Page", json.dumps(sources, ensure_ascii=False),
                    "public", now, now,
                ),
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?,?,?,?,?,?)",
                (SITE_ID, job_id, now, "INFO", "approved-demand-map", f"Queued approved {item['contentType']} page at {item['targetPath']}"),
            )
            created.append({"id": job_id, "targetPath": item["targetPath"], "title": item["title"]})
        conn.commit()
    finally:
        conn.close()
    print(json.dumps({"created": created, "skipped": skipped}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    args = parser.parse_args()
    seed(args.db)


if __name__ == "__main__":
    main()
