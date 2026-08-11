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

## Task Fidelity And Architecture

- Every fix must be universal at the relevant product boundary. A current domain, article, object, language, channel, or failed generated asset may be used only as a reproducible verification case; never add branching, prompt wording, validators, selectors, or data rules that name or special-case that example. Fix the shared contract, schema, planner, renderer, adapter, or integration so the same behavior applies to every existing and future site and every semantically equivalent input.
- Before editing after a failure, state the invariant that was violated and identify the shared layer that owns it. If the proposed change cannot be expressed without naming the current example, it is not an acceptable production fix.
- Never substitute a simpler implementation for an explicit product or creative contract merely to preserve existing code, reduce the diff, finish faster, or produce a technically valid artifact.
- Before implementing a non-trivial visual or architectural task, translate the request into observable acceptance criteria and verify whether the current architecture can satisfy them. If it cannot, replace the incompatible architecture instead of patching its symptoms.
- State any unavoidable limitation before generating costly assets. Do not silently reinterpret words such as `layer`, `native`, `source-authoritative`, `preview`, or `publish` to match an existing implementation.
- A technically valid file, successful API response, passing schema, or completed render is not evidence that the requested product behavior is correct. Visual tasks require visual inspection against the user's actual composition and interaction contract.
- Validate expensive generative work inside the requested production artifact. Do not create a separate test, proof, demo, placeholder, or throwaway generation unless the user explicitly asks for one. Any retry must advance or repair the real production asset and preserve already valid stages so generation cost is not repeated.
- For layered storyboard work specifically, the current operator-approved contract is master-derived: generate one complete coherent 9:16 master photograph first, reject it unless every intended movable person/group/object is large, complete, visually separable, inside the frame, and clear of unrelated crowds or overlapping silhouettes, then create an identical clean plate by removing only those approved groups. Extract full-canvas registered layers from the accepted master with specialised segmentation/matting and validate every layer before rendering. The renderer must never auto-center, independently rescale, or reposition an accepted layer. The earlier clean-background plus independently generated foreground architecture is replaced/deprecated because it repeatedly broke geometry, contact, scale, and scene coherence.
- Camera motion belongs to the assembled scene, never to one isolated layer. Use purposeful whole-scene dolly in/out, tracking, follow, crane and orbit moves, apply the identical transform to background and every layer, vary adjacent moves, and retain camera work in every production Reel unless the operator explicitly requests a static composition.
- Camera motion must hold while a new layer enters. After the layer settles, the camera may push toward its face or meaningful upper-body/group area, hold briefly, then pull back or transfer focus to the next settled group. Face/subject pushes are derived from accepted mask bounds and must not crop required anatomy unpredictably.
- Reel copy must use a visually verified quiet zone in the assembled frame. Placement from the text planner is a preference, not authority: the renderer measures foreground occupancy and local texture, chooses the safest available region, and derives fill/contour contrast from the pixels under the final text rectangle.
- Generative visual stages are one-pass. Put the complete quality contract into the first prompt. Validators may stop and report a non-compliant master, clean plate, or layer pack, but they must not automatically request another paid image candidate. A retry is an explicit operator action after the failed prompt or contract has been corrected.
- Do not claim a Reel is ready when the image model ignores registration, leaves matte artifacts, floats objects, clips people or overlaps accepted subjects. Stop the real production record before publication, preserve valid stages, and report the concrete blocker. Programmatic repositioning of a failed generated layer is not an allowed fallback.
