#!/usr/bin/env python3
"""Site-scoped, evidence-first content-engine primitives.

This module deliberately has no knowledge of a site's domain.  A site profile
is data: its contract URL and primary-source registry are supplied by callers.
It never publishes, generates media, or uses search/social discovery as proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "BlogCoreContentEngine/1.0 (+https://blog.yas.ooo; evidence-change-monitor)"
ALLOWED_ADAPTERS = {"official_api", "rss_atom", "xml_sitemap", "html_change_monitor", "manual_primary_document"}
HIGH_RISK = {"tax", "law", "immigration", "medical", "health", "safety", "live", "price", "schedule", "commercial"}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stable_id(prefix, *parts):
    payload = "\x1f".join(str(value or "").strip() for value in parts)
    return f"{prefix}_{hashlib.sha256(payload.encode()).hexdigest()[:20]}"


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def parse_json(value, fallback):
    try:
        return json.loads(value) if value else fallback
    except (ValueError, TypeError):
        return fallback


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip = max(0, self.skip - 1)
        if tag == "title":
            self._in_title = False
        if tag in {"p", "li", "h1", "h2", "h3", "br", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
            if self._in_title:
                self.title += data


def html_text(raw):
    parser = _TextParser()
    parser.feed(raw.decode("utf-8", "replace"))
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(parser.parts))
    text = re.sub(r"\n\s*\n+", "\n", text)
    # Preserve block boundaries as sentence boundaries. Collapsing every
    # newline to whitespace joined headings/buttons to the following paragraph
    # and produced source-attributed but non-atomic pseudo-claims.
    blocks = [re.sub(r"\s+", " ", block).strip(" .") for block in text.splitlines()]
    normalized = ". ".join(block for block in blocks if block)
    return normalized.strip(), re.sub(r"\s+", " ", parser.title).strip()


def ensure_schema(conn):
    conn.executescript("""
    create table if not exists content_engine_contracts (
      id integer primary key autoincrement, site_id integer not null, contract_url text not null,
      contract_version text not null, schema_version integer, payload_json text not null,
      payload_hash text not null, fetched_at text not null, active integer not null default 1,
      unique(site_id, contract_version), unique(site_id, payload_hash)
    );
    create table if not exists knowledge_sources (
      id text primary key, site_id integer not null, owner text not null, url text not null,
      source_class text not null, knowledge_families_json text not null default '[]',
      retrieval_adapter text not null, poll_cadence_hours integer not null default 168,
      robots_terms_state text not null default 'unknown', media_rights_policy text not null default 'citation_only',
      etag text, last_modified text, body_hash text, last_success_at text, last_error_at text,
      last_error text, last_changed_at text, active integer not null default 1,
      priority integer not null default 50, config_json text not null default '{}', created_at text not null, updated_at text not null,
      unique(site_id, url)
    );
    create table if not exists knowledge_documents (
      id text primary key, site_id integer not null, source_id text not null, url text not null,
      body_hash text not null, content_type text, fetched_at text not null, changed_at text not null,
      etag text, last_modified text, title text, text_content text not null, status text not null,
      unique(site_id, url, body_hash)
    );
    create table if not exists knowledge_entities (
      id text primary key, site_id integer not null, entity_type text not null, canonical_name text not null,
      aliases_json text not null default '[]', localized_names_json text not null default '{}',
      coordinates_json text, administrative_area text, parent_entity_id text, related_entity_ids_json text not null default '[]',
      first_verified_at text not null, last_verified_at text not null, status text not null default 'VERIFIED',
      unique(site_id, entity_type, canonical_name)
    );
    create table if not exists knowledge_claims (
      id text primary key, site_id integer not null, entity_id text not null, source_id text not null,
      document_id text not null, source_url text not null, claim_text text not null, claim_fingerprint text not null,
      supporting_excerpt text not null, excerpt_start integer, excerpt_end integer, checked_at text not null,
      valid_from text, valid_until text, precision_text text, confidence real not null,
      freshness_class text not null, risk_class text not null, visual_rights_state text not null,
      locales_approved_json text not null default '[]', effective_date_or_year text, scope_text text,
      conditions_text text, exceptions_text text, legal_citation text, reviewer text,
      status text not null default 'VERIFIED', version integer not null default 1, supersedes_claim_id text,
      created_at text not null, updated_at text not null,
      unique(site_id, source_id, claim_fingerprint, version)
    );
    create index if not exists knowledge_claims_site_freshness_idx on knowledge_claims(site_id, freshness_class, valid_until, status);
    create table if not exists knowledge_edges (
      id text primary key, site_id integer not null, source_entity_id text not null, target_entity_id text not null,
      relationship_type text not null, supporting_claim_ids_json text not null, verification_state text not null,
      confidence real not null, created_at text not null, updated_at text not null,
      unique(site_id, source_entity_id, target_entity_id, relationship_type)
    );
    create table if not exists content_candidates (
      id text primary key, site_id integer not null, entity_id text not null, claim_id text not null,
      relationship_id text, native_angle text not null, audience_state text not null, native_format text not null,
      locale text not null, hook_family text, proposed_payoff text not null, visual_mechanism text,
      score real not null, score_breakdown_json text not null, novelty_fingerprint text not null,
      workflow_state text not null, rejection_reason text, created_at text not null, updated_at text not null,
      unique(site_id, novelty_fingerprint)
    );
    create table if not exists content_briefs (
      id text primary key, site_id integer not null, candidate_id text not null unique, factual_spine_json text not null,
      prohibited_overclaims_json text not null, hook_json text not null, channel text not null, format text not null,
      locale text not null, cta_intent text, script_json text, media_rights_plan_json text not null,
      canonical_decision_json text not null, expires_at text, review_requirements_json text not null,
      workflow_state text not null, created_at text not null, updated_at text not null
    );
    create table if not exists content_packages (
      id text primary key, site_id integer not null, brief_id text not null, candidate_id text not null,
      channel text not null, locale text not null, format text not null, copy_json text not null default '{}',
      asset_manifest_json text not null default '[]', source_disclosure text, commercial_disclosure text,
      alt_text text, destination_url text, scheduled_for text, validation_report_json text not null default '{}',
      approval_state text not null default 'AWAITING_APPROVAL', remote_publication_id text, metrics_json text not null default '{}',
      package_fingerprint text not null, created_at text not null, updated_at text not null, unique(site_id, package_fingerprint)
    );
    create table if not exists content_performance (
      id integer primary key autoincrement, site_id integer not null, package_id text not null, observed_at text not null,
      observation_window text not null, reach integer, completion_rate real, shares integer, saves integer,
      meaningful_comments integer, clicks integer, downstream_tool_starts integer, fingerprint_json text not null,
      unique(package_id, observation_window)
    );
    create table if not exists content_engine_runs (
      id text primary key, site_id integer not null, run_type text not null, trigger text not null,
      contract_version text, status text not null, counters_json text not null default '{}', error_text text,
      started_at text not null, finished_at text
    );
    """)


def fetch_contract(conn, site_id, contract_url, timeout=30):
    req = urllib.request.Request(contract_url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    version = str(payload.get("contractVersion") or "unversioned")
    raw = json_text(payload)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    conn.execute("update content_engine_contracts set active=0 where site_id=?", (site_id,))
    conn.execute("""insert into content_engine_contracts(site_id,contract_url,contract_version,schema_version,payload_json,payload_hash,fetched_at,active)
                    values(?,?,?,?,?,?,?,1) on conflict(site_id,contract_version) do update set payload_json=excluded.payload_json,payload_hash=excluded.payload_hash,fetched_at=excluded.fetched_at,active=1""",
                 (site_id, contract_url, version, payload.get("schemaVersion"), raw, digest, now_iso()))
    return payload


def active_contract(conn, site_id):
    row = conn.execute("select * from content_engine_contracts where site_id=? and active=1 order by id desc limit 1", (site_id,)).fetchone()
    if not row:
        raise ValueError("No active content-engine contract; load the site contract first")
    return parse_json(row["payload_json"], {}), row["contract_version"]


def register_sources(conn, site_id, sources):
    created = 0
    for source in sources:
        adapter = source["retrievalAdapter"]
        if adapter not in ALLOWED_ADAPTERS:
            raise ValueError(f"Unsupported source adapter: {adapter}")
        source_id = stable_id("src", site_id, source["url"])
        now = now_iso()
        before = conn.execute("select id from knowledge_sources where site_id=? and url=?", (site_id, source["url"])).fetchone()
        conn.execute("""insert into knowledge_sources(id,site_id,owner,url,source_class,knowledge_families_json,retrieval_adapter,poll_cadence_hours,
                        robots_terms_state,media_rights_policy,active,priority,config_json,created_at,updated_at)
                    values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) on conflict(site_id,url) do update set owner=excluded.owner,source_class=excluded.source_class,
                        knowledge_families_json=excluded.knowledge_families_json,retrieval_adapter=excluded.retrieval_adapter,poll_cadence_hours=excluded.poll_cadence_hours,
                        robots_terms_state=excluded.robots_terms_state,media_rights_policy=excluded.media_rights_policy,active=excluded.active,priority=excluded.priority,
                        config_json=excluded.config_json,updated_at=excluded.updated_at""",
                     (source_id, site_id, source["owner"], source["url"], source.get("sourceClass", "official_government_or_municipality"),
                      json_text(source.get("knowledgeFamilies", [])), adapter, int(source.get("pollCadenceHours", 168)),
                      source.get("robotsTermsState", "respect_robots_and_terms"), source.get("mediaRightsPolicy", "citation_only"),
                      int(source.get("active", True)), int(source.get("priority", 50)), json_text(source.get("config", {})), now, now))
        created += not bool(before)
    return created


def _fetch(url, headers=None, timeout=25, max_retries=3):
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json, application/xml, text/xml, text/html;q=0.9, */*;q=0.1"}
    request_headers.update(headers or {})
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, headers=request_headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status, dict(response.headers.items()), response.read()
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt >= max_retries:
                raise
            retry_after = str(error.headers.get("Retry-After") or "").strip()
            delay = float(retry_after) if retry_after.replace(".", "", 1).isdigit() else min(8.0, 1.5 * (2 ** attempt))
            time.sleep(max(0.25, min(delay, 20.0)))


def _sitemap_urls(raw, base_url, limit):
    root = ET.fromstring(raw)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text.strip() for node in root.findall(".//sm:url/sm:loc", ns) if node.text]
    if not urls:
        urls = [node.text.strip() for node in root.findall(".//{*}url/{*}loc") if node.text]
    if urls:
        return urls[:limit]
    children = [node.text.strip() for node in root.findall(".//sm:sitemap/sm:loc", ns) if node.text]
    if not children:
        children = [node.text.strip() for node in root.findall(".//{*}sitemap/{*}loc") if node.text]
    output = []
    for child in children[:8]:
        try:
            _, _, body = _fetch(urllib.parse.urljoin(base_url, child))
            output.extend(_sitemap_urls(body, child, limit - len(output)))
        except Exception:
            continue
        if len(output) >= limit:
            break
    return output[:limit]


def _source_documents(source):
    config = parse_json(source["config_json"], {})
    adapter = source["retrieval_adapter"]
    if adapter == "manual_primary_document":
        text = str(config.get("text") or "").strip()
        return [(source["url"], text.encode(), {"Content-Type": "text/plain"})] if text else []
    conditional = {}
    if source["etag"]:
        conditional["If-None-Match"] = source["etag"]
    if source["last_modified"]:
        conditional["If-Modified-Since"] = source["last_modified"]
    try:
        _, headers, body = _fetch(source["url"], conditional)
    except urllib.error.HTTPError as error:
        if error.code == 304:
            return []
        raise
    if adapter == "xml_sitemap":
        page_limit = int(config.get("pageLimit", 25))
        scan_limit = max(page_limit, int(config.get("scanLimit", page_limit * 4)))
        urls = _sitemap_urls(body, source["url"], scan_limit)
        includes = [str(item) for item in (config.get("pathIncludes") or []) if str(item)]
        excludes = [str(item) for item in (config.get("pathExcludes") or []) if str(item)]
        min_segments = int(config.get("minPathSegments", 0))
        filtered = []
        for url in urls:
            path = urllib.parse.urlsplit(url).path
            if includes and not any(token in path for token in includes):
                continue
            if excludes and any(token in path for token in excludes):
                continue
            if len([part for part in path.split("/") if part]) < min_segments:
                continue
            filtered.append(url)
        start_offset = max(0, int(config.get("startOffset", 0)))
        selected = filtered[start_offset:start_offset + page_limit]
        docs = []
        delay = max(0.0, min(float(config.get("pageDelaySeconds", 0.35)), 5.0))
        failures = []
        for url in selected:
            try:
                _, page_headers, page_body = _fetch(url, max_retries=int(config.get("maxRetries", 3)))
                docs.append((url, page_body, page_headers))
            except Exception as error:
                failures.append(f"{url}: {error}")
            if delay:
                time.sleep(delay)
        if not docs and failures:
            raise RuntimeError("Sitemap page retrieval failed: " + "; ".join(failures[:3]))
        return docs
    if adapter == "rss_atom":
        root = ET.fromstring(body)
        entries = root.findall(".//{*}entry") + root.findall(".//{*}item")
        docs = []
        for entry in entries[: int(config.get("entryLimit", 25))]:
            title = " ".join(entry.findtext(tag, "") for tag in ("{*}title", "title")).strip()
            description = " ".join(entry.findtext(tag, "") for tag in ("{*}description", "{*}summary", "description", "summary")).strip()
            link = entry.findtext("{*}link") or source["url"]
            docs.append((link, f"{title}. {description}".encode(), {"Content-Type": "text/plain"}))
        return docs
    return [(source["url"], body, headers)]


def _freshness(text):
    lower = text.lower()
    if any(word in lower for word in ("price", "schedule", "opening", "closed", "availability", "alert", "weather", "preço", "taxa", "horário", "reabertura", "aberto", "encerrado", "alerta", "meteorologia")):
        return "volatile"
    if any(word in lower for word in ("2026", "2025", "tax", "rate", "calendar", "annual")):
        return "annual"
    return "durable"


def _risk(text):
    lower = text.lower()
    return next((risk for risk in HIGH_RISK if risk in lower), "low")


def _sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    rejected = ("cookie", "cookies", "privacy", "aceitar", "consent", "javascript", "skip to", "search this", "all rights reserved", "remove from wishlist", "add to wishlist", "search for")
    output = []
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])", text):
        sentence = sentence.strip(" -•\t")
        lower = sentence.casefold()
        if not 55 <= len(sentence) <= 550 or any(token in lower for token in rejected) or re.match(r"^(?:en|de|es|fr|pt)\s+(?:en|de|es|fr|pt)\b", lower):
            continue
        # A fact proposal needs a predicate or a numeric/date assertion; navigation labels and headings are not evidence.
        has_predicate = bool(re.search(r"\b(is|are|was|were|has|have|will|can|é|são|foi|tem|será|encontra-se|participaram|apresenta|fica)\b|\d", lower))
        if has_predicate:
            output.append(sentence)
    return output


def _entity_name(title, sentence, fallback):
    candidate = re.split(r"\s+[|–-]\s+", title or "")[0].strip()
    if 3 <= len(candidate) <= 120 and not re.fullmatch(r"(home|welcome|news|contacts?)", candidate, re.I):
        return candidate
    names = re.findall(r"\b[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'-]+(?:\s+[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'-]+){0,4}", sentence)
    return names[0] if names else fallback


def _upsert_entity(conn, site_id, name, checked_at, entity_type="place"):
    row = conn.execute("select id from knowledge_entities where site_id=? and entity_type=? and canonical_name=?", (site_id, entity_type, name)).fetchone()
    if row:
        conn.execute("update knowledge_entities set last_verified_at=? where id=?", (checked_at, row["id"]))
        return row["id"]
    entity_id = stable_id("ent", site_id, entity_type, name.casefold())
    conn.execute("""insert into knowledge_entities(id,site_id,entity_type,canonical_name,first_verified_at,last_verified_at)
                    values(?,?,?,?,?,?)""", (entity_id, site_id, entity_type, name, checked_at, checked_at))
    return entity_id


def _extract_document(conn, source, url, raw, headers, contract):
    digest = hashlib.sha256(raw).hexdigest()
    existing = conn.execute("select id from knowledge_documents where site_id=? and url=? and body_hash=?", (source["site_id"], url, digest)).fetchone()
    if existing:
        return {"unchanged": 1, "claims": 0, "entities": 0, "edges": 0}
    content_type = headers.get("Content-Type", "")
    text, title = html_text(raw) if "html" in content_type or raw.lstrip().startswith(b"<") else (raw.decode("utf-8", "replace"), "")
    checked = now_iso()
    document_id = stable_id("doc", source["site_id"], url, digest)
    conn.execute("""insert into knowledge_documents(id,site_id,source_id,url,body_hash,content_type,fetched_at,changed_at,etag,last_modified,title,text_content,status)
                    values(?,?,?,?,?,?,?,?,?,?,?,?,?)""", (document_id, source["site_id"], source["id"], url, digest, content_type, checked, checked,
                    headers.get("ETag"), headers.get("Last-Modified"), title[:300], text[:200000], "EXTRACTED"))
    locales = contract.get("project", {}).get("locales", ["en"])
    count = {"unchanged": 0, "claims": 0, "entities": 0, "edges": 0}
    source_class = source["source_class"]
    confidence = 0.96 if source_class in {"law_or_regulator", "official_government_or_municipality"} else 0.88
    for sentence in _sentences(text)[:80]:
        # The sentence itself is the atomic claim proposal; it remains private-auditable.
        name = _entity_name(title, sentence, source["owner"])
        entity_id = _upsert_entity(conn, source["site_id"], name, checked)
        # Keep a stable lineage when a source updates a numeric/date value, while exact
        # unchanged evidence remains one claim rather than a duplicate per document.
        identity = re.sub(r"\d+", "#", sentence.casefold())
        fingerprint = hashlib.sha256(re.sub(r"\W+", "", identity).encode()).hexdigest()
        previous = conn.execute("""select * from knowledge_claims where site_id=? and source_id=? and claim_fingerprint=?
                                  order by version desc limit 1""", (source["site_id"], source["id"], fingerprint)).fetchone()
        if previous and previous["claim_text"] == sentence:
            continue
        freshness = _freshness(sentence)
        valid_until = None
        if freshness == "volatile":
            valid_until = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(timespec="seconds")
        elif freshness == "annual":
            valid_until = (datetime.now(timezone.utc) + timedelta(days=366)).isoformat(timespec="seconds")
        risk = _risk(sentence)
        claim_id = stable_id("clm", source["site_id"], source["id"], fingerprint, document_id)
        version = int(previous["version"] + 1) if previous else 1
        conn.execute("""insert into knowledge_claims(id,site_id,entity_id,source_id,document_id,source_url,claim_text,claim_fingerprint,supporting_excerpt,
            excerpt_start,excerpt_end,checked_at,valid_until,precision_text,confidence,freshness_class,risk_class,visual_rights_state,locales_approved_json,
            effective_date_or_year,scope_text,conditions_text,exceptions_text,legal_citation,reviewer,status,version,supersedes_claim_id,created_at,updated_at)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (claim_id, source["site_id"], entity_id, source["id"], document_id, url, sentence, fingerprint, sentence, text.find(sentence), text.find(sentence) + len(sentence),
             checked, valid_until, "source_sentence", confidence, freshness, risk, source["media_rights_policy"], json_text(locales),
             None, "source-defined", None, None, None, None, "VERIFIED", version, previous["id"] if previous else None, checked, checked))
        count["claims"] += 1
        count["entities"] += 1
        # A source-backed relationship is only created when the anchor name appears in the exact claim.
        anchor = parse_json(source["config_json"], {}).get("anchorEntity")
        if anchor and anchor.casefold() in sentence.casefold() and name.casefold() != anchor.casefold():
            anchor_id = _upsert_entity(conn, source["site_id"], anchor, checked)
            edge_id = stable_id("edge", source["site_id"], entity_id, anchor_id, "connected_to")
            conn.execute("""insert into knowledge_edges(id,site_id,source_entity_id,target_entity_id,relationship_type,supporting_claim_ids_json,verification_state,confidence,created_at,updated_at)
                         values(?,?,?,?,?,?,?,?,?,?) on conflict(site_id,source_entity_id,target_entity_id,relationship_type) do update set
                         supporting_claim_ids_json=excluded.supporting_claim_ids_json,confidence=excluded.confidence,updated_at=excluded.updated_at""",
                         (edge_id, source["site_id"], entity_id, anchor_id, "connected_to", json_text([claim_id]), "VERIFIED", confidence, checked, checked))
            count["edges"] += 1
    return count


