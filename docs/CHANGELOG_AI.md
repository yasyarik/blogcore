## 2026-09-12 — Published separate monthly media-plan calendars for Aleksei and Veronika

* Read the supplied Google Sheet as a non-authoritative reference without changing it. Retained only the useful brand split: Aleksei focuses on premium new builds and investment decisions; Veronika focuses on houses, villas, family living and relocation.
* Added a reusable `/media-plan` renderer with separate host-scoped data, monthly overview, graphic calendar, platform colours, progress/status pills, factory-vs-owner filters, production deadlines and expandable Reels instructions.
* Materialized October 2026 independently for `karpaleksei.com` and `veselovaveronika.com`: 64 rows each (9 articles, 9 one-render Instagram+TikTok carousels, 16 Telegram posts, 22 Threads posts and 8 owner-recorded Reels). Every Reels row contains a hook, talking points, physical shot list, recording deadline and personal publication time.
* Added an optional private Telegram reminder recipient to each site Telegram connection. The scheduler sends deduplicated alerts 24 hours before recording, three hours before publication and at publication time; it never substitutes the public channel chat for the private recipient.
* Added the exact Nginx `/media-plan` proxy on both domains and enforced `noindex, nofollow, noarchive` in both HTML and HTTP headers with private no-store caching. Neither calendar is in a sitemap.
* Verification: Python compilation passed locally and on production; both Blog Core PM2 processes are online; health returned 200; both calendar URLs returned 200 with 64 rows, 8 owner tasks and the noindex contract; Playwright desktop/mobile review found no console errors, correct responsive layout and an owner filter showing exactly 8 Reels.
* Production recovery: `/var/backups/blog-core/pre-personal-media-plan-20260912` contains the prior application modules, Nginx files and SQLite database.

## 2026-09-06 — Replace SoloCruz episode 02 with a visual comedy story

* Rewrote `Episodes 02-24 Detailed!C2:F2` and `H2:J2`; `G2`, `K2` and every other episode remain unchanged.
* Removed the booking-list, tablet-scrolling, code-comparison and cabin-chain plot. Security now believes Cruz is an unlisted passenger; an event host summons her, and a packed theatre reveals that her cabin is compensation for serving as the ship's invited cruise expert.
* Reversed the opening power dynamic in the payoff: the security chief who came to remove Cruz is seated in the front row. Two microphone taps echo the opening door knocks and complete the comic loop.
* All three ten-second prompts retain three timed shots, reference continuity, exact short English dialogue and scene-specific physics. Exact readback matched the requested cells; no media was generated or published.

## 2026-09-06 — Remove repeated boilerplate from SoloCruz production prompts

* Replaced the repeated long-form instruction blocks in all 72 active cells of `Episodes 02-24 Detailed!H2:K24` with a concise generator contract.
* Preserved every timed three-shot staging block, exact English dialogue, supplied-reference continuity and scene-specific physical constraints. Episode 02 clip 01 retains its special one-door, one-opening choreography.
* Corrected episode 02 clip 01 after an ambiguous phrase made `pilot` look like the actor performing the knock. The prompt is now self-contained for Gemini: the supplied door reference establishes the closed door and security characters visible through its window, the supplied Cruz reference establishes her design, security knocks twice, and Cruz then opens that one door once. It contains no reference to a pilot, previous episode or information unavailable to the generator.
* Reduced active prompts from an average of 5,396 characters to 1,721 characters (68.1% reduction; 1,535–2,250 characters). Exact readback matched all 72 prompts and 20 end-of-episode placeholders; every active prompt still contains exactly three staged shots.
* Left episode metadata, plot, engagement structure, other tabs and all generation/publication state unchanged. The edited tab was visually checked in Google Sheets.

## 2026-09-06 — Remove repeated boilerplate from YAS AI film prompts

* Replaced the repeated long-form instruction blocks in all 75 active cells of `Episodes 01-24 Detailed!H2:K25` with a concise production contract.
* Preserved every timed three-shot staging block, exact quoted English dialogue, supplied-reference continuity and scene-specific physics; removed duplicated episode-purpose, camera-theory, performance, sound and output prose.
* Reduced active prompts from an average of 4,853 characters to 1,630 characters (66.4% reduction; 1,449–1,829 characters). Exact readback matched all 75 prompts and 21 end-of-episode placeholders; all prompts retain three staged shots and zero audited known-person trigger terms.
* Left columns `A:G`, the original `Лист1`, story structure and all publication/generation state unchanged. The updated tab was visually checked in Google Sheets.

## 2026-09-05 — Expand SoloCruz episodes 02–24 into detailed generator prompts

* Added the first-position Google Sheet tab `Episodes 02-24 Detailed` containing only episodes 02–24: 23 episode rows and 72 full ten-second prompts. Episode 01 is not duplicated.
* Added a distinct hook, retention mechanism and comment/CTA provocation for every episode. Each prompt now includes timed staging, bounded cast, camera execution, explicit prop/contact physics, acting, exact English dialogue, synchronized sound, continuity and output restrictions.
* Removed the invented transition action involving Cruz recording or holding a phone. Episode 02 starts from the security knock and door opening, with an explicit ban on adding a phone or recording action.
* Renamed v3 tabs to `SYNOPSIS ONLY` / `OLD` so summaries cannot be mistaken for production prompts. Verified all 24 sheet rows including header match the authored data exactly; no generation, scheduling or publication occurred.
* Replaced the episode 02 clip 01 prompt after the first generation failed continuity. The corrected prompt binds attached references semantically to exact Cruz appearance/outfit, exact cabin and entrance-door design, and exact Marcus identity; it requires one continuous door opening and forbids a phone, duplicate door, rebuilt cabin, replay or reverse-angle opening.
* Revised H2 again after Google's known-person safety error: removed identity/face-copy language and framed all character references as original fictional 3D model sheets. The set, clothing, hairstyle and single-door continuity requirements remain, but the prompt no longer uses known-person replication wording.
* After the same provider error recurred, removed all character names from H2 as a false-positive safeguard (`Cruz` can collide with a known-person surname). The prompt now has zero occurrences of `Cruz`, `Marcus`, `identity`, `real person`, `public figure`, `celebrity`, or `known people`; door/set continuity and physical staging are unchanged.
* Corrected that speculative diagnosis after the user confirmed all people are invented. Rebuilt H2 without likeness-transfer phrasing or face/skin/eye/body descriptors. The prompt now asks the supplied series artwork only for hair, costume, uniform and set continuity; detailed single-door choreography remains intact.
* Rebuilt H2 once more with exclusively fictional-character terminology and verified it contains none of the human/known-person trigger vocabulary or character names. The scene still retains the supplied hairstyle, costume, uniform, cabin, door and one-opening motion requirements.
* Applied the same fictional-character-only reference vocabulary to all 72 active generator prompts in `Episodes 02-24 Detailed!H2:K24`. Preserved the 20 non-generator end-of-episode placeholders and the already-corrected H2 prompt. Exact readback matched all written cells, and the full active range contains zero audited human/portrait/realism/known-person terms.
* Audited all 23 current episodes against the newly supplied 30-second SoloCruz comedy formula. Estimated exact structural compliance at 52%, with episodes 03, 06, 10, 13, 14 and 24 closest to the target. Recorded the principal gaps: late/mismatched hooks in several rows, few two-attempt escalation patterns, cliffhanger-heavy rather than comic-loop endings, serial context dependence, and only three or four continuous shots instead of 9–13 edited shots. No spreadsheet cells, prompts or generated media were changed.

## 2026-09-06 — Apply the SoloCruz hybrid 30-second episode formula

* Reworked all episodes 02–24 in the authoritative `Episodes 02-24 Detailed` tab without changing the established mystery, passenger and romance arcs. Each episode now closes one recognizable cruise microstory before adding a compact serial tag.
* Updated `C2:F24` with corrected literal 0–2-second hooks, two-step escalation summaries, comment prompts and a specific share-recipient rationale for every episode.
* Rebuilt all 72 generator prompts in `H2:K24`: exactly three clean-cut shots per ten-second generation, nine shots per standard episode and twelve in the three 40-second episodes. Removed the former one-continuous-shot instruction, required visual change every 1.5–2 seconds and retained detailed object/door/contact continuity.

## 2026-09-06 — Complete the YAS AI film with the same hybrid episode logic

* Preserved the original `Лист1` outline and added the first-position `Episodes 01-24 Detailed` production tab to spreadsheet `1-Nn5AxeDEXm3MqJ95-0apfIFqWj-mKyqFO-pjPipMrk`.
* Reworked all 24 episodes around a self-contained operational conflict, literal 0–2-second hook, two worsening attempts, completed result, visual callback and compact serial transition. Kept all twelve original industry problem/solution pairs and the existing YAS travel/mysterious-character arc.
* Authored 75 production-grade ten-second prompts: exactly three clean-cut shots per prompt, nine shots per standard 30-second episode and twelve in episodes 08, 16 and 24. Added detailed physics, reference continuity, bounded fictional cast, exact English dialogue, sound and output restrictions.
* Added an explicit comment provocation and specific share-recipient rationale to every episode. Exact readback matched all 25×11 authored cells; the rendered sheet was visually checked, and cramped Season/Duration columns were widened. No media was generated or published.
* Preserved episode 02's supplied-reference contract: the one cabin door opens once within the first two seconds, never reopens or duplicates, and subsequent shots inherit the already-open state. The remaining prompts continue to describe only original fictional 3D characters and design references.
* Verified exact post-write equality for both edited ranges, 23/23 literal 0–2 hooks, 23/23 specific share rationales, 72 active prompts, 20 untouched end-of-episode placeholders, 9/12 episode shot counts, 5–31 dialogue words and zero audited human/portrait/known-person terms. No video, image, social draft, schedule or publication was created.

## 2026-09-05 — Restore SoloCruz's original three story lines in v3

* Re-read the source Season 1 and preserved its core episode beats in a mapped rewrite: existing user-made pilot plus 23 follow-up episodes across three seasons, 72 new ten-second scene blocks with dialogue and physical staging.
* Added `24 Episodes v3` and `Series Bible v3` to the original Google Sheet, placed first for clarity, and verified all saved cells against the authored data. Original script/character tabs remain unchanged.
* Marked v2 rejected in its tab names and local document: it had replaced the user's premise with an archive/mother plot. Added `docs/SOLOCRUZ_SERIES_V3.md` and updated durable memory to distinguish user requirements from proposed new plot details.
* Preserved the pilot as a locked existing asset based on the user's description; its duration and last frame are not claimed verified. No generation, scheduling, publication or production-code changes.

## 2026-09-05 — Rewrite all 24 SoloCruz animated serial episodes (v2 subsequently rejected)

* Added `24 Episodes v2` and `Series Bible v2` to the existing user-provided Google Sheet, preserving the original script and character tabs. Added the full local script in `docs/SOLOCRUZ_SERIES_V2.md`.
* Created three eight-episode arcs with 75 connected ten-second scene prompts, short English dialogue, Russian editorial notes, physical blocking, prop custody, character development and season payoffs. The 30–40-second episode remains the unit of storytelling, not each ten-second generation fragment.
* Recorded the user's rejection of the iPhone-UGC treatment for this animated serial and the entertainment-first, sparse-branding requirement. Earlier UGC notes are explicitly superseded for this series.
* Verified saved spreadsheet values against the authored rows; checked browser layout and reduced frozen columns for narrow windows. No media was generated and no publishing settings, queues or public posts were changed.

## 2026-09-03 — Publish first Laycanmatch Facebook post

* Immediately submitted the first queued Laycanmatch Facebook draft through Zernio at the user's request. Zernio reconciliation confirmed it as published; Blog Core now stores the public Facebook permalink. The remaining ten drafts keep their local daily 18:00 `Europe/Warsaw` queue slots.

## 2026-09-03 — Connect and schedule Laycanmatch Facebook batch

* Connected the LaycanMatch Facebook Page through the existing Zernio profile after expanding the prior Facebook OAuth page selection; the old SoloCruz selection remains intact.
* Bound the new LaycanMatch Zernio account to the Laycanmatch site in Blog Core, generated 11 Facebook-native article adaptations plus 11 covers, and queued them locally one per day at 18:00 `Europe/Warsaw`, 4–14 September. No post was sent during setup.
* Verified all 11 Facebook covers are exactly 1200×630, all 11 drafts retain local due timestamps, and Blog Core health is `ok`.

## 2026-09-03 — Generate and schedule SoloCruz Facebook batch

* Generated 19 Facebook-native article adaptations and 19 article-specific magazine-cover images through Blog Core's live Gemini runtime, then scheduled all 19 factory-owned drafts daily at 18:00 `Europe/Warsaw`, 4–22 September. Nothing was sent to Facebook during generation or scheduling.
* Added the native Facebook 1200×630 image derivative after Gemini generation. It crops and resizes the finished image only; it does not place any programmatic text on the cover.
* Verified all 19 generated Facebook cover files are exactly 1200×630, all 19 records remain `DRAFT` with a local due timestamp, and Blog Core health is `ok`.

## 2026-09-03 — Preserve Blog Core Gemini runtime for manual batches

* Documented that production Blog Core loads its Gemini credentials through its protected runtime environment. Manual `app.py` batch invocations must use the same environment-loading sequence; this avoids false missing-key failures without exposing or duplicating credentials.

## 2026-09-03 — Added universal Facebook Page editorial contour

* Ported the useful SoloCruz Facebook mechanics into Blog Core: separate Facebook-native copy adaptation, one canonical article URL, a dedicated 1200×630 magazine-cover asset and generic review/publish support through the site-scoped Zernio mapping.
* Added Facebook to setup, Distribution, draft storage, review and delivery status handling. Superseded: the initial note that no Facebook page was configured. SoloCruz's configured Page mapping was subsequently verified and used only to prepare a local factory queue; no external post was sent.

## 2026-09-03 — Activated YAS Threads queue

* Materialized and scheduled all 14 ready YAS Threads work items: one daily post at 18:00 `Europe/Warsaw`, from 3 through 16 September. No post was sent during setup.
* Added a dedicated factory-owned Threads queue worker. It submits the already-prepared native draft to Zernio only after its local due timestamp; it never asks Zernio to maintain the calendar.

## 2026-09-03 — Cancelled provider-owned YAS Reddit schedule

* Deleted the six future YAS Reddit drafts from Zernio and marked their corresponding Blog Core social-post records `CANCELLED`. The seventh had already been published, so it was left live and its stale local status was corrected to `PUBLISHED`.
* Added a publish-time guard: Zernio requests containing a Reddit draft cannot include `scheduledFor`. Blog Core now remains the only schedule owner for Reddit; Zernio is called only for immediate delivery when the local queue is due.

## 2026-09-02 — Returned YAS LinkedIn post to draft for cover review

* Returned social post `208` for `Frontline Technical Bug Reproduction and Engineering Handoff: Designing Internal Triage Pipelines` to Blog Core `DRAFT` and generated a new unpublished `1065×795` LinkedIn cover (`Taming Bug Handoffs`). The external post was not deleted because its stored provider record does not contain an editable LinkedIn post identifier.
* Returned four more YAS LinkedIn posts to `DRAFT` and generated unpublished replacement covers: `Product Development Company vs Software Development Agency`, `Workflow Automation Cost: Scope, Integrations and Maintenance`, `Build the Smallest Working System That Resolves the Constraint`, and `Custom Software Development Services`.
* Shortened the maximum generated cover headline from 25 to 21 characters and added a no-clipping requirement after the `Smallest Working System` preview rendered beyond the frame edge.
* Marked the four reviewed YAS LinkedIn drafts as queued for automatic publication while retaining their scheduler-required `DRAFT` social-post state and their current generated covers.

## 2026-09-02 — LinkedIn hero prompt direction corrected

* Removed the broad bans on people, offices, desks, meetings, laptops, dashboards, floating UI, handshakes and generic business imagery from the dedicated LinkedIn hero prompt.
* Replaced the cinematic wording with a bright, glossy magazine-cover finish and an explicit attention-grabbing wow effect.
* Generated an unpublished LinkedIn-hero review image with the corrected prompt; no LinkedIn post was sent.
* Replaced full article-title rendering with a dynamic 2–5-word, 25-character cover headline derived only from the article title. Gemini uses the full title for the photo concept and renders the short cover line as the sole centred 55–60%-wide magazine headline.
* Corrected the LinkedIn asset contract: the temporary `1200×675` 16:9 crop was wrong. Dedicated LinkedIn heroes now use the established `1065×795` (3× `355×265`) centred crop without letterboxing; the current review asset was converted without regeneration.
* Added a title-specific photographic-concept gate: one bold, physically real visual premise must express the article's central tension and be visually distinct from generic startup, AI, software or consulting imagery.
* Removed the business/LinkedIn/startup/AI/software/consulting genre cues from the dedicated LinkedIn hero prompt. The image is now directed as a glossy, authored editorial magazine-cover visual story rather than corporate photography.
* Removed the stale `16:9` feed cue from the image prompt so Gemini composes for the actual `1065×795` delivery frame rather than a wide asset that would need aggressive side cropping.
* Strengthened LinkedIn cover typography to a bright, bold magazine headline with a pronounced shadow and a protected calm background field; also removed routine desk-work setting cues from its shared photo direction.
* Prohibited punctuation around or inside future LinkedIn cover headlines and added matching headline validation after Gemini previously added unwanted quotation marks.
* Replaced the surprise/scale/transformation/wow direction that caused futuristic abstractions with a present-day, photorealistic magazine-feature scene: a familiar location, natural scale and a tangible consequence of the title's central choice.
* Unified article-photo and LinkedIn-photo art direction. Article hero images no longer receive LinkedIn headline instructions, and body images are constrained to their exact anchor paragraph rather than the complete article; all article images prohibit readable text.

## 2026-09-02 — Made EPR Scan article crosslinking visible

* Diagnosed that the first draft already contained five valid in-body links, but the native renderer presented their paragraphs as ordinary copy, making the crosslinking effectively invisible.
* Updated the renderer to match declared `internalLinks` against in-body destinations and apply a distinct native contextual-reading card without replacing localized text. Supported locale prefixes are normalized for EN/DE/FR/ES reuse.
* Restyled the one-item `Recommended next` block as a compact dark CTA with a lime action card, removing the oversized empty column shown in review.
* Verified five contextual cards for `/packaging-epr`, `/ppwr`, `/guides/do-small-sellers-need-ppwr`, `/selling-to-eu/from-outside-eu` and `/countries`, plus the `/tools/ppwr-checker` CTA. Every target returned HTTP 200.
* Production typecheck, scoped ESLint, build, multilingual integration, release, sitemap crawl and localization checks passed. Lighthouse Accessibility remained 100 with contrast and link-name checks passing.
* The content job remains English-only `DRAFT`, with zero localization rows and no public article route. Recovery snapshot: `/var/www/eprscan-release-backups/pre-crosslink-presentation-20260902-1550`.

## 2026-09-02 — Polished the EPR Scan native article presentation

* Removed `Pending assignment`, `Pending` review date and `Pending` ruleset values from the English draft header. The review surface now shows the real editorial author and calculated reading time, while the compact draft banner communicates unpublished status.
* Rebuilt the article contents as a numbered navigation panel with clear grouping, readable spacing and mobile reflow.
* Rebuilt data tables as bordered desktop data cards with aligned columns, zebra rows and tabular dates. On phones, the same semantic table becomes a stack of locale-derived labelled cards instead of clipping or requiring horizontal reading.
* Rebuilt FAQ output as accessible native accordions with bordered cards, 44px-plus targets, visible focus, plus/minus state and contained answers. Also styled figures, captions, workflows, quotes and recommended-next cards into the same native EPR Scan system.
* Preserved the English-only `DRAFT` state: no localization records were created, no public article route was added and the preview remains `noindex`, no-store and absent from the sitemap.
* Verified the candidate at desktop and mobile sizes, including an opened FAQ and the responsive table. Production typecheck, scoped ESLint, build, multilingual integration, release, sitemap crawl and localization checks passed. Lighthouse Accessibility reached 100 with heading order, table headers and color contrast passing.
* Recovery snapshot: `/var/www/eprscan-release-backups/pre-article-style-polish-20260902-1528`.

## 2026-09-02 — Generated the first EPR Scan English approval draft

* Created one English-only, evidence-led content job for recommendation 41: `When does the PPWR apply to ecommerce sellers?` (`5c9fda97f3ca8c064871e6a6`). The draft contains 1,506 words, seven main sections, five FAQs, one hero and three body images.
* Kept the job in `DRAFT`: no DE/FR/ES localization rows were created and no article was published. RU and IT remain excluded from the locale contract.
* Added EPR Scan's native `/content-preview/[id]` renderer, an unpublished-review banner, robots `noindex`, no-store delivery and local Blog Core asset import. The draft is absent from the public sitemap.
* Extended `eprscan-blog-core-content.path` to watch both draft and published stores. Published payload validation remains strict and unchanged; draft ingestion accepts only EN source with the declared EN/DE/FR/ES target contract, no publication timestamp and no translations.
* Verified production typecheck, scoped ESLint, multilingual integration (60 public variants, 10 English hubs and 16 private routes), release checks, dynamic sitemap crawl, localization completeness, the preview's single H1/four images/noindex banner and 200 responses for every preview image.
* Blog Core database recovery snapshot: `backups/blog_core-pre-eprscan-first-en-draft-20260902-1415.sqlite3`. EPR Scan deployment recovery snapshot: `/var/www/eprscan-release-backups/pre-draft-preview-20260902-1448`.

