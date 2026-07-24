#!/usr/bin/env python3
"""Idempotently seed the approved Georivo typed-content plan into Blog Core."""

import argparse
import hashlib
import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path


TODAY = date(2026, 7, 24)
PRODUCT_SOURCE = {
    "id": "georivo-product",
    "title": "Georivo product page",
    "publisher": "Georivo",
    "publicUrl": "https://georivo.com/",
    "accessedAt": TODAY.isoformat(),
    "supports": (
        "Product definition, three story templates, address coverage check, programmed camera "
        "paths, protected links, domain-bound embeds, pricing, limits, and product limitations."
    ),
}
GOOGLE_SOURCE = {
    "id": "google-maps-terms",
    "title": "Google Maps Platform Terms of Service",
    "publisher": "Google",
    "publicUrl": "https://cloud.google.com/maps-platform/terms",
    "accessedAt": TODAY.isoformat(),
    "supports": "Attribution and permitted-use context for the live Google Maps experience.",
}
PLATFORM_SOURCES = {
    "wordpress": {
        "id": "wordpress-custom-html",
        "title": "Custom HTML block",
        "publisher": "WordPress.org",
        "publicUrl": "https://wordpress.org/documentation/article/custom-html/",
        "accessedAt": TODAY.isoformat(),
        "supports": "Current WordPress 7.0 Custom HTML workflow and unfiltered_html limitation.",
    },
    "webflow": {
        "id": "webflow-code-embed",
        "title": "Custom code embed",
        "publisher": "Webflow",
        "publicUrl": "https://help.webflow.com/hc/en-us/articles/33961332238611-Custom-code-embed",
        "accessedAt": TODAY.isoformat(),
        "supports": "Current Code Embed availability, supported code, publishing, and constraints.",
    },
    "wix": {
        "id": "wix-embed-widget",
        "title": "Wix Editor: Embedding a Site or a Widget",
        "publisher": "Wix",
        "publicUrl": "https://support.wix.com/en/article/wix-editor-embedding-a-site-or-a-widget",
        "accessedAt": TODAY.isoformat(),
        "supports": "Current Embed HTML flow, HTTPS requirement, sizing, and mobile limitations.",
    },
    "squarespace": {
        "id": "squarespace-code-blocks",
        "title": "Code blocks",
        "publisher": "Squarespace",
        "publicUrl": "https://support.squarespace.com/hc/en-us/articles/206543167-Code-blocks",
        "accessedAt": TODAY.isoformat(),
        "supports": "Current Code block flow, plan limitations, iframe support, preview, and troubleshooting.",
    },
}