def ingest_due_sources(conn, site_id, contract, limit=50, force=False):
    rows = conn.execute("select * from knowledge_sources where site_id=? and active=1 order by priority desc, id", (site_id,)).fetchall()
    totals = {"sources": 0, "documents": 0, "unchanged": 0, "claims": 0, "entities": 0, "edges": 0, "errors": 0}
    for source in rows[:limit]:
        if not force and source["last_success_at"]:
            then = datetime.fromisoformat(source["last_success_at"])
            if then + timedelta(hours=int(source["poll_cadence_hours"])) > datetime.now(timezone.utc):
                continue
        try:
            documents = _source_documents(source)
            totals["sources"] += 1
            for url, body, headers in documents:
                result = _extract_document(conn, source, url, body, headers, contract)
                totals["documents"] += 1
                for key in ("unchanged", "claims", "entities", "edges"):
                    totals[key] += result[key]
            body_hash = hashlib.sha256("".join(hashlib.sha256(body).hexdigest() for _, body, _ in documents).encode()).hexdigest() if documents else source["body_hash"]
            conn.execute("""update knowledge_sources set etag=coalesce(?,etag),last_modified=coalesce(?,last_modified),body_hash=?,last_success_at=?,
                         last_changed_at=case when body_hash is not ? then ? else last_changed_at end,last_error=null,updated_at=? where id=?""",
                         (None, None, body_hash, now_iso(), body_hash, now_iso(), now_iso(), source["id"]))
        except Exception as error:
            totals["errors"] += 1
            conn.execute("update knowledge_sources set last_error_at=?,last_error=?,updated_at=? where id=?", (now_iso(), str(error)[:1000], now_iso(), source["id"]))
    return totals