## 2026-08-13 — Remove Reel outlines and make camera motion continuous

### Summary
* Removed the uneven white silhouette treatment from the real SoloCruz Reel and retained only natural soft/contact shadows.
* Replaced start-stop camera beat execution with one continuous cubic trajectory through wide, medium, close-up, and target-transfer destinations.
* Re-rendered the existing seven scenes without generating new images or voice.

### Files changed
* `app.py` — universal director prompt now requires uninterrupted camera velocity and treats beats as destinations rather than separate moves.
* `reel_renderer.py` — natural two-depth shadows and continuous Catmull-Rom/Hermite camera interpolation.
* `docs/PROJECT_MEMORY.md` — durable shadow and continuous-camera contract.
* `docs/CHANGELOG_AI.md` — recorded this correction.

### Checks run
* Compiled `app.py` and `reel_renderer.py` in the VPS virtual environment.
* Numerically sampled the camera trajectory at 100 fps and verified smooth interpolation from establishing framing to close-up.
* Re-rendered a 30.041667-second, 1080x1920 H.264 draft from existing visual checkpoints.
* Extracted and visually reviewed 25 frames across all seven scenes; confirmed outlines are gone and framing progresses continuously through wide, medium, and close views.
* Blog Core health returned `ok`; post 33 remains `DRAFT` with no generated voice and no publication.

### Risks / TODO
* Hard cuts between separate scenes remain intentional; continuity applies within each scene up to its cut.

## 2026-08-13 — Prevent stale Reel previews after re-render

### Summary
* Fixed the Reel review page showing an older MP4 after a successful re-render.
* Every future Reel render now writes a uniquely versioned video and poster filename.
* Reel preview HTML and social-asset responses now explicitly disable browser and intermediary caching; the preview also appends the render token to media URLs.
* Pointed SoloCruz post 33 at a new versioned copy of the already-rendered final video without generating media again.

### Files changed
* `app.py` — versioned Reel filenames, cache-busted preview media URLs, and no-store response headers for review HTML and social assets.
* `docs/CHANGELOG_AI.md` — recorded the stale-preview correction.

### Checks run
* Compiled `app.py` and restarted `blog-yas-core`; `/health` returned `ok`.
* Verified the preview references `instagram-reel-20260813T161210Z.mp4?v=20260813T161210Z`.
* Verified preview HTML returns `Cache-Control: no-store` with Cloudflare `DYNAMIC` status.
* Verified the new MP4 returns `Cache-Control: no-store` with Cloudflare `BYPASS`, a new filename, and a `2026-08-13 16:12:10 UTC` modification time.

### Risks / TODO
* Old immutable Reel files remain on disk until a separate retention cleanup is implemented; they are no longer referenced by the current preview.

## 2026-08-13 — Finish adaptive Reel type, object separation, and real close-ups

### Summary
* Re-rendered the real seven-scene SoloCruz Reel from existing approved image checkpoints only.
* Replaced long 7-22-word overlays with 5-7-word headlines that preserve the countdown and SoloCruz resolution.
* Removed in-scene text pagination, added six-zone subject-aware placement and adaptive color-sampled gradient scrims.
* Added a light silhouette outline and soft offset shadow to every registered layer while reducing destructive legacy matte erosion.
* Upgraded camera execution from gentle crops to wide, medium, and genuine person/object close-ups with lateral transfers and pull-outs.

### Files changed
* `app.py` — universal overlay-length, reading-time, safe-placement, gradient-scrim, and cinematic camera prompt/validation contract.
* `reel_renderer.py` — six-zone type placement, 88-132 px single-title rendering, cached adaptive scrims, object outlines/shadows, preserved silhouette details, and 2.2-2.34x close framing.
* `docs/PROJECT_MEMORY.md` — durable Reel typography, edge treatment, placement, and film-scale camera rules.
* `docs/CHANGELOG_AI.md` — recorded this correction and verification.

### Decisions
* Small matte irregularities are hidden with a restrained outline and shadow; hands, feet, clothing, hair, and owned objects are never sacrificed by aggressive erosion.
* On-screen copy is intentionally shorter than article/narration prose and is always displayed as one readable title.
* Strong close-ups remain clear of overlay text whenever the scene duration permits.

### Checks run
* `python3 -m py_compile app.py reel_renderer.py` passed locally and on the VPS.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; `/health` returned `ok`.
* Re-rendered post 33 as a 30.041667-second, 1080x1920, 24 fps H.264 draft without image generation or voice.
* Extracted and visually inspected 15 full-resolution frames across all seven scenes, covering entrances, full titles, clean text exits, wide shots, medium relationships, and close-ups.
* Confirmed social post 33 returned to `DRAFT`; it was not published.

### Risks / TODO
* Existing source masters still determine pose and photographic quality. The renderer now preserves and separates their silhouettes but does not regenerate or redesign accepted photography during render-only correction.

# CHANGELOG_AI.md

## 2026-09-08 — Diagnosed the malformed final LinkedIn cover

* Confirmed that YAS LinkedIn post `209`, `Startup Portal vs No-Code Stack: Architecture and Workflow Decisions`, did not invoke the current dedicated LinkedIn hero prompt.
* The draft was created on 2 September before that draft carried a `linkedin.mediaUrl` and short `coverHeadline`; its saved payload contains neither field.
* At publication on 8 September, the publisher's fallback selected the 1376×768 article hero. The LinkedIn uploader then applied its normal 1065×795 centered crop, cutting both sides of the full-width article title and preserving the article hero's plain white typography instead of the magazine-cover treatment.
* Verified there are currently no remaining YAS LinkedIn drafts in `DRAFT` or `QUEUED` state with the same latent condition. No post, image, prompt or queue state was changed during this diagnosis.

## 2026-09-08 — Published the canonical NOMADeira EU registration guide

### Summary

* Consolidated the blocked legacy editorial-plan task with the unpublished Phase-A CRUE research and retained `/madeira-residence-registration-eu/` as the sole canonical route.
* Rechecked the current AIMA and gov.pt pages, recorded three bounded verified claims and generated a fresh 1,096-word English guide with DE, UK and RU localizations.
* Replaced three body images after visual QA found generated document and signage text. The reviewed replacements contain no readable text, and their alt text and captions were synchronized across all four locales.
* Removed duplicate contextual links from the NOMADeira native payload, completed editorial, source, SEO, localization, visual and responsive browser QA, then published immediately at the owner request.
* Canceled the unpublished overlapping Phase-A CRUE job only after the canonical route published successfully.
* Rebuilt and restarted NOMADeira so the English, German, Ukrainian and Russian URLs entered the static sitemap.

### Files changed

