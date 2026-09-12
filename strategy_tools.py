import json
import os
import re
import sqlite3
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", ".next", "venv", ".venv", "__pycache__", "backups", "_sync_backups", "media", "uploads"}
SENSITIVE_PATH = re.compile(r"(^|/)(\.env|id_rsa|credentials?|secrets?|tokens?)(\.|/|$)|\.(pem|key|p12)$", re.I)
SENSITIVE_COLUMN = re.compile(r"pass|secret|token|cookie|session|credential|api.?key|auth|email|phone|ip_address|full.?name", re.I)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _redact(value):
    text = str(value or "")
    text = re.sub(r"(?i)(api[_-]?key|token|secret|password|authorization)(\s*[=:]\s*)[^\s,;\"']+", r"\1\2[REDACTED]", text)
    text = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[REDACTED_GOOGLE_KEY]", text)
    text = re.sub(r"AQ\.[0-9A-Za-z_-]{20,}", "[REDACTED_KEY]", text)
    text = re.sub(r"(?i)bearer\s+[0-9A-Za-z._~-]+", "Bearer [REDACTED]", text)
    return text


def tool_declarations():
    return [
        {"name": "inspect_site_configuration", "description": "Read the current Blog Core registry record and detect the site's local technology and authoritative root path. Use this first.", "parameters": {"type": "object", "properties": {}}},
        {"name": "inspect_content_operations", "description": "Inspect current publishing inventory, queues, failures, social connections, cadences and unresolved Blog Core recommendations for this site.", "parameters": {"type": "object", "properties": {}}},
        {"name": "list_factory_content", "description": "Read the live Blog Core content registry for this site, including published, imported, queued, generating, draft and failed work. Paginate until nextCursor is null when auditing the complete inventory.", "parameters": {"type": "object", "properties": {"cursor": {"type": "integer", "description": "Zero-based row offset."}, "limit": {"type": "integer", "description": "Rows per page, from 1 to 200."}, "statuses": {"type": "array", "items": {"type": "string"}, "description": "Optional exact statuses to include."}}}},
        {"name": "search_factory_content", "description": "Batch-search the current Blog Core registry, live sitemap and actual social publication history before proposing SEO pages, articles or social assets. Returns closest existing jobs, live canonical routes and channel-specific social matches for every candidate query.", "parameters": {"type": "object", "properties": {"queries": {"type": "array", "items": {"type": "string"}, "description": "One to fifty proposed titles, intents, canonical paths, or channel-prefixed social assignments."}, "limit": {"type": "integer", "description": "Closest matches per query, from 1 to 10."}}, "required": ["queries"]}},
        {"name": "list_site_files", "description": "List current files and directories inside the site's authoritative VPS root. Backups, dependencies and secrets are excluded.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Relative directory under the site root, or empty for root."}, "depth": {"type": "integer", "description": "Depth from 1 to 4."}, "pattern": {"type": "string", "description": "Optional case-insensitive filename substring."}}}},
        {"name": "read_site_files", "description": "Read selected current text source files under the site's authoritative root. Use it to inspect homepage, routes, README, templates, sitemaps and product logic. Secret files are blocked and sensitive values are redacted.", "parameters": {"type": "object", "properties": {"paths": {"type": "array", "items": {"type": "string"}, "description": "One to eight relative file paths returned by list_site_files."}}, "required": ["paths"]}},
        {"name": "inspect_site_databases", "description": "Discover authoritative SQLite databases used by the current site, including validated external data paths used by its running process, and inspect tables, columns and aggregate row counts without exposing user records.", "parameters": {"type": "object", "properties": {}}},
        {"name": "query_site_database", "description": "Run one read-only SELECT aggregate against a discovered site SQLite database. Use for product inventory, listings, feature status and operational counts. Sensitive field values are redacted.", "parameters": {"type": "object", "properties": {"database": {"type": "string", "description": "Relative database path returned by inspect_site_databases."}, "sql": {"type": "string", "description": "A single SELECT/WITH query, no PRAGMA or multiple statements."}}, "required": ["database", "sql"]}},
        {"name": "inspect_site_runtime", "description": "Inspect matching VPS processes, repository state and recent redacted application log errors for the site. This tool is read-only.", "parameters": {"type": "object", "properties": {}}},
        {"name": "research_external_web", "description": "Run grounded Google Search research for four to eight distinct current market, competitor, distribution and community queries chosen by you. Returns findings and source URLs. This call is mandatory before strategy submission.", "parameters": {"type": "object", "properties": {"queries": {"type": "array", "items": {"type": "string"}, "description": "Four to eight precise, distinct current research queries."}}, "required": ["queries"]}},
    ]


