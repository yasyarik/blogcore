# CHANGELOG_AI.md

## 2026-08-11 — Integrate validated master-derived storyboard production

### Summary
* Replaced independently generated foregrounds with one coherent master frame per scene, an otherwise-identical clean plate, and full-canvas registered layers extracted from the accepted master.
* Added first-pass prompt requirements and vision gates for complete anatomy, complete clothing and owned objects, subject scale, frame margins, group separability, unrelated-crowd clearance, and text-safe space.
* Added connected clean-plate-difference recovery, enclosed-hole repair, reconstruction checks, and a final visual layer-pack review.
* Deferred all voice generation until every visual scene passes validation.
* Added whole-layer directional entrances, post-entrance face/group camera pushes, pullbacks/focus transfers, automatic quiet-zone typography, and local contrast selection.
* Removed automatic paid image retries. Validators stop a bad one-pass result and require an explicit operator retry after the shared contract is corrected.
* Enabled the master-derived Reel pipeline on the VPS with no existing `GENERATING` Reel jobs.

### Files changed
* `app.py` — master prompt/review, clean-plate generation, registered scene orchestration, integrity gates, one-pass media policy, delayed voice, and v12 metadata.
* `registered_scene.py` — 1-4 quality-driven layers, connected difference recovery, and enclosed-hole repair.
* `reel_renderer.py` — whole-object entrances, delayed subject-focused camera sequence, quiet-zone selection, and luminance-aware text palette.
* `AGENTS.md` — current master-derived, one-pass, camera, and typography invariants.
* `docs/PROJECT_MEMORY.md` — durable production architecture and replaced decisions.

### Decisions
* A prompt must carry the full visual quality contract on its first paid call. Validation is a stop gate, not a retry engine.
* An integrated master is the source of scene truth. Separately generated foreground assets are deprecated for production photorealistic storyboard scenes.

### Checks run
* Compiled `app.py`, `reel_renderer.py`, and `registered_scene.py` locally and in the production `.venv`.
* Ran production-environment contract tests proving that complete separated groups pass and an inseparable master is rejected.
* Ran renderer contract tests for automatic upper safe-zone selection, two subject-focus targets, static entrance phase, camera push, pullback, and focus transfer.
* Confirmed zero queued Instagram Reel generations before activation.
* Restarted `blog-yas-core`; `/health` returned `ok` and PM2 remained online.

### Risks / TODO
* No paid media was generated in this deployment task. The next operator-requested real Reel is the first end-to-end production verification of the one-pass v12 path.

## 2026-08-10 — Make the Reel third stage a deterministic technical manifest gate

### Summary
* Replaced the third-stage free-form visual elaboration model with a deterministic compiler. It cannot invent or replace backgrounds, people, props, placement, or motion after visual planning.
* Added a global composition-contract schema and a text-only SoloCruz verification runner. The initial candidate correctly failed compilation because it did not supply stable production asset IDs or a precise technical manifest.

### Files changed
* `staging/blogcore-live-dynamic-storyboard.py` — added generic Reel composition-contract schema, visual-planning prompt, and deterministic technical-manifest compiler.
* `staging/run_reel_composition_manifest_v3.py` — runs text-only visual planning followed by the compiler; it has no image, audio, music, or video operation.

### Decisions
* Stage three is code-only. Gemini is allowed one visual composition plan before it, but the compiler is the immutable boundary between approved planning and asset generation.

### Checks run
* `python3 -m py_compile staging/blogcore-live-dynamic-storyboard.py staging/run_reel_composition_manifest_v3.py`
* Deployed the updated app to `/var/www/blog.yas.ooo`, restarted `blog-yas-core`, and confirmed `/health` returned `ok`.
* Executed the text-only v3 planner on SoloCruz. Stage two completed in 28.6 seconds; stage three rejected its ambiguous output before any media work began.

### Risks / TODO
* The stage-two visual-composition prompt still needs its own contract-quality improvement. Three text-only retries supplied stable IDs and local timings but failed the semantic geometry gate. Replace the monolithic request with per-scene planning plus validation before moving to the next scene. Do not generate Reel media until a reviewed composition contract compiles successfully.

## 2026-08-10 — Verify the new first Reel architecture pass

### Summary
* Ran exactly one text-only Gemini architecture request against the SoloCruz article after the information-arc prompt update.
* It completed in 26.2 seconds and returned a 7-beat scenario. No downstream planning or media-generation step ran.

### Files changed
* `staging/run_reel_architecture_once.py` — one-shot verification utility used only to measure and save the standalone first-pass result.

### Checks run
* Verified saved architecture contains 7 beats, a source-grounded hook, an open loop, and a payoff.

### Risks / TODO
* The architecture must be reviewed before any visual frame planning. The older SoloCruz grid remains deprecated.

## 2026-08-10 — Remove the artificial first-pass timeout

### Summary
* Removed the 55-second timeout added to the text-only architecture request. The first prompt remains separate from heavy visual planning, but may complete naturally rather than being cut off.

### Files changed
* `staging/blogcore-live-dynamic-storyboard.py` — restores the normal Gemini request timeout for the architecture call.

### Checks run
* Python compilation and Blog Core health check.

## 2026-08-10 — Rebuild Reel prompt around the article's information hierarchy

### Summary
* Replaced the generic causal-character-story instruction with a source-grounded information-arc contract for all informational Reels.
* Added central-problem extraction, ranked key insights, held-back final payoff, and conditional countdown logic.
* Explicitly prohibited Gemini from inventing a character discovering price, consulting an agent, booking, arriving, or otherwise moving through a timeline absent from the article.

### Files changed
* `staging/blogcore-live-dynamic-storyboard.py` — global Reel architecture and visual-planning prompts; relaxed heading-by-heading coverage so the model can select the genuinely important source insights.
* `staging/run_reel_grid.py` — aligns review-grid instructions with the no-invented-timeline rule.

### Checks run
* Python compilation and deployed Flask health check.

### Risks / TODO
* The previously generated SoloCruz planning artifact used the deprecated contract and must not be used for media generation. Generate a new text-only scenario and show its full scene plan before creating assets.

## 2026-08-10 — Add source-grounded pre-production Reel photo-grid gate

### Summary
* Added a text-only review gate that plans each Reel scene's base frame and its source-evidenced visual components before any image, voice, music, or video request.
* Rebuilt the SoloCruz grid from scratch after rejecting the prior symbolic-prop plan. The accepted review artifact contains 7 scenes and 15 planned components; media generation was not run.

### Files changed
* `staging/blogcore-live-dynamic-storyboard.py` — validates Reel component source evidence and rejects symbolic or article-unmentioned standalone objects during production planning.
* `staging/run_reel_grid.py` — local/VPS text-only review utility for the SoloCruz source article; it does not create media.

### Decisions
* A source quote is mandatory for every independently generated Reel component. Objects may not be invented merely to visualize an abstract cost, risk, or choice.

### Checks run
* Python compilation for the Blog Core runtime and planning utility.
* Deployed runtime compiled successfully; `blog-yas-core` health endpoint returned `ok`.
* Confirmed the accepted grid is 7 scenes / 15 components and that no new image, audio, or video artifact was created during this planning task.

### Risks / TODO
* The grid is an approval artifact only. Do not start media generation until its scene plan is reviewed.

## 2026-08-10 — Make Gemini plan 30-second Reel scenarios before media production

### Summary

* Reworked the universal Reel planning contract so Gemini receives a 30-second duration target and independently chooses 6-8 causal screens rather than mapping every article heading to a screen.
* Required 2-4 semantic elements per screen, source-section grouping, an explicit screen-count rationale, and a text-only three-step plan before any visual or audio generation.
* Ran the text-only plan against the existing SoloCruz article. Gemini produced a 7-screen, 30-second production plan with 7 stage backgrounds and 14 additional elements, for 21 planned image generations. No image, voice, music, video, or social publication was created.

### Files changed

* `app.py` — duration-aware Gemini storyboard architecture, scene grouping, element IDs, production-plan validation, and clearer retry feedback.
* `docs/PROJECT_MEMORY.md` — records the durable short-form planning and no-media-before-plan rule.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py` locally and on VPS.
* Restarted `blog-yas-core`; `/health` returned `ok`.
* Verified `MASKED_LAYER_REEL_ENABLED=0` and confirmed the text-plan directory contains JSON only, with no newly generated media files.

### Risks / TODO

* The first saved SoloCruz plan is a planning artifact only and must be reviewed before media is enabled. Continue strengthening the model's visual-story quality gates if a future approved plan still uses generic or physically dependent components.

## 2026-08-10 — Add whole-scene camera work and registered-layer production gates

### Summary

* Added varied whole-scene camera moves (`dolly`, `tracking`, `follow`, `crane`, `orbit`) and varied layer reveals to the active Instagram Reel renderer.
* Replaced the rejected master-extraction assumption with separately generated, background-referenced full-canvas layers and strict stage-by-stage visual validation.
* Added scene-wide spatial planning, occupied-box checks, registration guides, production resume metadata preservation, and source-level rejection of fragile handheld/tabletop layers.
* Ran the real SoloCruz Reel record `32` only; no standalone test asset and no publication. Generation remains stopped in `ERROR` because Gemini did not reliably honor exact layer registration and produced matte/scale/contact artifacts.

### Files changed

* `app.py` — v6 storyboard, spatial planning, registration references, layer extraction/validation, resume behavior, and camera requirements.
* `reel_renderer.py` — full-canvas layer reveals and identical whole-scene camera transforms.
* `AGENTS.md` — current layer/camera architecture and forbidden fallback rules.
* `docs/PROJECT_MEMORY.md` — durable v6 architecture, current blocker, and deprecated v5 assumption.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Do not auto-position or rescale a generated layer when Gemini ignores registration; stop before publication.
* Camera movement always transforms the assembled scene and must include purposeful approach/withdrawal plus lateral movement.
* Preserve accepted production stages and their spatial/validation metadata across retries.

### Checks run

* `python3 -m py_compile app.py reel_renderer.py` locally and on the VPS.
* Restarted `blog-yas-core`; `/health` returned HTTP 200.
* Verified storyboard camera sequences include dolly, tracking/follow, crane and orbit moves with no adjacent repetition.
* Inspected real generated source layers and validator failures for clipping, floating objects, matte artifacts and overlap.

### Risks / TODO

* `social_posts.id=32` is intentionally unpublished and remains `ERROR` until the configured image model can produce spatially registered full-canvas layers without post-generation repositioning.

## 2026-08-09 — Build the real SoloCruz master-derived Reel v5

### Summary

* Built the requested real SoloCruz Reel directly from its existing article, narration, and active brand soundtrack; no separate test/demo asset was created and nothing was published.
* Replaced independent cutout placement with three coherent production masters decomposed into nine spatially registered full-canvas layers, then rendered seven causal story scenes with varied reveals and whole-scene camera work.
* Preserved and resumed valid master frames after downstream validation failures instead of regenerating accepted art.

### Files changed

* `app.py` — supports multiple image references for continuity, strengthens close-foreground production framing, and keeps the registered master contract.
* `registered_scene.py` — uses strict mask-overlap validation, coherent whole-plate empty bases, registered-union reconstruction checks, and production resume-compatible manifests.
* `registered_reel_renderer.py` — renders varied registered-layer reveals, whole-scene camera motion, kinetic type, narration, and continuous ducked brand music.
* `generate_registered_reel_v5.py` — orchestrates and resumes the three real production stages, renders the final Reel, updates the existing post in place, and leaves it as an unpublished draft.
* `AGENTS.md` — forbids unrequested standalone test/proof/demo generations and requires retries to repair the real production artifact.
* `docs/PROJECT_MEMORY.md` — records the final v5 architecture, production result, validation, and remaining generic integration boundary.
* `docs/CHANGELOG_AI.md` — records this task.

### Decisions

* Valid visual masters survive downstream segmentation, analysis, or transient model failures; only the invalid production stage is repaired.
* Generated removal imagery is one coherent base photograph, not a source of separately recolored patches.
* The old independent-cutout Reel path remains blocked and is not a fallback for v5.

### Checks run

* Compiled `app.py`, `registered_scene.py`, `registered_reel_renderer.py`, and `generate_registered_reel_v5.py` locally and on VPS.
* Visually inspected all three master scenes and a 12-frame final contact sheet.
* Verified all three manifests have `overlapPixels: 0` and `reconstructionMae: 0.0`.
* Verified final media: 33.46 seconds, 1080x1920 H.264 at 24 fps, stereo AAC at 48 kHz; `silencedetect` found no silent interval.
* Verified the review page and MP4 return HTTP 200, the social post is `DRAFT`, and no Zernio/Instagram publish action ran.
* Restarted `blog-yas-core`; local `/health` returned `ok`.

### Risks / TODO

* Dashboard Reel generation is not yet generically switched to v5 for every new task. Wire the ordinary queue to the registered production orchestrator before removing the old gate.
* Generated master continuity is visually strong but nondeterministic; retain stage-by-stage visual gates and production resume behavior.

## 2026-08-09 — Build and verify a non-overlapping master-derived scene proof

### Summary

* Replaced the proof path's independent-cutout composition with one integrated master photograph decomposed into spatially registered, full-canvas layers.
* Added hard scale, overlap, physical-grounding, continuous-photo, reconstruction, and clean-base validation.
* Produced one review-only SoloCruz proof with a large person and two separate scene elements. No Reel or social post was published.

### Files changed

* `app.py` — adds constrained scene planning, integrated master/removal generation, multimodal layout validation, per-component zones, text-model fallback, and an isolated registered-scene worker call.
* `registered_scene.py` — adds SAM-based full-canvas extraction, non-overlap and mobile-scale validation, per-layer empty-plate selection, exact reconstruction checks, and the proof renderer/CLI.
* `docs/PROJECT_MEMORY.md` — records the accepted architecture, measured proof, rejected failure modes, and remaining full-Reel gate.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* A 9:16 proof uses three large readable components rather than overcrowding four elements and shrinking or overlapping them.
* Empty-base sources are selected per layer; a single removal image cannot be trusted to remove every component or preserve every surface.
* SAM runs outside Flask so segmentation memory is reclaimed after every scene.
* Full-Reel generation remains blocked pending explicit review approval of the one-scene v5 proof.

### Checks run

* Compiled `app.py`, `registered_scene.py`, and `reel_renderer.py` locally and on VPS.
* Verified `gemini-3.1-flash-lite` structured JSON fallback after the configured primary returned quota errors.
* Rejected generated candidates for a person below the mobile threshold, overlapping component boxes, a floating support, and visible panel seams.
* Accepted proof metrics: person height 70.6%, person area 19.5%, overlap 0, reconstruction MAE 0.0; 10.0-second H.264 proof rendered successfully.
* Inspected master, empty base, all reveal stages, and a four-frame contact sheet; public review endpoint returns HTTP 200.
* Restarted `blog-yas-core`; `/health` returned `ok`. Confirmed no new SoloCruz social-post record was created and the full-Reel approval flag is absent.

### Risks / TODO

* The accepted proof validates one scene only. Do not enable the full-Reel gate until the operator approves this visual result.
* Generated masters remain nondeterministic; hard visual validators must stay active and reject bad scale, overlap, grounding, or panel seams rather than relaxing constraints.

## 2026-08-09 — Record the non-substitution rule for layered visual work

### Summary

* Added a mandatory project rule forbidding architectural substitution for the sake of smaller changes, faster completion, or technically valid output.
* Defined a real layered storyboard as one master composition decomposed into spatially registered full-canvas layers.
* Marked the existing independent-cutout Reel compositor as rejected and blocked further full-Reel generation until one production-quality layered scene passes visual review.

### Files changed

* `AGENTS.md` — adds task-fidelity, acceptance-criteria, visual-verification, and minimal-production-slice requirements for future Codex tasks.
* `docs/PROJECT_MEMORY.md` — records the durable layered-scene definition, rejected approach, current limitation, and required production gate.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Existing code preservation is never a reason to reinterpret the requested product behavior.
* For storyboards, independently generated cutouts cannot be treated as parts of one photograph, regardless of prompt quality.
* No additional expensive Reel batch should be generated before the master-frame decomposition proof is accepted.

### Checks run

* Reviewed the current Reel generation and compositor architecture against the clarified spatial-layer contract.
* Verified that the current pipeline still uses independently generated foreground assets, alpha extraction, and automatic placement, so it is correctly marked non-compliant rather than approved.

### Risks / TODO

* Replace the current cutout compositor with a master-scene decomposition workflow before producing another complete Reel.

## 2026-08-09 — Build evolving Reel scenes with continuous background music

### Summary

* Reworked the universal Instagram Reel factory from a repeated-subject sequence into a three-stage, seven-scene visual story. Each stage reuses a clean location plate while related foreground layers develop the moment.
* Changed protagonist continuity from raw asset reuse to identity-reference guidance: later appearances preserve the person but request a fresh pose, action, expression, and framing. The validator limits protagonist use to three to five scenes and rejects repeated actions.
* Kept the Lyria soundtrack playing throughout the complete Reel at a low level, with ducking under speech. Voice clips retain real-WAV sequential timing, preventing overlap.
* Regenerated SoloCruz Reel draft `#32` only. It remains unpublished.

### Files changed

* `app.py` — defines the staged storyboard contract, validates causal role-bound layers and non-repeating performances, caches one base plate per stage, supplies identity references only for later protagonist renders, and uses a Gemini-compatible structured-output schema.
* `reel_renderer.py` — gives layer roles directed placement/motion, composites kinetic copy after scene layers, and mixes continuous ducked Lyria audio with sequential speech.
* `docs/PROJECT_MEMORY.md` — records the v4 Reel visual, audio, validation, and recovery rules and marks v2 behavior deprecated.
* `docs/INTEGRATIONS.md` — updates the Lyria mix contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* A repeated identity is not a repeated performance: the renderer must receive a newly generated protagonist layer for each planned appearance.
* Stage backgrounds must be clean plates; foreground subjects, evidence, and environmental changes are composed as purpose-bound layers rather than being regenerated as unrelated full photographs.
* The Reel-specific JSON path has no JSON-repair pass. Unsupported numeric schema restrictions were moved to deterministic validation after a supported structured response is received.

### Checks run

* `python3 -m py_compile app.py scheduler.py reel_renderer.py` passed on VPS; `blog-yas-core` and `blog-yas-core-scheduler` restarted and `/health` returned `ok`.
* Tested the exact Gemini storyboard schema against the configured text model before queuing the production run.
* Ran normal scheduler regeneration for SoloCruz `social_posts.id=32`; it completed as `DRAFT` with three stage backgrounds, fourteen foreground assets, and seven TTS WAV clips.
* Verified final MP4 with `ffprobe`: 33.46 seconds, H.264 video, AAC 48 kHz stereo audio. `silencedetect` found no silent interval. Inspected a nine-frame contact sheet for staged scene continuity, varied protagonist actions, and plaque-free type.

### Risks / TODO

* The identity-reference prompt improves consistency but cannot create actual live action from stills; review remains required before publication.
* Generated foregrounds are independently alpha-extracted, so the final reviewer must still reject any image-model asset whose perspective or physical interaction is implausible.

## 2026-08-09 — Restore Reel narration and story-first composition

### Summary

* Regenerated SoloCruz Reel draft `#32` in the normal Blog Core factory after correcting the render and storyboard contracts. It remains a reviewable `DRAFT` and was not published.
* Eliminated two-voice collisions: scene duration now follows the real WAV duration, and the active vocal Lyria soundtrack is muted for the complete duration of every narration clip instead of only being ducked.
* Replaced decorative scene design with a continuity-anchored narrative: one recurring protagonist, a story-evidence layer per scene, composition fields, large word-revealed copy without a black text plaque, and no generic paths, icons, keys, compasses, coins, or fake UI.

### Files changed

* `app.py` — validates the causal Reel storyboard contract, reuses a single recurring-subject asset across scenes, uses concise scene narration, and adds safe in-place regeneration for unpublished Reel drafts.
* `reel_renderer.py` — calculates scene length from generated speech, creates narrator-exclusive music windows, and renders composition-driven story layers and plaque-free kinetic type.
* `docs/PROJECT_MEMORY.md` — records the current audio, storyboard, and regeneration rules and marks the superseded baseline.
* `docs/INTEGRATIONS.md` — documents the Lyria narrator-exclusive mix contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Retain the existing active SoloCruz Lyria track and do not generate a replacement. It is used only in gaps between voice clips.
* A real-story asset is preferable to a generic decorative motion layer. The image model receives the real logo only when the scene explicitly needs it; the renderer never manually stamps it onto frames.

### Checks run

* `python3 -m py_compile app.py scheduler.py reel_renderer.py` passed; both PM2 processes restarted successfully and `/health` returned `ok`.
* Exercised the production regeneration route for `social_posts.id=32`; all seven scene assets and TTS clips completed through the normal scheduler and the row returned to `DRAFT`.
* Verified output with `ffprobe`: 31.5 seconds, 1080x1920 H.264 video and 48 kHz stereo AAC audio.
* Inspected an eight-frame contact sheet. It contains no black text plaque or legacy decorative props; the recurring traveler and causal cruise-choice story are present across the new scenes.

### Risks / TODO

* Image generation can still introduce incidental text inside a generated document/sign if a storyboard requests a literal label. Prompts should prefer visual evidence over model-rendered copy where legibility matters.
* Review and explicit publish remain required; this task did not send the Reel to Zernio or Instagram.

## 2026-08-09 — Fix queued Reel foreground extraction

### Summary

* Fixed the production Reel worker failure that stopped queued renders at the first foreground extraction because Pillow's `Image` symbol was not imported by `app.py`.
* The normal Blog Core Reel task is retried after deployment; no detached renderer workaround or social publication is used.

### Files changed

* `app.py` — imports Pillow `Image` for the shared Reel alpha-extraction helper.
* `docs/PROJECT_MEMORY.md` — records the worker dependency and recovery boundary.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Preserve production-path behavior: queued Reel assets must be generated and retried through Blog Core so status, active soundtrack use, review, and later publishing remain auditable in one place.

### Checks run

* `python3 -m py_compile app.py scheduler.py reel_renderer.py` passed.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; `/health` returned `ok`.
* Ran an end-to-end normal Blog Core queue/review flow from the published SoloCruz article. The first attempt (`social_posts.id=31`) retained its audit error; the retry (`id=32`) completed as a `DRAFT` without a social publish.
* Verified the final file: 30.0 seconds, 1080x1920 H.264 video plus 48 kHz stereo AAC. The job payload records the active SoloCruz Lyria track, with the configured background mix and narration ducking.

### Risks / TODO

* `rembg` extraction can still fail for a model response without a viable foreground; that error is reported on the Reel row and is distinct from this import defect.

## 2026-08-09 — Add Gemini Lyria brand soundtracks for Reel production

### Summary

* Added a per-site brand soundtrack library to Blog Core and integrated its active track into future Instagram Reel renders.
* Added a 30-second Lyria Clip generation flow with a review state, editable creative direction/vocal hook, browser audio preview, and explicit active-track selection.
* Generated and activated one original SoloCruz soundtrack: a 30.72-second stereo MP3 with a sparse SoloCruz vocal hook. It was not published as a Reel or social post.

### Files changed

* `app.py` — adds the `reel_music_tracks` schema, Lyria API client, site-level soundtrack lifecycle, media endpoint, Distribution UI, and active-track selection for Reel renders.
* `reel_renderer.py` — mixes an active track below narration using fades, sidechain ducking, loudness control, and 48 kHz stereo AAC output.
* `scheduler.py` — serializes queued Lyria soundtrack generation before Reel rendering work.
* `docs/PROJECT_MEMORY.md` — records the durable music-generation, review, and mixing contract.
* `docs/INTEGRATIONS.md` — records the Gemini Lyria integration boundary.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Use `lyria-3-clip-preview` for the intended cheap fixed-length music asset rather than an interactive/streaming Lyria workflow or an unlicensed music source.
* Do not imitate famous Italian songs or a specific musical. The prompt asks for an original Mediterranean cinematic travel-pop composition and only a sparse brand refrain.
* A soundtrack is applied only after it is made active for its site, and it affects future Reel renders only.

### Checks run

* `python3 -m py_compile app.py scheduler.py reel_renderer.py` passed.
* Rendered a local video/audio smoke test with narration and an MP3 bed; output is H.264 plus 48 kHz stereo AAC and reports `musicApplied=true`.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; health endpoint returned `ok` and the new SQLite table exists.
* The scheduler successfully generated the SoloCruz track using `lyria-3-clip-preview`; verified MP3, stereo 44.1 kHz source, duration 30.719958 seconds, public review asset endpoint, returned lyric timing, and active-track state.

### Risks / TODO

* Lyria is Preview and requires a paid Gemini API tier. Pricing, rate limits, output behavior, and terms must be checked when the model changes.
* The current brand track is intentionally mixed only beneath future Reels. Music/SFX selection for any other production format remains out of scope.

## 2026-08-09 — Add native layered Instagram Reel production to Blog Core

### Summary

* Added a native Blog Core Reel factory that converts an existing content job into a reviewable vertical video rather than creating a detached one-off media pack.
* Reels use seven planned scenes, Gemini storyboard/image/TTS generation, alpha extraction for intended foreground assets, and a Pillow/ffmpeg compositor with denser independent motion and purposeful camera movement.
* Added dedicated Reel review, manual publishing, Zernio Reel payloads, and an optional per-site Reel cadence that is independent from standard Instagram carousel scheduling.

### Files changed

* `app.py` — adds Reel queueing, generation, preview, status polling, review/publish actions, isolated asset type, cadence settings, and Zernio video publishing.
* `reel_renderer.py` — new programmatic 1080x1920 H.264/AAC layer compositor with animated camera, foreground, text, and editorial-path layers.
* `scheduler.py` — processes one queued Reel render at a time and runs the optional due-Reel publisher.
* `requirements.txt` — adds `rembg[cpu]` for planned foreground alpha extraction.
* `docs/PROJECT_MEMORY.md` — records the durable Reel production and publishing contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Store Reels as `instagram_reel` social assets, not as standard Instagram posts, so carousel and Reel queues, previews, and cadence cannot collide.
* Pass the real site logo to Gemini only where the storyboard says a scene needs it; never overlay it through Python and never force it into every scene.
* Keep automatic Reel publishing disabled by default. Rendered assets become DRAFTs for review; social publishing requires either the dedicated manual action or an explicitly enabled Reel cadence.
* Do not add automatic music or SFX until an approved licensed media source is configured.

### Checks run

* `python3 -m py_compile app.py scheduler.py reel_renderer.py` passed.
* Installed and imported `rembg 2.0.69` in the VPS application virtualenv.
* Rendered a local 1080x1920 H.264/AAC smoke video through the new compositor; no Gemini, source-site, or social API call was made.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; `http://127.0.0.1:3299/health` returned `ok`.
* Verified the SQLite migration includes `social_posts.asset_type`, the SoloCruz dashboard renders the Reel controls, and no Reel was generated or published during this implementation task.

### Risks / TODO

* The first real foreground extraction downloads the rembg model into ignored runtime cache, and every real Reel consumes Gemini image/TTS usage.
* A licensed music/SFX provider, selection rules, and mix policy are still required before automatic sound design can be enabled.
* Full production generation and Zernio delivery have not been invoked in this task to avoid creating paid media or publishing without explicit approval.

## 2026-08-09 — Audit the SoloCruz Reel API spend

### Summary

* Calculated the current production Reel cost from saved Gemini image token metadata and final generated TTS duration.
* Separately reported the current usable v3 render and the historical discarded comparison/v1/replaced-narration spend so production cost is not confused with experimentation cost.

### Files changed

* `docs/PROJECT_MEMORY.md` — records current-render and total-development cost figures.
* `docs/CHANGELOG_AI.md` — this audited cost record.

### Checks run

* Parsed the 15-asset production batch: 8,846 prompt tokens, 5,479 non-image candidate tokens, and 16,800 image tokens.
* Parsed the eight-image replaced v1 batch and reconciled prior recorded comparison-pack costs.
* Verified final TTS duration at 25.56 seconds; the Gemini rate uses 25 audio tokens per second.

### Risks / TODO

* These are API list-price estimates excluding tax and account-specific discounts. Final billed value may vary by the account's active plan.

## 2026-08-09 — Lock SoloCruz narration to the scene and increase foreground scale

### Summary

* Enlarged the existing people, luggage, and product-interface layers; added separate background camera moves for a more cinematic 9:16 result without regenerating any images.
* Replaced the continuous voiceover with seven independently generated Gemini TTS clips. Each clip begins at its scene and reads the on-screen hook for that scene, eliminating semantic drift between visuals and audio.
* Extended the edit to preserve natural speech pacing rather than trimming or speeding up narration.

### Files changed

* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/renders/solocruz-cabin-before-booking.mp4` — current 26.261333-second H.264/AAC render with synchronized scene voices.
* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/renders/voiceover/*.wav` — seven scene-bound Gemini TTS source clips.
* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/renders/solocruz-cabin-before-booking-contact-sheet-v3.jpg` — visual QA contact sheet.
* `docs/PROJECT_MEMORY.md` — records per-scene narration, visual-scale, camera, and licensed-audio rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Do not speed, cut, or allow voiceovers to overlap the next scene merely to preserve a target duration.
* Music and SFX must come from an approved licensed source; automatic assembly controls timing and mixing, not rights.

### Checks run

* Generated seven Gemini `gemini-3.1-flash-tts-preview` `Kore` WAV clips.
* TypeScript compile passed before rendering.
* Rendered and inspected the 1080x1920 H.264/AAC video; verified duration is 26.261333 seconds and that all seven WAV assets exist in runtime storage.

### Risks / TODO

* The final social audio bed and SFX plan need a chosen licensed provider before adding them.
* The Reel remains unpublished.

## 2026-08-09 — Refine the SoloCruz storyboard for mobile readability and narration

### Summary

* Reassembled the approved layer-first SoloCruz Reel using the exact existing 15 scene assets. No new Gemini image batch was run.
* Replaced small explanatory type with hook-scale scene copy and added directional drop shadows plus contact shadows to separate foreground people, objects, and luggage from their backgrounds.
* Generated a production English voiceover through Gemini native TTS and muxed it into the current Reel render.

### Files changed

* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/renders/solocruz-cabin-before-booking.mp4` — current 24.384-second 1080x1920 H.264/AAC production render.
* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/renders/solocruz-cabin-before-booking-voiceover.wav` — Gemini TTS source narration.
* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/renders/solocruz-cabin-before-booking-contact-sheet-v2.jpg` — nine-frame mobile-readability review sheet.
* `docs/PROJECT_MEMORY.md` — records the visual-depth and narrated-render contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Production storyboards keep a one-idea, large-type hierarchy per scene. Supporting copy is permitted only when it remains clearly readable at mobile-first 9:16 scale.
* Foreground visual separation requires both object and contact shadows.
* Use `gemini-3.1-flash-tts-preview` with a directed prebuilt voice for a native voice track when a custom voice is not explicitly available or approved.

### Checks run

* TypeScript compile passed before render.
* Rendered and verified the MP4 contains H.264 video and AAC audio; duration is 24.384 seconds.
* Generated and visually inspected the v2 contact sheet for type scale, scene continuity, and foreground separation.

### Risks / TODO

* The TTS service remains Preview, so its voice and API behavior need a per-release availability check.
* Social publication is intentionally not enabled by this media-rendering task.

## 2026-08-09 — Produce the SoloCruz layer-first animated storyboard

### Summary

* Created one production Gemini Batch request with 15 scene-bound assets for the approved 22-second SoloCruz narrative, rather than a visual-model comparison or a list of generic still photos.
* Generated seven background plates and eight dedicated foreground sources, then extracted all person/object foregrounds to PNG-alpha before assembly.
* Composed and visually inspected a 1080x1920 H.264 Reel using independent background, foreground, product-interface, typography, route-graphic, object, and real-brand layers. No Google Flow/Veo request, source-site change, content job, or social publication occurred.

### Files changed

* `data/video_storyboards/solocruz-cabin-before-booking-storyboard-20260809/` — ignored production asset sources, alpha layers, scene manifest, storyboard timeline, usage metadata, MP4 and contact sheet.
* `docs/PROJECT_MEMORY.md` — recorded the new layer-first asset contract and production render boundary.
* `docs/CHANGELOG_AI.md` — recorded the batch, renderer verification, and remaining publishing boundary.

### Decisions

* Gemini 3.1 Flash Lite Image is used once as the production image provider for this approved storyboard. It produces source plates, not fake rendered logos, text, or interface screens.
* A foreground source must use a solid matte and become a PNG-alpha layer before composition because Gemini image output does not supply transparent backgrounds.
* The real SoloCruz mark and `/cruises/` interface must remain source-derived assets inside the renderer.

### Checks run

* Google Batch finished `JOB_STATE_SUCCEEDED`: 15/15 assets, zero errors.
* Extracted eight PNG-alpha foreground layers.
* TypeScript compile passed.
* Rendered and visually inspected a 22.058667-second 1080x1920 H.264 MP4 (18,607,792 bytes) and generated a seven-scene contact sheet.