* `deploy/prepare_nomadeira_crue_canonical.py` — fail-closed canonical consolidation, current source map, verified claims and generation brief.
* `deploy/regenerate_nomadeira_crue_body_images.py` — targeted replacement of the three rejected body images without regenerating the article or hero.
* `deploy/finalize_nomadeira_crue_publication.py` — multilingual media-copy synchronization, approval contract, duplicate-link payload correction and safe overlap supersession.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/CHANGELOG_AI.md` — durable canonical, evidence, renderer and sitemap operations.

### Checks run

* Both official sources returned HTTP 200 during the live source audit.
* Generation validation passed with 1,096 words, seven approved sections, six FAQs, three body images, four contextual internal links and two Recommended next destinations.
* Visually reviewed the hero and all three replacement body images; all are 1376×768 WebP files and contain no readable generated text.
* Desktop and 390×844 mobile previews passed with no horizontal page overflow; duplicated contextual links were removed.
* EN, DE, UK and RU public routes, all four media URLs, Blog Core health and the NOMADeira service returned successfully.
* The rebuilt sitemap contains all four localized canonical URLs.

### Recovery

* Production database snapshots: `backups/blog_core-pre-crue-publish-20260908-093238.sqlite3` and `backups/blog_core-pre-crue-release-20260908-095409.sqlite3`.

## 2026-08-14 — Rebuilt Reel direction around visual and framing variety

### Summary

* Rejected the technically valid but repetitive cabin-only director plan.
* Added sequence-level world and shot-scale planning, contextual stages, compact-object constraints, complete-human extraction checks, object ownership rules, and readable-label validation.
* Removed the requirement to manufacture three physical layers per scene. Scenes now use one to four meaningful layers, with text and camera supplying additional visible events.
* Generated and validated a replacement five-scene, 30-second plan using four visual worlds and wide, medium, and detail compositions. No images, voice, music, or video were generated.

### Files changed

* `app.py` — universal scene variety, framing, layer feasibility, grounding, and validation contracts.
* `docs/PROJECT_MEMORY.md` — durable Reel visual-variety and layer rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Large furniture and architecture create the fixed set and are never moved as extracted layers.
* A truthful sparse scene is preferable to a busy scene filled with unrelated props.
* Contextual backgrounds may provide production variety but cannot prove an editorial claim.

### Checks run

* `python3 -m py_compile app.py` passed locally and on the VPS.
* Restarted `blog-yas-core`; health returned `ok`.
* Stage two passed with five scenes, four visual worlds, and three shot-scale classes.
* Stage three passed for all five scenes at 30.0 seconds.
* Saved the replacement `director_plan_ready` checkpoint with `mediaGenerated: false`.

### Risks / TODO

* The new plan remains text-only and requires explicit approval before paid media generation.

## 2026-08-14 — Completed Reel scene concepts and technical direction

### Summary

* Ran stage two and stage three against a real published SoloCruz article using the production Gemini model and production validators.
* Fixed cross-stage loss of the central physical problem, unsupported environment selection, non-extractable human compositions, generic CTA substitution, and punctuation-sensitive final camera focus matching.
* Produced and saved an accepted five-scene, 30-second text-only director checkpoint for social post 33. No images, speech, music, or video were generated.

### Files changed

* `app.py` — universal stage-two evidence/environment contract, extraction validation, social-payoff validation, and stage-three camera identity validation.
* `docs/PROJECT_MEMORY.md` — durable cross-stage Reel planning rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* Environment phrases are closed-book copies from the current beat, not free-form descriptions from `domainContext` or the wider article.
* A model-valid camera plan must cover every direct-evidence layer by exact technical identity; punctuation differences cannot create false validation failures.
* Accepted text stages remain operator-gated. Media production starts only after explicit approval.

### Checks run

* `python3 -m py_compile app.py` passed after deployment.
* Restarted `blog-yas-core`; local health endpoint returned `ok`.
* Stage two passed for all five scenes.
* Stage three passed for all five scenes with a total duration of 30.0 seconds.
* Saved `director_plan_ready` with `mediaGenerated: false` in SoloCruz social post 33.

### Risks / TODO

* No visual assets were generated in this task, so the accepted text plan still requires explicit review before starting paid media production.

## 2026-08-13 — Clean Reel cutouts, persistent scene text, and verified final logo

### Summary

* Reworked registered-layer edge recovery so missing anatomy/object edges are restored only along a narrow clean-plate difference boundary instead of admitting surrounding floor or wall pixels.
* Made every overlay remain visible from scene start through the exact scene cut. Removed text strokes and retained a soft shadow, with a feathered color-sampled gradient only when local contrast requires it.
* Enabled the real connected-site logo reference for the final brand-resolution scene, added source SVG rasterization, and made the final camera pull back to reveal the logo in context.
* Rebuilt SoloCruz Reel post 33 without voice. Six existing scenes were reused; only the final master/clean pair was regenerated. The final output is a 30.04-second 1080x1920 H.264 draft.

### Files changed

* `app.py` — extraction-safe prompt, clean-plate spatial removal instructions, final-scene logo reference, high-resolution SVG logo conversion.
* `registered_scene.py` — narrow semantic-plus-difference mask repair and softer anatomy-preserving alpha edge.
* `reel_renderer.py` — persistent text, no stroke, conditional gradient scrim, soft text shadow, final brand-context camera reveal.
* `docs/PROJECT_MEMORY.md` — durable Reel mask/text/logo contracts.
* `docs/INTEGRATIONS.md` — Gemini logo-reference contract.
* `docs/CHANGELOG_AI.md` — task record.

### Decisions

* Do not hide poor masks with a white outline. Correct the extraction matte from semantic and clean-plate evidence.
* Final brand usage is produced by Gemini from a verified reference and remains part of the photographed scene, not a renderer overlay.

### Checks run

* `python3 -m py_compile app.py reel_renderer.py registered_scene.py` passed locally and on the VPS.
* Blog Core `/health` returned `ok`; `blog-yas-core` and `blog-yas-core-scheduler` are online.
* Gemini layer-pack review approved the rebuilt final scene: complete silhouettes, no missing anatomy, no holes, and no foreign pixels.
* Frame QA at all seven scene boundaries confirmed text remains present through each cut.
* Final-frame QA confirmed the real SoloCruz mark, final text, complete person, and both story objects remain visible together.
* `ffprobe` confirmed 1080x1920 H.264, 30.041667 seconds; voice generation remained disabled.

### Risks / TODO

* Some prior scene photography is reused from the approved master set; future generations benefit from the stronger extraction-safe source prompt, but old master composition is intentionally not regenerated in this task.

## 2026-08-13 — Improve Reel readability, matte quality, and cinematic camera work

### Summary
* Rebuilt the existing seven-scene SoloCruz Reel from its accepted visual checkpoints without generating new images or speech.
* Increased overlay typography and split long copy into sequential mobile-readable phrase groups.
* Added target-aware close-ups, focus transfers, direction changes, pull-outs, and varied scene-local camera sequences.
* Added soft inner mattes and foreground-edge decontamination for new registered layers, plus safe cleanup for legacy binary checkpoint layers.

### Files changed
* `app.py` — strengthened universal director and typography instructions for future Reels.
* `reel_renderer.py` — large paged captions, typed camera targets, cinematic camera beats, and legacy edge cleanup.
* `registered_scene.py` — decontaminated soft inner mattes for newly extracted registered layers.
* `requirements.txt` — added SciPy for nearest-interior edge-color recovery.
* `docs/PROJECT_MEMORY.md` — recorded the durable Reel typography, camera, matte, and checkpoint-reuse contracts.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Preserve complete silhouettes even when a more aggressive erosion would remove the last bright edge; cutting anatomy or owned objects is not an acceptable cleanup method.
* Camera movement acts on the complete assembled photograph only after registered entrances settle.
* Render refinements must reuse accepted scenes and must not incur new image or voice generation.

### Checks run
* Compiled `app.py`, `reel_renderer.py`, and `registered_scene.py` in the VPS virtual environment.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; `/health` returned `ok`.
* Re-rendered and visually inspected full-resolution frames across all seven real SoloCruz scenes, including wide frames, person close-ups, object close-ups, focus transfers, and pull-outs.
* Verified a 30.041667-second 1080x1920 H.264/AAC result at 24 fps with continuous music and no generated voice.

### Risks / TODO
* Some bright rim lighting belongs to the generated master photograph itself. Removing it more aggressively from old checkpoint masks damages real silhouette detail; future scenes use the clean-edge matte contract at extraction time.
* The Reel remains a draft for operator review and was not published.

## 2026-08-12 — Produce the first checkpointed SoloCruz Reel without voice

### Summary
* Connected the accepted seven-scene director plan directly to real media production instead of redesigning it in a second storyboard pass.
* Generated and validated coherent vertical masters, matching clean plates, and registered foreground layers for all seven scenes.
* Added per-scene visual checkpoints so accepted assets survive interruption and are reused on resume.
* Added an explicit no-voice production path while retaining the site's continuous background soundtrack.
* Tightened universal master composition, clean-plate removal, layer segmentation, camera timing, and optional support-object handling.

### Files changed
* `app.py` — production entry point, accepted-plan adapter, visual checkpoints, universal image prompts/reviews, no-voice mode, and production UI action.
* `registered_scene.py` — authoritative semantic masks, narrow clean-plate boundary repair, role-aware geometry checks, and layer overlap handling.
* `reel_renderer.py` — approved whole-layer entrances, post-entrance camera beats, caption timing, and music-only rendering.
* `docs/PROJECT_MEMORY.md` — recorded the durable checkpoint, visual, and no-voice production contracts.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* An accepted director plan is executed, not rewritten during media production.
* Accepted visual scenes are never regenerated merely because a later scene or final render is interrupted.
* No speech API call or voice file is allowed when production is started without voice.

### Checks run
* Python compilation for `app.py`, `registered_scene.py`, and `reel_renderer.py` locally and on the VPS.
* Real SoloCruz production created seven accepted visual scene checkpoints with three or four registered layers per scene.
* Confirmed production state records voice disabled and music-only audio mode.
* Rendered and visually reviewed the complete 30.04-second 1080x1920 H.264 Reel; confirmed all seven scenes, complete final copy, continuous AAC music, and zero voice files.
* Verified the private preview and public MP4 asset both return HTTP 200, and the Blog Core health endpoint is healthy.

### Risks / TODO
* The Reel remains a draft for operator review; it has not been published to Instagram.

## 2026-08-12 — Use plain language in operator-facing output

### Summary
* Recorded that project plans, scenarios, previews, and status explanations must use normal language rather than JSON or internal schema terminology.

### Files changed
* `docs/PROJECT_MEMORY.md` — added the durable communication preference.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Technical payloads are shown only when explicitly requested.

### Checks run
* Reviewed the memory entry for clarity and absence of secrets.

### Risks / TODO
* None.

## 2026-08-12 — Restrict Reel motion to executable rigid layers

### Summary
* Removed impossible internal object animation from Reel scene planning and direction.
* Made stage two choose an immutable rigid transform for every complete person or object layer.
* Added structured checks for unchanged appearance, full final visibility, and an unobstructed entrance path.
* Made stage three copy the approved transform instead of inventing a new reveal method.
* Rebuilt the SoloCruz text-only plan as seven scenes with moving people and complete objects; no media was generated.

### Files changed
* `app.py` — updated Reel schemas, stage-two and stage-three prompts, validators, checkpoint versioning, and deterministic immutable-field hydration.
* `docs/PROJECT_MEMORY.md` — recorded the rigid full-canvas layer contract and deprecated state-changing still-image motion.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Whole-layer translation and uniform scale are the only supported layer transforms in the current renderer.
* A bad object choice is corrected in stage two; later stages must not reinterpret an impossible layer action.
* Immutable source anchors and neutral kinetic-support purposes are hydrated by code rather than consuming another model call.

### Checks run
* Python compilation, VPS deployment, PM2 restarts for both app and scheduler, and `/health` check.
* Generated a version-16 SoloCruz plan with 7 scenes, 25 layers, 25 distinct physical events, 14 object layers, and a 30.0-second duration.
* Verified every event uses its stage-two `transformMode`; only `settle`, `slide_left`, `slide_right`, and `rise` are present.
* Verified every layer has unchanged appearance, full visibility, and an unobstructed path; no hinge, swing, fold, billow, `roll_in`, or `arc_in` behavior remains.
* Verified the planning preview returns HTTP 200 and `mediaGenerated` is false.

### Risks / TODO
* The text-only director plan still requires operator approval before any image, voice, music, or video production.

## 2026-08-12 — Require real object layers and three physical Reel events

### Summary
* Rebuilt stage two so every scene plans three or four registered layers, including a moving story object.
* Separated source-grounded direct evidence from honest kinetic support and blocked symbolic object substitutions.
* Rebuilt stage three so focus, camera, text, and static relationships cannot satisfy the three-event requirement.
* Added deterministic hydration of immutable stage-two fields instead of asking Gemini to copy them exactly.
* Generated and installed a new seven-scene, 29.4-second SoloCruz text-only director plan with three independent physical layer events per scene.
* Exposed registered layer type and role in the Reel review page.

### Files changed
* `app.py` — updated schemas, prompts, validators, checkpoint compatibility, director hydration, and planning UI.
* `docs/PROJECT_MEMORY.md` — recorded the durable object-layer and physical-event contract.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* An abstract article concept is never converted into a symbolic prop. Objects either have literal source grounding or operate only as kinetic support.
* Minimum events describe real independent layer motion, not optical attention changes.

### Checks run
* Python compilation, VPS deployment, PM2 restart, and health check.
* Step two generated seven scenes with three registered layers each and at least one story object per scene.
* Step three resumed from per-scene checkpoints and produced seven scenes totaling 29.4 seconds; every scene has three distinct layer events and two camera beats.
* Verified that kinetic-support events name the direct-evidence layer they physically assist and every final camera beat lands on direct evidence.
* Confirmed `mediaGenerated: false`; no image, voice, music, or video generation ran.

### Risks / TODO
* The new director plan remains text-only and must be reviewed before media production.

## 2026-08-12 — Rebuild Reel step-three prompt from approved scene evidence

### Summary
* Left the accepted step-two scene concepts unchanged.
* Replaced vague motion prose with an executable scene contract: registered entrances, material evidence, spatial relationships, kinetic copy, and sequential camera beats.
* Anchored every visual action to exact step-two evidence and rejected incidental scenery, decorative lighting, cropped people, invented coordinates, and repeated pseudo-subjects.
* Added resumable `directorScenes` and complete `directorPlan` checkpoints to the real Reel planning pipeline.
* Refined text contrast after review: aesthetic color-sampled feathered gradients are allowed; opaque black rectangles and hard-edged black plaques remain forbidden.
* Added explicit panel controls to advance only the next text-planning stage and a readable step-one, step-two, or step-three preview.
* Installed the accepted seven-scene SoloCruz director plan into the operational panel record without generating media.
* Added a Distribution-level Reel planning list so accepted plans and next-stage actions are visible independently of the article inventory page.

### Files changed
* `app.py` — rebuilt the step-three schema, prompt, validator, per-scene resume, and pipeline checkpoint integration.
* `docs/PROJECT_MEMORY.md` — recorded the durable step-three production contract.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Step three directs only the approved step-two composition and never redesigns it.
* Images, voice, music, and video remain blocked until the complete director plan is validated.

### Checks run
* Python compilation and Git whitespace checks.
* VPS deployment, PM2 restart, and `GET /health`.
* Real text-only SoloCruz run from the existing seven accepted step-two scenes: 7 scenes, 29.3 seconds, no media generated; all structural assertions passed.
* Checkpoint-resume smoke test reused the complete accepted `directorPlan` with 7 scenes and generated no images, voice, music, or video.
* The stage-advance API rejected a repeated step-three request with HTTP 400 instead of regenerating the accepted plan.
* Browser verification confirmed the Distribution planning list, direct plan navigation, all seven readable scene cards, physical events, camera beats, text direction, and the explicit no-media state.

### Risks / TODO
* The plan is ready for human review before any asset-generation stage begins.

## 2026-08-11 — Make Reel step three an executable director plan

### Summary
* Kept approved step-two scene concepts unchanged.
* Added time-coded director actions, camera plans, exact text direction, and extraction constraints to every step-three scene.
* Required at least three visible actions per scene, two tied to approved foreground groups, and a dynamic camera move after the entrances settle.
* Strengthened the contract after review: each scene now has six timed events minimum, three identifiable visual actions, text, and two camera beats; generic lighting or atmosphere changes cannot satisfy the action requirement.
* Replaced the vague event-list prompt with a positive technical motion score: three physical `visualBeats`, registered-layer or fixed-detail reveal mechanics, and two fully specified camera beats per scene.
* Anchored every physical beat to exact approved step-two evidence and separated registered entrances, material evidence, and spatial relationships so decorative scenery cannot satisfy the story-action requirement.
* Rejected cropped registered people and decorative lighting/vignette reveals at the step-three validation boundary.
* Defined role-specific subjects for one-group resolution scenes so the group entrance, internal evidence, and group-to-setting relationship remain distinct executable events.
* Fixed director-plan resume so a single regenerated scene is duration-validated locally and the 27-33 second total is enforced only after merging the complete plan.
* Connected the director pass directly to the approved step-two scene concepts rather than the obsolete parallel skeleton.

### Files changed
* `app.py` — added the step-three schema, prompt contract, normalization, and validation.
* `docs/PROJECT_MEMORY.md` — recorded the durable production boundary.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Step three is a separate reviewable director checkpoint; it does not generate media or alter editorial/scene concepts.

### Checks run
* Python compilation and diff whitespace validation.
* Deployed to the Blog Core VPS; `python3 -m py_compile app.py` and `GET /health` passed.
* Ran the new text-only director pass from the existing seven approved step-two SoloCruz concepts: seven scenes, 29.0 seconds, `mediaGenerated: false`.

### Risks / TODO
* The director plan is ready for operator review; image, voice, music, and video generation remain blocked until that review is approved.

## 2026-08-11 - Reject non-layerable Reel concepts at architecture stage

### Summary
* Moved complete free-standing group requirements into the first Reel planning pass.
* Added architecture validation for seated/furniture-supported people, small-prop-led concepts, and extraction language.
* Removed prompt contradictions that requested crops and separately generated foreground layers.
* Stopped automatic six-attempt regeneration after text-stage validation failures.
* Moved technical `element-NN` assignment out of Gemini and into deterministic application code.
* Prohibited background crowds and fixed/readable/handheld visual premises at architecture time, and persisted rejected raw skeleton candidates for diagnosis.
* Fixed the false positive that treated editorial social isolation as an isolated-asset instruction.
* Accepted exact single-term source quotations in layer evidence validation.
* Persisted rejected raw scene-detail and manifest candidates as durable diagnostics.
* Strengthened and validated the no-raw-URL Instagram Reel caption contract.

### Files changed
* `app.py` - made visual-world selection physically compatible with later layered animation.
* `docs/PROJECT_MEMORY.md` - recorded ownership of layerability constraints.
* `docs/CHANGELOG_AI.md` - recorded this correction.

### Decisions
* Invalid physical composition is rebuilt at architecture stage rather than repaired downstream.
* A rejected text stage makes no hidden repeat requests; the prompt must be corrected before resuming.

### Checks run
* Python compilation and `git diff --check`.
* Live VPS run completed architecture, skeleton, seven scene-detail checkpoints, seven manifest checkpoints, and final storyboard in 142 seconds.
* Final production validator confirmed 7 scenes, 10 unique registered groups, 7 stages, exact 30.0-second duration, valid reveal/timing/hold fields, source-grounded evidence, and no raw URL in the caption.
* Confirmed that no image, voice, music, or video generation ran during this task.

### Risks / TODO
* Media generation remains intentionally unstarted until the operator approves this text-only scenario and frame plan.

## 2026-08-11 — Make Reel planning checkpointed and resumable

### Summary
* Split Reel planning persistence into validated architecture, skeleton, per-scene detail, per-scene manifest, and complete-storyboard checkpoints.
* Added resume behavior from the first unfinished scene and preserved version-13 checkpoints during regeneration.
* Moved checkpoint writes outside Gemini retry blocks so a storage error cannot trigger a duplicate model call.
* Stopped the obsolete monolithic text-only process before further requests were spent.
* Moved movable-layer geometry validation into the skeleton boundary and added selective invalidation that preserves a valid architecture checkpoint.

### Files changed
* `app.py` — added checkpoint callbacks, sequential scene persistence, resume inputs, version-13 payloads, and regeneration preservation.
* `docs/PROJECT_MEMORY.md` — recorded the durable checkpoint and retry boundaries.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Every validated text stage is durable before the next stage starts.
* Retrying the current Gemini step and retrying checkpoint storage are separate concerns.

### Checks run
* Python compilation and AST parsing.
* VPS mock test confirmed a saved manifest scene is reused while only unfinished scenes invoke the model.
* VPS mock orchestration test resumed from one saved detailed scene and emitted sequential detail/manifest/storyboard checkpoints.
* Real text-only run persisted architecture, skeleton, and scene 1 independently; its scene-2 failure exposed an invalid old skeleton without losing the architecture checkpoint.
* The resumed run retained its architecture, rebuilt the invalid skeleton, and saved seven scene details independently. A stricter final camera-detail check then exposed validator drift; the per-scene gate was aligned with the final production validator and resume now truncates only from the first invalid scene.
* Root-cause inspection showed scene 5 had a 15-word immutable `visualStory`; moved immutable story/stage checks to the skeleton gate and made production-detail errors report exact field counts.
* The completed checkpoint test produced seven durable text scenes and manifests in 267 seconds with no media. Manual audit rejected the creative result for an invented recurring character, device-led scenes, and deprecated isolated/transparent layer wording; added automatic skeleton and pre-image gates for those violations.
* Corrected the over-broad character rule: internal recurring names are allowed for visual continuity. The prompt and source gate now reject unsourced knowledge/decision chronology rather than the name itself.
* A real rerun exposed `realize` as immutable skeleton causality that was only checked during detail; moved source-grounding into both new and resumed skeleton validation.
* The next skeleton run remained correctly isolated to that stage but exhausted attempts on fixed-contact geometry and unnamed device shortcuts. Strengthened the universal analog-action brief and made validator errors report the exact shortcut token.
* Inspection showed the preserved architecture itself mandated smartphone scenes. Added photographable analog-world requirements and architecture-level shortcut validation, plus selective invalidation of incompatible stored architecture and all dependents.

### Risks / TODO
* Existing pre-version-13 partial planning payloads cannot be resumed and must start under the new contract.

## 2026-08-11 — Enforce executable Reel layer geometry

### Summary
* Removed renderer-side index cycling that could make a seated or cropped person slide into frame as a partial torso.
* Made approved reveal mode, hold state, and entrance timing authoritative for full-canvas registered layers.
* Updated the universal planner and validators so seated, reclining, occluded, cropped, furniture-supported, and fixed-contact people cannot become movable foreground layers.
* Added a fail-fast media gate so old or incomplete storyboards stop before any image call.

### Files changed
* `app.py` — aligned step-two planning, step-three manifests, geometry validation, and the pre-image gate.
* `reel_renderer.py` — executes approved manifest reveal/timing instead of inventing animation by layer index.
* `docs/PROJECT_MEMORY.md` — recorded the durable geometry/motion contract and deprecated the moving-seat rule.
* `docs/CHANGELOG_AI.md` — recorded this task.

### Decisions
* Only complete unobstructed free-standing groups may translate. Fixed-contact people are background or must be recomposed before production.
* Registered layers hold after their entrance; camera motion begins after the entrance window.

### Checks run
* Python compilation and AST parsing for `app.py`, `reel_renderer.py`, and `registered_scene.py`.
* Synthetic registered-layer checks for approved slide timing, missing-manifest rejection, and unsupported post-entrance motion rejection.

### Risks / TODO
* Detailed camera prose is still compiled through the renderer's existing camera presets rather than interpreted word-for-word.

## 2026-08-11 — Compare planned Reel motion with renderer behavior

### Summary
* Extracted every generated background/component prompt, placement, reveal, motion, camera instruction, and overlay-text position from the SoloCruz text-only storyboard.
* Traced the same fields through `reel_renderer.py` and found that full-canvas rendering ignores manifest reveal/motion/timing in favor of an index-based animation cycle.

### Files changed
* `docs/PROJECT_MEMORY.md` — recorded the planning/rendering contract mismatch as a production blocker.

### Decisions
* Do not generate media from this storyboard until reviewed motion instructions and actual renderer behavior are the same contract.

### Checks run
* Compared all seven storyboard scenes and eight components with `_full_canvas_layer_frame` and `_subject_camera_values`.

### Risks / TODO
* Wire approved per-layer reveal, motion, and timing into the full-canvas renderer, and define how detailed camera start/end instructions compile into deterministic motion.

## 2026-08-11 — Align Reel planning with master-derived contact groups

### Summary
* Ran the text-only Reel planner on a published SoloCruz article without invoking image, voice, music, or rendering functions.
* Found that an obsolete independent-foreground validator rejected ordinary walking and any character interaction with seating/furniture across all six text attempts.
* Replaced the obsolete prohibition with the production rule that complete touching people and movable contact/owned items form one extraction-safe master-derived group while fixed architecture remains separate background.

### Files changed
* `app.py` — aligned the universal scene prompt and validators with master-derived extraction.
* `docs/PROJECT_MEMORY.md` — recorded the durable contact-group rule and deprecated validator.

### Decisions
* Scene planning must describe a valid master composition on the first prompt instead of forcing free-standing cutout restrictions inherited from the deprecated foreground generator.

### Checks run
* Confirmed the failed run stopped during text-only planning and generated no image, audio, music, or video file.
* Repeated the text-only run after deployment. It completed seven scenes in 517 seconds and created zero media files.
* Reviewed the resulting architecture, scene directions, backgrounds, layer actions, copy, camera instructions, and technical manifest.

### Risks / TODO
* The completed plan is blocked from media generation: it invents a fictional recurring protagonist, uses screen/device-dependent imagery, leaves most layer motion static, and its step-three manifest still describes deprecated separately generated transparent foregrounds. Align all text stages with the master-derived contract before another production run.

## 2026-08-11 — Audit the production Reel image contract

### Summary
* Re-read the active production path from storyboard planning through master image, clean plate, registered extraction, layer review, delayed voice, and render.
* Confirmed the master prompt carries the complete first-call composition contract and the active image stage has no automatic paid retry or legacy foreground-generation fallback.
* Confirmed non-compliant masters and layer packs stop before voice generation and publication.

### Files changed
* `docs/CHANGELOG_AI.md` — recorded the production prompt and execution-path audit.

### Decisions
* Prompt completeness reduces invalid generations; validators provide the publication guarantee. A generative model cannot guarantee that every first candidate is compliant.

### Checks run
* Inspected `build_instagram_reel_master_prompt`, master review normalization, clean-plate prompt, registered extraction, layer-pack review, and `generate_instagram_reel_post`.
* Confirmed the active master loop is exactly one attempt and voice starts only after all visual scenes pass.

### Risks / TODO
* The next operator-requested real Reel remains the first full production verification of the new one-pass image contract.

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

## 2026-07-26 — Restore all three Pricing tiers with safe checkout gating

### Summary

- Restored the visible Solo (€49), Pro (€99), and Agency (€199) plan cards on the Georivo Pricing page.
- Kept Solo connected to the real checkout while routing Pro and Agency to an honest localized request action until their Stripe recurring Prices are configured.
- Added an environment-controlled purchase gate so a tier cannot expose a broken or simulated checkout.

### Files changed

- `deploy/georivo/app.py` — three-plan rendering, localized request labels, and `GEORIVO_PURCHASABLE_PLANS` checkout gate.
- `deploy/georivo/georivo-blog.css` — distinct request-action styling and stylesheet revision.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable catalogue and deployment rules.

### Decisions

- Pricing always shows the complete three-tier catalogue.
- Only tiers backed by configured Stripe Prices may use checkout; unavailable tiers remain visible and lead to contact.

### Checks run

- `python3 -m py_compile deploy/georivo/app.py`
- `git diff --check`

### Risks / TODO

- Pro and Agency remain request-only until Stripe access is reauthorized and their recurring Price IDs are configured.

## 2026-07-26 — Connect every Georivo answer to the relevant product workflow

### Summary

- Audited the complete public Georivo sitemap and replaced the renderer's universal article CTA logic with six intent-specific product actions.
- Added localized in-article application panels for Property Showcase, Neighborhood Story, Arrival Guide, real coverage checking, protected embed publishing, and example setups.
- Kept the long-form answer intact while giving readers a concrete next step in the real Georivo product.
- Extended the public audit so a page cannot pass with only a generic CTA or one repeated action across the content tree.
- Restored the fail-closed indexation gate for unverified Webflow, Wix, and Squarespace instructions and for the Embed hub.

### Files changed

- `deploy/georivo/app.py` — contextual intent classifier, five-language product copy, exact builder/coverage/pricing destinations, and article/guide integration.
- `deploy/georivo/app.py` — also limits integration-guide sitemap/indexation to real-editor-verified platform slugs.
- `deploy/georivo/georivo-blog.css` — responsive product-step panel.
- `deploy/georivo/audit_content_plan.py` — public product-bridge and action-classification checks.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable SEO and release rules.

### Decisions

- Useful content remains a complete answer; the product bridge demonstrates how to apply that answer in Georivo.
- The renderer uses reader intent, not one universal sales message, and future content inherits the same contract.

### Checks run

- `python3 -m py_compile deploy/georivo/app.py deploy/georivo/audit_content_plan.py`
- `git diff --check`

### Risks / TODO

- Public sitemap and browser checks must run after the VPS renderer restart; production HTML cannot pass the new action audit before deployment.

## 2026-07-26 — Expand Georivo Pricing to three large subscription tiers

### Summary

- Replaced the single compact Solo offer with three equally prominent plans: Solo €49, Pro €99, and Agency €199.
- Restored large price, benefit, and CTA typography without reintroducing the removed duplicate hero action.
- Routed every plan card to the account-aware dashboard with its explicit plan key.

### Files changed

- `deploy/georivo/app.py` — renders three real plan choices and carries `solo`, `pro`, or `agency` into checkout continuation.
- `deploy/georivo/georivo-blog.css` — large three-column desktop offer grid and readable stacked responsive layout.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable Pricing hierarchy and rollout constraint.

### Decisions

- Pricing must expose at least three purchase tiers, not repeat a single package throughout the site.
- The plan grid has one CTA per tier and no competing hero CTA.
- A plan card may be published only when the product app recognizes the same plan key and Stripe has a configured recurring Price for it.

### Checks run

- `python3 -m py_compile deploy/georivo/app.py`
- `git diff --check`

### Risks / TODO

- Production publication is blocked until Stripe authorization is restored and real recurring Prices for Pro and Agency are configured.

## 2026-07-26 — Simplify the Georivo Pricing offer card

### Summary

- Removed the hero price/button that was visually covered by the following plan card.
- Removed the adjacent free-preview column and its competing address-check action.
- Reduced the plan summary to €49/month, three essential benefits, and one subscription button.
- Moved the card into normal document flow with explicit spacing.

### Files changed

- `deploy/georivo/app.py` — single-card Pricing summary and one above-the-fold checkout action.
- `deploy/georivo/georivo-blog.css` — compact plan typography, positive spacing, and responsive card layout.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable Pricing hierarchy and release record.

### Decisions

- A Pricing first screen should present one purchase decision, not adjacent free and paid actions.
- Plan details above the long-form SEO content must be scannable and limited to purchase essentials.

### Checks run

- Python compilation and production service health passed.
- Desktop 1440 px and mobile 390 px screenshots were visually reviewed.
- Production HTML contains one plan card, no free-preview plan column, and no hero CTA.
- The plan CTA still reaches `/login?returnTo=/dashboard?startCheckout=1` for a signed-out visitor.

### Risks / TODO

- The long-form Pricing content intentionally remains below the concise offer card for SEO and decision support.

## 2026-07-26 — Localize CTAs and restore the real Pricing conversion path

### Summary

- Prevented long Guide hero headings from clipping on desktop and from breaking arbitrarily on mobile.
- Localized free-preview and subscription CTAs in all five Georivo languages.
- Replaced the universal address-check CTA pattern with an intent-specific hierarchy: address checking remains a free secondary action, while commercial CTAs lead to Pricing or the real checkout flow.
- Added an above-the-fold Georivo Solo plan summary with €49/month pricing, allowances, benefits, and a working subscribe action.

### Files changed

- `deploy/georivo/app.py` — localized action vocabulary, CTA routing, Pricing plan summary, and stylesheet revision.
- `deploy/georivo/georivo-blog.css` — Guide title containment, Pricing offer layout, and responsive first-paint refinements.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable conversion, SEO, and deployment rules.

### Decisions

- Checking an address and buying a subscription are separate user intents and must not share one universal CTA.
- Pricing checkout must reuse Georivo's existing authenticated Stripe flow; no provider success is simulated.

### Checks run

- Python compilation and production service health passed.
- RU Pricing and Guide pages returned HTTP 200 with localized actions and visible €49 plan data.
- A signed-out subscription click reached `/login?returnTo=/dashboard?startCheckout=1`.
- Desktop and 390 px Guide/Pricing screenshots were visually reviewed.

### Risks / TODO

- Checkout beyond the sign-in boundary depends on the existing user session and Stripe configuration; this release did not create a new payment path.

## 2026-07-26 — Split Georivo Guides from Blog and remove repeated generic image

### Summary

- Replaced the shared Guides/Blog presentation with a practical Guides hub and handbook detail layout while preserving Blog's editorial journal layout.
- Removed the hard-coded `/georivo-hero.png` backgrounds from both the collection hero and final CTA.
- Collection heroes now use the first published record's own image, and that featured record is omitted from the card grid.
- Localized the Guides hub proposition in EN, DE, ES, FR, and RU.

### Files changed

- `deploy/georivo/app.py` — content-type-specific hub/detail markup, localized Guides copy, featured-record handling, and stylesheet cache bump.
- `deploy/georivo/georivo-blog.css` — separate Guides visual system, content-linked Blog hero media, solid final CTA, and responsive layouts.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable rendering, SEO, and deployment rules.

### Decisions

- Guides are practical handbooks; Blog is an editorial journal. They must not share one detail template.
- A universal product hero must not be used as a fallback throughout content pages.

### Checks run

- `python3 -m py_compile` passed locally and on the VPS.
- `georivo-blog.service` restarted and its loopback health endpoint returned OK.
- Public RU Blog hub, Guides hub, and Guide detail returned HTTP 200 with the expected distinct layout classes.
- Production HTML/CSS contained neither `/georivo-hero.png` nor `.journal-cta-image`.
- Desktop and 390px mobile screenshots were visually reviewed.

### Risks / TODO

- Existing article-specific images remain editorial assets supplied by their records; localization variants intentionally share the same asset for the same content identity.

## 2026-07-26 — Reuse the compact localized Georivo chrome

### Summary

- Extended the shared-chrome adapter so header and footer navigation, calls to action, legal labels, and route targets are localized consistently across EN, RU, DE, ES, and FR.
- Kept Blog Core money pages on the single Georivo header/footer and the current compact three-column footer layout supplied by the product stylesheet.

### Files changed

- `deploy/georivo/app.py` — complete shared-chrome localization and localized route rewriting.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable shared-chrome release record.

### Decisions

- Blog Core must adapt the current shared product chrome server-side; it must not recreate a separate money-page footer.
- Footer information architecture is Product, Resources, and Company, with localized labels and destinations.

### Checks run

- Python compilation and `georivo-blog` health passed.
- Production response checks passed for all five languages.

### Risks / TODO

- The live header/footer capture remains dependent on the current Georivo source markup; keep the server-side adapter covered whenever the source chrome changes.

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

## 2026-07-26 — Separate all money-page image libraries

### Summary

- Replaced page-local image uniqueness with a global three-page allocation.
- How it works, Coverage, and Pricing now receive disjoint supporting and recommendation-card images in every language.
- Added intentionally different Coverage and Pricing hero scenes instead of three near-identical office portraits.
- Strengthened the public audit to reject any reused main-content image between two root money pages.

### Files changed

- `deploy/georivo/app.py` — slug-aware global asset partition, unique card imagery, and curated hero overrides.
- `deploy/georivo/audit_money_pages.py` — cross-page main-image collision gate.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable media policy and release record.
- Georivo `public/brand/georivo-money-coverage.webp` and `public/brand/georivo-money-pricing.webp` — project-owned hero assets.

### Checks run

- Python compilation and `git diff --check`.
- Verified the live factory store contains 100 eligible non-money-page assets per language, yielding 34/33/33 disjoint allocations.
- Strict production audit passed all 15 canonical language pages with zero cross-page image collisions.
- Playwright visually confirmed three deliberately different hero scenes at 1440 px; console errors and warnings: zero.

### Risks / TODO

- None specific to this release. The audit will block future publication if the disjoint image contract regresses.

## 2026-07-26 — Enforce unique alternating money-page imagery

### Summary

- Replaced cyclic supporting-image reuse with a unique pool of published Georivo hero assets.
- Excluded current-page hero/editorial media and recommendation-card heroes from supporting-image selection.
- Converted every primary narrative section into a two-column media composition with strict right/left alternation.
- Strengthened the production audit to reject missing media, broken alternation, or duplicate supporting-image URLs.

### Files changed

- `deploy/georivo/app.py` — unique supporting-image pool and full-section media assignment.
- `deploy/georivo/georivo-blog.css` — full-height generated media columns and responsive stacking.
- `deploy/georivo/audit_money_pages.py` — unique-image and alternating-side release gates.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable correction and release record.

### Checks run

- Python compilation and `git diff --check`.
- Strict production audit passed all 15 canonical language pages.
- Playwright confirmed nine distinct primary-section image URLs on How it works and the exact right/left sequence across sections 1–9.
- 390 px remained free of horizontal document overflow; browser console reported zero errors and warnings.

### Risks / TODO

- Future publication must retain enough unique published hero assets; the renderer intentionally refuses to recycle a supporting image when the pool is exhausted.

## 2026-07-26 — Fill money-page whitespace with semantic visuals

### Summary

- Moved the factory TOC into the money-page hero as a responsive navigation layer.
- Filled non-media narrative sections with approved page imagery chosen from the page's own generated asset sequence.
- Replaced blog-like Related/Recommended blocks with localized photo recommendation cards using the linked target pages' published hero images.
- Strengthened the production audit so these commercial-layout requirements cannot silently regress.

### Files changed

- `deploy/georivo/app.py` — hero TOC composition, supporting visual assignment, localized recommendation-card transformation, and target-image resolution.
- `deploy/georivo/georivo-blog.css` — hero navigation, filled section columns, responsive image/card layouts, and mobile horizontal TOC.
- `deploy/georivo/audit_money_pages.py` — verifies hero-contained TOC, supporting visuals, photo cards, and removal of article resource markup.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable product and release record.

### Decisions

- Reuse only approved factory/published assets; do not fabricate external photos at request time.
- Decorative supporting images keep empty alt text while recommendation cards derive meaning from their visible linked title and description.

### Checks run

- Python compilation and `git diff --check`.
- Strict production audit passed all 15 canonical language pages.
- Playwright checks at 1440, 768, and 390 px; all three EN pages remained exactly viewport width at 390 px.
- Browser console reported zero errors and warnings; live renderer health returned `ok: true`.

### Risks / TODO

- Asset reuse is intentionally bounded by the approved image pool; future factory revisions may generate more section-specific imagery without changing the renderer contract.

## 2026-07-25 — Polish Georivo money-page typography and density

### Summary

- Rebalanced the commercial renderer into distinct heading, body, media, and utility regions without changing factory copy.
- Removed artificial vertical whitespace, made imagery fill its paired section, reduced oversized introductory/tablet type, and tightened the TOC, cards, CTA, FAQ, and recommendation rhythm.
- Added explicit responsive behavior for desktop, tablet, and mobile, including safe sticky-header anchor offsets.

### Files changed

- `deploy/georivo/app.py` — groups factory content into presentation regions and separates related/recommended/FAQ utilities.
- `deploy/georivo/georivo-blog.css` — refined commercial typography, grids, media sizing, spacing, utility layout, and responsive breakpoints.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable style and deployment record.

### Decisions

- Preserve the Georivo brand system while applying the UI/UX density, readable-line-length, typography-scale, and responsive-layout guidance.
- Never solve long-form page composition with fixed blank height; media and text must occupy the same visual section.

### Checks run

- Python compilation and `git diff --check`.
- Strict public audit passed all 15 canonical language pages.
- Playwright visual checks at 1440, 768, and 390 px; Coverage and Pricing reported no horizontal overflow at 390 px.
- Browser console reported zero errors and warnings; `georivo-blog.service` health returned `ok: true`.

### Risks / TODO

- Future generated copy lengths vary; keep the renderer content-driven and re-run all three viewport classes after typography changes.

## 2026-07-25 — Redesign Georivo money pages as commercial product pages

### Summary

- Replaced the article-like money-page body with a renderer-owned commercial section system.
- Added a compact sticky TOC, alternating product sections, media/text split layouts, section numbering, a mid-page CTA, and mobile stacking.
- Kept the generated long-form content, the shared Georivo header/footer, the real Coverage checker, and the Stripe Pricing action intact.

### Files changed

- `deploy/georivo/app.py` — splits safe factory HTML into commercial sections without changing ordinary article rendering.
- `deploy/georivo/georivo-blog.css` — dedicated desktop/mobile visual system for money pages.
- `deploy/georivo/audit_money_pages.py` — release gate for commercial structure.
- `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable design and deployment record.