GUIDES = [
    {
        "slug": "what-is-a-3d-property-flyover",
        "title": "What Is a 3D Property Flyover?",
        "meta": "Learn what a 3D property flyover is, what it shows, how it differs from drone footage, and when it helps buyers understand a listing location.",
        "intent": "what is a 3D property flyover",
        "answer": (
            "A 3D property flyover is an interactive, programmed journey through available geospatial "
            "imagery that approaches a confirmed property and can show its relationship to selected "
            "nearby places. It is not physical drone footage and does not prove current exterior "
            "condition, legal boundaries, or exact travel distance. Its purpose is to explain location "
            "context before a buyer arranges a viewing."
        ),
        "outline": ["Definition", "How it works", "What it shows", "What it does not show", "Media comparison", "Suitable listings", "Practical next step"],
        "links": ["/guides/3d-property-flyover-vs-drone-video/", "/guides/3d-property-flyover-vs-virtual-tour/", "/guides/which-property-listings-need-an-aerial-view/", "/examples/waterfront-villa-property-flyover/", "/#create"],
    },
    {
        "slug": "3d-property-flyover-vs-drone-video",
        "title": "3D Property Flyover vs Drone Video",
        "meta": "Compare interactive 3D property flyovers with physical drone video: interactivity, current imagery, logistics, website use, limitations and best-fit listings.",
        "intent": "3D property flyover vs drone video",
        "answer": (
            "A 3D property flyover and a drone video answer different questions. A flyover provides an "
            "interactive view of location relationships without a physical flight, while drone video "
            "records the actual exterior at a specific time. Choose by the evidence the buyer needs: "
            "current visual condition favors drone footage; explorable location context favors a 3D "
            "flyover; many listings benefit from both."
        ),
        "outline": ["Decision summary", "Evidence each format provides", "Interactivity and recency", "Logistics and permissions", "Website use", "Limitations", "Decision table"],
        "links": ["/guides/what-is-a-3d-property-flyover/", "/guides/which-property-listings-need-an-aerial-view/", "/guides/real-estate-listing-media-checklist/", "/examples/rural-estate-aerial-view/", "/#create"],
    },
    {
        "slug": "3d-property-flyover-vs-virtual-tour",
        "title": "3D Property Flyover vs Virtual Tour",
        "meta": "A property flyover explains exterior location context; a virtual tour shows interior space. Compare their roles and learn when to use both.",
        "intent": "3D property flyover vs virtual tour",
        "answer": (
            "A 3D property flyover explains where a property sits and how it relates to surrounding "
            "places, terrain, and approach. A virtual tour explains interior rooms, layout, and finishes. "
            "Neither is a universal replacement for the other. Use a flyover when location context "
            "affects the decision, a virtual tour when interior understanding matters, and both when a "
            "remote buyer needs the complete story."
        ),
        "outline": ["Decision summary", "Exterior context", "Interior evidence", "Buyer questions", "When to combine formats", "Limitations", "Media-stack example"],
        "links": ["/guides/what-is-a-3d-property-flyover/", "/guides/real-estate-listing-media-checklist/", "/guides/how-to-market-a-property-to-remote-buyers/", "/examples/urban-condo-neighborhood-story/", "/#create"],
    },
    {
        "slug": "how-to-show-nearby-amenities-on-a-property-listing",
        "title": "How to Show Nearby Amenities on a Property Listing",
        "meta": "Show nearby amenities with useful buyer context, a clear selection method, honest distance limits, and an interactive neighborhood story.",
        "intent": "how to show nearby amenities on a property listing",
        "answer": (
            "Show nearby amenities by selecting only the places that answer a real buyer question, then "
            "explain why each place matters and how it relates spatially to the property. Avoid long, "
            "unverified lists and claims of exact walking or driving time. A map or neighborhood story "
            "should support the listing narrative while making clear that routes, distances, names, and "
            "availability require independent verification."
        ),
        "outline": ["Buyer question first", "Selecting useful places", "Spatial presentation", "Distance and route caveats", "Neighborhood Story workflow", "Limitations", "Worked scenario"],
        "links": ["/templates/neighborhood-story/", "/examples/urban-condo-neighborhood-story/", "/guides/how-to-add-a-3d-map-to-a-real-estate-website/", "/guides/how-to-market-a-property-to-remote-buyers/", "/#create"],
    },
    {
        "slug": "how-to-add-a-3d-map-to-a-real-estate-website",
        "title": "How to Add a 3D Map to a Real Estate Website",
        "meta": "Plan, embed and verify an interactive 3D property map with a responsive container, domain access, lazy loading, attribution and mobile checks.",
        "intent": "how to add a 3D map to a real estate website",
        "answer": (
            "To add a 3D map to a real-estate website, publish the location story, authorize the website "
            "domain, copy the generated HTTPS iframe, place it in a responsive embed block, and verify it "
            "on the public domain. Check mobile sizing, lazy loading, attribution, consent behavior, and "
            "whether the protected widget loads after deployment. Use the platform-specific guide for "
            "the exact editor steps."
        ),
        "outline": ["Prerequisites", "Publish and authorize domain", "Copy generated embed", "Responsive container", "Performance", "Public verification", "Troubleshooting"],
        "links": ["/embed/wordpress/", "/embed/webflow/", "/embed/wix/", "/embed/squarespace/", "/guides/real-estate-listing-media-checklist/", "/#create"],
    },
    {
        "slug": "how-to-market-a-property-to-remote-buyers",
        "title": "How to Market a Property to Remote Buyers",
        "meta": "Build a remote-buyer listing that explains the property, interior, location, nearby places, access, limitations and next viewing step.",
        "intent": "how to market a property to remote buyers",
        "answer": (
            "Market a property to remote buyers by answering the questions they cannot resolve in person: "
            "what the property looks like now, how the interior works, where it sits, which nearby places "
            "matter, and how access feels. Combine current photography, plans or tours, documents, and "
            "interactive location context. Label limitations clearly and give the buyer a practical next "
            "step rather than relying on visual novelty."
        ),
        "outline": ["Remote-buyer uncertainty", "Evidence stack", "Location narrative", "Arrival and nearby places", "Trust and disclosure", "Limitations", "Publishing checklist"],
        "links": ["/guides/real-estate-listing-media-checklist/", "/templates/arrival-guide/", "/examples/waterfront-villa-property-flyover/", "/guides/3d-property-flyover-vs-virtual-tour/", "/#create"],
    },
    {
        "slug": "which-property-listings-need-an-aerial-view",
        "title": "Which Property Listings Benefit Most From an Aerial View?",
        "meta": "See which waterfront, rural, mountain, urban and remote-buyer listings gain from aerial location context, and when it adds little value.",
        "intent": "which property listings need an aerial view",
        "answer": (
            "An aerial view is most useful when the relationship between the property, surrounding land, "
            "terrain, access, or nearby places materially affects a buyer's decision and is difficult to "
            "explain with ground-level images. It adds less value to interior-led listings, unsupported "
            "locations, or pages that cannot embed the experience. Assess fit before checking coverage; "
            "the scorecard is guidance, not legal or valuation advice."
        ),
        "outline": ["Decision rule", "High-fit listings", "Medium-fit listings", "Low-fit listings", "Suitability scorecard", "High and low-fit scenarios", "Coverage next step"],
        "links": ["/guides/what-is-a-3d-property-flyover/", "/guides/3d-property-flyover-vs-drone-video/", "/examples/mountain-property-location-story/", "/examples/rural-estate-aerial-view/", "/#create"],
    },
    {
        "slug": "real-estate-listing-media-checklist",
        "title": "Real Estate Listing Media Checklist for Remote Buyers",
        "meta": "Use this checklist for photos, floor plans, tours, current video, location context, maps, documents and calls to action on a property listing.",
        "intent": "real estate listing media checklist",
        "answer": (
            "A complete real-estate listing media set should answer separate questions about current "
            "appearance, interior layout, exterior condition, location context, access, surrounding "
            "places, documents, and the next action. No single asset answers them all. Use photography, "
            "floor plans, tours or current video where appropriate, then add an interactive flyover when "
            "spatial location relationships are important to a remote buyer."
        ),
        "outline": ["Questions the listing must answer", "Current visual evidence", "Interior and layout", "Location and access", "Documents and disclosures", "Media checklist", "Limitations and handoff"],
        "links": ["/guides/3d-property-flyover-vs-drone-video/", "/guides/3d-property-flyover-vs-virtual-tour/", "/guides/how-to-market-a-property-to-remote-buyers/", "/templates/property-showcase/", "/#create"],
    },
]