def backfill_configured_anchor_edges(conn, site_id, contract):
    """Materialize source-scope relationships declared by site configuration.

    This is provider- and site-neutral: the source registry must explicitly
    attest its scope and choose an edge type allowed by the active contract.
    """
    allowed = set(contract.get("graph", {}).get("edgeTypes") or [])
    created = 0
    updated = 0
    checked = now_iso()
    sources = conn.execute("select * from knowledge_sources where site_id=? and active=1", (site_id,)).fetchall()
    for source in sources:
        config = parse_json(source["config_json"], {})
        anchor_name = str(config.get("anchorEntity") or "").strip()
        relationship = str(config.get("anchorRelationship") or "").strip()
        if not anchor_name or not relationship or not bool(config.get("scopeAttestation")) or relationship not in allowed:
            continue
        anchor_id = _upsert_entity(conn, site_id, anchor_name, checked)
        claims = conn.execute("""select id,entity_id,confidence from knowledge_claims
            where site_id=? and source_id=? and status='VERIFIED' and entity_id<>?""", (site_id, source["id"], anchor_id)).fetchall()
        for claim in claims:
            edge_id = stable_id("edge", site_id, claim["entity_id"], anchor_id, relationship)
            existing = conn.execute("select supporting_claim_ids_json from knowledge_edges where id=?", (edge_id,)).fetchone()
            support = parse_json(existing["supporting_claim_ids_json"], []) if existing else []
            if claim["id"] not in support:
                support = (support + [claim["id"]])[-100:]
            conn.execute("""insert into knowledge_edges(id,site_id,source_entity_id,target_entity_id,relationship_type,supporting_claim_ids_json,
                verification_state,confidence,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,?)
                on conflict(site_id,source_entity_id,target_entity_id,relationship_type) do update set
                supporting_claim_ids_json=excluded.supporting_claim_ids_json,confidence=max(knowledge_edges.confidence,excluded.confidence),updated_at=excluded.updated_at""",
                (edge_id, site_id, claim["entity_id"], anchor_id, relationship, json_text(support), "VERIFIED", float(claim["confidence"]), checked, checked))
            if existing:
                updated += 1
            else:
                created += 1
    return {"created": created, "updated": updated}