### Checks run

- Python compilation and `git diff --check`.
- Strict public audit: 15/15 canonical language pages passed; legacy aliases and sitemap remained correct.
- Playwright desktop and 390 px mobile visual checks; all three RU mobile pages reported `scrollWidth == innerWidth`.
- `georivo-blog.service` active and loopback health returned `ok: true`.

### Risks / TODO

- Factory copy remains intentionally long for search intent coverage; future content edits must preserve the section contract.

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

## 2026-07-25 — Replace manual Georivo pages with genuine factory output

## Summary

* Requeued How it works, Coverage, and Pricing as real Blog Core `seo_money_page` jobs with approved factual briefs.
* Ran the complete two-pass Gemini generation, image generation, five-language localization, strict validation, draft preview, browser QA, and explicit native publication workflow.
* Replaced the manual native records and removed the deterministic manual seed path.
* Added a guarded root-canonical contract and strengthened the public audit so thin manual substitutes cannot pass again.

## Files changed

* `app.py` — guarded `canonicalRootPage` publication and approved localized category labels.
* `deploy/georivo/app.py` — resolves approved factory `use_case` records at the three root money-page routes while preserving `WebPage` schema and product-page rendering; redirects collection-form aliases to the root canonical.
* `deploy/georivo/audit_money_pages.py` — long-form structure, image, table, FAQ, and duplicate-alias release gates.
* `deploy/georivo/seed_money_pages.py` — removed; manual page authoring is deprecated.
* `docs/PROJECT_MEMORY.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — corrected the durable ownership and release record.

## Decisions

* Blog Core may publish a use-case at `/{slug}` only with explicit `canonicalRootPage=true` and an exact matching target path.
* Editorial metadata may be approved deterministically, but page prose, factual editing, imagery, and localization must come from the factory pipeline.
* Internal labels such as `SEO Money Page` are not public copy.

## Checks run

* Blog Core generated EN drafts with 2,116, 1,821, and 2,106 validated words respectively; every page has 8 sections, 3 inline images, 6 FAQ items, contextual links, a table, ordered steps, and exactly 3 recommended-next links.
* DE/ES/FR/RU localizations generated and validated for all three pages.
* Native publish contracts passed with generated-content evidence and four localized variants.
* Desktop and mobile Playwright preview/live checks passed with shared chrome and zero browser console errors.
* Strict public audit passed all 15 canonical language URLs, 15 collection-alias redirects, and sitemap entries.
* Blog Core and Georivo renderer compilation/health checks passed.

## Risks / TODO

* Coverage continues to expose the existing real provider response; provider access is a separate integration concern and is not simulated by these pages.

## 2026-07-25 — Publish Georivo SEO money pages through live Blog Core

## Summary

* Replaced later on 2026-07-25: this release used a deterministic manual seed and must not be described as factory-generated. See the correction entry above.

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
## 2026-08-13 — Restored smart layer extraction and fixed Reel text colour

### Summary
* Replaced the production quantized-SAM extraction path with SAM 2.1 large plus ViTMatte alpha refinement.
* Removed manual mask growth and nearest-interior edge-colour replacement that caused torn, jagged silhouettes.
* Rebuilt all 22 real layers across the seven scenes of SoloCruz Reel post 33 without regenerating source images or voice.
* Forced Reel typography to remain light with shadow and adaptive background scrim; dark caption switching was removed.
* Added a per-post production lock to prevent scheduler/manual render races.

### Files changed
* `registered_scene.py` — SAM 2.1 + ViTMatte production segmentation and matting.
* `reel_renderer.py` — permanent light caption palette.
* `app.py` — exclusive per-Reel production lock.
* `requirements.txt` — reproducible CPU PyTorch, SAM 2 and ViTMatte dependencies.
* `docs/PROJECT_MEMORY.md` — durable Reel extraction and typography rules.
* `docs/CHANGELOG_AI.md` — task record.

### Checks run
* Python compilation for changed modules.
* Rebuilt seven production scene packs; reconstruction MAE ranged from 0.00000 to 0.00075.
* Visually reviewed a contact sheet of all 22 extracted layers.
* Rendered SoloCruz post 33 without voice and inspected seven timeline frames.
* `ffprobe`: H.264, 1080x1920, 24 fps, 30.04 seconds, AAC music track.

### Risks / TODO
* CPU ViTMatte is intentionally slower than the deprecated quantized SAM path.

## 2026-08-13 — Made the Gemini Reel director source-grounded and causally coherent

### Summary

* Reworked the shared three-stage Instagram Reel planning contract so the hook, every solution beat, and the resolution form one truthful answer to the article's central problem.
* Removed the empty retention-bridge scene; the unresolved promise now stays inside the hook and scene handoffs.
* Required each scene to preserve recognizable source-grounded domain context, protect its text zone through all entrances and camera framings, and keep the resolution in the payoff's visual world.
* Made camera motion continuous and explicitly synchronized to named evidence-layer entrances instead of starting as an unrelated zoom sequence after all motion.
* Replaced duplicated timing ownership with one authoritative visual-beat timeline and passed the full scene count into checkpointed per-scene director calls.
* Added fail-fast source contracts for physical settings and movable layers so an abstract idea cannot be materialized as an invented location, sign, document, confirmation, transaction, or filler prop.

### Files changed

* `app.py` — universal editorial brief, scene-concept, director-plan prompts, schemas, normalization, validation, and checkpoint orchestration.
* `docs/PROJECT_MEMORY.md` — durable universal Reel planning contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Decisions

* The article used for verification is test data only. Production prompts contain no site-, industry-, or object-specific exception.
* Text planning must fail before image, voice, or video generation when Gemini invents unsupported physical evidence or a setting.
* Semantic source grounding is owned by Gemini's explicit evidence inventory plus exact article quotes; brittle word-overlap heuristics must not cause paid retries for otherwise valid plans.

### Checks run

* `python3 -m py_compile app.py` passed locally and on the VPS after each deployed revision.
* Restarted `blog-yas-core`; `http://127.0.0.1:3299/health` returned `ok` after deployment.
* Completed a text-only six-scene, 30-second director plan with protected text zones and camera triggers linked to approved layers; generated no images, voice, or video.
* Verified the stricter scene-concept pass rejects an unsupported new physical setting before media generation.

### Risks / TODO

* Current real-article verification intentionally ends at text planning when Gemini proposes a setting not grounded in the current beat. Media production must remain blocked until a complete strict plan passes.

## 2026-08-13 — Made Reel solutions answer one auditable stake

### Summary

* Replaced vague activity-based Reel advice with an auditable causal contract: provider/counterparty, changed or shared resource, mechanism, and concrete outcome.
* Added one `primaryStakeMetric` per Reel brief. Every accepted solution must directly change that same metric and repeat it in both its causal explanation and outcome.
* Excluded parallel benefits from the ranked answer. Communication, meetings, community, and comfort can support a real mechanism but cannot masquerade as solutions to a financial hook.
* Restored the agreed Gemini key priority so text generation uses the working shared Gemini billing key before the depleted legacy text-only key.

### Files changed

* `app.py` — editorial schema, prompt, validation, and Gemini text-key priority.
* `docs/PROJECT_MEMORY.md` — durable single-stake Reel rule.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py` passed locally and on the VPS.
* Restarted `blog-yas-core`; health returned `ok`.
* Ran text-only step one against a real published article. The accepted result contains only three direct cost mechanisms: waived/reduced supplements, purpose-built solo cabins, and compatible cabin sharing.
* Generated no images, voice, or video.

### Risks / TODO

* This task validates the editorial brief only. Scene and director stages remain gated until this brief is accepted as the intended story.

## 2026-08-13 — Made social retention a cross-stage Reel contract

### Summary

* Made the first Reel step explicitly social-first rather than an article summary: immediate scroll stop, early promise, midpoint escalation, withheld answer, and payoff delivery.
* Passed each beat's social attention role unchanged into scene concepts and technical direction, where it now governs layer order, camera emphasis, persistent copy, and handoffs.
* Added source grounding and claim-strength checks so retention can intensify presentation but cannot invent guarantees, percentages, scarcity, safety, or stronger outcomes.

### Files changed

* `app.py` — social narrative schema, prompts, cross-stage data, normalization, and source/claim validation.
* `docs/PROJECT_MEMORY.md` — durable social-first Reel contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py` passed locally and on the VPS.
* Restarted `blog-yas-core`; health returned `ok`.
* Ran and production-validated a text-only editorial brief from a real published article. No images, voice, or video were generated.

### Risks / TODO

* Existing stored Reel checkpoints predate this contract and must be regenerated from step one before media production.
## 2026-08-14 — Restored three physical events per Reel scene

### Summary

* Found that the active Reel contract had incorrectly redefined three events as one layer entrance plus text plus camera.
* Restored a minimum of three distinct physical layer events per scene; text and camera are now explicitly additional.
* Added situation-mechanism-result event roles, layer necessity proofs, object ownership state, and exact one-event-per-layer validation.
* Blocked the previous one-layer SoloCruz plan and rejected new filler-heavy candidates rather than replacing the saved plan with decorative motion.

### Files changed

* `app.py` — step-two schema/prompt/validation and step-three physical-event enforcement.
* `docs/PROJECT_MEMORY.md` — durable three-physical-event Reel contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py` passed locally and on the VPS.
* Restarted `blog-yas-core`; `/health` returned `ok`.
* Verified the previous saved step two and step three are rejected because each scene contains only one physical layer event.
* Ran text-only planning against the real SoloCruz article; no images, voice, music, or video were generated.

### Risks / TODO

* The saved one-layer plan remains available for comparison but is invalid under the restored contract.
* A candidate with three layers per scene was not accepted because some layers were decorative accessories or violated object ownership. The pipeline now blocks those candidates; a new plan must satisfy both event count and semantic necessity before media production.

## 2026-08-14 — Generated corrected Reel steps two and three

### Summary

* Re-ran Gemini text-only planning for the SoloCruz article after rejecting symbolic physical props that did not prove pricing or savings.
* Produced a corrected five-scene construction with three causal events per scene and a separate six-second motion plan for every scene.
* Used explicit programmatic evidence graphics for abstract pricing, discount, cost-split, and matching facts instead of inventing gifts, keycards, tickets, or other misleading photo props.

### Files changed

* `docs/CHANGELOG_AI.md` — recorded the corrected text-only planning run.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule for honest visual evidence of abstract mechanisms.

### Checks run

* Gemini returned complete JSON for both corrected planning stages.
* Verified every scene has exactly three layer events, continuous camera direction, and persistent scene text.
* No images, voice, music, or video were generated.

### Risks / TODO

* The corrected plans are review artifacts and are not yet approved for media generation.
* Full production support for programmatic evidence layers must be completed before rendering this plan through the standard pipeline.

## 2026-08-14 — Produced the SoloCruz Reel without voice

### Summary

* Added production rendering for honest programmatic evidence graphics so prices, supplements, cost splits, and match results are not represented by invented photographed props.
* Kept evidence graphics in screen space while the camera moves through the photographic scene, and aligned camera phases with each scene's real event start times.
* Strengthened reusable photo-layer prompts and two-person framing so extractable people are large enough for a mobile Reel and do not carry straps, bags, or dangling accessories that damage mattes.
* Produced and visually checked a 30-second SoloCruz Reel with continuous brand music and no generated voice.

### Files changed

* `app.py` — programmatic evidence-layer generation and reusable registered-scene production rules.
* `reel_renderer.py` — event-aligned camera timing and screen-space evidence compositing.
* `docs/PROJECT_MEMORY.md` — durable Reel production and resume rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py reel_renderer.py` passed locally and on the VPS.
* Restarted `blog-yas-core`; `/health` returned `ok`.
* Verified the final MP4 is 1080x1920, H.264 with AAC music, exactly 30 seconds, and publicly returns HTTP 200.
* Inspected a five-frame contact sheet covering the middle of every scene.

### Risks / TODO

* Voice remains intentionally disabled until the visual Reel workflow is accepted.
* The production run used a focused operator script to exercise the generic renderer; scheduled generation should use the same generic app and renderer contracts.

## 2026-08-14 — Added safe evidence-card layout and synchronized Reel voice

### Summary

* Replaced fixed evidence-card text offsets with a measured layout that preserves explicit inner padding around logos, titles, and detail copy.
* Added automatic title/detail font fitting for unusually dense evidence cards without allowing content to cross the card boundary.
* Added one synchronized Gemini TTS narration sequence to the approved SoloCruz Reel while retaining continuous background music.
* Normalized every scene narration to fit inside its six-second scene and prevent adjacent voice segments from overlapping.

### Files changed

* `app.py` — reusable measured evidence-card layout and safe padding.
* `docs/PROJECT_MEMORY.md` — durable evidence-card and voice-timing rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py reel_renderer.py` passed.
* Inspected the regenerated transparent final evidence layer at full resolution.
* Verified all five narration WAV files are 4.78-4.80 seconds for six-second scenes.
* Verified the final 1080x1920 MP4 is exactly 30 seconds, contains one mixed AAC audio stream, and returns HTTP 200 publicly.
* Inspected a five-scene contact sheet and confirmed the final card content remains inside its border.

### Risks / TODO

* The focused production script remains an operator aid; the reusable card layout itself is implemented in the shared application code.

## 2026-08-14 — Restored natural Reel narration and content-driven timing

### Summary

* Removed narration speed normalization. Reel scenes now expand to the actual natural voice duration plus a reading pause; the complete Reel has no fixed maximum duration.
* Made overlay text persist for the complete expanded scene instead of disappearing at the original planned timestamp.
* Centered the complete evidence-card content group horizontally and vertically, including the logo, title, detail, and accent marker.
* Replaced template camera motion with scene-specific paths that focus only on photographic subjects and the source environment, never on screen-space evidence cards.
* Reused the existing backgrounds, people, extracted layers, voice recordings, logo, and music. No image or voice generation was performed for the corrected render.

### Files changed

* `app.py` — fully centered, untruncated evidence-card content layout; removed audio speed normalization.
* `reel_renderer.py` — content-driven scene duration and full-scene text persistence.
* `docs/PROJECT_MEMORY.md` — natural-duration and scene-specific camera rules.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py reel_renderer.py` passed locally and on the VPS.
* Verified the five reused source narration files retain their natural 7.76-11.12 second durations.
* Verified that the render uses the same existing photo and object assets.
* Verified the final MP4 is 52.54 seconds, 1080x1920 H.264 with one mixed AAC stream, and returns HTTP 200.
* Inspected three checkpoints per scene. The persistent text and evidence cards remain clear of faces, while the camera uses a deck reveal, terminal push/pull, corridor close/reveal, two-person focus transfer, and final brand pull-out.