TEMPLATES = [
    (
        "property-showcase",
        "Property Showcase Location Story Template",
        "Use a Property Showcase sequence to approach one confirmed property and finish with an interactive orbit that explains its immediate setting.",
        "property showcase location story template",
        "Property Showcase is the simplest Georivo story structure: confirm one property, choose a suitable approach, and finish with an interactive orbit. It works when the listing needs a clear exterior and immediate-location introduction without a longer sequence of nearby places. It does not replace current photography, interior media, title information, or a coverage check for the exact address.",
        ["Audience and result", "Required inputs", "Sequence", "Configuration steps", "Worked example", "Customization", "When not to use"],
        ["/guides/what-is-a-3d-property-flyover/", "/examples/waterfront-villa-property-flyover/", "/guides/which-property-listings-need-an-aerial-view/", "/templates/neighborhood-story/", "/#create"],
        {"audience": "Agents presenting one property and its immediate setting.", "sequence": ["Approach the confirmed property", "Identify the location", "Finish with an interactive orbit"], "limitations": ["Requires supported 3D coverage", "Does not show interiors or current exterior condition"]},
    ),
    (
        "neighborhood-story",
        "Neighborhood Story Template for Property Listings",
        "Plan a Neighborhood Story that visits selected nearby places, arrives at the property, and lets buyers explore the surrounding area in live 3D.",
        "neighborhood story template for real estate",
        "Neighborhood Story connects a property with up to three carefully selected nearby places before arriving at the confirmed address. Use it when daily access or area context is part of the buyer's decision. Each place needs a clear reason for inclusion. Do not present generated routes, distances, names, or availability as legally or navigationally exact without an independent source.",
        ["Audience and result", "Required inputs", "Point-selection rule", "Sequence", "Worked example", "Customization", "Limitations"],
        ["/guides/how-to-show-nearby-amenities-on-a-property-listing/", "/examples/urban-condo-neighborhood-story/", "/templates/arrival-guide/", "/guides/how-to-market-a-property-to-remote-buyers/", "/#create"],
        {"audience": "Agents who need to explain nearby places and neighborhood context.", "sequence": ["Visit selected places", "Travel toward the property", "Arrive and finish at the property"], "limitations": ["Up to three selected places", "Routes and distances require independent verification"]},
    ),
    (
        "arrival-guide",
        "Arrival Guide Template for Property Listings",
        "Create an Arrival Guide that travels from one meaningful starting place to the confirmed property and clarifies the general approach for remote buyers.",
        "property arrival guide template",
        "Arrival Guide starts from one selected place and travels toward the confirmed property, helping a remote buyer understand the general approach and terrain. Choose a starting point that answers a genuine arrival question, not a decorative landmark. The sequence is orientation, not turn-by-turn navigation, and it cannot replace current road information, access instructions, or independent route verification.",
        ["Audience and result", "Required inputs", "Choosing a starting point", "Sequence", "Worked example", "Customization", "When not to use"],
        ["/guides/how-to-market-a-property-to-remote-buyers/", "/examples/mountain-property-location-story/", "/templates/neighborhood-story/", "/guides/real-estate-listing-media-checklist/", "/#create"],
        {"audience": "Agents explaining the general approach to remote or unfamiliar buyers.", "sequence": ["Start at one selected place", "Show the general approach", "Arrive at the confirmed property"], "limitations": ["Not turn-by-turn navigation", "Access conditions and routes require current independent verification"]},
    ),
]

