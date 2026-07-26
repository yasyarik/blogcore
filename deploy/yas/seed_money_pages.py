#!/usr/bin/env python3
"""Idempotently seed the approved YAS commercial page plan into Blog Core."""

import argparse
import hashlib
import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path


TODAY = date(2026, 7, 26)
YAS_SOURCE = {
    "id": "yas-public-site",
    "title": "YAS public website",
    "publisher": "YAS",
    "publicUrl": "https://yas.ooo/",
    "accessedAt": TODAY.isoformat(),
    "supports": (
        "YAS method, public research flow, operating-system model, implementation "
        "capabilities, product portfolio, client-work evidence, and stated limitations."
    ),
}

PAGES = [
    {
        "slug": "shopify-development",
        "profile": "money_service",
        "title": "Shopify Development for Stores With Real Operational Logic",
        "meta": "YAS designs and builds Shopify systems when catalog, storefront, order and operational logic no longer fit a generic theme or disconnected app stack.",
        "intent": "custom Shopify development",
        "answer": "YAS builds Shopify systems for stores whose catalog, offer, storefront, order, fulfilment or support logic has outgrown a generic theme. The work starts by mapping the operating states and deciding what should remain native, what needs controlled custom logic, and what should be removed. The goal is a maintainable commerce system, not a larger app stack.",
        "outline": ["Where Shopify projects usually become fragile", "Native first architecture", "The working delivery sequence", "What you can verify in the work", "Limitations and suitability", "A practical starting point"],
        "links": ["/build/commerce-systems", "/client-work", "/case-studies", "/systems/customer-and-product-systems", "/contact", "/blog"],
        "details": {
            "verifiedCapabilities": ["Shopify theme and storefront work", "catalog and offer logic", "subscription and order workflows", "performance and integration work"],
            "workingPrinciples": ["map business state before interface work", "prefer native platform capabilities", "add custom logic only where the business rule requires it", "keep regression and exception paths visible"],
            "proofRoutes": ["/client-work", "/case-studies"],
            "forbiddenClaims": ["guaranteed conversion uplift", "universal architecture", "zero-maintenance custom code"],
        },
    },
    {
        "slug": "ai-automation",
        "profile": "money_service",
        "title": "AI Automation Built Around a Controlled Business Workflow",
        "meta": "YAS designs AI-assisted workflows with explicit inputs, review, exceptions, fallback and measurable operational purpose.",
        "intent": "AI automation for business workflows",
        "answer": "YAS uses AI inside a controlled workflow, not as an unbounded replacement for the process owner. A useful automation has known inputs, allowed outputs, confidence boundaries, human review, exception handling and a fallback. The work is judged by the task it improves, not by how impressive a prompt demonstration looks.",
        "outline": ["What should be automated first", "The control layer around AI", "From input to reviewed output", "Where practical proof comes from", "Limitations and suitability", "A practical starting point"],
        "links": ["/build/ai-assisted-workflows", "/workflows", "/systems/content-and-knowledge", "/products", "/case-studies", "/contact"],
        "details": {
            "verifiedCapabilities": ["classification", "information extraction", "research", "draft preparation", "content and publishing workflows", "operator handoff"],
            "requiredControls": ["explicit input contract", "quality review", "exception queue", "fallback", "traceable output"],
            "realProductContext": ["YAS public website scanner", "Blog Core publishing workflow", "YAS product portfolio"],
            "forbiddenClaims": ["fully autonomous business", "perfect output", "replacement of accountable human review"],
        },
    },
    {
        "slug": "product-development",
        "profile": "money_service",
        "title": "Product Development Around One Verifiable Working Loop",
        "meta": "YAS turns a product or internal-tool idea into a bounded workflow, data model, interface and release path before expanding the scope.",
        "intent": "custom product development",
        "answer": "YAS builds digital products and internal tools around one verifiable working loop. Before expanding the feature list, the work defines the user, input, state, decision, exception and output. The first release is useful only when someone can complete the core task and the team can see where it succeeds, fails or needs a product decision.",
        "outline": ["Start with the working loop", "Architecture follows the operating model", "What belongs in the first release", "Evidence from working YAS products", "Limitations and suitability", "A practical starting point"],
        "links": ["/build/digital-products-and-saas", "/products", "/my-startups", "/case-studies", "/method", "/contact"],
        "details": {
            "verifiedCapabilities": ["web applications", "internal tools", "portals", "SaaS products", "browser extensions", "mobile application surfaces"],
            "realProductContext": ["My UGC Studio", "BellB", "SoloCruz", "Georivo", "Blog Core"],
            "workingPrinciples": ["one end-to-end loop first", "explicit source of truth", "bounded interfaces", "observable release and triage"],
            "forbiddenClaims": ["market validation from code alone", "unlimited scope", "guaranteed product-market fit"],
        },
    },
    {
        "slug": "startup-advisory",
        "profile": "money_service",
        "title": "Technical Advisory That Ends With a Bounded Decision",
        "meta": "YAS helps founders reduce a technical or product decision to a practical next move, explicit risk, scope and stop condition.",
        "intent": "technical startup advisory",
        "answer": "YAS advisory is for a founder or operator who needs a bounded technical decision before committing more time or budget. The output is not a longer idea list. It is a documented constraint, the viable options, the tradeoffs, the smallest useful next move, acceptance criteria and the condition that should stop or change the plan.",
        "outline": ["When advisory is the right intervention", "What gets decided", "How the evidence is separated from assumptions", "What the handoff contains", "Limitations and suitability", "A practical starting point"],
        "links": ["/method", "/paid-advisory", "/research/business-constraint-map", "/products", "/case-studies", "/contact"],
        "details": {
            "verifiedOutputs": ["constraint definition", "option and tradeoff map", "bounded implementation scope", "decision record", "acceptance and stop criteria"],
            "workingPrinciples": ["separate evidence from assumption", "prefer reversible first moves", "assign a decision owner", "do not extend discovery without a decision"],
            "forbiddenClaims": ["legal or financial advice", "market validation guarantee", "certainty where evidence is missing"],
        },
    },
    {
        "slug": "method",
        "profile": "money_hub",
        "title": "The YAS Method: Find the Constraint Before Choosing the Software",
        "meta": "The YAS method moves from public evidence and business constraints to an operating model, bounded workflow and appropriate implementation surface.",
        "intent": "YAS business systems method",
        "answer": "The YAS method starts with the constraint, not the software category. It separates public evidence from assumptions, maps the current operating state, identifies the decision that is blocked, and defines the smallest working intervention. Only then does it choose whether the answer is a workflow change, Shopify logic, automation, an internal tool or a product build.",
        "outline": ["Observe before diagnosing", "Name the blocked decision", "Map the operating state", "Choose the smallest intervention", "Verify the handoff", "Limitations and suitability"],
        "links": ["/research", "/systems", "/workflows", "/build", "/case-studies", "/contact"],
        "details": {
            "stages": ["observe", "frame constraint", "map state and ownership", "design intervention", "build and verify"],
            "decisionRule": "choose the smallest intervention that changes the blocked decision or handoff",
            "forbiddenClaims": ["public evidence reveals private operations", "every constraint needs software", "method guarantees a business outcome"],
        },
    },
    {
        "slug": "research",
        "profile": "money_tool",
        "title": "Public-Signal Research Before a Private Business Diagnosis",
        "meta": "YAS public research checks visible website, search, AI, trust, speed, content and conversion signals without claiming access to internal operations.",
        "intent": "public business website research",
        "answer": "YAS research begins with evidence that can be checked from outside the business: website structure, search and AI visibility, content coverage, speed, trust signals, conversion paths and visible competitor patterns. It does not claim to know private operations. The scan is a bounded starting point for deciding what needs deeper validation.",
        "outline": ["What the public scan can observe", "What it cannot know", "How signals become a review queue", "Where AI visibility fits", "How to use the result", "Limitations and suitability"],
        "links": ["/research/business-constraint-map", "/method", "/systems", "/blog", "/paid-advisory", "/contact"],
        "details": {
            "observableSignals": ["website discoverability", "search and AI visibility", "content coverage", "speed", "trust elements", "conversion paths", "visible competitor patterns"],
            "boundaries": ["no internal system access", "no private analytics claim", "no guaranteed index or citation result", "results require review"],
            "productContext": "The public scanner is integrated into the YAS homepage.",
        },
    },
    {
        "slug": "systems",
        "profile": "money_hub",
        "title": "Business Systems Organized Around Decisions and Ownership",
        "meta": "YAS maps revenue, operations, content and customer systems as connected business states before choosing tools or implementation surfaces.",
        "intent": "business systems design",
        "answer": "YAS treats a business system as a connected set of states, decisions, owners and handoffs. The model covers revenue and demand, operations and decisions, content and knowledge, and customer and product systems. It makes the operating structure visible before tools, automation or custom software are added.",
        "outline": ["The four operating domains", "State before screens", "Ownership and handoffs", "Where automation belongs", "How systems become build scope", "Limitations and suitability"],
        "links": ["/systems/revenue-and-demand", "/systems/operations-and-decisions", "/systems/content-and-knowledge", "/systems/customer-and-product-systems", "/workflows", "/build"],
        "details": {
            "domains": ["revenue and demand", "operations and decisions", "content and knowledge", "customer and product systems"],
            "workingPrinciples": ["name the state", "assign the owner", "make handoffs testable", "design exceptions", "choose tools after the model"],
            "forbiddenClaims": ["one universal operating model", "software removes organizational ownership"],
        },
    },
    {
        "slug": "workflows",
        "profile": "money_hub",
        "title": "Workflow Design With Explicit State, Review and Exceptions",
        "meta": "YAS designs workflows that connect inputs, decisions, owners, handoffs, exceptions and measurable outputs across business systems.",
        "intent": "business workflow design",
        "answer": "A YAS workflow is not a diagram of the happy path. It defines the input, current state, decision owner, handoff, exception, review and output. This makes the process testable before automation and keeps operators able to understand, correct and continue the work when the normal path fails.",
        "outline": ["Start with the state transition", "Assign the decision owner", "Design the exception path", "Add AI only inside clear boundaries", "Test the handoff", "Limitations and suitability"],
        "links": ["/systems", "/build/ai-assisted-workflows", "/build/internal-tools-and-portals", "/method", "/case-studies", "/contact"],
        "details": {
            "workflowContract": ["input", "state", "decision", "owner", "handoff", "exception", "review", "output"],
            "workingPrinciples": ["normal and exception paths both matter", "automation needs a fallback", "review is part of the design", "measure the task outcome"],
            "forbiddenClaims": ["workflow diagrams alone change operations", "AI should own every decision"],
        },
    },
    {
        "slug": "build",
        "profile": "money_hub",
        "title": "Build the Smallest Working System That Resolves the Constraint",
        "meta": "YAS turns an approved operating model into AI workflows, internal tools, digital products, apps, extensions or commerce systems.",
        "intent": "business software development",
        "answer": "YAS chooses the implementation surface after the operating model is clear. The build may be an AI-assisted workflow, an internal tool, a portal, a digital product, an app, a browser extension or a commerce system. The first scope should resolve one real constraint and expose enough state to verify the result.",
        "outline": ["Choose the implementation surface last", "Bound the first release", "Keep state and ownership visible", "Use real products as technical evidence", "Release with triage", "Limitations and suitability"],
        "links": ["/build/ai-assisted-workflows", "/build/internal-tools-and-portals", "/build/digital-products-and-saas", "/build/apps-and-extensions", "/build/commerce-systems", "/products"],
        "details": {
            "surfaces": ["AI-assisted workflows", "internal tools and portals", "digital products and SaaS", "apps and extensions", "commerce systems"],
            "realProductContext": ["My UGC Studio", "BellB", "SoloCruz", "Georivo", "Blog Core"],
            "workingPrinciples": ["bounded first release", "explicit source of truth", "observable state", "exception handling", "release triage"],
            "forbiddenClaims": ["every problem needs custom software", "first release should include every requested feature"],
        },
    },
]