### Risks / TODO

* No remaining blocker was found in the final visual, timing, or audio checks.
## 2026-08-14 — Added reusable Reel visual library

### Summary

* Indexed every SoloCruz Reel image on the VPS, not only the previously downloaded scene-prefixed PNG subset.
* Added non-destructive quality classification, exact and visual duplicate detection, persistent manual overrides, canonical asset symlinks, and a searchable review UI.
* Connected approved site-specific scene and person references to future Gemini master-frame generation without directly pasting registered layers onto unrelated backgrounds.
* Added automatic background catalog refresh after every accepted Reel visual production.

### Files changed

* `app.py` — visual-library integration, future-generation references, automatic refresh, panel link, review routes, asset serving, and manual status controls.
* `reel_asset_library.py` — reusable catalog, quality metrics, deduplication, semantic reference selection, canonical links, and review gallery.
* `rebuild_reel_asset_library.py` — explicit per-site rebuild command.
* `docs/PROJECT_MEMORY.md` — durable scene-bundle and reference-reuse contract.
* `docs/DEPLOYMENT.md` — catalog location, rebuild command, and UI route.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py reel_asset_library.py rebuild_reel_asset_library.py` passed locally and on the VPS.
* Indexed 918 SoloCruz images: 63 approved canonical assets, 404 duplicate renders, 13 rejected layers, 204 manual-review candidates, and 234 non-reusable archive images.
* Tightened automatic admission: scene backgrounds, clean plates, and master frames now require an accepted manifest or a completed production record; technically valid legacy references remain in manual review.
* Verified the library page returns HTTP 200 and a selected approved PNG returns HTTP 200 with the expected image content type.
* Restarted `blog-yas-core`; `/health` returned `ok` and PM2 reports the process online.

### Risks / TODO

* The 204 conservative review candidates are intentionally excluded from automatic use until approved manually.
* Scene and person references guide new generation; cross-scene direct layer compositing remains prohibited because registration, perspective, and lighting belong to the original scene bundle.

## 2026-08-14 — Fixed immediate Reel library status filtering

### Summary

* Fixed manual `Approve`, `Review`, and `Reject` actions leaving cards visible under their previous filter while a full catalog rebuild ran in the background.
* The status, summary counts, and canonical-link removal are now applied atomically before redirecting back to the library; the background rebuild remains responsible for complete reconciliation.

### Files changed

* `app.py` — synchronously updates the visible catalog after a manual status decision.
* `docs/PROJECT_MEMORY.md` — records the immediate-status contract.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* `python3 -m py_compile app.py` passed locally and on the VPS.
* Restarted `blog-yas-core`; `/health` returned `ok`.
* Verified a live asset changes from `review` to `rejected` immediately, remains rejected after the asynchronous rebuild, and returns to `review` when restored.

### Risks / TODO

* None found for the status-filter workflow.

## 2026-08-14 — Audited approved Reel assets across production roles

### Summary

* Visually audited every approved SoloCruz scene, source frame, clean plate, master, and registered layer.
* Extended duplicate detection across file roles while preserving useful production relationships between populated masters, empty scenes, source frames, and extracted transparent objects.
* Rebuilt the live catalog and removed visually equivalent canonical variants from `Approved` without deleting any source files.

### Files changed

* `reel_asset_library.py` — cross-role exact deduplication, role-aware canonical ranking, safer opaque cross-role comparison, and source-reference near-duplicate coverage.
* `docs/PROJECT_MEMORY.md` — durable role-aware duplicate policy.
* `docs/CHANGELOG_AI.md` — this task record.

### Checks run

* Generated and inspected contact sheets for all 81 initially approved assets and the closest visual pairs.
* Rebuilt all 918 SoloCruz assets. The canonical approved pool now contains 78 assets: 32 registered layers, 23 source references, 8 clean plates, 8 master frames, and 7 scene backgrounds.
* Re-ran pairwise validation across all 78 approved assets; zero pairs still satisfy the exact, same-role near-duplicate, or encoding-equivalent cross-role duplicate rules.
* `python3 -m py_compile reel_asset_library.py rebuild_reel_asset_library.py` passed on the VPS.

### Risks / TODO

* Deliberately similar but functionally different production assets remain separate; this includes a populated master beside its clean plate and a source frame beside its extracted transparent layer.
## 2026-08-31 — Restored SoloCruz Instagram carousel publishing

### Summary

* Traced the stopped SoloCruz carousel schedule to a runtime f-string formatting error in the shared Instagram JSON prompt example. Every scheduled Instagram attempt since August 10 failed before Gemini was called.
* Escaped the literal `visualSystem` object correctly in the shared prompt builder.
* Removed an obsolete `run_scheduled_content_engine` import/call from the scheduler after the current app no longer exposed that retired worker.
* Generated a new seven-slide SoloCruz carousel from the next eligible published article and submitted it successfully through Zernio.

### Files changed

* `app.py` — fixed the shared Instagram carousel prompt's strict-JSON example.
* `scheduler.py` — removed the obsolete worker import and call so the deployed scheduler starts against the current app.
* `docs/PROJECT_MEMORY.md` — recorded prompt-builder and scheduler/import release gates.
* `docs/DEPLOYMENT.md` — added end-to-end social scheduler verification steps.
* `docs/CHANGELOG_AI.md` — recorded this repair.

### Checks run

* `python3 -m py_compile app.py scheduler.py` passed locally and on the VPS.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; both remain online and Blog Core health returns `ok`.
* Called the corrected prompt builder with SoloCruz and a real published content job; it produced the complete prompt without a format exception.
* Generated social post `189` with seven real JPEG slides; its review page returns HTTP 200.
* Zernio accepted the Instagram submission and returned remote ID `6a94dfc534cf2f14980ee21c`.

### Risks / TODO

* Zernio reports the new post as `SUBMITTED` while its asynchronous provider delivery completes; reconciliation retains that state until Zernio reports the final Instagram result.
## 2026-08-31 — Resolve scheduled carousels to real articles

### Summary
* Reworked shared Instagram/TikTok scheduling so a carousel plan resolves its actual article before generation.
* Legacy synthetic source identifiers are repaired only when the plan has a strong editorial match with a published or imported site article.
* Plans whose article is not yet published remain visible as waiting for source; they no longer block later valid carousel plans or trigger unrelated content.

### Files changed
* `app.py` — added generic source resolution, editorial-match safeguards, and due-plan selection that continues past waiting records.
* `docs/PROJECT_MEMORY.md` — recorded the durable source-resolution contract.
* `docs/CHANGELOG_AI.md` — recorded this scheduling repair.

### Checks run
* `python3 -m py_compile app.py` passed locally and on the VPS.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; both are online and `/health` returns `ok`.
* Resolved SoloCruz plan 152 to its real imported article, and validated all 17 queued shared carousel plans without generating or publishing media.

### Risks / TODO
* Plans that genuinely have no matching live article intentionally wait until their linked content job is published or a suitable article exists.
## 2026-08-31 — Restore LaycanMatch native publishing reliability

### Summary

* Diagnosed LaycanMatch scheduled-publication failures as two historical issues in its native factory: a retired Gemini text model and a V3 build crash when an old payload lacked `page_id`.
* Added a V3 publishing-boundary guard that derives page identity from the target route and completes the minimal structural payload before writing it. This prevents one legacy draft from breaking the build of the whole site.

### Files changed

* `staging/laycanmatch-factory/app.py` — normalize V3 identity and structural defaults immediately before native publish.
* `/var/www/content-factory-laycanmatch/app.py` — deployed the same native-factory fix.
* `staging/PROJECT_MEMORY-production.md` — recorded the durable V3 publishing rule.
* `staging/DEPLOYMENT-production.md` — recorded the LaycanMatch native-factory release check.

### Checks run

* Compiled `/var/www/content-factory-laycanmatch/app.py` in its virtual environment.
* Restarted `content-factory-laycanmatch`; PM2 reports it online and its OpenAPI endpoint returns HTTP 200.
* Ran `factory_v3.cli build-preview --site sites/laycanmatch/site.yaml --language en`; QA is `ok` for 38 pages.
* Confirmed the shared Blog Core scheduler is online. The next LaycanMatch job remains queued for `2026-08-31 10:00 UTC`.

### Risks / TODO

* Failed jobs from 7–22 August remain historical errors caused by the retired `gemini-2.5-flash` configuration; they were not silently retried or overwritten.
* After the publishing diagnosis, explicitly set the LaycanMatch native factory's `GEMINI_TEXT_MODEL` and compatibility alias `GEMINI_MODEL_TEXT` to `gemini-3.7-flash`, then restarted the PM2 process.

## 2026-08-31 — Batch-regenerate six LaycanMatch articles as drafts

### Summary

* Audited six historical failed jobs. Four had short but real legacy `/blog/` pages; two had no accessible public counterpart.
* Reset all six for native-factory regeneration and corrected each canonical target to `/blog/<slug>/` before starting the batch. This avoids creating duplicate `/resources/` articles.
* Started all six through Blog Core's delegated native-factory lifecycle. They are generating and have not been published.

### Files changed

* Runtime `content_jobs` rows for LaycanMatch — canonical targets, route contracts, and generation state.
* `staging/PROJECT_MEMORY-production.md` — durable route-preservation decision.
* `staging/CHANGELOG_AI-production.md` — batch record.

### Checks run

* Verified every batch-start API response returned `202` with `GENERATING`.
* Rechecked all six after launch: all remain `GENERATING` with no recorded error.

### Risks / TODO

* Native generation is asynchronous. Review the synced drafts when the factory completes; do not publish blindly.

## 2026-08-31 — Enforced Reel narrative ledger and in-Reel participation

### Changed

* Extended the separate NOMADeira video-plan schema with `narrativeArc` and `viewerReactionBeat`.
* The writer prompt now requires progressive, per-clip information release; it may not disclose a multi-clip payoff in the opening beat.
* The final clip now has to contain exact, story-specific `shareExpression` and `commentExpression` as well as the combined in-Reel expression. Caption or pinned-comment CTAs do not satisfy the contract.
* Added hostile-critic instructions and deterministic validation for early payoff leakage, repeated/non-escalating beats, non-evidentiary scenery, reaction metadata, and missing share/comment action.
* Updated the separate video review page to display the narrative ledger and final in-Reel expressions.

### Verification

* `python3 -m py_compile batch_video_engine.py app_video_canary.py`
* `.venv/bin/python -m unittest -q test_batch_video_engine.py` — 10 tests passed.
* Blog Core `/health` returned `ok: true`.

## 2026-09-01 — Map all NOMADeira Phase-A sources and protect scheduling

### Summary

* Added dated official-source maps for all 12 Phase-A compliance records. Each remains private `SOURCES_COLLECTED`; no claim was marked verified and no draft, localization, media, schedule or public page was created.
* Added a universal `complianceCluster` lifecycle gate. Generation needs current VERIFIED claims; publication and scheduling need Tier B approval, all-locale review and visual QA.

### Files changed

* `deploy/collect_nomadeira_compliance_phase_a_source_maps.py` — idempotent full-Phase-A primary-source map importer.
* `app.py` — generic high-risk generation, publication and scheduling guards; no domain-specific condition.
* Runtime `content_jobs` for NOMADeira — 12 source maps only; runtime data remains ignored.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — lifecycle and evidence boundary.

### Checks run

* `python3 -m py_compile app.py deploy/collect_nomadeira_compliance_phase_a_source_maps.py` passed on the VPS.
* First collection updated 12 jobs; immediate repeat updated 0.
* Verified all 12 are private `SOURCES_COLLECTED`, unscheduled and have no English draft.
* Restarted only `blog-yas-core`; `/health` returned `ok: true`.
* Direct gate tests rejected an unreviewed job for both generation and publication.
* Replaced source-map revision `v1` with `v2`: removed three live-502 legacy `www2.gov.pt` references and confirmed current AIMA endpoints through the verifier's TLS fallback; repeat import again changed zero rows.
* Added generic source-claim review and Tier B approval API transitions. Empty review/approval requests return HTTP 400 and cannot alter a job.
* Claim review now derives the closed evidence-led page brief from the reviewed claims, preserving each claim's conditions and exceptions for generation.
* Added `deploy/plan_nomadeira_compliance_batch.py`: it uses Gemini Batch for evidence-led English drafts and persists a complete four-image prompt set per article before any image batch. The first canary batch is running as a managed one-off worker.
* Ran one isolated text-only Gemini canary; no image, video, render, queue or publication action was performed. Its first result exposed a comment-only final beat, so the universal contract was strengthened before the next canary.
* Subsequent isolated canaries were intentionally stopped by the same shared gate for a comment-only reaction, an overlong/duplicated final overlay, and a missing reaction ledger. The final text-only canary passed with a two-clip hook → payoff arc and a single two-line final in-Reel share/comment overlay. No media action was taken.

## 2026-08-31 — Universal GSC finalized-data foundation

### Summary
* Added a per-site Search Console setup, property-access verification, manual sync and scheduler-driven finalized Web Search collection.
* Stored page and query aggregates in separate durable tables, with a collection-run history and no credentials in SQLite or UI.
* Verified the first live property for Georivo: one finalized page row was collected successfully; no content was created or modified.

### Files changed
* `app.py` — GSC schema, Google API client, collector, Setup controls and JSON endpoints.
* `scheduler.py` — invokes the collector.
* `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/DEPLOYMENT.md` — durable operating contract.

### Checks run
* `python3 -m py_compile app.py scheduler.py` passed on the VPS.
* Schema migration, route guard, live property verification, and one live finalized-data collection passed.

### Risks / TODO
* Weekly topic selection and later decision/evaluation stages are not enabled in this first stage.

## 2026-08-31 — Add GSC-backed weekly topic planning

### Summary
* Added a weekly GSC opportunity planner that identifies real query demand with near-ranking positions, applies the shared content-quality and duplicate checks, and creates only reviewable recommendations.
* No article is generated, queued or published automatically by this stage.

### Files changed
* `app.py` — weekly GSC planning data model and planner.
* `scheduler.py` — invokes the weekly planner.
* `docs/PROJECT_MEMORY.md` — durable planning contract.

### Checks run
* `python3 -m py_compile app.py scheduler.py` passed locally and on the VPS.
* The live scheduler-planner executed for Georivo. Its fresh GSC history has no qualifying query yet, so it correctly created zero artificial recommendations.

### Risks / TODO
* Other sites need their own GSC property access configured before the planner can use their search data.

## 2026-08-31 — Verify GSC coverage and make empty planning retryable

### Summary
* Audited every connected Blog Core dashboard and both Blog Core PM2 processes; all site dashboards return HTTP 200 and the core plus scheduler are online.
* Verified GSC access against every managed domain. Eight exact domain properties are connected and collected their first finalized Web Search day. Four inaccessible properties remain safely disabled.
* Changed weekly planning so a fresh `NO_CANDIDATES` outcome retries daily as GSC history accumulates instead of preventing another attempt for the week.

### Files changed
* `app.py` — retry semantics for empty GSC weekly planning.
* `scheduler.py` — deployed with the existing weekly planner worker.
* `AGENTS.md` — durable-memory instructions restored at the repository root.
* `docs/PROJECT_MEMORY.md` — GSC coverage and retry behavior.
* `docs/CHANGELOG_AI.md` — this record.

### Checks run
* `python3 -m py_compile app.py scheduler.py` passed locally and on the VPS.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; `/health` returned `ok`.
* GSC collection succeeded for eight connected properties for `2026-08-28`.
* The planner ran against the collected data and created no unsupported recommendations.

### Risks / TODO
* `solocruz.com`, `geo.yas.ooo`, `karpaleksei.com`, and `nomadeira.com` need the service account added to the exact `sc-domain:` Search Console property before collection can begin.
* One finalized day is not sufficient for 28-day planning. The scheduled collector will accumulate the required history without generating or publishing content automatically.

## 2026-08-31 — Reverify all GSC permissions

### Summary
* Reverified every configured independent Blog Core property after access was granted. All previously managed-site properties return `siteFullUser` and are enabled for scheduled collection.
* Confirmed `sc-domain:veselovaveronika.com` has the same access.

### Checks run
* Verified the Google Search Console property list through the production service account.

## 2026-08-31 — Add Veselova Veronika as an independent managed site

### Summary
* Added `veselovaveronika.com` as its own Blog Core site (`id 19`), preserving a strict separation from `karpaleksei.com` despite their shared VPS application host.
* Connected its exact `sc-domain:veselovaveronika.com` GSC property, verified `siteFullUser`, and collected the first finalized-day snapshot: one page row and zero query rows.
* No scan, generation, publication, template installation, or change to the website's files was performed.

### Checks run
* Verified the independent dashboard returns HTTP 200.
* Blog Core `/health` returned `ok` after setup.

## 2026-08-31 — Remove geo.yas.ooo as a separate GSC target

### Summary
* Removed the separate Search Console connection for `geo.yas.ooo` after confirming it is not an independent site property.
* Kept its Blog Core site record untouched. SEO collection and planning use the shared `yas.ooo` property instead.

### Files changed
* Runtime `gsc_site_connections` — removed the independent subdomain configuration.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — corrected the durable GSC inventory.

## 2026-09-01 — Seed NOMADeira compliance Phase A into the native Blog Core queue

### Summary

* Seeded all 12 Phase-A topics from NOMADeira's compliance-cluster specification into the existing Blog Core article queue.
* Each record is private and `BLOCKED_EVIDENCE`, with generation and publication explicitly blocked pending primary-source evidence and Tier B review. No article, localization, media or public page was generated.
* The pre-existing `/madeira-nif-bank-account-order` job was adopted as the canonical queue record instead of creating a duplicate. The other 11 slugs were created once.

### Files changed

* `deploy/seed_nomadeira_compliance_phase_a.py` — idempotent Phase-A queue seed, canonical collision adoption, high-risk brief metadata and duplicate technical-log cleanup.
* Runtime `content_jobs` and `content_job_logs` for NOMADeira — 12 protected Phase-A compliance briefs; runtime data remains ignored.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable queue and operating-rule record.

### Checks run

* `python3 -m py_compile deploy/seed_nomadeira_compliance_phase_a.py` passed.
* Repeated production seed created no rows and mutated no records; all 12 jobs remain private `BLOCKED_EVIDENCE` records with one seed log each.
* Blog Core `/health` returned `ok: true`.

## 2026-09-01 — Collect primary-source maps for NOMADeira compliance pilots

### Summary

* Collected private official-source maps for the three first pilots: NIF through representative, remote employee residence route and opening atividade.
* Each pilot now has three primary official sources and three scope-limited claim proposals. All remain private `SOURCES_COLLECTED`; no claim IDs, drafts, localizations, media, previews or publications were created.
* The remote-work map uses the current AIMA post-arrival page and the cited Diário da República visa regulation. NIF and atividade maps use current gov.pt and Autoridade Tributária sources; atividade also has the gov.pt/Segurança Social registration source.

### Files changed

* `deploy/collect_nomadeira_compliance_pilot_source_maps.py` — idempotent primary-source-map collector with expiry, source scope and unverified high-risk claim proposals.
* Runtime `content_jobs` for the three NOMADeira pilots — source maps and proposal metadata only; runtime data remains ignored.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — recorded the source-collection gate.

### Checks run

* `python3 -m py_compile deploy/collect_nomadeira_compliance_pilot_source_maps.py` passed.
* The first production run updated exactly three records; the immediate repeat updated zero.
* Verified three sources and three proposals per pilot, zero draft HTML and no public records.
* Blog Core `/health` returned `ok: true`.

## 2026-09-01 — Approve all Phase-A drafts and submit one NOMADeira image batch

### Summary

* Validated and recorded owner-authorized content approval for all 12 English, source-bounded Phase-A drafts and their 48 unique image prompts.
* Updated the universal evidence-led contract to avoid invented workflow actions and invented links when the approved ledger does not support them.
* Submitted one asynchronous `gemini-3.1-flash-image` batch containing all 48 images. No images were generated synchronously, published, scheduled or represented as visually approved.

### Files changed

* `app.py` — source-availability publication guard and universal evidence-led composition rules.
* `deploy/submit_nomadeira_phase_a_image_batch.py` — complete prompt-ledger batch submitter with provider batch-name persistence.
* Runtime Phase-A `content_jobs` — source-bounded English drafts, four visual prompts per job, content approval audit entries and one submitted image batch reference.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable operational record.

### Checks run

* `python3 -m py_compile app.py` passed on the VPS.
* All 12 structured drafts passed generation and draft validation; each has four non-empty, globally unique image prompts (48 total).
* Batch submission returned `batches/y00e3dypcsaqa0ob0dis03w8u96v6spk2y7t`.
* The batch completed successfully: 48 selected WebP assets were persisted, four per approved article, and Blog Core health remained `ok`.

## 2026-09-01 — Activate daily YAS article and X schedules

### Summary

* Audited all unpublished `yas.ooo` content instead of treating every `DRAFT` row as a public article. Kept the internal evidence social preview unscheduled, canceled one exact duplicate evidence article, and recovered the stale article generation job.
* Scheduled 16 unique public articles once per day at 09:00 `Europe/Warsaw`, from 2026-09-02 through 2026-09-17. Updated the site publication cadence from manual to daily.
* Replaced the inert 48-row legacy X schedule with executable `social_work_items`, one per day at 15:00 `Europe/Warsaw`, from 2026-09-02 through 2026-10-19.
* Generalized the explicit X scheduled worker to deliver both evidence-derived and article-derived reviewed X work items. Missing Zernio account mapping now preserves the due item for retry instead of failing it.
* Kept generic topic discovery disabled. The active evidence/vacancy contour and GSC planner remain the upstream sources for new YAS ideas.

### Files changed

* `app.py` — executable X queue coverage and wait-for-connection behavior.
* Runtime `sites`, `content_jobs`, `content_job_logs`, `social_work_items`, and legacy `social_post_schedule` state for `yas.ooo`; runtime data remains ignored.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable schedule and source-of-truth rules.

### Checks run

* `python3 -m py_compile app.py scheduler.py` passed locally and on the VPS.
* Missing X account mapping canary returned `waiting_for_connection` and preserved the first item as `SCHEDULED`.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler`; both are online and `/health` returns `ok`.
* Verified 16 unique scheduled public article jobs and 48 executable scheduled X work items; all 48 obsolete schedule rows are marked `SUPERSEDED`.