def expire_claims(conn, site_id):
    cursor = conn.execute("""update knowledge_claims set status='REFRESH_DUE',updated_at=? where site_id=? and status='VERIFIED'
                           and valid_until is not null and valid_until < ?""", (now_iso(), site_id, now_iso()))
    return cursor.rowcount


def _score(claim, source, has_edge, weights):
    freshness = {"durable": 80, "annual": 72, "volatile": 45, "live": 30}.get(claim["freshness_class"], 50)
    text = claim["claim_text"]
    number_bonus = 10 if re.search(r"\d", text) else 0
    mechanism_bonus = 10 if re.search(r"\b(why|because|water|forest|volcan|history|built|tax|route|levada|biodivers|infraestruct|engenh)", text, re.I) else 0
    parts = {"surprise": min(95, 64 + number_bonus + mechanism_bonus), "madeiraUniqueness": 92 if has_edge else 68,
             "visualStrength": min(92, 62 + number_bonus + (8 if len(text) > 180 else 0)), "storyDepth": 76 if has_edge else 60,
             "usefulness": min(92, 68 + number_bonus + mechanism_bonus), "sourceQuality": round(float(claim["confidence"]) * 100),
             "expandability": 76 if has_edge else 58, "freshness": freshness}
    score = sum(parts.get(key, 0) * float(weight) for key, weight in weights.items())
    return round(score, 2), parts