### Risks / TODO

* The Reel is not published and has no selected/licensed audio.
* A reusable Blog Core Reel UI, per-channel scheduling, review state, and publishing adapter remain future work; this task validates the production media contract only.

## 2026-08-09 — Generate the preliminary SoloCruz Reel v1 full-scene pack (replaced)

### Summary

- Generated eight reference-anchored 9:16 full-scene frames through Gemini Batch and combined them with the approved master traveller image into a nine-beat SoloCruz Reel still sequence.
- The pack is intended for the existing planned programmatic editorial-motion assembly, not Google Flow/Veo, alpha-cutout compositing, website publication, or social publication.
- Replaced: subsequent technical review found that full-scene stills do not fulfill the requested layer-first storyboard. The assets are not an approved production Reel sequence.

### Files changed

- `data/video_layer_tests/solocruz-reel-v1-20260809/` — ignored Reel v1 assets, Batch responses, usage metadata, and contact sheet.
- `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — records the production asset contract and this result.

### Checks run

- Batch job `JOB_STATE_SUCCEEDED`; all 8 requested frames returned with zero errors.
- Reviewed the complete nine-frame contact sheet for consistent traveller identity, wardrobe, setting, and narrative progression.

### Risks / TODO

- Programmatic MP4 assembly must use the layer-first scene contract. It may reuse individual photos as temporary slots, but must not treat this full-scene sequence as accepted final creative.

## 2026-08-09 — Compare Gemini Batch visual packs for SoloCruz Reels

### Summary

- Generated two matching, unpublished 13-image SoloCruz vertical travel packs through Gemini Batch API: `gemini-2.5-flash-image` and `gemini-3.1-flash-lite-image`.
- Saved each API response's usage metadata with the generated runtime-only images; no Blog Core job, source-factory job, website file, or social publication was created.

### Files changed

- `data/video_layer_tests/solocruz-reel-layer-compare-20260809/` — ignored test assets, API response metadata, and per-model usage ledgers.
- `docs/PROJECT_MEMORY.md` — records cost/format baseline and non-publication boundary.
- `docs/CHANGELOG_AI.md` — this task record.

### Decisions

- Do not switch the production image model merely from one comparison; use the measured visual/cost baseline for the next explicit Reel-assembly decision.

### Checks run

- Both Batch jobs reached `JOB_STATE_SUCCEEDED` with 13/13 images and zero response errors.
- Verified formats: 2.5 Flash Image PNG 768x1344; 3.1 Flash Lite Image JPEG 768x1376.
- Parsed every returned `usage_metadata` response and computed USD usage at the current official Gemini Batch rates.

### Risks / TODO

- The test establishes still-image quality only. Programmatic montage, timing, captions, music, and rendered Reel QA remain a separate implementation task.

## 2026-08-05 — Schedule the GEO Insights series every three days

### Summary

- Scheduled all 11 remaining queued GEO editorial blog tasks for native publication every 72 hours.
- The first task is `LLMs.txt: Useful Discovery File or SEO Myth?` at `2026-08-05T17:56:00Z`; the final scheduled Insight is due on `2026-09-04T17:56:00Z`.

### Files changed

- `docs/PROJECT_MEMORY.md` — records cadence, scope, scheduler behavior, and boundary.
- `docs/CHANGELOG_AI.md` — this task record.

### Decisions

- The schedule applies only to the 11 still-queued `blog` records for GEO site 16, never to commercial collections or already published pages.
- The native scheduler remains responsible for the two-step lifecycle: generate a due task, then publish its resulting draft on the next pass.

### Checks run

- Confirmed 11 matching queued GEO blog tasks before scheduling.
- Confirmed each task has an explicit timestamp exactly 72 hours after the previous task.
- Confirmed `blog-yas-core-scheduler` is online in PM2.

### Risks / TODO

- A model/provider failure leaves the due item visible as `ERROR`; the operator should fix or reschedule that one record rather than allowing the cadence to silently skip it.

## 2026-08-05 — Complete GEO collection inventory from approved demand research

### Summary

- Added the three remaining non-duplicative GEO page contracts needed to give every active commercial collection at least four pages.
- The additions are based only on the approved AI-visibility demand map: AI Visibility Checker, AI Readiness Checker/GEO Audit, and AI Citation Readiness for ChatGPT and Google AI Overviews.
- All three records are queued for native generation and manual publication; no synthetic checker result or automated publication is created.

### Files changed

- `deploy/seed_geo_collection_minimum.py` — idempotently queues the three site-16 page briefs by canonical path.
- `deploy/approve_geo_collection_minimum.py` — guarded explicit approval and publication of the reviewed three-page release.
- `docs/PROJECT_MEMORY.md` — records collection threshold, intent boundaries, and manual-publish rule.
- `docs/SEO_MEMORY.md` — records the demand-map basis and anti-cannibalisation constraints.
- `docs/CHANGELOG_AI.md` — this task record.

### Decisions

- Visibility checking, site readiness, and citation-readiness workflow are distinct user intents and must remain distinct even though all relate to AI-search visibility.
- Do not fill taxonomy gaps with competitor-analysis speculation or overlapping GEO/AEO/LLMO definition pages that are not in the approved priority map.

### Checks run

- `python3 -m py_compile deploy/seed_geo_collection_minimum.py` passed.
- The seed script was run against a copied production database and created exactly three `QUEUED` records with canonical `/tools/` and `/use-cases/` paths.
- Re-running the seed refreshes only still-queued contracts; generated drafts and published records retain their generated validation data.
- Generated drafts passed the native content contract: 1,843-1,959 words, 7-8 sections, hero plus three inline images, five FAQ items, four contextual links, and three Recommended next links each.
- All three native previews returned `200` with `noindex, nofollow` before publication.
- The guarded publish script recorded editorial, product, SEO, and browser QA gates, then published all three records successfully.
- The three final canonical URLs, `/tools/`, and `/use-cases/` return `200` after trailing-slash normalization. The sitemap and database both report six Solutions, four Tools, and four Use cases.

### Risks / TODO

- Each drafted typed page still requires editorial, product, SEO, and browser QA approval before manual publication.

## 2026-08-05 — Split GEO commercial pages into Solutions, Tools, and Use cases

### Summary

- Extended Blog Core native routing with `solution` and `tool` page types alongside `use_case`.
- Migrated all 11 published GEO commercial records: six Solutions, two Tools, and three Use cases.
- Added a reproducible migration that updates both the Blog Core publication contract and GEO's native published records.

### Files changed

- `app.py` — native type aliases, route prefixes, discovery/queue normalization, typed generation contracts, and delegated-factory money-page recognition.
- `deploy/migrate_geo_taxonomy.py` — idempotent GEO store/database taxonomy migration.
- GEO native content store — canonical type and target-path updates for the 11 published records.
- `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — taxonomy and migration contract.

### Checks run

- `python3 -m py_compile app.py deploy/migrate_geo_taxonomy.py` passed.
- Blog Core restarted and `/health` returned OK.
- Migration reported 11 database updates and 6 native-store file moves/updates.

### Risks / TODO

- `comparisons` and `services` remain page-intent labels, not hubs. Create a dedicated collection only once it has sufficient non-duplicative inventory and an approved route migration.

## 2026-08-05 — Publish GEO traffic-loss and AI SEO service pages

### Summary

- Generated and published the two remaining distinct commercial GEO pages: an evidence-led AI-search traffic-loss audit/recovery page and an AI SEO services page.
- Kept the existing `/use-cases/` route contract. The public collection now contains 11 pages, with the new entries on page one and five existing entries on page two.

### Files changed

- GEO native content store — two reviewed, published `seo_money_page` records with hero and inline assets.
- `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable scope, editorial boundaries, and validation lesson.

### Decisions

- Traffic-loss content must not assert that AI search caused a decline without evidence.
- AI SEO service content must describe verifiable work and limitations, never guarantee rankings or citations.
- Typed commercial briefs need at least six explicit decision sections so generation satisfies the existing structural validator without relaxing it.

### Checks run

- Both public URLs, `/use-cases/`, and `/use-cases/?page=2` return HTTP 200.
- Both new URLs are in `https://geo.yas.ooo/sitemap.xml`; each page exposes TOC, FAQ, hero, and inline generated images.
- Both hero assets return HTTP 200 with `image/png` content type.

### Risks / TODO

- The approved remaining GEO Insights stay queued and unpublished.
- Future `/comparisons` or `/tools` taxonomy requires a separate migration and redirects; these pages correctly remain in the current `/use-cases/` collection.

## 2026-08-05 — Publish the initial GEO Insights collection

### Summary

- Generated and published four foundational GEO editorial posts to make the native `/blog/` hub operational: citations, robots.txt, schema, and the AI-read/citation gap.
- Verified each generated draft includes the native hero asset, then confirmed the GEO index exposes the four entries after renderer deployment.

### Files changed

- Native GEO content store — four published `blog` records and associated generated image assets.
- `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the editorial-release and card-rendering contract.

### Checks run

- Every article URL and `https://geo.yas.ooo/blog` return HTTP 200.
- All four titles appear on the public hub; all four hero assets return HTTP 200 with an image content type.

### Risks / TODO

- Eleven planned GEO Insights remain queued and unpublished.
- Current money pages remain under `/use-cases/`; a separate approved taxonomy migration is needed before creating `/comparisons` or `/tools` routes and redirects.

## 2026-08-05 — Publish the GEO SEO money-page release

### Summary

- Generated and published all 9 approved GEO SEO money pages through the native content store.
- Kept the 15 GEO blog tasks queued and unpublished.
- Corrected two published records whose model-returned slugs diverged from their fixed canonical paths.

### Files changed

- `app.py` — typed content now always retains its queued canonical slug during generation.
- GEO native published records — 9 reviewed money pages below `/use-cases/`.
- `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the release and canonical-path rule.

### Decisions

- Operator approval recorded all four publication gates for this specific GEO money-page release.
- Generated prose can change, but typed pages may never change their canonical path.

### Checks run

- All 9 public money-page URLs and the `/use-cases` hub return HTTP 200.
- GEO sitemap contains exactly 9 use-case URLs; the native store contains exactly 9 published use-case records.
- Blog Core compilation, PM2 restart, and health check passed after the slug fix.

### Risks / TODO

- The separate 15-post editorial series remains queued and requires a later explicit generation/publishing decision.

## 2026-08-05 — Make service relevance explicit without making articles promotional

### Summary

- Strengthened the universal article prompt for typed commercial pages.
- Requeued the first GEO money-page draft under this rule; it remains unpublished.

### Files changed

- `app.py` — requires one evidence-led product decision section and explicitly forbids in-article CTA buttons and unsupported sales claims.
- `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the editorial rule.

### Checks run

- Python compilation, PM2 restart, and health check passed.

### Risks / TODO

- Generated drafts still require human product and factual review before publication.

## 2026-08-05 — Queue and generate the first YAS AI Visibility money page

### Summary

- Queued the approved GEO content plan: 9 SEO money pages and 15 supporting blog posts.
- Added controlled briefs to all queued GEO money pages and generated the first page as a reviewable native draft. No GEO content was published.
- Added a noindex native product preview route for GEO drafts.

### Files changed

- `app.py` — preserves supplied `pageBrief` data when queueing ideas and validates root-path internal links consistently through native rendering and draft validation.
- `docs/PROJECT_MEMORY.md` — records the durable brief, navigation, and native-preview contract.
- `docs/CHANGELOG_AI.md` — records this work.

### Decisions

- SEO money-page generation requires a structured brief; Blog Core must not relax draft requirements when an external planning flow has supplied only a title.
- The first GEO page remains `DRAFT` and is reviewable at the GEO product host. Publication approvals remain false until human editorial, product, SEO, and browser review.

### Checks run

- `python3 -m py_compile app.py`, PM2 restart, and `/health` passed.
- Generated draft has 3 inline image assets, TOC, 6 FAQ items, 4 contextual internal links, and 3 Recommended next links.
- Browser check confirmed the native noindex preview route and hero asset load successfully.

### Risks / TODO

- Review the first draft for product-specific factual claims before enabling publication approvals.
- The remaining GEO tasks remain queued and will not generate or publish automatically.

## 2026-08-05 — Register YAS AI Visibility as an independent native product

### Summary

- Registered `geo.yas.ooo` for an independent Blog Core content lifecycle without generating or publishing any content.
- Native product cards now suppress design-scan, preview-build, and static-install actions that do not apply to an application-owned content store.

### Files changed

- `app.py` — identifies native content-store products in the dashboard site card.
- `docs/PROJECT_MEMORY.md` — records GEO product, routing, publishing, and isolation boundaries.
- `docs/CHANGELOG_AI.md` — records this task.

### Decisions

- GEO has its own content context, topic strategy, store, sitemap, and public paths even while its initial implementation shares the YAS Next.js runtime.
- Content remains manual-publish only; this registration creates no queue items and does not alter the public product content.

### Checks run

- Verified GEO native store exists and GEO public `/blog/`, `/use-cases/`, `sitemap.xml`, and `robots.txt` return successfully after source deployment.

### Risks / TODO

- The first GEO blog or SEO money-page task still needs an operator-approved brief before any generation or publication.

## 2026-07-26 — Make Georivo money-page heroes distinct from first paint

### Summary

- Moved all three Georivo money-page heroes to same-origin Blog Core assets.
- Added per-page preload, background fallback, image position, and overlay treatment so the pages are visually distinct before and after image decoding.

### Files changed

- `deploy/georivo/app.py` — stable hero overrides, image preload metadata, and stylesheet cache bust.
- `deploy/georivo/georivo-blog.css` — page-specific hero imagery and treatments.
- `deploy/georivo/money-hero-*.webp` — three optimized thematic hero assets.
- `docs/PROJECT_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable delivery and release record.

### Decisions

- A unique image URL is not enough; first paint must also be page-specific.
- Hero images are delivered from the same Blog Core origin instead of mixing Blog Core and Sites asset hosts.

### Checks run

- Python compilation and service health passed.
- Production HTML exposes a matching preload and hero URL on all three pages.
- The strict money-page audit passed all 15 localized URLs with three distinct hero paths.
- Browser QA confirmed the three visually distinct hero compositions.

### Risks / TODO

- Browser cache is explicitly invalidated through stylesheet revision `20260726e`.

## 2026-07-25 — Register CabinJoin native money-page store

### Summary

- Added the CabinJoin site record as a multilingual native content-store target with a dedicated shared content root.
- No content draft or page was generated or published automatically.

### Decisions

- Blog Core owns the reviewable lifecycle for CabinJoin static money pages; CabinJoin owns its product shell and transactional facts.

### Checks run

- Confirmed the saved site mode, languages and content-root configuration through the local Blog Core API/database.

### Risks / TODO

- Create, review and explicitly publish the first CabinJoin SEO money-page draft; no page has been auto-published.

This file is updated by Codex after every task.

## 2026-08-09 — Select LinkedIn Company Pages in Blog Core

### Summary

* Replaced manual per-site LinkedIn access-token and author-URN entry with OAuth-derived publishing identities.
* OAuth now requests organization read access, retrieves eligible approved pages, and exposes a personal-profile or Company-Page selector.
* Connection testing now verifies the selected Company Page role instead of only proving that a personal token exists.

### Files changed

* `app.py` — LinkedIn organization lookup, identity selector API/UI, OAuth scope, and Company Page validation.
* `docs/PROJECT_MEMORY.md` — durable LinkedIn Company Page ownership and permission contract.
* `docs/CHANGELOG_AI.md` — task record.

### Risks / TODO

* LinkedIn must approve the app's organization permissions. If it does not, the OAuth member still connects personally but no Company Pages can be returned for selection.

## 2026-07-25 — Publish Georivo SEO money pages through live Blog Core

## Summary

* Added dedicated Blog Core rendering and native records for How it works, Coverage, and Pricing in EN/DE/ES/FR/RU.
* Reused the live Georivo header, footer, and stylesheet while giving every page a distinct thematic hero and product-specific layout.
* Connected Coverage to the real production coverage endpoint and Pricing to the existing account-aware Stripe Checkout flow.
* Added Nginx ownership routes, composite sitemap entries, deterministic publishing, and a public contract audit.

## Files changed

* `deploy/georivo/app.py` — direct money-page routes, rendering, schema, canonical/hreflang, and sitemap ownership.
* `deploy/georivo/seed_money_pages.py` — idempotent site-14 DB/native-store publication in five languages.
* `deploy/georivo/georivo-blog.css` — responsive namespaced product-page design.
* `deploy/georivo/georivo-blog-nav.js` — real coverage and Stripe interactions.
* `deploy/georivo/georivo.com.conf` — public root and locale-prefixed money-page routing.
* `deploy/georivo/audit_money_pages.py` — 15-URL SEO, chrome, hero, and action contract audit.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md` — durable ownership and release contract.

## Decisions

* Blog Core site 14 is the public owner of the three SEO money pages; the Sites-origin React copies are replaced for these paths.
* Shared source chrome remains the only public header/footer; money pages provide only their body.
* Coverage/payment outcomes remain real and fail honestly.

## Checks run

* Python compilation, JavaScript syntax check, and `git diff --check`.
* Seeded all three records into a copy of the production DB.
* Loopback audit passed all 15 language URLs before public Nginx cutover.
* Public audit passed all 15 language URLs after Nginx cutover.
* Playwright verified the shared source header/footer, unique loaded hero media, 1440 px and 390 px layouts, and no horizontal overflow.
* The Coverage form called the real production endpoint. Google currently returns a technical access denial, which the page reports as a technical error rather than inventing an unsupported-address result.

## Risks / TODO

* Restore valid Google Photorealistic 3D server access separately; the SEO page correctly exposes the current provider error.

## 2026-07-25 — Localize Georivo Guides and Blog navigation

### Summary

* Localized existing Guides and Blog menu entries in Georivo's reused source header/footer.
* Rewrote content-section links to the active locale instead of sending non-English readers to EN routes.
* Made the client-side Blog fallback locale-aware.

### Files changed

* `deploy/georivo/app.py` — localized existing native content anchors and their locale-prefixed paths.
* `deploy/georivo/georivo-blog-nav.js` — locale-aware Blog fallback label and URL.
* `docs/PROJECT_MEMORY.md` — recorded the durable native-navigation localization contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Native chrome reuse must localize existing Blog Core content links; checking only whether a link already exists is insufficient.

### Checks run

* Python and JavaScript syntax checks.
* Public Guides and Blog pages returned 200 for EN/DE/ES/FR/RU.
* Verified localized menu labels and locale-prefixed Guides/Blog URLs for all five languages.
* Browser-rendered the Guides hub with its hero and eight cards.
* Public content audit returned 19 expected, 19 found, 19 passed, 0 failed after the clean deployment.

### Risks / TODO

* None for this navigation change.

## 2026-07-25 — Add durable Georivo search-performance monitoring

### Summary

* Extended the operational Search Console job beyond sitemap submission.
* Added API-sourced current/previous complete 28-day performance totals, top-page reporting, and URL Inspection for Georivo's primary public URLs.
* Kept monitoring privacy-minimal by excluding search-query text and preserving honest empty-data states.

### Files changed

* `deploy/georivo/gsc_submit.py` — added Search Analytics and URL Inspection collection after successful sitemap read-back.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — documented the monitoring contract and operation.

### Decisions

* The comparison excludes today and yesterday because Search Console data can lag.
* Index-inspection failures are recorded per URL and do not falsify a successful sitemap submission.
* Only aggregate metrics and page URLs are stored; query strings are omitted.

### Checks run

* Python compilation.
* Live Search Console API execution through the Georivo VPS service account.
* Sitemap read-back, Search Analytics, and URL Inspection status-file validation.

### Risks / TODO

* Newly published URLs can remain `Discovered - currently not indexed` or unknown until Google chooses to crawl them.
* Performance rows require real impressions/clicks; the adapter reports an empty dataset honestly until traffic exists.

## 2026-07-25 — Submit Georivo sitemap to Search Console

### Summary

* Confirmed the verified `sc-domain:georivo.com` property in Search Console and submitted `https://georivo.com/sitemap.xml`.
* Confirmed the factory service account now has `siteFullUser` access.
* Re-ran the official API adapter successfully and read back the accepted sitemap record with zero errors and warnings.
* Re-ran the complete public content audit and service/timer health checks.

### Files changed

* `docs/PROJECT_MEMORY.md` — replaced the external-access blocker with the confirmed Search Console operating state.
* `docs/SEO_MEMORY.md` — recorded the accepted sitemap and pending initial Google processing.
* `docs/INTEGRATIONS.md` — recorded the verified service-account permission and official API result.
* `docs/GEORIVO_CONTENT_FACTORY_PLAN.md` — closed Search Console submission in the production checklist.
* `docs/CHANGELOG_AI.md` — logged this completion task.

### Decisions

* Search Console submission is complete only when the service-account API call succeeds and the submitted sitemap record can be read back.
* `isPending=true` immediately after submission means Google is processing the accepted sitemap; it is not a submission failure.

### Checks run

* Search Console UI confirmed the sitemap was submitted on 2026-07-25.
* Official Webmasters API reported `permissionLevel=siteFullUser`, `status=submitted`, `warnings=0`, `errors=0`, and `isPending=true`.
* Public content audit: 19 expected, 19 found, 19 passed, 0 failed.
* Verified `georivo-content-audit.timer` and `georivo-gsc-submit.timer` are enabled and active.
* Verified Blog Core and Georivo renderer health endpoints.

### Risks / TODO

* Google must complete its initial sitemap processing before discovered/indexed URL counts become meaningful.
* Query/page performance tracking and refresh decisions remain ongoing post-publication operations.

## 2026-07-25 — Automate Georivo Search Console submission retries

### Summary

* Added a durable Search Console adapter that validates the public sitemap, authenticates with the existing service account, checks property permissions, submits through the official API, and reads back the sitemap record.
* Added an atomic ignored status file with distinct `blocked`, `error`, and `submitted` states.
* Enabled a daily systemd retry so granting property access later does not require another deployment or manual command.

### Files changed

* `requirements.txt` — added pinned `google-auth` and `requests` runtime dependencies.
* `.gitignore` — ignored the server-only `keys/` directory.
* `deploy/georivo/gsc_submit.py` — official API check/submit adapter and atomic status reporting.
* `deploy/georivo/georivo-gsc-submit.service`, `deploy/georivo/georivo-gsc-submit.timer` — daily retry deployment.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/INTEGRATIONS.md`, `docs/GEORIVO_CONTENT_FACTORY_PLAN.md`, `docs/CHANGELOG_AI.md` — durable GSC behavior and blocker state.

### Decisions

* Missing property permission is a controlled temporary blocker (`75`), not a credential or application error.
* Search Console success is recorded only after API submission and read-back; a public sitemap or systemd success alone is insufficient.
* Credentials remain in ignored `keys/` with restrictive permissions.

### Checks run

* Compiled `gsc_submit.py`.
* Installed the pinned dependencies in the Blog Core virtualenv.
* Verified the script authenticates, validates the 122,943-byte public XML, hashes it, and records `blocked` because the service account is absent from `sc-domain:georivo.com`.
* Verified a missing credential produces `status=error` and exit code `1`.
* Enabled and ran `georivo-gsc-submit.timer`; the controlled `75` result is accepted and the next daily run is scheduled.

### Risks / TODO

* Property ownership/access is still external. The current Google account cannot access Georivo, so it cannot add the service account. The official submission will remain `blocked` until a verified owner grants `siteFullUser` or `siteOwner`.

## 2026-07-25 — Complete and publish the Georivo typed content plan

### Summary

* Finished the full approved Georivo factory rollout without reconnecting the site or changing its product application.
* Generated, validated, approved, and explicitly published 19 canonical typed pages: 8 Guides, 3 Templates, 4 Examples, and 4 Integration guides.
* Published EN plus DE/ES/FR/RU for every task and exposed all 95 language URLs through native routes and sitemap.
* Added a structured factual-editor pass, deterministic safety/navigation guarantees, and rejection of leaked model-control text.
* Added independent static/public audits, a 114-check browser QA gate, and a daily systemd audit timer.

### Files changed

* `app.py` — typed structured generation, factual editor, deterministic required-content restoration, strict validation, and model-control artifact rejection.
* `deploy/georivo/app.py` — native typed rendering, multilingual metadata, collection hubs, trust/CTA/schema blocks, asset URL handling, and current stylesheet cache version.
* `deploy/georivo/georivo-blog.css` — typed-page presentation, guide grouping, responsive tables, and safe wrapping for generated copy.
* `deploy/georivo/seed_content_plan.py` — the approved 19-page content tree and verified briefs.
* `deploy/georivo/run_content_plan.py` — bounded parallel generation runner.
* `deploy/georivo/audit_content_plan.py` — independent static and public contract audit, including model-artifact detection.
* `deploy/georivo/approve_and_publish_content_plan.py` — four-gate approval and explicit publication runner.
* `deploy/georivo/visual-test.js` — full browser matrix with decoded lazy-image verification.
* `deploy/georivo/georivo-content-audit.service`, `deploy/georivo/georivo-content-audit.timer` — daily production audit.
* `docs/GEORIVO_CONTENT_FACTORY_PLAN.md`, `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable rollout state and operational rules.

### Decisions

* A syntactically valid model response is still invalid if visible copy contains internal generation/control text.
* Publication requires editorial, product-fact, SEO, and browser QA gates; generation success alone is insufficient.
* Lazy images must be activated and decoded during browser QA rather than marked broken while outside the viewport.
* Search Console submission must remain reported as pending until property access exists and the API submission succeeds.

### Checks run

* Compiled Blog Core, Georivo renderer, and all deployment scripts.
* Restarted `blog-yas-core` and `georivo-blog`; both health endpoints passed.
* Regenerated the one draft rejected by the new model-artifact audit.
* Static draft audit: 19 expected, 19 passed, 0 failed.
* Browser QA: 114 checks, 19 pages, 0 failed pages.
* Public audit: 19 expected, 19 passed, 0 failed across 95 language URLs.
* Verified `/guides/`, `/templates/`, `/examples/`, and `/embed/` return 200 and are indexable.
* Verified the Guides hub on desktop/mobile with 8 loaded card images and zero horizontal overflow.
* Verified the sitemap contains 154 total URLs and all 95 expected typed URLs.
* Enabled and ran `georivo-content-audit.service`; first run exited `0/SUCCESS`.

### Risks / TODO

* Search Console is the only external blocker: the existing service account and current Google account have no access to a verified Georivo property. Grant access, then retry sitemap submission.
* Performance measurement and refresh decisions require post-publication Search Console data.

## 2026-07-24 — Expand Georivo's existing native content adapter

### Summary

* Extended the existing Georivo integration without reconnecting or reimporting the site.
* Added typed native content support for Guide, Template, Example, Integration guide, and Use case alongside Blog.
* Added base and localized routes for `/guides/`, `/templates/`, `/examples/`, `/embed/`, and `/use-cases/`.
* Preserved one canonical task with sequential localized child records and the existing explicit Generate, Preview, Publish workflow.
* Confirmed that no users, roles, permissions, or RBAC are required; workflow status, validation, explicit Publish, and logs remain the control model.

### Files changed