class StrategyToolExecutor:
    def __init__(self, db_path, site_id):
        self.db_path = str(db_path)
        self.site_id = int(site_id)
        self.trace = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("select * from sites where id=?", (self.site_id,)).fetchone()
        if not row:
            raise KeyError("site not found")
        self.site = dict(row)
        self.root = Path(self.site.get("root_path") or "").resolve()
        self.factory_inventory_seen = set()
        self.factory_inventory_total = None
        self.factory_inventory_complete = False
        self.factory_search_performed = False
        if not self.root.is_dir() or self.root == Path("/"):
            raise RuntimeError("site root is not a safe local directory")

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _path(self, relative, require_file=False):
        rel = str(relative or "").strip().lstrip("/")
        if SENSITIVE_PATH.search(rel):
            raise ValueError("sensitive path is blocked")
        target = (self.root / rel).resolve()
        if target != self.root and self.root not in target.parents:
            raise ValueError("path escapes site root")
        if require_file and not target.is_file():
            raise FileNotFoundError(rel)
        return target

    def execute(self, name, args):
        started = _now()
        try:
            method = getattr(self, name)
            result = method(**(args or {}))
            ok = True
        except Exception as error:
            result = {"error": f"{type(error).__name__}: {error}"}
            ok = False
        encoded = json.dumps(result, ensure_ascii=False, default=str)
        if len(encoded) > 70000:
            result = {"truncated": True, "content": encoded[:70000]}
        self.trace.append({"tool": name, "args": args or {}, "ok": ok, "at": started, "resultSummary": _redact(json.dumps(result, ensure_ascii=False, default=str)[:1200])})
        return result

    def inspect_site_configuration(self):
        safe = {k: v for k, v in self.site.items() if k not in {"content_context"}}
        markers = []
        for name in ("README.md", "package.json", "requirements.txt", "pyproject.toml", "docker-compose.yml", "index.html", "sitemap.xml", "robots.txt"):
            if (self.root / name).exists():
                markers.append(name)
        return {"site": safe, "storedContextIsUnverifiedHint": self.site.get("content_context") or "", "authoritativeRoot": str(self.root), "technologyMarkers": markers, "instruction": "Inspect current files and databases before accepting the stored context."}

    def inspect_content_operations(self):
        with self._connect() as conn:
            jobs = [dict(r) for r in conn.execute("select status,count(*) count from content_jobs where site_id=? group by status order by count(*) desc", (self.site_id,))]
            failures = [dict(r) for r in conn.execute("select id,title,status,error,updated_at from content_jobs where site_id=? and status in ('FAILED','ERROR') order by updated_at desc limit 15", (self.site_id,))]
            social = [dict(r) for r in conn.execute("select provider,status,display_name,connected_at,updated_at from social_connections where site_id=?", (self.site_id,))]
            auto = conn.execute("select enabled,times_per_day,channels_json,timezone,start_hour,end_hour,last_run_at,social_cadences_json from autopublish_settings where site_id=?", (self.site_id,)).fetchone()
            recs = [dict(r) for r in conn.execute("select priority,category,publication_type,title,rationale,status,updated_at from agent_recommendations where site_id=? and status not in ('DONE','DISMISSED') order by case priority when 'critical' then 0 when 'high' then 1 else 2 end,updated_at desc limit 30", (self.site_id,))]
            recent = [dict(r) for r in conn.execute("select title,status,category,published_url,updated_at from content_jobs where site_id=? order by updated_at desc limit 20", (self.site_id,))]
            social_counts = [dict(r) for r in conn.execute("select channel,asset_type,status,count(*) count from social_posts where site_id=? group by channel,asset_type,status order by channel,asset_type,status", (self.site_id,))]
            social_failures = [dict(r) for r in conn.execute("select id,job_id,channel,asset_type,status,updated_at from social_posts where site_id=? and status='ERROR' order by updated_at desc limit 20", (self.site_id,))]
            recent_social = [dict(r) for r in conn.execute("select id,job_id,channel,asset_type,status,content_text,remote_url,updated_at from social_posts where site_id=? and status in ('DRAFT','SCHEDULED','SUBMITTED','PUBLISHED','SENT') order by updated_at desc limit 50", (self.site_id,))]
            queued_social_plan = [dict(r) for r in conn.execute("select id,channel,format,status,title,details_json,updated_at from agent_media_plan_items where site_id=? and status in ('QUEUED','GENERATING','READY','APPROVED','SCHEDULED') order by updated_at desc limit 100", (self.site_id,))]
        return {"jobCounts": jobs, "recentFailures": failures, "connections": social, "autopublish": dict(auto) if auto else {}, "unresolvedRecommendations": recs, "recentContent": recent, "socialCounts": social_counts, "socialFailures": social_failures, "recentSocial": recent_social, "queuedSocialPlan": queued_social_plan}

    @staticmethod
    def _content_tokens(text):
        stop = {"about", "and", "are", "best", "blog", "for", "from", "guide", "how", "the", "this", "tips", "to", "what", "when", "with", "your"}
        return set(word for word in re.findall(r"[a-z0-9][a-z0-9-]{1,}", str(text or "").lower()) if word not in stop)

    @classmethod
    def _content_similarity(cls, left, right):
        left_tokens, right_tokens = cls._content_tokens(left), cls._content_tokens(right)
        if not left_tokens or not right_tokens:
            return 0.0
        overlap = left_tokens & right_tokens
        return max(len(overlap) / len(left_tokens | right_tokens), (len(overlap) / min(len(left_tokens), len(right_tokens))) * 0.82)

    def _factory_content_rows(self, statuses=None):
        status_filter = [str(value or "").strip().upper() for value in (statuses or []) if str(value or "").strip()]
        sql = """select id,status,title,topic,slug,description,category,published_url,sources_json,created_at,updated_at
                 from content_jobs where site_id=?"""
        params = [self.site_id]
        if status_filter:
            sql += " and upper(status) in (" + ",".join("?" for _ in status_filter) + ")"
            params.extend(status_filter)
        sql += " order by updated_at desc,id desc"
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def list_factory_content(self, cursor=0, limit=200, statuses=None):
        cursor = max(0, int(cursor or 0))
        limit = max(1, min(200, int(limit or 200)))
        rows = self._factory_content_rows(statuses=statuses)
        page = []
        for row in rows[cursor:cursor + limit]:
            sources = json.loads(row["sources_json"] or "{}") if row.get("sources_json") else {}
            page.append({
                "id": row["id"], "status": row["status"], "title": row["title"] or row["topic"],
                "contentType": sources.get("contentType") or row["category"],
                "targetPath": sources.get("targetPath") or urllib.parse.urlsplit(row["published_url"] or "").path,
                "publishedUrl": row["published_url"] or "", "updatedAt": row["updated_at"],
            })
        next_cursor = cursor + len(page) if cursor + len(page) < len(rows) else None
        if not statuses:
            self.factory_inventory_total = len(rows)
            self.factory_inventory_seen.update(item["id"] for item in page)
            self.factory_inventory_complete = len(self.factory_inventory_seen) >= len(rows)
        return {"total": len(rows), "cursor": cursor, "nextCursor": next_cursor, "items": page}

    def _live_sitemap_routes(self):
        homepage = self.site.get("homepage_url") or f"https://{self.site.get('domain')}/"
        parsed_home = urllib.parse.urlsplit(homepage)
        origin = f"{parsed_home.scheme or 'https'}://{parsed_home.netloc or self.site.get('domain')}"
        queue, visited, routes = [urllib.parse.urljoin(origin + "/", "sitemap.xml")], set(), []
        while queue and len(visited) < 50 and len(routes) < 10000:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "BlogCoreStrategyAgent/1.0"})
                body = urllib.request.urlopen(request, timeout=20).read().decode("utf-8", errors="replace")
            except Exception:
                continue
            locations = [value.replace("&amp;", "&").strip() for value in re.findall(r"<loc>\s*(.*?)\s*</loc>", body, flags=re.I | re.S)]
            if "<sitemapindex" in body.lower():
                queue.extend(location for location in locations if urllib.parse.urlsplit(location).netloc == parsed_home.netloc and location not in visited)
                continue
            routes.extend(location for location in locations if urllib.parse.urlsplit(location).netloc == parsed_home.netloc)
        return list(dict.fromkeys(routes))[:10000]

    def search_factory_content(self, queries, limit=5):
        clean_queries = list(dict.fromkeys(str(value or "").strip() for value in (queries or []) if str(value or "").strip()))[:50]
        if not clean_queries:
            raise ValueError("queries must contain at least one proposed title, intent or path")
        self.factory_search_performed = True
        limit = max(1, min(10, int(limit or 5)))
        rows = self._factory_content_rows()
        with self._connect() as conn:
            social_rows = [dict(row) for row in conn.execute(
                """select id,job_id,channel,asset_type,status,content_text,content_json,remote_url,updated_at
                   from social_posts where site_id=? and status in ('DRAFT','SCHEDULED','SUBMITTED','PUBLISHED','SENT')
                   order by updated_at desc,id desc""", (self.site_id,)
            ).fetchall()]
            queued_plan_rows = [dict(row) for row in conn.execute(
                """select id,channel,format,status,title,details_json,updated_at
                   from agent_media_plan_items where site_id=?
                     and status in ('QUEUED','GENERATING','READY','APPROVED','SCHEDULED')
                   order by updated_at desc,id desc""", (self.site_id,)
            ).fetchall()]
        factory = []
        for row in rows:
            sources = json.loads(row["sources_json"] or "{}") if row.get("sources_json") else {}
            target_path = sources.get("targetPath") or urllib.parse.urlsplit(row["published_url"] or "").path
            comparable = " ".join(filter(None, [row["title"], row["topic"], row["description"], row["slug"], target_path]))
            factory.append({"row": row, "sources": sources, "targetPath": target_path, "comparable": comparable})
        live_routes = self._live_sitemap_routes()
        social = []
        for row in social_rows:
            try:
                payload = json.loads(row["content_json"] or "{}")
            except json.JSONDecodeError:
                payload = {}
            comparable = " ".join(filter(None, [row["channel"], row["asset_type"], row["content_text"], json.dumps(payload, ensure_ascii=False)]))
            social.append({"row": row, "comparable": comparable})
        for plan in queued_plan_rows:
            channel_names = [name for name in ("instagram", "tiktok", "pinterest", "threads", "twitter", "youtube", "reddit") if name in str(plan["channel"] or "").lower()]
            for channel_name in channel_names or [str(plan["channel"] or "plan").lower()]:
                row = {
                    "id": f"media-plan:{plan['id']}:{channel_name}", "job_id": "", "channel": channel_name,
                    "asset_type": plan["format"], "status": plan["status"], "content_text": plan["title"],
                    "content_json": plan["details_json"], "remote_url": "", "updated_at": plan["updated_at"],
                }
                social.append({"row": row, "comparable": " ".join(filter(None, [channel_name, plan["format"], plan["title"], plan["details_json"]]))})
        results = []
        for query in clean_queries:
            job_matches = sorted(factory, key=lambda item: self._content_similarity(query, item["comparable"]), reverse=True)[:limit]
            route_matches = sorted(live_routes, key=lambda url: self._content_similarity(query, urllib.parse.urlsplit(url).path.replace("-", " ")), reverse=True)[:limit]
            social_matches = sorted(social, key=lambda item: self._content_similarity(query, item["comparable"]), reverse=True)[:limit]
            results.append({
                "query": query,
                "factoryMatches": [{
                    "score": round(self._content_similarity(query, item["comparable"]), 3),
                    "id": item["row"]["id"], "status": item["row"]["status"],
                    "title": item["row"]["title"] or item["row"]["topic"],
                    "contentType": item["sources"].get("contentType") or item["row"]["category"],
                    "targetPath": item["targetPath"], "publishedUrl": item["row"]["published_url"] or "",
                } for item in job_matches],
                "liveRouteMatches": [{"score": round(self._content_similarity(query, url), 3), "url": url, "targetPath": urllib.parse.urlsplit(url).path} for url in route_matches],
                "socialMatches": [{
                    "score": round(self._content_similarity(query, item["comparable"]), 3),
                    "id": item["row"]["id"], "jobId": item["row"]["job_id"],
                    "channel": item["row"]["channel"], "assetType": item["row"]["asset_type"],
                    "status": item["row"]["status"], "title": item["row"]["content_text"],
                    "remoteUrl": item["row"]["remote_url"] or "",
                } for item in social_matches],
            })
        return {"checkedAt": _now(), "queries": results}

    def list_site_files(self, path="", depth=2, pattern=""):
        base = self._path(path)
        depth = max(1, min(4, int(depth or 2)))
        needle = str(pattern or "").lower()
        rows = []
        for current, dirs, files in os.walk(base):
            current_path = Path(current)
            rel_depth = len(current_path.relative_to(base).parts)
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            if rel_depth >= depth:
                dirs[:] = []
            for name in sorted(files):
                rel = str((current_path / name).relative_to(self.root))
                if SENSITIVE_PATH.search(rel) or ".backup" in name or ".before-" in name or name.startswith("._"):
                    continue
                if needle and needle not in rel.lower():
                    continue
                try:
                    size = (current_path / name).stat().st_size
                except OSError:
                    continue
                rows.append({"path": rel, "bytes": size})
                if len(rows) >= 300:
                    return {"root": str(self.root), "files": rows, "truncated": True}
        return {"root": str(self.root), "files": rows, "truncated": False}

    def read_site_files(self, paths):
        if not isinstance(paths, list) or not paths:
            raise ValueError("paths must be a non-empty list")
        output = []
        total = 0
        for relative in paths[:8]:
            target = self._path(relative, require_file=True)
            if target.stat().st_size > 2_000_000:
                output.append({"path": str(relative), "error": "file too large"})
                continue
            raw = target.read_bytes()
            if b"\x00" in raw[:4096]:
                output.append({"path": str(relative), "error": "binary file"})
                continue
            text = _redact(raw.decode("utf-8", errors="replace"))[:20000]
            remaining = max(0, 60000 - total)
            text = text[:remaining]
            total += len(text)
            output.append({"path": str(relative), "content": text, "truncated": len(raw) > len(text)})
            if total >= 60000:
                break
        return {"files": output}

    def _database_files(self):
        found = []
        for current, dirs, files in os.walk(self.root):
            p = Path(current)
            if len(p.relative_to(self.root).parts) > 4:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for name in files:
                if name.lower().endswith((".db", ".sqlite", ".sqlite3")):
                    target = (p / name).resolve()
                    if self.root in target.parents and target.is_file():
                        found.append(target)

        # Product applications commonly keep mutable state outside the deploy
        # tree (for example /var/lib/solocruz-product). Discover only paths
        # attributable to this site; never sweep arbitrary system databases.
        allowed_external_roots = []
        var_lib = Path("/var/lib")
        site_tokens = {
            re.sub(r"[^a-z0-9]+", "-", str(self.site.get("domain") or "").lower()).strip("-"),
            re.sub(r"[^a-z0-9]+", "-", self.root.name.lower()).strip("-"),
            re.sub(r"[^a-z0-9]+", "-", str(self.site.get("domain") or "").split(".")[0].lower()).strip("-"),
        }
        site_tokens.discard("")
        if var_lib.is_dir():
            for child in var_lib.iterdir():
                name = child.name.lower()
                if not child.is_dir() or "backup" in name:
                    continue
                if "staging" in name and "staging" not in str(self.root).lower():
                    continue
                if any(name == token or name.startswith(token + "-") for token in site_tokens):
                    allowed_external_roots.append(child.resolve())

        # Prefer the database path actually configured on a matching running
        # process. Only DB-like environment values are inspected; all other
        # environment variables remain unread and are never returned.
        proc_root = Path("/proc")
        if proc_root.is_dir():
            needles = {str(self.root), str(self.site.get("domain") or ""), self.root.name}
            for proc_dir in proc_root.iterdir():
                if not proc_dir.name.isdigit():
                    continue
                try:
                    cmdline = (proc_dir / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", "replace")
                    cwd = (proc_dir / "cwd").resolve()
                except OSError:
                    continue
                if cwd != self.root and self.root not in cwd.parents and not any(n and n in cmdline for n in needles):
                    continue
                try:
                    entries = (proc_dir / "environ").read_bytes().split(b"\x00")
                except OSError:
                    continue
                for entry in entries:
                    if b"=" not in entry:
                        continue
                    key, value = entry.split(b"=", 1)
                    key_text = key.decode("ascii", "ignore")
                    if not re.search(r"(?:^|_)(?:DB|DATABASE)(?:_|$)", key_text, re.I):
                        continue
                    value_text = value.decode("utf-8", "replace")
                    candidate = Path(value_text)
                    if not candidate.is_absolute():
                        candidate = cwd / candidate
                    try:
                        candidate = candidate.resolve()
                    except OSError:
                        continue
                    if candidate.is_file() and candidate.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
                        if candidate == self.root or self.root in candidate.parents or candidate == var_lib or var_lib in candidate.parents:
                            found.append(candidate)
                            if var_lib in candidate.parents:
                                allowed_external_roots.append(next((p for p in candidate.parents if p.parent == var_lib), candidate.parent))

        for external_root in dict.fromkeys(allowed_external_roots):
            for current, dirs, files in os.walk(external_root):
                p = Path(current)
                if len(p.relative_to(external_root).parts) > 3:
                    dirs[:] = []
                    continue
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and "backup" not in d.lower() and not d.startswith(".")]
                for name in files:
                    if name.lower().endswith((".db", ".sqlite", ".sqlite3")):
                        target = (p / name).resolve()
                        if external_root in target.parents and target.is_file():
                            found.append(target)

        unique = []
        for target in found:
            if target not in unique:
                unique.append(target)
        return unique[:20]

    def _database_identifier(self, database):
        if self.root in database.parents:
            return str(database.relative_to(self.root))
        return str(database)

    def _resolve_database(self, database):
        requested = str(database or "").strip()
        for candidate in self._database_files():
            if requested in {str(candidate), self._database_identifier(candidate)}:
                return candidate
        raise ValueError("database was not discovered for this site")

    def inspect_site_databases(self):
        output = []
        for db in self._database_files():
            item = {"database": self._database_identifier(db), "bytes": db.stat().st_size, "tables": []}
            try:
                conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
                for (table,) in conn.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"):
                    cols = [r[1] for r in conn.execute(f'SELECT * FROM pragma_table_info("{table}")')]
                    count = conn.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
                    item["tables"].append({"name": table, "rows": count, "columns": cols})
                conn.close()
            except Exception as error:
                item["error"] = str(error)
            output.append(item)
        return {"databases": output}

    def query_site_database(self, database, sql):
        target = self._resolve_database(database)
        statement = str(sql or "").strip()
        if not re.match(r"^(select|with)\b", statement, re.I) or ";" in statement or re.search(r"\b(pragma|attach|detach|insert|update|delete|replace|drop|alter|create|vacuum)\b", statement, re.I):
            raise ValueError("only one read-only SELECT/WITH query is allowed")
        conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(statement)
        columns = [d[0] for d in cursor.description or []]
        rows = []
        for row in cursor.fetchmany(100):
            item = {}
            for column in columns:
                value = row[column]
                item[column] = "[REDACTED]" if SENSITIVE_COLUMN.search(column) else _redact(value)
            rows.append(item)
        conn.close()
        return {"columns": columns, "rows": rows, "limitedTo": 100}

    def inspect_site_runtime(self):
        proc = subprocess.run(["ps", "-eo", "pid,lstart,args"], capture_output=True, text=True, timeout=10, check=False).stdout.splitlines()
        needles = {str(self.root), self.site.get("domain", ""), self.root.name}
        processes = [_redact(line.strip()) for line in proc if any(n and n in line for n in needles)][:80]
        git = {}
        if (self.root / ".git").exists():
            for key, command in {
                "branch": ["git", "-C", str(self.root), "branch", "--show-current"],
                "lastCommit": ["git", "-C", str(self.root), "log", "-1", "--format=%h %cI %s"],
                "status": ["git", "-C", str(self.root), "status", "--short"],
            }.items():
                result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
                git[key] = _redact(result.stdout.strip())[:12000]
        logs = []
        for current, dirs, files in os.walk(self.root):
            p = Path(current)
            if len(p.relative_to(self.root).parts) > 3:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for name in files:
                if name.endswith((".log", ".err")):
                    target = p / name
                    try:
                        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
                        logs.append({"path": str(target.relative_to(self.root)), "tail": _redact("\n".join(lines))[:10000]})
                    except OSError:
                        pass
                if len(logs) >= 8:
                    break
        return {"processes": processes, "git": git, "recentLogs": logs}

    def research_external_web(self, queries):
        if not isinstance(queries, list):
            raise ValueError("queries must be a list")
        clean_queries = list(dict.fromkeys(str(q or "").strip() for q in queries if str(q or "").strip()))[:8]
        if len(clean_queries) < 4:
            raise ValueError("at least four distinct research queries are required")
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_TEXT_API_KEY")
        if not api_key:
            raise RuntimeError("Gemini API key is not configured")
        model = (os.environ.get("GEMINI_STRATEGY_MODEL") or "gemini-3.7-flash").strip()
        results = []
        all_sources = []
        observed_queries = []
        for query in clean_queries:
            prompt = (
                "Use Google Search now to research the following current market question. "
                "Summarize only evidence supported by the retrieved pages. Identify material caveats. "
                "Do not make strategic recommendations and do not rely only on memory.\n\nQuery: " + query
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "tools": [{"googleSearch": {}}],
                "generationConfig": {"thinkingConfig": {"thinkingLevel": "medium"}},
            }
            body = json.dumps(payload).encode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model, safe='.-')}:generateContent?key={urllib.parse.quote(api_key, safe='')}"
            request = urllib.request.Request(url, data=body, headers={"content-type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    data = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                detail = error.read(1200).decode("utf-8", errors="replace")
                raise RuntimeError(f"grounded search HTTP {error.code}: {detail}") from error
            candidate = (data.get("candidates") or [{}])[0]
            text = "".join(part.get("text") or "" for part in ((candidate.get("content") or {}).get("parts") or []))
            metadata = candidate.get("groundingMetadata") or {}
            search_queries = metadata.get("webSearchQueries") or []
            sources = []
            for chunk in metadata.get("groundingChunks") or []:
                web = chunk.get("web") or {}
                source_url = web.get("uri") or ""
                if source_url:
                    sources.append({"url": source_url, "title": web.get("title") or source_url})
            if not sources:
                raise RuntimeError(f"Google Search returned no grounded sources for query: {query}")
            observed_queries.extend(search_queries or [query])
            all_sources.extend(sources)
            results.append({"requestedQuery": query, "observedQueries": search_queries, "findings": text[:12000], "sources": sources[:12]})
        source_map = {item["url"]: item for item in all_sources}
        return {"queries": list(dict.fromkeys(observed_queries)), "sources": list(source_map.values())[:80], "results": results}