EXAMPLES = [
    ("waterfront-villa-property-flyover", "Waterfront Villa 3D Property Flyover Example", "See how a demo waterfront-villa story can relate the property to coastline, marina and access without claiming current or legal precision.", "waterfront villa 3D property flyover example", "This demo shows how a waterfront-villa flyover can explain the relationship between a confirmed property, the coastline, a marina or beach, and the general access direction. It is an illustrative scenario, not a customer case or current survey. The scene does not establish legal boundaries, exact distances, route conditions, property condition, or the present availability of nearby places.", ["Demo disclosure", "Live or poster demonstration", "Scenario", "Selected points", "Camera logic", "Buyer learning", "What it does not show", "Build notes"], ["/templates/property-showcase/", "/guides/how-to-market-a-property-to-remote-buyers/", "/guides/which-property-listings-need-an-aerial-view/", "/examples/mountain-property-location-story/", "/#create"], "Waterfront villa for a remote buyer", ["Property", "coastline", "beach or marina", "access road"]),
    ("urban-condo-neighborhood-story", "Urban Condo Neighborhood Story Example", "Explore a demo urban-condo story that connects a building with selected daily places while keeping travel and availability claims qualified.", "urban condo neighborhood story example", "This demo illustrates how an urban-condo Neighborhood Story can connect a confirmed building with a station, park, and city-center reference chosen for a relocating buyer. It demonstrates editorial selection and spatial context, not a verified customer result. Names, availability, route behavior, travel times, building condition, and legal information must be checked independently for a real listing.", ["Demo disclosure", "Live or poster demonstration", "Relocating-buyer scenario", "Selected places", "Narrative order", "Buyer learning", "Limitations", "Build notes"], ["/templates/neighborhood-story/", "/guides/how-to-show-nearby-amenities-on-a-property-listing/", "/guides/how-to-market-a-property-to-remote-buyers/", "/examples/waterfront-villa-property-flyover/", "/#create"], "Urban condo for a relocating buyer", ["Building", "station", "park", "centre"]),
    ("rural-estate-aerial-view", "Rural Estate Aerial View Example", "See a demo rural-estate aerial story that communicates scale and remoteness without drawing false parcel boundaries or promising current imagery.", "rural estate aerial view example", "This demo explains how an aerial location story can help a buyer understand a rural estate in relation to surrounding land, the main road, and a nearby town. It does not draw or verify parcel boundaries and is not current site photography, a survey, valuation, or access report. Any real listing needs verified title, road, condition, and distance information.", ["Demo disclosure", "Live or poster demonstration", "Estate scenario", "Selected points", "Scale narrative", "Buyer learning", "Legal and visual limitations", "Build notes"], ["/guides/which-property-listings-need-an-aerial-view/", "/templates/property-showcase/", "/guides/3d-property-flyover-vs-drone-video/", "/examples/mountain-property-location-story/", "/#create"], "Large rural estate and surrounding land", ["Property", "surrounding land", "main road", "town"]),
    ("mountain-property-location-story", "Mountain Property Location Story Example", "Review a demo mountain-property arrival story that explains terrain and general approach without presenting it as navigation or current access evidence.", "mountain property location story example", "This demo shows how a mountain-property location story can orient a buyer using a valley or landmark, the general approach, an entrance reference, and the confirmed property. It is not turn-by-turn navigation or proof of present road access, weather, safety, legal access rights, or property condition. Those details require current authoritative sources and local verification.", ["Demo disclosure", "Live or poster demonstration", "Mountain scenario", "Selected points", "Arrival logic", "Buyer learning", "Access limitations", "Build notes"], ["/templates/arrival-guide/", "/guides/how-to-market-a-property-to-remote-buyers/", "/guides/which-property-listings-need-an-aerial-view/", "/examples/rural-estate-aerial-view/", "/#create"], "Mountain home with complex access context", ["Valley or landmark", "approach", "entrance", "property"]),
]

