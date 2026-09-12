# Blog Core Agent Rules

## Durable project memory

Before any non-trivial task, read:

1. `docs/PROJECT_MEMORY.md`
2. `docs/CHANGELOG_AI.md`
3. Relevant files in `docs/`
4. Relevant existing code before changing it

Do not rely only on the current chat: context can be compacted or lost.

After every completed task, update `docs/CHANGELOG_AI.md`. Update
`docs/PROJECT_MEMORY.md` when the task creates durable product, architecture,
deployment, SEO, integration, or operational knowledge. Update relevant
specialized docs such as `docs/DEPLOYMENT.md` and `docs/INTEGRATIONS.md` when
they are affected.

Store only durable, verified, useful information: decisions and reasons,
business rules, API contracts, deployment details without secrets, SEO rules,
known pitfalls, rejected approaches, and client preferences. Never store
secrets, keys, passwords, private paths to credentials, large logs, guesses,
temporary noise, or duplicate detail. When a decision is superseded, mark the
old decision as replaced or deprecated instead of silently deleting it.

Every final response must state `Memory updated: yes` or `Memory updated: no,
because ...`, and name the memory/changelog files changed.

## Product constraints

* Blog Core is both a native content factory and a control panel for imported
  site factories. Imported sites must preserve their native design, templates,
  routes, multilingual behavior, and publication contracts.
* Prefer universal mechanics over site-specific exceptions.
* Do not store or commit `data/`, `previews/`, `.venv`, logs, secrets, tokens,
  private keys, or generated temporary media.
* A recommendation is not a task and is never automatically published.