def editorial():
    return {
        "author": "Iaroslav YAS",
        "reviewer": "Iaroslav YAS",
        "owner": "YAS",
        "reviewDueAt": (TODAY + timedelta(days=180)).isoformat(),
        "reviewCadence": "every 180 days or after a material service, product, or workflow change",
        "factCheckedAt": TODAY.isoformat(),
    }


def source_payload(item):
    target = f"/{item['slug']}"
    return {
        "contentType": "seo_money_page",
        "targetPath": target,
        "canonicalGroup": f"yas:money:{item['slug']}",
        "canonicalRootPage": True,
        "preserveSlug": True,
        "publicationMode": "native_next_content_store",
        "nativeProjectRoot": "/opt/yas-ooo",
        "pageBrief": {
            "contentProfile": item["profile"],
            "primaryIntent": item["intent"],
            "seoTitle": item["title"],
            "metaDescription": item["meta"],
            "h1": item["title"],
            "directAnswer": item["answer"],
            "outline": item["outline"],
            "approvedInternalLinks": item["links"],
            "sourceReferences": [YAS_SOURCE],
            "editorial": editorial(),
            "primaryCta": {"label": "Describe the bottleneck", "url": "/contact"},
            "contentDetails": item["details"],
            "voiceContract": {
                "speaker": "Iaroslav YAS",
                "style": ["direct", "specific", "calm", "practical", "first-person only where supported"],
                "ban": ["generic AI language", "invented anecdotes", "invented metrics", "filler", "text written to hit a word count"],
                "paragraphTest": "Every paragraph must help the reader understand, compare, verify, decide, or act.",
            },
            "approvals": {
                "editorialReview": False,
                "productFactCheck": False,
                "seoReview": False,
                "browserQa": False,
            },
        },
    }