INTEGRATIONS = [
    ("wordpress", "How to Embed a Georivo 3D Map in WordPress", "Embed a published Georivo widget in WordPress with the Custom HTML block, a responsive wrapper, domain authorization and public-page verification.", "embed 3D map in WordPress", ["Prerequisites", "Copy the Georivo embed", "Add a Custom HTML block", "Responsive sizing", "Publish and verify", "Troubleshooting", "Performance"], ["/guides/how-to-add-a-3d-map-to-a-real-estate-website/", "/embed/webflow/", "/templates/property-showcase/", "/examples/waterfront-villa-property-flyover/", "/#create"], "WordPress 7.0 documentation checked 2026-07-24"),
    ("webflow", "How to Embed a Georivo 3D Property Map in Webflow", "Add a Georivo iframe with Webflow's Code Embed element, preserve the aspect ratio, publish the authorized domain and verify the live widget.", "embed 3D property map in Webflow", ["Prerequisites", "Copy the Georivo embed", "Add a Code Embed element", "Responsive sizing", "Publish domain and verify", "Troubleshooting", "Performance"], ["/guides/how-to-add-a-3d-map-to-a-real-estate-website/", "/embed/wordpress/", "/templates/neighborhood-story/", "/examples/urban-condo-neighborhood-story/", "/#create"], "Webflow Code Embed help checked 2026-07-24"),
    ("wix", "How to Embed a Property Flyover in Wix", "Place a Georivo widget with Wix Embed HTML, use an HTTPS iframe, authorize the public domain, set desktop and mobile sizing, and verify after publish.", "embed property flyover in Wix", ["Prerequisites", "Copy the Georivo embed", "Add Embed HTML", "Desktop and mobile sizing", "Publish and verify", "Troubleshooting", "Performance"], ["/guides/how-to-add-a-3d-map-to-a-real-estate-website/", "/embed/squarespace/", "/templates/arrival-guide/", "/examples/mountain-property-location-story/", "/#create"], "Wix Editor embed help checked 2026-07-24"),
    ("squarespace", "How to Embed a Georivo 3D Map in Squarespace", "Add a Georivo HTTPS iframe with a Squarespace Code block, confirm plan support, make it responsive, authorize the domain and verify the public page.", "embed 3D property map in Squarespace", ["Prerequisites and plan support", "Copy the Georivo embed", "Add a Code block", "Responsive layout", "Publish and verify", "Troubleshooting", "Performance"], ["/guides/how-to-add-a-3d-map-to-a-real-estate-website/", "/embed/wix/", "/templates/property-showcase/", "/examples/rural-estate-aerial-view/", "/#create"], "Squarespace Code blocks help checked 2026-07-24"),
]