def build_candidates(conn, site_id, contract, limit=1000):
    cfg = contract.get("candidateEngine", {})
    limit = max(1, min(10000, int(cfg.get("poolLimit") or limit)))
    weights = cfg.get("scoring", {})
    minimum = float(cfg.get("minimumScore", 72))
    angles = cfg.get("nativeAngles", ["what_is_it"])
    formats = [("instagram", "reel"), ("tiktok", "short_video"), ("x", "thread"), ("threads", "conversation_post"), ("pinterest", "pin")]
    locales = contract.get("project", {}).get("locales", ["en"])
    rows = conn.execute("""select c.*, s.source_class from knowledge_claims c join knowledge_sources s on s.id=c.source_id
                           where c.site_id=? and c.status='VERIFIED' order by c.created_at desc limit ?""", (site_id, limit)).fetchall()
    created = rejected = 0
    for claim in rows:
        edge = conn.execute("select * from knowledge_edges where site_id=? and source_entity_id=? and verification_state='VERIFIED' limit 1", (site_id, claim["entity_id"])).fetchone()
        entity = conn.execute("select * from knowledge_entities where id=?", (claim["entity_id"],)).fetchone()
        for index, (channel, native_format) in enumerate(formats):
            angle = angles[index % len(angles)]
            locale = locales[0]
            fingerprint = hashlib.sha256("|".join((claim["id"], edge["id"] if edge else "", angle, native_format, locale)).encode()).hexdigest()
            score, parts = _score(claim, None, bool(edge), weights)
            state, reason = "CANDIDATE", None
            if claim["freshness_class"] in {"live", "volatile"}:
                state, reason = "REJECTED", "Mutable claim cannot enter drafting without a current source check."
            elif claim["risk_class"] in HIGH_RISK and (not claim["effective_date_or_year"] or not claim["conditions_text"]):
                state, reason = "REJECTED", "High-risk claim lacks required year/effective date and conditions."
            elif not edge:
                state, reason = "REJECTED", "Generic substitution guard: no source-backed relationship makes this destination-generic."
            elif score < minimum:
                state, reason = "REJECTED", f"Score {score} is below contract threshold {minimum}."
            payoff = f"What the official source establishes about {entity['canonical_name']} and its verified relationship."
            candidate_id = stable_id("cand", site_id, fingerprint)
            inserted = conn.execute("""insert into content_candidates(id,site_id,entity_id,claim_id,relationship_id,native_angle,audience_state,native_format,locale,hook_family,
                proposed_payoff,visual_mechanism,score,score_breakdown_json,novelty_fingerprint,workflow_state,rejection_reason,created_at,updated_at)
                values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) on conflict(site_id,novelty_fingerprint) do nothing""",
                (candidate_id, site_id, claim["entity_id"], claim["id"], edge["id"] if edge else None, angle, "curious about Madeira", native_format, locale,
                 "hidden_mechanism" if edge else None, payoff, "source-backed map or explanatory visual; no documentary assertion", score, json_text(parts), fingerprint, state, reason, now_iso(), now_iso()))
            if inserted.rowcount:
                created += state == "CANDIDATE"; rejected += state == "REJECTED"
    return {"created": created, "rejected": rejected}


def review_rows(conn, site_id, state=None, limit=30):
    sql = """select cc.*, e.canonical_name, kc.claim_text, kc.source_url, ks.owner, ks.source_class, ke.relationship_type
             from content_candidates cc join knowledge_entities e on e.id=cc.entity_id join knowledge_claims kc on kc.id=cc.claim_id
             join knowledge_sources ks on ks.id=kc.source_id left join knowledge_edges ke on ke.id=cc.relationship_id where cc.site_id=?"""
    params = [site_id]
    if state:
        sql += " and cc.workflow_state=?"; params.append(state)
    sql += " order by cc.score desc, cc.created_at desc limit ?"; params.append(limit)
    return conn.execute(sql, params).fetchall()


def _fact_hook(channel, entity, fact):
    fossil = re.search(r"fossils?\s+(over|more than)\s+(\w+(?:[- ]\w+){0,3}\s+years old)", fact, re.I)
    has_quarries = bool(re.search(r"two\s+limestone\s+quarries", fact, re.I))
    has_kiln = bool(re.search(r"(?:a|one)\s+lime\s+kiln", fact, re.I))
    if fossil and has_quarries and has_kiln:
        age = f"{fossil.group(1).lower()} {fossil.group(2).lower()}"
        hooks = {
            "instagram": f"Two limestone quarries. One lime kiln. Fossils {age}. Why are they all in one place?",
            "tiktok": f"Two quarries, one kiln — and fossils {age}. This is one Madeira museum route.",
            "x": f"What connects two limestone quarries, a lime kiln and fossils {age}?",
            "threads": f"Two quarries, a lime kiln and fossils {age} in one Madeira museum route is quite a combination.",
            "pinterest": f"{entity}: Two Quarries, One Lime Kiln and Fossils {age.title()}",
        }
        return hooks.get(channel, hooks["instagram"])
    if fossil:
        age = f"{fossil.group(1).lower()} {fossil.group(2).lower()}"
        return f"Why does {entity} contain fossils {age}?"
    number = re.search(r"(?:over|more than|approximately|about)?\s*\d[\d,.\s]*(?:m²|years?|km|ha|%)?", fact, re.I)
    if number:
        value = number.group(0).strip()
        return f"What does {value} reveal about {entity}?"
    return f"What unexpected connection does the evidence reveal at {entity}?"