### Remaining external setup

* Completed/superseded on 2026-09-01: the `yas.ooo` connection now maps the `YASflows` account from the dedicated Zernio `YAS` profile.

## 2026-09-01 — Connect the dedicated SoloCruz Pinterest destination

### Summary

* Discovered the new `solocruzcom` Pinterest account inside the dedicated Zernio profile `Solocruz` and verified its public default board `SoloCruz` through the live Zernio API.
* Saved the profile, account and default-board mapping in Blog Core site `7`, and registered the board in the site-scoped Pinterest strategy.
* Kept Pinterest generation and automatic delivery disabled (`daily_pin_target=0`). No Pin, image, schedule or publication was created.

### Runtime changes

* Production `social_connections` and `pinterest_strategies` rows for `solocruz.com`; runtime data remains ignored.
* Recoverable pre-change database copy: `backups/blog_core-before-solocruz-pinterest-20260901.sqlite3` on the VPS.

### Checks run

* Zernio listed five connected accounts; Blog Core's connection test passed and reports Instagram, Pinterest and TikTok mapped for SoloCruz.
* Pinterest connection state changed from `disconnected` to `connected` via Zernio.
* The registered board ID matches Zernio's `defaultBoardId`; automatic Pinterest remains inactive and no `visual_pins` or Pinterest `social_posts` were created by this setup.

## 2026-09-01 — Build the 45-Pin SoloCruz ledger and submit one image batch

### Summary

* Authored a complete 45-Pin English ledger from 15 public SoloCruz articles, using three different search/decision angles per source. Every record has its own short hook, native title, description, CTA, alt text, keywords, destination URL and photographic scene.
* Preserved the four owner-viewed 1000×1500 previews as the first four unpublished Pin drafts. Submitted exactly the remaining 41 unique scene prompts in one asynchronous `gemini-3.1-flash-image` batch; no image was regenerated for the accepted previews.
* Added deterministic post-processing for batch results: Gemini supplies a text-free background, while Blog Core later adds the exact hook and site-owned SoloCruz logo. No Pin was scheduled or published, and Pinterest automation remains disabled.
* Expanded the universal Pin review UI to display up to 60 records and show article source, image hook, search intent, CTA and exact destination for article-derived Pins.

### Files changed

* `deploy/pinterest_pin_batch.py` — universal idempotent ledger seed, Gemini batch submit/status/collection and deterministic overlay compositor.
* `deploy/solocruz_pinterest_45.json` — reviewed site configuration for 45 article-derived SoloCruz Pins.
* `app.py` — complete article-derived Pin review metadata and 60-item panel coverage.
* Runtime `visual_pins` for site `7`; runtime data and generated media remain ignored.

### Checks run

* `python3 -m py_compile app.py deploy/pinterest_pin_batch.py` passed locally and on the VPS.
* Ledger checks passed for 45 rows, 45 unique overlays, 45 unique titles, 45 unique scenes, public SoloCruz destinations and all Pinterest field limits.
* Repeated seed created zero new rows and preserved 41 `BATCH_SUBMITTED` plus four `DRAFT` rows with one unchanged provider batch name.
* Batch `batches/ixvtvgfo5cofm4ur65eaa3ravoearq0d316u` completed and supplied the 41 requested backgrounds. Full-contact-sheet QA rejected Pins 6 and 27 because their images did not prove the promised three-option and money-boundary stories; a revised two-image correction batch replaced only those two scenes.
* Final verification found 45 `DRAFT` rows, 45 unique 1000×1500 JPEGs, valid SoloCruz article destinations and zero remote URLs, schedules or publications.
* Blog Core restarted successfully and `/health` returned `ok`.

## 2026-09-01 — Lock the SoloCruz Pin finishing direction without regenerating backgrounds

### Summary

* Reused the already-paid Pinterest photographic backgrounds and produced two corrected owner-review previews without another Gemini image request.
* Locked the requested SoloCruz finish: a top-only navy-to-blue gradient headline panel, edge-to-edge photograph below it, contextual turquoise headline emphasis and the official full logo centered over the bottom of the photo.
* Removed the rejected footer, direct-on-photo and free-form layout experiments from the accepted direction.
* Normalized the supplied `logo600.svg` from its embedded checkerboard appearance to a true-alpha colour logo with a white separation edge for compositing.

### Artifacts

* `output/solocruz-pin-salvage/pin-005-gradient-logo600-final.jpg`
* `output/solocruz-pin-salvage/pin-007-gradient-logo600-final.jpg`

### Safety

* No production Pin row was replaced, scheduled or published.
* No replacement photographic background was generated.

## 2026-09-01 — Apply the approved SoloCruz finish to all remaining Pin drafts

### Summary

* Recollected and recomposed all 41 batch-backed SoloCruz Pins from their saved Gemini responses; no new image request was submitted and the four owner-approved Pins were not changed.
* Applied one site-configured frame to every remaining asset: top navy-to-blue gradient panel, exact large hook with one contextual turquoise line, edge-to-edge photograph below it, no footer, and the official full SoloCruz logo centered over the bottom of the photograph.
* Added deterministic removal of substantial uniform provider edge/spacer bands before crop, preventing accidental white or dark fields in the finished Pin.

### Files changed

* `deploy/pinterest_pin_batch.py` — universal configurable finishing compositor and provider-band cleanup.
* `deploy/solocruz_pinterest_finish.json` — exact site-scoped line breaks, accent line, colours, dimensions and logo reference for all 45 Pins.
* Runtime `visual_pins` assets for site `7` and `assets/brand/logo600-pin.png`; generated media and runtime data remain ignored.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable production and safety rules.

### Checks run

* Local and production `py_compile` passed for `deploy/pinterest_pin_batch.py`; Blog Core `/health` returned `ok`.
* Verified 45 `DRAFT` rows and 45 unique 1000×1500 JPEGs: 41 use the exact configured gradient finish and four approved originals are byte-identical to the recoverable pre-change backup.
* Verified exact configured hook line joins for all 41 recomposed Pins and zero Pinterest schedules, sends or publications.
* Full ordered review sheet: `output/solocruz-pinterest-final-review-v4/contact-sheet-45.jpg`.

## 2026-09-01 — Correct SoloCruz Pin headline line spacing

### Summary

* Corrected a mass-composition defect where uppercase headline lines used only 5–8 pixels of spacing and appeared to collide.
* Replaced it with proportional 20% font spacing, a 20-pixel floor and a hard rendered-glyph assertion requiring at least 18 pixels between every adjacent line.
* Proved the correction first on three-line and four-line canaries, then recomposed all 41 batch-backed drafts from saved provider responses. No image generation, scheduling or publication occurred.

### Checks run

* All 41 recomposed headlines passed rendered-box collision checks; the minimum measured line gap is 20 pixels.
* Verified 45 unique 1000×1500 JPEG drafts, four owner-approved originals byte-identical to backup, and zero scheduled or published Pinterest records.
* Production `py_compile` and Blog Core `/health` passed.
* Corrected review sheet: `output/solocruz-pinterest-final-review-v5/contact-sheet-45-clean.jpg`.

## 2026-09-01 — Schedule all 45 approved SoloCruz Pins

### Summary

* Submitted all 45 approved SoloCruz Pins to the mapped Zernio Pinterest destination as scheduled posts, three per logical Warsaw day at 15:00, 19:00 and 24:00.
* Scheduled logical dates 2026-09-02 through 2026-09-16; `24:00` is stored and sent as `00:00` on the next calendar date, making the final execution 2026-09-17 00:00 Warsaw time.
* Persisted the exact provider timestamp and logical Warsaw slot in each Pin's `publicationSchedule` metadata and exposed the scheduled timestamp in the Blog Core Pin panel.
* Kept continuous Pinterest automation disabled with a daily target of zero; only these 45 owner-approved Pins were scheduled.

### Files and runtime changed

* `app.py` — persist and display explicit visual-Pin schedule metadata after Zernio accepts a scheduled post.
* Production `visual_pins` for site `7`; every record is now `SCHEDULED` with its own Zernio schedule identifier.
* Recoverable pre-schedule database copy: `backups/blog_core-before-solocruz-pinterest-schedule-20260901.sqlite3` on the VPS.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable schedule and finite-queue rule.

### Checks run

* Local and production `py_compile` passed for `app.py`.
* Verified 45 `SCHEDULED` records, 45 unique non-empty Zernio schedule identifiers, and exactly 15 slots each at 15:00, 19:00 and logical 24:00 `Europe/Warsaw`.
* Verified continuous Pinterest automation remains disabled, restarted `blog-yas-core`, and confirmed Blog Core `/health` returns `ok`.

## 2026-09-01 — Connect YAS X and move its reviewed queue to 17:00 Warsaw

### Summary

* Disambiguated two Zernio accounts with the same `YASflows` username and mapped Blog Core site `12` specifically to the X account inside the dedicated `YAS` profile, not the account inside `Default`.
* Rescheduled the existing 48 reviewed X work items to one per day at 17:00 `Europe/Warsaw`, from 2026-09-02 through 2026-10-19. No post text or media was regenerated.
* Kept the generic X cadence disabled; the explicit reviewed work-item queue remains the only YAS X publication source.

### Runtime changes

* Production `social_connections` and `social_work_items` for `yas.ooo`; runtime data remains ignored.
* Recoverable pre-change database copy: `backups/blog_core-before-yas-x-profile-and-17h-schedule-20260901.sqlite3` on the VPS.

### Checks run

* Zernio connection test passed and reported the Twitter mapping.
* Verified 48 unique `SCHEDULED` work items, 48 linked `DRAFT` social posts, a continuous one-per-day 17:00 Warsaw sequence, and 48 superseded legacy schedule rows.
* Restarted `blog-yas-core-scheduler`; it is online. A pre-first-slot worker canary found zero due items, and Blog Core `/health` returned `ok`.

## 2026-09-01 — Map the YAS Instagram account without enabling publication

### Summary

* Discovered Instagram account `yas.flows` inside the dedicated Zernio `YAS` profile and saved that exact account mapping for Blog Core site `12`.
* Preserved the existing `YASflows` X mapping and verified Zernio now reports both Instagram and Twitter as mapped.
* Kept Instagram and Instagram Reel cadences disabled because the owner has not yet selected frequency and Warsaw publication times.

### Runtime changes and checks

* Production `social_connections` for `yas.ooo`; runtime data remains ignored.
* Recoverable pre-change database copy: `backups/blog_core-before-yas-instagram-map-20260901.sqlite3` on the VPS.
* Verified the Instagram connection is `connected`, all 27 carousel drafts and three rendered Reel drafts remain unpublished, and no Instagram schedule was created.

## 2026-09-01 — Schedule the 27 YAS vacancy carousels at 18:00 Warsaw

### Summary

* Submitted all 27 completed seven-slide YAS vacancy carousels to the mapped `yas.flows` Instagram destination through Zernio, one per day at 18:00 `Europe/Warsaw`, from 2026-09-02 through 2026-09-28.
* Extended the universal Zernio draft publisher to persist explicit schedule metadata in each social post's `content_json.publicationSchedule`; no YAS-specific domain branch was added.
* Kept all three rendered YAS Reels as unscheduled `DRAFT` records and left generic Instagram and Reel cadences disabled, so only the reviewed finite carousel queue will run.
* One request returned a transient HTTP 400; replaying the exact same payload with the same idempotency key was accepted without content changes, then reconciled. No duplicate schedule was created.

### Files and runtime changed

* `app.py` — pass and persist the explicit provider schedule for Zernio social drafts.
* Production `social_posts` for Blog Core site `12`; all 27 carousel rows now have distinct Zernio schedule identifiers.
* Recoverable pre-change database copy: `backups/blog_core-before-yas-instagram-carousel-schedule-20260901.sqlite3` on the VPS.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable YAS Instagram execution rules and schedule.

### Checks run

* Local and production `py_compile` passed for `app.py`.
* Verified 27 `SCHEDULED` carousels, 27 unique non-empty Zernio identifiers, one continuous daily 18:00 Warsaw sequence, and exact first/last slots of 2026-09-02 and 2026-09-28.
* Verified all three Reels remain `DRAFT`, both automatic Instagram cadences remain disabled, `blog-yas-core` is online, and Blog Core `/health` returns `ok`.

## 2026-09-02 — Map the verified YAS Reddit account without enabling publication

### Summary

* Confirmed that reconnecting Reddit replaced the earlier incorrect OAuth identity with the intended system username `AiStartupGuy` in the dedicated Zernio `YAS` profile.
* Mapped that exact Zernio Reddit account to Blog Core site `12` while preserving the existing YAS Instagram and X mappings.
* Did not select a default subreddit, activate Reddit as an automatic channel, enable a cadence, schedule a candidate or publish anything. The seven discovered Reddit candidates remain review-only.

### Runtime changes and checks

* Production `social_connections` for `yas.ooo`; runtime data remains ignored.
* Recoverable pre-change database copy: `backups/blog_core-before-yas-reddit-map-20260902.sqlite3` on the VPS.
* Zernio connection test passed and reported Instagram, Reddit and Twitter mappings. Verified Reddit cadence remains disabled, no Reddit `social_posts` exist, both Blog Core PM2 processes are online, and `/health` returns `ok`.

## 2026-09-02 — Schedule the reviewed YAS Reddit queue and map Threads

### Summary

* Confirmed and mapped Threads account `yas.flows` in the dedicated Zernio `YAS` profile without enabling Threads generation, scheduling or publication.
* Reviewed the seven prepared Reddit candidates against current community availability and rules. Replaced unavailable destinations with relevant reviewed communities and materialized seven neutral text/self posts with no links, company mention, offer or CTA.
* Submitted the finite Reddit queue to Zernio for `AiStartupGuy`, one post per day at 18:00 `Europe/Warsaw`, from 2026-09-02 through 2026-09-08: two to `r/automation`, two to `r/businessanalysis`, and three to `r/softwareengineering`.
* Kept both generic Reddit and Threads cadences disabled. Threads' fourteen existing drafts remain unscheduled.

### Files and runtime changed

* `app.py` — make Reddit subreddit routing creative-scoped, retain the connection default only as a legacy fallback, and force reviewed text/self-post delivery.
* Production `social_connections`, `social_community_rule_snapshots`, `social_work_items`, and `social_posts` for Blog Core site `12`; runtime data remains ignored.
* Recoverable pre-change database copy: `backups/blog_core-before-yas-threads-map-and-reddit-schedule-20260902.sqlite3` on the VPS.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — durable per-creative Reddit routing and YAS schedule state.

### Checks run

* Local and production `py_compile` passed for `app.py`; both Blog Core PM2 processes are online and `/health` returns `ok`.
* Zernio reports Instagram, Reddit, Threads and Twitter mapped for YAS. Its posts API returns all seven Reddit records as `scheduled`, each with the intended `AiStartupGuy` account, exact subreddit and 16:00 UTC / 18:00 Warsaw timestamp.
* Verified seven unique Zernio schedule IDs, a continuous one-per-day sequence, per-post rule snapshots, and deterministic no-link/no-company validation. Reddit and Threads automatic cadences remain disabled.

## 2026-09-02 — Make Zernio the authority for Reddit community availability

### Summary

* Confirmed that Zernio exposes the connected Reddit account's managed community list through `/accounts/{accountId}/reddit-subreddits`, analogous to its Pinterest boards endpoint.
* Detected before the first release that five initially selected communities were absent from the `AiStartupGuy` Zernio list. Updated the existing scheduled provider records in place, preserving all seven dates and Zernio IDs.
* The final provider-accepted routing is four posts to `r/automation` and three context-adapted startup discussions to `r/GetStartups`. `r/SaaS` was deliberately excluded because its current rules explicitly prohibit AI-generated text.
* Supersedes the initial two/two/three community split recorded in the immediately preceding change; the 18:00 Warsaw cadence and 2026-09-02 through 2026-09-08 dates are unchanged.

### Files and runtime changed

* `app.py` — require every future Reddit target to appear in the selected Zernio account's live subreddit list before submission; fail closed when provider validation is unavailable or the target is absent.
* Production Reddit work-item, social-post and rule-snapshot metadata for site `12`; five already scheduled Zernio records were updated in place.
* Recoverable pre-correction database copy: `backups/blog_core-before-yas-reddit-zernio-community-correction-20260902.sqlite3` on the VPS.
* `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md` — provider-owned destination rule and corrected final schedule.

### Checks run

* Zernio returned the live `AiStartupGuy` subreddit list; every final target is present in it. All five provider updates returned `scheduled` and retained their existing IDs and exact timestamps.
* Verified seven local `SCHEDULED` work items and posts, each with provider-verified community metadata, one daily 18:00 Warsaw slot, no link/company validation, and a unique provider ID.
* Local and production `py_compile` passed; both Blog Core processes are online and `/health` returns `ok`. A later read-only provider-list request hit HTTP 429 after the successful validations and updates; no write was ambiguous.

## 2026-09-02 — Integrate EPR Scan with Blog Core and release EN/DE/FR/ES SEO foundations

### Summary

* Registered `eprscan.eu` as Blog Core native content-store site `20` with English, German, French and Spanish only; Russian and Italian are excluded.
* Added a strict reviewed-compliance publication gate for site-declared Blog Core articles and expanded the durable payload with reviewer date, ruleset version and change log.
* Fixed collision-prone non-blog native filenames by deriving them from the complete target path.
* Released EPR Scan `/blog`, `/de/blog`, `/fr/blog`, `/es/blog`, article rendering, native navigation, reciprocal hreflang, sitemap integration, Article/Breadcrumb schema and visible author/reviewer/evidence/change metadata.
* Corrected `/account` to a self-canonical `noindex,nofollow` page with a server-rendered H1. Existing PPWR/checker/product routes and design remain source-authoritative.
* Installed an enabled systemd path handoff so an explicit valid Blog Core publication triggers validation, typecheck, production build and EPR Scan restart. No article was generated or published because no real reviewer-approved content was supplied.

### Files and runtime changed

* `app.py` — native filename identity, reviewed multilingual blog publication gate and expanded editorial payload.
* `docs/EPRSCAN_INTEGRATION.md`, `docs/PROJECT_MEMORY.md`, `docs/INTEGRATIONS.md`, `docs/DEPLOYMENT.md`, `docs/CHANGELOG_AI.md` — durable contract and operations.
* Production Blog Core database site `20`; recoverable backup `backups/blog_core-pre-eprscan-20260902-1338.sqlite3`.
* EPR Scan source/build and systemd units on the VPS; recoverable source/build snapshot `/var/www/eprscan-release-backups/pre-blog-core-20260902-1345`.

### Checks run

* Blog Core local and production `py_compile` passed; both Blog Core PM2 processes restarted online.
* EPR Scan TypeScript, ESLint and production build passed. The complete source test suite passed 313/315 in the extracted checkout; the two failures are pre-existing repository-context checks for absent parent `../.node-version` and `../docs/REQUIREMENTS_TRACEABILITY.md`, not application failures.
* Candidate and public production release checks passed across the 12 original launch routes, 52 internal targets, security headers, canonicals, hreflang, sitemap/robots and required schema.
* Public `https://eprscan.eu` returns 200 for EN/DE/FR/ES blog hubs and sampled translated product/checker pages. The dedicated Blog Core integration check passes, and `/account` exposes one H1 plus `noindex,nofollow` without a home canonical.
* A live GSC property verification for `sc-domain:eprscan.eu` returned `no_access`. The connection is saved but disabled to prevent scheduler noise; Search Console and Bing completion remain external owner-permission steps.

## 2026-09-02 — Complete EPR Scan multilingual route integrity and seed the review-only TOR roadmap

### Summary