def editorial(cadence_days):
    return {
        "author": "Georivo Editorial",
        "reviewer": "Georivo Product Review",
        "owner": "Georivo Content",
        "reviewDueAt": (TODAY + timedelta(days=cadence_days)).isoformat(),
        "reviewCadence": f"every {cadence_days} days or after a material product/source change",
        "factCheckedAt": TODAY.isoformat(),
    }


def brief(item, content_type, details=None, extra_sources=None):
    prefixes = {
        "guide": "guides",
        "template": "templates",
        "example": "examples",
        "integration_guide": "embed",
    }
    path = f"/{prefixes[content_type]}/{item['slug']}/"
    return {
        "contentType": content_type,
        "targetPath": path,
        "canonicalGroup": f"georivo:{content_type}:{item['slug']}",
        "preserveSlug": True,
        "publicationMode": "native_next_content_store",
        "nativeProjectRoot": "/var/www/georivo-blog",
        "pageBrief": {
            "primaryIntent": item["intent"],
            "seoTitle": item["title"],
            "metaDescription": item["meta"],
            "h1": item["title"],
            "directAnswer": item["answer"],
            "outline": item["outline"],
            "approvedInternalLinks": item["links"],
            "sourceReferences": [PRODUCT_SOURCE, GOOGLE_SOURCE] + list(extra_sources or []),
            "editorial": editorial(90 if content_type in {"integration_guide", "example"} else 180),
            "primaryCta": {"label": "Check a property address", "url": "/#create"},
            "contentDetails": details or {},
            "approvals": {
                "editorialReview": False,
                "productFactCheck": False,
                "seoReview": False,
                "browserQa": False,
            },
        },
    }