def _generated_media_plan(channel, entity, fact):
    """Specific generative plan; media is editorial illustration, never factual evidence."""
    shared = {
        "productionState": "PLANNED_NOT_GENERATED",
        "rightsState": "generated_explanatory_media",
        "disclosure": "AI-generated editorial illustration. It does not depict the actual site, current conditions, artifacts, staff, or documentary events.",
        "hardExclusions": ["no photoreal claim of the real location", "no readable third-party logos", "no real people", "no archive-photo imitation", "no invented dates or facts", "no text baked into imagery"],
        "factualSpine": fact,
    }
    subject = f"editorial explanatory illustration for {entity}; visually translate only this verified fact: {fact}"
    if channel == "instagram":
        return {**shared, "assetType": "generated_video", "aspectRatio": "9:16", "durationSeconds": 24, "safeTextZone": "upper 20% and lower 18% clear",
                "scenes": [
                    {"seconds": "0-4", "shot": "macro dolly across abstract limestone texture; a single embedded fossil silhouette becomes visible", "onScreenText": _fact_hook("instagram", entity, fact)},
                    {"seconds": "4-10", "shot": "slow reveal from stone strata to a stylised, non-literal quarry cross-section with two distinct cut faces", "onScreenText": "Two quarries. One lime kiln."},
                    {"seconds": "10-17", "shot": "diagrammatic transition: stone → kiln heat glow → narrow water-channel/terrace lines, with no people or real architecture", "onScreenText": "A production landscape, not just a museum."},
                    {"seconds": "17-24", "shot": "pull back to a clean editorial map-like Madeira silhouette with a highlighted north-coast dot; retain clear lower CTA zone", "onScreenText": "Source-backed Madeira detail."}],
                "generationPrompt": f"Vertical 9:16 cinematic editorial explainer, 24 seconds, {subject}. Tactile limestone, restrained earth palette, physically plausible macro photography blended with minimal 3D explanatory diagrams. Smooth camera moves, no people, no signage, no logos, no readable text. This is a conceptual illustration, not a reconstruction of a real place. Keep upper and lower safe zones clean."}
    if channel == "tiktok":
        return {**shared, "assetType": "generated_video", "aspectRatio": "9:16", "durationSeconds": 18, "safeTextZone": "top 16% clear for captions",
                "scenes": [
                    {"seconds": "0-3", "shot": "immediate macro reveal of a fossil impression in pale limestone", "onScreenText": _fact_hook("tiktok", entity, fact)},
                    {"seconds": "3-8", "shot": "fast match-cut sequence: fossil texture → abstract quarry wall → glowing lime kiln silhouette", "onScreenText": "One site, several layers."},
                    {"seconds": "8-14", "shot": "top-down animated terrain diagram with two quarry marks and terrace lines", "onScreenText": "See the whole mechanism."},
                    {"seconds": "14-18", "shot": "calm final stone texture with an open lower text zone", "onScreenText": "Check the official source."}],
                "generationPrompt": f"Vertical 9:16 fast-paced conceptual TikTok explainer, 18 seconds, {subject}. Editorial macro limestone and clean abstract terrain graphics, match cuts, no people, no real buildings, no logos, no embedded typography. Illustrative only, never documentary."}
    if channel == "pinterest":
        return {**shared, "assetType": "generated_image_set", "aspectRatio": "2:3", "safeTextZone": "top third clear for title overlay", "images": [
                    {"role": "hero", "shot": "editorial macro of limestone with an ancient fossil impression; warm directional side light"},
                    {"role": "context", "shot": "stylised cutaway terrain illustration showing quarry faces, kiln geometry and terraces; non-literal"},
                    {"role": "detail", "shot": "minimal graphic composition of stone, kiln glow and thin levada-like linework"}],
                "generationPrompt": f"Portrait 2:3 premium editorial illustration set, {subject}. Museum-quality limestone texture, quiet earth palette, generous clean top-third safe zone, no people, no signage, no logos, no text in image. Do not recreate an actual museum or site."}
    if channel == "x":
        return {**shared, "assetType": "generated_image", "aspectRatio": "16:9", "safeTextZone": "right 30% clear for optional thread card text", "images": [
                    {"role": "thread-card", "shot": "wide editorial triptych: fossil texture, quarry cross-section, kiln silhouette; clear separators but no labels"}],
                "generationPrompt": f"Wide 16:9 conceptual editorial thread card, {subject}. Three visual beats: limestone fossil, non-literal quarry geology, abstract lime kiln glow. No people, logos, maps with real boundaries, or text; clearly illustrative."}
    if channel == "threads":
        return {**shared, "assetType": "generated_image", "aspectRatio": "4:5", "safeTextZone": "upper 18% clear", "images": [
                    {"role": "conversation-image", "shot": "one tactile fossil-in-limestone foreground, dissolving into a restrained quarry-and-kiln line illustration"}],
                "generationPrompt": f"Portrait 4:5 conceptual editorial image, {subject}. Tactile stone macro with subtle overlay of quarry and kiln geometry, muted natural palette, no people, signage, logos or baked text. Not a photo of a real site."}
    raise ValueError(f"Unsupported review channel: {channel}")


