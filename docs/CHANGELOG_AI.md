# CHANGELOG_AI.md

This file is updated by Codex after every task.

## 2026-07-01 — Set up self-updating project memory

### Summary

* Added repository-level project memory and future-agent instructions.
* Documented confirmed product overview, architecture, business rules, integrations, SEO/content behavior, deployment notes, known pitfalls, and prior decisions.
* Added the rule that Codex must read memory before non-trivial tasks and update changelog/memory after completed tasks.

### Files changed

* `AGENTS.md` — added required memory workflow, what to store/avoid, and repository rules.
* `docs/PROJECT_MEMORY.md` — created durable project memory with product, architecture, deployment, integration, SEO, pitfalls, decisions, and do-not-repeat notes.
* `docs/CHANGELOG_AI.md` — created AI changelog and logged this memory setup task.
* `docs/BUSINESS_CONTEXT.md` — documented business/product context.
* `docs/DEPLOYMENT.md` — documented runtime, PM2, nginx, environment, and deployment checks.
* `docs/INTEGRATIONS.md` — documented scanner, CNAME, DNS, RSS, and SQLite integration contracts.
* `docs/SEO_MEMORY.md` — documented SEO/content behavior and current limitations.

### Decisions

* Memory files live inside the repository and must be maintained as part of future tasks.
* Sensitive values, raw logs, generated databases, previews, and secrets must not be stored in memory.

### Checks run

* Read existing `README.md`, `requirements.txt`, `run.sh`, `.gitignore`, `app.py`, nginx configs, PM2 process details, Git history, and SQLite schema.
* Confirmed `python3 -m py_compile app.py` still passes before creating memory files.

### Risks / TODO

* Keep memory concise and durable; avoid turning it into a duplicate of the full codebase.
* Future agents must update this file after every completed task.

## 2026-07-01 — Clean up topic discovery signal quality

### Summary

* Removed Reddit/Google source failures from selectable signal cards.
* Increased topic discovery capacity to 20 usable signals per source.
* Added relevance scoring, deduplication, and Reddit discussion filtering so article ideas are based on top/relevant signals instead of random or error items.
* Updated the manage-page UI to show source warnings as notes and display signal counts.

### Files changed

* `app.py` — changed Google and Reddit signal fetchers to return `(signals, warnings)`, added scoring/filtering, updated `/topic-signals` API payload, and updated signal UI rendering.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that source errors must be warnings, not cards.
* `docs/INTEGRATIONS.md` — documented the topic discovery contract and limitations.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Do not pad the signal grid with low-relevance or failed-source items just to increase card count.
* Reddit RSS 429 is an expected degraded state and should not block Google signals.

### Checks run

* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/api/sites/5/topic-signals` for `week`, `month`, `3m`, and `6m`; confirmed no disabled/error cards and no zero-score returned signals.

### Risks / TODO

* Reddit RSS can still rate-limit; a more reliable Reddit integration may require API credentials or caching/backoff.
* Current Google source is Google News RSS, not official Google Trends.