def all_jobs():
    jobs = []
    for item in GUIDES:
        jobs.append((item, "guide", brief(item, "guide")))
    for slug, title, meta, intent, answer, outline, links, details in TEMPLATES:
        item = {"slug": slug, "title": title, "meta": meta, "intent": intent, "answer": answer, "outline": outline, "links": links}
        jobs.append((item, "template", brief(item, "template", details)))
    for slug, title, meta, intent, answer, outline, links, scenario, points in EXAMPLES:
        item = {"slug": slug, "title": title, "meta": meta, "intent": intent, "answer": answer, "outline": outline, "links": links}
        details = {
            "exampleType": "demo",
            "scenario": scenario,
            "selectedPoints": points,
            "limitations": ["Illustrative demo, not a customer case", "No legal, navigational, distance, condition, or current-imagery guarantee"],
            "lastFunctionalCheck": "",
        }
        jobs.append((item, "example", brief(item, "example", details)))
    for platform, title, meta, intent, outline, links, version_note in INTEGRATIONS:
        answer = (
            f"To embed a Georivo location story in {platform.title()}, first publish the widget and authorize "
            "the exact public website domain in Georivo. Copy the generated HTTPS iframe, add it through "
            "the platform's supported HTML or code element, preserve its aspect ratio, and publish the "
            "page. Verify the live public URL on desktop and mobile, including domain access, loading, "
            "attribution, consent behavior, and fallback handling."
        )
        item = {"slug": platform, "title": title, "meta": meta, "intent": intent, "answer": answer, "outline": outline, "links": links}
        details = {
            "platform": platform.title(),
            "platformVersionNote": version_note,
            "versionCheckedAt": TODAY.isoformat(),
            "prerequisites": ["Published Georivo widget", "Editor access", "Authorized public domain", "Platform plan that permits iframe/custom code"],
            "troubleshooting": ["Blank iframe", "Blocked or mismatched domain", "CSP or mixed content", "Incorrect height", "Mobile crop", "Stale cache or consent block"],
            "embedContract": "Use only the iframe copied from the published Georivo widget. Never expose or invent its protected URL or token.",
        }
        jobs.append((item, "integration_guide", brief(item, "integration_guide", details, [PLATFORM_SOURCES[platform]])))
    return jobs


def seed(db_path, site_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
    if not site:
        raise SystemExit(f"site {site_id} not found")
    if site["domain"] != "georivo.com":
        raise SystemExit(f"site {site_id} is {site['domain']}, expected georivo.com")
    created = updated = skipped = 0
    for item, content_type, sources in all_jobs():
        target_path = sources["targetPath"]
        existing = conn.execute(
            "select id,status from content_jobs where site_id=? and json_extract(sources_json,'$.targetPath')=?",
            (site_id, target_path),
        ).fetchone()
        payload = json.dumps(sources, ensure_ascii=False, separators=(",", ":"))
        now = f"{TODAY.isoformat()}T00:00:00+00:00"
        if existing:
            if existing["status"] == "PUBLISHED":
                skipped += 1
                continue
            conn.execute(
                "update content_jobs set topic=?,slug=?,title=?,description=?,category=?,sources_json=?,updated_at=? where id=?",
                (item["title"], item["slug"], item["title"], item["meta"], content_type.replace("_", " ").title(), payload, now, existing["id"]),
            )
            conn.execute(
                "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
                (site_id, existing["id"], now, "INFO", "content-plan", f"Refreshed approved Georivo brief for {target_path}"),
            )
            updated += 1
            continue
        job_id = hashlib.sha256(f"georivo:{target_path}".encode()).hexdigest()[:24]
        conn.execute(
            """insert into content_jobs(
                 id,site_id,topic,slug,status,title,description,category,hero_image,draft_html,
                 faq_json,error,sources_json,visibility,created_at,updated_at
               ) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                job_id, site_id, item["title"], item["slug"], "IDEA", item["title"], item["meta"],
                content_type.replace("_", " ").title(), "", "", "[]", None, payload, "public", now, now,
            ),
        )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (site_id, job_id, now, "INFO", "content-plan", f"Created approved Georivo brief for {target_path}"),
        )
        created += 1
    conn.commit()
    total = conn.execute(
        "select count(*) from content_jobs where site_id=? and json_extract(sources_json,'$.contentType') <> 'blog'",
        (site_id,),
    ).fetchone()[0]
    conn.close()
    print(json.dumps({"created": created, "updated": updated, "skippedPublished": skipped, "typedJobs": total}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=14)
    args = parser.parse_args()
    seed(Path(args.db), args.site_id)
