# AGENTS.md

These instructions apply to all Codex work in this repository.

## Required Memory Workflow

Before starting any non-trivial task, Codex must read:

1. `docs/PROJECT_MEMORY.md`
2. `docs/CHANGELOG_AI.md`
3. Relevant files in `docs/` such as:
   - `docs/BUSINESS_CONTEXT.md`
   - `docs/DEPLOYMENT.md`
   - `docs/INTEGRATIONS.md`
   - `docs/SEO_MEMORY.md`
4. Relevant existing code before making changes.

Codex must not rely only on the current chat because context may be compacted or lost.

After every completed task, Codex must update:

1. `docs/CHANGELOG_AI.md` always.
2. `docs/PROJECT_MEMORY.md` if the task created or changed durable project knowledge.
3. Relevant additional memory files if the task affects SEO, business logic, deployment, integrations, architecture, or known pitfalls.

Final responses after each task must include:

- `Memory updated: yes` if memory/changelog files were updated.
- `Memory updated: no, because ...` if there was nothing durable to update.
- A short list of memory/changelog files changed.

This final-response memory line is mandatory even for small tasks. If a task is
purely investigative and creates no durable project knowledge, say why memory
was not updated.

## What Belongs In Memory

Store only durable, useful knowledge:

- Architecture decisions.
- Business logic and product rules.
- API contracts and data model notes.
- Integrations and external services.
- Environment/deployment notes without secrets.
- SEO/content rules.
- Known bugs, edge cases, fragile areas.
- Things already tried and rejected.
- Important client/project preferences.
- Reasons behind decisions.

Do not store:

- Temporary noise.
- Guesses or unverified assumptions.
- Large logs.
- Secrets, tokens, passwords, private keys, or raw `.env` values.
- Duplicated information already captured elsewhere.

If information becomes outdated, do not silently remove it. Mark it as `replaced` or `deprecated` and add the current version.

## Repository Rules

- Primary live working copy is on the VPS at `/var/www/blog.yas.ooo`.
- Canonical GitHub repo is `yasyarik/blogcore`.
- The VPS may use SSH remote `git@github.com:yasyarik/blogcore.git`; local
  clones may use HTTPS through GitHub CLI when SSH keys are unavailable.
- Do not commit `data/`, `previews/`, `.venv/`, logs, secrets, or generated caches.
- Preserve existing user/server state unless the user explicitly asks to remove it.
- For deployment-affecting changes, run at least `python3 -m py_compile app.py` and a health check after restart.