def _native_copy(channel, entity, fact, source_url):
    """Create review copy and a channel-specific planned generative visual treatment."""
    hook = _fact_hook(channel, entity, fact)
    disclosure = f"Source: {source_url}"
    media_brief = _generated_media_plan(channel, entity, fact)
    if channel == "instagram":
        return {"hook": hook, "scriptOrSlides": [hook, "The official description brings all three elements into one 12,000 m² centre.", fact, disclosure],
                "caption": f"{hook}\n\n{fact}\n\n{disclosure}", "altText": f"AI-generated conceptual editorial illustration for {entity}; not a documentary image.", "mediaBrief": media_brief}
    if channel == "tiktok":
        return {"hook": hook, "scriptOrSlides": [hook, "The answer is Rota da Cal's 12,000 m² centre.", fact, disclosure],
                "caption": f"{hook}\n\n{fact}\n\n{disclosure}", "altText": f"AI-generated conceptual explanatory video for {entity}; not a documentary video.", "mediaBrief": media_brief}
    if channel == "x":
        return {"hook": hook, "scriptOrSlides": [f"1/3 {hook}", f"2/3 {fact}", f"3/3 Geological time and lime production share the same museum route. {disclosure}"],
                "caption": f"{hook}\n\n{fact}\n\n{disclosure}", "altText": f"AI-generated conceptual thread card for {entity}; not a real site photo.", "mediaBrief": media_brief}
    if channel == "threads":
        return {"hook": hook, "scriptOrSlides": [hook, fact, disclosure],
                "caption": f"{hook}\n\n{fact}\n\n{disclosure}", "altText": f"AI-generated conceptual editorial image for {entity}; not a real site photo.", "mediaBrief": media_brief}
    if channel == "pinterest":
        return {"hook": hook, "scriptOrSlides": [hook, fact, disclosure],
                "caption": f"{hook}\n\n{fact}\n\n{disclosure}", "altText": f"AI-generated conceptual editorial Pin for {entity}; not a real site photo.", "mediaBrief": media_brief}
    raise ValueError(f"Unsupported review channel: {channel}")


def _draftable_claim(row):
    """Provider/tourism copy may evidence its own operations, never an absolute judgment."""
    promotional = re.compile(r"\b(one of the|most |best |top |quickly became|unique|unforgettable|must[- ]see|perfect|ideal|attractive)\b", re.I)
    return not promotional.search(row["claim_text"])


def materialize_review_drafts(conn, site_id, limit=5):
    """Make text-only, approval-gated native packages from a single verified factual spine."""
    contract, _ = active_contract(conn, site_id)
    channel_by_format = {"reel": "instagram", "short_video": "tiktok", "thread": "x", "conversation_post": "threads", "pin": "pinterest"}
    existing = conn.execute("select count(*) from content_packages where site_id=? and approval_state='AWAITING_APPROVAL'", (site_id,)).fetchone()[0]
    remaining = max(0, int(limit) - int(existing))
    if not remaining:
        return {"created": 0, "packages": [], "reason": "review queue target already met"}
    rows = conn.execute("""select cc.*, e.canonical_name, kc.claim_text, kc.source_url, kc.freshness_class, kc.risk_class,
                                  kc.valid_until, kc.visual_rights_state, ks.owner
                           from content_candidates cc join knowledge_entities e on e.id=cc.entity_id
                           join knowledge_claims kc on kc.id=cc.claim_id join knowledge_sources ks on ks.id=kc.source_id
                           where cc.site_id=? and cc.workflow_state='CANDIDATE' and kc.status='VERIFIED'
                           and kc.freshness_class in ('durable','annual') and kc.risk_class='low'
                           order by cc.score desc, cc.id""", (site_id,)).fetchall()
    rows = [row for row in rows if _draftable_claim(row)]
    selected = []
    spine_claim_id = rows[0]["claim_id"] if rows else None
    # A factual spine must fan out to genuinely different native formats, not cloned captions.
    for row in rows:
        if row["claim_id"] != spine_claim_id:
            continue
        if row["native_format"] in {item["native_format"] for item in selected}:
            continue
        if row["native_format"] not in {"reel", "short_video", "thread", "conversation_post", "pin"}:
            continue
        selected.append(row)
        if len(selected) >= remaining:
            break
    if len({channel_by_format.get(row["native_format"]) for row in selected}) < min(remaining, 5):
        raise ValueError("Not enough distinct low-risk native formats to materialize review drafts")
    made = []
    for row in selected:
        channel = channel_by_format[row["native_format"]]
        copy = _native_copy(channel, row["canonical_name"], row["claim_text"], row["source_url"])
        hook = {"hook": copy["hook"], "promise": "A source-backed Madeira explanation.", "openLoop": "The factual detail is supplied before the close.",
                "payoff": row["claim_text"], "payoffClaimIds": [row["claim_id"]], "risk": "low",
                "rejectedAlternatives": [{"hook": "The best Madeira secret", "reason": "Unsupported superlative."}, {"hook": "You must see this now", "reason": "Invented urgency."}]}
        brief_id = stable_id("brief", site_id, row["id"])
        review = {"required": True, "reason": "Phase 2 text-only package; publication and media are disabled.", "risk": "low"}
        conn.execute("""insert into content_briefs(id,site_id,candidate_id,factual_spine_json,prohibited_overclaims_json,hook_json,channel,format,locale,cta_intent,
                      script_json,media_rights_plan_json,canonical_decision_json,expires_at,review_requirements_json,workflow_state,created_at,updated_at)
                      values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) on conflict(candidate_id) do nothing""",
                     (brief_id, site_id, row["id"], json_text({"claimIds": [row["claim_id"]], "claim": row["claim_text"], "sourceUrl": row["source_url"]}),
                      json_text(["No superlatives, urgency, recommendation, current availability, or unsupported visual assertion."]), json_text(hook), channel, row["native_format"], row["locale"], "source_review",
                      json_text(copy["scriptOrSlides"]), json_text(copy["mediaBrief"]), json_text({"action": "none", "reason": "Phase 2 does not create a canonical article."}),
                      row["valid_until"], json_text(review), "AWAITING_APPROVAL", now_iso(), now_iso()))
        package_id = stable_id("pkg", site_id, row["id"], channel, row["locale"])
        package_fingerprint = hashlib.sha256("|".join((row["id"], channel, row["native_format"], row["locale"])).encode()).hexdigest()
        validation = {"ok": True, "claimIds": [row["claim_id"]], "sourceBacked": True, "mediaGenerated": False, "mediaPlan": "specific_generated_editorial", "publicationDisabled": True,
                      "checks": ["low-risk durable/annual claim", "exact source disclosure", "native channel format", "planned media is illustrative, not evidence", "approval required"]}
        inserted = conn.execute("""insert into content_packages(id,site_id,brief_id,candidate_id,channel,locale,format,copy_json,asset_manifest_json,source_disclosure,
                      commercial_disclosure,alt_text,destination_url,validation_report_json,approval_state,metrics_json,package_fingerprint,created_at,updated_at)
                      values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) on conflict(site_id,package_fingerprint) do nothing""",
                     (package_id, site_id, brief_id, row["id"], channel, row["locale"], row["native_format"], json_text(copy), json_text([copy["mediaBrief"]]),
                      f"{row['owner']}: {row['source_url']}", None, copy["altText"], None, json_text(validation), "AWAITING_APPROVAL", json_text({}), package_fingerprint, now_iso(), now_iso()))
        if inserted.rowcount:
            conn.execute("update content_candidates set workflow_state='BRIEFED',updated_at=? where id=?", (now_iso(), row["id"]))
            made.append({"packageId": package_id, "channel": channel, "format": row["native_format"], "entity": row["canonical_name"], "claimId": row["claim_id"]})
    return {"created": len(made), "packages": made}