* `app.py` — preserve native content types, derive typed fallback paths, use collision-safe published filenames, and add type-specific generation instructions.
* `deploy/georivo/app.py` — typed collection/article routing, locale switching, canonical, hreflang, structured data, preview, and sitemap behavior.
* `deploy/georivo/georivo.com.conf` — proxy only the approved typed content routes and locale variants to the existing native renderer.
* `docs/GEORIVO_CONTENT_FACTORY_PLAN.md` — complete factory-only execution plan extracted from the Georivo specification.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/DEPLOYMENT.md` — durable typed-route, SEO, integration, deployment, and single-user workflow rules.

### Decisions

* Georivo remains existing Blog Core site 14; this change expands its adapter rather than creating another connection.
* Content type plus slug is the publication identity. Different collections may safely reuse a slug.
* Empty collection hubs are available but `noindex` and excluded from sitemap until their first explicit publication.
* Editorial author/reviewer data may be stored as trust metadata, but it does not create application roles.

### Checks run

* Compiled Blog Core, the shared chrome adapter, and the Georivo renderer.
* Passed a renderer contract fixture for all six content types across EN/DE/ES/FR/RU, including duplicate slugs, canonical, hreflang, preview noindex, redirects, and sitemap.
* Passed all six existing Georivo publication records through the new renderer in every available language.
* Verified live Blog Core and Georivo health endpoints and nginx configuration.
* Verified live `/blog/`, `/de/blog/`, `/guides/`, `/de/guides/`, `/templates/`, `/examples/`, and `/embed/` routes.
* Browser-checked the live responsive `/blog/` composition after route generalization; native header, hero, article grid, CTA, footer, and language selector remain intact.

### Risks / TODO

* No Guide, Template, Example, Integration guide, or Use case has been queued or published by this task. Empty hubs intentionally remain out of the sitemap.
* Typed generation currently shares the proven long-form structured article schema with type-specific instructions. Dedicated template/example/integration data schemas, verified source inventory, trust metadata, internal-link plans, and Recommended next remain later phases in `docs/GEORIVO_CONTENT_FACTORY_PLAN.md`.

## 2026-07-24 — Publish five additional Georivo articles

### Summary

* Explicitly published the five reviewed Georivo multilingual drafts through the native content-store publisher.
* Exposed each canonical article in EN, DE, ES, FR, and RU and added all variants to their localized blog indexes and the Georivo sitemap.
* Preserved the generated TOC, article structure, FAQ, table, lists, and one hero plus three inline images per article.

### Files changed

* `data/blog_core.sqlite3` — moved five Georivo tasks from `DRAFT` to `PUBLISHED` and recorded their canonical public URLs; runtime data remains ignored.
* `/var/www/georivo-blog/data/blog-core/published/*.json` — stored five multilingual native publication records; runtime data remains ignored.
* `docs/CHANGELOG_AI.md` — logged publication and public validation.

### Decisions

* No new architecture or product rule was introduced. This task executed the existing explicit Publish lifecycle for approved native content-store drafts.

### Checks run

* Verified all five database tasks are `PUBLISHED` with no errors.
* Verified all 25 public language URLs return HTTP 200, are indexable, have the correct per-language canonical, and expose EN/DE/ES/FR/RU plus `x-default` hreflang links.
* Verified all five localized blog indexes contain every newly published slug.
* Verified `https://georivo.com/sitemap.xml` contains all 25 article URLs.
* Verified each article exposes four generated article images and all 20 JPEG URLs return HTTP 200 with an image MIME type.

### Risks / TODO

* No publication errors remain. Editorial or social distribution is separate from this native article publication.

## 2026-07-24 — Generate five additional Georivo article drafts

### Summary

* Added five distinct Georivo editorial tasks covering off-plan location trust, useful interactive property maps, contextual digital twins, master-planned development phases, and walkability context.
* Generated every task through Blog Core as one canonical multilingual article with EN, DE, ES, FR, and RU variants.
* Left all five tasks in `DRAFT`; no article was published or added to the public Georivo blog index.

### Files changed

* `data/blog_core.sqlite3` — added five Georivo content jobs and their generated localization records; runtime data remains ignored.
* `/var/www/georivo-blog/data/blog-core/drafts/*.json` — stored five native multilingual draft payloads; runtime data remains ignored.
* `data/article_assets/14/*` — stored one hero and three inline JPEG assets for each draft; generated assets remain ignored.
* `docs/CHANGELOG_AI.md` — logged the generation and validation task.

### Decisions

* These articles remain reviewable drafts. Generation does not imply publication; an explicit Publish action is still required for each canonical task.
* One Georivo task continues to own all configured language variants rather than creating separate dashboard tasks per language.

### Checks run

* All five generation calls completed successfully and returned `DRAFT` with `en`, `de`, `es`, `fr`, and `ru`.
* Verified all five database records have DE/ES/FR/RU localization rows and matching native draft payload translations.
* Verified each draft has four generated JPEG assets, three inline figures, 7-8 editorial sections, a table, an ordered list, and six FAQ items.
* Verified all 25 language preview URLs return HTTP 200 and contain `noindex`, TOC markup, and images.
* Verified the five draft slugs are absent from the public `https://georivo.com/blog/` index.

### Risks / TODO

* The drafts require editorial review and explicit publication before they appear on Georivo or enter its public sitemap.

## 2026-07-24 — Use live source chrome globally and expose article TOC

### Summary

* Replaced Georivo's manually reproduced header/footer with the actual current header/footer fetched from the source homepage.
* Moved live source-chrome extraction into reusable `native_site_chrome.py` and connected Blog Core's hosted/CNAME renderer to the same adapter.
* Preserved each site's real account control, language-switcher markup, footer credits, navigation structure, and current stylesheet references; site-specific adapters add only the Blog route and current article-language URLs.
* Moved Georivo's generated TOC out of the article-body stream and placed it directly below article metadata, before the hero image.

### Files changed

* `native_site_chrome.py` — shared cached source header/footer and stylesheet extraction.
* `app.py` — hosted/CNAME blogs refresh source chrome from `homepage_url`, using the saved design scan only as fallback.
* `deploy/georivo/app.py` — consume shared live chrome, adapt native Blog/language links, and surface TOC before hero.
* `deploy/georivo/georivo-blog.css` — explicit top-level article TOC placement.
* `deploy/georivo/georivo-blog.service` — make the shared Blog Core module available to the native renderer.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — global source-chrome contract and deployment requirements.

### Decisions

* Blog Core-owned native and hosted/CNAME renderers must use current source chrome at runtime with a short cache and a saved-scan fallback. They must not maintain a hand-copied header/footer.
* Imported source-authoritative sites remain owned by their native factory publisher; Blog Core must not wrap those pages in a second header/footer.
* A generated TOC must be a first-section navigation element visible before the article hero, not buried after the lead inside generated body HTML.

### Checks run

* Compiled the shared adapter, Blog Core, and Georivo renderer.
* Smoke-tested extraction of the exact Georivo native account icon, compact flag language selector, footer credit, Blog route insertion, and one TOC before hero in EN and DE.

### Risks / TODO

* A source site that renders header/footer only after client-side JavaScript and emits no server HTML needs an explicit source adapter or server endpoint; the saved scan remains the fallback.

## 2026-07-24 — Generate and publish Georivo's first multilingual article

### Summary

* Confirmed that Georivo had no queued jobs; the earlier topic slate existed only as recommendations and had not been inserted into Blog Core.
* Queued, generated, validated, and explicitly published “How Remote Property Buyers Evaluate Location Before Booking a Viewing”.
* Produced one canonical task with EN, DE, ES, FR, and RU variants plus one hero and three inline editorial images.
* Corrected native-store reading-time calculation so it counts the complete article instead of the 1400-character text-excerpt default.

### Files changed

* `app.py` — count full native article HTML when calculating base and localized `readMinutes`.
* `docs/PROJECT_MEMORY.md` — recorded Georivo's first live multilingual article.
* `docs/CHANGELOG_AI.md` — logged generation, publication, validation, and the reading-time correction.

### Decisions

* A proposed topic list is not considered queued until `content_jobs` rows exist.
* Native-store reading time must use full article text; excerpt limits remain appropriate only for summaries and metadata.

### Checks run

* Validated the base article at 1688 words, 7 sections, 3 inline images, one hero, a table, an ordered list, and 6 FAQ items.
* Validated all four localized child records and confirmed every language preview remained `noindex,nofollow`.
* Published through the native content-store publisher and verified HTTP 200 for all five public article URLs.
* Verified the article appears on `/blog/`, all four image assets return HTTP 200, article pages expose six hreflang entries including x-default, and the multilingual sitemap contains the article.
* Browser-verified the live EN article structure, media, TOC, FAQ, native header/footer, and language selector.

### Risks / TODO

* The remaining proposed Georivo topics are not queued yet.

## 2026-07-24 — Add end-to-end multilingual native publishing

### Summary

* Extended the reusable native content-store contract so one Blog Core task generates and validates every configured site language while keeping one canonical task in the dashboard.
* Enabled Georivo in English, German, Spanish, French, and Russian with localized blog indexes, article chrome, draft previews, language switching, canonical/hreflang metadata, and multilingual sitemap entries.
* Added nginx routing for localized `/{language}/blog/` URLs and fixed the shared navigation helper so localized Blog links are not duplicated.

### Files changed

* `app.py` — localization schema, structured-article translation generation, localized static article labels, and multilingual native-store payloads.
* `deploy/georivo/app.py` — localized routes, chrome, content selection, language switcher, canonical/hreflang, and sitemap output.
* `deploy/georivo/georivo-blog.css` — compact language-selector styling within the native header.
* `deploy/georivo/georivo-blog-nav.js` — recognize both base and localized Blog links.
* `deploy/georivo/georivo.com.conf` — proxy supported localized blog routes to the native renderer.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md` — durable multilingual generation, routing, and SEO contracts.

### Decisions

* Native content-store sites use one task per article; translations are child records keyed by `job_id + language`, not separate dashboard tasks.
* English remains Georivo's base path at `/blog/`; DE, ES, FR, and RU use `/{language}/blog/`. All variants retain the same slug and generated image assets.
* Only actually generated article variants receive article-level hreflang links.

### Checks run

* Compiled Blog Core and the Georivo renderer locally and on the VPS.
* Ran a five-language renderer fixture covering indexes, articles, localized draft preview, canonical URLs, hreflang/x-default, sitemap output, and unknown-language handling.
* Ran a Blog Core schema/render smoke test for the localization table and localized TOC/FAQ labels.
* Passed `nginx -t`; reloaded nginx; restarted `georivo-blog` and `blog-yas-core`; both health endpoints returned `ok`.
* Verified all five public blog indexes return HTTP 200.
* Browser-tested desktop and mobile navigation, opened the mobile menu, switched DE to ES, and confirmed localized navigation without duplicate Blog links.
* Verified draft language switching stays on the same noindex preview job through `?lang=` rather than navigating to an unpublished public URL.

### Risks / TODO

* Existing drafts generated before this change have no translations. Regenerate them after configuring site languages if localized variants are required.
* Each additional language performs a full structured Gemini localization during generation, so multilingual tasks take longer than single-language tasks.

## 2026-07-24 — Restore Georivo blog's native stylesheet

### Summary

* Identified that the Georivo product's hashed native CSS asset changed while the blog renderer still referenced the old asset, which now returned `404`.
* Restored the current native stylesheet and made stylesheet discovery dynamic so future upstream rebuilds do not leave the blog header, footer, logo, and navigation unstyled.
* Kept the source `header.nav.glass` and footer DOM contracts unchanged; no replacement visual system was introduced.

### Files changed

* `deploy/georivo/app.py` — validated discovery and short caching of the current native `/assets/index-*.css` path.
* `docs/PROJECT_MEMORY.md` — recorded the durable hashed-asset rule.
* `docs/CHANGELOG_AI.md` — logged the repair and verification.

### Decisions

* Source-owned hashed assets must be resolved from the source page rather than copied into a permanent hard-coded renderer URL.

### Checks run

* Compiled the live and tracked Georivo renderer.
* Restarted `georivo-blog` and verified its service and public `/blog/` response.
* Verified `/blog/` now references the live native `/assets/index-BzOmagHL.css` asset, which returns HTTP 200.
* Browser-verified the repaired full page.
* Compared computed header and footer styles between the product homepage and `/blog/`; position, dimensions, padding, colors, display, and border radius match.

### Risks / TODO

* If the external product stops using the `/assets/index-*.css` naming contract entirely, configure `GEORIVO_NATIVE_STYLESHEET` or update the strict resolver pattern.

## 2026-07-24 — Research Georivo trend-led article topics

### Summary

* Reviewed Georivo's complete live product positioning, current sitemap, Blog Core site profile, and empty content queue.
* Built a prioritized editorial slate from broad Google Trends parent clusters rather than copying low-volume raw queries into titles.
* Kept the slate focused on Georivo's defensible territory: location context, interactive 3D property experiences, drone alternatives, remote-buyer decisions, and trustworthy geospatial visualization.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded Georivo's durable trend-led editorial territory.
* `docs/SEO_MEMORY.md` — recorded the Trends-to-editorial transformation rule and corrected the deprecated Google News source note.
* `docs/CHANGELOG_AI.md` — logged the research task.

### Decisions

* Google Trends is a relative-demand input, not a source of ready-made article titles.
* Exact niche phrases with insufficient Trends data must not be assigned invented growth figures; use broader parent-topic evidence and apply product/audience fit before proposing an article.

### Checks run

* Confirmed Georivo site 14 has no existing or planned `content_jobs`.
* Reviewed the live homepage product claims, use cases, FAQ, sitemap, and robots directives.
* Checked Google Trends methodology and related-search guidance; attempted direct worldwide 12-month and five-year Explore comparisons.

### Risks / TODO

* Google Trends rate-limited direct Explore/API requests during this research, and several exact niche phrases had insufficient data. The resulting list is intentionally ranked by broad trend-cluster relevance plus product fit, not by unsupported absolute search-volume claims.
* No article tasks were queued or published in this task.

## 2026-07-23 — Rebuild Georivo blog with exact native visual chrome

### Summary

* Replaced the initial approximate dark blog theme with Georivo's actual visual system: the same glass navigation, logo treatment, mobile menu, editorial typography, cream and dark section rhythm, native aerial media, CTA treatment, and exact footer grid.
* Reworked both the empty blog index and generated-article template across wide desktop, desktop, laptop, tablet, mobile, and narrow-mobile breakpoints.
* Preserved Blog Core's native content-store contract; this task changed presentation only and did not generate or publish a real article.

### Files changed

* `deploy/georivo/app.py` — exact source header/footer markup and Georivo-native blog/article composition.
* `deploy/georivo/georivo-blog.css` — responsive native visual system for index, article content, TOC, tables, FAQ, media, and CTAs.
* `deploy/georivo/georivo-blog-nav.js` — native mobile menu behavior in the blog shell while preserving Blog-link injection on the existing product site.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable native-style requirements and verification record.

### Decisions

* Native style fidelity is measured against the source site's DOM and computed styles at matching viewport widths. Reusing only colors and fonts is insufficient.

### Checks run

* Compared source and blog header/footer DOM plus computed dimensions at 1440, 1024, 768, and 390 px.
* Verified blog widths at 1920, 1440, 1024, 768, 390, and 320 px with no horizontal overflow.
* Captured and visually inspected full-page desktop, tablet, and mobile blog screenshots plus desktop/mobile article screenshots.
* Verified the mobile menu opens, exposes the Blog link, and updates `aria-expanded`.
* Verified the existing product homepage retains exactly one Blog link in both header and footer after React hydration at desktop and mobile widths.
* Verified all article fixture images loaded, then removed the temporary fixture and database row.

### Risks / TODO

* The renderer references the source site's stable `/georivo-hero.png`, brand assets, fonts, and compiled CSS. A future source redesign or hashed CSS asset change requires a deliberate renderer parity update.

## 2026-07-23 — Integrate Georivo as a native Blog Core site

### Summary

* Added `georivo.com` to Blog Core as site 14 with an English, product-wide editorial context and a manual-by-default publishing workflow.
* Added the reusable `native_content_store` site mode. Blog Core now generates, previews, schedules, and explicitly publishes its own sites through a local site-owned content store without requiring a legacy source-factory binding.
* Deployed a Georivo-native blog renderer on the VPS. It serves `/blog/`, article URLs, draft previews, and the combined sitemap while retaining Georivo's existing product pages and visual language.
* Added Blog navigation to the existing externally hosted Georivo shell without replacing or rebuilding its product-page design.

### Files changed

* `app.py` — recognize `sites.access_type=native_content_store` in generation, preview, and publication.
* `deploy/georivo/app.py` — native Georivo blog/article renderer.
* `deploy/georivo/georivo-blog.css` — responsive Georivo journal and article styles.
* `deploy/georivo/georivo-blog-nav.js` — non-destructive Blog navigation injection for the current upstream shell.
* `deploy/georivo/georivo-blog.service` — local Gunicorn systemd service template.
* `deploy/georivo/georivo.com.conf` — nginx routing template for local content routes and the unchanged product upstream.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable architecture and deployment memory.

### Decisions

* Georivo is a Blog Core-owned site, not an imported source-authoritative factory. Blog Core is its factory and control plane; the local renderer is only the native presentation and publication adapter.
* The current externally hosted product site remains untouched. Only `/blog`, `/content-preview`, and `/sitemap.xml` are routed to the VPS renderer.

### Checks run

* Compiled both Python applications; restarted Blog Core and the `georivo-blog` systemd service; verified both health endpoints.
* Ran `nginx -t`, reloaded nginx, and confirmed `/blog/`, sitemap inclusion, injected Blog navigation, and HTTP 200 responses.
* Verified desktop and 390 px mobile layouts with Playwright screenshots.
* Created a temporary Blog Core draft, verified the native-store write and redirect to the Georivo noindex preview, then removed the temporary database row and file.

### Risks / TODO

* No Georivo article was generated or published during integration. The public journal intentionally shows its connected empty state until an operator queues and publishes the first article.
* Georivo's product application currently runs on an external `chatgpt.site` upstream. The local blog remains independent of that upstream, but future upstream asset-name changes should be checked against the renderer's stylesheet preload.

## 2026-07-21 — Repair SoloCruz native hero, blog index, and sitemap submission path

### Summary

* Changed the native article hero so a generated image fills the full-height media panel with no overlay copy obscuring it. Added `og:image` for native SEO pages.
* Fixed the SEO publication branch to rebuild each locale's blog index and feed. The indexer now preserves manually authored cards and adds factory output in a separate marked section.
* Re-published the EN/RU/ES/DE/FR article set. The new article is present on `/blog/` and localized blog indexes; all five article URLs are present in the rebuilt blog sitemap.
* Verified Search Console submission cannot complete: the configured service-account credential file is missing. The public `robots.txt` references the current sitemap, but no successful GSC submission can be asserted.

### Files changed

* `/var/www/content-factory-solocruz/app.py` — native SEO index/feed refresh and GSC submission result handling; source-factory repository, not Blog Core Git.
* `/var/www/content-factory-solocruz/factory/landing.py` — preserve source index cards, append a marked factory-card block, and repair the stale excerpt helper call; source-factory repository, not Blog Core Git.
* `/var/www/content-factory-solocruz/factory/seo_waitlist.py` — full-height unobstructed hero media and `og:image`; source-factory repository, not Blog Core Git.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable native-publication and GSC status memory.

### Checks run

* Compiled and restarted `content-factory-solocruz`.
* Confirmed the EN and ES `/blog/` indexes contain the new article while retaining an existing manual card.
* Confirmed no `visual-card` markup in the article hero, and `sitemap-blog.xml` contains the article in all five locales.
* Confirmed `robots.txt` references `https://solocruz.com/sitemap.xml`; GSC submission returned the expected missing-credentials error.

### Risks / TODO

* Add an authorized Search Console service-account credential and grant it access to the SoloCruz property before automatic sitemap submission can work.

## 2026-07-21 — Recreate SoloCruz article in all native languages

### Summary

* Recreated the SoloCruz cruise-community article through `content-factory-solocruz`, not through Blog Core's generic renderer.
* Generated and published a canonical native set in EN, RU, ES, DE, and FR. Each page retains the source site's route structure and the same article slug.
* Re-published all variants after the set was complete so their native language selector and hreflang links point to the matching translated article rather than a homepage.
* Synchronized the source factory inventory back to Blog Core without generating or changing any additional pages.

### Files changed

* `/var/www/content-factory-solocruz/factory.sqlite` — five native source-factory job records and publication state; server data, not Blog Core Git.
* `/var/www/solocruz.com/{,ru/,es/,de/,fr/}blog/how-to-choose-a-cruise-community-before-you-book-group-cabin-share-or-fully-solo/index.html` — native factory output; source-site repository output, not Blog Core Git.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — multilingual native-publication rule and task log.

### Decisions

* A single English source job is not considered a multilingual publication. The native factory must have a published counterpart for each intended locale before the language switch is shown.

### Checks run

* Confirmed all five native URLs return HTTP 200.
* Confirmed EN language switch links to this article's EN/RU/ES/DE/FR URLs.
* Ran `POST /api/sites/7/source-factory/sync`, `python3 -m py_compile app.py`, and the Blog Core health check.

### Risks / TODO

* Future Blog Core delegation should fan out a multilingual planned task into its configured native locale set automatically; this recreation created the required source-factory locale jobs explicitly.

## 2026-07-21 — Schedule native SoloCruz publications

### Summary

* Added an explicit per-job publication schedule and a single PM2 worker that starts native generation when due, waits for the source factory draft, and publishes through the authoritative factory.
* The scheduler is page-only: it never generates or publishes social posts.
* Aligned SoloCruz source-factory blog generation and validation after the first job exposed a contradictory H3 requirement and an impossible non-blog link requirement.
* Fixed SoloCruz native SEO-page asset resolution: generated media is preserved in `/blog/` and published HTML now uses absolute asset URLs instead of nested relative paths.
* Replaced the factory's shortened header/footer on SoloCruz native pages with chrome extracted from the published source site, including its own CSS and interaction script.
* Corrected native-page identity and language behavior: generated pages now retain SoloCruz favicon assets, and a language switch only exposes published translations of the same article rather than routing to a homepage.
* Audited published source-factory samples across YAS Wine, My UGC Studio, SoloCruz, LaycanMatch, AIREP24, and PipsAlerts. No equivalent header/footer or media-path defect was found outside SoloCruz; recorded the separate stale AIREP24 French URL for a deliberate future migration.

### Files changed

* `app.py` — `scheduled_for` migration, scheduling API, and due-job lifecycle runner.
* `scheduler.py`, `run-scheduler.sh` — durable PM2 worker entry point.
* `/var/www/content-factory-solocruz/factory/generate.py`, `/var/www/content-factory-solocruz/factory/validate.py` — source-factory writer/validator alignment; not part of Blog Core Git.
* `/var/www/content-factory-solocruz/factory/seo_waitlist.py` — native SEO-page media URL resolution; not part of Blog Core Git.
* `/var/www/content-factory-solocruz/factory/seo_waitlist.py` — native header/footer extraction; not part of Blog Core Git.
* `/var/www/content-factory-solocruz/factory/seo_waitlist.py` — native favicon/manifest extraction and article-aware language switch; not part of Blog Core Git.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — schedule contract and deployment memory.

### Decisions

* Automatic publication requires an explicit timestamp on each job; the previous cadence setting alone remains non-executing.

### Checks run

* Compiled Blog Core scheduler and SoloCruz factory modules, performed a zero-due scheduler dry run, started and saved the `blog-yas-core-scheduler` PM2 process, and verified Blog Core health.
* Created 12 new SoloCruz tasks; published the first one through `content-factory-solocruz` and verified its public URL returns HTTP 200. The remaining 11 have explicit three-day UTC intervals from 2026-07-24 through 2026-08-23.
* Re-published the first SoloCruz article and verified HTTP 200, the native SVG favicon and Apple touch icon in its `<head>`, and no homepage language switch while only its English version exists.

### Risks / TODO

* A source-factory generation error remains `ERROR` for operator review; the scheduler will not retry it blindly.

## 2026-07-18 — Complete source-factory control for connected sites

### Summary

* Added a binding-first source endpoint resolver so every lifecycle action for a source-authoritative task uses that site's configured factory endpoint.
* Added rerunnable source-factory inventory synchronization and safe backfill APIs. Sync links existing factory jobs by source ID, canonical path, or slug; backfill creates only source `NEW` jobs for imported records that predate a factory. Neither operation generates, publishes, rewrites, or mirrors source pages.
* Bound and synchronized My UGC Studio, LaycanMatch, and AIREP24 alongside the existing YAS Wine, SoloCruz, and PipsAlerts bindings. `yas.ooo` continues to publish through its native content-store adapter.

### Files changed

* `app.py` — binding-first lifecycle resolution and source-factory inventory synchronization endpoint.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable source-control contract and site bindings.

### Decisions

* A source factory remains the publisher and template authority. Blog Core is the control plane and synchronizes job state only.

### Checks run

* Python compilation, factory API contract probes, source inventory synchronization, and Blog Core health check.

### Risks / TODO

* The inventory synchronization is intentionally explicit rather than background polling. Direct source-factory changes can be imported by rerunning the sync endpoint.

## 2026-07-18 — Make YAS Wine a fully managed source factory

### Summary

* Bound `yas.wine` to `content-factory-yaswine` so Blog Core now delegates new work, generation, native preview, explicit publishing, and regeneration to the source factory rather than acting only as imported inventory.
* Linked 176 unique current factory jobs, including 88 SEO money-page records, to Blog Core. The factory has three older published duplicate jobs for the same URLs; the newer source job remains the authoritative control record for each of those pages.
* Corrected the generic explicit Regenerate flow so it calls a source factory even after a previous draft/publication; an already-running job is only polled.
* Restored the YAS Wine factory's required article template as a private factory asset outside `/var/www/yaswine`, so native Preview and future Publish work again without exposing `/blog/template.html`.

### Files changed

* `app.py` — source-factory regenerate behavior.
* `data/blog_core.sqlite3` — ignored YAS Wine source-factory binding and linked job state; not committed.
* `/var/www/content-factory-yaswine/factory/landing.py`, private template asset, server-only `.env` — source preview/template configuration, committed separately to `yasyarik/factory` as `8491d9b`.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable source-factory state and preview contract.

### Decisions

* Primary `jobs` status is authoritative for the YAS Wine source-factory API. The auxiliary `seo_jobs` table classifies money pages but must not overwrite executable job status in Blog Core.

### Checks run

* Confirmed the factory API serves 179 records and Blog Core site ID 5 has a source-authoritative binding to `127.0.0.1:3199`.
* Confirmed Blog Core has 176 linked factory jobs: 15 queued, 1 draft, 12 errors, and 148 live/imported; 88 are marked SEO money pages.
* Compiled and restarted Blog Core and the YAS Wine factory.
* Verified native source Preview and Blog Core proxy Preview both return HTTP 200 with noindex and the YAS Wine theme; public `/blog/template.html` returns 404.
* No factory generation or publication was triggered.

### Risks / TODO

* The 821-page webroot inventory contains pages that never had an original factory job. They remain live inventory; creating a rewrite task for one will create a new native source-factory job rather than silently altering its existing page.
* Source-factory social execution remains provider-specific; direct Blog Core social actions need explicit source adapters where no shared integration exists.

## 2026-07-16 — Bind SoloCruz to its native content factory

### Summary

* Bound `solocruz.com` to `content-factory-solocruz` so Blog Core is now the control plane for new source-factory work instead of only displaying its imported inventory.
* Extended the generic source-factory creation contract with `contentType`, page kind, native target path, canonical group, and locale. This applies to every compatible source-factory binding, not only SoloCruz.
* Repaired the non-secret SoloCruz factory configuration that still had placeholder webroot/domain values, and aligned source-factory preview rendering with the same `seo_waitlist` renderer used by its Publish path.

### Files changed

* `app.py` — forwards the complete canonical page contract when creating a source-factory job.
* `/var/www/content-factory-solocruz/app.py`, server-only `.env` — native preview branch and non-secret site configuration; not part of Blog Core Git.
* `data/blog_core.sqlite3` — ignored source-authoritative binding for site ID 7; not committed.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable integration and delegation rules.

### Decisions

* SoloCruz keeps ownership of public page rendering, multilingual output, assets, and publication. Blog Core must not write a generic mirror or replace the source site's pages.

### Checks run

* Compiled Blog Core and the SoloCruz factory Python applications.
* Restarted `content-factory-solocruz` and `blog-yas-core`.
* Confirmed both health/API endpoints respond, the site ID 7 binding points to `127.0.0.1:12838`, and the SoloCruz management page returns HTTP 200.
* No source job was created, generated, or published during integration.

### Risks / TODO

* The existing 75 SoloCruz pages remain imported inventory records because the source factory currently has no historical job rows. New work will be source-factory-backed from creation onward.
* Social posting routes remain source-factory-specific and need an explicit adapter before Blog Core can trigger them directly.

## 2026-07-15 — Import PipsAlerts into the source-factory control plane

### Summary

* Added a generic source-factory binding layer so a new Blog Core task for an imported site can be created, generated, previewed, and explicitly published by that site's native factory.
* Connected `pipsalerts.com` to its existing `content-factory-pipsalerts` service and imported its guide inventory without changing the PipsAlerts website or guide files.
* Preserved each guide's native `/guides/{slug}/` URL and source factory job ID. Imported 61 live guides and 2 source-factory error tasks for recovery in the dashboard.

### Files changed

* `app.py` — source-factory binding schema, PipsAlerts endpoint registry, native target-path selection, and delegation of newly queued work to the source factory.
* `data/blog_core.sqlite3` — ignored live site/binding/job records for PipsAlerts; not committed.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable source-authoritative integration contract and PipsAlerts operating details.

### Decisions

* PipsAlerts remains source-authoritative. Blog Core is its control plane and must not build a second public blog, overwrite the Next template, or publish generic static files into its webroot.

### Checks run

* Confirmed the native PipsAlerts factory API responds on `127.0.0.1:13095`.
* Confirmed the Blog Core database contains site ID 13, its source-factory binding, 61 `IMPORTED` jobs, and 2 `ERROR` jobs.
* Ran `python3 -m py_compile app.py`, checked `http://127.0.0.1:3299/health`, and verified the PipsAlerts site-management page returns HTTP 200.

### Risks / TODO

* The two imported source errors are preserved for operator recovery; no generation or publication was triggered during import.
* Existing source-factory social statuses are displayed after import, but any source-specific social execution API needs an explicit adapter before it can be controlled from Blog Core.

## 2026-07-13 — Generalise Scanner Studio draft ingestion by site

### Summary

* Changed the authenticated Source Scanner Studio endpoint from YAS-only to site-aware so each Scanner editorial project can place finished drafts in its connected Blog Core site queue.
* Preserved the native YAS content-store draft preview only for `yas.ooo`; other sites receive a reviewable `DRAFT` without an unsafe publishing assumption.

### Files changed

* `app.py` — project metadata intake, generic site acceptance and conditional native preview preparation.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — documented the generic contract and YAS-specific adapter boundary.

### Checks run

* Ran `python3 -m py_compile app.py`, restarted `blog-yas-core`, and confirmed `/health` returns `ok`.

### Risks / TODO

* A non-YAS site still needs its own explicit publication adapter before a Blog Core draft can become a live page.

## 2026-07-13 — Add LinkedIn personal OAuth connection

### Summary

* Added `Connect LinkedIn` to the per-site Setup card when server OAuth credentials are configured.
* Added a state-protected OAuth authorization-code start/callback flow that stores the issued personal access token and derived `urn:li:person:<id>` only after LinkedIn authorization completes.
* Stored the provided LinkedIn application credentials in the ignored server `.env` with restricted file permissions; they were not committed or rendered.

### Files changed

* `app.py` — LinkedIn OAuth helpers, start/callback routes, and Setup action.
* Server-only `.env` — LinkedIn OAuth application settings; ignored and not committed.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — document the durable connection contract without secrets.

### Checks run

* `python3 -m py_compile app.py`.
* Restarted `blog-yas-core`; `/health` returns `ok`.
* Verified the OAuth start route returns LinkedIn authorization URL with the configured callback, a state value, and `openid profile w_member_social` scopes.
* Verified the `Connect LinkedIn` button appears on the YAS site Setup screen.

### Risks / TODO

* This flow connects the personal profile because the LinkedIn app currently exposes `w_member_social`. Company-page publishing needs the relevant organization scope and organization role/URN.

## 2026-07-13 — Make social drafts native and route five networks through Zernio

### Summary

* Replaced the mixed direct-provider setup for X/Twitter, Pinterest, Instagram, Threads, and Reddit with one per-site Zernio connection and explicit account mappings.
* Added Reddit as a first-class channel, including community-first title/body drafts, subreddit rules, review, status fields, and Zernio delivery metadata.
* Strengthened native content contracts: validated Instagram carousel types/roles/deduplication, Threads conversation formats, X post/thread formats, actual Pinterest JPEG Pin generation, and separate Telegram/Tumblr editorial media metadata.
* Added a generic social review route and an explicit Zernio publish action for ready drafts. No social posts were published during this task.
* Removed raw `credentials_json` from the factory-settings API response.

### Files changed

* `app.py` — Zernio connection/publish adapter, channel models, prompt contracts, validators, assets, reviews, Reddit persistence, and API credential redaction.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — record the durable social architecture and contracts.

### Checks run

* `python3 -m py_compile app.py` before and after deployment.
* Restarted `blog-yas-core`; `/health` returns `ok`.
* Zernio connection test succeeded using the configured server default; it found one connected account and published nothing.
* Confirmed SQLite migrations for Reddit social status and distribution settings.
* Confirmed the setup page includes Zernio, Reddit, Pinterest/Reddit mapping fields, and subreddit rules.
* Unit-checked Instagram validation: a correctly structured carousel passes and invalid type/final role fails.
* Confirmed factory-settings API does not return `credentials_json`.

### Risks / TODO

* The tested Zernio profile currently has no per-channel account mappings in Blog Core, so Zernio channels remain intentionally inactive until those IDs are saved in Setup.
* Direct final-publish adapters for LinkedIn, Telegram, and Tumblr, and a UI for scheduling a specific Zernio datetime, remain separate follow-up work.

## 2026-07-13 — Accept selected YAS Studio drafts in Blog Core

### Summary

* Added an authenticated source-scanner endpoint that creates or updates an authored YAS Studio article as a native `yas.ooo` Blog Core `DRAFT` task.
* Stored a scanner-article-to-Blog-Core-job mapping for idempotent resends and protected published tasks from replacement.

### Files changed

* `app.py` — source-scanner mapping schema, authentication, safe draft upsert and native YAS draft-store preparation.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — recorded the integration contract and operating rule.

### Decisions

* Receiving a Studio draft is not article generation or publishing; publication and social distribution remain explicit Blog Core actions.

### Checks run

* Ran `python3 -m py_compile app.py` before deployment.
* Restarted `blog-yas-core` and confirmed local `/health` returns `200`.
* Confirmed the endpoint rejects an unauthenticated request (`401`) and accepts the configured Scanner shared secret before correctly rejecting an empty payload (`400` for missing article ID). No content task was created during the check.

### Risks / TODO

* A published task intentionally cannot be overwritten through the scanner integration.

## 2026-07-13 — Remove Shopify tasks from the YAS queue

### Summary

* Removed the four queued YAS Blog Core rewrite tasks whose title, topic, or slug contained `Shopify`.
* No generation or publication was started; existing public YAS pages and their design were not changed.

### Files changed

* `data/blog_core.sqlite3` — removed four ignored live queue records and their associated Blog Core logs/social-draft records.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the current YAS content focus and this operation.

### Checks run

* Confirmed the four matched tasks before deletion.
* Confirmed eight planned YAS jobs remain and zero queued YAS jobs contain `Shopify`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* The removed jobs can be recreated later only through a deliberate new queue action.

## 2026-07-13 — Integrate Blog Core into the new YAS use-cases design

### Summary

* Preserved the user-authored `/use-cases/` cinematic page without replacing its hero, existing cards, imagery, navigation, or CSS.
* Added published factory use cases after the existing four entries in the same alternating operating-case layout.
* Added a native dark use-case detail/preview renderer so factory-generated money pages do not fall back to the generic article template.

### Files changed

* `/opt/yas-ooo/src/app/use-cases/page.tsx` — reads published use-case records and appends them to the existing design.
* `/opt/yas-ooo/src/components/ManagedUseCasePage.tsx`, `/opt/yas-ooo/src/app/use-cases/[slug]/page.tsx`, `/opt/yas-ooo/src/app/content-preview/[jobId]/page.tsx`, and `use-cases.module.css` — render managed use-case details and previews in the source visual system.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the source-design preservation rule.

### Checks run

* `npm run build` in `/opt/yas-ooo`.
* Restarted `yas-ooo.service`.
* Added and removed a temporary managed use-case record: it appeared in the index after the four existing cases; its detail response contained `useCasesFilm`, `YAS / IMPLEMENTATION USE CASE`, and `IMPLEMENTATION BRIEF`.

### Risks / TODO

* No permanent content record was created by the integration test.

## 2026-07-13 — Make native YAS sitemap publication-driven

### Summary

* Fixed the YAS sitemap so it reads the native Blog Core published store at request time rather than only during a Next build.

### Files changed

* `/opt/yas-ooo/src/app/sitemap.ts` — marks the sitemap route dynamic.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the indexing contract.

### Checks run

* `npm run build` in `/opt/yas-ooo`; the route is confirmed dynamic in Next build output.
* Restarted `yas-ooo.service`.
* Added and removed an isolated published-store record; its `/blog/<slug>` URL appeared in `http://127.0.0.1:3200/sitemap.xml` immediately.

### Risks / TODO

* No permanent test content was left in the native store.

## 2026-07-13 — Route Discovery money-page tasks to native use cases

### Summary

* Extended the universal Discovery prompt and queue contract with an explicit `seo_money_page` type.
* Service-aligned use-case ideas now queue with `pageType=seo_money_page` and `/use-cases/<slug>/`; editorial ideas retain their `/blog/<slug>/` path.
* Verified the behavior with an isolated task, then removed the test task and its logs.

### Files changed

* `app.py` — adds deliberate money-page classification guidance, normalizes content types, and assigns canonical targets at queue time.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/CHANGELOG_AI.md` — recorded the durable routing rule.

### Decisions

* A money page is created only when it is a durable use case directly aligned to a site's service/product; commercial keywords alone do not qualify.

### Checks run

* `python3 -m py_compile /tmp/blogcore-discovery-content-type.py`
* Deployed `app.py`, restarted `blog-yas-core`, and checked `/health`.
* Queued a temporary `seo_money_page` idea for YAS and verified its `category=SEO Money Page`, `contentType=seo_money_page`, and `targetPath=/use-cases/shopify-architecture-recovery-for-app-heavy-stores/`; removed the test job and logs immediately afterwards.

### Risks / TODO

* No public content was generated or published by this routing test.

## 2026-07-13 — Add YAS SEO use-case architecture

### Summary

* Added a native YAS `/use-cases/` hub and four initial decision-oriented SEO money pages.
* Added `Use Cases` to the primary navigation.
* Extended the native Blog Core content-store contract so `use_case` and SEO-money-page jobs publish into `/use-cases/<slug>/`, remain separate from the blog feed, and enter the YAS sitemap.

### Files changed

* `app.py` — adds `contentType` to native content-store payloads and maps use-case/SEO-money-page task types separately from blog content.
* `/opt/yas-ooo/src/content/use-cases.ts` — defines initial commercial use-case content.
* `/opt/yas-ooo/src/app/use-cases/page.tsx` and `/opt/yas-ooo/src/app/use-cases/[slug]/page.tsx` — render the hub and canonical detail pages, including managed published replacements.
* `/opt/yas-ooo/src/lib/managed-content.ts`, `src/app/sitemap.ts`, and `src/components/Header.tsx` — add managed content typing, sitemap coverage, and primary navigation.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/CHANGELOG_AI.md` — record the durable SEO and architecture decision.

### Decisions

* Use cases are first-class SEO money pages, not blog category pages.
* Blog Core content can replace or extend a use case through the native content store without editing the YAS route implementation.

### Checks run

* `python3 -m py_compile /var/www/blog.yas.ooo/app.py`
* `npm run build` in `/opt/yas-ooo`
* Restarted `blog-yas-core` and `yas-ooo.service`.
* Confirmed `/use-cases`, `/use-cases/shopify-storefront-performance`, and all four use-case URLs return HTTP `200`.
* Confirmed all use-case routes are present in `https://yas.ooo/sitemap.xml` and the `Use Cases` navigation link renders.
* Browser-tested desktop and 390px mobile layouts with Playwright screenshots; mobile navigation collapses to `Menu`, cards become one column, and text remains contained.

### Risks / TODO

* `/opt/yas-ooo` still has no Git repository or configured remote, so the live YAS source changes cannot yet be committed/pushed.

## 2026-07-13 — Queue YAS legacy blog rewrites with locked URLs

### Summary

* Connected `yas.ooo` to Blog Core as a local site using `/opt/yas-ooo`.
* Added all 12 existing English blog topics as `QUEUED` rewrite tasks, retaining their current `/blog/<slug>/` paths.
* Added a generic `preserveSlug` contract: jobs explicitly marked with it keep their preassigned canonical slug when a draft is generated.
* Added the native Next content-store publisher for YAS: draft records go to `data/blog-core/drafts`, Preview redirects to a noindex YAS-native route, and explicit Publish moves a record to `data/blog-core/published` without changing page templates or source arrays.
* Updated the YAS blog, article route, homepage insight section, and sitemap so a published managed article takes priority on its existing slug and appears automatically in the native site feed.
* Did not generate, publish, alter, or remove any public legacy YAS article.

### Files changed

* `app.py` — honors `sources_json.preserveSlug` and provides the native content-store preview/publish contract.
* `/opt/yas-ooo/src/lib/managed-content.ts` — reads managed draft/published records at runtime.
* `/opt/yas-ooo/src/components/ManagedArticle.tsx` and `/opt/yas-ooo/src/app/content-preview/[jobId]/page.tsx` — render noindex draft previews in the native YAS UI.
* `/opt/yas-ooo/src/app/blog/page.tsx`, `/opt/yas-ooo/src/app/blog/[slug]/page.tsx`, `/opt/yas-ooo/src/app/page.tsx`, `/opt/yas-ooo/src/app/sitemap.ts` — give published managed content priority in the blog, homepage feed, and sitemap while retaining legacy fallback content.
* `data/blog_core.sqlite3` — live ignored database now has the YAS site and its 12 queued rewrite jobs.
* `docs/PROJECT_MEMORY.md` — recorded canonical-slug and YAS queue decisions.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Existing URLs remain canonical while their content is rewritten.
* Publishing stays an explicit action and uses the native YAS content-store publisher rather than the generic static installer.

### Checks run

* `python3 -m py_compile /tmp/blogcore-app.py`
* `python3 -m py_compile /var/www/blog.yas.ooo/app.py`
* Restarted `blog-yas-core` with PM2 and confirmed `http://127.0.0.1:3299/health` returns `ok`.
* Queried the live database: 12 `QUEUED` YAS jobs exist and every `targetPath` matches its existing `/blog/<slug>/` route.
* Normalized all 12 YAS jobs to `pageType=blog`, `contentType=blog`, `publicationMode=native_next_content_store`, and an explicit `/opt/yas-ooo` native project root; the dashboard API now reports `types: ['blog']`.
* Ran `npm run build` in `/opt/yas-ooo`, restarted `yas-ooo.service`, and confirmed `/`, `/blog`, and an existing article return HTTP `200`.
* Created and removed an isolated private smoke-test job. Blog Core preview redirected to `https://yas.ooo/content-preview/<job>` and YAS rendered the draft in its native UI; the test JSON and DB record were removed afterwards.

### Risks / TODO

* `/opt/yas-ooo` has no Git repository or configured remote. Its code is deployed and build-tested, but cannot be committed/pushed until its canonical repository is identified or created.

## 2026-07-09 — Add persistent progress for generating tasks

### Summary

* Added an animated in-card progress panel for content/planned tasks whose status is `GENERATING`.
* Added polling against the existing content-job API so the dashboard updates the latest generation log text and reloads when the task becomes `DRAFT` or `ERROR`.
* Added elapsed-time updates and moving progress animation so async legacy/source factory generation no longer appears frozen after the first request returns.

### Files changed

* `app.py` — added `generating_progress_panel`, `GENERATING` card actions, progress CSS, and frontend polling functions.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that `GENERATING` tasks must show animated progress and poll until finished.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Reuse the existing `GET /api/sites/<site_id>/content-jobs/<job_id>` endpoint for generation polling instead of adding another status endpoint.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` and docs to `/var/www/blog.yas.ooo`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/sites/9` HTML contains `generation-progress`, `data-generating-job-id`, `pollGeneratingJob`, and `initGeneratingPollers()`.
* Verified the currently running AIREP24 task `AiRep24 vs. Live Chat` renders an in-card animated progress panel.
* Verified `GET /api/sites/9/content-jobs/6fb2a84685c8450183d67eb7` returns `status=GENERATING` and generation logs for polling.

### Risks / TODO

* Polling reloads the page when a task leaves `GENERATING`; exact backend sub-step progress still depends on source factory logs.

## 2026-07-09 — Preserve source-site post-article blocks in previews

### Summary

* Added generic extraction of post-article source template sections for local imported-site draft previews.
* Local previews now preserve recognizable sections that follow the main article block, such as recommendations, related content, newsletter/signup, or updates blocks.
* Added source-template FAQ adaptation so generic Blog Core FAQ markup can use a recognized `faq-grid`/`faq-card` pattern instead of raw generic `<details>` styling.
* Kept the solution pattern-based and site-agnostic; no domain-specific logic was added for AIREP24.

### Files changed

* `app.py` — added source post-article extraction, FAQ pattern adaptation, and wired them into local draft preview rendering.
* `docs/PROJECT_MEMORY.md` — recorded the durable generic rules for preserving source post-article blocks and adapting FAQ markup.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Preserve source-site UX blocks by recognizing template structure around the article, not by hardcoding site names or exact block titles.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified the AIREP24 draft preview returns HTTP 200.
* Verified the local preview now selects a sibling article template with post-article blocks instead of the blog hub.
* Verified preview contains source-style `faq-grid`/`faq-card` and no generic `article-faq`.
* Verified preview contains `Recommended next`, `recommend-grid`, `Get updates`, and `waitlist-form`.
* Verified preview still has 3 Blog Core article asset refs, 7 rewritten TOC refs, no `airep24.com/sites/...` asset refs, and no plain `href="#..."` TOC links.

### Risks / TODO

* Extraction intentionally targets the first source `section.article-layout` in the local template. Sites with very different article markup may need additional generic patterns later.

## 2026-07-09 — Fix local draft preview assets and TOC links

### Summary

* Fixed local source-site draft previews where the source template's `<base href="https://source-site/">` caused Blog Core article image URLs to resolve on the source domain.
* Fixed TOC links in the same previews so fragment links target the current Blog Core preview URL instead of resolving through the source template base URL.
* The fix is applied at preview render time, so existing regenerated drafts do not need another regeneration just to repair asset and TOC links.

### Files changed

* `app.py` — added `prepare_local_draft_content` and wired it into local draft preview body rendering.
* `docs/PROJECT_MEMORY.md` — recorded the durable `<base>`/preview URL rule for local imported-site previews.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Keep the source site's `<base>` behavior for source assets, but rewrite Blog Core-only draft body links to absolute Blog Core preview URLs.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` and docs to `/var/www/blog.yas.ooo`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified the AIREP24 preview returns HTTP 200.
* Verified preview HTML rewrites 3 article image refs to `https://blog.yas.ooo/sites/9/article-assets/...`.
* Verified preview HTML rewrites 7 TOC links to the current preview URL plus anchor.
* Verified no `airep24.com/sites/...`, root-relative asset URLs, or plain `href="#..."` TOC links remain in the preview HTML.
* Verified an article image asset URL returns HTTP 200.

### Risks / TODO

* Existing drafts do not need regeneration for this fix because link rewriting happens at preview render time.

## 2026-07-09 — Fix article image aspect ratio

### Summary

* Fixed generic Blog Core article image generation after Gemini rejected the unsupported `16:10` aspect ratio.
* Changed article hero/body image prompts and Gemini Image calls to use supported `16:9`.
* Regenerated the failed AIREP24 draft task `fbd0f8d9fee07da8482f01e0` successfully after deploy.

### Files changed

* `app.py` — changed generic article image generation from `16:10` to `16:9`.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule to use supported Gemini Image aspect ratios only.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Generic article assets use `16:9` because it is supported by Gemini Image and fits article hero/body media.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` and docs to `/var/www/blog.yas.ooo`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Ran `POST /api/sites/9/content-jobs/fbd0f8d9fee07da8482f01e0/generate`; it returned `ok: true`, `status: DRAFT`.
* Verified the regenerated draft has 1822 validated words, 7 sections, 3 body images, 6 FAQ items, TOC, FAQ, table, ordered list, and no generation error.
* Verified 4 JPEG files were created under `data/article_assets/9/fbd0f8d9fee07da8482f01e0`.
* Verified the draft preview returns HTTP 200 and article asset URLs return HTTP 200.

### Risks / TODO

* None yet.

## 2026-07-09 — Add explicit draft regeneration controls

### Summary

* Added an explicit `Regenerate draft` button for `DRAFT` tasks in Planned publications.
* Added the same regeneration action for `DRAFT` rows shown in the Content inventory.
* Renamed the bulk generation action to `Generate / regenerate selected` so selected `DRAFT` tasks can be corrected without deleting and re-queueing them.
* Updated single-job progress text so regeneration shows `Regenerating draft` instead of the generic generation label.

### Files changed

* `app.py` — added `regenerate_draft_button`, wired it into DRAFT actions, and updated the generation JS label handling.
* `docs/PROJECT_MEMORY.md` — recorded that DRAFT tasks must be explicitly regenerable.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* A bad draft should be corrected by regenerating the same task in place, not by deleting the planned task.

### Checks run

* Pending deploy checks in this task.

### Risks / TODO

* Regenerating a generic Blog Core draft now includes Gemini text plus 4 Gemini Image calls, so it can take noticeably longer than the old placeholder-only draft generation.

## 2026-07-09 — Restore full article draft blocks and validation

### Summary

* Restored the structured article renderer so generated drafts include TOC, 3 body figures, a useful table, an ordered list, quote, and FAQ.
* Removed duplicate title/subtitle rendering from local source-site draft previews: the title is rendered once in the source-site hero and no longer repeated again inside the article body.
* Added server-side validation before a generic Blog Core article can become `DRAFT`, including minimum length, section count, exactly 3 image specs, FAQ, table, ordered list, and duplicate lead/description checks.
* Added real JPEG article asset generation for generic Blog Core drafts: one hero image plus 3 body images through Gemini Image, stored under ignored `data/article_assets/...` and served by a Blog Core asset route.

### Files changed

* `app.py` — restored full structured article HTML rendering, added article draft validation, added article image asset generation/routes, and removed duplicated heading blocks from local draft preview bodies.
* `docs/PROJECT_MEMORY.md` — recorded durable rules for the full article block contract, validation, and real article JPEG assets.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Structured article JSON remains the right model contract, but Blog Core must render and validate the complete article page, not a shortened subset.
* Generic Blog Core drafts must fail clearly if required blocks or minimum length are missing; they must not be saved as ready drafts.
* Generic Blog Core article photos are generated assets, not filename placeholders.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Copied patched `app.py` to `/tmp/blogcore-app.py` on the VPS and ran `python3 -m py_compile /tmp/blogcore-app.py`.
* Verified `render_structured_article_html` outputs 3 figures, TOC, FAQ, table, ordered list, no body `<h1>`, no title duplication, and article asset URLs.
* Verified `validate_structured_article_draft` rejects short/incomplete drafts with explicit errors.

### Risks / TODO

* Full runtime generation with Gemini text plus 4 Gemini Image calls was not run from the dashboard in this patch. It should be checked on a real queued generic Blog Core task after deploy because SSH shell environment may not expose the same API keys as PM2.

## 2026-07-09 — Generate article drafts as structured JSON

### Summary

* Removed the main cause of malformed article-generation JSON: asking Gemini to place a large `contentHtml` fragment inside a JSON string.
* Added an article draft `responseSchema` for Gemini with structured fields: metadata, lead, sections, table, ordered list, quote, images, and FAQ.
* Added server-side HTML rendering from structured article fields so Blog Core controls escaping, figures, tables, lists, and blockquotes.
* Changed generic Blog Core article generation to use the schema with `repair=False`; the repair pass is no longer the primary path for article/page drafts.
* Kept the generic JSON repair helper available for other JSON helpers, but article/page draft correctness now comes from schema plus server rendering.

### Files changed

* `app.py` — added `ARTICLE_DRAFT_SCHEMA`, `render_structured_article_html`, image filename cleanup, schema support in `_gemini_generate_text`, and schema-based article draft generation.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that article/page generation must use structured schema output and server-side HTML rendering instead of raw HTML inside JSON.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Article/page generation should be correct by construction: structured JSON from the model, HTML rendered by Blog Core.
* Large HTML strings inside JSON are fragile and should not be used as the model contract for article drafts.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Verified `render_structured_article_html` produces 3 figures, a table, an ordered list, and a blockquote from a structured draft object.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* A direct schema call could not be tested from the plain SSH shell because `GEMINI_API_KEY` is not exported there; PM2 may carry a different environment. Runtime article generation should be verified from the dashboard or a PM2-env-backed request.

## 2026-07-09 — Add article generation progress and JSON repair

### Summary

* Added visible single-job article/page generation progress with elapsed time and staged status text.
* The generation progress updates both the in-page planned-publications progress area and the toast so it remains visible even outside the Distribution tab.
* Added a Gemini JSON repair pass for malformed model JSON before failing a generic Blog Core article generation job.
* Improved the JSON generation helper by splitting text generation, parsing, and repair into separate functions.

### Files changed

* `app.py` — added `_gemini_generate_text`, `_repair_json_text`, robust `_gemini_text_json` repair handling, and draft generation progress JS.
* `docs/PROJECT_MEMORY.md` — recorded durable rules for article generation progress and malformed Gemini JSON repair.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* The current article generation endpoint remains synchronous, so UI progress is client-side staged progress with elapsed time.
* Invalid Gemini JSON should get one repair attempt before the job is marked `ERROR`.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/sites/9#distribution` HTML contains `startDraftProgress`, `draftProgressStep`, and toast progress updates.
* Verified `_gemini_text_json` can recover from a mocked malformed JSON response when the repair pass returns valid JSON.

### Risks / TODO

* Exact server-side generation progress would require converting single article generation into a job/polling or streaming workflow. Current progress shows active waiting and elapsed time but not exact backend sub-step completion.

## 2026-07-09 — Improve Discovery idea diversity

### Summary

* Added editorial diversity fields to generated article ideas: `topic_axis` and `audience_problem`.
* Updated the journalist prompt to require distinct topic axes and concrete audience/business problems.
* Improved same-response semantic deduplication by comparing editorial axes, audience problems, titles, angles, business relevance, and query clusters.
* Improved query-cluster normalization by stripping weak decision modifiers such as `evaluating`, `choose`, and `select`.

### Files changed

* `app.py` — added editorial-axis normalization, diversity-aware same-response dedupe, prompt fields/rules, and cleaner query-cluster normalization.
* `docs/PROJECT_MEMORY.md` — recorded the durable editorial diversity rule.
* `docs/INTEGRATIONS.md` — documented the updated article idea API/dedupe behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Universal article idea quality should be enforced by topic-axis and audience-problem diversity, not by per-site exceptions.
* Similar signals can produce multiple ideas only when they target clearly different problems, outcomes, or funnel moments.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `POST /api/sites/9/article-ideas` returns a more diverse set of AIREP24 ideas across axes such as `technical product questions`, `response latency`, `conversational memory`, `returns prevention`, `post-purchase retention`, `conversational search`, and `human/mobile escalation`.

### Risks / TODO

* Axis normalization is heuristic and should be expanded only with generic cross-site patterns, not site-specific exceptions.

## 2026-07-09 — Add Discovery idea generation progress

### Summary

* Added an in-page progress panel while SEO article ideas are being generated.
* The progress panel shows an active loader, elapsed time, and staged status text for context prep, model passes, and validation.
* Disabled the generation button while a generation request is in flight and re-enabled it afterward.

### Files changed

* `app.py` — added Discovery idea progress CSS and client-side progress/timer logic around `createIdeasFromSignals`.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that long Discovery idea generation must show visible progress.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* The current backend does not stream exact model-pass progress, so the UI shows a truthful staged waiting indicator and elapsed timer until the request returns.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/sites/9#discovery` HTML contains the new progress UI and JS hooks.

### Risks / TODO

* Exact server-side progress would require changing the article-idea endpoint to a job/polling or streaming model. Current progress is client-side but clearly shows the request is still active.

## 2026-07-09 — Simplify Discovery signal selection UX

### Summary

* Removed the manual raw-topic selection step from the Discovery workflow.
* Discovery now starts with a deep-analysis status and loader while topic signals are fetched and filtered.
* All usable search/Reddit audience signals are selected automatically for article idea generation.
* The `Generate SEO article ideas` button is disabled until signal analysis completes and at least one usable signal is available.
* Replaced the visible raw signal card list with a compact analysis summary showing kept/raw/filtered counts.

### Files changed

* `app.py` — updated Discovery HTML/CSS/JS to hide raw signal cards, add analysis state/loading UI, disable/enable generation based on signal readiness, and always pass all usable signals to the idea generator.
* `docs/PROJECT_MEMORY.md` — recorded the automatic-signal Discovery UX rule.
* `docs/INTEGRATIONS.md` — documented UI behavior while preserving the topic-signal API contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Raw Discovery signals remain important inputs and diagnostics, but they should not be the primary operator workflow.
* Operators should review/select final article ideas, not raw autocomplete/Reddit inputs.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Checked `/sites/9#discovery` HTML contains the deep-analysis state, disabled generation button, hidden signal container, and no Reddit period buttons.

### Risks / TODO

* Period-specific Reddit controls were removed from the main UI. The backend still supports ranges, but the simplified workflow currently defaults to the existing `week` range.

## 2026-07-09 — Normalize Discovery idea clusters and dedupe

### Summary

* Cleaned article idea `target_query_cluster` values so raw autocomplete modifiers such as `best`, `top`, `review`, `comparison`, and obsolete years do not leak into visible cards or downstream planning.
* Changed the visible idea source line to use the normalized SEO cluster instead of dirty raw search strings such as `best ... 2025`.
* Added validation for dirty SERP modifiers inside query clusters and SEO rationale.
* Added semantic deduplication against already accepted ideas in the same generation response, not only exact title matching.
* Tightened the journalist prompt to require normalized SEO clusters and consolidation of repeated business-problem clusters.

### Files changed

* `app.py` — added query-cluster cleanup, visible source normalization, dirty field validation, and same-response semantic deduplication.
* `docs/PROJECT_MEMORY.md` — recorded normalized visible query/source lines and semantic dedupe rules.
* `docs/INTEGRATIONS.md` — documented the updated article idea API behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Dirty autocomplete strings may remain useful as raw signals internally, but they must not be displayed as article idea source/query lines or passed forward as SEO clusters.
* Discovery should produce fewer but stronger ideas when many signals represent the same underlying audience problem.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `POST /api/sites/9/article-ideas` returns normalized source/query lines such as `ai sales assistant`, `ai chatbot technical support`, and `agentic ai customer service` without visible `best/top/2025` strings.

### Risks / TODO

* Semantic dedupe is heuristic; it may still allow adjacent ideas when they target distinct business angles inside the same product area.

## 2026-07-09 — Enforce Google-style editorial Discovery ideas

### Summary

* Rebuilt the Discovery article-idea prompt around Google Search Central 2026 generative-search guidance: unique, valuable, non-commodity, people-first pages grounded in the connected site's business and expertise.
* Made search/Reddit items explicit audience-interest signals rather than article titles.
* Added site editorial policy inference for whether comparison/review/listicle or tutorial/build/setup formats are allowed.
* Added server-side idea validation that rejects obsolete years, copied signal titles, generic SERP-clone formats, and unsupported tutorial/review formats before ideas are shown.
* Fixed editorial policy inference so bad existing/generated content cannot grant permission for future bad formats.

### Files changed

* `app.py` — added site editorial policy inference, Google-style journalist/SEO prompt, richer idea fields, stricter idea validation, and safer fallback idea templates.
* `docs/PROJECT_MEMORY.md` — recorded durable Discovery editorial rules.
* `docs/INTEGRATIONS.md` — documented the updated article idea prompt/validation contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Discovery fixes must be global and site-agnostic: the generator should understand each site's profile and strategy, then create editorial topics from audience demand.
* Editorial-format permissions come from stable site profile/settings, not from already-generated content that may contain obsolete or low-quality patterns.
* Product/commercial sites default to problem/business-impact/use-case/decision-context topics, not generic `best/top/review/how to build` SERP formats.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified site editorial policy for AIREP24 rejects comparison/tutorial formats by default.
* Verified `POST /api/sites/9/article-ideas` now returns AIREP24 topics without obsolete `2025`, numbered listicles, `best/top` roundups, buyer/evaluation frameworks, or `how to train/configure/build` titles.

### Risks / TODO

* Gemini can still produce borderline phrasing; server-side validation now blocks the worst unsupported formats, but editorial tuning may continue as better universal quality criteria emerge.

## 2026-07-09 — Make Discovery topic selection content-informed

### Summary

* Reworked Discovery topic query selection to use the connected site's full context instead of a single heading or first category tokens.
* Added content-corpus extraction from existing `content_jobs` titles, descriptions, categories, slugs, and URLs.
* Preferred English/canonical records for multilingual sites when enough English records exist.
* Prioritized multiword product/editorial clusters over single generic words such as `ai`, `questions`, or `support`.
* Removed hard-coded Shopify/product-photography drift for sites where the content does not support that cluster.
* Added broader vertical-aware query candidates for customer support/ecommerce assistant, AI UGC, solo cruise, and maritime/shipbroking/logistics sites.
* Added filters for career/vendor autocomplete noise and AI news/culture drift in Reddit.

### Files changed

* `app.py` — added content-informed topic corpus extraction, query candidate generation, English-preference for multilingual content, multiword cluster prioritization, vertical query candidates, and additional noise filters.
* `docs/PROJECT_MEMORY.md` — recorded content-informed Discovery rules.
* `docs/INTEGRATIONS.md` — documented the updated topic query candidate contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Discovery topic selection must be global and site-agnostic: it should infer each site's topic map from its full connected content and settings, not from per-site hard-coded exceptions.
* Single high-frequency tokens are allowed as anchors but should not become the main query when multiword topic clusters exist.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified AIREP24 (`site_id=9`) now uses `ai customer support` and returns AI support/chatbot/platform signals instead of Shopify product photography.
* Verified SoloCruz (`site_id=7`) now uses `solo cruise` and returns solo cruise/single supplement/cabin sharing signals.
* Verified LaycanMatch (`site_id=8`) now uses maritime/software/shipping/freight matching signals instead of returning zero or career/developer results.
* Verified My UGC Studio (`site_id=6`) still returns AI UGC/ecommerce creative signals.

### Risks / TODO

* Reddit RSS remains frequently rate-limited and sparse for niche B2B queries; it should be treated as a degraded source when `failedQueries` is high.
* Autocomplete can still contain occasional vendor-market noise such as M&A; keep expanding generic noise filters when repeated patterns appear.

## 2026-07-08 — Remove fixed Discovery idea targets

### Summary

* Removed fixed article idea targets such as 4, 12, or 16 from Discovery generation.
* Changed Gemini idea generation to iterate while new valid ideas are still being accepted.
* Kept only technical guards: `ARTICLE_IDEA_SAFETY_CAP`, `ARTICLE_IDEA_SIGNAL_CAP`, and `ARTICLE_IDEA_MAX_PASSES`.
* Updated UI/API copy to show accepted/generated/rejected/pass counts instead of accepted/target.

### Files changed

* `app.py` — replaced target-count generation with iterative multi-pass generation until no new valid ideas are found or a technical guard is reached.
* `docs/PROJECT_MEMORY.md` — recorded that Discovery should return all valid ideas after filters, not arbitrary target counts.
* `docs/INTEGRATIONS.md` — updated the article idea `counts` contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* The number of article ideas is determined by editorial/SEO validity after filters, not by a product-level target.
* Technical caps remain only to control runaway latency/cost and are exposed as diagnostics, not presented as the desired number of ideas.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `POST /api/sites/6/article-ideas` with 25 live Discovery signals now returns counts `accepted=21`, `generated=27`, `rejected=6`, `passes=4`, `safetyCap=50`, `signals=25`.

### Risks / TODO

* More passes increase latency; the current guard is configurable with `ARTICLE_IDEA_MAX_PASSES`.

## 2026-07-08 — Scale Discovery article idea volume

### Summary

* Replaced/deprecated by 2026-07-08 — Remove fixed Discovery idea targets.
* Made article idea generation target scale with the number of selected Discovery signals.
* Added a second Gemini pass when the first validated idea set is below target.
* Increased the selected signal window used by the idea generator from 18 to 24.
* Added API/UI counts for accepted, target, generated, rejected, and signal count so a short result set is explainable.

### Files changed

* `app.py` — added target idea count logic, second-pass Gemini generation, idea generation counts, and UI copy showing accepted/target/generated/rejected.
* `docs/PROJECT_MEMORY.md` — recorded that Discovery idea volume should scale with selected signal volume.
* `docs/INTEGRATIONS.md` — documented the article idea counts contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Do not fill the UI with weak mechanical fallback ideas when Gemini returns some valid ideas. Use a second journalist/SEO Gemini pass first.
* For 20+ selected signals, target 16 validated ideas while still allowing duplicate/SEO-quality filters to reject bad candidates.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `POST /api/sites/6/article-ideas` with 25 live Discovery signals now returns counts `target=16`, `generated=21`, `accepted=15`, `rejected=6`, `signals=24`.

### Risks / TODO

* The quality filter can still return fewer than target when many model candidates duplicate existing/planned content or fail SEO/editorial validation; the UI now exposes that instead of hiding it.

## 2026-07-08 — Normalize Discovery topic queries

### Summary

* Fixed topic query extraction so short meaningful terms such as `AI` and `UGC` are preserved.
* Normalized `user generated content` to `ugc` and `e-commerce` to `ecommerce`.
* Stopped dropping category-defining terms only because they appear in a brand/domain name.
* Changed source relevance matching to whole-word matching so unrelated substrings do not pass Reddit filtering.
* Expanded search and Reddit source fetching to use multiple normalized query candidates instead of one fragile query.

### Files changed

* `app.py` — updated Discovery topic normalization, keyword extraction, query candidates, search suggestion variants, and Reddit query/scoring behavior.
* `docs/PROJECT_MEMORY.md` — recorded durable topic-normalization and whole-word relevance rules.
* `docs/INTEGRATIONS.md` — documented normalized query candidates and multi-query Reddit/search behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Discovery fixes must stay site-agnostic; `AI/UGC/ecommerce` handling is category normalization, not a one-site exception.
* Reddit returning `429` remains a source degradation and should be shown as a warning, not silently treated as real absence of discussion demand.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `GET /api/sites/6/topic-signals?range=week` now uses query `ai ugc creation ecommerce`, returns 84 raw search suggestions, 20 kept search-demand signals, and shows Reddit query variants/429 degradation separately.
* Verified `POST /api/sites/6/article-ideas` returned four SEO-rationalized article ideas from the normalized `ai ugc` signals, with one similar idea rejected.

### Risks / TODO

* Reddit RSS is still rate-limiting multi-period calls; the next robustness step should be caching Reddit source responses or adding a non-Reddit discussion source fallback.

## 2026-07-08 — Split Discovery signal sources

### Summary

* Split Discovery into source-aware search-demand and Reddit discussion signals.
* Made it explicit that the period selector affects Reddit only, not Google autocomplete demand signals.
* Added API metadata for raw, kept, filtered, deduped, source limit, and Reddit time bucket counts.
* Expanded reusable autocomplete query variants and kept the journalist/SEO idea generator as the step that turns raw signals into article ideas.
* Replaced the mechanical signal-to-title idea generator with a Gemini journalist/SEO prompt and strict idea validation requiring SEO intent and rationale.

### Files changed

* `app.py` — added source metadata to topic-signal fetchers/API, grouped Discovery UI rendering by source, default-checked usable signals, let idea generation use all visible signals if none are manually selected, and required generated ideas to include SEO intent/rationale.
* `docs/PROJECT_MEMORY.md` — recorded durable Discovery rules about raw signals vs article ideas and source-specific period behavior.
* `docs/INTEGRATIONS.md` — documented the updated `/api/sites/{site_id}/topic-signals` contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Search-demand autocomplete is treated as a non-time-filtered audience signal source.
* Reddit remains the period-controlled discussion source, with 3-month and 6-month UI ranges mapped to Reddit's year bucket where needed.
* Raw signals must remain inputs for the journalist/SEO prompt; they are not final article titles.
* Article idea generation should reject direct copies of raw signal titles and reject ideas missing durable SEO rationale.

### Checks run

* `python3 -m py_compile /tmp/blogcore-work/app.py`
* Deployed updated `app.py` and memory docs to `/var/www/blog.yas.ooo`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Ran `git diff --check`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `GET /api/sites/6/topic-signals?range=6m` returns `sources.popularSearches.rangeApplies=false`, `sources.reddit.rangeApplies=true`, Reddit `bucket=year`, combined `signals`, and raw/filtered/kept counts.
* Verified live dashboard HTML for site `id=6` contains `Discovery inputs`, `Reddit: last week`, `Generate SEO article ideas`, and the source-specific UI copy.
* Verified `POST /api/sites/6/article-ideas` with live Discovery signals returned four journalist-style SEO ideas with `seo_intent` and `seo_rationale` and did not append mechanical fallback titles after valid Gemini results.

### Risks / TODO

* Search-demand autocomplete can still return fewer visible cards than the source limit after dedupe/relevance/global-topic filters; the UI now shows raw/filtered/kept counts to make this explicit.

## 2026-07-06 — Generate Threads-specific media images

### Summary

* Stopped reusing Instagram carousel slides as Threads media.
* Added separate Threads image generation through Gemini Image.
* Threads media is now one natural 4:5 JPEG with no overlay text, no logo, no UI screenshot, and no banner/advertising composition.
* Threads media is stored separately under `data/social_assets/{site_id}/{job_id}/threads/image-01.jpg`.

### Files changed

* `app.py` — added Threads-specific image prompt and media generation/storage.
* `docs/PROJECT_MEMORY.md` — recorded that Threads should generate separate native images rather than reuse Instagram creatives.
* `docs/INTEGRATIONS.md` — documented Threads media storage and visual rules.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Threads image style should be simpler and more candid than Instagram carousel creative.
* Threads images must not contain text overlay; the post text carries the conversation.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Regenerated the test Threads draft for existing `myugc.studio` article `0619c746c0433e10b6ce64d4`.
* Verified new Threads draft `social_posts.id=15` is question-led, `224/500` UTF-8 bytes, and stores `content_json.threads.mediaUrls[0]` as `/threads/image-01.jpg`.
* Verified `/sites/6/social-posts/15/threads` renders and includes the Threads-specific image.
* Verified `/sites/6/social-assets/0619c746c0433e10b6ce64d4/threads/image-01.jpg` returns HTTP `200` with `Content-Type: image/jpeg`.
* Visually inspected the generated Threads image: simple workspace/social-photo style, no banner layout or readable ad text.

### Risks / TODO

* Threads actual publishing is still pending; this task updates the draft payload and preview assets.

## 2026-07-05 — Make Threads drafts native and media-aware

### Summary

* Replaced generic social copy for Threads with a Threads-specific prompt.
* Threads drafts now aim for a short conversational question or opinion instead of promotional ad copy.
* Threads draft metadata can attach one existing generated image from the article's Instagram carousel assets.
* Added a Threads draft preview route that shows the post text, byte count, and attached image.
* Added a `Threads` preview action on content/planned cards when a Threads draft exists.

### Files changed

* `app.py` — added Threads-specific prompt/generator, media lookup, preview route, and preview button.
* `docs/PROJECT_MEMORY.md` — recorded native Threads style and media attachment rules.
* `docs/INTEGRATIONS.md` — documented Threads media metadata and preview route.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Threads should not reuse LinkedIn-style or ad-style copy.
* When available, a Threads post should use one relevant image from already generated social assets instead of being text-only.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Regenerated the test Threads draft for existing `myugc.studio` article `0619c746c0433e10b6ce64d4`.
* Verified new Threads draft `social_posts.id=13` is question-led, `280/500` UTF-8 bytes, and stores `content_json.threads.mediaUrls[0]`.
* Verified `/sites/6/social-posts/13/threads` renders the post text and includes `slide-01.jpg`.
* Verified the attached `slide-01.jpg` returns HTTP `200` with `Content-Type: image/jpeg`.

### Risks / TODO

* Actual Threads publishing is still pending; this task prepares a more realistic draft payload and review surface.

## 2026-07-05 — Add Threads social channel

### Summary

* Added Threads as a separate social channel in Setup, Distribution, active-channel gating, content-card status icons, and factory settings persistence.
* Added SQLite migrations for `content_jobs.threads_*` status fields and `autopublish_settings.threads_include_link`.
* Added Threads credential configuration and test-connect support through the Threads `/me` API probe.
* Added Threads draft generation through the text social draft path with Threads-specific 500 UTF-8 byte validation.
* Added byte-aware shortening so emoji and non-ASCII languages do not silently exceed the Threads limit.

### Files changed

* `app.py` — added Threads provider config, migrations, UI/settings integration, byte-aware validation, and text draft generation.
* `docs/PROJECT_MEMORY.md` — recorded Threads as a separate channel with a 500 UTF-8 byte rule.
* `docs/INTEGRATIONS.md` — documented Threads credentials, connection test, and validation behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Threads is not X/Twitter and not Instagram; it has its own provider, status fields, credentials, include-link setting, and draft validation.
* Threads uses byte-aware validation because the platform counts emoji/non-ASCII text by UTF-8 bytes.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live SQLite migrations added `content_jobs.threads_*` columns and `autopublish_settings.threads_include_link`.
* Generated a Threads draft for existing `myugc.studio` imported article `0619c746c0433e10b6ce64d4` using a temporary generation-only Threads gate, then restored the original `myugc.studio` social settings.
* Verified the generated Threads draft stores `char_count=324`, `max_chars=500`, and validation JSON `byteCount=324`, `maxBytes=500`.
* Verified live `/sites/6` renders Threads in Setup/Distribution, `threads_include_link`, and the Distribution channel value `threads`.

### Risks / TODO

* Actual Threads publishing is still pending; this task prepares connection setup and validated drafts for the publisher.

## 2026-07-05 — Tighten Instagram caption target length

### Summary

* Kept Instagram's technical hard caption limit at 2200 characters.
* Added a practical generated-caption target of 700 characters for Instagram carousel drafts.
* Updated the Instagram prompt to produce compact captions with one hook, short context, one CTA, and at most three hashtags.
* Made normalization shorten Instagram captions to the practical target instead of only checking the hard limit.

### Files changed

* `app.py` — added Instagram target character limit and tightened prompt/normalization/validation.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that Instagram captions should be much shorter than the hard limit.
* `docs/INTEGRATIONS.md` — documented the 700-character target alongside the 2200-character hard limit.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* The hard limit protects against API rejection; the 700-character target protects feed readability.
* Carousel slide images should carry the detailed story; the shared caption should stay compact.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Updated the existing test Instagram draft `social_posts.id=11` from 1113 chars to a 279-char caption while keeping the same generated slides.
* Verified `/sites/6/social-posts/11/instagram-carousel` renders the shorter caption.

### Risks / TODO

* Other existing Instagram social draft rows, if any, are not automatically regenerated unless explicitly updated or recreated.

## 2026-07-05 — Clarify Instagram intermediary and caption model

### Summary

* Changed Instagram Setup fields from direct Graph credentials to third-party intermediary API credentials.
* Stopped Instagram test-connect from calling Instagram Graph API directly; it now validates that intermediary credentials are saved until the intermediary contract is known.
* Updated Instagram carousel preview so it no longer displays separate text captions under each slide.
* Labeled the single shared Instagram caption as the caption for the whole carousel.

### Files changed

* `app.py` — updated Instagram credential fields, test-connect behavior, and carousel preview wording/layout.
* `docs/PROJECT_MEMORY.md` — recorded that Instagram publishing must use the intermediary server and that Instagram has one shared carousel caption.
* `docs/INTEGRATIONS.md` — documented intermediary credential fields and removed direct Graph publishing assumptions.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Blog Core should not publish Instagram directly through Instagram Graph API; publishing will use the project's intermediary server.
* Per-slide headline/subtext are for image generation and visual overlay review only. The published Instagram post has one shared caption for the full carousel.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified `/sites/6/social-posts/11/instagram-carousel` contains `Single Instagram carousel caption`.
* Verified the live preview no longer contains the old `slide-copy` per-slide caption block.

### Risks / TODO

* The exact intermediary publish/test endpoints still need to be wired once the API contract is provided.

## 2026-07-05 — Add real Instagram carousel creative drafts

### Summary

* Added Instagram as a per-site social channel in Setup, Distribution, active-channel gating, and content-card social status icons.
* Added Instagram SQLite status fields and `instagram_include_link` persistence.
* Added Instagram carousel draft generation with caption length validation, 5-10 slide planning, and real Gemini Image JPEG slide generation.
* Stored generated slide metadata in `social_posts.content_json.instagramCarousel` and slide files under ignored `data/social_assets/...`.
* Added routes to serve generated social assets and review the actual Instagram carousel creative.
* Added an `IG carousel` action for rows that already have an Instagram creative draft.

### Files changed

* `app.py` — added Instagram provider/config/migrations, Gemini Image JPEG generation, carousel asset storage, review routes, and UI actions.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that Instagram drafts must be real publishable JPEG creatives, not SVG/mock previews.
* `docs/INTEGRATIONS.md` — documented Instagram limits, Gemini Image env usage, asset storage, and preview route.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Instagram uses Gemini Image through the Gemini Interactions API and stores JPEG slide assets because the live endpoint accepts `image/jpeg` for `response_format.mime_type`.
* Instagram draft generation is still gated by per-site Distribution selection plus configured/connected Setup credentials.
* Review must show the real generated slide files that the publisher can use, not an SVG approximation.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live SQLite migrations added `content_jobs.instagram_*` columns and `autopublish_settings.instagram_include_link`.
* Generated a real Instagram draft for existing `myugc.studio` imported article `0619c746c0433e10b6ce64d4` using a temporary generation-only Instagram gate, then restored the original `myugc.studio` social settings.
* Verified `social_posts.id=11`, `channel=instagram`, `char_count=1113`, `max_chars=2200`, `status=DRAFT`.
* Verified six generated JPEG slides exist under `data/social_assets/6/0619c746c0433e10b6ce64d4/instagram/`.
* Verified `slide-01.jpg` returns HTTP `200` with `Content-Type: image/jpeg`.
* Verified `/sites/6/social-posts/11/instagram-carousel` renders and includes all six slide images.

### Risks / TODO

* Replaced/deprecated by 2026-07-05 intermediary decision: direct Instagram Graph publishing is not the target. This task creates the real creative assets and review surface for the intermediary publisher to consume.
* The current social draft endpoint is synchronous; generating several images can take around a minute and should eventually move to the same background job model used for longer source-factory generation.

## 2026-07-05 — Add Pinterest social draft support

### Summary

* Added Pinterest as a per-site social channel in Setup, Distribution, active-channel gating, and content-card status icons.
* Added SQLite migrations for Pinterest content job status fields and `pinterest_include_link`.
* Added Pinterest credential configuration and test-connect support using Pinterest API v5 user account probing.
* Added native Pinterest pin draft generation based on an article: pin title, description/caption, overlay text, alt text, 2:3 image prompt, recommended size, and optional destination URL.
* Stored Pinterest creative metadata in `social_posts.content_json.pin` while keeping the description/caption in `content_text`.

### Files changed

* `app.py` — added Pinterest provider config, migrations, UI, settings persistence, active-channel support, and pin creative draft generation.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that Pinterest drafts are native pin creative specs, not plain text posts.
* `docs/INTEGRATIONS.md` — documented Pinterest draft fields and limits.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Pinterest is gated the same way as other social channels: selected in Distribution and configured/connected in Setup.
* Pinterest draft generation creates a pin creative spec for downstream image generation/publishing; it does not upload an image or publish to Pinterest yet.
* Pinterest description limit is treated as 500 characters; pin title, overlay text, alt text, and image prompt have their own validation limits.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live SQLite migrations added `content_jobs.pinterest_*` columns and `autopublish_settings.pinterest_include_link`.
* Verified live `/sites/7` renders Pinterest in Setup, Distribution, include-link settings, and content-card social icons.
* Verified Pinterest draft generation on a temporary test site creates `social_posts.channel=pinterest` with `content_json.pin.imageAspectRatio=2:3`, `recommendedSize=1000x1500`, overlay text, image prompt, and a 500-char-limited description; then deleted the temporary test site.

### Risks / TODO

* Real Pinterest image rendering/upload and pin publishing are still future publisher work. The current implementation prepares the native pin creative spec and stores it for the publishing pipeline.

## 2026-07-05 — Add Discovery idea review before queueing

### Summary

* Changed Discovery from "checked signals immediately create jobs" to a two-step workflow.
* Selected signals now generate reviewable article idea candidates first.
* Operators can select specific generated ideas and then add only those ideas to Planned publications.
* Added server-side similarity checks against existing imported/published and planned site content before ideas are shown and again before queueing.
* Added compact UI for generated idea review and duplicate-filter messaging.

### Files changed

* `app.py` — added article idea candidate generation, duplicate similarity helpers, `/article-ideas/queue`, and Discovery idea review UI.
* `docs/PROJECT_MEMORY.md` — recorded the durable two-step Discovery workflow and duplicate-check rule.
* `docs/INTEGRATIONS.md` — documented the split idea-generation and queue endpoints.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* `POST /api/sites/{site_id}/article-ideas` returns ideas only and must not create `content_jobs`.
* `POST /api/sites/{site_id}/article-ideas/queue` is the only Discovery endpoint that creates planned article jobs.
* Duplicate checks compare generated idea titles and original signal titles against existing site topics, slugs, and published URLs.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live SoloCruz `/article-ideas` generated ideas from selected Discovery signals without changing the planned jobs count.
* Verified a near-duplicate SoloCruz test topic, `Best Cruises for Solo Travelers`, is rejected with `rejectedSimilar` against imported live content.
* Verified `/article-ideas/queue` creates a `QUEUED` job on a temporary test site, then deleted the temporary site from Blog Core.
* Verified live `/sites/7` contains `Generate article ideas`, `Article ideas to add`, `Add selected to queue`, and the `/article-ideas/queue` client call.

### Risks / TODO

* Similarity checking is token-based and intentionally conservative; future work can improve it with embeddings or source-factory/site-specific editorial constraints.

## 2026-07-05 — Replace news-based discovery signals

### Summary

* Replaced Google News RSS-based Discovery signals with non-news popular search suggestions.
* Kept Reddit top discussions as the discussion signal source.
* Made the Discovery topic seed prefer the site's Discovery direction and category hint, so connected sites use their intended topic profile instead of weak product-description words.
* Added filtering for navigation/source-specific autocomplete tails such as YouTube, Reddit, and marketplace-brand searches.
* Updated the Discovery UI wording so it no longer claims to use Google Trends or news-like topic signals.

### Files changed

* `app.py` — removed `news.google.com` usage from topic discovery, added Google autocomplete/search suggestion fetching, updated API counts/source labels, and changed Discovery UI copy.
* `docs/PROJECT_MEMORY.md` — recorded the global product rule that Discovery must use non-news topic-demand signals and marked Google News RSS discovery as replaced.
* `docs/INTEGRATIONS.md` — documented the new popular search suggestion source and range behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* This Discovery rule applies globally to all existing and future sites, not only `solocruz.com`.
* Google autocomplete/search suggestions are treated as broad search-demand hints, not as the official Google Trends API.
* The selected range affects Reddit only; Google autocomplete suggestions do not support a time range.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `GET /api/sites/7/topic-signals?range=month` returns `query=solo cruise travel`, `counts.popularSearches`, and `source=popular_search` signals.
* Verified the live SoloCruz Discovery response no longer contains `news.google`, `youtube`, `costco`, `fees increase`, or the previous Bordeaux trade-promo example.
* Verified the live `/sites/7` page shows `Popular topic trends and discussions` and no longer shows `Google Trends`/`Google topic signals` UI wording.

### Risks / TODO

* Google autocomplete can still temporarily fail or return sparse suggestions; failures are surfaced as warnings and must not be replaced with news fallback.

## 2026-07-04 — Delegate migrated jobs to source factories

### Summary

* Stopped using Blog Core's generic article generator for migrated/source-factory jobs.
* Added a legacy factory bridge for rows with `sources_json.migratedFrom` and `oldFactoryJobId`.
* AIREP24 migrated jobs now delegate generation to `content-factory-airep24` and sync validated drafts back into Blog Core.
* Reset two weak AIREP24 drafts that had been generated by the generic Blog Core prompt back to `QUEUED`.

### Files changed

* `app.py` — added legacy factory endpoint mapping, async source-factory generation bridge, sync-back logic, and UI wording for background generation.
* `docs/PROJECT_MEMORY.md` — recorded that imported legacy jobs must use the source factory's own requirements and generator.
* `docs/INTEGRATIONS.md` — documented the source-factory bridge contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Imported/source-factory jobs are source-factory authoritative. Blog Core is the dashboard/control plane for those rows.
* Source factory validation errors should be surfaced as `ERROR`; Blog Core must not keep weaker generic drafts as ready content.
* Legacy generation runs asynchronously from Blog Core so long source-factory generation and image generation do not hit Gunicorn's 120 second request timeout.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified Blog Core generation for AIREP24 job `6b7d0e8df768437cabeb54f2` delegates to `content-factory-airep24`.
* Verified the first blocking bridge attempt hit Gunicorn timeout, then changed the bridge to return `GENERATING` and run the source-factory call in a background worker.
* Verified `content-factory-airep24` rejected job `6b7d0e8df768437cabeb54f2` with its own validation error instead of accepting the weaker generic draft.
* Added visible planned-row error text so source-factory validation failures are shown in Blog Core.
* Reset AIREP24 generic drafts `7342dcb79c4d422b8b3f1007` and `bfbe6c3ac8ee4b93a4dce5c3` to `QUEUED` for regeneration through the source factory.

### Risks / TODO

* Background generation state is currently tracked through `content_jobs.status` and logs. A fuller job runner/poller would be more robust than in-process daemon threads.
* `content-factory-airep24` currently rejects at least one migrated job because its own prompt/validation repair loop cannot satisfy internal-link/title/H3 constraints; that must be fixed in the source factory, not bypassed in Blog Core.

## 2026-07-04 — Hide bootstrap actions on imported site cards

### Summary

* Removed `Scan design`, `Build preview`, and `Install /blog` from dashboard cards for sites that already have imported live content.
* Added a compact imported live-site status badge with the imported page count.
* Kept the relevant actions for imported sites: `Manage`, `Open live blog`, and `Delete`.

### Files changed

* `app.py` — dashboard site query now includes imported page count and renders setup/bootstrap buttons only for non-imported sites.
* `docs/PROJECT_MEMORY.md` — recorded that imported live-site cards should not show new-site bootstrap/install actions.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* A site is treated as imported on the dashboard when it has at least one `content_jobs.status=IMPORTED` row.
* New-site bootstrap actions remain available for sites that do not yet have imported live content.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified the AIREP24 dashboard card contains `Manage`, `Imported live site`, `Open live blog`, and `Delete`.
* Verified the AIREP24 dashboard card no longer contains `Scan design`, `Build preview`, or `Install /blog`.

### Risks / TODO

* The Setup tab still contains technical settings for operators who explicitly enter site management; this change only simplifies the main dashboard card.

## 2026-07-04 — Render local draft previews with source-site templates

### Summary

* Changed `Preview draft` for local imported sites to render through the real source-site HTML template from `root_path`.
* Preserved source-site assets, header/footer, and page classes while replacing the article/content area with the Blog Core draft.
* Added `base href` for the source domain and `noindex,nofollow` metadata to draft previews.

### Files changed

* `app.py` — added local webroot template discovery and source-site draft preview rendering before the generic Blog Core fallback.
* `docs/PROJECT_MEMORY.md` — recorded that local imported-site previews must use source-site templates/assets.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* `Preview draft` for `local_path` sites should use `sources_json.targetPath` or the source URL to find the closest existing `index.html` in the site's webroot.
* Generic Blog Core preview rendering remains only as a fallback when no local template can be found.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified AIREP24 draft previews include `base href="https://airep24.com/"`, `/assets/css/site.min.css`, `site-header`, `site-main`, and `factory-article-layout`.
* Verified AIREP24 draft previews no longer include `blog-core-page` or `/sites/9/blog-core.css`.

### Risks / TODO

* Preview still serves from the Blog Core admin route, but it now uses the source site's template and absolute source-site assets. Final publish-back into `/var/www/airep24.com` remains separate work.

## 2026-07-04 — Gate social drafts behind configured channels

### Summary

* Stopped offering `Social drafts` actions when a site has no configured/connected social channels selected for autopublish.
* Removed the fallback that generated drafts for every social provider when channels were missing.
* Changed the social draft API to return `400` without creating drafts when no active social channel exists.

### Files changed

* `app.py` — added active-channel gating for social draft buttons and API generation.
* `docs/PROJECT_MEMORY.md` — recorded the durable product rule that social drafts require selected and configured/connected channels.
* `docs/INTEGRATIONS.md` — documented the `social-drafts` endpoint's active-channel contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Distribution selection is not enough to generate social drafts. A channel must also be configured or connected in Setup.
* Blog Core must not silently create social drafts for all providers as a fallback.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified AIREP24 site `id=9` has no rendered `social-draft-action` buttons or `generateSocialDrafts` click handlers when no social connections exist.
* Verified direct `POST /api/sites/9/content-jobs/{draft_id}/social-drafts` returns HTTP 400 and leaves `social_posts` unchanged at 0.

### Risks / TODO

* Real per-provider publishing/OAuth completion remains separate parity work.

## 2026-07-04 — Add generation progress and draft preview

### Summary

* Added persistent in-page progress for bulk generation.
* Added `Preview draft` actions for `DRAFT` planned rows and Content inventory rows.
* Added an admin draft preview route that renders generated draft HTML with the site's scanned design shell and Blog Core CSS.

### Files changed

* `app.py` — added draft preview buttons, preview HTML/CSS routes, bulk progress UI, and control disabling during bulk operations.
* `docs/PROJECT_MEMORY.md` — recorded the durable UX rule for long-running generation and draft previews.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Draft preview is an admin dashboard route under `/sites/<site_id>/content-jobs/<job_id>/preview`; it does not publish the draft to the live source site.
* Bulk generation progress stays visible inside Planned publications and tells the operator to keep the tab open.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` contains `Preview draft`, `bulkProgress`, and the `Keep this tab open` progress text.
* Verified an AIREP24 draft preview returns HTTP 200 and includes the generated article title/content.
* Verified `/sites/9/blog-core.css` returns HTTP 200 CSS for draft preview styling.

### Risks / TODO

* Draft preview is for review only. Publishing the approved draft back into `/var/www/airep24.com` is still separate publish-back work.

## 2026-07-04 — Add bulk actions for planned task groups

### Summary

* Added selection checkboxes to canonical planned task groups.
* Added bulk actions for `Generate selected` and `Delete selected`.
* Added a bulk planned-groups API for group-level delete operations.
* Kept grouped planned tasks as the operator-facing model while preserving legacy per-language rows in SQLite.

### Files changed

* `app.py` — added stable planned group IDs, bulk selection UI, bulk delete endpoint, and browser-side sequential bulk generation.
* `docs/PROJECT_MEMORY.md` — recorded the durable bulk-operation behavior for planned task groups.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Bulk generate runs one selected primary job per canonical group as separate browser requests to avoid one long HTTP request timing out.
* Bulk delete removes all legacy rows in the selected canonical groups, plus their content logs and social draft rows, but never touches live source-site files.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` renders 14 grouped planned rows, 14 stable group IDs, bulk selection UI, `Generate selected`, and `Delete selected`.
* Verified `POST /api/sites/9/planned-groups/bulk` with an empty selection returns HTTP 400.
* Verified `POST /api/sites/9/planned-groups/bulk` with a fake group ID returns HTTP 404.
* Verified AIREP24 still has 56 queued legacy rows after non-destructive checks.

### Risks / TODO

* The underlying schema still stores legacy language rows in `content_jobs`. A future schema pass should introduce explicit parent tasks and language output rows.
* Bulk generate can still take time because each selected task calls Gemini; the browser keeps it as separate requests to avoid server timeout.

## 2026-07-04 — Collapse planned jobs by canonical task

### Summary

* Updated the planned publications UI so legacy per-language rows are grouped into one canonical task per topic/path.
* Corrected AIREP24 site language configuration from EN/DE/ES/FR back to EN only.
* Planned rows now show active generation languages from site settings and show old extra language rows as legacy variants.

### Files changed

* `app.py` — added planned-job grouping by canonical group/base path and language-aware primary-row selection.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that generation tasks should be canonical and language expansion should come from site settings.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Preserve old per-language rows in SQLite for traceability, but do not show them as separate generation tasks.
* Use `sites.languages` as the active language set for new generation. For AIREP24, active languages are now `["en"]`.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Updated live AIREP24 site `id=9` `sites.languages` to `["en"]`.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` planned block now renders 14 planned rows instead of 56.
* Verified the database still preserves 56 queued legacy rows grouped into 14 canonical groups.
* Verified planned rows show `Generates: EN` and legacy variant chips.

### Risks / TODO

* The generation endpoint still operates on a single primary `content_jobs` row. Full multi-language generation should be implemented as a canonical parent task with language child outputs in a future schema/publisher pass.

## 2026-07-04 — Point imported-site open action to live blogs

### Summary

* Changed the primary top/dashboard open action for imported sites from generated Blog Core previews to the live source-site blog URL.
* Imported local-path sites now show `Open live blog` and link to `https://domain/blog/`.

### Files changed

* `app.py` — added primary site link selection based on imported inventory and live blog URL generation.
* `docs/PROJECT_MEMORY.md` — recorded that imported blogs should open the live source-site blog, not generated previews.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Generated previews remain available as a technical Build preview flow, but they are not the main open action for existing imported blogs.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` contains `Open live blog` and `https://airep24.com/blog/`, and no longer contains `/previews/9/blog/`.
* Verified the dashboard contains live blog links for imported sites.

### Risks / TODO

* The generated preview files still exist under `/previews/...`; they are not deleted because they may still be useful for technical checks.

## 2026-07-04 — Add content type filter chips

### Summary

* Added content-type filters to the Content inventory toolbar.
* Operators can now switch between `All`, `Blog`, `SEO money`, `Home`, and `Other` while keeping the selected language.
* Pagination and the content jobs API now preserve and expose the selected content type.

### Files changed

* `app.py` — added `content_job_page_type`, server-side `content_type` filtering, filter chips, pagination query preservation, API response fields, and compact toolbar styling.
* `docs/PROJECT_MEMORY.md` — recorded the durable Content inventory filtering rule.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Type filters are server-side, matching the existing language filter behavior.
* Available content types are calculated after the language filter so the chips reflect what exists in the selected language.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified API counts for AIREP24 EN: `All=31`, `Blog=20`, `SEO money=10`, `Home=1`.
* Verified live `/sites/9?content_lang=en&content_type=seo_money_page#content` contains type filter chips and preserves `content_type=seo_money_page` in language links.

### Risks / TODO

* Content inventory still includes both imported live records and queued content records according to the current underlying list behavior; planned jobs also remain visible in the Distribution planned block.

## 2026-07-04 — Fully migrate AIREP24 legacy factory jobs

### Summary

* Migrated all legacy `jobs` from `/var/www/content-factory-airep24/factory.sqlite` into Blog Core site `id=9`.
* Preserved old factory job IDs, content type, page kind, locale/language, target path, canonical group, legacy status, and social status columns in Blog Core metadata/columns.
* Expanded the `Planned publications` dashboard block so it shows all planned jobs instead of only the first 12, with content type, language, and target path metadata.

### Files changed

* `app.py` — raised planned publication display limit to 200 and added compact language/type/target-path metadata to planned rows.
* `docs/PROJECT_MEMORY.md` — replaced the partial AIREP24 import note with the complete migration state.
* `docs/SEO_MEMORY.md` — recorded AIREP24 SEO money-page migration behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Old AIREP24 `NEW` jobs were migrated as Blog Core `QUEUED` planned jobs, not as imported live pages.
* Old AIREP24 `PUBLISHED` jobs were migrated as Blog Core `IMPORTED` inventory records.
* The old `content-factory-airep24` process/database was left in place; this task copied state into Blog Core without deleting the source factory.

### Checks run

* Created live DB backup `/var/www/blog.yas.ooo/data/blog_core.sqlite3.before-airep24-full-migration-20260704144135.bak`.
* Migrated 64 legacy records: 56 `QUEUED` and 8 `IMPORTED`.
* Verified Blog Core site `id=9` now has 80 `content_jobs`: 24 imported inventory records and 56 planned jobs.
* Verified planned jobs consist of 20 blog jobs and 36 SEO money-page jobs across EN/DE/ES/FR.
* Verified 64 records have `sources_json.migratedFrom=content-factory-airep24`.
* Ran `python3 -m py_compile app.py` locally and on the VPS.
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` HTML contains 56 planned rows, planned metadata, SEO money-page badges, and migrated target paths.

### Risks / TODO

* Final publish-back from Blog Core into `/var/www/airep24.com` for these queued jobs still depends on the broader local static publisher/parity work.
* The legacy `content-factory-airep24` process remains online as a source/rollback reference until an explicit cutover/removal decision is made.

## 2026-07-04 — Import airep24.com from local VPS webroot

### Summary

* Connected `airep24.com` to Blog Core as site `id=9`.
* Confirmed the active nginx config serves `airep24.com` from `/var/www/airep24.com`.
* Scanned the live homepage design; Gemini inferred the AIREP24 topic profile for Discovery settings.
* Imported existing AIREP24 blog pages directly from the local VPS webroot.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `airep24.com`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `airep24.com` is managed as a local-path site because the authoritative static site files are present on the same VPS at `/var/www/airep24.com`.
* The `/blog/` hub was imported as metadata but remains hidden from the Content inventory; the visible inventory contains the 15 article pages.

### Checks run

* Verified `airep24.com` was not already present in the Blog Core database.
* Checked nginx configs and confirmed the active domain root is `/var/www/airep24.com`.
* Verified `/var/www/airep24.com` contains 61 HTML files, including 16 under `/blog/`.
* Verified `https://airep24.com/sitemap.xml` exposes 16 `/blog/` URLs.
* Created site `id=9` with `access_type=local_path`, `root_path=/var/www/airep24.com`, and language EN.
* Ran `POST /api/sites/9/scan`; Gemini returned `source=gemini` topic profile data.
* Local Blog Core discovery returned `source=local_webroot`, 16 candidates, 0 warnings, 0 duplicates.
* Imported site `id=9` from local webroot: imported 16, skipped 0, errors 0.
* Verified imported counts: EN 16, all `pageType=blog`; 1 is the `/blog/` hub metadata record and 15 are visible article records.
* Verified all 16 imported records have `sources_json.webrootPath` under `/var/www/airep24.com` and `importMethod=direct_webroot`.
* Ran `POST /api/sites/9/bootstrap-preview`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/9#content` contains `AIREP24`, `/var/www/airep24.com`, `Content inventory`, language switching, `LIVE / IMPORTED`, and `Social drafts`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* Publishing new generated AIREP24 articles back into `/var/www/airep24.com` is still future publish-back work; this task imported and connected the existing blog inventory/control-plane records.

## 2026-07-04 — Clean VPS temporary files and caches

### Summary

* Inspected VPS disk usage and large backup/temp/cache files.
* Removed safe rebuildable caches and temporary files.
* Left active Chromium/Playwright runtime/cache paths untouched because processes were using them.
* Left `.git/objects/pack` files untouched because they are required repository data, not disposable backups.

### Files changed

* `docs/CHANGELOG_AI.md` — logged this VPS maintenance task.

### Decisions

* Cleaned only recoverable cache/temp/log data and one obsolete dev SQLite backup.
* Did not delete working databases, webroot HTML, source trees, `node_modules`, or Git pack files.

### Checks run

* Checked `df -hT`; root filesystem went from 79G used / 18G free / 83% to 76G used / 21G free / 79%.
* Removed `.next`/Turbopack caches for `build.yas.ooo`, `my-ugc-studio-saas`, `my-ugc-studio-saas-staging`, and `revaltix`.
* Removed root tool caches: pip, Prisma, TypeScript, cloud-code, node-gyp, and Jedi.
* Removed `/tmp/shopify-new`, `/tmp/tsx-0`, `/tmp/inspectroute-backend.tgz`, `/tmp/yas-agent-vps.tgz`, and old `.tmp` files under `/root/.gemini`.
* Truncated `/var/www/my-ugc-studio-saas/logs/access.log`.
* Ran `apt-get clean`.
* Ran `journalctl --vacuum-size=100M`.
* Removed `/var/www/highpurebreed/backups/dev.sqlite.before-calendly-ai-20260622182214.bak`.
* Verified `http://127.0.0.1:3299/health` still returns OK.

### Risks / TODO

* `/tmp/snap-private-tmp/snap.chromium` and `/root/.cache/ms-playwright` still use about 2GB combined, but active Chromium/Playwright processes were using them, so they were intentionally not removed.
* Large `.git/objects/pack` files remain the biggest large-file category; do not delete them manually.

## 2026-07-03 — Add channel-specific social draft adaptation

### Summary

* Added per-channel social draft generation for content jobs.
* Added strict character-limit validation before saving social drafts.
* Preserved article language for social drafts using `sources_json.language` with site-language fallback.
* Added a `Social drafts` action to content cards and updated social status icons to show drafted channel state.

### Files changed

* `app.py` — expanded `social_posts` schema, added social channel limits, language-aware post generation, validation/shortening, API route, content-card action, and JS handler.
* `docs/PROJECT_MEMORY.md` — recorded durable social draft rules and channel limits.
* `docs/INTEGRATIONS.md` — documented the social draft endpoint, storage contract, language behavior, and limits.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Store adapted social texts in `social_posts` before real publishing, one row per `job_id + channel` draft attempt.
* Use conservative strict limits: LinkedIn 3000, Telegram 4096, X/Twitter 280, Tumblr 4096.
* Do not rely on social platforms truncating overlong text; saved drafts must validate with `char_count <= max_chars`.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Generated EN social drafts for LaycanMatch site `id=8`, job `38eae646b39daefef960f375`: LinkedIn 1626/3000, Telegram 1224/4096, X/Twitter 254/280, Tumblr 1064/4096.
* Verified saved `social_posts` rows have `status=DRAFT`, `language=en`, `char_count <= max_chars`, and matching `content_jobs` channel statuses set to `drafted`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/8#content` contains `Social drafts` actions and drafted channel icons.
* Generated a RU X/Twitter social draft for SoloCruz site `id=7`, job `6dc8145c44dcf8247dbf62e8`; result was `language=ru`, 261/280 characters, and Russian text.

### Risks / TODO

* Real provider publish calls are still pending; this task prepares validated social drafts but does not post them to LinkedIn, Telegram, X/Twitter, or Tumblr yet.
* Social draft generation currently calls Gemini once per channel; this can be optimized later into a single multi-channel generation call.

## 2026-07-03 — Import laycanmatch.com from local VPS webroot

### Summary

* Connected `laycanmatch.com` to Blog Core as site `id=8`.
* Confirmed the active nginx config serves `laycanmatch.com` from `/var/www/laycanmatch.com`.
* Scanned the live homepage design; Gemini inferred the LaycanMatch topic profile for Discovery settings.
* Imported existing LaycanMatch blog pages directly from the local VPS webroot.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `laycanmatch.com`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `laycanmatch.com` is managed as a local-path site because the authoritative static site files are present on the same VPS at `/var/www/laycanmatch.com`.
* The `/blog/` hub was imported as metadata but remains hidden from the Content inventory; the visible inventory contains the five article pages.

### Checks run

* Verified `laycanmatch.com` was not already present in the Blog Core database.
* Checked nginx configs and confirmed the active domain root is `/var/www/laycanmatch.com`.
* Verified `/var/www/laycanmatch.com` contains 44 HTML files, including 6 under `/blog/`.
* Verified `https://laycanmatch.com/sitemap.xml` exposes 6 `/blog/` URLs.
* Created site `id=8` with `access_type=local_path`, `root_path=/var/www/laycanmatch.com`, and language EN.
* Ran `POST /api/sites/8/scan`; Gemini returned `source=gemini` topic profile data.
* Local Blog Core discovery returned `source=local_webroot`, 6 candidates, 0 warnings, 0 duplicates.
* Imported site `id=8` from local webroot: imported 6, skipped 0, errors 0.
* Verified imported counts: EN 6, all `pageType=blog`.
* Verified all 6 imported records have `sources_json.webrootPath` under `/var/www/laycanmatch.com` and `importMethod=direct_webroot`.
* Ran `POST /api/sites/8/bootstrap-preview`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/8#content` contains `LaycanMatch`, `/var/www/laycanmatch.com`, `Content inventory`, language switching, and `LIVE / IMPORTED`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* Publishing new generated LaycanMatch articles back into `/var/www/laycanmatch.com` is still future publish-back work; this task imported and connected the existing blog inventory/control-plane records.

## 2026-07-03 — Import solocruz.com from local VPS webroot

### Summary

* Connected `solocruz.com` to Blog Core as site `id=7`.
* Confirmed the active nginx config serves `solocruz.com` from `/var/www/solocruz.com`.
* Scanned the live homepage design; Gemini inferred the SoloCruz topic profile for Discovery settings.
* Imported existing multilingual SoloCruz blog pages directly from the local VPS webroot.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `solocruz.com`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `solocruz.com` is managed as a local-path site because the authoritative static site files are present on the same VPS at `/var/www/solocruz.com`.
* The import kept existing live URLs as source-site authoritative records; Blog Core acts as inventory/control plane for the existing blog rather than changing public pages.

### Checks run

* Verified `solocruz.com` was not already present in the Blog Core database.
* Checked nginx configs and confirmed the active `000-solocruz.com.conf` root is `/var/www/solocruz.com`; the Hestia `/home/mysites/.../public_html` path has no blog HTML.
* Verified `https://solocruz.com/sitemap-blog.xml` exposes 75 blog URLs, 15 per EN/RU/ES/DE/FR.
* Created site `id=7` with `access_type=local_path`, `root_path=/var/www/solocruz.com`, and languages EN/RU/ES/DE/FR.
* Ran `POST /api/sites/7/scan`; Gemini returned `source=gemini` topic profile data.
* Local Blog Core discovery returned `source=local_webroot`, 75 candidates, 0 warnings, 0 duplicates.
* Imported site `id=7` from local webroot: imported 75, skipped 0, errors 0.
* Verified imported counts: EN 15, RU 15, ES 15, DE 15, FR 15; all are `pageType=blog`.
* Verified all 75 imported records have `sources_json.webrootPath` under `/var/www/solocruz.com` and `importMethod=direct_webroot`.
* Ran `POST /api/sites/7/bootstrap-preview`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/7#content` contains `SoloCruz`, `/var/www/solocruz.com`, `Content inventory`, language switching, and `LIVE / IMPORTED`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* Publishing new generated SoloCruz articles back into `/var/www/solocruz.com` is still future publish-back work; this task imported and connected the existing blog inventory/control-plane records.

## 2026-07-03 — Reimport myugc.studio from local VPS webroot

### Summary

* Corrected the `myugc.studio` import source from public sitemap to the actual local webroot on the VPS.
* Found that active nginx serves `myugc.studio` from `/var/www/landing`; `/var/www/my-ugc-studio` is not the public static blog root.
* Updated Blog Core site `id=6` to `root_path=/var/www/landing` and `access_type=local_path`.
* Cleared the prior site `id=6` imported inventory and reimported from local files.

### Files changed

* `docs/PROJECT_MEMORY.md` — marked the earlier public-sitemap import note as replaced and recorded the actual local webroot import state.
* `docs/CHANGELOG_AI.md` — logged this correction.

### Decisions

* For `myugc.studio`, `/var/www/landing` is the authoritative local source for current public blog HTML and sitemap files.
* The earlier public-sitemap import was replaced because the VPS already has the static public blog files locally.

### Checks run

* Read active `/etc/nginx/conf.d/myugc.studio.conf`; confirmed `root /var/www/landing`.
* Verified `/var/www/landing` contains local blog HTML files and sitemap files.
* Local Blog Core discovery returned `source=local_webroot`, 442 unique candidates, 0 warnings.
* Reimported site `id=6` from local webroot: imported 442, skipped 0, errors 0.
* Verified site `id=6` now has `root_path=/var/www/landing` and `access_type=local_path`.
* Verified every imported `content_jobs` row for site `id=6` has `sources_json.webrootPath` under `/var/www/landing`.
* Verified language counts: EN 88 stored records, DE 89, ES 89, FR 89, RU 87.
* Verified `/api/sites/6/content-jobs?language=en` returns 87 visible EN records after hiding the `/blog/` hub.
* Verified live dashboard HTML contains `/var/www/landing`, `LIVE / IMPORTED`, `My UGC Studio`, and language switching.

### Risks / TODO

* Publishing new generated articles back into `/var/www/landing` is still future publish-back work; this task corrected the import/control-plane inventory source.

## 2026-07-03 — Import myugc.studio blog into Blog Core

### Summary

* Connected `myugc.studio` to Blog Core as site `id=6`.
* Scanned the live homepage design and let Gemini infer the site's discovery direction/category profile.
* Imported existing `myugc.studio` blog URLs non-destructively from public sitemaps.
* Left the live `myugc.studio` site untouched; imported records point back to the original published URLs.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `myugc.studio`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `myugc.studio` was imported as `public_sitemap` without `root_path` because `/var/www/my-ugc-studio` has no static `/blog/*.html` files. Using a local root would make Blog Core's current import scanner stop at an empty webroot result instead of reading public sitemaps.

### Checks run

* Verified `myugc.studio` was not already present in Blog Core.
* Checked VPS roots and nginx config for `myugc.studio`.
* Verified public sitemap sources include multilingual blog URLs.
* Created/updated site `id=6` in the live Blog Core SQLite database.
* Ran `POST /api/sites/6/scan`; Gemini returned a topic profile for My UGC Studio.
* Ran `POST /api/sites/6/import-blog/scan`; found 343 public-fetch blog URLs.
* Ran `POST /api/sites/6/import-blog/import`; imported 343, skipped 0, errors 0.
* Verified imported counts by language: EN 43 stored records, DE 75, ES 75, FR 75, RU 75.
* Verified `/api/sites/6/content-jobs?language=en` returns 42 visible EN article records after hiding the `/blog/` hub.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/6#content` contains `My UGC Studio`, `Content inventory`, language switching, and `LIVE / IMPORTED`.
* Ran `POST /api/sites/6/bootstrap-preview`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* The import is stored in the live SQLite database, which is intentionally not committed to Git.
* Publishing new generated My UGC Studio articles back into the original site locations is still future publish-back work; imported records are currently dashboard inventory/control-plane records.

## 2026-07-03 — Add social credential setup and connection tests

### Summary

* Added a `Social channel credentials` block to the Setup tab.
* Added per-site credential forms for LinkedIn, Telegram, X/Twitter, and Tumblr.
* Added `Save credentials` and `Test connect` actions for each provider.
* Updated Distribution channel cards to point to Setup and show `Configure in Setup`, `Ready to test`, or `Connected` based on saved/tested status.

### Files changed

* `app.py` — added social provider credential config, per-site save/test API routes, provider API probes, Setup UI, JS handlers, and status styling.
* `docs/PROJECT_MEMORY.md` — recorded the durable Setup-vs-Distribution social channel rule and secret-handling rule.
* `docs/INTEGRATIONS.md` — documented social credential storage and connection test behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Setup is where keys/tokens are entered and tested. Distribution only controls autopublish selection for configured/connected channels.
* Saved secrets are kept in SQLite `social_connections.credentials_json` and are not rendered back into the dashboard.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified live `https://blog.yas.ooo/sites/5#setup` contains social credential forms and JS handlers.
* Verified live HTML does not contain raw env secret names such as `GEMINI_API_KEY`.
* Smoke-tested Telegram save endpoint with empty payload and Telegram test endpoint; missing credentials return a controlled `400` with `Missing required credentials`.

### Risks / TODO

* Real social publishing routes still need to use these stored per-site credentials.
* OAuth authorization flows for providers that need browser-based authorization are still not implemented; current Setup supports entering issued tokens/keys and testing them.

## 2026-07-03 — Auto-infer Discovery settings from scanned site

### Summary

* Added Gemini-based site topic-profile inference during `Scan design`.
* `Discovery direction` and `Category hint` are now auto-filled from scanned homepage metadata/nav/footer when empty.
* Added a deterministic fallback so scans still succeed if Gemini is unavailable.
* Updated `run.sh` to source `/var/www/blog.yas.ooo/.env` before Gunicorn, and configured the live VPS `.env` with existing Gemini/Google key/model env vars without committing secrets.
* Ran a live scan for `yas.wine` and updated site `id=5` with Gemini-inferred Discovery settings.

### Files changed

* `app.py` — added site topic-profile prompt/inference/fallback logic and connected it to the scan route; updated Distribution field hints.
* `run.sh` — loads `.env` before starting Gunicorn.
* `docs/PROJECT_MEMORY.md` — recorded Gemini topic-profile inference and `.env` runtime behavior.
* `docs/DEPLOYMENT.md` — documented `.env` loading and Gemini env vars without secrets.
* `docs/INTEGRATIONS.md` — documented the topic-profile inference contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Gemini should infer a site's initial editorial direction and category hints from the site scan; the UI fields remain editable overrides.
* Normal scans preserve manual overrides by writing inferred values only when the fields are empty.
* Missing Gemini configuration is degraded behavior; fallback values are allowed so site scanning is not blocked.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` and `run.sh` to `/var/www/blog.yas.ooo/`.
* Created `/var/www/blog.yas.ooo/.env` on the VPS from existing Gemini/Google env names without exposing values; `.env` remains untracked.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Ran `POST http://127.0.0.1:3299/api/sites/5/scan`; verified Gemini returned `source=gemini`.
* Verified `/api/sites/5/factory-settings` now returns Gemini-inferred `direction` and `category_hint` for YAS Wine.

### Risks / TODO

* Topic inference depends on Gemini env vars being present in the runtime `.env`.
* Existing manually edited Discovery fields are intentionally not overwritten by future scans.

## 2026-07-03 — Clarify social connect state and planned publications placement

### Summary

* Replaced active-looking social `Connect` buttons with non-clickable `OAuth setup needed` indicators until per-site OAuth/connect routes are implemented.
* Moved `Planned publications` to the bottom of Distribution below the social channel settings.
* Changed the no-planned-publications state from a large empty panel to a compact row.

### Files changed

* `app.py` — updated Distribution rendering, removed the placeholder connect toast function, and added compact planned-publication/connection-state CSS.
* `docs/PROJECT_MEMORY.md` — recorded durable UI rules for disabled social connect state and bottom placement of planned publications.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Non-implemented OAuth/connect actions should be shown as setup state, not as buttons that appear to do something.
* Planned publication tasks belong at the bottom of Distribution under social channels, not above the channel controls.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified live HTML for `https://blog.yas.ooo/sites/5#distribution`: no `connectSocialChannel`, no connect `onclick`, `OAuth setup needed` indicators present, `Planned publications` appears after `Channels`, compact `planned-empty` is present.

### Risks / TODO

* Per-site OAuth/connect routes for LinkedIn, Telegram, X/Twitter, and Tumblr still need real implementation before accounts can be connected.
* Planned publications still show only current working content job statuses, not a calendar/time-based publishing schedule.

## 2026-07-03 — Move planned publications into Distribution

### Summary

* Moved `Planned publications` out of the Content tab.
* Placed planned publication tasks under Distribution, directly below autopublish scheduler settings.
* Kept Content focused on imported/live inventory and import actions.

### Files changed

* `app.py` — moved planned publication rendering into `render_distribution_settings()` and removed the Content-tab planned section.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that planned/future publication tasks belong under Distribution scheduling.
* `docs/CHANGELOG_AI.md` — logged this placement correction.

### Decisions

* Planned tasks are part of publishing/scheduling workflow, so they belong with Distribution rather than Content inventory.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/sites/5#distribution`: `Planned publications` appears in Distribution, not in Content, and no `__PLANNED_PUBLICATIONS__` placeholder remains.

### Risks / TODO

* Planned publications are still status-based jobs, not a true scheduled calendar with publish timestamps.

## 2026-07-03 — Align multilingual content sorting and show planned publications

### Summary

* Fixed Content inventory sorting so language tabs keep the same article/topic order across EN/RU/ES/DE/FR.
* Added a separate `Planned publications` section for non-imported Blog Core work items.
* Planned publications now show `QUEUED`, `GENERATING`, `DRAFT`, and `ERROR` content jobs separately from imported live pages.

### Files changed

* `app.py` — added normalized base-path sort keys, planned content query/rendering, and a Content tab section for planned publications.
* `docs/PROJECT_MEMORY.md` — recorded stable cross-language sorting and planned-publication visibility rules.
* `docs/CHANGELOG_AI.md` — logged this inventory/scheduling UI fix.

### Decisions

* Imported multilingual content should sort by normalized source path, not by import timestamp or database id.
* Planned publications are currently content jobs in working statuses; a full scheduled calendar remains a future layer.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified first five normalized paths match across EN/RU/ES/DE/FR on `/api/sites/5/content-jobs`.
* Verified `https://blog.yas.ooo/sites/5#content` contains `Planned publications` and no leftover `__PLANNED_PUBLICATIONS__` placeholder.

### Risks / TODO

* `Planned publications` is not yet a time-based schedule/calendar because `content_jobs` does not have a scheduled publish timestamp.

## 2026-07-03 — Unify distribution channel controls

### Summary

* Removed duplicated social channel sections in Distribution.
* Replaced separate `Publish channels`, include-link checkboxes, and connection-status cards with one unified card per provider.
* Each channel card now shows connection status, a visible `Connect` placeholder, `Use for autopublish`, and `Include article link`.

### Files changed

* `app.py` — rewrote `render_distribution_settings()` channel UI, added unified channel CSS, and added a `connectSocialChannel()` placeholder toast.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule to keep social provider controls unified.
* `docs/CHANGELOG_AI.md` — logged this Distribution UI fix.

### Decisions

* Until per-site OAuth/connect routes are implemented, `Connect` should be visible but honest that the route is not wired yet.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/sites/5#distribution` no longer contains `Publish channels` or `Channel connection status`, and contains unified channel cards with `Use for autopublish`, `Include article link`, and Connect controls.

### Risks / TODO

* Per-site OAuth/connect routes are still not implemented; Connect currently shows a placeholder toast.

## 2026-07-03 — Filter trade-promo Discovery signals

### Summary

* Added filtering for promotional/trade campaign signals such as grants, retailer campaigns, `Wine Month`, and money-based promo headlines.
* Confirmed `Indies to receive £250 for Bordeaux Wine Month` is classified as promotion/trade-specific and filtered out.

### Files changed

* `app.py` — added promo/trade signal terms to `is_global_topic_signal()`.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that trade-promo/campaign items are not global discovery trends.
* `docs/CHANGELOG_AI.md` — logged this filtering refinement.

### Decisions

* Discovery should not show retailer/trade promotions as global content trends.

### Checks run

* `python3 -m py_compile app.py`
* Local classifier check returned `(False, 'promotion/trade-specific')` for `Indies to receive £250 for Bordeaux Wine Month`.
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/api/sites/5/topic-signals?range=month` no longer contains `Indies to receive`.

### Risks / TODO

* Filtering remains heuristic; add source/domain quality scoring if weak celebrity or brand-news items still appear.

## 2026-07-03 — Filter Discovery to broad global signals

### Summary

* Changed topic discovery to use a broader global/consumer/industry signal query.
* Added filtering for city-specific, festival/event, ticket, local-opening, and local guide signals before showing Google/Reddit items.
* Updated Discovery copy to clarify that local events and one-off news are filtered out.
* Article idea jobs now instruct generation to turn signals into generalizable articles, not city/event/festival pieces.

### Files changed

* `app.py` — added global signal query construction, local/event signal filters, warnings for filtered signals, Discovery UI copy, and article idea angle guidance.
* `docs/PROJECT_MEMORY.md` — recorded the durable global-signal rule for Discovery.
* `docs/CHANGELOG_AI.md` — logged this filtering change.

### Decisions

* Discovery should surface broad topic/consumer/industry trends, not local event feeds.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/api/sites/5/topic-signals?range=month` uses query `wine food pairing global trends consumer industry`, filters local/event Google and Reddit items, and no longer returns the earlier `Castro Wine Fest` items.

### Risks / TODO

* Filtering is heuristic. Some weak celebrity or brand-news items can still pass if they are not local/event-specific; future scoring can add a stronger editorial-quality layer.

## 2026-07-03 — Add language switching and simplify content pagination

### Summary

* Changed Content inventory to default to a concrete language instead of mixing all imported languages.
* Added language chips for available content languages (`EN`, `RU`, `ES`, `DE`, `FR`).
* Simplified Content inventory pagination to one centered bottom nav with numeric links and arrow icons only.

### Files changed

* `app.py` — added content job language detection/filtering, language switcher rendering, API language metadata, and simplified bottom-only pagination.
* `docs/PROJECT_MEMORY.md` — recorded durable rules for language-separated inventory and compact bottom-only pagination.
* `docs/CHANGELOG_AI.md` — logged this UI/data filtering task.

### Decisions

* Multilingual imported content must be browsed per language by default; `All` is not shown in the Content inventory UI.
* Pagination should be unobtrusive and only at the bottom of the content list.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/api/sites/5/content-jobs?page=1&per_page=24` returns `language=en`, `total=166`, and sample rows all have `sources_json.language=en`.
* Verified `/api/sites/5/content-jobs?page=1&per_page=24&language=ru` returns `language=ru`, `total=160`, and sample rows all have `sources_json.language=ru`.
* Verified `https://blog.yas.ooo/sites/5#content` has language chips, no `Page 1 of`/`Showing` text, and exactly one bottom pagination nav: `1 2 3 ›`.

### Risks / TODO

* The API still supports `language=all` if explicitly requested, but the dashboard UI intentionally does not expose an all-languages mixed view.

## 2026-07-03 — Compact imported content actions and type badges

### Summary

* Replaced the visible `Open live page` text button with a compact external-link icon in Content inventory cards.
* Styled `LIVE / IMPORTED` as a green status badge.
* Added compact content type badges for imported records, including `Blog` and `SEO money page`.

### Files changed

* `app.py` — added live-page icon rendering, content type badge rendering, and CSS for imported status/type/action indicators.
* `docs/PROJECT_MEMORY.md` — recorded durable UI rules for compact content card actions and type badges.
* `docs/CHANGELOG_AI.md` — logged this UI refinement.

### Decisions

* Imported content cards should show ownership/status/type at a glance without large action buttons.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Fetched `https://blog.yas.ooo/sites/5#content` and verified a production card action row renders `SEO money page`, `LIVE / IMPORTED`, and an external-link `↗` icon.

### Risks / TODO

* Browser runtime checks timed out during this task, so verification used live HTML fetch and server health checks.

## 2026-07-03 — Compact social status indicators in content cards

### Summary

* Replaced large per-channel social status pills in Content inventory cards with compact icon indicators.
* Muted unpublished/not queued channels visually and kept tooltips/ARIA labels with the exact channel status.
* Deployed the dashboard UI fix to live Blog Core.

### Files changed

* `app.py` — added social status icon rendering and CSS for muted/queued/published/failed states.
* `docs/PROJECT_MEMORY.md` — recorded the durable UI rule for compact social status indicators.
* `docs/CHANGELOG_AI.md` — logged this UI fix.

### Decisions

* Social publishing status in content cards should be a compact visual indicator, not a row of large text buttons.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Browser check of `https://blog.yas.ooo/sites/5#content`: first content card has four `.social-icon` elements at 30x30, old `linkedin: not queued` text is absent, and muted icons have opacity `0.32`.

### Risks / TODO

* The current icons are lightweight text glyphs (`in`, `tg`, `X`, `t`) because Blog Core has no frontend icon package. They can later be replaced with SVG brand icons if the dashboard adds an icon asset strategy.

## 2026-07-03 — Fix public YAS Wine blog pagination

### Summary

* Corrected the target from Blog Core dashboard pagination to the public source-site page `https://yas.wine/blog/`.
* Replaced the public blog's `More guides` load-more behavior with visible pagination controls: `Previous`, numbered pages, and `Next`.
* Updated the public page counter to show `Page X of Y · Showing A-B of N guides`.

### Files changed

* `/var/www/yaswine/blog/index.html` — live source-site file edited directly on the VPS; backup created at `/var/www/yaswine/blog/index.html.bak-pagination-20260703-1248`.
* `docs/PROJECT_MEMORY.md` — recorded the durable distinction between Blog Core dashboard pagination and source-site public blog pagination.
* `docs/CHANGELOG_AI.md` — logged this public-site pagination fix.

### Decisions

* Public `yas.wine/blog/` pagination belongs to the source site's webroot, not to Blog Core dashboard rendering.
* Keep 12 cards per page and use `?page=N` URLs for direct navigation.

### Checks run

* Browser check of `https://yas.wine/blog/`: 61 total cards, 12 visible cards, `More guides` hidden, pager visible with `Previous 1 2 3 4 5 6 Next`, and text `Page 1 of 6 · Showing 1-12 of 61 guides`.
* Browser check of `https://yas.wine/blog/?page=2`: active page `2`, 12 visible cards, and text `Page 2 of 6 · Showing 13-24 of 61 guides`.

### Risks / TODO

* The public blog pagination is client-side over the existing static 61-card page. SEO/server-rendered paginated archive pages are still a separate future improvement if needed.

## 2026-07-03 — Make content pagination explicit

### Summary

* Changed Content inventory pagination from bare page numbers to an explicit `Page X of Y` block.
* Renamed numeric links to `Page 1`, `Page 2`, etc. so the controls read as pagination instead of stray numbers.
* Deployed the UI clarification to live Blog Core.

### Files changed

* `app.py` — updated `render_content_pagination()` labels and CSS for clearer visible pagination.
* `docs/CHANGELOG_AI.md` — logged this pagination clarity fix.

### Decisions

* Pagination controls must be visually explicit on large imported inventories; bare numbers are too easy to miss.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Browser reload of `https://blog.yas.ooo/sites/5#content` confirmed visible text: `Page 1 of 34`, `Page 1`, `Page 2`, `Page 3`, `Next`.

### Risks / TODO

* Filters by content type/status/language are still needed for large imports, but pagination is now visibly present.

## 2026-07-03 — Hide imported hub pages and add content pagination

### Summary

* Hid imported section listing/hub pages such as `/blog/`, language blog indexes, `/wine-countries/`, and `/wine-regions/` from the Content inventory work list.
* Added server-side pagination metadata and UI controls for the Content inventory.
* Updated the Content inventory copy to explain that listing pages are kept as import metadata, not shown as article/task cards.

### Files changed

* `app.py` — added imported hub detection, paginated `get_content_jobs()`, pagination rendering, API pagination fields, and Content inventory explanatory copy.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that imported hub/listing pages are metadata and Content inventory must stay paginated.
* `docs/CHANGELOG_AI.md` — logged this UI/data-list fix.

### Decisions

* Do not delete imported hub/listing pages from the database. Hide them from the work list so Blog Core preserves source-site structure without confusing those pages with articles.
* Keep `/api/sites/<id>/content-jobs` backward compatible by still returning `jobs`, while adding `page`, `per_page`, `total`, and `total_pages`.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/api/sites/5/content-jobs?page=1&per_page=24` returns `total=806`, `total_pages=34`, `jobs=24`, and no first-page job with `published_url=https://yas.wine/blog/`.
* Verified `https://blog.yas.ooo/sites/5#content` contains `Content inventory`, pagination UI, and the hub-page explanatory note, and no card title `Wine Blog: Pairing Guides, Wine Tips and Buying Advice | YAS Wine`.

### Risks / TODO

* Content inventory still needs filters by status/type/language for very large imports.
* Imported hub pages are hidden from this UI list only; they remain in the database for source-site metadata.

## 2026-07-03 — Clarify imported content versus publication tasks

### Summary

* Renamed the `Article production queue` section to `Content inventory`.
* Changed `IMPORTED` cards to show `LIVE / IMPORTED` and `Open live page`.
* Removed `Generate draft` actions from imported records so already-published source pages are not presented as unpublished tasks.
* Updated explanatory copy: imported pages are already live on the source site; queued items are future work.

### Files changed

* `app.py` — updated `render_content_jobs()` labels/actions and the Content tab heading/copy.
* `docs/PROJECT_MEMORY.md` — recorded the durable UI distinction between imported live pages and queued generation tasks.
* `docs/CHANGELOG_AI.md` — logged this UI clarification task.

### Decisions

* `IMPORTED` means an existing live source-site page imported into Blog Core's control-plane inventory. It is not a publication task.
* Generation buttons belong only on new/queued Blog Core tasks, not on imported live pages.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Fetched `https://blog.yas.ooo/sites/5#content` and verified `Content inventory`, `LIVE / IMPORTED`, and `Open live page` are present while `Article production queue` and `Generate draft` are absent for imported rows.
* Browser DOM check confirmed the same state and no console errors/warnings.

### Risks / TODO

* The `Content` tab still needs filters/pagination to separate imported live pages, queued tasks, drafts, and published-by-Blog-Core records at scale.

## 2026-07-03 — Split site manage page into tabs

### Summary

* Reorganized the site manage page into clear tabs: `Content`, `Discovery`, `Distribution`, `Activity`, and `Setup`.
* Moved import controls and article production queue into `Content`.
* Moved Google/Reddit topic signals into `Discovery`.
* Kept autopublish/social channel settings in `Distribution`.
* Moved `Factory jobs` into `Activity` and site/webroot/CNAME/design controls into `Setup`.
* Deployed the tabbed UI to live Blog Core and validated desktop/mobile rendering in the in-app browser.

### Files changed

* `app.py` — added tab navigation, tab panels, tab switching JS, and tab styles in `MANAGE_SITE_HTML`.
* `docs/PROJECT_MEMORY.md` — documented the durable tab organization rule.
* `docs/CHANGELOG_AI.md` — logged this UI organization task.

### Decisions

* The manage page should keep operational concerns separate: content work, discovery, distribution, activity logs, and technical setup should not share one long mixed page.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Browser QA on `https://blog.yas.ooo/sites/5`: page identity, tab visibility, tab clicks, console errors/warnings, desktop screenshot, and mobile viewport screenshot.

### Risks / TODO

* The content queue still returns only the latest 24 records; full filtering/pagination remains needed for large imports such as 821 `yas.wine` records.

## 2026-07-03 — Summarize factory job messages in UI

### Summary

* Fixed the `Factory jobs` panel rendering huge raw JSON payloads from import jobs.
* Added compact job-message summaries for import and article-idea jobs.
* Added CSS clamping/overflow protection for job messages so a long payload cannot break the page layout.
* Deployed the fix to live Blog Core and verified `/sites/5` no longer contains the repeated `already imported` JSON dump.

### Files changed

* `app.py` — added `summarize_job_message()` and changed `render_jobs()` to display summaries instead of raw `publish_jobs.message`.
* `docs/PROJECT_MEMORY.md` — recorded the durable UI rule to summarize job messages.
* `docs/CHANGELOG_AI.md` — logged this UI fix.

### Decisions

* `publish_jobs.message` can keep structured JSON for internal/debug use, but the dashboard must present compact human-readable summaries.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Fetched `https://blog.yas.ooo/sites/5` and confirmed the page shows `imported 0; skipped 821; errors 0` instead of raw JSON.

### Risks / TODO

* The factory jobs panel still needs richer pagination/filtering, but it no longer breaks the page.

## 2026-07-03 — Replace partial YAS Wine import with full webroot import

### Summary

* Corrected the earlier partial `yas.wine` import approach. The 61 URL count was only the public English `/blog/` index, not the real site inventory.
* Inspected `/var/www/yaswine` directly over SSH and found 828 candidate HTML files, 821 distinct canonical URLs, 433 blog files, and 395 `wine-countries`/`wine-regions` SEO money page files.
* Backed up the live Blog Core SQLite database and imported the missing 760 records directly from `/var/www/yaswine`.
* Updated the existing 61 records with direct `webrootPath`, page type, language, and source-site-authoritative metadata.
* Updated and deployed `app.py` so future local-site imports use `root_path` filesystem discovery, include multilingual blog pages and SEO money pages, and use public fetch only as fallback.

### Files changed

* `app.py` — added local webroot import discovery/extraction, multilingual blog and SEO money page import prefixes, recursive sitemap-index fallback, path-safe import slugs, and higher import batch limit.
* `docs/PROJECT_MEMORY.md` — replaced the incomplete 61-URL state note with the full 821-record production state.
* `docs/INTEGRATIONS.md` — documented direct webroot import behavior.
* `docs/SEO_MEMORY.md` — recorded that imported SEO money pages are part of local-site inventory.
* `docs/CHANGELOG_AI.md` — logged this correction.

### Decisions

* For VPS-local imported sites, direct webroot inventory is authoritative. Public crawling is only a fallback for external sites.
* SEO money pages under `wine-countries` and `wine-regions` are imported content for Blog Core control-plane purposes, not ignored non-blog pages.

### Checks run

* Backed up `/var/www/blog.yas.ooo/data/blog_core.sqlite3`.
* Imported `yas.wine` from `/var/www/yaswine`: 821 distinct imported records total.
* Verified DB counts: `IMPORTED=821`, `Imported Blog=426`, `Imported SEO Money Page=395`.
* Verified language metadata: `en=169`, `ru=163`, `es=163`, `de=163`, `fr=163`.
* `python3 -m py_compile app.py` locally and on VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified live scan endpoint returns `source=local_webroot`, `articles=821`, `duplicates=7`.
* Verified repeat API import returns `0 imported`, `821 skipped`, `0 errors`.

### Risks / TODO

* UI currently lists only the latest 24 content jobs via `/api/sites/<id>/content-jobs`; filtering/pagination is needed to manage all 821 imported records comfortably.
* Publishing generated updates back into exact source files/URLs still needs the publish-back-in-place pipeline.

## 2026-07-03 — Import YAS Wine into live Blog Core

### Summary

* Imported the existing `yas.wine` blog into live Blog Core site `id=5`.
* The production scan found 61 English article URLs from `https://yas.wine/blog/`.
* The import created 61 `content_jobs` with `status=IMPORTED`, preserved original `published_url` values, and reported 0 errors.
* A repeat import check returned 0 imported, 61 skipped as `already imported`, confirming duplicate protection.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the live `yas.wine` import state and scripted API User-Agent pitfall.
* `docs/CHANGELOG_AI.md` — logged this production import verification task.

### Decisions

* Keep `yas.wine` original `/blog/...` URLs authoritative after import; imported jobs are control-plane records for now.

### Checks run

* `GET https://blog.yas.ooo/health`
* `GET https://blog.yas.ooo/api/sites`
* `POST https://blog.yas.ooo/api/sites/5/import-blog/scan`
* `POST https://blog.yas.ooo/api/sites/5/import-blog/import`
* `GET https://blog.yas.ooo/api/sites/5/content-jobs`
* `GET https://blog.yas.ooo/api/sites/5/content-jobs/f0c496a5a5fc26cc67077613`
* `curl -I -L https://yas.wine/blog/wine-region-napa-valley-united-states/`

### Risks / TODO

* Current import covered English URLs discoverable from `/blog/`; multilingual URLs in `sitemap_index.xml` still need recursive sitemap-index discovery.
* Publishing generated tasks back into the original `yas.wine` locations is not implemented yet.

## 2026-07-03 — Clarify imported-blog ownership model

### Summary

* Clarified that the "Blog Core as control plane, not public mirror" rule applies to imported existing blogs only.
* Documented that imported blogs should keep publishing into the same original site locations and URL structure.
* Preserved the separate rule that blogs created by Blog Core from scratch can be fully owned, hosted, and published by Blog Core.

### Files changed

* `docs/PROJECT_MEMORY.md` — added imported-vs-created ownership distinction and decision log entry.
* `docs/SEO_MEMORY.md` — clarified canonical behavior for imported blogs versus Blog Core-created blogs.
* `docs/INTEGRATIONS.md` — clarified import publishing target and current hosted mirror/preview caveat.
* `docs/CHANGELOG_AI.md` — logged this clarification task.

### Decisions

* Imported existing blogs are managed in place by default: original URLs stay authoritative, and future generated tasks should publish back into those same locations.
* Blog Core-created blogs can be native Blog Core publications with Blog Core as the source of truth.

### Checks run

* Read existing project memory, SEO memory, integrations memory, and changelog before editing.

### Risks / TODO

* Implement publish-back-in-place for imported blogs; current code still has hosted mirror rendering and incomplete local/static export parity.

## 2026-07-03 — Analyze YAS Wine import coexistence

### Summary

* Checked how imported articles coexist with the source site's existing blog.
* Inspected `yas.wine` public blog, robots, sitemap index, article canonical metadata, and import/rendering code.
* Confirmed that import is non-destructive and stores source canonical URLs, but hosted rendering does not yet emit canonical tags from that stored source URL.
* Confirmed that current discovery finds 61 English `yas.wine/blog/` article URLs from the blog index, while `sitemap-blog.xml` and `/blog/sitemap.xml` return 404.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded duplicate-content/canonical migration rule and `sitemap_index.xml` import pitfall.
* `docs/SEO_MEMORY.md` — documented source canonical/noindex recommendation during coexistence and the missing hosted canonical output.
* `docs/INTEGRATIONS.md` — documented current `yas.wine` import discovery behavior and sitemap-index limitation.
* `docs/CHANGELOG_AI.md` — logged this analysis task.

### Decisions

* Treat the source blog URL as authoritative until an explicit cutover is implemented.
* Do not expose a public indexed Blog Core mirror of imported content without canonical/noindex/redirect strategy.

### Checks run

* Read project memory and import/render code.
* `curl -I -L https://yas.wine/blog/`
* Fetched `https://yas.wine/robots.txt`, `https://yas.wine/sitemap.xml`, `https://yas.wine/sitemap_index.xml`, language sitemaps, and a sample article canonical.
* Counted 61 candidate English article URLs from `https://yas.wine/blog/`.

### Risks / TODO

* Add recursive sitemap-index discovery for multilingual imports.
* Add hosted canonical/noindex behavior before exposing imported mirrors to search engines.

## 2026-07-03 — Refresh self-updating project memory after local clone

### Summary

* Verified the separate local clone at `/Users/yasyas/Library/Mobile Documents/com~apple~CloudDocs/проекты/blogcore`.
* Read existing memory, README, runtime files, nginx template, `.gitignore`, and key `app.py` routes/schema before editing.
* Tightened future-agent memory rules and refreshed durable project/deployment/SEO notes from confirmed repository state.
* Marked the older SEO sitemap limitation as replaced for hosted CNAME blogs while preserving the remaining local static export gap.

### Files changed

* `AGENTS.md` — clarified mandatory final memory-status reporting and Git remote expectations for VPS vs local clones.
* `docs/PROJECT_MEMORY.md` — refreshed durable product, architecture, SEO, deployment, pitfalls, and decisions after local clone setup.
* `docs/SEO_MEMORY.md` — updated hosted sitemap/content-job behavior and marked the stale dynamic-sitemap gap as replaced.
* `docs/DEPLOYMENT.md` — recorded local clone path and Git access notes without secrets.
* `docs/CHANGELOG_AI.md` — logged this memory refresh task.

### Decisions

* Future Codex sessions must treat repository memory as the durable source of truth and still verify relevant code before changes.
* Local HTTPS Git access through GitHub CLI is acceptable when SSH publickey auth is unavailable locally; VPS SSH remote remains valid server context.

### Checks run

* `python3 -m py_compile app.py`
* `git status --short --branch`
* Read `AGENTS.md`, `README.md`, `.gitignore`, `requirements.txt`, `run.sh`, `deploy/nginx-blog.yas.ooo.conf`, docs memory files, and relevant `app.py` schema/routes.

### Risks / TODO

* Keep memory concise; do not duplicate all code details.
* Final article publishing/export, social OAuth/publishing, autopublish runner, GSC/sitemap submission, and production custom-domain SSL remain incomplete parity items.

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

## 2026-07-01 — Add YAS Wine factory parity backbone

### Summary

* Audited `/var/www/content-factory-yaswine` for article jobs, social publishing, autopublish, topic discovery, and generation flow.
* Added a parity map documenting which YAS Wine factory capabilities must exist in universal Blog Core.
* Added per-site Blog Core schema for article production jobs, job logs, social connections, social posts, autopublish settings/runs, and topic discovery settings/runs.
* Added manage-page Production Queue and Distribution/autopublish settings UI.
* Changed selected topic signals to create real `content_jobs`, not only legacy `publish_jobs`.
* Added a universal Gemini draft-generation contract for `content_jobs` that uses connected site context instead of wine-only rules.

### Files changed

* `app.py` — added factory parity tables, per-site settings helpers/endpoints, content job creation/list/detail/generate routes, manage-page production/distribution panels, and universal article draft generation.
* `docs/FACTORY_PARITY.md` — added the source-to-target parity map from YAS Wine factory to Blog Core.
* `docs/PROJECT_MEMORY.md` — recorded durable parity decision.
* `docs/INTEGRATIONS.md` — documented current backbone and pending provider/publish parity work.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Provider credentials and publishing settings must be scoped by `site_id`.
* Do not copy the YAS Wine prompt literally into Blog Core; use the same quality contract with site-specific context.
* Keep old `publish_jobs` as legacy/service jobs while new article production uses `content_jobs`.

### Checks run

* `python3 -m py_compile app.py`
* Ran `init_db()` against the live SQLite database to create new tables.
* Restarted PM2 process `blog-yas-core`.
* Checked `/health`.
* Smoke-tested `/api/sites/5/factory-settings`, `/api/sites/5/article-ideas`, and `/api/sites/5/content-jobs/<job_id>`; removed smoke job afterward.

### Risks / TODO

* Full parity is not finished yet: real social publishing routes, OAuth callbacks, autopublish runner, and final publish/localization/sitemap/GSC behavior still need to be ported.
* Real Gemini generation route exists but was not smoke-run to avoid spending model calls on a test topic.

## 2026-07-01 — Tighten Reddit topic relevance

### Summary

* Fixed Reddit topic discovery passing unrelated discussions when they matched only generic words from the site topic seed.
* Added a stricter Reddit relevance gate requiring a strong site-topic anchor plus contextual title match.
* Verified that broad YAS Wine false positives such as generic food/SNAP/mountain supply posts are rejected.

### Files changed

* `app.py` — added Reddit weak-term filtering, shared term matching, and `reddit_signal_is_relevant()` for stronger discussion filtering.
* `docs/PROJECT_MEMORY.md` — recorded the durable Reddit relevance rule.
* `docs/INTEGRATIONS.md` — documented the stricter Reddit signal contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Prefer returning zero Reddit cards with a warning over showing random or weakly related discussions.

### Checks run

* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Checked `/api/sites/5/topic-signals?range=month`; Reddit false positives were removed and the API returned a no-relevant-Reddit warning.

### Risks / TODO

* Reddit RSS can still rate-limit or return sparse results. A better long-term solution is a credentialed Reddit API integration with subreddit/topic expansion and caching.

## 2026-07-01 — Add existing blog import flow

### Summary

* Added a per-site existing blog import workflow to Blog Core.
* Added scan/import endpoints that discover current `/blog/` article URLs from sitemaps and blog index links.
* Imported articles are stored as `content_jobs` with `status=IMPORTED`, preserving original URL/canonical metadata and captured HTML without changing live files.
* Hosted Blog Core rendering now lists imported/generated jobs, includes them in hosted sitemap, and serves `/blog/{slug}/` from saved job HTML.
* Added dashboard UI inside each site page to scan existing blog URLs, review them, and import selected articles.

### Files changed

* `app.py` — added article metadata parser, existing blog discovery/import helpers, import API routes, site import UI/JS, and dynamic hosted rendering for imported/generated jobs.
* `docs/PROJECT_MEMORY.md` — recorded the migration/import rule.
* `docs/INTEGRATIONS.md` — documented the existing blog import contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Existing blog migration starts as a non-destructive import into Blog Core, not as an overwrite of live `/blog` files.
* Imported articles use `content_jobs.status=IMPORTED` so they are visible to the same production system without pretending they were generated by Blog Core.

### Checks run

* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Smoke-tested `/api/sites/5/import-blog/scan`; found 61 `yas.wine` article URLs.
* Smoke-imported one `yas.wine` article, verified dynamic render by slug, then removed the smoke job/log from SQLite.

### Risks / TODO

* Import currently stores referenced media URLs and article HTML but does not copy media into Blog Core storage yet. A later migration step should add optional media mirroring before switching a live site.
* Hosted rendering supports imported jobs, but local static `/blog` install still writes only the sample shell until final publishing/export parity is completed.

## 2026-07-09 — Recover stuck legacy factory generation status

### Summary

* Confirmed the AIREP24 source factory job `6fb2a84685c8450183d67eb7` had already reached `READY`, while Blog Core remained stuck in `GENERATING` after Gunicorn restarts killed the in-memory sync thread.
* Added status-poll recovery so Blog Core re-checks legacy/source factories for `GENERATING` jobs, syncs ready drafts, surfaces legacy errors, and marks very stale legacy generation instead of leaving the UI stuck.
* Triggered the content-job API for the affected AIREP24 task; it synced into Blog Core as `DRAFT` with the legacy factory HTML.

### Files changed

* `app.py` — extracted reusable legacy draft sync, added throttled legacy status recovery, and wired it into the content-job detail API used by frontend polling.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that legacy factory synchronization must survive Blog Core restarts.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Treat the content-job detail/status endpoint as a recovery path for source-factory jobs, not just a passive DB read.
* Keep source-factory generation authoritative for migrated jobs; Blog Core only syncs the completed draft/status.

### Checks run

* `python3 -m py_compile app.py`
* `pm2 restart blog-yas-core --update-env`
* `curl -fsS http://127.0.0.1:3299/health`
* Checked `/api/sites/9/content-jobs/6fb2a84685c8450183d67eb7`; status changed from `GENERATING` to `DRAFT`, `draft_html` length is 26001, and a sync log was added.

### Risks / TODO

* The recovery check is throttled in-process; multiple Gunicorn workers may still each perform occasional source-factory checks, which is acceptable for current low volume but can be centralized later if needed.

## 2026-07-09 — Record AIREP24 duplicate comparison path fix

### Summary

* Recorded the user-confirmed production fix for `AiRep24 vs. Live Chat: Modern Business Comparison`: the old `/compare/airep24-vs-live-chat/` static page was synchronized with the canonical `/comparisons/airep24-vs-live-chat/` page.
* Verified the old static file on the VPS now contains article structure markers for images, figures, TOC/navigation, and FAQ-related content.

### Files changed

* `docs/PROJECT_MEMORY.md` — added AIREP24 production note and duplicate-path pitfall.
* `docs/CHANGELOG_AI.md` — logged this memory update.

### Decisions

* Treat `/comparisons/...` as the canonical AIREP24 comparison path, while remembering that old `/compare/...` aliases can serve stale static HTML if not synchronized.

### Checks run

* Confirmed `/var/www/airep24.com/compare/airep24-vs-live-chat/index.html` exists.
* Confirmed `/var/www/airep24-landing/compare/airep24-vs-live-chat/index.html` exists.
* Grepped the old AIREP24 static page for `nav`, `img`, `figure`, and `toc` markers.

### Risks / TODO

* This records a production fix made outside Blog Core code. Future publishing should avoid leaving canonical and alias static paths out of sync.

## 2026-07-10 — Fix duplicate AIREP24 v3 article intro

### Summary

* Removed the duplicated title/subtitle block from factory v3 article pages by changing the shared renderer to stop outputting `article-head` with the same title and lead directly after the hero.
* Rebuilt and published the AIREP24 v3 site, then synchronized the old `/compare/airep24-vs-live-chat/` alias and `/var/www/airep24-landing` copies with the canonical `/comparisons/airep24-vs-live-chat/` output.
* Verified both public URLs keep TOC, images, and FAQ while no longer containing the duplicated article heading.

### Files changed

* `/var/www/template-core-v3/factory_v3/renderers/site.py` — factory article renderer now starts with TOC/body content and places media inline instead of rendering a duplicate intro after the hero.
* `/var/www/airep24.com/comparisons/airep24-vs-live-chat/index.html` — rebuilt public canonical page.
* `/var/www/airep24.com/compare/airep24-vs-live-chat/index.html` — resynced old alias with canonical output.
* `/var/www/airep24-landing/comparisons/airep24-vs-live-chat/index.html` — resynced landing copy.
* `/var/www/airep24-landing/compare/airep24-vs-live-chat/index.html` — resynced old landing alias.
* `docs/PROJECT_MEMORY.md` — recorded the durable template rule.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* For factory v3 pages, the hero owns the title and subtitle. The article layout should not repeat the same page title and description immediately below it.

### Checks run

* `python3 -m py_compile factory_v3/renderers/site.py`
* `python3 -m factory_v3.cli build-preview --site sites/airep24/site.yaml --language en`
* `python3 -m factory_v3.cli publish-preview --site sites/airep24/site.yaml`
* `python3 -m factory_v3.cli publish-live-bundle --site sites/airep24/site.yaml`
* `python3 -m factory_v3.cli publish-live-target --site sites/airep24/site.yaml`
* Public HTTP checks for `https://airep24.com/comparisons/airep24-vs-live-chat/` and `https://airep24.com/compare/airep24-vs-live-chat/`: both return `200`, no `article-head`, no duplicate `<h2>AiRep24 vs. Live Chat</h2>`, TOC/images/FAQ present.

### Risks / TODO

* `/var/www/template-core-v3` still has unrelated pre-existing modified/untracked files; only the renderer change was committed for this task.

## 2026-07-10 — Restore AIREP24 article layout while removing only duplicate copy

### Summary

* Corrected the previous AIREP24 v3 renderer change: restored the original article-head/media placement and removed only the duplicated title/subtitle text after the hero.
* Rebuilt and published the AIREP24 v3 site, then resynchronized the old `/compare/airep24-vs-live-chat/` alias and `/var/www/airep24-landing` copies.
* Confirmed the public canonical and alias pages keep the top article image, TOC, and FAQ, while the second duplicated `<h2>` and lead paragraph are absent.

### Files changed

* `/var/www/template-core-v3/factory_v3/renderers/site.py` — restored factory article media placement and removed only duplicated heading/lead copy.
* `/var/www/airep24.com/comparisons/airep24-vs-live-chat/index.html` — rebuilt public canonical page.
* `/var/www/airep24.com/compare/airep24-vs-live-chat/index.html` — resynced old alias.
* `/var/www/airep24-landing/comparisons/airep24-vs-live-chat/index.html` — resynced landing copy.
* `/var/www/airep24-landing/compare/airep24-vs-live-chat/index.html` — resynced old landing alias.
* `docs/PROJECT_MEMORY.md` — corrected the durable factory v3 intro rule.
* `docs/CHANGELOG_AI.md` — logged this corrective task.

### Decisions

* The right fix is not to redesign the article body. The hero owns title/subtitle; the original article media layout stays, and only the repeated title/lead copy is suppressed.

### Checks run

* `python3 -m py_compile factory_v3/renderers/site.py`
* `python3 -m factory_v3.cli build-preview --site sites/airep24/site.yaml --language en`
* `python3 -m factory_v3.cli publish-preview --site sites/airep24/site.yaml`
* `python3 -m factory_v3.cli publish-live-bundle --site sites/airep24/site.yaml`
* `python3 -m factory_v3.cli publish-live-target --site sites/airep24/site.yaml`
* Public HTTP checks for `https://airep24.com/comparisons/airep24-vs-live-chat/` and `https://airep24.com/compare/airep24-vs-live-chat/`: both return `200`, keep `article-head` with `article-figure`, have no duplicate `<h2>AiRep24 vs. Live Chat</h2>` and no duplicate lead paragraph, and still include TOC and FAQ.

### Risks / TODO

* `/var/www/template-core-v3` still has unrelated pre-existing dirty files in CLI/preview/CSS and untracked site/build artifacts; they were not committed for this task.

## 2026-07-10 — Restore AIREP24 live CSS after duplicate-copy fix

### Summary

* Restored the AIREP24 live stylesheet after the previous publish accidentally carried unrelated dirty `template-core-v3` article TOC style changes.
* Kept the HTML-only fix that removes the duplicated title/subtitle after the hero.
* Restored the `template-core-v3` working copy CSS to the clean Git version so future publishes do not reapply the unintended style change.

### Files changed

* `/var/www/airep24.com/assets/css/site.css` — restored from clean `template-core-v3` Git stylesheet.
* `/var/www/template-core-v3/factory_v3/static/assets/css/site.css` — restored working copy to clean Git state.
* `docs/CHANGELOG_AI.md` — logged this corrective task.

### Decisions

* Do not change AIREP24 visual styling while fixing duplicate generated copy. The fix scope is only the repeated article heading/lead block.

### Checks run

* Verified public `https://airep24.com/assets/css/site.css` uses the old `.article-toc` styles: `var(--line)` border, white/blue gradient background, old link background/hover.
* Verified `https://airep24.com/comparisons/airep24-vs-live-chat/` still has the top article image and no duplicated title/lead block.

### Risks / TODO

* `/var/www/template-core-v3` still has unrelated pre-existing dirty files in CLI/preview and untracked site/build artifacts; they were not changed for this corrective task.

## 2026-07-10 — Restore AIREP24 static page source and original stylesheet

### Summary

* Restored the public AIREP24 `AiRep24 vs. Live Chat` pages from the tracked `airep24-landing` static source instead of publishing through factory v3 again.
* Restored the original AIREP24 `site.css` and `site.min.css` files to the public webroot.
* Removed only the second duplicated article title/lead block from the canonical comparison page.

### Files changed

* `/var/www/airep24-landing/comparisons/airep24-vs-live-chat/index.html` — restored original static markup and removed only the duplicate intro block.
* `/var/www/airep24.com/comparisons/airep24-vs-live-chat/index.html` — synced public canonical page from the restored static source.
* `/var/www/airep24.com/compare/airep24-vs-live-chat/index.html` — restored public legacy alias from the tracked static source.
* `/var/www/airep24.com/assets/css/site.css` — restored original AIREP24 stylesheet from `airep24-landing` Git HEAD.
* `/var/www/airep24.com/assets/css/site.min.css` — restored original AIREP24 minified stylesheet from `airep24-landing` Git HEAD.
* `docs/CHANGELOG_AI.md` — logged the corrective rollback.
* `docs/PROJECT_MEMORY.md` — recorded the static-source rollback rule for imported site fixes.

### Decisions

* For imported/static site pages, do not republish through a generic template pipeline when the user asks for a surgical fix. Restore from the site's own tracked static source and change only the requested duplicate content.

### Checks run

* Public HTTP checks for `https://airep24.com/comparisons/airep24-vs-live-chat/`, `https://airep24.com/compare/airep24-vs-live-chat/`, and `https://airep24.com/assets/css/site.min.css?v=20260630-pagespeed-1`: all return `200`; CSS returns `text/css`.
* Confirmed canonical page links to `/assets/css/site.min.css?v=20260630-pagespeed-1`, has no `laycanmatch.com` metadata, has no duplicate `<h2>AiRep24 vs. Live Chat</h2>`, and keeps TOC/FAQ.

### Risks / TODO

* Browser cache may need a hard refresh if the previously loaded broken stylesheet is still cached in an open tab.

## 2026-07-10 — Redirect source-authoritative previews to live source pages

### Summary

* Fixed imported legacy/source-authoritative content job previews so Blog Core no longer renders them through the generic Blog Core draft shell.
* Preview requests for source-authoritative jobs now redirect to the recorded source-site URL, preserving the original site's design and avoiding misleading Blog Core-styled previews.
* Confirmed the AIREP24 `AiRep24 vs. Live Chat` preview redirects to the live AIREP24 comparison URL instead of returning Blog Core wrapper HTML.

### Files changed

* `app.py` — added source-authoritative job detection and source URL resolution, then short-circuited the preview route before generic/local draft rendering.
* `docs/PROJECT_MEMORY.md` — recorded that source-authoritative imported previews must not use the Blog Core renderer.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Blog Core is the control plane for imported/source-factory jobs. If native source-factory preview is unavailable, Blog Core must not fake a preview with its own renderer; it should open the authoritative source-site URL or report that native preview is unavailable.

### Checks run

* `python3 -m py_compile /tmp/blogcore-app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/sites/9/content-jobs/6fb2a84685c8450183d67eb7/preview` returns `302` to `https://airep24.com/comparisons/airep24-vs-live-chat/`.
* Verified following the redirect returns `200`, uses AIREP24 `site.min.css`, contains AIREP24 navigation, has no `blog-core-draft-body`, and has no duplicate `<h2>AiRep24 vs. Live Chat</h2>`.

### Risks / TODO

* This fixes misleading previews by opening the source-site page. A true unpublished-draft preview still needs native source-factory preview support for v3Page jobs; Blog Core should delegate that to the source factory rather than rendering it itself.

## 2026-07-10 — Add explicit Publish action for source-factory drafts

### Summary

* Added an explicit `Publish` action for `DRAFT` content jobs in planned/content task cards.
* Added a Blog Core publish API route that delegates source-authoritative imported jobs to their original factory via `/api/jobs/<oldFactoryJobId>/publish`.
* Kept generation and publication separate: generating a draft does not publish it automatically.

### Files changed

* `app.py` — added `publish_content_job`, `POST /api/sites/<site_id>/content-jobs/<job_id>/publish`, `Publish` task button, and frontend `publishArticleJob` handler.
* `docs/PROJECT_MEMORY.md` — recorded the durable generate/preview/publish separation for source-authoritative jobs.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Blog Core must not silently publish immediately after generation. `Generate/regenerate`, `Preview`, and `Publish` are separate operator actions.
* For imported/source-authoritative jobs, Blog Core publishes through the source factory, not by editing the source site's HTML/CSS directly.

### Checks run

* `python3 -m py_compile /tmp/blogcore-app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/sites/9` HTML includes the `Publish` button and `publishArticleJob` handler for job `6fb2a84685c8450183d67eb7`.
* Verified Flask registered `POST /api/sites/<site_id>/content-jobs/<job_id>/publish`.

### Risks / TODO

* I did not click/test live publish because it writes to the production source site. The first real publish may still surface source-factory errors if that factory's native publish path is broken.

## 2026-07-10 — Native preview for source-authoritative AIREP24 drafts

### Summary

* Replaced the unavailable/fake Blog Core draft preview path with an AIREP24 factory-native v3 preview.
* Preview now builds the pending v3 payload only in the factory preview tree and returns the rendered source-site HTML through Blog Core.
* The returned document is `noindex`; its asset base is `https://airep24.com/`, so it uses AIREP24's own CSS, images, header, footer, TOC, FAQ, and recommendation sections.

### Files changed

* `app.py` — proxies source-authoritative `DRAFT` previews from the original factory instead of using the generic Blog Core renderer or redirecting to the live page.
* `docs/PROJECT_MEMORY.md` — recorded the native-preview contract and safety rule.
* `docs/CHANGELOG_AI.md` — logged this task.
* `/var/www/content-factory-airep24/app.py` — added a v3 preview-only builder; this is maintained in the AIREP24 factory repository, not in Blog Core.

### Decisions

* A draft preview is neither a generic dashboard rendering nor an implicit publication. It must be rendered by the same source factory that will publish it.
* Native preview may temporarily stage its content in the source factory workspace but must restore it after rendering and must never execute `publish-preview`, `publish-live-bundle`, or `publish-live-target`.

### Checks run

* `python3 -m py_compile` succeeded for Blog Core and the AIREP24 factory.
* Restarted `blog-yas-core` and `content-factory-airep24`; Blog Core health endpoint returned `ok`.
* Requested the AIREP24 factory preview and the final Blog Core preview for job `b32afeff73e644f5badde7d7`: both returned `200`.
* Verified final preview contains `<base href="https://airep24.com/">`, `noindex,nofollow`, `article-toc`, `Recommended next`, native images, and AIREP24 stylesheet links.
* Confirmed the preview build did not change `/var/www/airep24.com/features/telegram-operator-handoff/index.html` and restored the temporary v3 source files.

### Risks / TODO

* The native preview endpoint is currently implemented for AIREP24 v3 payload jobs. Other imported factories need the same explicit native-preview capability before Blog Core can render their unpublished source-authoritative drafts.

## 2026-07-10 — Match draft preview to the current source-site shell

### Summary

* Corrected the first native preview implementation: it used the factory's v3 shell, which was visually stale compared with the live AIREP24 page.
* Preview now preserves the actual source page's document head, stylesheet links, header, footer, breadcrumb, navigation, and CTA links from `/var/www/airep24.com`; only the unpublished draft content is inserted between the source header and footer.

### Files changed

* `/var/www/content-factory-airep24/app.py` — added generic live-shell composition for v3 draft previews.
* `app.py` — corrected preview HTML base-tag detection/injection in the Blog Core proxy.
* `docs/PROJECT_MEMORY.md` — refined the source-authoritative preview contract.
* `docs/CHANGELOG_AI.md` — logged this correction.

### Checks run

* Compiled both applications and restarted `content-factory-airep24` and `blog-yas-core`.
* Browser-verified `https://blog.yas.ooo/sites/9/content-jobs/b32afeff73e644f5badde7d7/preview`.
* Verified the preview has AIREP24's current `page-breadcrumbs`, `web.airep24.com` header CTA, the generated draft body, and noindex metadata.

### Risks / TODO

* The generic shell merge requires a local source webroot. A remote-only source factory needs its own preview-shell retrieval strategy.

## 2026-07-10 — Bind draft values to the actual source-page template

### Summary

* Replaced the interim shell merge, which still inserted foreign v3 layout markup, with semantic binding into the real source page template.
* The preview now retains AIREP24's own `hero`, `article-layout`, `article-toc`, `article-body`, FAQ, recommendation, breadcrumb, update, header, and footer markup. It replaces only title, lead, TOC entries, article sections, and FAQ content from the draft payload.
* If a draft references an image that is not present in the source webroot, preview retains the existing source-template image rather than rendering an empty image slot.

### Files changed

* `/var/www/content-factory-airep24/app.py` — added source-template semantic binding for v3 draft previews and safe image fallback.
* `docs/PROJECT_MEMORY.md` — clarified that source page internal template markup must be preserved.
* `docs/CHANGELOG_AI.md` — logged this correction.

### Checks run

* `python3 -m py_compile /var/www/content-factory-airep24/app.py`.
* Restarted `content-factory-airep24`.
* Browser-verified the Blog Core preview: current AIREP24 header CTA, breadcrumb, native `hero` and `article-block` classes, TOC, generated draft text, and source-template hero image are present; `page-hero` factory markup is absent.

### Risks / TODO

* Semantic binding currently uses common source-template markers (`.hero`, `.article-toc`, `.article-body`, `.faq-grid`). A source factory whose public template does not expose equivalent semantic markers must provide an adapter before its drafts are previewed.

## 2026-07-10 — Remove unwanted preview breadcrumbs and restore inline draft images

### Summary

* Removed breadcrumbs from the AIREP24 draft preview as requested.
* Located the three generated draft images already present in the AIREP24 webroot and inserted them between article sections through the site's existing `article-inline-figure` component.
* Uses absolute source-site image URLs and eager loading for preview-only inserted images.

### Files changed

* `/var/www/content-factory-airep24/app.py` — source-template preview image discovery/insertion and breadcrumb removal.
* `docs/PROJECT_MEMORY.md` — recorded the preview media/breadcrumb rule.
* `docs/CHANGELOG_AI.md` — logged this task.

### Checks run

* Compiled and restarted `content-factory-airep24`.
* Verified preview output has zero `page-breadcrumbs`, three `article-inline-figure` blocks, and absolute URLs for all three `telegram-operator-handoff` draft images.

### Risks / TODO

* A draft whose images are not available in its source webroot must publish/stage its assets through that factory before preview can include them.

## 2026-07-13 — Add Gemini podcast production and Blog Core publishing

### Summary

* Added a site-scoped Podcast workflow: choose a finished/imported article, generate a spoken script, synthesize Gemini TTS audio, review it in the dashboard, then explicitly publish it.
* Published episodes receive a stable Blog Core episode page and are included in a per-site podcast RSS feed. Generation never publishes automatically.
* Added per-site host name, Gemini voice, voice direction, and target-duration settings. Generated audio is WAV in ignored `data/podcast_assets/`.

### Files changed

* `app.py` — podcast SQLite schema/migration, Gemini TTS client, script and chunked-audio generation, audio/episode/RSS routes, API, and Podcast dashboard tab.
* `docs/PROJECT_MEMORY.md` — durable podcast ownership, review, and custom-voice boundary.
* `docs/INTEGRATIONS.md` — Gemini TTS integration contract and public routes.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Gemini prebuilt voices plus a per-site voice direction are supported now. True voice cloning is not represented as a Gemini TTS feature because Google documents it as a separate Cloud Custom Voice product/access path.
* Blog Core publishes the audio to its own episode URL/feed. Imported source sites require their own explicit factory adapter for native embedding or source-site publication.

### Checks run

* `python3 -m py_compile app.py` passed before and after deployment.
* Restarted `blog-yas-core`; `curl -fsS http://127.0.0.1:3299/health` returned `ok`.
* Verified the site management page renders the new Podcast tab and production panel.
* Verified an empty per-site RSS endpoint returns valid `application/rss+xml`.
* Verified the create-episode API rejects an empty source article request without creating audio.

### Risks / TODO

* Gemini TTS is Preview and longer audio is generated in chunks to reduce quality drift; real content generation needs a selected article and incurs model usage.
* WAV is reliable and avoids a new transcoding dependency. Add MP3/AAC transcode only when a distribution host requires it.
* Native podcast pages/players on imported source sites are intentionally not changed by this implementation.
## 2026-08-09 — Verify a programmatic layer-first Reel renderer

### Summary

* Built an isolated, non-production 1080x1920 motion-design proof with a real timeline and independent visual layers. It uses no Google Flow, Veo, Gemini call, source-site edit, content job, or social publication.
* The proof uses four overlapping scenes with independently timed background photos, masked media panels, card motion, typography, line graphics, and the real SoloCruz logo mark.
* Corrected the durable decision: a sequence of full-frame stills is not a layer-first storyboard and is deprecated as the future factory pattern.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the layer contract and deprecated the previous full-scene still sequence.
* `docs/CHANGELOG_AI.md` — recorded the isolated renderer validation and its boundary.

### Decisions

* The future factory input must be a scene-and-layer specification, not only image prompts or a list of complete photos.
* Programmatic rendering is appropriate for designed motion, transitions, masks, panels, typography, and assets with known layer boundaries. It must not claim to produce live-action motion from a static photo.

### Checks run

* TypeScript compile with `tsc --noEmit` passed.
* Rendered and inspected an 18.048-second 1080x1920 H.264 MP4; output size 6.2 MB.

### Risks / TODO

* The proof is not a deployed Blog Core capability and its temporary imagery is not approved creative.
* Product implementation still needs an asset contract, reusable templates, audio/licensing policy, and a review/publish flow before it can generate or schedule Reels.
## 2026-08-10 — Make universal fixes an explicit project rule

### Summary

* Added a mandatory architecture rule that current failures are regression examples, never production rules.
* Recorded that fixes must target the shared contract or owning abstraction and must not contain object-, domain-, article-, language-, or channel-specific exceptions.

### Files changed

* `AGENTS.md` — made universal, invariant-driven fixes mandatory for every future task.
* `docs/PROJECT_MEMORY.md` — added the durable decision and a do-not-repeat rule against example-specific production fixes.
* `docs/CHANGELOG_AI.md` — recorded this memory update.

### Decisions

* A proposed production fix is unacceptable when it must name the currently failing example instead of the violated invariant.

### Checks run

* Read back the edited memory files before deployment.

### Risks / TODO

* The Reel layer pipeline still requires replacement of conversational placement with a universal explicit-mask editing contract; the current Reel remains unpublished and stopped.

## 2026-08-10 — Deploy universal Reel layer generation and produce SoloCruz Reel 32

### Summary

* Replaced model-controlled placement and guide-image extraction with scene-aware isolated foreground generation and deterministic programmatic registration.
* Added collision resolution, role-specific sizing, aspect-aware asset prompts, bounded scene color matching, object contact shadows, and source-asset recomposition on resume.
* Added optional Vertex explicit binary-mask insertion. Correct IAM was granted, but the configured project does not have model access; model-access `404` now switches the worker to the constrained isolated-matte path.
* Generated the real seven-scene Reel for SoloCruz social post `32` from its published article and left it as an unpublished `DRAFT` for review.

### Files changed

* `app.py` — universal Reel planner, generator, compositor, validator, resumability, Vertex integration, and model-access fallback.
* `docs/PROJECT_MEMORY.md` — durable Reel layer contract and deprecated approaches.
* `docs/INTEGRATIONS.md` — non-secret Vertex IAM/configuration and fallback behavior.
* `docs/DEPLOYMENT.md` — Reel environment and restart notes.
* `docs/CHANGELOG_AI.md` — task record and verification.

### Decisions

* A Reel foreground is generated as one isolated scene-aware asset; the renderer alone owns final geometry.
* A missing Vertex customization model must not re-enable unconstrained full-scene editing.
* Geometry checks are role-aware, while semantic composite review decides whether scale, lighting, and visual hierarchy are believable.

### Checks run

* `python3 -m py_compile app.py` locally and `.venv/bin/python -m py_compile app.py reel_renderer.py` on VPS.
* PM2 restart with environment update and `/health` check.
* Real production generation: 7 scenes, 14 foreground layers, voice, continuous site soundtrack, and programmatic H.264 render.
* `ffprobe`: 28.42 seconds, 1080x1920, 24 fps, H.264 video plus one AAC audio stream.
* Contact-sheet visual review across all seven scenes; no blank frames, guide rectangles, black text plates, or layer overlaps observed.

### Risks / TODO

* Native Vertex binary-mask insertion remains unavailable to the current Google Cloud project; use the constrained isolated-matte path until model access is granted or a current explicit-mask endpoint is available.
* Reel `32` is a review draft and has not been published.

## 2026-08-10 — Replace fixed Reel structure with source-derived planning

### Summary

* Removed the fixed seven-scene and three-stage storyboard contract.
* Added article-outline extraction, source-coverage architecture, independent per-beat visual-world selection, dynamic scene/stage/duration totals, and a separate production-detail pass for every screen.
* Added universal validation for complete source coverage, truthful stage continuity, distinct adjacent shot design, camera motivation, and isolated foreground actions that do not depend on the background.
* Updated Reel progress metadata and UI copy to display dynamic totals instead of a seven-scene assumption.

### Files changed

* `app.py` — dynamic story architecture, scene elaboration, validation, progress accounting, and UI wording.
* `docs/PROJECT_MEMORY.md` — recorded the source-derived Reel planning contract and deprecated the fixed template.
* `docs/CHANGELOG_AI.md` — recorded implementation and verification.

### Decisions

* Physical worlds are selected for editorial truth independently for each beat; production cost and background reuse are not planning criteria.
* Full media generation remains disabled while the new text storyboard is validated. Planner verification must not generate images, voice, or video.

### Checks run

* Local and VPS `py_compile` passed; PM2 restarted and `/health` returned `ok`.
* Real published SoloCruz article planner run covered 8 source sections as 8 beats, 8 scenes, and 8 independently derived physical stages; calculated 17 future image generations and 31.5 seconds.
* A stricter follow-up planner run correctly rejected repeated framing and non-isolated layer directions before media generation. It later reached the Gemini text-request limit, so no replacement media was produced.

### Risks / TODO

* The successful JSON proves dynamic source and stage coverage, but its shot direction was still too repetitive to approve for rendering. The deployed validator now rejects that repetition.
* Re-run the text-only planner after the Gemini request window resets; keep `MASKED_LAYER_REEL_ENABLED=0` until the stricter storyboard passes review.

## 2026-08-10 — Make Reel architecture the sole editorial-copy owner

### Summary

* Added source-grounded hook, open loop, escalation, payoff, per-beat viewer question, information release, stakes change, overlay text, and narration to the Gemini architecture contract.
* Removed overlay and narration fields from both later visual-production response schemas.
* Added deterministic beat-ID hydration so visual passes cannot rewrite approved editorial copy.
* Removed the implicit `gemini-3.1-flash-lite` text fallback and separated text, image, and TTS credential resolution.

### Files changed

* `app.py` — retention architecture, single-owner copy flow, visual-only schemas, and strict provider credential/model routing.
* `docs/PROJECT_MEMORY.md` — recorded the single-owner and provider-separation contracts.
* `docs/CHANGELOG_AI.md` — recorded implementation and verification.

### Decisions

* Editorial fields are generated once by Gemini 3.5 Flash during architecture; subsequent Gemini passes can only direct visuals.
* A text quota failure must remain a visible Gemini 3.5 Flash failure and must never silently switch to an image-project model or key.

### Checks run

* Local and VPS `py_compile` passed; PM2 restarted and `/health` returned `ok`.
* VPS configuration fingerprints confirmed distinct text and image keys, `gemini-3.5-flash` for text, `gemini-3.1-flash-image` for images, and no text fallback.
* Real SoloCruz architecture run produced a source-grounded hook, explicit open loop, nine retention beats, and late payoff with final copy for every beat.
* Follow-up visual request reported the expected `429` specifically for `gemini-3.5-flash` limit 20; it did not switch models or keys.

### Risks / TODO

* The 3.5 Flash text quota is currently exhausted. Complete visual-only skeleton and per-scene verification after its request window resets; no images, voice, or video were generated in this task.
## 2026-08-10 — Install the existing Google Cloud Gemini key for Blog Core text generation

### Summary

* Read the existing service-account-bound Gemini API key from project `exalted-tempo-504018-v0` in Google Cloud Console and installed it as the live Blog Core text credential.
* Preserved the independent image-generation credential and restarted `blog-yas-core` with the updated environment.
* Verified that authentication reaches `gemini-3.5-flash`; Google now reports the separate Gemini Prepay balance is depleted rather than the previous free-tier request-limit error.

### Files changed

* `/var/www/blog.yas.ooo/.env` — replaced `GEMINI_TEXT_API_KEY` with the existing paid-project Cloud key; no secret was added to Git or documentation.
* `docs/PROJECT_MEMORY.md` — recorded the durable separation between Cloud welcome credit and Gemini API Prepay billing.
* `docs/CHANGELOG_AI.md` — recorded this deployment and verification.

### Decisions

* Continue using the existing Cloud Console key and `gemini-3.5-flash`; do not introduce Vertex, another key, or a model fallback.

### Checks run

* Restarted PM2 process `blog-yas-core` with `--update-env`.
* `curl -fsS http://127.0.0.1:3299/health` returned healthy.
* Confirmed text and image key fingerprints differ without exposing either credential.
* Direct `gemini-3.5-flash:generateContent` smoke test authenticated but returned `429 RESOURCE_EXHAUSTED` with `Your prepayment credits are depleted`.

### Risks / TODO

* Text generation remains blocked until the separate Gemini API Prepay balance is funded or activated for the current Cloud Billing account. The ordinary Cloud welcome credit cannot pay for Gemini API usage under Google's current rules.
## 2026-08-10 — Reuse the working image credential for Gemini text generation

### Summary

* Set live `GEMINI_TEXT_API_KEY` to the same environment credential already used for Gemini image generation.
* Restarted Blog Core and verified `gemini-3.5-flash` with a real API request.

### Files changed

* `/var/www/blog.yas.ooo/.env` — text generation now uses the existing image-generation credential; no secret was stored in Git.
* `docs/PROJECT_MEMORY.md` — superseded the earlier separate-key decision.
* `docs/CHANGELOG_AI.md` — recorded deployment and verification.

### Decisions

* Text and image models remain independently configured, but currently share one working credential by operator decision.

### Checks run

* Restarted PM2 process `blog-yas-core` with `--update-env`.
* `/health` returned healthy.
* Verified matching text/image credential fingerprints without exposing the credential.
* Direct `gemini-3.5-flash` request returned HTTP 200, `modelVersion: gemini-3.5-flash`, and `serviceTier: standard`.

### Risks / TODO

* Text and image usage now share the same project quotas and billing limits.

## 2026-08-11 — Make Reel step three a locked Gemini production-manifest pass

### Summary

* Replaced the incorrect code-only third-stage assumption with a Gemini text pass that decomposes every approved step-two scene into exact background and layer generation jobs.
* Locked all creative scene/layer fields to step two and limited Gemini to production detail: prompts, references, placement, depth, timing, motion, and camera implementation.
* Connected the accepted manifest to the normal storyboard and image-generation pipeline; a third-stage failure no longer causes step two to be regenerated.
* Kept the verification run text-only: no images, voice, music, or video were generated.

### Files changed

* `app.py` — locked step-three scene prompt/validation, Gemini asset manifest, pipeline integration, and manifest-driven image prompt/placement routing.
* `staging/run_reel_step3_locked_once.py` — one-scene immutable-contract regression runner.
* `staging/run_reel_step3_locked_full.py` — full approved-scene decomposition runner with progress output.
* `staging/run_reel_step3_asset_manifest.py` — full Gemini asset-manifest verification runner.
* `docs/PROJECT_MEMORY.md` — recorded the corrected durable three-stage contract and deprecated code-only step three.
* `docs/CHANGELOG_AI.md` — recorded implementation and verification.

### Decisions

* Step two owns creative composition; step three uses Gemini to author technical decomposition without changing it.
* Short explicit directions such as `none` or `already present` are valid when a layer exists from frame start; validators check meaning and required presence rather than arbitrary verbosity.
* Physically necessary interaction between approved layers may overlap, while dominant incoherent occlusion remains rejected.

### Checks run

* Local and VPS Python compilation passed.
* A real SoloCruz plan completed locked Gemini scene elaboration for all 11 approved scenes in 115.2 seconds.
* The same real plan completed the full Gemini asset manifest for all 11 scenes in 130.9 seconds, with 18 separate foreground assets plus 11 background prompts and no media generation.
* Assertions confirmed unchanged approved scene fields and unchanged non-empty layer semantics; VPS health returned `ok`.

### Risks / TODO

* Existing stored Reel plans without `productionManifest` continue through the legacy runtime spatial planner. Newly generated plans use the manifest path.
* Actual image rendering remains intentionally untested in this task because the operator requested text planning only until the frame/object plan is correct.

## 2026-08-11 — Verify a dependency-closed Reel scene with real Gemini images

### Summary

* Generated a real first-scene reference chain: empty room, complete Sarah+chair+desk+laptop initial unit, and the same unit with changed reaction and screen state.
* Removed the near-white matte and composited both unit states over the same empty room.
* Confirmed that physically dependent objects can be generated as one coherent unit while the room remains a separate immutable plate.
* Confirmed that Gemini does not reliably preserve exact readable price/interface text, so such content must be rendered programmatically.

### Files changed

* `staging/generate_solocruz_scene1_dependency_chain.py` — real reference-chain image generator and composite/contact-sheet builder.
* `docs/PROJECT_MEMORY.md` — recorded dependency-closed units, explicit state keyframes, and the programmatic screen-content boundary.
* `docs/CHANGELOG_AI.md` — recorded the real image verification.

### Decisions

* Image layers are based on physical composability, not one layer per semantic noun.
* A changed face, pose, device screen, or object condition requires a new reference-anchored keyframe.
* Exact screen copy and numbers belong to the renderer, not Gemini image pixels.

### Checks run

* Three sequential `gemini-3.1-flash-lite-image` generations completed successfully; no voice or video was generated.
* Visual inspection confirmed coherent room integration, a viewer-facing laptop screen, simultaneous visibility of Sarah's face and screen, and a changed facial/hand state.
* Visual inspection rejected generated screen lettering as insufficiently exact for production.

### Risks / TODO

* Add a universal screen-plane detector and perspective-mapped programmatic UI layer before this scene can be considered production-ready.
* Finish wiring the dependency-closed assembly/keyframe schema into the production Reel planner and renderer before generating the remaining scenes.

## 2026-08-11 — Build and verify the first real SoloCruz motion scene

### Summary

* Added mandatory pre-composite validation for exact component counts, complete silhouettes, visible screens, physical coherence, and safe margins.
* Added registered-pair validation so changed keyframes cannot add/remove limbs, furniture supports, devices, or alter unrelated geometry.
* Replaced destructive near-white matte removal with contrast-safe chroma extraction for the light silver laptop unit.
* Detected the laptop screen plane and perspective-mapped exact `$1,200` and `$2,400` interface states into it.
* Rendered a real 4.5-second vertical motion scene with an animated hook, state transition, and camera movement; no voice or music was generated.

### Files changed

* `staging/generate_solocruz_scene1_motion_proof.py` — validated keyframe generation, chroma extraction, screen UI renderer, and H.264 motion proof.
* `docs/PROJECT_MEMORY.md` — recorded universal asset-integrity, matte-selection, and exact-screen-rendering rules.
* `docs/CHANGELOG_AI.md` — recorded implementation and verification.

### Checks run

* Automatic image validation rejected missing, duplicate, unsupported, and cropped mandatory components before video assembly.
* Final video verified as H.264, 1080x1920, 30 fps, 4.5 seconds, with no audio stream.
* Visual frame-strip review confirmed a complete laptop, complete desk supports, person legs present from the initial frame onward, stable registered geometry, readable programmatic UI, large on-frame hook, emotional state change, and camera push-in.

### Risks / TODO

* The production Reel worker still needs the validated chroma/matte and screen-plane path integrated from this proof script before full 30-second automatic Reel generation.

## 2026-08-11 — Validate professional scene-layer extraction

### Summary

* Installed a dedicated local MPS environment with `SAM 2.1`, Grounding DINO, and ViTMatte.
* Extracted three independently usable visible layers from an existing SoloCruz scene: person, large foreground laptop, and wall lamp.
* Generated object masks, trimaps, RGBA PNG layers, and a checkerboard contact sheet. No new Gemini imagery, narration, music, or video was generated.

### Files changed

* `staging/layer-lab/extract_scene_layers.py` — reusable proof extractor using role-aware detection, SAM 2.1 masks, and ViTMatte alpha refinement.
* `staging/layer-lab/.venv/` — local-only model runtime; not a repository artifact.
* `staging/layer-lab/output/` — local-only masks, trimaps, layers, and visual QA artifacts; not a repository artifact.
* `docs/PROJECT_MEMORY.md` — recorded the validated extraction stack and its bounds.
* `docs/CHANGELOG_AI.md` — recorded installation and visual verification.

### Checks run

* Ran the stack on Apple M3 Pro with MPS enabled.
* Visually reviewed the person, laptop, and lamp RGBA layers against a checkerboard background.

### Risks / TODO

* The source composition contains normal occlusion: the table hides part of the person. Extraction correctly preserves only visible pixels, so this specific person layer cannot be moved in a way that exposes unseen body parts.
* Set up an on-demand GPU worker before making this a Blog Core production dependency; the VPS has no GPU.

## 2026-08-11 — Revalidate extraction on a SoloCruz deck scene

### Summary

* Replaced the unsuitable indoor proof source with an already generated SoloCruz sunset-deck scene containing ship, sea, deck, and a group of travellers.
* Extracted three distinct visible traveller layers from the one master frame using Grounding DINO, SAM 2.1, and ViTMatte.
* Left the partially occluded fourth traveller in the master rather than produce a broken independent cutout.

### Files changed

* `staging/layer-lab/extract_scene_layers.py` — supports multiple non-duplicate person detections for a scene-level extraction proof.
* `docs/PROJECT_MEMORY.md` — documented the universal separable-subject selection rule.
* `docs/CHANGELOG_AI.md` — recorded the deck-scene visual check.

### Checks run

* Visual review of source plus three RGBA layers on a checkerboard background.

### Risks / TODO

* The next stage remains Gemini-generated clean-plate creation from the same master, followed by registration and compositing. It must not start until this layer extraction is visually accepted.

## 2026-08-11 — Select a large-subject SoloCruz deck source

### Summary

* Reviewed existing SoloCruz image packs and rejected distant deck figures and dining-table groups as poor layer-extraction sources.
* Chose an existing ship-deck onboarding scene with large travellers, visible deck, ship, and sea context.
* Added a primary-subject size gate. It extracted two usable foreground traveller layers and exposed the third candidate as fragmented by occlusion, which is a valid rejection outcome rather than a layer count failure.

### Files changed

* `staging/layer-lab/extract_scene_layers.py` — filters small background detections so only large primary subjects are eligible.
* `docs/PROJECT_MEMORY.md` — records the quality-over-count layer rule.
* `docs/CHANGELOG_AI.md` — records source selection and visual validation.

### Checks run

* Visual review of the ship-deck source and extracted RGBA subjects on a checkerboard background.

## 2026-08-11 — Extract physically coherent traveller groups

### Summary

* Replaced individual-person extraction with universal spatial clustering before masking.
* The SoloCruz onboarding deck now yields two meaningful RGBA scene layers: foreground travellers and background crew, rather than fragmented individual people.

### Files changed

* `staging/layer-lab/extract_scene_layers.py` — clusters proximate people by depth/scale before unioning their SAM masks and refining one alpha matte per group.
* `docs/PROJECT_MEMORY.md` — records the group-layer invariant.
* `docs/CHANGELOG_AI.md` — records the verified group extraction result.

### Checks run

* Extracted and visually inspected foreground group and background group over a checkerboard background.

### Risks / TODO

* A clean plate must remove each accepted group and its contact shadows as a group. The renderer may move/reveal each group, but may not independently animate members inside the extracted group.

## 2026-08-11 — Preserve carried objects in group extraction

### Summary

* Extended group extraction beyond person masks to recognise and attach carried/worn scene objects.
* The SoloCruz foreground traveller group now includes its backpack, duffel, handbag, camera bag, and suitcase; the distant crew group no longer receives a duplicated foreground item.

### Files changed

* `staging/layer-lab/extract_scene_layers.py` — detects carried-object categories, assigns each object once by group depth, and unions it into its owner group mask.
* `docs/PROJECT_MEMORY.md` — records universal ownership rules for connected visual groups.
* `docs/CHANGELOG_AI.md` — records the visual validation.

### Checks run

* Re-extracted the existing SoloCruz onboarding frame and visually inspected both group RGBA layers.

## 2026-08-11 — Keep occluded depth groups in the static base

### Summary

* Added relationship-aware movement eligibility to the proof extractor.
* The partially covered distant crew group is now classified as static base content and omitted from movable RGBA output; the complete foreground traveller-and-baggage group remains the one extracted layer.

### Files changed

* `staging/layer-lab/extract_scene_layers.py` — replaces hard-coded layer-name filtering with projected-overlap/depth validation for independent movability.
* `docs/PROJECT_MEMORY.md` — records the universal scene-role contract.
* `docs/CHANGELOG_AI.md` — records the corrected visual output.

### Checks run

* Re-extracted and visually reviewed the master plus the sole eligible movable group.

### Risks / TODO

* Geometry alone cannot infer every semantic ownership or depth relationship. The production worker must obtain a scene-role contract from the configured vision planner, then validate it against the CV masks before media generation.

## 2026-08-11 — Run Gemini scene-role analysis on existing SoloCruz frames

### Summary

* Added and ran a text-only multimodal analyser through Blog Core's configured Gemini client against three existing SoloCruz frames.
* It returned structured physical groups, carried-object ownership, depth, movability, static-base content, clean-plate requirements, and extraction risks.
* No new images, narration, music, or video were generated.

### Files changed

* `staging/layer-lab/analyze_scene_roles.py` — reusable image-to-scene-role JSON analyser using the existing Blog Core Gemini client and structured schema.
* `staging/layer-lab/scene-role-analysis.json` — local result from the three-frame analysis; not a production artifact.
* `docs/PROJECT_MEMORY.md` — documents the vision-planner stage.
* `docs/CHANGELOG_AI.md` — records the real model validation.

### Checks run

* Parsed schema-valid JSON for boarding, shore-excursion, and onboard coffee-scene images.

### Risks / TODO

* Wire the analyser into the normal Reel workflow and require its returned contract to be accepted by the CV extraction validator before image generation or rendering.

## 2026-08-11 — Reject incorrect vision-only grouping for shore walkers

### Summary

* Re-ran the shore-walk scene analysis with explicit silhouette-contact instructions.
* Gemini still incorrectly classified all four walkers as independent, so its grouping output was rejected.
* The durable rule is now explicit: vision proposes relationships; instance-mask contact/occlusion validation decides whether people become a common layer.

### Files changed

* `staging/layer-lab/analyze_scene_roles.py` — strengthened scene-group instructions for visible silhouette geometry.
* `docs/PROJECT_MEMORY.md` — records the vision-only limitation and replacement rule.
* `docs/CHANGELOG_AI.md` — records the rejected analysis.

### Checks run

* Parsed two schema-valid Gemini analyses for the shore-walk frame; both were visually reviewed and the second was rejected for grouping.

## 2026-08-11 — Reject unsuitable scene sources and proximity-based person grouping

### Summary

* Added a universal scene-suitability gate: low-light, low-contrast, crowded, fragmented, or clean-plate-unsafe frames are rejected before they become layered-motion sources.
* Replaced the proof extractor's proximity clustering. It now keeps all detected people independent until a later physical-contact graph, backed by instance masks and the vision contract, proves a merge.
* Strengthened the Gemini role-analysis contract to require visible-connection explanations and distinguish `layerable`, `static_only`, and `reject_for_layered_motion` scenes.

### Files changed

* `staging/layer-lab/analyze_scene_roles.py` — suitability decision plus explicit silhouette and merge rules.
* `staging/layer-lab/extract_scene_layers.py` — removes the invalid bounding-box-gap merge heuristic.
* `docs/PROJECT_MEMORY.md` — records the durable eligibility and grouping rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile staging/layer-lab/analyze_scene_roles.py staging/layer-lab/extract_scene_layers.py`

### Risks / TODO

* The current shore-walk analysis must not be used as a reference grouping; the actual contact relationship must be resolved from masks or explicit review before extraction. No images, audio, or video were generated.

## 2026-08-11 — Reject layers anchored to shared scene geometry

### Summary

* Tightened the universal clean-plate eligibility rule: a scene is rejected when any intended moving layer materially crosses or is anchored to shared furniture, fixtures, controls, railings, screens, tableware, or other structured base geometry.
* This rejects visually attractive but technically unsafe scenes before segmentation instead of extracting partial people and attempting to reconstruct their shared context later.

### Files changed

* `staging/layer-lab/analyze_scene_roles.py` — adds clean-plate feasibility requirements to the scene-role contract.
* `docs/PROJECT_MEMORY.md` — persists the clean-plate eligibility rule.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Text-only re-analysis is run after the contract update; no media-generation operation is permitted by this analyser.

## 2026-08-11 — Simplify the clean-plate edit instruction

### Summary

* Replaced the verbose clean-plate prompt with an in-place edit command that makes pixel preservation the dominant requirement and names only the groups to remove.
* Removed numeric dimension instructions and exhaustive scene restatement, which distracted from preserving the reference image.

### Files changed

* `staging/layer-lab/plan_and_create_clean_plates.py` — concise clean-plate prompt.
* `docs/PROJECT_MEMORY.md` — durable prompt rule.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Prompt construction review only. No replacement image, audio, or video was generated by this change.

### Correction

* Removed a contradictory preservation list from the first revision. The clean-plate instruction is now a single unambiguous frame-invariance condition with only the named groups as exceptions.

## 2026-08-11 — Verify concise Gemini clean-plate edit on one SoloCruz frame

### Summary

* Ran one Gemini image-edit request against the existing boarding-gangway frame using the concise in-place prompt.
* The accepted review artifact removes only the planned foreground groups and their luggage while retaining the existing gangway, ship, harbour, and background scene.

### Files changed

* `staging/layer-lab/clean-plate-review/05-boarding-group-clean-plate-v2.jpg` — review-only Gemini clean plate.
* `docs/PROJECT_MEMORY.md` — records the verified clean-plate prompt behavior.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Visual comparison against the source frame.
* Verified output dimensions remain 768x1376.

### Risks / TODO

* The review artifact must still pass the future layer-extraction and reconstruction checks before it is used in a rendered Reel. No other source frame or media type was generated.

## 2026-08-11 — Verify concise Gemini clean-plate edit on the shore-walk frame

### Summary

* Ran one Gemini image-edit request for the existing SoloCruz shore-walk master using the accepted concise in-place clean-plate prompt.
* The review artifact removes only the three foreground traveller groups while preserving the harbour street, ship, buildings, and distant pedestrians.

### Files changed

* `staging/layer-lab/clean-plate-review/05-shared-shore-day-clean-plate-v2.jpg` — review-only Gemini clean plate.
* `docs/PROJECT_MEMORY.md` — records the second verified frame.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Visual comparison against the source frame.
* Verified output dimensions remain 768x1376.

### Risks / TODO

* The clean plate is not itself a final Reel frame. Its associated group masks and later recomposition must pass visual QA before rendering.

## 2026-08-11 — Run Gemini creative direction on two approved SoloCruz scenes

### Summary

* Ran a text-only Gemini creative-direction pass for the boarding and shore-walk scenes. The model received the source frame, approved foreground groups, clean-plate availability, and a short editorial essence for each scene.
* It proposed staged entries, renderer text, light graphic treatment, and a camera treatment, but the output is rejected as a production plan because both scenes reuse the same push-in/fade/drift pattern.

### Files changed

* `staging/layer-lab/plan_scene_motion_direction.py` — reusable text-only creative-direction utility.
* `staging/layer-lab/motion-direction-review/*-motion-direction.json` — rejected review proposals, not production artifacts.
* `docs/PROJECT_MEMORY.md` — records proposal-only status and required diversity validation.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Parsed schema-valid Gemini responses for both scenes.
* Reviewed camera, reveal, text, and graphic proposals against the cross-scene variety requirement.

### Risks / TODO

* Implement a validator for repeated camera/reveal combinations before motion-direction output can reach image/layer/video generation. No media beyond the previously approved clean plates was generated.

## 2026-08-11 — Plan two Reel scenes as one cross-scene Gemini direction

### Summary

* Replaced isolated scene planning with one text-only Gemini request containing both approved master frames and their constrained available layers.
* The proposal now contains beat timing, whole-scene camera scales/offsets, layer-reveal mechanisms, overlay coordinates/animation, and scene-specific graphic treatments. It deliberately differentiates the two camera paths and reveal styles.

### Files changed

* `staging/layer-lab/plan_motion_direction_pair.py` — reusable paired creative-direction planner.
* `staging/layer-lab/motion-direction-review/pair-motion-direction-v2.json` — review-only Gemini proposal.
* `docs/PROJECT_MEMORY.md` — records the paired planning rule and review-only status.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Parsed the schema-valid paired Gemini response and reviewed its camera, reveal, text, and graphic instructions.

### Risks / TODO

* This is a direction proposal, not an approved render specification. Review and simplify any unsuitable overlay/graphic choices before layer extraction or rendering. No new image, audio, music, or video was generated.

## 2026-08-11 — Render a two-scene full-canvas SoloCruz motion review

### Summary

* Prepared full-canvas RGBA foreground layers from the existing master/clean-plate pairs, then rendered the approved two-scene plan locally at 768x1376, 24 fps, for 9 seconds.
* The renderer composites all layers in their native registered canvas positions and applies camera motion only after the full scene is assembled. It generated neither new source art nor audio.
* Fixed one renderer-only text-alpha defect found during visual keyframe QA and produced v3 with readable boarding copy.

### Files changed

* `staging/layer-lab/analyze_scene_roles.py` — adds normalized segmentation hints to the text-only contract.
* `staging/layer-lab/render_clean_plate_motion_review.py` — review renderer with full-canvas layers, camera, reveal masks, copy, and graphics.
* `staging/layer-lab/motion-render-review/solocruz-two-scene-motion-review-v3.mp4` — local review-only render.
* `staging/layer-lab/motion-render-review/full-canvas-layers-v3/*` — review-only registered RGBA layers.
* `docs/PROJECT_MEMORY.md` — records full-canvas rendering contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python -m py_compile` for the analyser and renderer.
* `ffprobe`: H.264, 768x1376, 24 fps, 9.0 seconds.
* Visually checked reveal and text keyframes; rebuilt after the alpha defect.

### Risks / TODO

* This is an internal review render, not an Instagram publication. Future production must replace segmentation hints with a validated scene-role/mask contract before general dashboard use.

## 2026-08-11 — Strengthen motion variety, typography, shadows, and graphics

### Summary

* Added distinct layer entrances from left, right, top, and bottom while retaining full-canvas registration after settling.
* Increased overlay typography size and contrast with a soft halo and contour instead of a solid text panel.
* Strengthened layer contact shadows and replaced faint line decoration with visible rings, route nodes, arrows, and split-path graphics.

### Files changed

* `staging/layer-lab/render_clean_plate_motion_review.py` — v5 review renderer changes.
* `staging/layer-lab/motion-render-review/solocruz-two-scene-motion-review-v5.mp4` — regenerated review video.
* `staging/layer-lab/motion-render-review/qa-v5/timeline/*` — keyframe QA images.
* `docs/PROJECT_MEMORY.md` — durable renderer rules and verification record.

### Checks run

* Project virtualenv `staging/layer-lab/.venv/bin/python -m py_compile`.
* Render completed successfully with the project virtualenv.
* `ffprobe`: H.264, 768x1376, 24 fps, 9.0 seconds.
* Visually checked boarding and shore keyframes for contrast, entrance variety, shadows, and graphics.

### Risks / TODO

* This remains a local review render. It does not publish and does not yet replace the production GPU extraction pipeline.

## 2026-08-11 — Remove decorative graphics and add subject-focused camera motion

### Summary

* Removed all decorative rings, route lines, arrows, and other renderer graphics from the review direction.
* Directional layer entrances now move the complete subject as one unit; they no longer combine side/top/bottom motion with reveal masks.
* Added timed camera shots with zoom and focus transitions between scene subjects. Text is rendered after the camera pass so it stays readable and screen-anchored.
* Added local luminance-based text contrast: the renderer chooses the fill and opposing contour from the actual background under the copy.

### Files changed

* `staging/layer-lab/render_clean_plate_motion_review.py` — v6 renderer behavior.
* `staging/layer-lab/motion-render-review/solocruz-two-scene-motion-review-v6.mp4` — regenerated review video.
* `staging/layer-lab/motion-render-review/qa-v6/timeline/*` — keyframe QA images.
* `docs/PROJECT_MEMORY.md` — durable motion and overlay rules.

### Checks run

* Project virtualenv compile and render succeeded.
* `ffprobe`: H.264, 768x1376, 24 fps, 9.0 seconds.
* Visual QA checked the camera close-up, focus transition, complete directional subject entry, and screen-anchored text.

### Risks / TODO

* This remains a local review render only. It does not publish and does not generate new media.

## 2026-08-11 — Repair layer masks and sequence camera after entrances

### Summary

* Replaced difference-only review masks with cached SAM masks assembled from each person and their owned/contact objects.
* Repaired the foreign-clothing fragment on the independent boarding woman and the internal clothing/bag holes in the shore scene.
* Held the camera during object entrances, then added stronger close-ups and focus transfers between the first and next appeared groups.
* Added automatic quiet-zone text placement and local contrast selection; shore copy now uses the large open sky instead of the crowded lower frame.

### Files changed

* `staging/layer-lab/prepare_review_masks_sam.py` — cached SAM mask preparation for approved review scenes.
* `staging/layer-lab/render_clean_plate_motion_review.py` — v8 masks, camera timing, focus shots, and text layout.
* `staging/layer-lab/motion-render-review/sam-masks-v8/*` — repaired full-canvas masks.
* `staging/layer-lab/motion-render-review/solocruz-two-scene-motion-review-v8.mp4` — regenerated review video.
* `staging/layer-lab/motion-render-review/qa-v8/timeline/*` — visual QA keyframes.
* `docs/PROJECT_MEMORY.md` — durable mask, camera, and text-placement rules.

### Checks run

* Compiled both Python utilities with the project virtualenv.
* Ran SAM 2.1 mask preparation on Apple MPS and rendered the full video locally.
* `ffprobe`: H.264, 768x1376, 24 fps, 9.0 seconds.
* Visually checked entrances, mask integrity, close-ups, focus transfer, and text placement at seven timeline positions.

### Risks / TODO

* This is still a review-only two-scene render and is not published. The reusable production worker must receive object ownership and prompt boxes from the validated scene-role contract rather than fixed review coordinates.

## 2026-08-11 — Complete hands and harden text-safe motion review

### Summary

* Repaired the boarding group's missing handshake parts with a narrow contact-area patch while excluding unrelated background luggage.
* Restricted copy to genuinely free upper zones and corrected local fill/contour contrast.
* Retained whole-object entrances, delayed camera movement, close-ups, and focus transfers between appeared groups.

### Files changed

* `staging/layer-lab/prepare_review_masks_sam.py` — narrow contact-area reconstruction and v10 cached masks.
* `staging/layer-lab/render_clean_plate_motion_review.py` — v10 safe-zone typography and camera sequence.
* `staging/layer-lab/motion-render-review/sam-masks-v10/*` — final full-canvas masks.
* `staging/layer-lab/motion-render-review/solocruz-two-scene-motion-review-v10.mp4` — final review video.
* `staging/layer-lab/motion-render-review/qa-v10/timeline/*` — visual QA keyframes.
* `docs/PROJECT_MEMORY.md` — durable extraction, typography, and camera rules.

### Checks run

* Compiled the mask preparation and renderer utilities with the project virtualenv.
* Ran SAM 2.1 mask preparation and the complete local render.
* Verified with `ffprobe`: H.264, 768x1376, 24 fps, 9.0 seconds.
* Visually checked six timeline frames for complete hands and clothing, absence of background-object leakage, upper-safe-zone text, contrast, close-ups, and focus transfer.

### Risks / TODO

* This remains a local review artifact and was not published. No new image, voice, audio, music, or video-model generation was performed.
