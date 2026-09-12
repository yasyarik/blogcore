import json
import os
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from strategy_tools import StrategyToolExecutor, tool_declarations


PRIORITY_DOMAINS = {
    "myugc.studio",
    "laycanmatch.com",
    "solocruz.com",
    "airep24.com",
    "cabinjoin.com",
    "yas.ooo",
}

STRATEGY_CHANNELS = (
    "website",
    "blog",
    "linkedin",
    "instagram",
    "tiktok",
    "youtube",
    "pinterest",
    "x",
    "threads",
    "reddit",
    "email",
    "directories",
    "partnerships",
    "communities",
    "pr",
    "podcast",
)

STRATEGY_SCHEMA = {
    "type": "object",
    "required": [
        "executiveSummary", "businessModel", "market", "channelStrategy",
        "mediaPlan", "leadGeneration", "offsite", "newsletter",
        "experiments", "first30Days", "risks", "dataGaps",
    ],
    "properties": {
        "executiveSummary": {"type": "string"},
        "businessModel": {
            "type": "object",
            "required": ["primaryGoal", "conversionEvents", "audiences", "offers", "constraints"],
            "properties": {
                "primaryGoal": {"type": "string"},
                "conversionEvents": {"type": "array", "items": {"type": "string"}},
                "audiences": {"type": "array", "items": {"type": "string"}},
                "offers": {"type": "array", "items": {"type": "string"}},
                "constraints": {"type": "array", "items": {"type": "string"}},
            },
        },
        "market": {
            "type": "object",
            "required": ["category", "demandThemes", "competitors", "positioningOpportunity"],
            "properties": {
                "category": {"type": "string"},
                "demandThemes": {"type": "array", "items": {"type": "string"}},
                "positioningOpportunity": {"type": "string"},
                "competitors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "url", "positioning", "strengths", "gaps"],
                        "properties": {
                            "name": {"type": "string"}, "url": {"type": "string"},
                            "positioning": {"type": "string"},
                            "strengths": {"type": "array", "items": {"type": "string"}},
                            "gaps": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        },
        "channelStrategy": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["channel", "score", "priority", "role", "reason", "formats", "cadence", "contentPillars", "cta", "kpis", "prerequisites", "avoid"],
                "properties": {
                    "channel": {"type": "string"}, "score": {"type": "integer"},
                    "priority": {"type": "string"}, "role": {"type": "string"},
                    "reason": {"type": "string"},
                    "formats": {"type": "array", "items": {"type": "string"}},
                    "cadence": {"type": "string"},
                    "contentPillars": {"type": "array", "items": {"type": "string"}},
                    "cta": {"type": "string"},
                    "kpis": {"type": "array", "items": {"type": "string"}},
                    "prerequisites": {"type": "array", "items": {"type": "string"}},
                    "avoid": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "mediaPlan": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["week", "channel", "format", "title", "objective", "funnelStage", "cta", "generator", "kpi", "executionMode", "repurposeGroup", "rationale"],
                "properties": {
                    "week": {"type": "integer"}, "channel": {"type": "string"},
                    "format": {"type": "string"}, "title": {"type": "string"},
                    "objective": {"type": "string"}, "funnelStage": {"type": "string"},
                    "cta": {"type": "string"}, "generator": {"type": "string"},
                    "kpi": {"type": "string"}, "executionMode": {"type": "string"},
                    "repurposeGroup": {"type": "string"}, "rationale": {"type": "string"},
                    "contentAction": {"type": "string"},
                    "targetPath": {"type": "string"},
                    "existingContentUrl": {"type": "string"},
                    "templateEvidence": {"type": "string"},
                    "refreshEvidence": {"type": "string"},
                    "changeBrief": {"type": "string"},
                    "opportunityEvidence": {"type": "string"},
                    "slideCount": {"type": "integer"},
                    "pinType": {"type": "string"},
                    "boardKey": {"type": "string"},
                    "destinationUrl": {"type": "string"},
                    "visualBrief": {"type": "string"},
                    "interfaceReference": {"type": "string"},
                    "overlayText": {"type": "string"},
                    "pinDescription": {"type": "string"},
                    "altText": {"type": "string"},
                    "storyboard": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["slide", "role", "onScreenText", "visualDirection"],
                            "properties": {
                                "slide": {"type": "integer"},
                                "role": {"type": "string"},
                                "onScreenText": {"type": "string"},
                                "visualDirection": {"type": "string"},
                                "speakerNotes": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
        "leadGeneration": {"type": "array", "items": {"type": "object", "required": ["initiative", "audience", "offer", "capturePoint", "followUp", "successMetric"], "properties": {"initiative": {"type": "string"}, "audience": {"type": "string"}, "offer": {"type": "string"}, "capturePoint": {"type": "string"}, "followUp": {"type": "string"}, "successMetric": {"type": "string"}}}},
        "offsite": {"type": "array", "items": {"type": "object", "required": ["type", "target", "url", "reason", "requirements", "action", "priority"], "properties": {"type": {"type": "string"}, "target": {"type": "string"}, "url": {"type": "string"}, "reason": {"type": "string"}, "requirements": {"type": "array", "items": {"type": "string"}}, "action": {"type": "string"}, "priority": {"type": "string"}}}},
        "newsletter": {"type": "object", "required": ["recommended", "reason", "audience", "captureMethod", "cadence", "contentPromise", "firstSequence"], "properties": {"recommended": {"type": "boolean"}, "reason": {"type": "string"}, "audience": {"type": "string"}, "captureMethod": {"type": "string"}, "cadence": {"type": "string"}, "contentPromise": {"type": "string"}, "firstSequence": {"type": "array", "items": {"type": "string"}}}},
        "experiments": {"type": "array", "items": {"type": "object", "required": ["name", "hypothesis", "execution", "durationDays", "successMetric", "decisionRule"], "properties": {"name": {"type": "string"}, "hypothesis": {"type": "string"}, "execution": {"type": "string"}, "durationDays": {"type": "integer"}, "successMetric": {"type": "string"}, "decisionRule": {"type": "string"}}}},
        "first30Days": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "dataGaps": {"type": "array", "items": {"type": "string"}},
    },
}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect(db_path):
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma foreign_keys=on")
    return conn


def ensure_strategy_schema(db_path):
    with _connect(db_path) as conn:
        conn.executescript(
            """
            create table if not exists agent_strategy_profiles (
                site_id integer primary key,
                priority integer not null default 0,
                status text not null default 'NOT_ANALYZED',
                strategy_model text,
                strategy_version integer not null default 0,
                strategy_json text not null default '{}',
                evidence_json text not null default '{}',
                last_run_id integer,
                last_analyzed_at text,
                next_review_at text,
                error text,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create table if not exists agent_strategy_runs (
                id integer primary key autoincrement,
                site_id integer not null,
                trigger text not null,
                model text not null,
                status text not null,
                started_at text not null,
                finished_at text,
                evidence_json text not null default '{}',
                result_json text not null default '{}',
                error text,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists agent_strategy_runs_site_started_idx on agent_strategy_runs(site_id, started_at desc);
            create table if not exists agent_media_plan_items (
                id integer primary key autoincrement,
                site_id integer not null,
                strategy_version integer not null,
                week integer not null,
                channel text not null,
                format text not null,
                title text not null,
                objective text,
                funnel_stage text,
                cta text,
                generator text,
                kpi text,
                execution_mode text not null default 'manual',
                repurpose_group text,
                rationale text,
                status text not null default 'PROPOSED',
                details_json text not null default '{}',
                created_at text not null,
                updated_at text not null,
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists agent_media_plan_site_version_idx on agent_media_plan_items(site_id, strategy_version, week, id);
            create table if not exists agent_content_intent_rules (
                id integer primary key autoincrement,
                site_id integer not null,
                intent_key text not null,
                required_action text not null,
                target_path text not null default '',
                rationale text not null,
                status text not null default 'ACTIVE',
                created_at text not null,
                updated_at text not null,
                unique(site_id, intent_key),
                foreign key(site_id) references sites(id) on delete cascade
            );
            create index if not exists agent_content_intent_rules_site_idx on agent_content_intent_rules(site_id, status);
            """
        )
        now = _now()
        for row in conn.execute("select id, lower(domain) as domain from sites").fetchall():
            priority = 1 if row["domain"] in PRIORITY_DOMAINS else 0
            conn.execute(
                """insert into agent_strategy_profiles(site_id,priority,updated_at) values(?,?,?)
                   on conflict(site_id) do update set priority=max(agent_strategy_profiles.priority,excluded.priority)""",
                (row["id"], priority, now),
            )


def _safe_json(value, fallback):
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(fallback)) else fallback
    except Exception:
        return fallback


def _topic_tokens(text):
    stop = {
        "about", "after", "and", "are", "best", "blog", "for", "from", "guide", "guides", "how",
        "into", "the", "this", "tips", "to", "using", "what", "when", "with", "your", "you",
    }
    words = []
    for word in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9-]{2,}", (text or "").lower()):
        if word in stop:
            continue
        if word.endswith("s") and len(word) > 4:
            word = word[:-1]
        if word not in words:
            words.append(word)
    return words


def _topic_similarity(left, right):
    left_tokens, right_tokens = set(_topic_tokens(left)), set(_topic_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = left_tokens & right_tokens
    jaccard = len(overlap) / len(left_tokens | right_tokens)
    coverage = len(overlap) / min(len(left_tokens), len(right_tokens))
    return max(jaccard, coverage * 0.82)


def _content_index(rows):
    result = []
    for row in rows:
        sources = _safe_json(row["sources_json"], {})
        title = row["title"] or row["topic"] or sources.get("title") or ""
        path = urllib.parse.urlsplit(row["published_url"] or "").path
        target_path = str(sources.get("targetPath") or path or "")
        comparable = " ".join([
            title, row["topic"] or "", row["description"] or "", (row["slug"] or "").replace("-", " "),
            target_path.replace("-", " ").replace("/", " "),
        ]).strip()
        if comparable:
            result.append({
                "id": row["id"], "title": title, "status": row["status"],
                "url": row["published_url"] or "", "targetPath": target_path,
                "contentType": sources.get("contentType") or row["category"] or "blog",
                "comparable": comparable,
            })
    return result


def _find_existing_topic(title, existing_content):
    token_sets = [set(_topic_tokens(item["comparable"])) for item in existing_content]
    document_frequency = {}
    for tokens in token_sets:
        for token in tokens:
            document_frequency[token] = document_frequency.get(token, 0) + 1
    common_threshold = max(5, int(len(existing_content) * 0.02))
    common_tokens = {token for token, count in document_frequency.items() if count >= common_threshold}
    common_tokens.update({"cabin", "cruise", "cruiser", "ship", "solo", "travel", "traveler"})
    title_tokens = set(_topic_tokens(title))
    normalized_title = " ".join(re.findall(r"[a-z0-9]+", title.lower()))
    best = None
    for existing, existing_tokens in zip(existing_content, token_sets):
        score = _topic_similarity(title, existing["comparable"])
        distinctive_overlap = (title_tokens & existing_tokens) - common_tokens
        normalized_existing = " ".join(re.findall(r"[a-z0-9]+", str(existing.get("title") or "").lower()))
        title_ratio = SequenceMatcher(None, normalized_title, normalized_existing).ratio() if normalized_existing else 0.0
        score = max(score, title_ratio)
        if not distinctive_overlap and title_ratio < 0.72:
            score = 0.0
        if best is None or score > best["score"]:
            best = {**existing, "score": score}
    return best if best and best["score"] >= 0.68 else None


def _normalized_path(value):
    path = urllib.parse.urlsplit(str(value or "")).path or str(value or "")
    path = "/" + path.strip("/") if path.strip("/") else "/"
    return path.casefold()


def _matches_editorial_intent(candidate, intent_key):
    """Match an owner-defined intent rule against a proposed content assignment.

    This intentionally uses coverage of the rule's meaningful terms rather
    than title similarity: a plan may rename “MVP development cost” as
    “MVP pricing and scope” while remaining the same editorial intent.
    """
    rule_terms = set(_topic_tokens(intent_key))
    candidate_terms = set(_topic_tokens(candidate))
    if not rule_terms or not candidate_terms:
        return False
    return len(rule_terms & candidate_terms) / len(rule_terms) >= 0.67


def _sitemap_content_index(homepage_url):
    parsed_home = urllib.parse.urlsplit(str(homepage_url or ""))
    if not parsed_home.scheme or not parsed_home.netloc:
        return []
    origin = f"{parsed_home.scheme}://{parsed_home.netloc}"
    queue = [urllib.parse.urljoin(origin + "/", "sitemap.xml")]
    visited, urls = set(), []
    while queue and len(visited) < 50 and len(urls) < 10000:
        sitemap_url = queue.pop(0)
        if sitemap_url in visited:
            continue
        visited.add(sitemap_url)
        try:
            request = urllib.request.Request(sitemap_url, headers={"User-Agent": "BlogCoreStrategyAgent/1.0"})
            body = urllib.request.urlopen(request, timeout=20).read().decode("utf-8", errors="replace")
        except Exception:
            continue
        locations = [value.replace("&amp;", "&").strip() for value in re.findall(r"<loc>\s*(.*?)\s*</loc>", body, flags=re.I | re.S)]
        if "<sitemapindex" in body.lower():
            for location in locations:
                if urllib.parse.urlsplit(location).netloc == parsed_home.netloc and location not in visited:
                    queue.append(location)
            continue
        for location in locations:
            parsed = urllib.parse.urlsplit(location)
            if parsed.netloc != parsed_home.netloc:
                continue
            path = _normalized_path(parsed.path)
            slug_text = " ".join(part.replace("-", " ") for part in path.strip("/").split("/") if part) or parsed_home.netloc
            urls.append({
                "id": f"sitemap:{path}", "title": slug_text, "status": "LIVE_SITEMAP",
                "url": urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")),
                "targetPath": path, "contentType": "live-site", "comparable": f"{slug_text} {path.replace('-', ' ')}",
            })
            if len(urls) >= 10000:
                break
    return urls


def _social_content_index(rows):
    result = []
    for row in rows:
        try:
            payload = json.loads(row["content_json"] or "{}")
        except json.JSONDecodeError:
            payload = {}
        title = str(row["content_text"] or "").strip()
        if not title:
            for key in ("tiktokCarousel", "instagramCarousel", "pinterestPin", "instagramReel"):
                value = payload.get(key)
                if isinstance(value, dict):
                    title = str(value.get("title") or value.get("caption") or "").strip()
                    if title:
                        break
        comparable = " ".join(filter(None, [row["channel"], row["asset_type"], title, json.dumps(payload, ensure_ascii=False)]))
        result.append({
            "id": row["id"], "title": title or f"{row['channel']} {row['asset_type']} {row['id']}",
            "status": row["status"], "url": row["remote_url"] or "", "targetPath": "",
            "contentType": row["asset_type"], "channel": row["channel"], "comparable": comparable,
        })
    return result


def _site_context(db_path, site_id):
    with _connect(db_path) as conn:
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        if not site:
            raise KeyError("site not found")
        theme = conn.execute("select title,description from site_theme_profiles where site_id=?", (site_id,)).fetchone()
        discovery = conn.execute("select direction,category_hint from topic_discovery_settings where site_id=?", (site_id,)).fetchone()
        counts = conn.execute(
            """select
                 sum(case when status in ('PUBLISHED','IMPORTED') then 1 else 0 end) published,
                 sum(case when status in ('QUEUED','PLANNED','DRAFT') then 1 else 0 end) active,
                 sum(case when status in ('FAILED','ERROR') then 1 else 0 end) failed
               from content_jobs where site_id=?""",
            (site_id,),
        ).fetchone()
        connections = [dict(row) for row in conn.execute("select provider,status,display_name from social_connections where site_id=?", (site_id,)).fetchall()]
        autopublish = conn.execute("select enabled,channels_json,social_cadences_json from autopublish_settings where site_id=?", (site_id,)).fetchone()
        try:
            pinterest_strategy = conn.execute("select enabled,daily_pin_target,boards_json,landing_pages_json,mix_json from pinterest_strategies where site_id=?", (site_id,)).fetchone()
        except sqlite3.OperationalError:
            pinterest_strategy = None
        content_rows = conn.execute(
            """select id,status,topic,slug,title,description,category,published_url,sources_json
               from content_jobs where site_id=? order by updated_at desc""", (site_id,)
        ).fetchall()
        existing_content = _content_index(content_rows)
        editorial_decisions = [dict(row) for row in conn.execute(
            """select intent_key,required_action,target_path,rationale
               from agent_content_intent_rules where site_id=? and status='ACTIVE'
               order by id""",
            (site_id,),
        ).fetchall()]
        social_rows = conn.execute(
            """select id,channel,asset_type,status,content_text,content_json,remote_url
               from social_posts where site_id=? and status in ('DRAFT','SCHEDULED','SUBMITTED','PUBLISHED','SENT')
               order by updated_at desc,id desc""", (site_id,)
        ).fetchall()
        existing_social = _social_content_index(social_rows)
        queued_plan_rows = conn.execute(
            """select id,channel,format,status,title,details_json from agent_media_plan_items
               where site_id=? and status in ('QUEUED','GENERATING','READY','APPROVED','SCHEDULED')""",
            (site_id,),
        ).fetchall()
        for row in queued_plan_rows:
            for channel_name in ("instagram", "tiktok", "pinterest", "threads", "twitter", "youtube", "reddit"):
                if channel_name not in str(row["channel"] or "").lower():
                    continue
                existing_social.append({
                    "id": f"media-plan:{row['id']}:{channel_name}", "title": row["title"], "status": row["status"],
                    "url": "", "targetPath": "", "contentType": row["format"], "channel": channel_name,
                    "comparable": " ".join(filter(None, [channel_name, row["format"], row["title"], row["details_json"]])),
                })
        recent = [dict(row) for row in conn.execute(
            """select title,category as content_type,status,published_url from content_jobs where site_id=?
               order by updated_at desc limit 40""", (site_id,)
        ).fetchall()]
    sitemap_content = _sitemap_content_index(site["homepage_url"] or f"https://{site['domain']}/")
    known_paths = {_normalized_path(item.get("targetPath") or item.get("url")) for item in existing_content}
    existing_content.extend(item for item in sitemap_content if _normalized_path(item.get("targetPath")) not in known_paths)
    return {
        "site": dict(site),
        "homepageProfile": dict(theme) if theme else {},
        "discoveryProfile": dict(discovery) if discovery else {},
        "contentInventory": {
            "published": int(counts["published"] or 0), "active": int(counts["active"] or 0),
            "failed": int(counts["failed"] or 0), "recent": recent,
        },
        "connections": connections,
        "autopublish": {**(dict(autopublish) if autopublish else {}), "channels": _safe_json(autopublish["channels_json"] if autopublish else "", []), "cadences": _safe_json(autopublish["social_cadences_json"] if autopublish else "", {})},
        "pinterestStrategy": {
            **(dict(pinterest_strategy) if pinterest_strategy else {}),
            "boards": _safe_json(pinterest_strategy["boards_json"] if pinterest_strategy else "", []),
            "landingPages": _safe_json(pinterest_strategy["landing_pages_json"] if pinterest_strategy else "", []),
            "mix": _safe_json(pinterest_strategy["mix_json"] if pinterest_strategy else "", {}),
        },
        "_existingContentIndex": existing_content,
        "_existingSocialIndex": existing_social,
        "editorialDecisions": editorial_decisions,
    }


def _strategy_prompt(context):
    site = context["site"]
    prompt_context = {key: value for key, value in context.items() if not key.startswith("_")}
    return f"""
You are the senior growth strategist responsible for one connected website inside a multi-site AI content factory.

Research date: {datetime.now(timezone.utc).date().isoformat()}
Website: {site.get('homepage_url') or ('https://' + site['domain'] + '/')}
Domain: {site['domain']}
Languages: {site.get('languages') or '[\"en\"]'}

This is one autonomous analysis run. Before writing any strategy, you MUST investigate the connected site yourself through the provided read-only VPS tools. Call inspect_site_configuration, inspect_content_operations, list_factory_content, list_site_files, read_site_files, inspect_site_databases and inspect_site_runtime. Paginate list_factory_content until nextCursor is null; do not rely on a cached prompt snapshot. Read the current product entry points, routes, templates or application source and relevant database schemas/counts. If inspect_site_databases finds a database, use query_site_database for relevant aggregate product/usage facts before deciding the strategy. Treat storedContextIsUnverifiedHint and all cached Blog Core descriptions only as historical hints. Current files, current databases and current runtime state take precedence.

After the internal audit, you MUST call research_external_web once with at least four distinct current research queries covering demand, competitors, off-site distribution targets and platform/community opportunities. Use its grounded findings and source URLs. You may additionally use built-in Google Search and URL Context for follow-up inspection. Do not submit until research_external_web has actually succeeded; model memory is not external research. Do not infer that a product is upcoming, waitlisted, launched, priced, verified, autonomous or integrated unless the internal tools prove it. If required evidence cannot be obtained, return RESEARCH_BLOCKED rather than inventing a strategy.

Build an evidence-led 90-day growth strategy. Do not merely recommend more blog posts. Decide which channels and formats deserve production capacity, which should be tested, and which should be avoided.

The strategy must cover SEO money pages, editorial content, LinkedIn, Instagram posts/carousels/Reels, TikTok photo carousels/videos, YouTube/Shorts, Pinterest, X, Threads, Reddit, email/newsletters, lead magnets, directories/marketplaces, partnerships, communities, PR and podcasts. A low score or explicit rejection is valid. Do not force every channel.

Available AI production capabilities:
- Gemini Pro for research, reasoning, strategy, long-form copy and structured plans.
- Gemini Flash for frequent classification, adaptation and monitoring.
- Gemini Image/Omni image generation for native images, diagrams, pins and carousel slides.
- Veo for product demonstrations, short-form video and cinematic social assets when video has a real strategic role.
- Existing source-authoritative website templates for SEO pages and articles.
- Existing article hero images should be reused for text-only social adaptations when appropriate; do not generate redundant images.
- Existing Blog Core adapters may publish website/blog, LinkedIn, Telegram, X, Tumblr, Pinterest, Instagram, TikTok, Threads, Reddit and podcasts when the correct account is connected. A recommendation may identify a missing connection but must not pretend it exists.

Hard rules:
1. Never invent traffic, conversion, search-volume, competitor feature, directory acceptance or platform-performance data.
2. Separate verified facts, reasoned hypotheses and missing data.
3. Every competitor and off-site target must have a current public URL. Do not invent directories.
4. Do not promise rankings, conversions, accuracy, autonomous operation or business outcomes.
5. Every channel entry needs a 0-100 fit score, role, cadence, native formats, CTA, KPIs, prerequisites and what to avoid.
6. Produce a concrete 12-week media plan. Each item is a finished production assignment, not a vague theme. Connect related items with repurposeGroup and adapt them natively by default. The explicit exception is an Instagram + TikTok photo carousel: when both destinations are active, render the carousel once and publish the exact same approved slides in the same order to both channels; never invent separate topics or regenerate a second carousel for TikTok.
7. executionMode must be one of: factory-now, connect-first, manual-partnership, manual-directory, data-required.
8. generator must name the realistic production path: Gemini Pro, Gemini Flash, Gemini Image, Veo, Existing asset, Human outreach, or a sensible combination.
9. Prefer measurable bounded experiments over permanent cadence guesses.
10. Where email is useful, specify the lead offer, capture point, consent-safe follow-up and first sequence. Where it is not useful, say so.
11. Never use the words waitlist, early access, founding member, verified profile or launch unless current site files or databases explicitly prove that state.
12. Do not upgrade a narrow fact into a broader trust claim. Email verification does not mean an identity-verified user, a verified profile, a verified listing, a verified sailing, verified data or a verified transaction. Name the exact implemented mechanism or omit the claim.
13. Never write a numeric customer saving, revenue lift, conversion lift, workload reduction or other achieved outcome unless the current internal data proves that exact outcome. Targets belong only in successMetric/KPI fields and must be labelled as targets.
14. You must finish the internal tool audit and external research before submitting the result.
15. Finish by calling submit_strategy exactly once with the complete strategy. Do not print the strategy as JSON or explanatory prose.
16. Every Instagram or TikTok carousel/photo-carousel assignment must include slideCount and a complete storyboard with exactly that many ordered slides. Each slide must contain its production role, finished on-screen copy, and visual direction; include speakerNotes only when narration is actually used. When both Instagram and TikTok carousel publishing are active, represent it as one `Instagram + TikTok` shared-carousel assignment with one title, one repurposeGroup and one storyboard. Its generator must state that the slides are rendered once for Instagram and reused unchanged for TikTok. A carousel without this slide-by-slide contract is not a finished production assignment.
17. Draft every candidate media-plan assignment internally, then call search_factory_content once with all candidates in a single batch formatted as `channel | title or target path`. Reconcile returned factory jobs, live canonical routes and same-channel socialMatches. Set contentAction to new, refresh, or expand-existing for SEO/blog work. Never propose a new URL for an intent already covered by a published, imported, queued, draft, generating, failed or live-site result. Work already queued, generating, drafted or scheduled is operational context and MUST NOT appear as a media-plan assignment. Never propose an Instagram, TikTok, Pinterest, Threads, X or YouTube asset that duplicates a same-channel DRAFT, SCHEDULED, SUBMITTED, PUBLISHED or SENT social item. Check a combined `Instagram + TikTok` carousel candidate against the existing history of both channels. Cross-channel repurposing is adapted natively except for the exact shared-carousel rule in 6 and 16. For refresh/expand-existing, copy the exact existingContentUrl or targetPath returned by the tool.
18. Every SEO money page must include its verified canonical targetPath and templateEvidence naming the existing approved source-site route/template found during the internal audit. Never invent a route or create a parallel page outside the approved template system. If the approved page already resolves and rule 19 supplies evidence for a change, use refresh or expand-existing rather than new; otherwise omit it from the plan.
19. Never add refresh or expand-existing merely to fill an SEO or money-page slot. It is allowed only when current evidence proves a specific defect or opportunity, such as stale facts, declining impressions/CTR, query-intent undercoverage, a technical/indexing defect, or a documented content gap. Include refreshEvidence with the observed fact and changeBrief with the exact bounded edit. If no such evidence exists, omit the assignment entirely; evaluating SEO does not require manufacturing an SEO task.
20. A new SEO/blog assignment must include opportunityEvidence naming the uncovered intent and the current demand/research evidence supporting it. Existing queue items do not count as new ideas and must not consume weeks in the strategic media plan. If SEO/editorial is scored 60 or higher, include at least one genuinely new factory-checked assignment or lower the channel score and explain why no uncovered opportunity merits production.
21. `editorialDecisions` in the internal context are hard operating rules set by the owner. Before considering any new URL, match every candidate against those intent keys semantically. When it matches, use exactly the decision's required action and target path; do not reinterpret it, create a near-synonym URL, or omit the existing URL.
22. A keyword match is not enough for content deduplication. Compare the search intent, buyer question, promised outcome, and required sections of every SEO/blog candidate with every existing route and editorial decision. If the candidate would answer materially the same question for the same audience, it is not `new`: use refresh/expand-existing on the canonical route or omit it. A different title, format, or a few additional subtopics never creates a new intent.
23. Pinterest is a visual-search and conversion channel, never a mechanical article reposting channel. When the current context contains configured Pinterest boards and landing pages, Pinterest assignments must be concrete finished briefs with: pinType (product_proof, searchable_inspiration, how_it_works, or conversion_offer), boardKey matching one configured board, destinationUrl matching one configured landing page or a directly relevant published article, a search-led title, pinDescription, overlayText, altText, and a visualBrief. Match the Pin promise to that exact destination. Do not send every Pin to the homepage or blog. The generated Pin is a finished visual, not a text-heavy slide: visualBrief must specify either one real-world photographic scene/collage based on verified site assets, or a real verified product screenshot via interfaceReference. Never ask the image model to render an infographic, flowchart, numbered steps, comparison/pricing cards, CTA button, labels, badges, or textual UI. Use only the one approved overlay line; a genuine referenced screenshot may retain its existing native text. Do not propose Pinterest work if the account/boards are not connected; name the prerequisite instead. Pinterest draft generation is factory-now only; external publishing remains scheduled by Blog Core only after a human enables that site strategy.
24. Every social assignment is subject to the same evidence standard as site copy. Do not use or imply proven outcomes such as high-converting, boosts conversion, drives sales, lowers returns, reduces spend, improves ROAS, or any guaranteed speed/quality claim unless current internal evidence proves that exact result. Describe the supported capability and invite testing instead. A Pin may show a real product interface only when the site audit found an actual screenshot asset: then set interfaceReference to that exact relative file path and describe it as the real reference. Never invent UI controls, metrics, dashboards, badges, labels, or text inside a generated image. If no verified screenshot asset exists, choose a real-world scene instead.

Current internal context (not public evidence):
{json.dumps(prompt_context, ensure_ascii=False, default=str)}

Return only the requested JSON structure in English. Make the strategy detailed enough that an operator can execute it without interpreting generic advice.
""".strip()


def _extract_grounding(data):
    sources = []
    queries = []
    seen = set()
    for candidate in data.get("candidates") or []:
        metadata = candidate.get("groundingMetadata") or {}
        queries.extend(metadata.get("webSearchQueries") or [])
        for chunk in metadata.get("groundingChunks") or []:
            web = chunk.get("web") or {}
            url = web.get("uri") or ""
            if url and url not in seen:
                seen.add(url)
                sources.append({"url": url, "title": web.get("title") or url})
    return {"queries": list(dict.fromkeys(queries))[:80], "sources": sources[:120], "retrievedAt": _now()}


def _call_strategy_model(prompt, db_path, site_id, thinking_level="high"):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_TEXT_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key is not configured")
    primary = (os.environ.get("GEMINI_STRATEGY_MODEL") or "gemini-3.7-flash").strip()
    fallback = (os.environ.get("GEMINI_STRATEGY_FALLBACK_MODEL") or "").strip()
    models = list(dict.fromkeys([model for model in (primary, fallback) if model]))
    last_error = ""
    for model in models:
        executor = StrategyToolExecutor(db_path, site_id)
        declarations = tool_declarations() + [{
            "name": "submit_strategy",
            "description": "Submit the complete final strategy only after all required internal and external research has finished.",
            "parameters": STRATEGY_SCHEMA,
        }]
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        evidence = {"queries": [], "sources": [], "retrievedAt": _now(), "internalTools": executor.trace}
        try:
            for step in range(16):
                payload = {
                    "contents": contents,
                    "tools": [{"functionDeclarations": declarations}, {"googleSearch": {}}, {"urlContext": {}}],
                    "toolConfig": {"includeServerSideToolInvocations": True, "functionCallingConfig": {"mode": "VALIDATED"}},
                    "generationConfig": {"thinkingConfig": {"thinkingLevel": thinking_level}},
                }
                body = json.dumps(payload).encode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model, safe='.-')}:generateContent?key={urllib.parse.quote(api_key, safe='')}"
                request = urllib.request.Request(url, data=body, headers={"content-type": "application/json"}, method="POST")
                with urllib.request.urlopen(request, timeout=420) as response:
                    data = json.loads(response.read().decode("utf-8"))
                grounded = _extract_grounding(data)
                evidence["queries"] = list(dict.fromkeys(evidence["queries"] + grounded["queries"]))[:80]
                source_map = {item["url"]: item for item in evidence["sources"] + grounded["sources"]}
                evidence["sources"] = list(source_map.values())[:120]
                content = ((data.get("candidates") or [{}])[0].get("content") or {})
                parts = content.get("parts") or []
                calls = [part.get("functionCall") for part in parts if part.get("functionCall")]
                if calls:
                    contents.append(content)
                    responses = []
                    submissions = []
                    for call in calls:
                        if call.get("name") == "submit_strategy":
                            submissions.append(call)
                            continue
                        result = executor.execute(call.get("name") or "", call.get("args") or {})
                        if call.get("name") == "research_external_web" and isinstance(result, dict):
                            evidence["queries"] = list(dict.fromkeys(evidence["queries"] + (result.get("queries") or [])))[:80]
                            source_map = {item["url"]: item for item in evidence["sources"] + (result.get("sources") or []) if item.get("url")}
                            evidence["sources"] = list(source_map.values())[:120]
                        responses.append({"functionResponse": {"id": call.get("id") or "", "name": call.get("name") or "", "response": {"result": result}}})
                    evidence["internalTools"] = executor.trace
                    if submissions and not responses:
                        result = submissions[-1].get("args") or {}
                        required_tools = {"inspect_site_configuration", "inspect_content_operations", "list_factory_content", "search_factory_content", "list_site_files", "read_site_files", "inspect_site_databases", "inspect_site_runtime", "research_external_web"}
                        used_tools = {item["tool"] for item in executor.trace if item.get("ok")}
                        missing = sorted(required_tools - used_tools)
                        if missing:
                            raise RuntimeError(f"Strategy research incomplete: required internal tools not used: {', '.join(missing)}")
                        if not executor.factory_inventory_complete:
                            raise RuntimeError("Strategy research incomplete: live factory content inventory was not fully paginated")
                        if not executor.factory_search_performed:
                            raise RuntimeError("Strategy research incomplete: proposed SEO assignments were not batch-checked against the live factory")
                        if executor._database_files() and "query_site_database" not in used_tools:
                            raise RuntimeError("Strategy research incomplete: a site database was found but no aggregate product query was made")
                        if len(evidence["queries"]) < 4 or len(evidence["sources"]) < 3:
                            raise RuntimeError(f"Strategy research incomplete: external research produced {len(evidence['queries'])} queries and {len(evidence['sources'])} grounded sources; required minimum is 4 queries and 3 sources")
                        return result, evidence, model
                    for submission in submissions:
                        responses.append({"functionResponse": {"id": submission.get("id") or "", "name": "submit_strategy", "response": {"error": "Research calls and submission cannot be mixed. Finish remaining research, then call submit_strategy alone."}}})
                    contents.append({"role": "user", "parts": responses + [{"text": "Continue the same analysis. Use additional tools if needed; call submit_strategy only after completing all required research."}]})
                    continue
                raise RuntimeError("Gemini strategy returned text instead of the required submit_strategy function call")
            raise RuntimeError("Strategy tool loop exceeded 16 steps without a final answer")
        except urllib.error.HTTPError as error:
            detail = error.read(2400).decode("utf-8", errors="replace")
            last_error = f"Gemini strategy HTTP {error.code} ({model}): {detail[:2000]}"
            if error.code in {404, 503} and model != models[-1]:
                continue
            raise RuntimeError(last_error) from error
        except (TimeoutError, urllib.error.URLError) as error:
            last_error = f"Gemini strategy request failed ({model}): {error}"
            if model != models[-1]:
                continue
            raise RuntimeError(last_error) from error
    raise RuntimeError(last_error or "Strategy model did not return a response")


def _semantic_content_gate(candidates, existing_content):
    """Independently audit every proposed site/article intent against live content.

    String overlap cannot distinguish “MVP scope” from “MVP development cost”.
    This gate receives the canonical routes, titles and actual available content
    descriptions, then blocks a plan unless a second model finds a genuinely
    uncovered buyer question.
    """
    if not candidates:
        return []
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_TEXT_API_KEY")
    if not api_key:
        raise RuntimeError("Semantic content gate cannot run: Gemini API key is not configured")
    model = (os.environ.get("GEMINI_STRATEGY_MODEL") or "gemini-3.7-flash").strip()
    inventory = [
        {
            "canonicalPath": item.get("targetPath") or item.get("url") or "",
            "title": item.get("title") or "",
            "status": item.get("status") or "",
            "coverage": str(item.get("comparable") or "")[:5000],
        }
        for item in existing_content
    ]
    prompt = """You are a strict editorial-intent gate for a content factory. Compare every proposed website or blog assignment with the complete existing canonical inventory. Judge semantic intent, not word overlap: audience, buyer question, outcome, decision to be made, and article/page sections. A new title is NOT new when an existing canonical page can answer the same question after a bounded expansion. Different wording, a price/scope/cost subtopic, a checklist, examples, or a different format do not make a new intent by themselves.

Return JSON only: {\"verdicts\":[{\"planIndex\":integer,\"decision\":\"ALLOW_NEW|USE_REFRESH|USE_EXPAND_EXISTING|DUPLICATE_OR_OMIT\",\"canonicalPath\":string,\"reason\":string}]}. Every planIndex must occur exactly once. For ALLOW_NEW canonicalPath is empty. For every other decision canonicalPath must be an exact existing canonical path.

EXISTING CANONICAL INVENTORY:\n""" + json.dumps(inventory, ensure_ascii=False) + "\n\nPROPOSED ASSIGNMENTS:\n" + json.dumps(candidates, ensure_ascii=False)
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.0},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model, safe='.-')}:generateContent?key={urllib.parse.quote(api_key, safe='')}"
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError(f"Semantic content gate failed: Gemini HTTP {error.code}: {detail}") from error
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    raw = "".join(str(part.get("text") or "") for part in parts).strip()
    try:
        verdicts = json.loads(raw).get("verdicts")
    except (TypeError, json.JSONDecodeError) as error:
        raise RuntimeError("Semantic content gate returned invalid JSON") from error
    allowed_paths = {_normalized_path(item.get("targetPath") or item.get("url")) for item in existing_content}
    expected = {int(item["planIndex"]) for item in candidates}
    resolved = {}
    for verdict in verdicts if isinstance(verdicts, list) else []:
        if not isinstance(verdict, dict):
            continue
        try:
            index = int(verdict.get("planIndex"))
        except (TypeError, ValueError):
            continue
        decision = str(verdict.get("decision") or "")
        path = _normalized_path(verdict.get("canonicalPath")) if verdict.get("canonicalPath") else ""
        if index not in expected or decision not in {"ALLOW_NEW", "USE_REFRESH", "USE_EXPAND_EXISTING", "DUPLICATE_OR_OMIT"}:
            continue
        if decision != "ALLOW_NEW" and path not in allowed_paths:
            continue
        resolved[index] = {"decision": decision, "canonicalPath": path, "reason": str(verdict.get("reason") or "")[:1000]}
    if set(resolved) != expected:
        raise RuntimeError("Semantic content gate did not return one valid verdict for every proposed website/blog assignment")
    return [resolved[index] for index in sorted(resolved)]