* Corrected inherited home canonicals on `/reports` and `/access/recover`; added server-rendered H1 headings to English and localized account/report entry pages while preserving `noindex` on private routes.
* Extended localized source generation to translate multiline and expression-split JSX text, including fallback string literals inside composite expressions. Added a catalog-driven completeness check for generated German, French and Spanish source.
* Expanded the integration regression check to 60 public and 16 private routes across EN/DE/FR/ES, with exact H1, canonical, reciprocal hreflang, sitemap/noindex and RU/IT-exclusion assertions.
* Added 12 open TOR recommendations to EPR Scan site `20`; no content job was created and nothing was generated or published.

### Runtime changes and recovery

* EPR Scan production source/build at `/var/www/eprscan`; recoverable snapshot `/var/www/eprscan-release-backups/pre-locale-integrity-20260902-1435`.
* Blog Core production recommendations for site `20`; recoverable database backup `backups/blog_core-pre-eprscan-recommendations-20260902-1442.sqlite3`.
* The isolated EPR Scan candidate process, source directory and state directory were removed after successful production verification.

### Checks run

* Candidate and public production multilingual checks passed all 76 routes. The standard release check passed 12 launch pages, 52 internal targets, the 27-country capability contract, security, metadata, hreflang, sitemap/robots and required JSON-LD.
* Localization completeness, TypeScript, source-scoped ESLint and Node 22 production build passed. The repository-wide lint command still scans retained historical `dist.*` snapshots and reports their pre-existing generated-bundle findings, so release lint is scoped to source directories.
* Production reports 12 open `eprscan-tor:*` recommendations and zero site `20` content jobs. GSC/Bing ownership and assignment of a real legal reviewer remain external gates.

## 2026-09-02 — Enforce honest review indexing and release EPR Scan SEO hubs

### Summary

* Removed the public effect of the placeholder reviewer identity. Country pages now become reviewed/indexable only through a real public reviewer profile.
* Made DE/FR/ES indexing page-level and fail-closed: translated routes remain accessible but stay `noindex` and out of hreflang/sitemap until named language and legal approvals exist. English remains canonical at root; RU/IT remain excluded.
* Released populated English `/guides`, `/countries`, `/marketplaces`, `/tools` and `/company` trust directories, visible breadcrumbs, curated related links, Organization/WebSite schema and route-aware language navigation.
* Added the TOR funnel events alongside existing analytics, with server-confirmed purchase/assistance events and hashed internal identifiers. Kept `template_download` absent because no real template asset exists.

### Runtime changes and recovery

* EPR Scan production source/build at `/var/www/eprscan`.
* Review/index gate backup: `/var/www/eprscan-release-backups/pre-review-index-gates-20260902-1505`.
* Hubs/linking/analytics backup: `/var/www/eprscan-release-backups/pre-seo-hubs-20260902-1252`.
* No Blog Core content job or public article was created.

### Checks run

* Candidate localization, TypeScript, ESLint and Node 22 production build passed; focused new tests passed 10/10. The full isolated suite passed 318/320, with only the two known parent-repository fixture checks failing.
* Candidate and public production integration checks passed 60 translated public variants, 10 English hub/trust routes and 16 private routes. The release check passed 12 launch pages, 59 internal targets, the EU27 capability catalog, metadata, schema, sitemap/robots, security headers and paid-report readiness.
* Production health is `ok`, PM2 `eprscan` is online and the Blog Core content path watcher is active.
* Remaining external gates: real compliance/language reviewers with public evidence, Google Search Console access, and Bing Webmaster Tools ownership/submission.

## 2026-09-02 — Add the EPR Scan weekly production SEO crawl

### Summary

* Added an enabled persistent systemd timer for a read-only weekly production crawl, scheduled Mondays at 06:15 UTC with randomized delay.
* Added a dynamic sitemap crawler that checks every current sitemap page and discovered internal target for status/redirects, noindex, canonical, metadata duplication, H1, broken links, orphans and hreflang integrity. Future approved Blog Core articles are included automatically.
* Persisted compact atomic `last.json` status and append-only NDJSON history while retaining full command output in the systemd journal. Failed runs are observable and never mutate or publish content.

### Checks run

* Calendar syntax validated with `systemd-analyze`; the timer is enabled and active.
* Manual end-to-end timer run passed in 23 seconds: 60 translated variants, 10 English hubs, 16 private routes, 12 release pages, 21 sitemap pages and 69 internal targets.
* Production health remained `ok`. RU/IT remained excluded as locales.

### Recovery

* `/var/www/eprscan-release-backups/pre-weekly-seo-crawl-20260902-1301`.
* `/var/www/eprscan-release-backups/pre-indexable-sitemap-crawl-20260902-1305`.

## 2026-09-02 — Remove EPR Scan image redirects and repair contrast

### Summary

* Fixed the new breadcrumb and related-card muted colors that Lighthouse identified below WCAG AA contrast.
* Switched already-compressed editorial WebP assets to direct static delivery, removing the Vinext `/_next/image` 302-to-HTTP hop from hero loading, and marked above-the-fold heroes for preload/high priority.
* Reduced the favicon from a 512px/129KB PNG to a visually verified 64px/2.1KB indexed PNG; recompressed the three representative LCP images without changing their subjects.

### Checks run

* Candidate TypeScript, source-scoped ESLint and production build passed; integration, release and dynamic sitemap crawls passed.
* Post-change Lighthouse reports Accessibility 100 and SEO 100 for home, PPWR and checker. Synthetic mobile performance remains variable and one production run still exceeded the strict 2.5s LCP threshold, so lab performance is not represented as fully closed; actual LCP/CLS/INP continue to be collected in the protected RUM dashboard.
* Final production weekly crawl passed, favicon delivery is 2,140 bytes, service health is `ok`, and the temporary candidate was removed.

## 2026-09-02 — Stabilize EPR Scan critical rendering and Lighthouse release validation

### Summary

* Deferred the optional `web-vitals` module until browser idle time, reducing the initial analytics-tracker chunk from 10,978 to 2,147 bytes; the 7,962-byte metrics chunk now loads separately.
* Added intrinsic `content-visibility:auto` containment to below-the-fold public sections. Explicit cream/paper/lime surfaces preserve accurate WCAG contrast checks for skipped content.
* Reworked the strict Lighthouse release check to run three attempts by default and aggregate conservatively: median Performance/LCP, minimum Accessibility/SEO and maximum CLS. The TOR thresholds remain unchanged.
* Kept Lighthouse out of the low-priority weekly systemd crawl after real runs showed scheduling/CDN-induced false failures. The deterministic weekly multilingual, release, sitemap and localization checks remain enabled; field LCP/CLS/INP continue through protected RUM.

### Runtime changes and recovery

* EPR Scan production source/build: `/var/www/eprscan`; recovery snapshot: `/var/www/eprscan-release-backups/pre-lcp-stabilization-20260902-1347`.
* Removed the temporary PM2 candidate, `/var/www/eprscan-lcp-candidate-20260902`, and `/var/lib/eprscan-lcp-candidate-20260902` after deployment.
* No Blog Core recommendation was materialized and no article was generated or published.

### Checks run

* Candidate three-run medians passed all representative pages: home LCP 2,435 ms, PPWR 2,403 ms and checker 2,483 ms; Accessibility and SEO were 100 throughout, with maximum CLS 0.1.
* The deployed production-origin run reported home 2,460 ms, PPWR 2,427 ms and checker 2,518 ms. The 18 ms checker overage demonstrates remaining lab variance and is not represented as a closed field-performance result; RUM remains authoritative.
* Production TypeScript, source-scoped ESLint and Vinext build passed. Public multilingual integration, release, dynamic sitemap and localization checks passed; the final weekly run `20260902T135725Z` passed in 14 seconds.

### Recovery

* `/var/www/eprscan-release-backups/pre-quality-fix-20260902-1322`.
## 2026-09-02 — Generate and batch-localize the EPR Scan first content wave

* Materialized the ten remaining substantive EPR Scan TOR recommendations as native `/blog/{slug}` content jobs. Kept queue-health and named-reviewer governance recommendations open instead of turning operational work into articles.
* Prepared a distinct source-bounded page brief for every job with a direct answer, seven-section outline, official/primary sources, reader checks, prohibited claims, required terminology and approved contextual crosslinks to existing source-authoritative EPR Scan routes.
* Generated the ten new English drafts in controlled waves. Two first-pass drafts failed the 1,200-word validator and were regenerated; the final 11/11 draft set contains 1,201–1,636 words, three inline images, five FAQ items and four or five internal links per page.
* Ran one `gemini-3.7-flash` translation batch across all 11 English sources. It created and structurally validated exactly 33 rows: 11 DE, 11 FR and 11 ES; RU/IT count remains zero.
* Extended EPR Scan's unpublished-content validator and TypeScript draft contract to accept complete DE/FR/ES draft localizations without publishing or exposing them. The English private preview remains `noindex`, no-store and outside the sitemap.
* Rebuilt EPR Scan once after the atomic batch, restored the enabled systemd path watcher and verified all 11 preview IDs return HTTP 200, the service health endpoint passes, zero EPR Scan jobs have a public URL and the sitemap contains no draft blog routes.
* Production recovery points: `/var/www/eprscan-release-backups/pre-draft-localizations-20260902`, `/var/www/blog.yas.ooo/backups/blog_core-pre-eprscan-batch-20260902.sqlite3`, and `/var/www/blog.yas.ooo/backups/blog_core-pre-eprscan-localization-batch-20260902.sqlite3`.

## 2026-09-02 — Replace human-review gates with official-source audit and publish EPR Scan wave

* Replaced the EPR Scan human reviewer/language reviewer gate with `publication_contract:source_audited_multilingual_compliance`. Publication now requires a passing claim-to-official-source ledger, live source checks, exact EN/DE/FR/ES locale coverage, DOM/number/link parity, SEO review and browser QA.
* Removed public `Reviewed by` and person-review schema. Published pages transparently display `Official sources verified`, the check date and ruleset version; trust-policy copy documents the automated method.
* Audited and published 11 English articles plus 33 DE/FR/ES variants. One unsupported added number in the German PPWR translation was removed; the bot-blocked Etsy Help citation was removed, leaving the article bounded by accessible PPWR and ZSVR official sources.
* Dismissed the obsolete named-human-review recommendation and closed the stale two-article validation warning after the source audit passed. Only the next-five-topics recommendation remains open; it does not authorize generation.
* Added all four localized blog hubs to the sitemap after the article set became public. Publication now removes its stale private draft-store record.
* Production checks passed: Python compile, EPR Scan TypeScript, Vinext build, the 60-public/10-English-hub/16-private integration suite, all 44 article routes, reciprocal hreflang, contextual crosslinks, desktop/mobile browser inspection and 48 blog sitemap URLs. RU/IT remain absent.
* Recovery database: `/var/www/blog.yas.ooo/data/blog_core.sqlite3.pre-source-audit-20260902`.
## 2026-09-02 — Diagnosed missed yas.ooo LinkedIn and Threads publications

* The scheduled LinkedIn run for yas.ooo started at 08:00 UTC (10:00 Europe/Warsaw) and ended in `ERROR` before provider submission: the prepared draft contained 3,642 characters, exceeding the enforced 3,000-character LinkedIn limit. No LinkedIn post was published.
* Threads was disabled in yas.ooo's active social cadence (`postsPerDay: 0`), so the scheduler correctly created no Threads slot or publication attempt today.
* Both Blog Core PM2 processes were online during the check. No credentials, cadence settings, drafts, or public posts were changed while diagnosing the incident.

## 2026-09-02 — Recover LinkedIn overflow slots and make future hero images article-specific

* LinkedIn overflow is now handled as a text-only factual rewrite. When an initial draft exceeds 3,000 characters, Blog Core requests a bounded rewrite, revalidates its length and safety, then continues the same publication flow. It never truncates sentences or regenerates media.
* Recovered yas.ooo's missed 2026-09-02 LinkedIn delivery: the replacement draft was 2,635 characters and the Posts API accepted it. The existing article hero image was retained; no image-generation request was made.
* Hero visual planning now requires a concrete, article-specific scene (subject, action, environment and evidence objects) and explicitly rejects generic stock-office compositions. New hero prompts require a bright, readable article-title treatment; body illustrations remain text-free.
* Compiled `app.py` and `scheduler.py` on production, restarted `blog-yas-core` and `blog-yas-core-scheduler`, and confirmed the health endpoint returned `ok`.

## 2026-09-02 — Published article-specific YAS hero validation draft

* Published `Startup Portal vs No-Code Stack` at `https://yas.ooo/blog/startup-portal-vs-no-code-stack/` after retaining its validated 1,571-word English draft and four completed article assets. The non-English localization tail was stopped; yas.ooo has an English-only publication contract for this job.
* Set this job's `minimumWordCount` quality requirement to 1,000 words at the user's direction. The completed draft exceeds both the new threshold and the prior 1,200-word default.
* Visually checked the generated hero: it depicts the article-specific comparison between a unified portal core and a fragile modular stack, and renders the article title as a readable high-contrast headline. It is not a generic office/dashboard visual.
* Created a 2,316-character LinkedIn draft using the published article and its existing hero. The LinkedIn draft remains `DRAFT`; it was not sent during this verification.

## 2026-09-02 — Restored the established LinkedIn 16:9 image treatment

* Reverted an incorrect experimental LinkedIn crop change before it was used to publish any post. The production LinkedIn asset is restored from the saved working version: 1200×675 (16:9), with the existing centred-crop behavior.
* The application and scheduler compile successfully; Blog Core restarted cleanly and `/health` returned `ok`.
## 2026-09-05 — Defined SoloCruz viral short-Reel direction

* Replaced explanation-first and fear-based SoloCruz Reel concepts with six 10-second, joy-led viral concepts. The creative premise is a compatible companion to share the cruise experience with; cost sharing is a payoff rather than the opening subject.
* Prepared production prompts for vertical photorealistic footage with a universal no-generated-text/no-logo constraint, preserving exact editorial hooks for deterministic overlay.
* Corrected the execution direction: SoloCruz Reels are spontaneous iPhone UGC rather than cinematic or commercial footage, with a brief warm conversational female voiceover.
* Refined audio direction: conversational dialogue may come from the on-camera heroines when it strengthens the scene; voiceover is reserved for inward or emotional beats.
* No media was generated, no social draft was changed, and nothing was scheduled or published.

## 2026-09-05 — Generated SoloCruz iPhone-UGC Omni review batch

* Added `generate_solocruz_ugc_omni_batch.py`, a review-only six-item Omni generator. It creates start/end boundary frames, sends one 10-second iPhone-UGC clip per idea with native speech, and preserves all exact overlay copy outside generated pixels.
* Generated all six requested SoloCruz Reels using `gemini-omni-1.1-flash` and `Kore`: `not-a-tinder-date`, `best-upgrade`, `survive-one-cabin`, `shared-reaction`, `cruise-person`, and `two-main-characters`. The first attempt for `survive-one-cabin` received a provider HTTP 500; its single retry succeeded. No quota-limit failure occurred.
* Verified every output as a 10.005-second vertical 720×1280 H.264/AAC file. Mirrored the review MP4s through Blog Core's noindex social-asset route for owner viewing.
* No social-post row, schedule, or publication was created.
## 2026-09-06 — Corrected diagnosis of failed yas.ooo X publications

* Verified the live yas.ooo X queue on Blog Core site `12`: five due items from 2026-09-02 through 2026-09-06 were released by the factory on schedule and all five failed at Zernio submission with `HTTP Error 403: Forbidden`; no X post was published.
* Superseded the initial shared-key diagnosis. YAS successfully submitted a Threads post through Zernio with the same server-side key after the latest X failure, so the key is accepted for publication and cannot explain an X-only 403. LinkedIn remains the only direct YAS publisher; the other YAS social destinations use Zernio.
* Confirmed the configured X account mapping is present and all five attached image URLs return public HTTP 200. Zernio's read-only activity log gives the exact stable error `account_disconnected`: X account `YASflows` is disconnected because its platform token expired or was revoked. Zernio requires reconnecting that X account and then refreshing its account ID from `GET /v1/accounts`.
* No credential, queue item, cadence, code, or public post was changed during diagnosis. Failed X work items remain `ERROR` and are not automatically retried by the current scheduler.
## 2026-09-06 — Reconnected YAS X and recovered five missed publications

* Verified that Zernio reports the reauthorized `YASflows` X account as active; its account ID remained unchanged, so no Blog Core mapping edit was required.
* Immediately resubmitted the five due X work items that had failed from 2026-09-02 through 2026-09-06. Zernio accepted all five, returned five distinct public X URLs, and reconciliation confirmed both `social_work_items` and `social_posts` as `PUBLISHED`.
* Left the 43 future scheduled X items unchanged. Created the recoverable production database snapshot `backups/blog_core-before-yas-x-recovery-20260906-200913.sqlite3` before queue-state changes.
## 2026-09-06 — Diagnosed missing images on recovered YAS X threads

* Verified that Blog Core and Zernio received one public JPEG for each of the five recovered X publications and that Zernio reported `media_count: 1` for every successful delivery.
* Four recovered publications were multi-tweet threads. Blog Core incorrectly sent their image only in top-level `mediaItems`; when `platformSpecificData.threadItems` is present, Zernio publishes only the per-item content/media and requires the image under `threadItems[0].mediaItems`. The sole single-tweet publication correctly used the top-level image and therefore displayed it.
* No published X post was deleted, edited, or reposted during diagnosis. Existing X media cannot be added through Zernio's text-only edit operation; correcting those four publications requires an explicit delete/repost decision.
## 2026-09-06 — Fix X thread cover placement

* Updated the universal Zernio request builder so media for any `threadItems` sequence is attached to the root item (`threadItems[0].mediaItems`). Ordinary single-post media remains top-level.
* Deployed the change to `/var/www/blog.yas.ooo/app.py`, compiled the application and scheduler, passed isolated single-post/thread payload assertions, restarted both Blog Core PM2 processes, and confirmed `/health` returns `ok` with both processes online.
* Did not delete or republish the five existing X publications. Server recovery copy: `backups/app.py.before-x-thread-media-20260906-201600`.

## 2026-09-06 — Natural social writing contract and corrected YAS X recovery

### Summary

* Added a shared natural-writing contract directly to the active generic, Facebook, Reddit, X, evidence-X and discovery generation prompts. The model is now explicitly instructed not to write long dashes, smart typography, Markdown emphasis, canned AI phrases, formulaic reversals, generic `PROBLEM`/`SOLUTION` headings, fake quotations, vague hype or generic engagement bait.
* Added a final publication-boundary normalization for all social text and every X thread item. If forbidden typography still appears, Blog Core converts it to plain social copy before the provider request. X weighted length is revalidated after this normalization.
* Kept the existing images and corrected X thread delivery so each thread cover is attached to its first tweet. No image was regenerated.
* Rewrote and republished the five YAS X items the owner had deleted. A shell-escaping defect damaged the monetary values in the first Notion and Gusto recovery attempt; those two complete threads were immediately unpublished and recreated with the verified `$3.8k-$4.5k` and `$1.9k-$2.3k` text.

### Verification

* Compiled `app.py` and `scheduler.py` locally and in production, restarted `blog-yas-core` and `blog-yas-core-scheduler`, and confirmed `/health` is healthy.
* Zernio reports all five final X publications as `published`, with exactly one image on the root item of each multi-tweet thread and one image on the standalone post.
* Verified every final tweet item is within X's weighted 280-character limit and contains none of `—`, `–`, `→`, smart quotes, Markdown asterisks or the accidental escaped-number sequence.
* Production recovery database: `backups/blog_core-before-corrected-x-repost-20260906-203100.sqlite3`. Deployment recovery copies: `backups/app.py.before-social-natural-writing-20260906-203000` and `backups/app.py.before-social-writing-contract-20260906-203500`.

## 2026-09-06 — Replace SoloCruz episode 2 with the unsold-cabin premise

* Superseded in part later the same day: the bag, pillow clue and Marcus inspection described below were removed in favor of the simpler restaurant bridge documented in the next entry.
* Replaced row 2 on `Episodes 02-24 Detailed` in the existing SoloCruz Google Sheet. The former guest-expert, presenter, microphone and theatre reveal was removed.
* Episode 2 is now `Пустая на бумаге`: security identifies the referenced cabin as registered empty, Cruz uses a five-minute window to perform a practiced exit, and Marcus finds the remaining pillow indentation after arriving seconds late.
* Replaced the title, hook, retention summary, comment prompt and all three 10-second production prompts in `C2:J2`. Preserved the existing row formatting, sheet structure, neighboring episodes, pilot and media-generation state.
* Each prompt binds the exact prior frame and character/set references, keeps the original cabin and single door, sequences every object and hand action, separates the two legitimate door operations with an explicit time cut, and prohibits added doors, characters, narration or generated text.
* Verified the saved values through the Sheets API and visually in the native Google Sheets UI. No video was generated and nothing was published.

## 2026-09-06 — Simplify SoloCruz episode 2 exit into the Nina restaurant bridge