def seed(db_path: Path, site_id: int):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
    if not site or site["domain"] != "yas.ooo":
        raise SystemExit(f"site {site_id} is not yas.ooo")
    conn.execute(
        "update sites set access_type='native_content_store',root_path='/opt/yas-ooo',languages='[\"en\",\"ru\",\"de\"]',updated_at=? where id=?",
        (f"{TODAY.isoformat()}T00:00:00+00:00", site_id),
    )
    created = updated = skipped = 0
    for item in PAGES:
        sources = source_payload(item)
        target = sources["targetPath"]
        payload = json.dumps(sources, ensure_ascii=False, separators=(",", ":"))
        existing = conn.execute(
            "select id,status from content_jobs where site_id=? and json_extract(sources_json,'$.targetPath')=?",
            (site_id, target),
        ).fetchone()
        now = f"{TODAY.isoformat()}T00:00:00+00:00"
        if existing and existing["status"] == "PUBLISHED":
            skipped += 1
            continue
        if existing:
            conn.execute(
                "update content_jobs set topic=?,slug=?,title=?,description=?,category='Services',sources_json=?,status='IDEA',error=NULL,updated_at=? where id=?",
                (item["title"], item["slug"], item["title"], item["meta"], payload, now, existing["id"]),
            )
            updated += 1
        else:
            job_id = hashlib.sha256(f"yas:{target}".encode()).hexdigest()[:24]
            conn.execute(
                """insert into content_jobs(
                   id,site_id,topic,slug,status,title,description,category,hero_image,draft_html,
                   faq_json,error,sources_json,visibility,created_at,updated_at
                 ) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (job_id, site_id, item["title"], item["slug"], "IDEA", item["title"], item["meta"],
                 "Services", "", "", "[]", None, payload, "public", now, now),
            )
            created += 1
    conn.commit()
    conn.close()
    print(json.dumps({"created": created, "updated": updated, "skippedPublished": skipped, "pages": len(PAGES)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=12)
    args = parser.parse_args()
    seed(Path(args.db), args.site_id)