def start_strategy_run(db_path, site_id, trigger="manual"):
    ensure_strategy_schema(db_path)
    model = (os.environ.get("GEMINI_STRATEGY_MODEL") or "gemini-3.7-flash").strip()
    with _connect(db_path) as conn:
        if not conn.execute("select id from sites where id=?", (site_id,)).fetchone():
            raise KeyError("site not found")
        running = conn.execute("select id from agent_strategy_runs where site_id=? and status='RUNNING' order by id desc limit 1", (site_id,)).fetchone()
        if running:
            return int(running["id"]), False
        run_id = conn.execute(
            "insert into agent_strategy_runs(site_id,trigger,model,status,started_at) values(?,?,?,?,?)",
            (site_id, trigger, model, "RUNNING", _now()),
        ).lastrowid
        conn.execute("update agent_strategy_profiles set status='ANALYZING',error=null,last_run_id=?,updated_at=? where site_id=?", (run_id, _now(), site_id))
    return int(run_id), True


def execute_strategy_run(db_path, run_id, site_id):
    strategy = None
    evidence = None
    try:
        with _connect(db_path) as conn:
            run = conn.execute("select trigger from agent_strategy_runs where id=?", (run_id,)).fetchone()
        thinking_level = "medium" if run and run["trigger"] == "scheduled" else "high"
        context = _site_context(db_path, site_id)
        strategy, evidence, model = _call_strategy_model(_strategy_prompt(context), db_path, site_id, thinking_level=thinking_level)
        channel_names = {str(item.get("channel") or "").strip().lower() for item in strategy.get("channelStrategy") or []}
        if len(channel_names) < 8:
            raise RuntimeError("Strategy did not evaluate enough distinct growth channels")
        media_plan = strategy.get("mediaPlan") or []
        if len(media_plan) < 12:
            raise RuntimeError("Strategy did not produce a complete 12-week media plan")
        existing_content = context.get("_existingContentIndex") or []
        website_candidates = []
        for plan_index, item in enumerate(media_plan):
            channel = str(item.get("channel") or "").lower()
            if not any(marker in channel for marker in ("seo", "blog", "website", "money page", "ship hub")):
                continue
            website_candidates.append({
                "planIndex": plan_index,
                "title": str(item.get("title") or ""),
                "requestedAction": str(item.get("contentAction") or "").lower(),
                "targetPath": str(item.get("targetPath") or ""),
                "existingContentUrl": str(item.get("existingContentUrl") or ""),
                "opportunityEvidence": str(item.get("opportunityEvidence") or ""),
                "changeBrief": str(item.get("changeBrief") or ""),
            })
        semantic_verdicts = _semantic_content_gate(website_candidates, existing_content)
        semantic_by_index = {int(candidate["planIndex"]): verdict for candidate, verdict in zip(website_candidates, semantic_verdicts)}
        # The semantic auditor is the source of truth for duplicate intent.  Reconcile
        # a candidate to its canonical route in-place instead of throwing away an
        # otherwise useful strategy because its first wording was too close to an
        # existing page.  This is deliberately generic: it applies to every topic
        # and every site, not to a list of special-case keywords.
        semantic_reconciliations = []
        semantic_omissions = set()
        for candidate in website_candidates:
            verdict = semantic_by_index[int(candidate["planIndex"])]
            requested = candidate["requestedAction"]
            decision = verdict["decision"]
            assigned_path = _normalized_path(candidate["targetPath"] or candidate["existingContentUrl"])
            expected_path = verdict["canonicalPath"]
            if decision == "ALLOW_NEW" and requested == "new":
                continue
            if decision == "DUPLICATE_OR_OMIT":
                semantic_omissions.add(int(candidate["planIndex"]))
                semantic_reconciliations.append({
                    "title": candidate["title"], "action": "omitted",
                    "reason": verdict["reason"],
                })
                continue
            if decision in {"USE_REFRESH", "USE_EXPAND_EXISTING"}:
                item = media_plan[int(candidate["planIndex"])]
                action = "refresh" if decision == "USE_REFRESH" else "expand-existing"
                item["contentAction"] = action
                item["targetPath"] = expected_path
                item["existingContentUrl"] = expected_path
                item["refreshEvidence"] = verdict["reason"]
                item["changeBrief"] = (
                    f"Use the canonical page {expected_path}; extend its existing coverage to include "
                    f"the proposed scope, without creating a competing URL."
                )
                semantic_reconciliations.append({
                    "title": candidate["title"], "action": action,
                    "canonicalPath": expected_path, "reason": verdict["reason"],
                })
                continue
            # An existing-page assignment marked ALLOW_NEW is internally
            # inconsistent.  Omit it rather than silently creating a second route.
            semantic_omissions.add(int(candidate["planIndex"]))
            semantic_reconciliations.append({
                "title": candidate["title"], "action": "omitted",
                "reason": "Semantic gate found no canonical basis for the requested existing-page action.",
            })
        evidence.setdefault("semanticIntentAudit", semantic_verdicts)
        if semantic_reconciliations:
            evidence.setdefault("semanticReconciliations", []).extend(semantic_reconciliations)
        filtered_media_plan = []
        removed_unactionable = []
        for plan_index, item in enumerate(media_plan):
            if plan_index in semantic_omissions:
                removed_unactionable.append({"title": item.get("title"), "reason": "semantic duplicate or invalid canonical action"})
                continue
            action = str(item.get("contentAction") or "").strip().lower()
            if action == "already-planned":
                removed_unactionable.append({"title": item.get("title"), "reason": "already present in the factory queue"})
                continue
            if action in {"refresh", "expand-existing"} and (
                not str(item.get("refreshEvidence") or "").strip()
                or not str(item.get("changeBrief") or "").strip()
            ):
                removed_unactionable.append({"title": item.get("title"), "reason": "refresh lacked evidence or a bounded change brief"})
                continue
            filtered_media_plan.append(item)
        if removed_unactionable:
            evidence.setdefault("planCorrections", []).extend(removed_unactionable)
        media_plan = filtered_media_plan
        strategy["mediaPlan"] = media_plan
        if len(media_plan) < 12:
            raise RuntimeError("Strategy became incomplete after removing queued or unsupported refresh assignments")
        incomplete_storyboards = []
        for item in media_plan:
            channel = str(item.get("channel") or "").lower()
            format_name = str(item.get("format") or "").lower()
            if not ({"instagram", "tiktok"} & set(channel.replace("/", " ").split())):
                continue
            if "carousel" not in format_name and "slides" not in format_name:
                continue
            storyboard = item.get("storyboard") or []
            slide_count = int(item.get("slideCount") or 0)
            valid_order = [slide.get("slide") for slide in storyboard if isinstance(slide, dict)] == list(range(1, slide_count + 1))
            valid_content = all(
                isinstance(slide, dict)
                and str(slide.get("role") or "").strip()
                and str(slide.get("onScreenText") or "").strip()
                and str(slide.get("visualDirection") or "").strip()
                for slide in storyboard
            )
            if slide_count < 2 or len(storyboard) != slide_count or not valid_order or not valid_content:
                incomplete_storyboards.append(str(item.get("title") or "Untitled assignment"))
        if incomplete_storyboards:
            raise RuntimeError(f"Strategy contains incomplete social storyboards: {', '.join(incomplete_storyboards[:8])}")
        cadences = (context.get("autopublish") or {}).get("cadences") or {}
        shared_carousels_required = bool(
            isinstance(cadences.get("instagram"), dict)
            and cadences["instagram"].get("enabled")
            and isinstance(cadences.get("tiktok_carousel"), dict)
            and cadences["tiktok_carousel"].get("enabled")
        )
        invalid_shared_carousels = []
        if shared_carousels_required:
            for item in media_plan:
                channel_name = str(item.get("channel") or "").lower()
                format_name = str(item.get("format") or "").lower()
                if "carousel" not in format_name and "slides" not in format_name:
                    continue
                has_instagram = "instagram" in channel_name
                has_tiktok = "tiktok" in channel_name
                if has_instagram != has_tiktok:
                    invalid_shared_carousels.append(f"{item.get('title')}: must target Instagram + TikTok together")
                    continue
                if has_instagram and has_tiktok:
                    generator = str(item.get("generator") or "").lower()
                    if not str(item.get("repurposeGroup") or "").strip() or not any(marker in generator for marker in ("reuse", "same", "once", "unchanged")):
                        invalid_shared_carousels.append(f"{item.get('title')}: missing render-once/reuse-unchanged contract")
        if invalid_shared_carousels:
            raise RuntimeError(f"Strategy splits shared Instagram/TikTok carousels: {'; '.join(invalid_shared_carousels[:8])}")
        editorial_decisions = context.get("editorialDecisions") or []
        invalid_content_assignments = []
        for item in media_plan:
            channel = str(item.get("channel") or "").lower()
            if not any(marker in channel for marker in ("seo", "blog", "website", "money page", "ship hub")):
                continue
            title = str(item.get("title") or "").strip()
            action = str(item.get("contentAction") or "").strip().lower()
            target_path = str(item.get("targetPath") or "").strip()
            existing_url = str(item.get("existingContentUrl") or "").strip()
            candidate_intent = " ".join((
                title,
                target_path,
                str(item.get("opportunityEvidence") or ""),
                str(item.get("changeBrief") or ""),
            ))
            for decision in editorial_decisions:
                if not isinstance(decision, dict) or not _matches_editorial_intent(candidate_intent, str(decision.get("intent_key") or "")):
                    continue
                required_action = str(decision.get("required_action") or "").strip().lower()
                required_path = _normalized_path(decision.get("target_path"))
                actual_path = _normalized_path(target_path or existing_url)
                if action != required_action or actual_path != required_path:
                    invalid_content_assignments.append(
                        f"{title}: violates editorial decision '{decision.get('intent_key')}' — {decision.get('rationale')}"
                    )
                break
            exact_existing = next((
                entry for entry in existing_content
                if target_path and _normalized_path(entry.get("targetPath") or entry.get("url")) == _normalized_path(target_path)
            ), None)
            if action not in {"new", "refresh", "expand-existing"}:
                invalid_content_assignments.append(f"{title}: missing contentAction")
                continue
            if action in {"refresh", "expand-existing"}:
                referenced_existing = exact_existing or next((
                    entry for entry in existing_content
                    if existing_url and _normalized_path(entry.get("targetPath") or entry.get("url")) == _normalized_path(existing_url)
                ), None)
                if not referenced_existing:
                    invalid_content_assignments.append(f"{title}: existing factory item was not identified")
                    continue
            if action == "new" and not str(item.get("opportunityEvidence") or "").strip():
                invalid_content_assignments.append(f"{title}: new assignment has no uncovered-intent evidence")
                continue
            if action in {"refresh", "expand-existing"} and (
                not str(item.get("refreshEvidence") or "").strip()
                or not str(item.get("changeBrief") or "").strip()
            ):
                invalid_content_assignments.append(f"{title}: refresh/expansion has no concrete evidence and bounded change brief")
                continue
            is_money_page = any(marker in channel for marker in ("money page", "catalogue", "ship hub"))
            if is_money_page and (not target_path or not str(item.get("templateEvidence") or "").strip()):
                invalid_content_assignments.append(f"{title}: missing verified targetPath/templateEvidence")
        if invalid_content_assignments:
            raise RuntimeError(f"Strategy contains invalid or duplicate factory assignments: {'; '.join(invalid_content_assignments[:8])}")
        # A high SEO score never authorizes inventing a new URL.  If the semantic
        # audit finds every candidate already covered, the correct strategy may
        # be to expand existing work or concentrate on other channels.
        new_editorial = [
            item for item in media_plan
            if str(item.get("contentAction") or "").lower() == "new"
            and any(marker in str(item.get("channel") or "").lower() for marker in ("seo", "blog", "editorial", "website", "money page"))
        ]
        duplicate_new_assignments = []
        for index, left in enumerate(new_editorial):
            for right in new_editorial[index + 1:]:
                same_path = _normalized_path(left.get("targetPath")) == _normalized_path(right.get("targetPath"))
                similarity = _topic_similarity(str(left.get("title") or ""), str(right.get("title") or ""))
                if same_path or similarity >= 0.68:
                    duplicate_new_assignments.append(f"{left.get('title')} <> {right.get('title')}")
        if duplicate_new_assignments:
            raise RuntimeError(f"Strategy contains mutually cannibalizing new assignments: {'; '.join(duplicate_new_assignments[:6])}")
        existing_social = context.get("_existingSocialIndex") or []
        social_duplicate_assignments = []
        for item in media_plan:
            channel_name = str(item.get("channel") or "").lower()
            channels = [name for name in ("instagram", "tiktok", "pinterest", "threads", "twitter", "youtube") if name in channel_name]
            if not channels:
                continue
            for channel in channels:
                same_channel = [entry for entry in existing_social if str(entry.get("channel") or "").lower() == channel]
                match = _find_existing_topic(str(item.get("title") or ""), same_channel) if same_channel else None
                if match:
                    social_duplicate_assignments.append(f"{channel}: {item.get('title')} duplicates {match.get('title')} ({match.get('status')})")
        if social_duplicate_assignments:
            raise RuntimeError(f"Strategy contains duplicate same-channel social assignments: {'; '.join(social_duplicate_assignments[:8])}")
        pinterest_config = context.get("pinterestStrategy") or {}
        configured_boards = {str(item.get("key") or "") for item in (pinterest_config.get("boards") or []) if isinstance(item, dict)}
        configured_urls = {str(item.get("url") or "") for item in (pinterest_config.get("landingPages") or []) if isinstance(item, dict)}
        invalid_pins = []
        invalid_pin_indexes = set()
        for item_index, item in enumerate(media_plan):
            if "pinterest" not in str(item.get("channel") or "").lower():
                continue
            fields = ("pinType", "boardKey", "destinationUrl", "overlayText", "pinDescription", "altText", "visualBrief")
            missing = [field for field in fields if not str(item.get(field) or "").strip()]
            if missing:
                invalid_pins.append(f"{item.get('title')}: missing {', '.join(missing)}")
                invalid_pin_indexes.add(item_index)
                continue
            if configured_boards and str(item.get("boardKey") or "") not in configured_boards:
                invalid_pins.append(f"{item.get('title')}: boardKey is not mapped")
                invalid_pin_indexes.add(item_index)
            destination = str(item.get("destinationUrl") or "")
            if configured_urls and destination not in configured_urls and not destination.startswith(("http://", "https://")):
                invalid_pins.append(f"{item.get('title')}: invalid destinationUrl")
                invalid_pin_indexes.add(item_index)
            visual_brief = str(item.get("visualBrief") or "")
            if re.search(r"\b(?:interface|dashboard|ui|screen(?:shot)?|mockup)\b", visual_brief, re.I) and not str(item.get("interfaceReference") or "").strip():
                invalid_pins.append(f"{item.get('title')}: interface visual is missing interfaceReference")
                invalid_pin_indexes.add(item_index)
            if re.search(r"\b(?:infographic|flowchart|pricing\s+(?:card|tier|comparison)|\d+\s*(?:step|panel|quadrant)|clear\s+numbering|cta\s+button)\b", visual_brief, re.I):
                invalid_pins.append(f"{item.get('title')}: visualBrief asks for generated information graphics")
                invalid_pin_indexes.add(item_index)
        if invalid_pins:
            # A malformed social suggestion must never block a complete site
            # strategy or slip into the publishing queue. Keep only the
            # independently valid work and retain the rejection in the audit.
            media_plan = [item for item_index, item in enumerate(media_plan) if item_index not in invalid_pin_indexes]
            strategy["mediaPlan"] = media_plan
            evidence.setdefault("rejectedAssignments", []).extend({"channel": "pinterest", "reason": reason} for reason in invalid_pins)
        strategy_text = json.dumps(strategy, ensure_ascii=False)
        assurance_pattern = re.compile(
            r"\bverified\s+((?:[a-z-]+\s+){0,2}(?:profiles?|users?|travelers?|listings?|sailings?|itineraries?|catalog(?:ue)?s?|inventory|data|results?|transactions?|answers?|support))\b",
            flags=re.I,
        )
        unsupported_assurances = [match.group(0) for match in assurance_pattern.finditer(strategy_text)]
        if unsupported_assurances:
            strategy_text = assurance_pattern.sub(lambda match: match.group(1), strategy_text)
            strategy = json.loads(strategy_text)
            media_plan = strategy.get("mediaPlan") or []
            evidence.setdefault("claimCorrections", []).extend({"removedUnsupportedAssurance": claim} for claim in dict.fromkeys(unsupported_assurances))
        unsupported_outcomes = re.findall(r"\bsav(?:e|ed|ing)\s+\$[\d,.]+\+?", strategy_text, flags=re.I)
        if unsupported_outcomes:
            claims = list(dict.fromkeys(unsupported_outcomes))[:8]
            raise RuntimeError(f"Strategy contains unsupported achieved outcome claims: {', '.join(claims)}")
        finished = _now()
        next_review = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(timespec="seconds")
        with _connect(db_path) as conn:
            profile = conn.execute("select strategy_version from agent_strategy_profiles where site_id=?", (site_id,)).fetchone()
            version = int(profile["strategy_version"] or 0) + 1
            conn.execute(
                """update agent_strategy_profiles set status='ACTIVE',strategy_model=?,strategy_version=?,strategy_json=?,evidence_json=?,last_run_id=?,last_analyzed_at=?,next_review_at=?,error=null,updated_at=? where site_id=?""",
                (model, version, json.dumps(strategy, ensure_ascii=False), json.dumps(evidence, ensure_ascii=False), run_id, finished, next_review, finished, site_id),
            )
            conn.execute("update agent_strategy_runs set status='COMPLETED',finished_at=?,evidence_json=?,result_json=? where id=?", (finished, json.dumps(evidence, ensure_ascii=False), json.dumps(strategy, ensure_ascii=False), run_id))
            conn.execute("delete from agent_media_plan_items where site_id=? and status in ('PROPOSED','PROPOSED_NEW')", (site_id,))
            for item in media_plan:
                content_action = str(item.get("contentAction") or "").strip().lower()
                plan_status = {
                    "new": "PROPOSED_NEW",
                    "refresh": "REFRESH_EXISTING",
                    "expand-existing": "EXPAND_EXISTING",
                }.get(content_action, "PROPOSED")
                item_details = {
                    "contentAction": content_action or None,
                    "targetPath": item.get("targetPath"),
                    "existingContentUrl": item.get("existingContentUrl"),
                    "templateEvidence": item.get("templateEvidence"),
                    "refreshEvidence": item.get("refreshEvidence"),
                    "changeBrief": item.get("changeBrief"),
                    "opportunityEvidence": item.get("opportunityEvidence"),
                    "slideCount": item.get("slideCount"),
                    "storyboard": item.get("storyboard") or [],
                    "pinType": item.get("pinType"),
                    "boardKey": item.get("boardKey"),
                    "destinationUrl": item.get("destinationUrl"),
                    "visualBrief": item.get("visualBrief"),
                    "interfaceReference": item.get("interfaceReference"),
                    "overlayText": item.get("overlayText"),
                    "pinDescription": item.get("pinDescription"),
                    "altText": item.get("altText"),
                }
                conn.execute(
                    """insert into agent_media_plan_items(site_id,strategy_version,week,channel,format,title,objective,funnel_stage,cta,generator,kpi,execution_mode,repurpose_group,rationale,status,details_json,created_at,updated_at)
                       values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (site_id, version, max(1, min(12, int(item.get("week") or 1))), str(item.get("channel") or "website")[:80], str(item.get("format") or "content")[:120], str(item.get("title") or "Untitled assignment")[:300], str(item.get("objective") or "")[:500], str(item.get("funnelStage") or "")[:80], str(item.get("cta") or "")[:400], str(item.get("generator") or "")[:160], str(item.get("kpi") or "")[:300], str(item.get("executionMode") or "manual")[:80], str(item.get("repurposeGroup") or "")[:120], str(item.get("rationale") or "")[:1000], plan_status, json.dumps(item_details, ensure_ascii=False), finished, finished),
                )
        return {"ok": True, "runId": run_id, "version": version, "model": model, "items": len(media_plan)}
    except Exception as error:
        failed = _now()
        retry_at = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(timespec="seconds")
        with _connect(db_path) as conn:
            conn.execute(
                "update agent_strategy_runs set status='ERROR',finished_at=?,error=?,evidence_json=?,result_json=? where id=?",
                (failed, str(error)[:4000], json.dumps(evidence or {}, ensure_ascii=False), json.dumps(strategy or {}, ensure_ascii=False), run_id),
            )
            error_text = str(error)[:4000]
            if "prepayment credits are depleted" in error_text.lower() or "RESOURCE_EXHAUSTED" in error_text:
                conn.execute("update agent_strategy_profiles set status='BLOCKED_QUOTA',error=?,next_review_at=?,updated_at=? where priority=1", (error_text, retry_at, failed))
            else:
                conn.execute("update agent_strategy_profiles set status='ERROR',error=?,next_review_at=?,updated_at=? where site_id=?", (error_text, retry_at, failed, site_id))
        return {"ok": False, "runId": run_id, "error": str(error)}


def get_strategy_snapshot(db_path, site_id):
    ensure_strategy_schema(db_path)
    with _connect(db_path) as conn:
        site = conn.execute("select id,domain,homepage_url,brand_name from sites where id=?", (site_id,)).fetchone()
        if not site:
            raise KeyError("site not found")
        profile = conn.execute("select * from agent_strategy_profiles where site_id=?", (site_id,)).fetchone()
        run = conn.execute("select id,status,model,trigger,started_at,finished_at,error from agent_strategy_runs where site_id=? order by id desc limit 1", (site_id,)).fetchone()
        items = conn.execute("select * from agent_media_plan_items where site_id=? and strategy_version=? order by week,id", (site_id, int(profile["strategy_version"] or 0))).fetchall()
    return {
        "site": dict(site), "profile": dict(profile), "run": dict(run) if run else None,
        "strategy": _safe_json(profile["strategy_json"], {}),
        "evidence": _safe_json(profile["evidence_json"], {}),
        "mediaPlan": [dict(item) for item in items],
    }


def next_due_strategy_site(db_path):
    ensure_strategy_schema(db_path)
    now = _now()
    with _connect(db_path) as conn:
        return conn.execute(
            """select p.site_id from agent_strategy_profiles p join sites s on s.id=p.site_id
               where p.status!='ANALYZING' and (p.priority=1 or p.last_analyzed_at is not null)
                 and coalesce(p.next_review_at,p.last_analyzed_at,'')<=?
               order by p.priority desc, coalesce(p.last_analyzed_at,'') asc, s.domain asc limit 1""",
            (now,),
        ).fetchone()