* Replaced only the second and third production prompts of episode 2 in `Episodes 02-24 Detailed!I2:J2`.
* Removed the bag-packing, pillow clue, master-key return and Marcus cabin inspection. Cruz now leaves all belongings in the cabin, exits only after security has gone, and temporarily waits out the inspection in the restaurant.
* The final fragment now introduces Nina naturally: Cruz asks to sit for five minutes, says she doubts they will check the restaurant, and Nina asks who she is avoiding. This creates a direct continuity bridge into episode 3.
* Preserved the first fragment, spreadsheet formatting, neighboring rows and all other prompts. Verified the saved values through the Sheets API and the native Google Sheets UI. No video was generated or published.

## 2026-09-06 — Remove an accidental third-party name collision from SoloCruz episode 2 prompt 3

* Inspected the failed Flow card for episode 2 fragment 3. Flow returned its third-party content-provider restriction rather than the earlier known-person warning; the same project successfully generated the first two episode fragments.
* The rejected prompt repeatedly placed the fictional names `Nina` and `Cruz` in the same text, which can be interpreted as the existing name `Nina Cruz`. Replaced names only inside the production directions with reference-bound role labels (`главный персонаж` and `второй персонаж`).
* Preserved the two characters, attached-reference contract, restaurant action, all three spoken lines and physical continuity. Updated only `Episodes 02-24 Detailed!J2`, retained its formatting, and verified the saved value through the Sheets API and native Sheets UI.
* No replacement video was generated; the mitigation still requires one Flow generation to confirm that this was the provider classifier trigger.

## 2026-09-07 — Align SoloCruz episode 2 ending with the existing episode 3 opening

* Replaced only `Episodes 02-24 Detailed!J2`; episode 3 and every other cell remain unchanged.
* Removed Nina, her table and the premature conversation from episode 2. The third fragment now ends with Cruz entering the restaurant, saying she expects not to be checked there, noticing the same two security characters entering behind her, and disappearing deeper into the dining room while they scan it.
* Preserved episode 3's actual opening: Nina begins alone by hiding the second place setting, and Cruz reaches her only during that episode's third shot at second six.
* Kept all character names out of the revised generation directions to avoid the earlier provider-name collision. No video was generated or published.

## 2026-09-07 — Rotate the production Gemini API key

* Replaced the primary `GEMINI_API_KEY` only in the protected production environment at `/var/www/blog.yas.ooo/.env`; no secret value was written to source code, documentation, logs, or the local workspace.
* Created a mode-0600 recovery copy under the production `backups/` directory before changing the environment.
* Verified the rotated credential directly against the Gemini models endpoint: authentication returned HTTP 200 with an available model result.
* Restarted `blog-yas-core` and `blog-yas-core-scheduler` with refreshed environment values. Both PM2 processes are online and the Blog Core health endpoint returns `ok`.

## 2026-09-07 — Add durable email alerts for failed queued publications

* Added `publication_failure_email_alerts`, a durable outbox for failures from website, social, shared-carousel, Instagram Reel, TikTok carousel, evidence-X, Threads, and Facebook publication workers.
* Added stable event fingerprints to prevent duplicate alerts, while failed mail delivery retries with exponential backoff capped at one hour.
* Reused SoloCruz's proven local `/usr/sbin/sendmail` to Exim delivery path. Recipient and optional sender are protected environment settings; no mail credential is stored in source or SQLite.
* Added asynchronous Zernio failure capture during provider reconciliation and excluded waiting/no-source states from alerts.
* Passed Python compile validation and an isolated production-runtime test covering event capture, duplicate suppression, successful delivery state, and attempt accounting.
* Deployed `app.py` and `scheduler.py`, initialized the outbox schema, restarted both Blog Core PM2 processes, and verified the health endpoint plus matching production source hashes. Delivery remains intentionally disabled until `PUBLICATION_ALERT_EMAIL_TO` is set.
* The first production reconciliation captured two distinct SoloCruz Facebook provider failures as pending alerts. They were not duplicated on later scheduler passes and will be delivered after the recipient is configured.
* Configured the protected production recipient as `info@yas.ooo` and successfully delivered both pending alerts through the existing local Exim transport.
* Diagnosed both Facebook failures from Zernio's destination-level records: Facebook requires the Page owner to complete identity confirmation in the Facebook mobile app before publishing as SoloCruz. The mapped Page account remains active; the rejection occurred at the platform gate before a publish attempt.
* Extended reconciliation error extraction to preserve Zernio's destination-level `errorMessage`, so future emails contain Facebook's exact actionable reason instead of the generic failed status.
* Corrected the alert fingerprint after exact error enrichment caused the same two already-sent Facebook failures to be emailed a second time. The fingerprint now uses the durable queue record/slot identity and excludes mutable error wording; anonymous worker failures alone use their message as a fallback identity.

## 2026-09-08 — Diagnose blocked NOMADeira native publication

* Traced the alert to NOMADeira job `8b67f5810fa19fd0be505ce7`, `EU Residence Registration in Madeira: Steps and Verification`, due at 09:00 Europe/Warsaw.
* Verified that generation and all three configured localizations completed, but the legacy `nomadeira_editorial_plan` source record has no `pageBrief`, no `complianceCluster`, and still states `generationBlockedUntilSourceReview=true`.
* Identified a contract-version gap: compliance generation and schedule eligibility recognize `complianceCluster`, while this older queue format carries only legacy blocking flags. The strict typed native publisher therefore correctly refused to publish the unreviewed guide.
* Found seven additional NOMADeira editorial-plan rows scheduled from 9 through 15 September with the same missing contract. No schedule, draft, approval or publication state was changed during this diagnosis.

## 2026-09-08 — Migrate eight scheduled NOMADeira rows to the current evidence contract

* Added the idempotent `deploy/migrate_nomadeira_scheduled_editorial_plan.py` migration for exactly the eight affected unpublished routes; it refuses missing or published targets and defaults to a read-only plan unless `--apply` is explicit.
* Migrated all eight production rows to private `BLOCKED_EVIDENCE`, removed their 8–15 September schedules, cleared active pre-review draft/hero/FAQ/localization state, and retained only an audit summary that an invalid pre-compliance artifact had existed. No source, verified claim, review, approval or QA state was invented.
* Marked the EU residence route `CANONICAL_REVIEW_REQUIRED` because it may overlap the existing Phase-A CRUE guide. The other seven rows are `CANONICAL_CHECKED` and await source collection.
* Updated the universal compliance gates so legacy `generationBlockedUntilSourceReview` and `publicationBlocked` flags remain authoritative even without `complianceCluster`. This closes the format-version hole that allowed the scheduled row to generate.
* Preserved a production SQLite recovery snapshot, the prior application file and the four removed active image assets under the protected production `backups/` directory.
* Passed Python compilation, a full migration against a temporary production database copy, repeat-run idempotency, generation/schedule guard assertions, production row/localization validation, PM2 restart checks and the Blog Core health endpoint.

## 2026-09-08 — Preserve the established LinkedIn hero pipeline and task scope

* Recorded the operator rule that implementation must not broaden the requested task or redesign working behavior without an explicit request.
* Reverted the unrequested LinkedIn hero composition experiment. Dedicated LinkedIn heroes again use the established 16:9 Gemini generation, 55–60% centred headline block and existing 1065×795 crop.
* Retained only the scoped safeguard that a LinkedIn draft without its dedicated reviewed hero cannot silently fall back to the article hero.
* Re-generated the missing dedicated hero for YAS LinkedIn post `209` through that restored pipeline. The exact 1065×795 result is stored on the draft with headline `Portal Or No Code`; the deleted publication was not recreated and the draft has no schedule or remote URL.
* Verified that no other active YAS LinkedIn draft or queued item lacks a dedicated LinkedIn hero. Historical publications and drafts belonging to other sites were not changed.
* After explicit operator approval of the corrected `Portal Or No Code` cover, published YAS LinkedIn post `209` immediately through the direct LinkedIn Posts API. LinkedIn accepted it; the local post and content job are `SENT` with no publication error.

## 2026-09-11 — Remove contradictory and duplicated LinkedIn hero instructions

* Simplified only the dedicated LinkedIn image prompt. The image model now receives one dynamic string, `COVER HEADLINE`; the complete article title is used only by the preceding headline-writing step and is no longer exposed to image generation.
* Removed the shared article-photo direction from the LinkedIn prompt because its `never graphic design` instruction contradicted the requested glossy magazine-cover typography and its human-scale scene language biased unrelated covers toward generic people and offices.
* Removed repeated large-headline and negative-list wording while retaining the existing 16:9 generation, exact headline-once rule, bright editorial typography with drop shadow, 55–60% centred text block, safe margins, and final 1065×795 crop.
* Deployed the scoped prompt change without altering later production Gemini failover or SoloCruz short-video work. Compiled the application and scheduler, verified the actual generated prompt contract without an image request, restarted both PM2 services, and confirmed a healthy production endpoint.

## 2026-09-12 — Verify My UGC Studio LinkedIn application identity

* Confirmed that the LinkedIn connection stored for My UGC Studio uses the intended application Client ID and has both an access token and client secret.
* Confirmed that the token was issued only with the deployed member-publishing OAuth flow and stores `Iaroslav Olencovschi` as a personal author. No Company Page organization identity is selected, and no My UGC Studio LinkedIn post has been created or published through Blog Core.
* No connection, scope, token, publishing identity or queue state was changed during this verification.
* Confirmed from the application's available OAuth scope inventory that the required Company Page permissions are available: `rw_organization_admin` for organization discovery and `w_organization_social` for publishing. The deployed OAuth request still omits both.

## 2026-09-12 — Connect My UGC Studio as a LinkedIn organization

* Added Blog Core's callback URL to the LinkedIn application's authorized redirect list while preserving the existing My UGC callback.
* Updated the OAuth request to use the application's available `r_basicprofile`, `w_member_social`, `rw_organization_admin`, and `w_organization_social` scopes. Replaced the OpenID `/v2/userinfo` dependency with `/v2/me` for both callback identity resolution and connection testing.
* Replaced process-local OAuth state with a 10-minute Secure, HttpOnly, SameSite=Lax callback cookie so callbacks remain valid across the two production Gunicorn workers.
* Corrected organization discovery by removing the invalid ACL projection and resolving each administered organization's display name through the supported organization lookup endpoint.
* Reconnected site `6`, selected the exact `My UGC Studio` organization (`urn:li:organization:110609498`) rather than `My UGC Studiio`, and verified the selected Company Page role through the live LinkedIn API. No LinkedIn post was created.
* Compiled the production application and scheduler, restarted both PM2 services, and confirmed the health endpoint after deployment.

## 2026-09-12 — Allow imported articles in the LinkedIn source queue

* Updated the automatic LinkedIn source selector to accept both `IMPORTED` and `PUBLISHED` content jobs, including already-created LinkedIn drafts attached to either status.
* Kept the change scoped to LinkedIn; Facebook and every other automatic social channel retain their published-only selection behavior.
* Required imported sources to have a live URL and excluded localized blog-index URLs ending at the configured blog path, preventing catalog pages from becoming posts.
* Verified the production selection against My UGC Studio: 450 article records are LinkedIn-eligible, five localized blog indexes are excluded, and Facebook still sees only the seven `PUBLISHED` rows.
* Compiled and deployed the current production application, restarted both Blog Core PM2 services, and confirmed the health endpoint. My UGC Studio autopublishing was not enabled and no social draft or publication was created.

## 2026-09-12 — Connect Karp and Veselova Veronika to independent native blogs

* Added an optional `sites.content_root_path` so a native site's code root and persistent data/media root can remain separate. Existing native sites retain the prior `<root_path>/data/blog-core` fallback.
* Reconfigured Karp site `17` to `/var/www/karp-preview` plus `/var/lib/karp-preview/data`, and Veronika site `19` to `/var/www/veronika-preview` plus `/var/lib/veronika-preview/data`. Both are independent RU/EN `native_content_store` factories.
* Updated post-publication warming to target the isolated artifact processes on ports `3045` and `3055` instead of the former shared Build YAS port.
* Added native JSON consumers to both source applications. They preserve each site's existing blog chrome and card styles, add localized article routes, and expose noindexed native draft previews.
* Extended both native sitemaps from the same published-record source; draft records remain excluded.
* Verified both renderer builds (Veronika with full TypeScript validation; Karp's new code compiled while its pre-existing repository-wide type debt required a one-build-only type-check bypass), restarted only the two artifact processes, checked all six RU/EN public test routes and both private previews, then removed the temporary records and confirmed their routes returned 404.

## 2026-09-12 — Keep a visible Karp native-blog verification article

* Corrected the mistaken removal of the native-blog verification content after the renderer check.
* Activated the existing Karp blog-card topic `Как выбрать новостройку в Казани` as a persistent RU/EN native article, with its localized routes present in the blog listing and sitemap.
* Verification content requested for operator review must remain available until the operator explicitly asks to remove it.

## 2026-09-12 — Preserve non-Latin article copy during deduplication

* Fixed the structured-article deduplicator so its comparison key supports Unicode letters instead of only ASCII `a-z`.
* The former expression reduced every Cyrillic paragraph and ordered-list item to an empty key, silently deleting the full Russian body before validation and making otherwise complete drafts appear to contain only about 460 words.
* Added a focused Cyrillic duplicate/non-duplicate verification before deploying the fix and rebuilding the Karp article.

## 2026-09-12 — Replace the Karp fixture with a complete native article

* Replaced the five-block placeholder at `/blog/kak-vybrat-novostroyku-v-kazani` with a validated 1,650-word native publication containing eight sections, a comparison table, seven-step checklist, three inline images, six FAQ entries and three contextual internal links.
* Generated a dedicated hero and three paragraph-bound editorial images, created the English localization, and published the result atomically through Blog Core's native content-store lifecycle.
* Updated Karp's listing materializer to replace an existing same-title placeholder card in place instead of prepending a duplicate. The live RU blog now has one linked card for the article.

## 2026-09-12 — Bring Karp native articles to the site's editorial standard

* Reworked only Karp's native-article presentation layer, preserving article copy, media, routes and publication state.
* Added a premium dark editorial system for the contents panel, paragraph rhythm, figures, contextual links, comparison tables, numbered checklist cards, pull quote and accessible FAQ accordions using Karp's existing serif typography and gold accent.
* Added responsive behavior: the contents and checklist collapse to one column, the comparison table scrolls with a sticky first column, and FAQ controls retain touch-sized targets.
* Browser QA confirmed the desktop table, checklist, quote, closed FAQ state and expanded FAQ answer. The temporary one-build TypeScript bypass was removed after compilation.

## 2026-09-12 — Repair the Karp blog-index card regression

* Repaired the native article card on `/blog` after the materializer had cloned a runtime property card and then changed Karp's tag-sensitive `span.blog-list__item` wrapper into an anchor.
* The materializer now preserves the original blog-card wrapper and native classes, updates the matching placeholder in place, and adds a full-card overlay link without changing the page's grid or authored structure.
* Added card-scoped block spacing for the populated publication date so imported titles, dates and descriptions remain visually distinct.
* Rebuilt and restarted only `karp-preview-artifact`; desktop browser QA confirmed the three-column grid, separated title/date/description, loaded card images and successful navigation to the native article.

## 2026-09-12 — Complete Veronika's first native Blog Core article

* Published the existing card topic `Как сформировать техническое задание на частный дом` as a complete 1,451-word RU and 1,551-word EN native article with eight sections, three contextual images, a comparison table, seven-step checklist, pull quote, contents navigation and six FAQ entries.
* Reused Veronika's existing approved house, briefing, location and engineering media; no new or unrelated imagery was generated.
* Reworked the native article presentation around Veronika's approved single maroon `#6b1730`, white serif typography, translucent panels and rose accents. No second solid maroon was introduced.
* Fixed Veronika's listing materializer using the same safe contract as Karp: preserve the authored `span.blog-list__item`, replace the matching placeholder in place, separate the populated date, and add an inner full-card link.
* Full TypeScript/build validation passed. Restarted only `veronika-preview-artifact`; verified RU/EN routes, all four media URLs, sitemap entries, listing-card navigation, contents, article structure and FAQ expansion in the browser.

## 2026-09-12 — Diagnose Veronika's shared contact-section layout defect

* Confirmed the defect is global because every route reuses section `section-23fb0b03-fe4a-4fb1-8474-2f76b5d59948` and the same server materializer.
* The three social controls are appended to the full `.lp-container`, then styled as an `83.34%` centered row. That ignores the portrait composition's left negative-space column and places the row across Veronika's body.
* The faulty rule is present in the pre-article runtime backup, so the native Blog Core article CSS did not create this layout. No visual fix was applied during this diagnosis.

## 2026-09-12 — Center Veronika's shared contact section on every route

* Replaced the split desktop composition with one centered group containing the title, primary CTA and Telegram/WhatsApp/Instagram controls, and moved that group below the section midpoint as requested.
* Preserved the contact photograph, authored 850px desktop/tablet section height and existing mobile bottom-centered layout. The first implementation exposed that absolute positioning collapses the source section unless its height is explicitly retained; the final rule includes that invariant.
* Bumped the Veronika contact artifact presentation version, rebuilt and restarted only `veronika-preview-artifact`, then warmed every unique sitemap route so public pages no longer fall back to stale HTML.
* The focused contact-materialization test and full production TypeScript build pass. Browser QA confirmed identical centered geometry on `/` and `/blog`; a route audit found no non-200 or non-`HIT` artifacts.

## 2026-09-12 — Match Veronika's mobile contact CTA to the hero CTA

* Removed the mobile contact CTA's forced full-width, 80px-high geometry only for Veronika's shared contact section.
* The CTA now uses the Home hero button contract: intrinsic width, 59.2px rendered height and `22px 50px` padding. Its width is slightly larger than the hero CTA only because `Написать Веронике` is a longer label.
* Preserved the contact image, heading, messenger controls, desktop layout and Karp tenant. Focused tests and the full production build pass; browser QA at `390×844` confirmed the compact button.
* Bumped the shared Veronika contact presentation version, warmed every unique sitemap route and verified that all public artifacts return HTTP 200 `HIT`.

## 2026-09-11 — Diagnose recurring LinkedIn hero generation defects

* Verified that production uses `gemini-3.1-flash-image` and that no LinkedIn image generation is currently pending.
* Inspected the deployed LinkedIn hero prompt and identified direct conflicts and accumulated instruction noise: magazine-cover typography versus `never ... graphic design`, two separate title strings, human-subject bias from shared article-photo direction, central-scene exclusions, and repeated `large` wording competing with the single numeric width constraint.
* No prompt, model, crop, queue or publication state was changed during this diagnosis.

## 2026-09-12 — Create a complete Blog Core repository checkpoint

* Prepared one full source checkpoint containing all current tracked modifications/deletions plus the accumulated untracked application modules, operational scripts, deployment units and canonical documentation.
* Kept runtime secrets, environment backups, databases, core dumps, generated media, temporary work directories, historical source snapshots and backup files outside Git; expanded `.gitignore` so those unsafe artifacts do not reappear in future status checks.
* The checkpoint records repository state only. It does not publish content, modify queues, restart services or push to the remote repository.
## 2026-09-12 — Add direct Telegram photo-post publishing to Blog Core

### Summary
* Completed the existing article-to-Telegram draft contour with direct Bot API delivery; Zernio is not involved.
* Telegram drafts now generate a dedicated 16:9 editorial JPEG and a caption capped to the native 1,024-character photo-caption limit.
* Added publish-time recovery for legacy overlong Telegram drafts: rewrite and revalidate the caption while retaining the existing generated image.
* Added factory-owned automatic cadence delivery and a manual `Publish Telegram` action for reviewed drafts.
* Added Telegram media to the shared social review page and records the returned message ID/public channel URL in the social and content-job status fields.
* Allowed Telegram to use both `PUBLISHED` and real live `IMPORTED` article sources, which is required for the imported `yas.wine` catalogue; imported blog-index rows remain excluded.
* Migrated the existing site-scoped bot/channel credentials for `yas.wine` and `myugc.studio` from their legacy factories and verified both connections through Telegram without publishing a post. Automatic Telegram cadence remains off for both sites.

### Checks run
* Compiled the deployed application and scheduler, restarted both PM2 services, and verified the Blog Core health endpoint.
* Exercised direct `sendPhoto` request construction against an isolated database with a stubbed Telegram response, including generated image URL, caption, inline article button and persisted public message URL.
* Exercised a due automatic Telegram slot against an isolated `IMPORTED` article and verified that it generated the Telegram draft and selected the direct bot publisher rather than Zernio.
* Built the real Telegram prompt for one `yas.wine` imported article and one `myugc.studio` published article; both use the 1,024-character photo-caption contract. Live `getMe` and `getChat` checks passed for both migrated connections.

### Files changed
* `app.py` — direct `sendPhoto` publisher, scheduling, manual API/UI action, Telegram review image and native caption limit.
* `docs/PROJECT_MEMORY.md` — durable direct-bot architecture and queue contract.
* `docs/INTEGRATIONS.md` — current transport and platform-limit documentation.
* `docs/CHANGELOG_AI.md` — implementation record.