def refresh_review_package_media_plans(conn, site_id):
    """Upgrade existing review drafts in place; preserves IDs and never generates assets."""
    rows = conn.execute("""select cp.id package_id, cp.brief_id, cp.candidate_id, cp.channel, cp.format, cp.locale,
            cc.claim_id, e.canonical_name, kc.claim_text, kc.source_url, kc.visual_rights_state, ks.owner
            from content_packages cp join content_candidates cc on cc.id=cp.candidate_id join knowledge_entities e on e.id=cc.entity_id
            join knowledge_claims kc on kc.id=cc.claim_id join knowledge_sources ks on ks.id=kc.source_id where cp.site_id=?""", (site_id,)).fetchall()
    updated = 0
    for row in rows:
        if not _draftable_claim(row):
            continue
        copy = _native_copy(row["channel"], row["canonical_name"], row["claim_text"], row["source_url"])
        hook = {"hook": copy["hook"], "promise": "A specific source-backed factual tension.", "openLoop": "The opening visual question resolves with the cited detail.",
                "payoff": row["claim_text"], "payoffClaimIds": [row["claim_id"]], "risk": "low",
                "rejectedAlternatives": [{"hook": "The best Madeira secret", "reason": "Unsupported superlative."}, {"hook": "You must see this now", "reason": "Invented urgency."}]}
        validation = {"ok": True, "claimIds": [row["claim_id"]], "sourceBacked": True, "mediaGenerated": False, "mediaPlan": "specific_generated_editorial", "publicationDisabled": True,
                      "checks": ["low-risk durable/annual claim", "exact source disclosure", "native channel format", "planned media is illustrative, not evidence", "approval required"]}
        conn.execute("update content_briefs set hook_json=?,script_json=?,media_rights_plan_json=?,updated_at=? where id=?", (json_text(hook), json_text(copy["scriptOrSlides"]), json_text(copy["mediaBrief"]), now_iso(), row["brief_id"]))
        conn.execute("""update content_packages set copy_json=?,asset_manifest_json=?,alt_text=?,validation_report_json=?,updated_at=? where id=?""",
                     (json_text(copy), json_text([copy["mediaBrief"]]), copy["altText"], json_text(validation), now_iso(), row["package_id"]))
        updated += 1
    return {"updated": updated, "generated": 0}


def review_packages(conn, site_id, limit=20):
    return conn.execute("""select cp.*, cb.hook_json, e.canonical_name from content_packages cp
        join content_candidates cc on cc.id=cp.candidate_id join knowledge_entities e on e.id=cc.entity_id
        join content_briefs cb on cb.id=cp.brief_id where cp.site_id=? order by cp.created_at desc limit ?""", (site_id, limit)).fetchall()


def run(conn, site_id, contract_url=None, sources=None, trigger="manual", force=False, source_limit=50):
    ensure_schema(conn)
    contract = fetch_contract(conn, site_id, contract_url) if contract_url else active_contract(conn, site_id)[0]
    _, version = active_contract(conn, site_id)
    # Runs can start within one second (manual retry or test); timestamps alone are not unique.
    run_id = stable_id("run", site_id, trigger, now_iso(), time.time_ns())
    conn.execute("insert into content_engine_runs(id,site_id,run_type,trigger,contract_version,status,started_at) values(?,?,?,?,?,?,?)", (run_id, site_id, "phase1_ingestion", trigger, version, "RUNNING", now_iso()))
    try:
        registered = register_sources(conn, site_id, sources or []) if sources else 0
        totals = ingest_due_sources(conn, site_id, contract, limit=source_limit, force=force)
        totals["registered_sources"] = registered
        totals["expired_claims"] = expire_claims(conn, site_id)
        anchor_edges = backfill_configured_anchor_edges(conn, site_id, contract)
        totals["configured_edges_created"] = anchor_edges["created"]
        totals["configured_edges_updated"] = anchor_edges["updated"]
        totals.update(build_candidates(conn, site_id, contract))
        conn.execute("update content_engine_runs set status='SUCCEEDED',counters_json=?,finished_at=? where id=?", (json_text(totals), now_iso(), run_id))
        return {"run_id": run_id, **totals}
    except Exception as error:
        conn.execute("update content_engine_runs set status='FAILED',error_text=?,finished_at=? where id=?", (str(error)[:2000], now_iso(), run_id))
        raise


def main():
    parser = argparse.ArgumentParser(description="Run the generic evidence-first content engine.")
    parser.add_argument("--db", default=str(Path(__file__).resolve().parent / "data/blog_core.sqlite3"))
    parser.add_argument("--site-id", required=True, type=int)
    parser.add_argument("--contract-url")
    parser.add_argument("--sources-json", help="Path to a site-owned source registry JSON array")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    sources = json.loads(Path(args.sources_json).read_text()) if args.sources_json else None
    with sqlite3.connect(args.db) as conn:
        conn.row_factory = sqlite3.Row
        result = run(conn, args.site_id, args.contract_url, sources, trigger="cli", force=args.force)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
