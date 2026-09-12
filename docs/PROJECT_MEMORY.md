## 2026-09-12 — Personal-brand monthly media plans are separate noindex client calendars

* Aleksei Karp and Veronika Veselova each have a separate site-scoped client calendar at `/media-plan` on their own domain. The route is server-rendered by Blog Core through an exact Nginx proxy and must remain excluded from sitemaps, uncached, and protected by both a robots meta tag and `X-Robots-Tag: noindex, nofollow, noarchive`.
* The Google Sheet `KARP ALEXEI + VERONIKA — план и стоимость` is historical planning context only. It is not the authoritative calendar and must not be edited or treated as a production contract.
* One stored calendar row represents one source material or one human assignment. Cross-platform material is rendered as a separate destination card for every publication: an Instagram+TikTok carousel becomes two cards, and one live Reel becomes separate Instagram Reels, TikTok and YouTube Shorts cards. It includes a Warsaw publication timestamp, production/recording deadline, platform, format, status, campaign relationship and an executable brief. Aleksei and Veronika plans and statuses never mix. Factory rows expose the actual planned content/meaning to the client; only owner-recorded rows are presented as assignments.
* Factory-owned work covers website articles, one-render Instagram+TikTok carousels, Telegram photo posts and Threads. Live Reels are the only owner-executed format: the named owner records and publishes them personally. Spontaneous owner posts may coexist with the plan and do not cancel planned factory work.
* Owner Reel reminders use the site-scoped Telegram bot plus a separate private `reminder_chat_id`; the public Telegram channel destination is never used as an implicit personal recipient. Reminder events are uniquely persisted to prevent duplicates.
* The first materialized month is October 2026: 90 source records and 165 visible destination cards per person, including 15 articles, 15 shared Instagram+TikTok carousels (30 destination cards), 15 Telegram posts, 15 Threads posts and 30 live Reels (90 destination cards across Instagram, TikTok and YouTube Shorts). The 30 Reels are unique and distributed evenly across ten formats: lifestyle, property review, lifehack, expert advice, myth check, A/B choice, behind the scenes, one important detail, common question and personal rule. These are planning records, not proof that disconnected channels are ready to publish.
* The header start-date control persistently shifts the complete selected plan batch, including publication timestamps, production/recording deadlines and future unsent Telegram reminder events. If the shifted 30-day range crosses a month boundary, every covered month is rendered. This is not a display-only offset.
* Public client status vocabulary is deliberately short: `В плане`, `Готово`, `Ошибка`, `Просрочено`. Completed cards are visually faded like disabled items but remain openable for details; errors use a bright red contour and shadow; overdue cards use a blinking orange contour and shadow. `Просрочено` is derived when the publication time has passed without a completed state. Personal live Reels have a one-way `Отметить готово` action; it advances the shared source row to `READY`, updates all three destination cards together, and cannot be cancelled from the client calendar.
* Calendar dots preserve destination and format identity separately: article, Instagram carousel, TikTok carousel, Instagram Reel, TikTok video, YouTube Short, Telegram and Threads. Summary counts must also keep Instagram Reels separate from Instagram carousels and TikTok Reels separate from TikTok carousels; every counter shows `completed/total`, while platform filters may remain destination-wide. Future Instagram/TikTok Stories and ordinary posts retain their own labels, counters and dot identities rather than collapsing into a platform-only bucket. Karp calendar chrome uses the native black/ivory/bronze palette; Veronika uses the native maroon/cream/rose palette. Social publication cards retain their platform colours.
* Each media-plan hero uses the site's real native logo asset, a natural-language date range and a top-right start-date selector on desktop. Do not create substitute logo marks or reintroduce a redundant month badge above the date input.
* The client page is date-led: every active calendar day links to its own anchored date section, each section contains square platform-coloured cards, and every card carries an inline platform SVG logo and opens an accessible native dialog with full content or recording instructions. Execution badges are deliberately distinct: `Готовит фабрика` has a static white outline, while `Снять лично` has a luminous outlined pulse. Filtering may hide cards and empty date sections but must not alter their stored schedule.

## 2026-09-02 — EPR Scan crosslinks must be visible in reading context

* A stored `internalLinks` array is not sufficient by itself. EPR Scan matches those declared targets to their semantic in-body paragraphs and renders each match as a visible contextual reading card beside the relevant section.
* Crosslink matching normalizes the supported `/de`, `/fr` and `/es` path prefixes, while retaining the localized paragraph and anchor text. The renderer must not replace translated copy with English interface labels.
* A single `recommendedNext` action renders as a compact high-contrast CTA, not as an oversized two-column panel with an empty half. Contextual reading links and the conversion CTA remain visually distinct.
* Every declared contextual target and CTA must return HTTP 200 before the article presentation is accepted.

## 2026-09-02 — EPR Scan articles use a native editorial component system

* Blog Core article HTML remains semantic content, while EPR Scan owns its visual presentation. Generated article blocks must render through the site's native cream/ink/green editorial system rather than browser-default styles.
* The article contract includes a numbered contents panel, bounded readable text measure, styled figures/captions, a structured desktop data table, locale-derived labelled table cards on phones, numbered workflow steps, a high-contrast quotation, a recommended-next card and accessible FAQ accordions.
* An English draft preview shows only meaningful available metadata such as author and reading time. It must not expose empty reviewer, last-reviewed or ruleset fields as `Pending`; the draft banner already communicates its workflow status.
* FAQ controls use native `details`/`summary`, visible plus/minus affordances, keyboard focus and at least 44px interaction height. Evidence links and secondary text must meet WCAG AA contrast.

## 2026-09-02 — EPR Scan first English review draft precedes localization (completed)

* Superseded state: the first roadmap item began as the English-only draft `When does the PPWR apply to ecommerce sellers?` (`content job 5c9fda97f3ca8c064871e6a6`). It is now published with DE/FR/ES localizations after approval and source audit.
* The approval sequence is English generation and visual/editorial review first. Only after explicit approval may Blog Core translate the accepted English source in one batch to German, French and Spanish. Russian and Italian remain excluded locales.
* EPR Scan renders review drafts at `/content-preview/{jobId}` in its native design. Draft previews are private workflow surfaces with `noindex`, `no-store`, no sitemap membership and an explicit unpublished-draft banner; they must never be treated as publication.
* Draft and published article media are copied into EPR Scan-owned `/images/blog-core/{jobId}/` paths during sync so the native self-only image CSP remains intact.

## 2026-08-31 — Social prompt templates and scheduler imports are release gates

* JSON examples embedded in Python f-strings must escape every literal object brace. Compile-only validation is insufficient: release checks must call each active social prompt builder with a real site/job row so formatting errors surface before the daily slot.
* `scheduler.py` may import only workers that exist in the deployed `app.py`. Restarting both PM2 processes is a required release check because a long-lived scheduler can conceal an app/scheduler mismatch until its next restart.
* A restored social schedule is verified end to end: generate a new native creative, submit it through the configured provider, confirm the provider returns a remote ID, and keep the public review URL available.

## 2026-09-03 — Reddit scheduling belongs exclusively to Blog Core

* Blog Core is the sole owner of a Reddit draft's queue state and due timestamp. Zernio is a delivery adapter only: it receives a Reddit draft with `publishNow` when Blog Core's local queue releases that reviewed item.
* A Zernio `scheduledFor` request that includes a Reddit draft is rejected. This prevents a second, provider-owned calendar from bypassing factory queue controls or making cancellation opaque.
* Replaced: the 2026-09-01 finite YAS Reddit schedule that was materialized directly in Zernio. Six future provider drafts were deleted; the one already published post remains published.

## 2026-09-03 — Threads work queue uses factory-owned daily slots

* Ready Threads work items are materialized as native social drafts and scheduled by Blog Core at 18:00 `Europe/Warsaw`, one per day. Zernio receives an immediate delivery request only after the local due time.
* The generic channel cadence does not consume this queue: its global time window belongs to other channels. A dedicated Threads queue worker prevents a generic article-derived post from competing with reviewed Threads work.

## 2026-09-03 — Facebook Page is a dedicated editorial social contour

* Facebook Page drafts are not generic cross-posts: Blog Core creates a 420–900-character native adaptation with a single canonical article URL, then a separate article-specific 1200×630 magazine-style cover with its own bounded headline.
* Facebook delivery uses the site-scoped Zernio Facebook Page account mapping. No account mapping authorizes no generation or publication; production YAS currently has no such mapping. SoloCruz and Laycanmatch have their respective Facebook Page mappings configured in Blog Core.
* Facebook cover generation starts from a single article-specific Gemini image, then crops/resizes the finished raster to the native 1200×630 (1.91:1) feed surface. This is an image-format derivative only; Blog Core must never add a programmatic text overlay.
* For SoloCruz's 19 published articles, Facebook drafts are factory-owned and scheduled one per day at 18:00 `Europe/Warsaw` from 4 through 22 September 2026. Zernio receives each item only as an immediate due-time delivery.
* For Laycanmatch's 11 published articles, Facebook drafts are factory-owned and scheduled one per day at 18:00 `Europe/Warsaw` from 4 through 14 September 2026. Zernio receives each item only as an immediate due-time delivery.

## 2026-09-03 — Blog Core Gemini runtime configuration

* Blog Core's protected production environment holds the Gemini runtime credentials used by its own text and image generation. Production `run.sh` loads and exports that environment before starting Gunicorn.
* Manual maintenance or batch commands that import `app.py` must first use the same environment-loading sequence. A bare Python shell does not inherit those variables and must never be interpreted as evidence that a key is missing. Credentials remain secret and must never be printed, copied into source code, or recorded here.

## 2026-09-02 — LinkedIn overflow recovery and article-specific hero contract

* A LinkedIn post that exceeds the 3,000-character hard limit must receive a bounded factual rewrite and be revalidated before the same publication attempt continues. It must never be silently skipped or sentence-truncated. Text-only recovery must retain the existing article hero asset.
* New article hero artwork is an article-specific editorial scene, not a reusable stock office image. The image plan must express the article's central decision or practical task through its own subject, action, environment and physical evidence objects.
* The exact article title is the only permitted readable text on a new hero image. It uses a bright, high-contrast editorial treatment with safe margins; body illustrations remain free of text overlays and incidental readable UI/document text.
* Known legacy-queue hazard: LinkedIn draft `209` was created before the dedicated LinkedIn hero payload existed. Its `content_json` had no `linkedin.mediaUrl` or `coverHeadline`, so the publisher fell back to the 1376×768 article hero and then center-cropped it to 1065×795. The article hero carried the full-width article title, which was clipped on both sides. A missing dedicated LinkedIn payload is therefore not a prompt failure and must not be treated as publishable merely because an article hero exists.

## 2026-09-02 — LinkedIn social hero art direction

* The dedicated 16:9 LinkedIn social hero is a photorealistic glossy magazine-cover photograph with a bright, attention-grabbing wow effect. It derives its visual from the article title and renders that title as the only readable text.
* People, offices, desks, meetings, laptops, dashboards, floating UI, handshakes and generic business imagery are not globally prohibited for LinkedIn heroes; the title should determine whether they fit. Do not use the word `cinematic` in this prompt.
* A text step derives a 2–5-word cover headline (maximum 21 characters) from the article title. The image model receives only that `COVER HEADLINE`; the full article title must not appear in the image prompt. The headline determines both the photograph and the sole rendered text. It is centred in a 55–60%-wide glossy magazine-cover block with clear space on each side; every glyph must remain fully inside the frame.
* LinkedIn cover headlines are large, bright, bold magazine-cover typography with a pronounced drop shadow. They require a calm single-tone, softly defocused central field behind the complete text block; no busy visual subject may cross that field. Settings must arise from the visual concept rather than routine desk-work conventions.
* Cover headlines contain only their generated words: quotation marks, apostrophes, brackets, colons, dashes and other punctuation are prohibited in both the text-generation validation and image prompt.
* Replaced: LinkedIn social heroes must not use a 16:9 `1200×675` crop. The native post-card contract is `1065×795` (3× the `355×265` card), using a centred crop without letterboxing after generation.
* LinkedIn hero photography must express one central tension from the title through a single unexpected, physically real magazine-cover scene. It needs one bold visual premise and dominant subject, and must be specific enough that it cannot fit a generic startup, AI, software or consulting article.
* The dedicated LinkedIn hero prompt must not use the genre triggers `business`, `LinkedIn post`, `startup`, `AI`, `software` or `consulting`; they bias Gemini toward stock corporate photography. Use a glossy editorial magazine-cover visual story instead.
* LinkedIn heroes favour present-day photorealistic magazine-feature situations: a familiar location, natural human scale and a tangible consequence of the title's central choice. Avoid futuristic, fantastical, abstract or technologically exaggerated visual directions.
* Article images never render a title or other readable text. Their hero uses its article-specific visual plan; each body image uses only its anchored paragraph and visual brief, not the full article context. The concise LinkedIn cover prompt is separate and must not inherit article-photo restrictions that conflict with magazine-cover typography.

## 2026-09-08 — Do not expand operator tasks or redesign working logic

* Execute the operator's stated scope literally. Do not invent adjacent tasks, broaden the target set, or redesign an already working pipeline unless the operator explicitly asks for that change.
* When the request is to apply an existing working mechanism where it is missing, preserve that mechanism exactly. For LinkedIn heroes this means keeping the established 16:9 generation, 55–60% centred headline block and existing 1065×795 crop; only add the missing dedicated-hero application or publication guard requested.

## 2026-09-11 — Current LinkedIn hero prompt has verified internal conflicts

* The observed LinkedIn hero defects cannot be attributed only to `gemini-3.1-flash-image`. The current prompt combines a magazine cover with a shared direction that explicitly says `never ... graphic design`; asks for a dominant natural-human-scale subject while clearing people and objects from the central headline field; supplies both the full article title and a separate renderable cover headline; and repeats qualitative `large` headline instructions more strongly than the single 55–60% width constraint.
* The shared article-photo direction also biases the model toward a familiar physical location and human subject, which can produce recurring office/person scenes even when the title calls for another visual. This prompt diagnosis is verified from the deployed source. Do not change the prompt or generation mechanics without an explicit operator request.

## 2026-09-12 — My UGC Studio LinkedIn publishes as its organization page

* Replaced: My UGC Studio is no longer connected only as a member. Its site-scoped LinkedIn application now requests `r_basicprofile`, `w_member_social`, `rw_organization_admin`, and `w_organization_social`; the application does not expose OpenID scopes.
* The LinkedIn application has both `https://web.myugc.studio/factory/linkedin/callback` and `https://blog.yas.ooo/oauth/linkedin/callback` registered as authorized redirect URLs.
* OAuth state is carried in a short-lived Secure, HttpOnly, SameSite=Lax callback cookie. Do not return to process-local state storage: production uses multiple Gunicorn workers and an authorization callback can reach a different worker.
* Organization discovery uses the unprojected `/rest/organizationAcls?q=roleAssignee&state=APPROVED` finder, then resolves each eligible organization name through `/rest/organizations/{id}`. The earlier custom ACL projection returned HTTP 400.
* My UGC Studio site `6` is configured to publish as `urn:li:organization:110609498` (`My UGC Studio`), not the similarly named `My UGC Studiio` page. The selected organization role and token were verified through the live LinkedIn API. No post was created during connection.

## 2026-09-12 — LinkedIn may use imported live articles as social sources

* The automatic article-to-LinkedIn worker accepts both `PUBLISHED` and `IMPORTED` content jobs. This expansion is LinkedIn-only; other automatic social channels retain their existing `PUBLISHED` source rule.
* An `IMPORTED` source must have a real `published_url`. Imported localized blog-index pages whose URL ends at the site's configured blog path are excluded because they are listings, not articles.
* Existing LinkedIn drafts attached to an `IMPORTED` article are eligible for their due slot under the same rule. My UGC Studio autopublishing remains disabled until explicitly enabled; changing source eligibility alone must not schedule or publish anything.

## 2026-09-02 — YAS article-length preference

* YAS articles may use a per-job minimum of 1,000 words when the editorial task is complete and validated at that length. Do not pad a concise draft solely to reach the former default of 1,200 words.

## 2026-08-13 — Reel layers use natural shadows and one continuous camera path

* Visible light/white silhouette outlines are deprecated because uneven mattes make them look torn or sticker-like. Registered layers use only a broad soft offset shadow plus a restrained contact shadow for separation from the background.
* Director camera beats are framing destinations on one continuous whole-scene spline, not separate start-stop commands. Camera scale and center move from scene start through every destination and retain continuous velocity, then continue a restrained drift until the cut.
* A Reel scene must not visibly zoom, hold, zoom again, or jump between camera stages. Wide, medium, close, and focus-transfer framing remain useful film grammar, but the transition between them is one uninterrupted movement.

## 2026-08-13 — Reel renders use immutable versioned media URLs

* Every completed Reel render writes a unique timestamped MP4 and poster filename and stores that URL in the social-post payload. Replacing bytes behind a stable Reel URL is deprecated because browser/CDN caches can show an older draft after a successful re-render.
* Reel review HTML and social-asset routes return `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`; the review page also appends the render token as a query parameter.

## 2026-08-13 — Reel typography and cinematic framing follow the final assembled scene

* Reel overlay copy is a 2-to-7-word glanceable headline, rendered as one title rather than paged fragments. The renderer starts at 132 px, may use up to three lines, and must not shrink below 88 px; detail belongs in narration/caption rather than on-screen copy.
* Text placement is selected from upper, middle, and lower zones on either side by measuring occupied pixels, person safety regions, texture, and local contrast. Placement is not fixed at the top or bottom. A soft color-sampled gradient scrim may fade in only when local contrast needs it.
* The reading window is at least 0.28 seconds per word plus 0.8 seconds and should finish before the strongest close-up whenever timing permits, leaving faces and meaningful objects unobscured.
* Legacy registered layers preserve narrow anatomy and clothing details. Do not conceal edge contamination by eroding silhouettes. Use a fine light object outline plus a separate soft offset shadow to hide small matte irregularities and separate the layer from the background.
* Camera execution uses real film scale: establishing wide, medium relationship framing, and a genuine face/upper-body or object close-up around 2.2-2.34x. Lateral moves and focus transfers must land on meaningful close framing rather than remain small digital pans.
* Render-only corrections reuse saved visual checkpoints and remain unpublished drafts. They must not generate replacement images, speech, or other paid media.

# PROJECT_MEMORY.md

## 2026-09-12 — Telegram article posts publish directly through the site bot

* Telegram does not use Zernio. Each site stores its own bot token and destination channel/chat ID in the protected social connection record, and the connection must be tested before delivery.
* A Telegram article adaptation consists of channel-native copy plus its own generated 16:9 editorial JPEG. Blog Core publishes both as one Bot API `sendPhoto` message and may attach the article as an inline URL button when link inclusion is enabled.
* Because the post always carries a photo, the hard text contract is Telegram's 1,024-character photo-caption limit, not the 4,096-character text-message limit.
* A legacy Telegram draft above 1,024 characters is rewritten from its source article at publish time and revalidated while retaining its existing generated image. It is never silently truncated, skipped or regenerated visually.
* Telegram participates in the same factory-owned article-to-social cadence as LinkedIn and supported Zernio channels. A due slot uses the oldest Telegram draft first or creates one from the oldest eligible `PUBLISHED` or real live `IMPORTED` article, then sends it directly through the bot. Imported blog-index URLs remain excluded.
* The existing `yas.wine` and `myugc.studio` legacy-factory Telegram bot/channel connections were migrated into their site-scoped Blog Core connection records and verified through the live Bot API without sending a post. Their Telegram cadences remain disabled until explicitly enabled.

## 2026-08-14 — Reel scenes require varied worlds, practical layers, and varied shot scales

* A five-scene Reel uses at least three visual worlds and at least three shot scales, including wide/establishing, medium, and close/detail. Adjacent scenes cannot repeat the same scale, and one world cannot occupy three consecutive scenes.
* Source-named environments remain preferred. A neutral contextual stage is allowed when the article lacks enough useful physical locations, but the stage carries no editorial proof; claims remain grounded in current-beat people, objects, mechanisms, and overlay copy.
* Architecture and room-scale set pieces are always fixed background: doors, windows, walls, decks, railings, desks, tables, beds, sofas, cabinets, partitions, and built-in lighting never become movable layers.
* Movable objects are compact or medium standalone items occupying less than half the frame. They cannot contain or overlap human anatomy. Anything worn, carried, held, or touched belongs to the complete head-to-feet human group and cannot be extracted again as a separate object.
* A scene may contain one to four truthful layers. The pipeline must not invent filler props to reach an event quota: one layer entrance, persistent text entrance, and synchronized camera motion already provide three visible events.
* Direct-evidence layers are built from a closed current-beat evidence block. A compact object from elsewhere in the article may serve only as honest kinetic support and cannot import another beat's mechanism or conclusion.
* Human movable layers must explicitly state that they are fully visible from head through both feet. `standing` alone is not sufficient proof of extractability.

## 2026-08-14 — Reel planning carries literal evidence and resumable director checkpoints

* Stage two receives the stage-one central problem together with its source grounding. This prevents the concrete physical noun that defines the hook from disappearing between stages.
* A new visual world may be established only from an exact physical-environment substring copied from the current beat's editorial input, source grounding, or problem connection. `domainContext`, another beat, and category knowledge cannot authorize scenery. Resolution always reuses the payoff scene's visual world.
* Stage-two validation rejects movable human layers described as seated, reclining, leaning, cropped, obscured, or partly hidden. Layerability is enforced before any image generation.
* Social execution may close the editorial payoff but cannot replace it with `call to action`, follow/save/link instructions, or another generic social CTA.
* Stage three copies technical layer identities exactly. Every direct-evidence layer triggers a camera beat, and final-focus matching normalizes punctuation identically on both the generated focus text and approved layer name.
* Director generation checkpoints each accepted scene and resumes from the accepted prefix. A failed later scene must not regenerate an earlier accepted scene.

## 2026-08-13 — Reel typography, cinematic camera, and clean-edge matte contract

* Reel overlay copy must remain mobile-readable: 82-118 px in the 1080x1920 renderer, at most three large lines on one screen. Longer locked copy is shown as sequential phrase groups; it is never shrunk into a paragraph.
* Camera direction is executed against real registered-layer alpha geometry and layer type. Person close-ups target the upper body/face, object close-ups target the object center, and an object camera beat must not silently focus a person (or vice versa).
* After layer entrances settle, a scene may establish, push to a true close-up, transfer to another subject or object, and pull out. Adjacent scenes should not repeat the same camera sequence; the camera always transforms the complete assembled scene rather than moving background and layers independently.
* Legacy binary checkpoint layers are tightened and antialiased inside the subject boundary at render time. New registered packs save a decontaminated soft inner matte derived against the selected clean plate. Edge cleanup must reduce source-background fringe without cutting hands, feet, hair, clothing, or owned objects.
* Render-only improvements reuse accepted visual checkpoints. They do not trigger new Gemini image generation or speech generation.

## 2026-08-12 — Approved Reel plans render through resumable visual checkpoints

* An accepted time-coded director plan is the production source of truth. Production adapts that plan to registered layers without asking Gemini to redesign the story, overlay copy, timing, or camera sequence.
* Each accepted visual scene is checkpointed with its background, full-canvas foreground layers, stable layer IDs, and completion time. A resumed run reuses those files and starts at the first unfinished scene; it must not regenerate accepted images.
* Voice is an explicit production option and may be disabled independently. A no-voice Reel generates no speech asset; an existing site soundtrack may still be mixed continuously as background music.
* The visual master must be one coherent vertical photograph with no collage or split-screen composition. People and objects are complete, separated, front-lit, large enough for mobile viewing, and free of selection contours, halos, or cutout styling.
* Semantic masks derived from the coherent master are authoritative. Clean-plate difference may repair only a narrow boundary around that mask; it must not grow into unrelated background regions.
* A visually conflicting optional kinetic-support object may be removed before extraction only when at least three useful layers remain and a non-human story object is still present. People and direct editorial evidence are never silently removed.

## 2026-08-12 — Operator-facing explanations use plain language

* Plans, scenarios, previews, progress reports, and final answers must be written in normal human-readable language by default.
* Do not show JSON, schema fields, internal enum values, database payloads, or implementation identifiers unless the user explicitly requests technical output.
* Translate internal production state into concrete descriptions of what appears, what moves, how it moves, and what the viewer sees.

## 2026-08-12 — Reel layers are immutable rigid images

* Every movable Reel layer is one complete static full-canvas image. The renderer may change only its x/y translation or uniform whole-layer scale; pixels inside the layer never move relative to one another.
* Stage two owns motion feasibility. Every approved layer records a fixed `transformMode`, `appearanceChange: none`, `occlusionState: fully_visible`, and `entrancePathState: unobstructed`. Stage three copies that transform and cannot reinterpret it.
* Movable subjects may include people and complete independent scene-native objects such as vessels, furniture assemblies, clouds, or luggage when they are visually meaningful. At least one non-human object layer moves in every scene.
* A movable layer is invalid when the intended action requires deformation, articulation, a different pose/expression, a changed material state, a different visible side, or an occluded entrance path. Choose another complete object instead of asking later stages to simulate an impossible action.
* The clean plate is the exact master frame without all approved layers. Every layer remains fully visible, unobstructed, and surrounded by recoverable background at its registered final position.
* Replaced/deprecated: the earlier same-day rule allowed story objects to open, swing, roll, or change state. A single extracted still cannot execute those internal changes.

## 2026-08-12 — Reel scenes require object motion, not focus-count padding

* Every stage-two Reel scene contains three or four registered full-canvas layers and at least one `story_object`; people cannot be the only movable content.
* Stage two classifies layers as `direct_evidence` or `kinetic_support`. Direct evidence carries an exact source quote. A direct-evidence object is valid only when its concrete object words are literally present in that quote; abstract concepts cannot be converted into invented notebooks, boards, signs, luggage, barriers, or similar proxies.
* Kinetic support is an honest movable part of the photographed environment that physically admits, reveals, frames, or supports one named direct-evidence layer. It provides motion but never claims to prove the editorial point.
* Every stage-three scene has at least three physical events on three distinct registered layers, including at least one object event. Focus shifts, camera movement, text animation, lighting, and noticing a static relationship do not count toward these events.
* A kinetic-support event's purpose names the exact direct-evidence layer it physically assists and cannot assign the support object symbolic, emotional, or editorial meaning. The final camera beat lands on a direct-evidence layer, never on kinetic support.
* Immutable stage-two identity fields are copied into stage three deterministically; Gemini controls timing and motion direction but cannot rewrite layer name, type, role, grounding quote, supported layer, final position, master frame, clean plate, or overlay copy.
* Reel planning checkpoint version 15 invalidates old static stage-two/three plans while preserving an accepted editorial brief when available.
* Replaced/deprecated: using one person entrance plus two fixed focus/relationship reveals to satisfy a nominal three-event requirement.

## 2026-08-11 — Reel step three is a time-coded director plan

* Step two remains the approved scene-concept boundary. Step three must not reinterpret its story; it turns each approved scene into a detailed execution plan.
* The active step-three director pass consumes the step-two scene concepts directly. The prior parallel skeleton/manifest path is not a valid source for this review checkpoint because it can contain a different scene composition.
* Every scene plan now requires at least three visible, time-coded actions, including at least two foreground actions, plus an independent whole-scene camera move that starts only after foreground entrances settle.
* Clarification: a visual action must reveal or introduce an identifiable source-grounded person, object, or physical detail. Generic light sweeps, atmosphere, texture, reflection, or a bare camera pan do not count. Each scene also requires text and at least two distinct whole-scene camera beats.
* Step three's active positive contract calls these actions `visualBeats`: at least three distinct physical story reveals selected from the approved step-two master inventory. Each declares a registered group/object entrance or fixed-detail reveal, source anchor, reveal method, from-state, trajectory, easing, final state, and story purpose. Text and camera never count toward the three visual beats.
* Each scene requires at least two sequential camera beats with explicit movement type, from/to framing, focus target, easing, and purpose. Camera starts only after the last registered entrance settles.
* Step-three physical events must be anchored by an exact phrase from the approved scene's `evidenceInMasterFrame`. The event roles are registered-group entrance, material-evidence reveal, and spatial-relationship reveal. Incidental scenery and text-placement space are not story evidence.
* Registered people remain complete head-to-feet layers through every entrance. Material/relationship reveals use existing depth, focus, or a real source-grounded occlusion; generated lighting, vignettes, glows, and decorative masks are not executable story events.
* In a scene with one cohesive registered group, its three events target different things: the registered group entrance, a concrete internal interaction/posture, and the named relationship between that group and the fixed environment. Repeating the group name as all three event subjects is invalid.
* The accepted step-three plan is persisted as `planningCheckpoint.directorPlan`; partial accepted scenes live in `directorScenes`. Resume validates and reuses that prefix and generates only the first unfinished director scene. No media starts during this checkpoint.
* Reel planning is operator-gated in the panel: step one can continue to step two, step two can continue to step three, and the accepted step-three plan opens as a readable preview. Advancing a stage reuses the stored checkpoint and never starts image, voice, music, or video generation.
* Distribution has a site-wide `Instagram Reel planning` list independent of content pagination. It exposes the current accepted phase and scene count plus only the valid next action.
* Reel text contrast starts with type color, a fine outline, or a soft shadow. If the image still prevents clean reading, a soft color-sampled, feathered, edge-to-transparent gradient scrim is allowed when it remains visually integrated and preserves image texture. Opaque black rectangles, hard-edged black plaques, solid panels, banners, and boxed text backgrounds are invalid. Replaced: the stricter typography-only rule recorded earlier on 2026-08-12.
* The plan includes exact locked overlay copy, local display timing, kinetic entrance, placement and contrast direction; it also includes an extraction constraint for every approved movable group.
* The director plan must use technical group IDs, local scene seconds, and explicit final states. A prose-only scene description is invalid.
* Replaced/deprecated: treating stage-three camera/layer prose as sufficient direction for production.

## 2026-08-11 - Reel layerability is owned by story architecture

* The first text pass must choose physical visual worlds whose meaningful people are complete unobstructed free-standing groups. Seated, furniture-supported, cropped, small-prop-led, or extraction-oriented visual worlds are rejected before the visual skeleton is generated.
* A later prompt cannot reliably turn an intrinsically non-layerable composition into independent animated layers. The earliest stage that chooses the physical world owns this constraint.
* Reel text stages make one model request per unfinished checkpoint. A validator failure stops that stage with its exact reason; it must not trigger several paid regenerations from the same inadequate prompt. Fix the owning prompt or contract first, then resume from the last accepted checkpoint.
* Character planning always describes a complete in-frame person from head through both feet, with visible air gap from fixed architecture. `crop`, `waist-up`, separate/isolated layer language, unseen support, and physical contact with railings, bars, counters, desks, tables, chairs, walls, or doors are incompatible with the registered master/clean-plate workflow.
* Gemini does not own technical layer numbering. Skeleton responses use an ID placeholder and application code assigns stable global `element-NN` IDs before validation; a numbering-format mistake must never consume another model request.
* Every person named by Reel architecture is a planned foreground group. Background/distant crowds and atmospheric extras are forbidden because they cannot be cleanly registered or extracted. A rejected skeleton, scene-detail, or manifest candidate and exact validation error are saved in the checkpoint for prompt diagnosis before any new request.
* Geometry validation distinguishes social separation from extraction instructions. `isolated from the crowd` is editorial meaning, while `isolated subject/layer/foreground` or `isolated on a background` is a deprecated asset instruction. Prompts should use `standing alone` or `separated by visible background space` to remove ambiguity.
* Layer `sourceEvidence` accepts any exact non-empty consecutive source phrase, including one meaningful hyphenated source term. It must not reject valid source grounding merely because token counting expects two words.
* Instagram Reel captions contain no protocols, `www`, raw URLs, or dot-domains. They may name the brand in plain text; clickable destination handling belongs to the publishing channel, not caption prose.
* Replaced/deprecated: accepting a conceptually relevant visual world and trying to repair its geometry during skeleton or asset-manifest generation.

## 2026-08-11 — Reel production is resumable from validated checkpoints

* Reel text planning is not one disposable transaction. Version 13 persists these validated checkpoints in `social_posts.content_json.instagramReel.planningCheckpoint`: source outline and editorial architecture, visual skeleton, each detailed scene, each technical manifest scene, and the complete storyboard.
* A later phase starts only after the preceding result passes its validator and is saved. Scene checkpoints are sequential; an out-of-order or duplicate checkpoint is an error.
* An interrupted or failed run resumes from the first unfinished scene. It must not regenerate accepted architecture, skeleton, detailed scenes, or manifest scenes.
* Skeleton validation owns extraction geometry. A skeleton containing seated, reclining, cropped, furniture-supported, naturally occluded, or fixed-contact movable people must never be saved as `skeleton_ready`. If stricter current validation rejects an older saved skeleton, retain its valid architecture and invalidate only the skeleton and downstream checkpoints.
* A per-scene checkpoint must pass the same production-detail validator used by the final storyboard. Final aggregation must not introduce a stricter local scene check. When current validation rejects a previously saved detail scene, retain the contiguous valid scene prefix, truncate from the first invalid scene, and clear only downstream manifest/storyboard checkpoints.
* Fields locked between skeleton and scene detail, including `visualStory` and the canonical empty stage description, must satisfy their final requirements before `skeleton_ready`. A later stage must never retry an immutable upstream defect.
* Source-grounding for every scene is also a skeleton responsibility. Unsourced character knowledge/decision causality must fail before `skeleton_ready`, not during scene detail.
* Editorial architecture owns the photographable visual world. Device/interface/readable-sign shortcuts are invalid at architecture time; downstream skeleton prompts must never be asked to contradict an approved visual world. If current validation rejects stored architecture, invalidate architecture and every dependent checkpoint.
* Informational Reel plans may use a named recurring performer as internal visual-continuity metadata; the name is not shown or narrated. The performer demonstrates separate source-grounded conditions and must not be given an unsourced knowledge, transaction, decision, or success chronology. Registered-layer prompts describe subjects inside one integrated master photograph; isolated/transparent/matte/cutout wording and device-led visual shortcuts are invalid before media generation.
* Replaced/deprecated: the same-day rule that any recurring character name absent from the article is itself invalid. The actual violation is invented story causality, not the internal production name.
* Model retry loops cover only model generation/validation for the current step. Database/checkpoint callback errors are outside those loops and must never cause a hidden repeated model call.
* Regenerating an unpublished version-13 Reel preserves valid planning checkpoints. Older checkpoint versions are ignored because their contracts may be incompatible.

## 2026-08-11 — Reel registered-layer geometry and motion are one enforced contract

* The active full-canvas renderer consumes each component's approved `manifestReveal`, `manifestMotion`, `manifestStartSeconds`, and `manifestEndSeconds`. It must never choose an entrance from scene/layer indexes or silently invent missing motion.
* A movable person/group must be a complete, fully contained, unobstructed, free-standing silhouette. A seated, reclining, naturally occluded, cropped, furniture-supported, or fixed-contact person is not a movable layer: recompose the source-grounded action as free-standing or keep the person inseparably in the static background.
* `focus` is an in-place optical reveal, not permission to translate an incomplete body. Directional entrances are only for complete groups that can translate without exposing missing anatomy or moving fixed furniture/architecture.
* Entrances finish within the first 38% of a scene; registered layers hold afterward while whole-scene camera work supplies motion. Invalid geometry or missing manifest fields block before image generation.
* Camera prose (`cameraStart`, `cameraEnd`, `cameraMotivation`) is also not interpreted directly. The renderer holds its base camera until 46% scene progress, pushes to the first detected subject, then pulls/transfers or finishes with the coarse `cameraMove` preset.
* Replaced/deprecated: index-based reveal cycling and the rule that a person plus movable seat/contact furniture could form one translating group. That produced cropped torsos or visibly moving furniture.

## 2026-08-11 — Text-only Reel planning remains blocked before media production

* A full text-only production plan for the published SoloCruz article `What Makes a Cruise Truly Solo-Friendly? A Checklist Beyond the Single Cabin` completed with seven scenes and no media generation.
* The plan is not approved for image generation. It invented a recurring fictional protagonist and chronology for an informational guide, relied on laptops/phones/readable screens and contact furniture, produced mostly static layer directions, and emitted a technical manifest describing separately generated transparent foregrounds instead of the active master-derived scene contract.
* Operational rule: do not generate images, voice, music, or video from this plan. The storyboard and step-three prompts must be aligned end to end with source-grounded editorial scenes and the master/clean-plate/extracted-layer architecture before another production run.

## 2026-08-11 — Reel scene planning matches master-derived contact groups (replaced)

* A movable character group may walk, turn, gesture, or interact naturally. When a source-grounded action requires another person or a movable contact/owned item, every touching person and complete contacting item belongs to the same extraction-safe group and is described as one combined silhouette.
* Fixed architecture remains in the clean background and must not touch or occlude a movable group. Separate movable groups retain visible background space between them.
* Replaced/deprecated: the old independent-foreground validator that rejected walking and every scene mentioning seating or furniture. That rule contradicted the current master-derived extraction architecture and caused repeated text-only storyboard rejection.
* Replaced/deprecated by the later same-day geometry contract: movable carried/worn items may remain inside a complete silhouette, but seating and fixed-contact furniture may not be part of a translating group.

## 2026-08-11 — Production Reels use one-pass validated master-derived scenes

* Current architecture: each storyboard scene generates one complete coherent 9:16 master photograph containing all approved movable groups. The first prompt requires large mobile-readable subjects, complete heads/limbs/hands/clothing/owned items, clear background gaps between independent groups, no unrelated nearby crowd, and a calm text-safe region.
* Visual gate: Gemini vision must identify every approved group, return its normalized bounds, and confirm a single coherent photograph, complete in-frame groups, sufficient scale, separability, owned/contact objects, background clearance, and the quietest text zone. A failed gate stops the production record.
* Clean-plate and layer path: from an accepted master, Gemini edits one otherwise-identical clean plate removing only the approved complete groups. `registered_scene.py` extracts 1-4 full-canvas registered masks, grows clean-plate difference only through pixels connected to the accepted subject, fills enclosed holes, checks overlap/scale/reconstruction, and sends a review sheet through a final layer-integrity gate.
* Cost rule: visual generation is one-pass. Validators never trigger hidden paid regeneration. A failed master, clean plate, or layer pack remains failed until the operator explicitly retries after correcting the universal prompt or contract.
* Audio rule: no voice is generated until every visual scene in the Reel has passed master, clean-plate, segmentation, reconstruction, and integrity validation.
* Renderer: whole layers enter from varied directions without a simultaneous wipe/reveal mask. The camera stays static during entrances, then pushes toward a face/upper-body/group target derived from real alpha bounds, holds, pulls back, or transfers focus to the next settled group. Copy placement is recalculated from foreground occupancy and local texture; fill and contour are chosen from local luminance.
* Deployment: `MASKED_LAYER_REEL_ENABLED=1` on the Blog Core VPS. Existing Reel rows were not queued when it was enabled, so deployment caused no media generation.
* Replaced/deprecated: the earlier clean-background plus independently generated foreground contract, the statement that master-derived extraction was rejected, automatic paid image retries, fixed minimum layer quotas, camera movement during entrances, and planner-only text placement authority.

## 2026-07-26 — Complete Pricing catalogue is independent from checkout readiness

- Decision: Pricing always displays Solo (€49), Pro (€99), and Agency (€199); an unconfigured tier must not disappear from the commercial page.
- Decision: `GEORIVO_PURCHASABLE_PLANS` controls which visible tiers may enter checkout. It defaults to `solo`.
- Decision: a tier without a confirmed Stripe recurring Price uses a localized contact/request action and must never expose a broken or simulated checkout.
- Replaced: the earlier rule that every visible paid tier must already be directly purchasable. Visibility and checkout readiness are now separate, while purchase claims remain fail-closed.

## 2026-07-26 — Informational content uses intent-specific Georivo product steps

- Decision: every published Guide, Blog article, Template, Example, and Embed guide contains a visible contextual product step inside the main article content.
- Decision: the renderer classifies the page intent as Property Showcase, Neighborhood Story, Arrival Guide, coverage check, publishing/embed, or example setup and links to the matching real Georivo screen with the relevant template/movement query where supported.
- Decision: contextual product copy is localized in EN, DE, ES, FR, and RU. A universal repeated CTA is not an acceptable substitute.
- Reason: useful informational content should complete the reader's answer with a concrete way to apply it in Georivo without turning every article into the same template advertisement.
- Release gate: public typed-content audits require `product-bridge` and a valid `data-product-action`; the complete sitemap audit requires at least four distinct product-action intents.

## 2026-07-26 — Embed indexation follows real-editor verification

- Decision: only WordPress is currently a verified integration guide. Webflow, Wix, and Squarespace remain public for review/use but are `noindex` and excluded from sitemap until each is verified in its current authenticated editor.
- Decision: the `/embed/` hub remains `noindex` and outside sitemap while fewer than three platform guides are verified.
- Reason: a generated `versionCheckedAt` field is not proof of real-editor verification and must not make unverified operational instructions indexable.

## 2026-07-26 — Pricing uses three large plan cards

- Replaced: the same-day single compact Solo card is superseded by a large three-tier grid.
- Decision: Pricing presents Georivo Solo (€49; 10 widgets; 1,000 monthly 3D starts), Pro (€99; 30; 5,000), and Agency (€199; 100; 20,000).
- Decision: every card has one account-aware CTA carrying its explicit plan key; the Pricing hero must not duplicate those purchase buttons.
- Release gate: the renderer and product app must agree on plan keys and limits, and every visible paid tier must map to a real configured Stripe recurring Price. Decorative or simulated paid plans are prohibited.

## 2026-07-26 — Pricing first paint uses one plan card and one action

- Decision: the Pricing hero does not repeat the price or subscription button immediately above the plan card.
- Decision: the first plan summary is one compact Georivo Solo card, not a side-by-side free-preview/paid comparison. It contains only €49/month, 10 active widgets, 1,000 visitor-started plays, protected distribution, and one checkout CTA.
- Layout rule: the plan card follows the hero in normal document flow with positive spacing. Negative overlap that can cover hero controls is prohibited.
- Reason: adjacent free/paid actions and repeated subscribe controls diluted the purchase hierarchy, while small explanatory copy obscured the plan essentials.

## 2026-07-26 — Georivo separates preview and subscription actions

- Decision: address checking is a secondary free-preview action; subscription is the primary commercial action on Pricing and at the end of Guides, Blog, and collection pages.
- Decision: every visible commercial CTA is localized server-side for EN, DE, ES, FR, and RU.
- Decision: Pricing exposes the Georivo Solo offer above the long-form SEO content: €49/month, 10 active widgets, 1,000 visitor-started 3D plays, protected links, domain-bound embeds, dashboard access, and the real account-aware checkout action.
- Decision: signed-out subscription clicks use `/login?returnTo=/dashboard?startCheckout=1`; signed-in unpaid users continue through the existing `/api/billing/checkout` Stripe flow. The renderer must not simulate checkout.
- Responsive rule: long Guide titles must fit both halves of the split hero on desktop and use natural/hyphenated word wrapping on mobile rather than arbitrary mid-word clipping.

## 2026-07-26 — Georivo Guides and Blog use different presentation systems

- Decision: Georivo Guides are practical handbooks with a split guide hero, sticky in-guide navigation, numbered content sections, and a task-oriented action rail. Blog pages remain editorial journal articles.
- Decision: Collection heroes use the featured record's own `heroImage`; the former universal `/georivo-hero.png` CSS background is not a Blog Core fallback or CTA image.
- Decision: The featured record is omitted from the collection card grid to avoid showing the same story image twice on one hub.
- Reason: Guides serve task completion and Blog serves editorial discovery. Reusing one article shell and one generic product image made the content types indistinguishable and caused visible media repetition.
- Files/areas affected: `deploy/georivo/app.py`, `deploy/georivo/georivo-blog.css`.

## 2026-07-26 — Shared Georivo chrome is localized server-side

- Decision: Blog Core money pages continue to reuse `LiveSiteChrome`, while `adapt_native_chrome` localizes every visible header/footer label, CTA, legal line, and route for EN, RU, DE, ES, FR.
- Decision: the shared footer information architecture is three balanced navigation groups: Product, Resources, and Company. Blog Core does not own a separate footer layout.
- Reason: client-side insertion left untranslated first-paint HTML and could show a stale or visually inconsistent shell during navigation.

## 2026-07-26 — Georivo money-page heroes are distinct from first paint

- Decision: `/how-it-works`, `/coverage`, and `/pricing` use three separate same-origin WebP hero assets served by `georivo-blog.service`.
- Decision: each money page preloads its own hero and has a page-specific CSS background fallback using that same asset, plus a page-specific wash/object position.
- Reason: distinct `<img>` URLs alone were insufficient because the shared neutral placeholder could occupy the first visible frame while the image loaded, making all three pages appear to use the same hero.
- Release gate: the 15-page audit must report three different hero paths; production HTML must include a matching hero preload for each page.

## 2026-07-26 — Root money pages own disjoint visual libraries

- Decision: image uniqueness is global across `/how-it-works`, `/coverage`, and `/pricing`, not merely local to one page. A main-content image used by one root money page may not appear in either of the other two in the same language.
- Decision: each money page keeps its own factory figures, while generated section visuals and recommendation-card photos come from a stable slug-partitioned pool of non-money-page published assets.
- Decision: recommendation cards preserve their real destinations and copy but use the current money page's allocated contextual imagery; reusing the linked target's hero across several money pages is deprecated.
- Decision: hero scenes must be intentionally different by subject. How it works uses the existing workflow scene; Coverage uses a people-free aerial coverage landscape; Pricing uses a publishable-widget/subscription scene in a real-estate gallery.
- Release gate: `audit_money_pages.py` compares every image inside each money-page main region and fails on any cross-page overlap for the same language.
- Replaced: the prior rule guaranteed uniqueness only within a single page and therefore allowed all three pages to render the same supporting asset sequence.

## 2026-07-26 — Money-page section media is unique and strictly alternating

- Decision: every primary money-page narrative section is a two-column media section. Odd sections place copy left and image right; even sections place image left and copy right.
- Decision: supporting visuals are selected from unique published Georivo hero assets. The selection excludes the current money-page hero, its opening/editorial figures, and hero images reserved for recommendation cards.
- Decision: a supporting image URL may appear only once among primary sections. If the unique pool is exhausted, the renderer must not cycle back to a previously used image.
- Replaced: the earlier same-day approach that cycled the current page's small hero/editorial pool and placed generated visuals beneath the heading.
- Release gate: `commercial_sections` fails unless every primary section has media, reverse layout matches even-numbered sections, and all supporting image URLs are unique.

## 2026-07-26 — Georivo money pages integrate navigation and semantic imagery

- Decision: the money-page TOC is part of the hero composition, not a detached article sidebar. Desktop/tablet use a wide multi-column navigation panel; mobile keeps it inside the hero as a horizontally scrollable strip that must not expand the document width.
- Replaced later 2026-07-26: the initial visual-fill renderer used the page's own small asset pool beneath headings. The current renderer uses unique published Georivo heroes as full opposite-column media and strictly alternates their side.
- Decision: old `Related reading` and `Recommended next` article blocks are transformed into one localized `Explore Georivo` commercial recommendation grid. Cards preserve and deduplicate the factory's internal links/descriptions, resolve the target page's published hero image, and retain the FAQ below.
- Reason: money pages must use long-form content without looking like stretched articles or leaving unused columns.
- Release gate: the 15-page audit requires the TOC inside the hero, at least four supporting visuals, at least three photo recommendation cards, and no remaining article-related/article-recommended markup.

## 2026-07-25 — Georivo money-page styling uses content-driven density

- Decision: commercial sections must not use artificial minimum heights. Section height is determined by real copy and media, with compact inter-section gaps and consistent internal padding.
- Decision: long introductory copy is supporting text, not a second hero heading. Desktop leads use a restrained 21–25 px scale; mobile uses 20 px with a readable line height.
- Decision: non-media sections split heading and body into balanced columns. In media sections the image fills the complete paired section height; it must not stop at a fixed 16:9 frame while copy continues beside an empty area.
- Decision: related links, recommended pages, and FAQ are presentation utilities and belong in their own compact closing section rather than inside the final narrative section.
- Responsive contract: the TOC becomes in-flow below 1180 px; story layouts stack below 900 px; mobile spacing/type are reduced below 640 px; no supported viewport may create horizontal document overflow.
- Reason: commercial pages should feel like dense, deliberate Georivo product pages, not a stretched article or a sequence of disconnected oversized cards.

## 2026-07-25 — Georivo money pages use a dedicated commercial section system

- Decision: factory-generated Georivo root money pages are transformed at render time into a dedicated sales-page composition: full product hero, compact sticky TOC rail, large alternating section cards, media/text split sections, a mid-page conversion CTA, and a final CTA.
- Reason: SEO money pages must keep the complete validated factory content while looking and behaving like Georivo product pages, not like Blog Core articles.
- Boundary: the transformation applies only to the three approved root money-page slugs. Article, guide, template, example, integration-guide, and ordinary use-case renderers are unchanged.
- Responsive rule: below tablet width the TOC becomes an in-flow card, media/text sections stack, tables scroll within their section, and the page must not create horizontal document overflow.

## 2026-07-25 — Register CabinJoin as a native money-page content store

- Decision: CabinJoin is connected as a `native_content_store` site with EN/RU/FR/ES/DE and a dedicated shared content root. Static `seo_money_page` records will be drafted, reviewed and explicitly published by Blog Core; CabinJoin renders only the published local payload in its own transactional application.
- Reason: CabinJoin needs the same controlled content lifecycle as other generated sites without making Blog Core responsible for availability, payment, identity or marketplace transactions.
- Boundary: Blog Core publishes CabinJoin SEO money pages below /use-cases/. The interactive homepage remains a native CabinJoin product page and is not managed by Blog Core.
- Replaced/deprecated: The earlier CabinJoin-only assumption that Blog Core would be limited to a future blog tenant.

This file is the durable memory of the project.
It must be updated after every meaningful task.

## 2026-07-25 — Georivo root money pages use the genuine Blog Core factory

* Decision: `/how-it-works`, `/coverage`, and `/pricing` are generated as native `seo_money_page`/`use_case` jobs by the standard Blog Core text, factual-edit, image, localization, validation, draft, and explicit-publish pipeline.
* Decision: A native use-case may publish at an approved root canonical only when `sources_json.canonicalRootPage` is exactly `true` and `targetPath` exactly equals `/{slug}`. Other typed pages retain their normal collection prefix.
* Decision: Root money-page records are stored as ordinary factory `use_case` files. The Georivo renderer recognizes only the three approved root slugs as money pages and presents them with `WebPage` schema and the shared product chrome.
* Decision: Their collection-form aliases under `/use-cases/{slug}/` and localized equivalents permanently redirect to the approved root canonical and never render duplicate pages or appear as use-case hub cards.
* Decision: Public category/eyebrow copy comes from approved per-language `pageBrief.categoryLabels`; internal workflow terms such as `SEO Money Page` must not leak into visible copy.
* Replaced/deprecated: The deterministic `seed_money_pages.py` implementation and its manually authored short HTML are retired. The old `money--*.json` records were replaced by factory-generated `use-cases--*.json` records and preserved only in the dated VPS backup.
* Verification: each EN draft passed the factory contract with 1,821–2,116 words, 8 sections, 3 inline images, 6 FAQ items, contextual links, and exactly 3 recommended-next links; all DE/ES/FR/RU variants passed localization validation. The strict public audit passed all 15 canonical language URLs and all 15 collection-alias redirects.

## 2026-07-25 — Georivo SEO money pages are owned by live Blog Core

* Replaced 2026-07-25: `/how-it-works`, `/coverage`, and `/pricing`, plus DE/ES/FR/RU variants, remain owned by Blog Core site 14 and rendered by `georivo-blog.service`, but the earlier manual `money_page` seed records are superseded by genuine factory-generated `use_case` records.
* Reason: SEO money pages need the live content workflow while remaining visually and navigationally part of `georivo.com`.
* Files/areas affected: `deploy/georivo/app.py`, `georivo-blog.css`, `georivo-blog-nav.js`, `georivo.com.conf`, native published records, and site 14 content jobs.
* Decision: The renderer continues to obtain the current Georivo header, footer, and native stylesheet through `LiveSiteChrome`. Money pages add only a namespaced marketing-page body, so source chrome remains the single public header/footer implementation.
* Decision: Every money page has its own thematic hero. Coverage calls the real production coverage endpoint, and Pricing opens the existing account-aware Stripe Checkout flow. Neither interaction may simulate success.
* Replaced/deprecated: The React-origin implementations for these three public paths are no longer the production owner after Nginx cutover.

## 2026-07-25 — Native content navigation follows the active locale

* Decision: Existing source-header/footer links for Blog Core-owned content sections are rewritten to the active locale path and localized menu label by the native renderer.
* Reason: Reusing live source chrome can preserve newly added `/guides/` and `/blog/` anchors with English labels and EN URLs unless the adapter localizes the existing anchors, not only links it inserts itself.
* Files/areas affected: `deploy/georivo/app.py` and `deploy/georivo/georivo-blog-nav.js`.
* Current labels: EN `Guides`/`Blog`; DE `Leitfäden`/`Magazin`; ES `Guías`/`Revista`; FR `Guides`/`Journal`; RU `Руководства`/`Блог`.

## 2026-07-25 — Georivo Search Console monitoring is durable

* Decision: The daily Georivo Search Console task records two complete 28-day performance windows, top pages, and URL Inspection results for the primary product/collection URLs after every successful sitemap read-back.
* Reason: Sitemap submission alone does not prove indexation or provide a basis for search-performance decisions. The operator needs API-sourced, timestamped evidence without a browser session.
* Files/areas affected: `deploy/georivo/gsc_submit.py`, ignored `data/georivo-gsc-status.json`, Search Console operations.
* Decision: Query text is deliberately not stored. Monitoring keeps aggregate totals and page URLs only, and a missing data row is reported honestly rather than converted into an invented zero trend.
* Replaced/deprecated: The earlier submission-only status file and manual Search Console inspection as the only source of indexation evidence.

## 2026-07-25 — Georivo Search Console submission is operational

* Decision: `sc-domain:georivo.com` grants the factory service account `siteFullUser` access. The official adapter submitted `https://georivo.com/sitemap.xml` and read back the accepted API record with zero errors and warnings.
* Reason: This closes the external-access blocker and proves that the daily retry path works without an operator browser session.
* Files/areas affected: Search Console property access, `deploy/georivo/gsc_submit.py`, ignored `data/georivo-gsc-status.json`, and `georivo-gsc-submit.timer`.
* Current state: Google returned `isPending=true` immediately after submission on 2026-07-25. This is normal initial processing, not a failed submission.
* Replaced/deprecated: The earlier 2026-07-25 statement that Georivo Search Console access and submission were pending.

## 2026-07-25 — Search Console submission is retryable and observable

* Decision: Native-site Search Console submission uses a repository script with Google service-account OAuth, public sitemap validation, explicit property-permission checks, official Webmasters API submission, and an atomic ignored status file.
* Reason: A public sitemap and an authenticated service account are not proof that Google accepted a submission. The system must distinguish missing property access from credential/network/API errors and record the actual result.
* Files/areas affected: `requirements.txt`, `.gitignore`, `deploy/georivo/gsc_submit.py`, `georivo-gsc-submit.service`, `georivo-gsc-submit.timer`, and ignored `data/georivo-gsc-status.json`.
* Decision: Exit code `75` means a controlled external-access blocker and is accepted by systemd; exit code `1` remains a real operational error. The daily timer retries automatically after the content audit.
* Reason: Property permission can be granted later without another deployment, while credential or network failures must remain visible as failures.
* Replaced/deprecated: One-off manual GSC commands that leave no durable state and require an operator to remember to rerun them.

## 2026-07-25 — Georivo typed content rollout is live

* Decision: Georivo's approved initial typed-content tree is live as 19 canonical tasks: 8 Guides, 3 Templates, 4 Examples, and 4 Integration guides. Every task publishes EN plus DE/ES/FR/RU variants from one dashboard record.
* Reason: The first production rollout proves the complete native content-store lifecycle without reconnecting Georivo or changing its product application.
* Files/areas affected: `app.py`, `deploy/georivo/`, Georivo native content records, collection hubs, and sitemap.
* Decision: Typed generation uses a structured first pass, a factual-editor second pass, deterministic safety/navigation restoration, and strict final validation. Validation rejects incomplete structure, unsupported precision/recency claims, unapproved links, and leaked model-control text such as code fences, chain-of-thought markers, or JSON-output narration.
* Reason: A model response can be valid JSON yet still contain unsafe claims, remove required sections, or leak internal generation text into a visible heading. Correctness must be enforced before a draft is saved.
* Files/areas affected: structured article generation and validation in `app.py`, plus `deploy/georivo/audit_content_plan.py`.
* Decision: Georivo publication requires four recorded gates: editorial review, product fact check, SEO review, and browser QA. The rollout passed 19/19 static audits and 114/114 browser checks before explicit publication.
* Reason: Generation success is not publication approval. The site needs independent structure, language, asset, responsive, and SEO checks.
* Files/areas affected: page briefs, content-job logs, `deploy/georivo/approve_and_publish_content_plan.py`, and `deploy/georivo/visual-test.js`.
* Replaced/deprecated 2026-07-25: Search Console access is no longer pending. The service account now has `siteFullUser`, and the official API submission/read-back succeeded.
* Decision: A daily systemd audit rechecks the public Georivo contract, while the separate GSC timer validates and resubmits the current sitemap through the official API.
* Reason: Public sitemap availability alone does not prove submission; the durable success signal is the API `submitted` state plus a readable sitemap record.
* Files/areas affected: `georivo-content-audit.service`, `georivo-content-audit.timer`, deployment/integration memory.
* Replaced/deprecated: The 2026-07-24 plan state in which typed hubs existed but no typed pages had been queued or published.

## 2026-07-24 — Typed native content routes and single-user workflow

* Decision: Native content-store sites preserve explicit content types instead of collapsing them into Blog. The supported route contract is Blog `/blog/`, Guide `/guides/`, Template `/templates/`, Example `/examples/`, Integration guide `/embed/`, and Use case `/use-cases/`, with the same route under each configured non-default language prefix.
* Reason: Blog Core is a full content factory, not only an article renderer. Typed routes preserve search intent, avoid slug collisions across collections, and let native adapters present each content class without changing the product application.
* Files/areas affected: `app.py`, native content-store JSON, native site adapters, nginx route allowlists, canonical/hreflang, and sitemap generation.
* Replaced/deprecated: Mapping every native content type except use cases to `blog`.
* Decision: Blog Core remains a single-user operator dashboard. Do not add users, roles, permissions, or RBAC. Use workflow status, mandatory validation, explicit Publish, and durable task logs for control and auditability.
* Reason: The project does not need organizational access control; role labels from editorial specifications are trust metadata, not application accounts.
* Files/areas affected: Dashboard workflow, publication validation, logs, and future trust metadata.
* Replaced/deprecated: Any planned RBAC or multi-role editorial workflow for this project.

## 1. Product overview

* Project name: Blog Core for yas.ooo.
* What it does: Universal blog/content core MVP that connects external sites, scans their public design, generates a matching blog shell/preview, installs static blog pages into local site roots when available, or hosts a blog through a custom CNAME domain.
* Target users: Site owners/operators who need a blog/content factory attached to existing sites without rebuilding those sites; internally this is used to manage multiple content factories/sites from one dashboard.
* Main business goal: Provide a reusable, site-agnostic blog and article factory layer that can adapt to each connected site's design and publish SEO/content assets at scale.
* Main user flows:
  - Connect a site by homepage URL, optional brand name, and optional local webroot.
  - Scan public site design and save a theme profile.
  - Build a preview blog under `/previews/{site_id}/blog/`.
  - For local VPS sites, install static `/blog/` files into a configured webroot.
  - For external sites, configure `custom_blog_domain`, ask the client to CNAME it to `blog.yas.ooo`, enable hosted CNAME blog, and serve the blog by Host routing.
  - Manage a site's factory settings, discover topic signals, select trends/discussions, queue article idea jobs, generate draft article jobs, and import existing `/blog/` articles as preserved Blog Core content jobs.

## 2. Current architecture

* Frontend: Server-rendered HTML/CSS/JS strings inside `app.py`; no frontend build pipeline.
* Backend: Python Flask app in `app.py` served by Gunicorn.
* Database: SQLite at `data/blog_core.sqlite3`; `data/` is ignored and must not be committed.
* Hosting: VPS path `/var/www/blog.yas.ooo`; PM2 process `blog-yas-core` runs `run.sh`.
* Scheduled page publishing: PM2 process `blog-yas-core-scheduler` runs `run-scheduler.sh` once per minute. It advances only explicitly scheduled `content_jobs` through the native factory lifecycle and does not distribute social posts.
* Auth: No application-level dashboard auth is implemented in the MVP. The private YAS Source Scanner draft-ingestion endpoint uses a shared secret header and must never expose or log its value.
* Payments: None.
* Main external services:
  - Public site HTML/CSS fetched via `urllib.request` for design scanning.
  - Popular topic discovery uses Google autocomplete/search suggestions as a non-news search-demand signal source, plus Reddit top discussions.
  - Reddit search RSS is used for discussion signals; it may rate-limit.
  - DNS resolution uses Python `socket.getaddrinfo` for CNAME/custom-domain status checks.
  - Gemini text generation is used for draft generation and for automatic site topic-profile inference when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is configured.
  - Draft generation is represented by the content job generation contract in `app.py`; provider credentials/secrets must not be committed or documented in raw form.
* Important folders/files:
  - `app.py` — Flask app, routes, SQLite schema/migrations, scanner, blog rendering, dashboard UI.
  - `run.sh` — Gunicorn launcher bound to `127.0.0.1:3299`.
  - `requirements.txt` — Flask and Gunicorn versions.
  - `deploy/nginx-blog.yas.ooo.conf` — tracked nginx vhost template for `blog.yas.ooo` only.
  - `/etc/nginx/conf.d/blog.yas.ooo.conf` — live vhost on VPS.
  - `/etc/nginx/conf.d/000-default-catchall.conf` — live catchall proxy to Blog Core for CNAME Host routing; this server file is not currently tracked in the repo.
  - `previews/` — generated preview files, ignored.
  - `docs/` — durable project memory.

## 3. Business rules
* Generate/regenerate, Preview, and Publish are separate operator actions. Generating a draft must not automatically publish it. `DRAFT` tasks need an explicit Publish action. For imported/source-authoritative jobs, Publish delegates to the original source factory rather than editing source-site files directly from Blog Core.
* Finished Source Scanner Studio drafts can be inserted into the target site's task queue only through the authenticated source-scanner endpoint. They arrive as `DRAFT` tasks with their authored HTML, source attribution, FAQ and scanner-hosted media; Blog Core must not regenerate or auto-publish them. Re-sending an unpublished scanner draft updates the same task. A published task cannot be replaced through this integration. Native YAS draft-store preparation remains specific to `yas.ooo`; other sites are queued without assuming a publication adapter.


* Blog Core must support arbitrary external sites, not just sites hosted on this VPS.
* External sites should normally use hosted CNAME blog routing instead of requiring SSH/SFTP/Git/CMS access.
* Local install is only for sites whose filesystem root is available on the same VPS and configured in `root_path`.
* Deleting a connected site from the dashboard must remove only Blog Core records and preview cache. It must not delete installed `/blog` files from the target site root.
* Factory settings are per site: content context, topic strategy, languages, cadence, CNAME settings, and jobs belong to the site.
* `Discovery direction` and `Category hint` should be auto-inferred from the scanned site with Gemini during `Scan design`. They remain editable overrides, but should not be empty/manual-first for newly scanned sites. If Gemini is unavailable, use a deterministic metadata fallback and do not block scanning.
* The manage page should allow switching between connected sites without returning to the dashboard.
* Factory parity with the old YAS Wine factory must include article jobs, logs, generation modes, social channels, autopublish settings, topic discovery settings, and publish status per site.
* Social publishing/OAuth must be scoped per site, not globally.
* Setup must include per-site social channel credential configuration for LinkedIn, Telegram, X/Twitter, Tumblr, Pinterest, Instagram, and Threads, with Save credentials and Test connect actions. Distribution should only select which configured/connected channels are used for autopublish.
* Social publishing drafts must be adapted per channel and per article language before publishing. Blog Core stores one `social_posts` draft per `job_id + channel`, validates exact character counts before saving, and must not rely on social platforms truncating overlong text.
* Pinterest drafts are not plain text posts. Blog Core must generate a native Pinterest pin creative spec from the article: title, description/caption, overlay text, alt text, vertical 2:3 image prompt, recommended size, and optional destination URL. The pin spec is stored in `social_posts.content_json`.
* Instagram drafts are native carousel creatives, not plain text posts and not SVG/mock previews. Blog Core generates one shared carousel caption plus real 4:5 JPEG slide assets through Gemini Image, stores slide metadata in `social_posts.content_json.instagramCarousel`, and serves generated files from ignored `data/social_assets/...`. Instagram has one caption for the whole carousel; per-slide text is visual overlay/review metadata only.
* Instagram captions have a hard maximum of 2200 characters, but Blog Core should target a much shorter default caption around 700 characters for generated carousel posts. The caption should be a compact hook/context/CTA with no more than three hashtags, because slide content carries the details.
* Instagram publishing must go through the project's third-party intermediary publishing server, not direct Instagram Graph API calls from Blog Core.
* Threads is a separate social channel from X/Twitter and Instagram. Threads drafts must feel native to Threads: short, conversational, question-led or opinion-led, not promotional ad copy. They must stay within 500 UTF-8 bytes, use at most one hashtag, and should generate one separate Threads-specific image: simple, natural, non-advertising, no overlay text, no logo, no UI screenshot, not reused from Instagram carousel creative. Blog Core should validate bytes, not only Python character count, because emoji/non-ASCII text can exceed platform limits sooner.
* Social publishing drafts must not be offered or generated unless at least one social channel is both selected in Distribution and configured/connected in Setup. There must be no fallback that silently generates drafts for every provider when channels are missing.
* Technical settings should stay compact on the site factory page; main workflow should focus on topic discovery and jobs.
* Existing imported blogs and Blog Core-created blogs have different ownership models. For imported existing blogs, Blog Core should act as the control plane/dashboard and publish new/updated tasks back into the same original site locations and URL structure. It should not default to becoming a second public copy of that blog. For blogs created by Blog Core from scratch, Blog Core can be the full source of truth and public hosting/publishing layer.
* For imported sites that have legacy/source factory jobs (`sources_json.migratedFrom` and `oldFactoryJobId`), Blog Core must not use its generic article generator. It must delegate generation to the source site's factory so validation, length rules, internal-link rules, image generation, SEO money-page contracts, and publishing requirements remain site-specific.
* Legacy/source factory generation must be recoverable after Blog Core restarts. The content-job status API should re-check the source factory for `GENERATING` legacy jobs, sync `READY`/`PUBLISHED` drafts back into Blog Core, surface legacy `ERROR`, and mark stale long-running legacy jobs instead of leaving the dashboard stuck forever.
* For imported existing blogs, primary dashboard open actions should point to the live source-site blog URL, not to generated Blog Core previews. Generated previews are only useful for new/from-scratch Blog Core blogs or technical design checks.
* Dashboard site cards for imported live sites must not show new-site setup actions such as `Scan design`, `Build preview`, or `Install /blog`. Imported site cards should focus on `Manage`, live-site status, `Open live blog`, and safe dashboard removal.
* The site manage page is organized by tabs: `Content` for import and article production queue, `Discovery` for topic signals, `Distribution` for autopublish/social settings, `Activity` for system/factory job logs, and `Setup` for webroot/CNAME/design settings.
* In the `Content` tab, imported records must be presented as already-live source-site pages, not as publication tasks. Use labels such as `Content inventory`, `LIVE / IMPORTED`, and `Open live page`; reserve generation actions for `QUEUED`/new Blog Core tasks.
* In content cards, social publishing status must be compact icon indicators, not large text pills. Unpublished/not queued channels should be visually muted; published/sent channels should appear active.
* Content card actions should stay compact: use an external-link icon for the live URL action, render `LIVE / IMPORTED` as a green status, and show content type with small badges such as `Blog` or `SEO money page`.
* Content inventory must not mix languages by default. Use language switching chips (`EN`, `RU`, `ES`, `DE`, `FR`) and filter content jobs by language server-side.
* Content inventory must also support content-type switching chips so operators can filter the same list by `All`, `Blog`, `SEO money page`, `Home`, or `Other` while preserving the selected language and pagination state.
* Content inventory sorting must be stable across languages. Sort imported pages by normalized base URL/path with the language prefix removed, so switching `EN/RU/ES/DE/FR` keeps the same article/topic positions when translations exist.
* Content inventory pagination should appear only once at the bottom of the list, centered, using compact numeric links and arrow icons without `Page X of Y` wording.
* Planned/future Blog Core publications should be visible separately from imported live pages. Show `Planned publications` at the bottom of Distribution, below the social channel settings, for `QUEUED`, `GENERATING`, `DRAFT`, and `ERROR` content jobs; imported live pages stay in Content inventory. If there are no planned jobs, keep the empty state compact.
* Discovery must be a two-step workflow: operators select topic signals, generate article idea candidates, review/select specific ideas, then add selected ideas to Planned publications. Selecting signals alone must not immediately create planned jobs.
* Discovery article ideas must be checked for similarity against existing imported/published and already planned site content before they are shown and again before they are queued. Topics that are too similar to existing content should be filtered or rejected instead of creating duplicate/near-duplicate planned tasks.
* Discovery must distinguish raw audience/search-demand signals from final article ideas. Search autocomplete signals are not time-filtered; period controls apply only to Reddit discussion signals. The UI/API should show raw, filtered, kept, and source-specific warnings so users understand why the visible count changes.
* Discovery UI should not force operators to review and check every raw audience signal before generating ideas. Raw signals are selected automatically after deep analysis, hidden from the main workflow, and summarized with counts/status. The article idea generation button stays disabled until signal analysis finishes.
* Long-running Discovery idea generation must show visible in-page progress, not only a toast or static loading text. The UI should show an active loader, elapsed time, and current stage while the article-ideas request is running.
* Discovery article idea generation should return as many valid editorial/SEO ideas as actually survive checks, not an arbitrary product target such as 4, 12, or 16. The generator may run multiple Gemini passes until a pass adds no new valid ideas, while a technical safety cap only prevents runaway cost/latency. UI/API should show accepted/generated/rejected/pass counts.
* Discovery article ideas must be formed from Google Search Central 2026 generative-search principles: unique, valuable, non-commodity, people-first pages that fit the connected site's business, audience, expertise, existing content, and SEO opportunity. Raw search/Reddit signals are audience-interest inputs, not titles.
* For product/commercial sites, Discovery should prefer concrete audience problems, business impact, decision context, product-category value, adoption blockers, ROI/efficiency context, objections, and misconceptions. It must not default to generic SERP-clone formats such as numbered listicles, `best/top tools`, review/comparison roundups, buyer frameworks, or build/setup/configuration tutorials unless the site's own topic strategy explicitly allows those editorial formats.
* Discovery article idea validation must reject obsolete years earlier than the current year and reject title formats that do not match the site's editorial policy. Editorial-format permissions should come from the site's scanned/profile strategy and settings, not from already-generated content that may contain bad old patterns.
* Discovery article idea cards must not display raw dirty autocomplete strings such as `best ... 2025` as the visible source/query line. `target_query_cluster` and the displayed source line should be normalized SEO clusters without obsolete years or generic SERP modifiers.
* Discovery must deduplicate article ideas semantically within the same generation run, not only by exact title. Multiple signals pointing to the same core problem should become one strong idea, not several near-duplicate cards.
* Discovery article ideas should carry explicit editorial diversity fields such as `topic_axis` and `audience_problem`. Same-run dedupe should compare these axes so the final idea set covers distinct problems/outcomes/funnel moments rather than several versions of the same commercial angle.
* Planned generation work should be shown as one canonical task per topic/path, not as separate tasks per language. The task should generate the site's configured languages. Legacy per-language factory rows may be preserved in the database for traceability, but the dashboard should collapse them by canonical group/base path and show extra old languages only as legacy variants.
* Planned task groups should support bulk operations from the dashboard. Bulk generate runs selected canonical tasks one by one from the browser to avoid long single-request timeouts. Bulk delete removes selected planned groups from Blog Core records/logs/social drafts only; it must not delete live source-site files.
* Long-running generation must show persistent in-page progress, not only a toast. When a task reaches `DRAFT`, the dashboard must provide a `Preview draft` action that opens the generated HTML before publishing.
* Any task with `status=GENERATING` must render an animated in-card progress indicator and poll its content-job API until it becomes `DRAFT` or `ERROR`. This is especially important for legacy/source factory jobs where the initial generate request returns immediately while the source factory continues asynchronously.
* `DRAFT` planned/content tasks must also expose an explicit `Regenerate draft` action. Regeneration should overwrite the current draft/artifacts for the same task instead of requiring deletion and re-queueing.
* Article/page draft generation must show visible progress while the request is running. Single-job generation should update both the in-page planned-publications progress area and the toast with elapsed time/stage text.
* Article/page draft generation must not ask Gemini to return a large raw HTML fragment inside a JSON string. That pattern causes malformed JSON when HTML attributes, quotes, or long fragments are not escaped perfectly. Blog Core should request structured article fields through Gemini `responseSchema` and render the final HTML server-side.
* Replaced/deprecated 2026-07-09: The previous malformed-JSON repair pass should not be the primary correctness mechanism for article/page generation. Generic JSON repair may remain as a fallback for non-article helpers, but article/page drafts should be correct by construction through structured schema output.
* Structured article rendering must preserve the full article/page block contract: one page title rendered outside the body, non-duplicated meta description and lead, TOC from section headings, 3 body figures, useful table, ordered list, quote, and 5-7 FAQ items. Do not regress back to short body-only drafts.
* Generic Blog Core article/page drafts must pass server-side validation before becoming `DRAFT`: minimum useful length, enough sections, exactly 3 body image specs, FAQ, table, and ordered list. Invalid structured output should fail with a clear generation error instead of being saved as a ready draft.
* Generic Blog Core article/page drafts must generate real JPEG article assets through Gemini Image: one hero image for cards plus 3 body images. Generated files live in ignored `data/article_assets/...` and are served by Blog Core asset routes. Imported legacy factory jobs continue to use their source factory output instead.
* Gemini Image article assets must use supported aspect ratios only. For generic article hero/body images, use `16:9`; do not use unsupported ratios such as `16:10`.
* For local imported sites with `root_path`, `Preview draft` must render through the real source-site HTML template/assets from the webroot, not through the generic Blog Core preview shell. The preview should be noindexed and preserve source-site visual classes, header, footer, and assets while replacing only the draft content area.
* Local imported-site draft previews may inherit the source template's `<base href="https://source-site/">`. Blog Core preview-only links inside generated draft bodies must therefore be rewritten to absolute Blog Core URLs for `/sites/.../article-assets/...`, and TOC fragment links must point to the current preview URL plus `#anchor`.
* Local imported-site draft previews should preserve source-site post-article sections that follow the main article/content block, such as recommendations, related content, newsletter/signup, or update blocks. Do this with template-pattern extraction, not domain-specific hardcoding.
* Local imported-site draft previews should adapt generic Blog Core FAQ markup to the source template's FAQ pattern when recognizable, such as `faq-grid`/`faq-card`, instead of always showing raw generic `<details>` styling.
* Distribution channel settings should not duplicate the same providers across separate blocks. Each channel card should combine connection status, Connect action, autopublish enablement, and include-link setting in one place.
* Social channel status in Distribution should point users to Setup when credentials are missing, show `configured` after credentials are saved, and `connected` only after a successful test.
* Imported section listing/hub pages such as `/blog/`, language blog indexes, `/wine-countries/`, and `/wine-regions/` may be stored as import metadata, but they must be hidden from the Content inventory work list so they are not confused with articles or publish tasks.

## 4. Integrations

* Design scanner fetches the connected homepage URL and captures title, meta description, stylesheet URLs, inline `<style>`, body class, nav/header/footer, colors, and fonts.
* If source CSS includes native patterns `.section`, `.blog-card`, `.blog-carousel`, and `.container`, generated blog pages reuse native-looking markup.
* Hosted CNAME blog routing uses `Host` header lookup against `sites.custom_blog_domain` when `hosted_blog_enabled=1`.
* CNAME status check compares resolved custom domain IPs against `HOSTED_BLOG_IPS` or the resolved `CNAME_TARGET`.
* Topic discovery must not use news feeds as the default source of "trends". Use broad non-news search/topic-demand signals and Reddit top discussions, derived from the site's Discovery direction/category hint/topic profile.
* Reddit signal fetching uses `https://www.reddit.com/search.rss` with top sorting; rate limits are expected and must be handled gracefully without rendering error cards. Reddit matches must include a strong site-topic anchor and contextual match; do not surface broad matches based only on generic words like `food`, `product`, or `shop`.
* Discovery signals should be broad/global topic signals suitable for scalable articles. Filter out city-specific, festival/event, ticket, local-opening, trade-promo/campaign/grant/retailer, navigation/source-specific autocomplete tails such as `youtube`/`reddit`, and one-off news signals before showing them as selectable search/Reddit items.
* Discovery topic normalization must preserve short meaningful category terms such as `AI` and `UGC`, normalize phrases such as `user generated content` to `ugc` and `e-commerce` to `ecommerce`, and not discard category-defining terms just because they also appear in the brand/domain. Relevance matching should use whole words, not accidental substrings inside unrelated words.
* Discovery topic selection must be content-informed across the whole connected site, not derived from one heading or the first words of a category hint. Query candidates should use scanned profile/settings plus existing imported/planned content titles, descriptions, categories, slugs, and URLs. For multilingual imports, prefer English/canonical content when enough records exist so non-English fragments do not become query seeds.
* Discovery query candidates should prefer multiword editorial/product clusters over single generic tokens such as `ai`, `questions`, or `support`. Single tokens may be anchors, but not the main query when content clusters exist.
* Article ideas must be generated by the journalist/SEO prompt from selected audience signals and existing-site context. Do not copy autocomplete suggestions or Reddit titles directly as article titles; generated ideas need SEO intent/rationale and must be checked against already imported/published/planned content.
* The journalist/SEO prompt must first understand the site, then cluster audience signals into real needs, and only then produce article ideas with target query clusters, business relevance, unique site context, and duplicate-check rationale.
* Existing blog import scans sitemap and `/blog/` index sources for external sites. If a connected site has a local `root_path`, import must prefer direct webroot discovery and include multilingual `/blog/` pages plus SEO money pages under `wine-countries` and `wine-regions`.
* Social credentials are stored per site in SQLite `social_connections.credentials_json`; secrets must not be rendered back into the page, committed, or written to memory files.
* Social post adaptation uses `social_posts` for per-channel drafts. Current hard limits are LinkedIn 3000, Telegram 4096, X/Twitter 280, Tumblr 4096, and Pinterest description 500 characters. The generator uses the article language from `content_jobs.sources_json.language` when present, falls back to the site's first configured language, and rejects/squeezes output before saving if it would exceed the channel limit.
* Replaced/deprecated 2026-07-03: The earlier production state note saying `yas.wine` import found only 61 English `/blog/` URLs was an incomplete external-scan result, not a complete import.
* Current production state: On 2026-07-03, `yas.wine` site `id=5` was fully imported from local webroot `/var/www/yaswine`. Blog Core now has 821 distinct `content_jobs.status=IMPORTED`: 426 blog pages and 395 SEO money pages. All records have `published_url` on `https://yas.wine/...` and `sources_json.webrootPath` pointing to the source file.
* Replaced/deprecated 2026-07-03: The earlier `myugc.studio` import as `public_sitemap` with 343 records was based on checking the wrong local path (`/var/www/my-ugc-studio`). The public site is served by nginx from `/var/www/landing`, not `/var/www/my-ugc-studio`.
* Current production state: On 2026-07-03, `myugc.studio` site `id=6` was reconnected to Blog Core with `root_path=/var/www/landing` and `access_type=local_path`. Blog Core reimported 442 distinct existing blog URLs directly from the local VPS webroot with `sources_json.webrootPath` pointing to `/var/www/landing/...`: EN 88 stored records, DE 89, ES 89, FR 89, RU 87. The Content inventory hides hub pages such as `/blog/`, so EN shows 87 visible article records.
* Current production state: On 2026-07-03, `solocruz.com` site `id=7` was connected to Blog Core with `root_path=/var/www/solocruz.com` and `access_type=local_path`. Blog Core imported 75 existing blog URLs directly from the local VPS webroot with `sources_json.webrootPath` pointing to `/var/www/solocruz.com/...`: EN 15, RU 15, ES 15, DE 15, FR 15. Records are `status=IMPORTED`, `pageType=blog`, and keep `https://solocruz.com/...` as the source-site authoritative `published_url`.
* Current production state: On 2026-07-03, `laycanmatch.com` site `id=8` was connected to Blog Core with `root_path=/var/www/laycanmatch.com` and `access_type=local_path`. Blog Core imported 6 existing English blog URLs directly from the local VPS webroot with `sources_json.webrootPath` pointing to `/var/www/laycanmatch.com/...`: 5 article pages plus the `/blog/` hub metadata record. The Content inventory hides the hub, so 5 imported live article records are visible.
* Replaced/deprecated 2026-07-04: The initial `airep24.com` import moved only 16 English `/blog/` URLs from `/var/www/airep24.com`; that was not a complete factory migration.
* Current production state: On 2026-07-04, `airep24.com` site `id=9` was connected to Blog Core with `root_path=/var/www/airep24.com` and `access_type=local_path`, then fully migrated from `/var/www/content-factory-airep24/factory.sqlite`. Blog Core now has 80 AIREP24 `content_jobs`: 24 `IMPORTED` inventory records and 56 legacy `QUEUED` planned rows. The imported inventory contains the original 16 English blog/webroot records plus 8 legacy published factory records: 4 localized home pages and 4 localized `features/automated-knowledge-base` SEO money pages. The planned queue contains 20 blog rows and 36 SEO money-page rows with EN/DE/ES/FR legacy variants preserved in `sources_json`; the dashboard collapses those rows into 14 canonical planned tasks. AIREP24's active site language is EN only (`sites.languages=["en"]`), so new generation should target EN unless the site's language setting is changed.
* Current production state: On 2026-07-09, AIREP24 had duplicate comparison static paths for `airep24-vs-live-chat`: canonical `/comparisons/airep24-vs-live-chat/` and old `/compare/airep24-vs-live-chat/`. The old `/compare/...` page was manually synchronized with the canonical page in `/var/www/airep24.com/compare/airep24-vs-live-chat/index.html` and `/var/www/airep24-landing/compare/airep24-vs-live-chat/index.html` so it includes images, TOC, and FAQ.

## 5. SEO / content rules

* Hosted blogs serve `robots.txt` and `sitemap.xml` for the custom host.
* Hosted sitemap includes `/blog/` plus imported/generated public `content_jobs` when available; otherwise it falls back to the sample article.
* Local install writes `sitemap-blog.xml` and appends its URL to target site's `robots.txt` when possible.
* Generated sample blog/article content is placeholder-level and should not be treated as final editorial content. Existing blogs can be imported as `content_jobs.status=IMPORTED` while preserving original slugs, canonical/source URLs, metadata, and saved HTML.
* Legacy factory job migrations should preserve old factory IDs and target paths in `sources_json`; unfinished old `NEW` jobs should become Blog Core planned jobs (`QUEUED`) rather than imported live pages.
* Article ideas generated from trend/discussion signals are queued as jobs and should connect audience problems/questions to the site's offer, expertise, or editorial point of view.
* Article idea generation from Discovery signals should not create `content_jobs` directly. Only the selected ideas submitted through the queue step should create `content_jobs.status=QUEUED`.
* Final publishing parity is still incomplete: local static `/blog` install writes the sample shell, while hosted rendering can serve imported/generated content jobs.
* For imported blogs, the target behavior is not a public Blog Core mirror. Imported content should let Blog Core understand, display, manage, update, and create tasks for the existing blog while preserving the original live URL structure. The original site URL remains the canonical/authoritative destination unless an explicit cutover is requested.
* For imported local sites, distinguish Blog Core dashboard UI from the source site's public UI. Fixes requested against `https://yas.wine/blog/` usually require editing `/var/www/yaswine`, not only Blog Core's `/sites/<id>` dashboard.

## 6. Deployment

* Runtime command: `./run.sh`.
* `run.sh` loads `/var/www/blog.yas.ooo/.env` before starting Gunicorn; this is where live Gemini/Google API keys and model env vars should be configured. Do not commit `.env`.
* Gunicorn binds `127.0.0.1:3299` with 2 workers and 120 second timeout.
* PM2 process name: `blog-yas-core`.
* Public dashboard domain: `https://blog.yas.ooo`.
* Live nginx `blog.yas.ooo` vhost proxies to `http://127.0.0.1:3299`.
* Live default catchall nginx config proxies unknown HTTP/HTTPS Host traffic to Blog Core so CNAME domains can be routed by the Flask app.
* Current vhost/catchall configs reference self-signed certificate paths. Automated public SSL issuance for arbitrary custom domains is not yet implemented.
* Repository clone path for local Codex work: `/Users/yasyas/Library/Mobile Documents/com~apple~CloudDocs/проекты/blogcore`.
* Canonical GitHub repo: `yasyarik/blogcore`; local clone currently uses HTTPS remote because SSH publickey auth was unavailable locally.
* Important environment variables:
  - `PORT` default `3299`.
  - `ADMIN_HOSTS` default `blog.yas.ooo,127.0.0.1,localhost`.
  - `CNAME_TARGET` default `blog.yas.ooo`.
  - `HOSTED_BLOG_IPS` default `72.61.1.109`.
  - `GEMINI_API_KEY` or `GOOGLE_API_KEY` enables Gemini site analysis and article generation.
  - `GEMINI_TEXT_MODEL`, `GEMINI_MODEL_TEXT`, or `GEMINI_MODEL` can override the text model.
* Never store secrets or raw `.env` values in memory files.

## 7. Known pitfalls
* Source-authoritative imported/legacy job previews must not use the generic Blog Core renderer. If the source factory has no native unpublished preview, open the recorded source-site URL or show a clear unavailable state instead of faking a Blog Core-styled page.

* Imported/static site fixes must preserve the site's own tracked static source and stylesheet. For AIREP24-style static pages, do not republish through a generic factory/template pipeline for a surgical copy fix; restore from the site repo/webroot source first, then change only the requested markup.


* `data/blog_core.sqlite3` is ignored; Git commits do not preserve connected sites/jobs/theme profiles.
* The scanner handoff idempotency mapping is stored in the ignored `source_scanner_drafts` SQLite table; do not reconstruct it by title matching.
* `previews/` is ignored and regenerated.
* The live catchall nginx config is important for CNAME routing but is not currently represented in `deploy/nginx-blog.yas.ooo.conf`.
* HTTPS for arbitrary CNAME domains is not production-complete until certificate automation is added.
* Reddit may return `429 Too Many Requests`; topic discovery must surface it as a note/warning, not as a selectable signal card.
* Replaced/deprecated 2026-07-05: Google News RSS must not be used or labelled as a trend source. Discovery now uses Google autocomplete/search suggestions as a non-news popular-search signal source; this is still not the official Google Trends API.
* Do not turn Discovery into a local event or trade-promo feed. Results like a city wine festival, local guide, `Indies to receive £250 for Bordeaux Wine Month`, or retailer campaign should be filtered out even if they contain topical words.
* Do not make the Discovery period selector appear to apply to every source. It applies to Reddit discussions only; search-demand/autocomplete signals have no date filter.
* `install-blog` writes static files into `root_path/blog`; avoid using it for external sites with no local webroot.
* Theme scan depends on public HTML/CSS structure and may fail or capture weak design context for SPA-heavy or protected sites.
* If Gemini env vars are missing, `Scan design` still succeeds but topic-profile inference falls back to homepage title/description heuristics. This should be treated as degraded behavior, not the desired production path.
* `SEO_MEMORY.md` had an older note that dynamic sitemap expansion was not implemented. As of the imported/generated content job renderer, that note is replaced for hosted CNAME blogs; local static install still lacks final article publishing/export parity.
* Replaced/deprecated 2026-07-03: Existing blog import no longer has to rely on `sitemap_index.xml` for local VPS sites with `root_path`. For local sites such as `yas.wine`, direct webroot discovery is the authoritative inventory path.
* Production API may reject default Python `urllib` requests with `403`; use a normal User-Agent for scripted verification/import calls.
* Factory job messages may contain large JSON payloads from import/article-idea jobs. UI must render summarized job messages, not raw `publish_jobs.message`, or the dashboard becomes unreadable.
* Do not collapse content queue, discovery, distribution, setup, and activity logs into one long page again; keep these concerns separated in the tabbed manage UI.
* Do not show `Generate draft` on `IMPORTED` records; that makes already-published source pages look like unpublished tasks.
* Do not render per-channel social status as full-width text buttons/pills inside content cards; use compact icons with tooltips.
* Do not use a large text button for `Open live page` in content cards; use the compact external-link icon.
* Do not mix imported multilingual content in one default Content inventory list; default to a concrete language and require explicit language switching.
* Do not sort language-specific inventories by import timestamp/id; this makes each language show different first articles. Use normalized base path sorting instead.
* Do not place planned/future publication tasks in the Content inventory area; keep them at the bottom of Distribution below social channel settings.
* Do not render content pagination both above and below the cards, and do not use verbose `Page`/`Showing` text there.
* Do not show Publish Channels, include-link checkboxes, and connection status as three separate repeated channel sections. Use one unified card per social provider.
* Do not show active-looking `Connect` buttons for social providers without a credential setup/test path. Setup is the place to enter keys/tokens and test connections.
* Large imports need pagination in the Content inventory. Do not return to a hard-coded latest-24 list without navigation.
* Do not confuse Blog Core Content inventory pagination with public source-site blog pagination. `yas.wine/blog/` is a static public page in `/var/www/yaswine/blog/index.html`; its visible pagination must be fixed in that webroot.
* Do not render local imported-site draft previews with the generic Blog Core shell; that makes operators review the wrong design. Use the source site's local HTML template and assets.
* Do not leave Blog Core preview-only asset URLs or TOC `#anchor` links relative inside source-site templates that contain `<base>`, or browsers will resolve them against the source domain instead of the Blog Core preview page.
* Do not solve missing source-site blocks such as recommendations/newsletter locally per domain. Preserve recognizable post-article template sections generically for all imported local sites.
* Do not show setup/bootstrap actions on imported live-site cards; scanning/building/installing is for new Blog Core sites, not already imported production blogs.
* Do not generate imported legacy factory jobs with the generic Blog Core prompt. If the source factory rejects a draft, surface that error instead of keeping a weaker Blog Core-generated draft.
* Do not remove article TOC, FAQ, body figures, tables, ordered lists, quotes, length validation, or real article image generation when changing the structured article schema/prompt.
* Do not make operators delete a planned/content task just to fix a bad generated draft. Provide explicit regeneration for `DRAFT` tasks.
* Do not represent active `GENERATING` tasks as only a static badge. Show motion/progress, latest log/status text, and auto-refresh when finished.
* Do not rely only on in-memory daemon threads to finish legacy/source factory synchronization. PM2/Gunicorn restarts can kill those threads while the source factory continues and finishes; polling/status endpoints must be able to recover and sync the finished draft.
* For AIREP24 comparison pages, watch for old `/compare/...` static paths alongside canonical `/comparisons/...` paths. A fixed Blog Core draft can still appear broken publicly if an old static alias is serving stale shortened HTML.
* Factory v3 article pages must not render a second title/subtitle immediately after the hero. Keep the original article media/layout structure, including the top `article-head` image where applicable, but remove only the duplicated heading and lead copy from that block.
* Do not invent Gemini Image aspect ratios. Check provider-supported values before changing image generation contracts.

## 8. Decisions log

### 2026-07-21 — Explicit native publication scheduling

* Decision: Use a separate single PM2 worker and a per-job UTC `scheduled_for` value for automated page publication.
* Reason: The former cadence setting was UI/database-only. Explicit per-job scheduling avoids accidental publication of unrelated drafts and preserves source factories as the template and publisher authority.
* Files/areas affected: `app.py` scheduler contract, `scheduler.py`, `run-scheduler.sh`, `content_jobs` SQLite migration, PM2 deployment.
* Replaced/deprecated: A `publishing_cadence` value by itself is not treated as an active scheduler.

### 2026-07-21 — Source-factory blog validation alignment

* Decision: Align the source-factory writer brief with its blog validator: six to eight H2 sections, at most twelve H3 sections, and contextual blog links only where no real non-blog link inventory is supplied.
* Reason: The old source prompt demanded 20-40 H3 while the validator capped articles at 16, and it required a non-blog link that the blog-generation contract did not provide.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/generate.py`, `/var/www/content-factory-solocruz/factory/validate.py`.
* Replaced/deprecated: The contradictory 20-40 H3 blog instruction and impossible non-blog link requirement.

### 2026-07-21 — Native SEO-page article asset URLs

* Decision: Native SEO-page rendering resolves generated article media from the shared absolute `/blog/` asset folder.
* Reason: SEO pages are published in nested route directories, so bare media filenames incorrectly resolve relative to the page URL and make otherwise generated hero/inline images appear missing.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/seo_waitlist.py`.
* Replaced/deprecated: Relative generated article-media URLs in nested native SEO pages.

### 2026-07-21 — Native source-site chrome

* Decision: Native static publication extracts the header and footer from the source site's locale homepage and loads its existing CSS/JS assets.
* Reason: A source factory is a control-plane publisher, not a replacement theme. Its fallback chrome is visibly incomplete and must only be used when source chrome is unavailable.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/seo_waitlist.py`.
* Replaced/deprecated: Default factory navigation/footer on pages for sites that already provide native chrome.

### 2026-07-21 — Native page identity and language links

* Decision: Native static pages copy favicon/manifest identity tags from the source homepage. A copied language switch is rewritten to link only to published locales of the current canonical page; it is omitted when no translation exists.
* Reason: A homepage language menu on an article silently sends a reader away from the article, and generic factory pages must not show a browser icon that differs from the connected site.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/seo_waitlist.py`.
* Replaced/deprecated: Reusing source-homepage language URLs verbatim on article pages and dropping source favicon assets from generated page heads.

### 2026-07-21 — SoloCruz article locale set

* Decision: A multilingual SoloCruz article is a canonical group of native source-factory jobs, one per published locale and native route. Publish the complete set, then re-publish each member so hreflang and the native language switch see every real counterpart.
* Reason: A single EN job cannot provide translations; copying a homepage switch is not an acceptable substitute for article-localized routes.
* Files/areas affected: source-factory job records and `/var/www/content-factory-solocruz/factory/seo_waitlist.py` publication behavior.
* Replaced/deprecated: Treating a single source job as a completed multilingual article.

### 2026-07-21 — Native SEO publication index and hero contract

* Decision: Native SEO blog publication must update the matching locale blog index and feed while preserving manually authored index cards; factory cards are maintained in a separate marked block. When a hero image exists, render it as unobstructed full-height media rather than placing generic copy over it.
* Reason: A published page is incomplete when it is absent from `/blog/`, and an image asset loses its purpose when template text obscures it.
* Files/areas affected: `/var/www/content-factory-solocruz/app.py`, `factory/landing.py`, and `factory/seo_waitlist.py`.
* Known issue: SoloCruz sitemap files are rebuilt and publicly referenced in `robots.txt`, but automated Google Search Console submission is not operational because the configured service-account credential file is absent. Do not claim a submission succeeded until an authorized credential is configured.

### 2026-07-21 — Source-factory publishing adapter audit

* Decision: Keep each source factory's native rendering adapter where it already preserves site chrome and asset behavior; do not force a single SoloCruz renderer onto unrelated sites.
* Reason: Published URL and media contracts differ by site. The SoloCruz nested-route asset fix is not evidence that YAS Wine, My UGC Studio, LaycanMatch, PipsAlerts, or AIREP24 use the same path model.
* Files/areas affected: source-factory audit across YAS Wine, My UGC Studio, SoloCruz, LaycanMatch, AIREP24, and PipsAlerts.
* Known issue: An old AIREP24 French job is marked published at a now-missing URL. It must be repaired through an explicit locale/path migration, not automated republishing.

### 2026-07-01 — Store durable project memory in repo

* Decision: Add `AGENTS.md` and `docs/` memory files requiring Codex to read memory before non-trivial work and update changelog after each task.
* Reason: Prevent loss of project knowledge after context compaction or fresh Codex sessions.
* Files/areas affected: `AGENTS.md`, `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md`, and supporting docs.
* Replaced/deprecated: Ad hoc reliance on chat history only.

### 2026-07-01 — Use hosted CNAME blogs for external sites

* Decision: External sites should point a custom blog domain to `blog.yas.ooo`; Blog Core routes by `Host` and serves that site's blog.
* Reason: This avoids needing filesystem, Git, CMS, SSH, or SFTP access for arbitrary client sites.
* Files/areas affected: `app.py`, nginx catchall config, site settings.
* Replaced/deprecated: Assuming every site can be installed via local webroot.

### 2026-07-01 — Keep technical settings behind a gear on factory pages

* Decision: The site factory page should prioritize discovery/jobs and hide technical setup/design controls behind a settings gear.
* Reason: Factory workflow should focus on content operations, not large technical panels.
* Files/areas affected: `app.py` manage page HTML/CSS/JS.
* Replaced/deprecated: Large always-visible design/publishing panel.

### 2026-07-01 — Topic discovery must prioritize usable signals over filled grids

* Decision: Google/Reddit source errors are returned as warnings, not selectable cards. Reddit results must be top discussions and strongly title-relevant to the site topic, with a real site-topic anchor plus context. Low-relevance Google/Reddit results should be filtered instead of padding the grid.
* Reason: The dashboard should generate useful article ideas from strong signals, not from rate-limit errors or unrelated posts.
* Files/areas affected: `app.py` topic signal fetchers and manage-page signal UI.
* Replaced/deprecated: Displaying disabled error cards such as `Reddit unavailable: HTTP Error 429`.

### 2026-07-01 — Blog Core must reach YAS Wine factory parity per site

* Decision: Blog Core should preserve the operational capabilities of `/var/www/content-factory-yaswine`, but with every setting/job/social connection scoped by `site_id`.
* Reason: Blog Core is meant to become a universal multi-site article factory, not a single-site wine factory clone.
* Files/areas affected: `app.py`, `docs/FACTORY_PARITY.md`, future factory/social/publish modules.
* Replaced/deprecated: One-site global factory settings and wine-only prompt assumptions.


### 2026-07-01 — Import existing blogs without changing live URLs

* Decision: Existing `/blog/` articles should be scanned from sitemap/index URLs and imported into Blog Core as `content_jobs` with `status=IMPORTED`.
* Reason: This lets sites such as `yas.wine` or `airep24.com` move onto Blog Core without losing indexed URLs, metadata, or existing article HTML.
* Files/areas affected: `app.py` import scanner/import endpoints and hosted blog renderer.
* Replaced/deprecated: Rebuilding or overwriting existing blog content as the first migration step.

### 2026-07-03 — Keep project memory self-updating after local repo setup

* Decision: Treat repository memory files as the durable source of truth for future Codex runs and require a final memory-status line after every task.
* Reason: The project is now in a separate local clone and future sessions may start after context compaction or from a fresh Codex launch.
* Files/areas affected: `AGENTS.md`, `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`.
* Replaced/deprecated: Relying on the current chat or older VPS-only context as the only memory source.

### 2026-07-03 — Imported blogs are managed in place, not mirrored by default

* Decision: For existing imported blogs, Blog Core should be the management/control plane and publish generated updates/articles back to the same original site locations and URL structure. Blog Core should not default to hosting an indexed second copy. For new blogs created entirely by Blog Core, Blog Core may fully host/publish the blog.
* Reason: Imported sites such as `yas.wine` already have working indexed blogs. The goal is to preserve those URLs and operations while adding a stronger dashboard/factory layer.
* Files/areas affected: Import model, publishing/export pipeline, hosted renderer SEO rules, future local/CMS/static publisher.
* Replaced/deprecated: Treating all imported content as if it should become public under Blog Core-hosted URLs.

### 2026-07-03 — Hide imported hub pages from content work lists

* Decision: Keep imported section index pages in metadata, but hide them from the Content inventory and paginate the visible records.
* Reason: Pages such as `https://yas.wine/blog/` are blog listing/hub pages, not article records or publication tasks. Showing them beside articles confused the imported-content workflow.
* Files/areas affected: `app.py` content job listing/rendering and `/api/sites/<id>/content-jobs`.
* Replaced/deprecated: Showing all latest imported `content_jobs` with `limit 24`, including `/blog/` and other section indexes, without pagination.

### 2026-07-05 — Discovery uses non-news topic demand

* Decision: Replace Google News RSS-based discovery with Google autocomplete/search suggestions plus Reddit top discussions. Apply this globally to all current and future sites.
* Reason: Blog Core Discovery should find broad popular topic demand, not local news, events, festivals, campaigns, or trade promotions.
* Files/areas affected: `app.py` topic signal API/UI, `docs/INTEGRATIONS.md`.
* Replaced/deprecated: Treating Google News RSS results as trend/topic signals.

### 2026-07-05 — Discovery ideas are reviewed before queueing

* Decision: Discovery now separates signal selection, article idea generation, operator idea selection, and queue creation. Similarity checks run before ideas are shown and again before selected ideas become planned jobs.
* Reason: Operators need to choose from generated article topics, and Blog Core must avoid suggesting/queueing near-duplicates of already published/imported or planned site content.
* Files/areas affected: `app.py` Discovery API/UI and `content_jobs` queue creation.
* Replaced/deprecated: Immediately creating `content_jobs` from checked Discovery signals.

### 2026-07-05 — Pinterest social drafts use native pin specs

* Decision: Add Pinterest as a per-site social channel and generate native pin draft specs instead of treating it as a plain text post.
* Reason: Pinterest needs vertical image creative, overlay/caption text, description, alt text, and destination URL metadata based on the article.
* Files/areas affected: `app.py` social provider config, social draft generation, Distribution/Setup UI, SQLite migrations.
* Replaced/deprecated: Treating all social channels as only text-length-limited post drafts.

### 2026-07-05 — Instagram drafts must show real publishable creatives

* Decision: Add Instagram as a per-site social channel whose drafts are carousel creatives with a caption and real 4:5 JPEG slide files generated by Gemini Image.
* Reason: Operators need to see the actual visual result that the factory will publish to Instagram, not a fast SVG/layout mockup.
* Files/areas affected: `app.py` social provider config, social draft generation, `social_posts`, ignored `data/social_assets`.
* Replaced/deprecated: Using SVG or placeholder-only previews for Instagram carousel review.

### 2026-07-05 — Instagram publishing uses an intermediary

* Decision: Treat Instagram as a per-site channel backed by a third-party publishing server. Blog Core stores intermediary API credentials and generated creatives; it must not directly publish through Instagram Graph API.
* Reason: The project publishes Instagram through a separate server-side intermediary.
* Files/areas affected: `app.py` Instagram social provider config, Setup credential labels, future publish route.
* Replaced/deprecated: Direct Instagram Graph API publishing assumptions in Blog Core.


### 2026-07-09 — Recover legacy factory drafts during status polling

* Decision: `GET /api/sites/<site_id>/content-jobs/<job_id>` re-checks legacy/source factory jobs that are still `GENERATING` in Blog Core and syncs completed `READY`/`PUBLISHED` drafts back into Blog Core.
* Reason: Legacy generation starts asynchronously; Blog Core PM2/Gunicorn restarts can kill the in-memory sync thread while the source factory continues and finishes successfully.
* Files/areas affected: `app.py` legacy factory generation/status sync and planned-publications polling.
* Replaced/deprecated: Assuming the original daemon thread is the only path that can move a legacy job from `GENERATING` to `DRAFT`.

### 2026-07-10 — Preview source-factory drafts natively

* Decision: For a source-authoritative `DRAFT` with a v3 payload, Blog Core proxies a native preview built by the original factory. The factory temporarily stages the payload and builds it without publishing, then binds the draft fields into semantic slots of the actual current source-page HTML template from the local webroot. The factory restores the v3 source files afterwards. Blog Core adds the source origin as `<base>` so CSS and asset URLs resolve to the real site.
* Reason: A generic Blog Core renderer, a stale v3 shell, or v3 markup injected into a live shell can all show the wrong page template. Preview must retain the live page's actual hero, article blocks, TOC, FAQ, recommendations, header/footer, and source-specific classes while replacing content values only.
* Files/areas affected: `Blog Core app.py` source-factory preview proxy; `content-factory-airep24/app.py` native v3 preview builder.
* Replaced/deprecated: Redirecting every source-authoritative draft preview to the live source URL, rendering it with the generic Blog Core/local-template preview shell, using a stale factory v3 shell, or injecting foreign v3 layout markup into the current source-site shell.

### 2026-07-13 — Preserve canonical paths when rewriting legacy content

* Decision: A queued content job can set `sources_json.preserveSlug=true` to lock its existing slug. Generic Blog Core generation may rewrite the title and body but must retain that canonical slug.
* Reason: Rewriting legacy content should improve the page without breaking its established URL, inbound links, or search history.
* Files/areas affected: `app.py` generic draft generation; `content_jobs.sources_json` migration metadata.
* Replaced/deprecated: Allowing a model-proposed slug to replace a preassigned canonical legacy path.

### 2026-07-13 — YAS legacy blog rewrite queue

* Decision: `yas.ooo` is connected in Blog Core as a local site rooted at `/opt/yas-ooo`. Its 12 existing English `/blog/<slug>/` topics are queued for full rewrites, not imported as duplicate public content. Its Next app reads Blog Core-managed JSON records from `data/blog-core/drafts` and `data/blog-core/published`.
* Reason: Blog Core should become the control plane and factory for future YAS content while preserving existing URLs. Draft generation and publishing remain separate actions; Preview writes only a noindex draft record, while Publish atomically writes the public record.
* Files/areas affected: ignored live `data/blog_core.sqlite3` site/job records; Blog Core `native-content-store` adapter; `/opt/yas-ooo` dynamic blog/home/sitemap content readers and preview route.
* Replaced/deprecated: Treating legacy YAS articles as a separate migration/copy target.

### 2026-07-13 — Native Next content-store publisher contract

* Decision: For a local Next site marked with `publicationMode=native_next_content_store` (the former YAS compatibility value `native_yas_publisher` remains supported), Blog Core saves generated drafts as JSON under `<root>/data/blog-core/drafts/<job>.json`. Preview redirects to `/content-preview/<job>` on the source site; explicit Publish atomically writes `<root>/data/blog-core/published/<slug>.json` and marks the Blog Core job `PUBLISHED`.
* Reason: The source site retains its own components and visual system. Content changes do not require reauthoring TypeScript arrays, rebuilding the website, or using the generic Blog Core static installer.
* Files/areas affected: `app.py` publication and preview routes; YAS `src/lib/managed-content.ts`, `ManagedArticle`, dynamic `/blog`, `/blog/[slug]`, `/content-preview/[jobId]`, homepage insights, and sitemap.
* Replaced/deprecated: Generic local HTML preview/install for YAS-generated content.

### 2026-07-13 — Native SEO use-case content type for YAS

* Decision: YAS has an indexable `/use-cases/` hub and four initial decision-oriented money pages. The Next content store recognizes `use_case`, `seo_money_page`, and `seo-money-page` publication types as managed `use_case` content, separate from the blog feed.
* Reason: Commercial intent pages need their own information architecture, service linkage, canonical routes, and sitemap entries; they should not be mixed into editorial blog output.
* Files/areas affected: YAS `src/content/use-cases.ts`, `/use-cases` routes, header navigation, dynamic sitemap, and the Blog Core native content-store payload.
* Replaced/deprecated: Treating every generated content task as a blog article regardless of its target page type.

### 2026-07-13 — Discovery routes SEO money pages by content type

* Decision: The universal Discovery journalist prompt may return `contentType=seo_money_page` only for a durable, service-aligned use case. Queueing normalizes this to a canonical `/use-cases/<slug>/` target with `pageType=seo_money_page`; editorial ideas retain `/blog/<slug>/`.
* Reason: Content type must drive destination and publication behavior. A commercial intent signal alone is not enough to make a money page.
* Files/areas affected: `app.py` Discovery prompt, idea sanitizer, and article-idea queue route.
* Replaced/deprecated: Defaulting all Discovery output to blog paths after the model had classified a page as a money page.

### 2026-07-13 — Native YAS sitemap is publication-driven

* Decision: The YAS `sitemap.xml` route is dynamic and reads the native content store at request time.
* Reason: A Blog Core Publish action must expose its new canonical blog/use-case URL to crawlers immediately without a Next rebuild.
* Files/areas affected: `/opt/yas-ooo/src/app/sitemap.ts`.
* Replaced/deprecated: Build-time-only sitemap output for native published content.

### 2026-07-13 — Preserve the YAS use-cases visual system for factory output

* Decision: The user-owned YAS `/use-cases/` cinematic design is the authoritative template. Published factory use cases append to its existing operating-case list, and their detail/preview pages use the same dark `useCasesFilm` visual system.
* Reason: Blog Core is the content factory/control plane, not a replacement for the source site's design. A use-case publication must not fall back to the generic light article template.
* Files/areas affected: YAS `use-cases/page.tsx`, `use-cases/[slug]/page.tsx`, `use-cases.module.css`, `ManagedUseCasePage`, and `content-preview/[jobId]/page.tsx`.
* Replaced/deprecated: Rendering managed use-case detail and preview pages through `ManagedArticlePage`.

### 2026-07-13 — YAS content queue focus excludes Shopify

* Decision: Remove the queued YAS rewrite tasks whose subject is Shopify. The current YAS editorial focus is not Shopify.
* Reason: The queue must reflect the active positioning of the site rather than preserve historical topic inventory by default.
* Files/areas affected: Ignored live `data/blog_core.sqlite3` YAS planned content jobs.
* Replaced/deprecated: The initial Shopify-oriented subset of the YAS legacy rewrite queue.

### 2026-07-13 — Receive finished YAS Studio drafts as Blog Core tasks

* Decision: Accept explicitly selected YAS Source Scanner drafts through an authenticated endpoint and store them as native `yas.ooo` `DRAFT` jobs.
* Reason: Studio is the authoring desk; Blog Core already owns the native YAS review, publication and distribution controls.
* Files/areas affected: `source_scanner_drafts`, `content_jobs`, native YAS draft store, source-scanner integration API.
* Replaced/deprecated: The old scanner-brief-only handoff does not represent an authored Studio article and is not used for this workflow.

### 2026-07-13 — Per-site Zernio transport for social publishing

* Decision: X/Twitter, Pinterest, Instagram, Threads, and Reddit use one per-site Zernio connection with explicit connected-account mappings. Blog Core owns per-channel draft generation, native assets, validation, review, and explicit submission; Zernio owns OAuth accounts and delivery.
* Reason: The same five networks must not be configured or published through unrelated direct integrations. Per-site account mappings prevent content from being sent to the wrong brand account.
* Files/areas affected: `app.py` social connections, drafts, Zernio publish route, Setup/Distribution UI, ignored social assets and social post records.
* Replaced/deprecated: Direct per-network connection forms for X, Pinterest, Instagram, and Threads. Existing legacy credentials remain stored but are not considered active for these channels.

### 2026-07-13 — Native social editorial contracts

* Decision: Social drafts must select a channel-native editorial format rather than produce a generic article summary. Instagram carousels carry a validated type/slide structure; Threads carries a conversation format; X can carry a validated thread sequence; Pinterest produces a finished 2:3 JPEG Pin; Telegram and Tumblr drafts include their own editorial image metadata; Reddit carries a community-first title/body and site-configured subreddit rules.
* Reason: Character limits alone do not produce content that fits a network or earns meaningful engagement.
* Files/areas affected: `app.py` social prompt builders, validators, asset generation, social review routes.
* Replaced/deprecated: One generic text-only social prompt for all providers.

### 2026-07-13 — LinkedIn personal-profile OAuth connection

* Decision: Blog Core provides a server-side OAuth authorization-code flow for LinkedIn personal-profile publishing. The configured callback is `https://blog.yas.ooo/oauth/linkedin/callback`; successful authorization stores only the issued access token and `urn:li:person:<id>` for the selected site.
* Reason: Client ID/secret are application credentials, not a publish token or author identity. Operators should not copy temporary access tokens or URNs manually.
* Files/areas affected: server-only `.env` (ignored), `app.py` OAuth start/callback routes and LinkedIn Setup card.
* Replaced/deprecated: Pasting a manually obtained LinkedIn access token and personal URN into the Setup form.

### 2026-07-13 — Podcast production is a separate reviewable content workflow

* Decision: Blog Core creates podcast episodes from existing article content through a per-site workflow: script generation, Gemini TTS audio generation, review, then explicit publication to a stable Blog Core episode URL and RSS feed.
* Reason: Audio generation must not implicitly publish an episode or overwrite an imported site's native design. Podcast assets and publication state need the same traceability as article and social work.
* Files/areas affected: `podcast_settings`, `podcast_episodes`, ignored `data/podcast_assets/`, Podcast dashboard tab, podcast API/routes and RSS feed.
* Replaced/deprecated: Treating an article narration as an untracked one-off asset or automatic source-site publication.

### 2026-07-15 — Source-factory bindings make Blog Core an imported-site control plane

* Decision: Imported sites with their own compatible factory are bound through `site_factory_bindings`. Blog Core creates new work in that source factory, then delegates generation, native preview, and explicit publication to it while synchronizing the job state into its own dashboard.
* Reason: The source factory remains authoritative for its current template, image workflow, validation, URLs, and deploy process. Blog Core must manage that workflow without creating a parallel public blog or modifying the source design.
* Files/areas affected: `app.py` factory-binding helpers and new-job delegation; ignored `data/blog_core.sqlite3` bindings and imported job inventory.
* Replaced/deprecated: Creating a generic Blog Core job for a source-authoritative site and attempting to render or publish it through the generic pipeline.

### 2026-07-15 — PipsAlerts factory imported as source-authoritative

* Decision: `pipsalerts.com` is managed through its existing `content-factory-pipsalerts` FastAPI factory on the same VPS. Its public content stays at `/guides/{slug}/`; the local Next site and factory remain the only publisher/template authority.
* Reason: PipsAlerts already has a working factory and native guide architecture. The dashboard should expose its content inventory and initiate work in the existing system rather than recreate the guides in Blog Core.
* Files/areas affected: PipsAlerts site record, `site_factory_bindings`, and imported `content_jobs` in ignored Blog Core SQLite data.
* Replaced/deprecated: Treating the PipsAlerts guide collection as a new generic `/blog/` installation.

### 2026-07-16 — SoloCruz source factory bound to Blog Core

* Decision: `solocruz.com` is managed through `content-factory-solocruz` as a source-authoritative factory. Blog Core passes the complete native page contract when it creates a source job: content type, page kind, locale, target path, and canonical group.
* Reason: A source factory needs more than a topic and slug to preserve a site's path structure and multilingual publication model. This lets Blog Core manage a single canonical task while the source factory creates its own localized public pages.
* Files/areas affected: `app.py` delegation payload; ignored Blog Core binding data; `/var/www/content-factory-solocruz` server-only factory configuration and preview implementation.
* Replaced/deprecated: The unbound SoloCruz inventory-only integration and the factory's placeholder webroot/domain configuration.

### 2026-07-18 — YAS Wine factory bound as the source-authoritative publisher

* Decision: `yas.wine` is bound to `content-factory-yaswine` at `127.0.0.1:3199`. Blog Core manages its native job queue and delegates Generate, Preview, Regenerate, and explicit Publish to that factory; the factory remains authoritative for the live wine blog and SEO section pages.
* Reason: The original local factory owns multilingual output, images, validation, source template, static page writes, indexes, and sitemaps. Blog Core must be the dashboard without replacing these site-specific publication contracts.
* Files/areas affected: `site_factory_bindings`, linked YAS Wine `content_jobs` in ignored SQLite data, Blog Core legacy regeneration behavior, and the private template configuration in `/var/www/content-factory-yaswine`.
* Replaced/deprecated: Inventory-only YAS Wine import without source job linkage.

### 2026-07-18 — Complete connected-site source-factory control plane

* Decision: Every connected site with a compatible local content factory is bound through `site_factory_bindings`, and its historical source jobs are linked into Blog Core by a rerunnable inventory synchronization. `yas.ooo` remains a native content-store integration rather than a source-factory binding.
* Reason: The dashboard must operate the original factory for all imported sites without re-rendering, relocating, or publishing generic Blog Core pages into those sites.
* Files/areas affected: `app.py` source endpoint resolver plus inventory-sync/backfill APIs; ignored Blog Core SQLite bindings and source-job mappings; `docs/INTEGRATIONS.md`.
* Replaced/deprecated: Factory-name endpoint defaults as the primary routing mechanism. They remain only for legacy records that predate a binding.

### 2026-07-23 — Native content-store sites use Blog Core as their factory

* Decision: A site with `sites.access_type=native_content_store` uses Blog Core's universal generation, review, scheduling, and explicit publication lifecycle. Blog Core writes atomic JSON records into `{root_path}/data/blog-core/drafts` and `{root_path}/data/blog-core/published`; the site-owned renderer consumes those records.
* Reason: Newly integrated first-party sites do not need a duplicate legacy factory service. They still require native preview and publication under their own domain and visual system.
* Files/areas affected: `app.py` native-store detection; site-owned renderer deployments such as `deploy/georivo/`.
* Replaced/deprecated: Treating the native content-store contract as a `yas.ooo`-only special case.

### 2026-07-23 — Georivo native journal integration

* Decision: Georivo site 14 is a first-party Blog Core factory site with local native content storage at `/var/www/georivo-blog`. Nginx keeps the existing product upstream intact and routes only `/blog`, `/content-preview`, and `/sitemap.xml` to the local renderer.
* Reason: The live product application is currently proxied from an external `chatgpt.site` origin and has no `/blog`. A local route adapter gives Blog Core full editorial control without rebuilding or modifying the product application.
* Files/areas affected: `deploy/georivo/`, live `/var/www/georivo-blog`, `/etc/nginx/conf.d/georivo.com.conf`, ignored Blog Core SQLite site/profile data.
* Replaced/deprecated: External design scanning followed by a generic Blog Core-hosted mirror for Georivo.

### 2026-07-23 — Georivo renderer must reuse exact source visual chrome

* Decision: The Georivo journal uses the source site's `header.nav.glass`, `brand-logo`, `nav-links`, `footer-top`, `footer-links`, and `footer-bottom` DOM/CSS contracts. Its content follows the same photographic hero, cream editorial band, dark content band, photographic CTA, Arial display copy, Georgia emphasis, Geist metadata, lime action, and 14-28 px radius system.
* Reason: A separate theme that merely reused Georivo colors and fonts did not look like the product site. Exact source chrome and responsive behavior are required for a native integration.
* Files/areas affected: `deploy/georivo/app.py`, `deploy/georivo/georivo-blog.css`, `deploy/georivo/georivo-blog-nav.js`.
* Replaced/deprecated: The initial custom dark `site-header`/`site-footer` renderer and oversized standalone logo treatment.

### 2026-07-24 — Resolve Georivo's native hashed stylesheet dynamically

* Decision: The Georivo blog renderer discovers the current `/assets/index-*.css` reference from the live product homepage, validates the path against a strict asset pattern, and caches it briefly. A configurable current fallback remains available when the upstream homepage cannot be read.
* Reason: The externally hosted product rebuilds its CSS under new hashed filenames. Pinning one hash caused the blog's otherwise native header/footer structure to render unstyled as soon as the upstream asset changed.
* Files/areas affected: `deploy/georivo/app.py` and the live `/var/www/georivo-blog/app.py`.
* Replaced/deprecated: Hard-coded `/assets/index-22jNjtDO.css`.

### 2026-07-24 — Native content-store multilingual contract

* Decision: One native content-store task generates the base article plus full structured localizations for every language in `sites.languages`. Localizations are stored in `content_job_localizations` by `job_id + language` and exported inside the native JSON record's `translations` map; they are not separate dashboard jobs.
* Reason: Editors manage one topic and publication decision while the site receives complete language variants with the same slug, structure, facts, FAQ, and generated image files.
* Files/areas affected: `app.py`, native content-store JSON, and site-owned renderers such as `deploy/georivo/`.
* Replaced/deprecated: Native content-store generation that wrote only the site's first configured language.

### 2026-07-24 — Georivo multilingual URL and SEO model

* Decision: Georivo uses EN as its base language at `/blog/` and DE/ES/FR/RU at `/{language}/blog/`. Article slugs remain identical across languages. The native renderer localizes its interface, links language variants, emits per-language canonical plus hreflang/x-default, and includes localized variants in the sitemap.
* Reason: Language switching must keep the reader on the same article and search engines must receive an explicit relationship between real translated pages.
* Files/areas affected: site 14 language settings, `deploy/georivo/`, live `/var/www/georivo-blog`, and `/etc/nginx/conf.d/georivo.com.conf`.
* Replaced/deprecated: Georivo as an English-only native journal.

### 2026-07-24 — Georivo first live multilingual article

* Decision: Georivo's first Blog Core-owned publication is the canonical task “How Remote Property Buyers Evaluate Location Before Booking a Viewing”, published at `/blog/remote-property-buyers-evaluate-location-before-viewing/` with DE/ES/FR/RU counterparts under their locale prefixes.
* Reason: It establishes the intended editorial territory through a real end-to-end native publication and proves one-task multilingual generation, media delivery, language routing, hreflang, index listing, and sitemap expansion.
* Files/areas affected: Blog Core site 14 database records and `/var/www/georivo-blog/data/blog-core/published/`.
* Replaced/deprecated: Georivo's connected-but-empty journal state.

### 2026-07-24 — Live source chrome is a global renderer contract

* Decision: Blog Core-owned hosted/CNAME pages and native renderers obtain current source `<header>`, `<footer>`, and stylesheet URLs from the connected site's `homepage_url` through shared `native_site_chrome.py`, cache briefly, and fall back to the saved design scan only when the source cannot be read.
* Reason: Copying source chrome into a renderer drifts as soon as account controls, language selectors, footer credits, navigation, or compiled assets change. Runtime source reuse keeps Blog Core content native without modifying the product application.
* Files/areas affected: `native_site_chrome.py`, `app.py` hosted rendering, and native adapters under `deploy/`.
* Replaced/deprecated: Hand-maintained header/footer copies in Blog Core-owned renderers and relying on a historical design scan as the public chrome authority.

### 2026-07-24 — Source-authoritative publisher boundary

* Decision: Imported sites bound to their own source factory do not use Blog Core's hosted chrome wrapper. Their source publisher must render the site's real template, header, footer, language routing, and assets.
* Reason: A universal wrapper cannot safely replace a source application's routing, hydration, authentication controls, or page-template contract.
* Files/areas affected: source-factory bindings and preview/publish adapters.
* Replaced/deprecated: Assuming one generic header/footer mechanism should overwrite source-authoritative factory output.

### 2026-07-24 — Georivo trend-led editorial territory

* Decision: Georivo's initial journal should build authority around the intersection of virtual property tours, real-estate photography, drone alternatives, interactive maps, digital twins, neighborhood context, remote-buyer decisions, and verifiable geospatial visualization. Raw Trends/search phrases are research signals, not article titles.
* Reason: Exact Georivo-specific phrases are often too low-volume for reliable Google Trends reporting. Broader parent topics reveal audience demand, while the final editorial angle must answer a real property-marketing decision and express Georivo's distinct location-story expertise.
* Files/areas affected: Georivo Discovery profile and future `/blog/` queue.
* Replaced/deprecated: Treating generic real-estate marketing news or copied trend-query wording as suitable Georivo article ideas.

## 9. Do not repeat

### 2026-08-13 — Registered Reel masks, scene text, and final brand reference

* Decision: Reel foreground mattes combine semantic segmentation with only a narrow, clean-plate-difference edge recovery. Do not broadly grow masks: that admits carpet, walls, and other foreign pixels around people and objects.
* Decision: Reel overlay copy appears at scene start, remains continuously visible until that scene's cut, and changes only at a scene boundary. Use a soft offset shadow without a letter stroke; add a feathered color-sampled gradient scrim only when the image does not provide sufficient local contrast.
* Decision: A final brand-resolution scene receives the connected site's verified real logo as a Gemini image reference. Prefer a source-owned SVG converted to a high-resolution transparent PNG. The logo is integrated once into a plausible physical scene touchpoint, never programmatically overlaid as a corner watermark. The final camera path pulls back to reveal the complete branded context.
* Reason: Broad masks made extracted people visibly dirty; early text removal made copy unreadable; and an unreferenced or cropped logo undermined brand accuracy in the payoff frame.
* Files/areas affected: `registered_scene.py`, `reel_renderer.py`, `app.py`, Instagram Reel generation for all connected sites.
* Replaced/deprecated: aggressive 12-iteration difference-mask growth, per-scene text ending before the cut, outlined lettering, and hard-coded `usesLogoReference=false` in the director-plan adapter.

* Do not rely on local `/blog` installation for third-party sites; use CNAME hosting unless the local webroot is truly available.
* Do not delete installed target-site `/blog` files when removing a connected site from Blog Core.
* Do not commit SQLite database, generated previews, virtualenv, logs, or secrets.
* Do not treat Reddit availability as guaranteed; build and test degraded states.
* Do not assume chat context has all prior decisions; read memory first.
* Do not silently delete outdated memory. Mark replaced/deprecated and add the current version.
* Do not design imported-blog workflows as public mirrors by default. Preserve the source site's URLs and publish back in place unless the user explicitly asks for a cutover.
* Do not present raw Discovery signals as finished article topics. They are inputs for the journalist/SEO article idea generator.
* Do not let existing bad/generated content grant permission for future generic review/tutorial/listicle topics. Site editorial policy is inferred from stable site profile/settings, while existing content is used for context and duplicate checks.
* Do not fake a source-authoritative draft preview with Blog Core HTML, and do not run any `publish-*` v3 command merely to preview it. Build the source factory preview only, keep it `noindex`, and preserve the live webroot unchanged until the operator explicitly publishes.
* A source-factory preview must preserve the actual current source-page shell from that site's webroot, including head/CSS, header, footer, breadcrumbs, and current navigation/CTA links. Do not assume the factory's v3 shell is visually current.
* Preserve the source page's internal template classes and blocks too. Bind draft values to the existing hero/article/TOC/FAQ/recommendation slots rather than replacing a live page's content area with a different factory layout. If a new draft image has not been deployed to the source site, retain the existing template image instead of showing an empty media block.
* Draft previews must not show breadcrumb navigation unless it is explicitly part of the required public page view. When the source template has reusable inline-media components, bind real generated draft image files to those components using source-site absolute URLs; do not show empty image frames or generic image markup.
* Do not replace a user-authored source-site page design during integration. Extend its native data list/components and reuse its visual system for published and previewed factory content.
* Do not cross-post an article summary unchanged. Select the social format from the article's evidence, audience intent, and the target channel's native behaviour, then validate its channel-specific constraints before storing or sending it.
* Do not imply Gemini TTS prebuilt voices are voice cloning. A selected Gemini voice and per-site direction are supported; true custom/clone voice requires a separate Google Cloud Custom Voice arrangement and adapter.
* Do not auto-publish podcast audio after generation. A ready episode must be reviewed and explicitly published. Native embedding on an imported source site must use that source factory's adapter rather than Blog Core changing its public template.
* Do not bypass a configured source-factory binding for a new imported-site task. Create, generate, preview, and publish through the native source factory so the public URL, design, assets, and validations remain authoritative.
* Do not create a legacy source-factory binding for a first-party `native_content_store` site. Blog Core is already its factory; keep the native renderer focused on preview and publication.
* Do not claim a site integration is native because it shares colors or fonts. Match and verify the source DOM, computed header/footer dimensions, section rhythm, typography roles, controls, and responsive behavior.
* Do not delegate only a title and slug to a source factory. Preserve the planned task's native path, canonical group, type, and language in the source job payload.
* An explicit Regenerate action for a source-authoritative task must call the source factory even when the previous result is `READY` or `PUBLISHED`; merely re-syncing an old result is not regeneration.
## 2026-08-13 — Production Reel matting and caption contrast

* Instagram Reel registered layers must use SAM 2.1 large for box-prompted semantic segmentation and ViTMatte for alpha refinement. The old quantized `rembg` SAM path and manual clean-difference edge growth are deprecated because they produce jagged people contours and damaged clothing/hands.
* The SAM 2.1 checkpoint is deployment data at `models/sam2.1_hiera_large.pt` and must not be committed. Production must fail clearly when the smart matting stack is unavailable; it must not silently fall back to lower-quality segmentation.
* Reel captions are always light with a soft dark shadow. They must never switch to dark text based on local luminance; an adaptive local gradient may be used when the photographic background needs more contrast.
* Reel rendering is locked per site/post so the scheduler and a manual production request cannot write the same temporary render concurrently.

## 2026-08-13 — Universal source-grounded Reel direction

* Reel planning is a gated three-stage process: editorial problem/solution brief, source-grounded photographable scene concepts, then executable layer/camera/text direction. Each stage must finish and validate before the next starts; no image, voice, or video generation may begin from a rejected text plan.
* The hook, all solution beats, and the final brand resolution must answer one common reader problem. A narrow consequence may create the hook only when later beats truthfully contribute to the same larger decision. Retention promises belong inside the hook and handoffs, never in a standalone empty screen.
* Every scene must remain identifiable without overlay text through exact article-grounded domain anchors. A new physical environment is allowed only when the current beat literally names that environment; otherwise the scene reuses an already approved visual world. Category convention cannot authorize invented terminals, counters, offices, rooms, journey stages, or outcomes.
* Every movable direct-evidence or support layer carries an exact source quote. Support layers cannot be random luggage, furniture, drinks, cushions, decorative architecture, or other filler added to satisfy an event count. Abstract claims cannot become invented bills, documents, signs, confirmations, transactions, or symbolic props.
* Step two owns the exact overlay copy and a protected text zone. Step three must prove that the zone stays clear through the clean plate, every layer path and final position, and every camera framing. Hook copy has the highest visual priority.
* Camera motion is one continuous scene path synchronized to named evidence-layer arrivals. Every direct-evidence layer triggers camera attention; timing is authoritative, while descriptive phase labels are derived from that timeline. Per-scene checkpoint calls receive the total scene count so the complete Reel remains 27-33 seconds.
* Do not add project-, industry-, site-, or object-specific exceptions to solve a failed Reel. Improve the shared Gemini evidence, scene, and direction contracts and use the current article only as verification data.

## 2026-08-13 — One primary stake per Reel

* A Reel editorial brief owns exactly one `primaryStakeMetric`. Do not combine independent costs, risks, comfort, community, confidence, or other benefits merely to include more article sections.
* Every ranked solution must expose an auditable causal chain: provider or counterparty, changed/shared resource or action, causal mechanism, and concrete outcome. The outcome and problem connection must explicitly name the same primary stake metric.
* An activity label such as communication, meetings, research, community, an app, or a checklist is not a solution by itself. It may support a solution only when the prompt explains who participates, what resource or decision changes, how the change occurs, and how it changes the primary stake.
* A useful parallel benefit must not be presented as a causal answer to a financial or risk hook. Omit it from that Reel's ranked solutions unless the article explicitly proves the connection.
* Shared `GEMINI_API_KEY`/`GOOGLE_API_KEY` is the primary key for Gemini text and image generation. `GEMINI_TEXT_API_KEY` is a compatibility fallback, not the first choice.

## 2026-08-13 — Social-first attention contract for Reels

* Every Reel is planned for a distracted, often silent, fast-scrolling social-feed viewer. It is not an article summary, slide deck, or sequence of unrelated tips.
* Step one must define the complete attention arc: the exact first-second hook, concrete early promise, truthful midpoint escalation, withheld resolution, and payoff delivery. The first second contains the central stake, never branding, context setting, or a slow establishing introduction.
* Each intermediate scene delivers a useful mini-payoff while making the remaining question more specific or consequential. It cannot reset the story, repeat the hook, or disclose the final mechanism early.
* Social attention roles are immutable cross-stage data. Step two translates them into visual evidence and handoffs; step three must use them to control layer order, camera emphasis, copy hierarchy, timing, and the payoff landing.
* Social energy may strengthen presentation, ordering, specificity, and curiosity, but never factual certainty or outcome strength. Retention and payoff claims require exact source phrases; never infer guarantees, percentages, equal splits, scarcity, safety, verification, or eliminated costs from weaker source verbs.
## 2026-08-14 — Reel scenes require three physical events in addition to text and camera

* Every Reel scene must contain three or four distinct physical layer events. The persistent overlay, camera path, focus, lighting, and static-set reveals are additional direction and never count toward this minimum.
* Step two must create three or four independently extractable layers and at least one meaningful non-human object. Step three creates exactly one timed rigid entrance for every approved layer and cannot omit or duplicate one.
* The first three layer events form one causal evidence chain: situation, mechanism, and visible result. An optional fourth event may preserve continuity. Every layer must explain what becomes impossible to understand if it is removed; location dressing, generic accessories, atmosphere, and visual padding are not events.

## 2026-08-14 — Abstract Reel claims need honest evidence layers

* Pricing, discounts, cost splits, matching results, and similar abstract mechanisms must not be converted into invented gifts, luggage, keycards, tickets, wristbands, receipts, or other photographic proxies that do not prove the claim.
* When people and physical relationships cannot communicate the mechanism honestly, use a restrained programmatic evidence layer with only the minimum fact needed for comprehension. It is not an AI-generated photographed prop and must remain subordinate to the main scene copy.
* This production capability is still pending full renderer integration. Until then, plans using evidence layers remain text-only review artifacts and must not start image, voice, or video generation.
* A person layer owns every item worn, carried, held, touched, or overlapped by that person. An independent object layer must be physically separate from people and other movable layers, freestanding, detachable, and unobstructed.
* Replaced/deprecated: the same-day rule that counted one layer entrance plus overlay text plus camera motion as a valid three-event scene.

## 2026-08-14 — Programmatic Reel evidence is independent of the photographic camera

* Decision: Abstract facts such as prices, discounts, supplements, cost splits, and matching results are rendered as transparent programmatic RGBA evidence layers. They are composited in screen coordinates and are not zoomed or panned with the photographic camera.
* Decision: Camera phases start from the approved event timestamps, not equal subdivisions of scene duration. Physical photo layers follow the camera; evidence graphics retain their readable screen placement.
* Decision: Resume production reuses costly completed photo assets but regenerates cheap programmatic graphics from the current approved plan so placement and copy fixes take effect.
* Decision: Extractable person masters must avoid bags, backpacks, straps, luggage, dangling accessories, and other ownership-crossing details. Two-person mobile scenes use medium-wide framing with each person large enough for reliable matting and phone viewing.
* Decision: Voice generation remains disabled until the visual result is approved. A visual-only production run may use the site's existing brand music continuously.
* Reason: Camera-transforming evidence made it overlap people and become unreadable; stale resumed graphics ignored corrected placements; straps and undersized people caused avoidable matting failures.
* Files/areas affected: `app.py`, `reel_renderer.py`, Instagram Reel generation for every connected site.
* Replaced/deprecated: photographed proxy props for abstract claims, camera-transforming UI/evidence cards, and blind reuse of stale programmatic layers during resume.

## 2026-08-14 — Reel cards and narration must fit their time and frame

* Decision: Programmatic evidence cards use measured content layout with explicit left, right, top, and bottom safe padding. Logo, title, and detail lines are measured together; typography may reduce within a bounded range when required, but content must never cross the card edge.
* Decision: Scene narration must finish before its scene boundary. Measure generated audio before rendering and normalize an overlong delivery to the approved narration window so sequential scene voices cannot overlap.
* Decision: A Reel has one narrative voice sequence. Per-scene WAV segments are timeline parts of that sequence, not concurrent speakers. Brand music remains continuous and is ducked beneath speech.
* Reason: Fixed text offsets clipped the final evidence detail, while unexpectedly slow TTS delivery exceeded six-second scenes and would have produced overlapping narration.
* Files/areas affected: `app.py`, Instagram Reel evidence graphics and audio production for every connected site.
* Replaced/deprecated: unmeasured evidence-card typography and trusting requested TTS speaking duration without inspecting the generated file.

## 2026-08-14 — Reel duration follows comprehension, not a fixed runtime

* Decision: Never accelerate, truncate, paraphrase, or shorten approved narration merely to fit a target Reel duration. Measure the natural generated voice and expand each scene to the full narration duration plus a calm reading pause. The total Reel duration has no fixed upper limit.
* Decision: Overlay text remains visible until the expanded scene ends. A scene cut, text change, voice transition, and camera-plan boundary share the same content-driven timeline.
* Decision: Camera direction is authored per scene from that scene's subjects, environment, evidence order, and intended reveal. Camera focus targets only photographic subjects or the physical environment; programmatic evidence graphics remain fixed in screen space and are never camera targets.
* Decision: Every camera keyframe must preserve the persistent overlay and evidence-card safe zones. A face or essential object may not enter those zones during a push, pan, focus transfer, or pull-out; use a wider environmental move when a close-up has no safe destination.
* Decision: Evidence-card content is one centered layout group. Accent marker, logo, title, and detail copy are centered horizontally, and the measured group is centered vertically inside safe padding. Text wraps and typography adapts without hard line-count truncation.
* Reason: Speed-normalized narration became unnaturally fast; keeping six-second scene metadata made text and camera timing diverge from longer audio; left-aligned fixed card layouts produced inconsistent empty space.
* Files/areas affected: `app.py`, `reel_renderer.py`, all Instagram Reel production.
* Replaced/deprecated: the earlier same-day rule that normalized overlong narration into a fixed scene window. Scene duration now expands instead.
## 2026-08-14 — Reel visuals form a reusable, non-destructive per-site library

* Every site's generated Reel imagery is indexed from `data/social_assets/{site_id}` into `data/reel_asset_library/{site_id}/catalog.json`; originals remain untouched in their production directories.
* Curation separates approved canonical assets, manual-review candidates, rejected assets, exact/visual duplicates, and non-reusable archive imagery. Only `approved` canonical assets may enter future automatic generation.
* A reusable scene is a registered bundle: its clean/background frame, master context, and registered layers remain geometrically related. A layer from one scene must never be pasted directly onto an unrelated background.
* Approved scene/master imagery may be supplied to Gemini as a site-specific photographic-world reference. Approved person layers may be supplied as identity/wardrobe references. Both are reference-only outside their original scene: the new master owns pose, action, scale, lighting, and registration.
* Exact and near duplicates remain on disk for provenance but are excluded from the canonical library. Low-resolution, empty, non-transparent registered layers and clearly undersized mobile subjects are rejected automatically; ambiguous edge contact or matte quality remains manual review.
* Duplicate detection is role-aware. Exact bytes are compared across all reusable roles; visually equivalent variants are compared within their role; and cross-role opaque frames collapse only at encoding-noise equivalence. A clean plate, populated master, source frame, and registered transparent layer remain separate when they carry different production value.
* The Distribution tab exposes the Reel visual library with status filters and manual `Approve`, `Review`, and `Reject` controls. Manual decisions persist in `overrides.json` and survive catalog rebuilds.
* Manual status changes update `catalog.json` atomically before the browser redirect, then queue the full background rebuild. The visible filter state must never wait for the slower scan.
* The library refreshes automatically in the background after a Reel's complete visual scene set is accepted. Expensive image generation does not wait for the catalog rebuild.
## 2026-08-31 — Shared carousels require a real editorial source

* A shared Instagram/TikTok carousel plan is never itself a content source. It must resolve to a `PUBLISHED` or `IMPORTED` article before creative generation starts.
* A stored direct content-job link is authoritative. Legacy synthetic `agent-social-*` links may be repaired only through a high-confidence editorial match using at least two shared topic terms, including one non-generic term.
* Generic site vocabulary such as `cruise`, `solo`, `best`, or `guide` cannot create a source match. Blog hubs and navigation/index pages are not valid social-source articles.
* A plan whose source article is still queued or absent remains `WAITING_FOR_SOURCE`; it stays in the plan and is re-evaluated on later scheduler runs. It must not block later plans that have valid articles and must never generate a carousel from an unrelated article.

## 2026-09-01 — High-risk content uses configuration-driven release gates

* A `content_job` with a `complianceCluster` contract uses universal gates, without a site, domain or topic exception: generation needs a current source map and explicitly VERIFIED claims; publication and scheduling need a recorded Tier B approver, all-locale review and visual QA.
* The NOMADeira Phase-A queue has dated primary-authority source maps for all 12 narrow-intent articles. `SOURCES_COLLECTED` is evidence intake only: it has no generated drafts, localizations, media, schedules or public pages.
* The daily scheduler uses the same publication gate and cannot publish a protected article merely because it has a due timestamp.
* Replaced: three legacy `www2.gov.pt` references that returned live HTTP 502 were excluded from the Phase-A source revision; the remaining official sources were retained only after reachability checks.
* The generic compliance lifecycle exposes two auditable API transitions: `compliance-claim-review` records source-bound verified claims and unlocks draft generation; `compliance-tier-b-approval` requires a generated draft, every configured localization and explicit all-locale/visual QA confirmations before a job can be scheduled.
* Claim review derives the generator's closed `pageBrief.sourceReferences` from the reviewer-approved claims, including conditions and exceptions. It never feeds a broad source-topic summary to the writing model.
* Compliance article visual generation is two-stage: a Gemini text batch first creates the complete article and a persisted `mediaBatchPlan` with one hero and three paragraph-bound final image prompts per article; only then may one image batch be sent. The planning stage creates no image bytes or publication.
## 2026-08-31 — Native V3 publishers derive route identity at publish time

* A stored native-factory draft can predate the current V3 payload schema. Before serializing it, the publisher must derive `page_id` and `language` from the target route and supply safe structural defaults.
* One incomplete page payload must never make `factory_v3.cli build-preview` fail for every page on the site. The publishing boundary owns this compatibility guard, rather than relying on a later whole-site build to surface it.
* LaycanMatch's native factory follows this rule. Its release verification is a Python compile, a PM2 restart, and a complete V3 `build-preview` with an `ok` QA result.
* Its text generation is explicitly configured as `gemini-3.7-flash`; `gemini-2.5-flash` is retired and must not be restored as a fallback.

## 2026-08-31 — LaycanMatch legacy article rewrites preserve the blog cluster

* Existing LaycanMatch informational articles are canonical `/blog/<slug>/` pages. Rewriting them through the native factory must preserve that route rather than creating a second `/resources/<slug>/` page.
* Generation remains separate from publication. Batch-started native jobs return to Blog Core as drafts for review; they do not replace public pages until explicitly published.

## 2026-08-31 — Separate generated-video Reel plans use an executable narrative ledger

* The separate NOMADeira batch-video contour (`app_video_canary.py` + `batch_video_engine.py`) must not treat a factual hook, a self-score, a caption, or a pinned comment as evidence of a compelling Reel.
* Every new Gemini production plan has a `narrativeArc` with one ordered beat per clip, the exact payoff clip, the information newly released, the information withheld, visible proof, and the reason the next beat is necessary. In multi-clip stories, the payoff cannot be clip one.
* Replaced: forcing an explicit recipient/"share this" CTA inside a Reel. `viewerReactionBeat` is an actual final clip requirement, not post metadata, but it contains only a short story-specific comment expression. Shareability is evaluated from the story's transmission value; no geographic, national, cultural, diaspora, resident, heritage, family, friend, or other invented recipient targeting may be persisted from commissioning seeds.
* A separate hostile Gemini critic and a deterministic structural gate reject early payoff leaks, non-escalating repetition, generic scenery used as proof, and reaction copy absent from the Reel. A failed plan is prompt/contract evidence; it must not trigger blind media generation or mass retries.
* This applies to every present and future site/story. No place, domain, entity, topic, or prior canary is special-cased. The contour remains separate from the legacy Reel renderer and does not generate or publish media during planning.

## 2026-08-31 — Universal finalized Google Search Console collection

* Each site may select one exact Search Console property in `gsc_site_connections`. Only the property, access state and collection state are stored; credentials and paths remain server-only.
* The scheduled collector reads the latest finalized Web Search date, three days behind UTC, and persists page and query aggregates separately in `gsc_daily_page_metrics` and `gsc_daily_query_metrics`.
* Each run is durable in `gsc_collection_runs`. A failed read leaves the last successful daily snapshot untouched.
* This stage only collects search data. Topic selection, content creation, 21–30-day evaluation, consolidation and conversion attribution remain deliberately separate.

## 2026-08-31 — GSC weekly opportunity planning

* Weekly planning operates only for sites with a connected GSC property. It aggregates the last 28 days of query metrics and considers queries with real impressions and positions 4–25.
* Candidate ideas still pass the universal editorial and duplicate checks against all existing and planned site content. It creates reviewable `gsc-near-ranking` recommendations, not jobs or publications.
* The intended output is three to five quality candidates per week, but it is never a quota: insufficient demand or uniqueness produces fewer (including zero) recommendations.

## 2026-08-31 — GSC coverage is verified per connected site

* Search Console access is verified against one exact property per Blog Core site. A successful connection is enabled automatically; inaccessible properties remain disabled and cannot produce collection failures or invented data.
* The service account currently has confirmed `siteFullUser` access for every independently managed panel site: `yas.wine`, `myugc.studio`, `solocruz.com`, `laycanmatch.com`, `airep24.com`, `yas.ooo`, `pipsalerts.com`, `georivo.com`, `cabinjoin.com`, `karpaleksei.com`, `nomadeira.com`, and `veselovaveronika.com`. `geo.yas.ooo` is not an independent GSC target; its SEO data belongs to the shared `yas.ooo` property.
* `veselovaveronika.com` is a distinct Blog Core site (`id 19`), even though it shares the VPS application host with `karpaleksei.com`. Its management boundary, GSC property, data, jobs, and future content remain independent. Creating its panel record and initial GSC collection did not scan, publish, or modify its webroot.
* An initial collection covers only the latest finalized day. Weekly planning is deliberately allowed to return zero until enough 28-day query evidence exists. A `NO_CANDIDATES` result retries once daily rather than blocking the rest of that calendar week.
* Replaced/deprecated: treating an empty first-week GSC response as a completed weekly plan.

## 2026-09-01 — NOMADeira compliance articles use the native Blog Core article queue

* The NOMADeira compliance cluster does not create a second publisher or a social-content substitute. Verified graph evidence feeds the existing `content_jobs` → `content_job_localizations` → native JSON draft/preview/publish lifecycle.
* Phase A's 12 narrow-intent records are seeded idempotently as private `BLOCKED_EVIDENCE` jobs. Each records its immutable target slug, one curated parent core route, required primary-authority families, high-risk claim fields and atomic `en`/`de`/`uk`/`ru` release requirement.
* A matching unpublished job is adopted instead of duplicated. A published, drafted or generating job is never mutated by the seed. No compliance record may generate, preview publicly, or publish until its current primary-source map and Tier B high-risk review are complete.

## 2026-09-01 — Compliance source collection precedes claim verification and drafting

* The first three NOMADeira compliance pilots — NIF through representative, remote employee residence route and opening atividade — now hold private, dated primary-source maps and restricted claim proposals in their existing Blog Core jobs.
* `SOURCES_COLLECTED` means only that the official material, its supported scope and expiry are recorded. It is not claim verification, legal review, draft authorization, localisation authorization or publication approval. `claimIds` remains empty until the next gate is completed.
* A source-map collector is idempotent by a stored revision. It preserves the job's generation/publication block and never creates draft HTML, locale records, media or public URLs.

## 2026-09-01 — NOMADeira Phase A content approval and one image batch

* The twelve Phase-A compliance articles are generated as source-bounded English drafts only after verified claims exist. Each is approved only when its structured draft validates and it has exactly four distinct planned images: one hero plus three paragraph-bound scenes.
* The editorial contract must not force invented workflow steps. Where the closed source ledger supplies three approved reader checks, the quality minimum is three and each is used exactly once; an absent approved internal-link list requires empty link arrays.
* A transient failure to fetch a still-current reviewed official source is recorded as `TEMPORARILY_UNAVAILABLE`. It permits private drafting from the unexpired reviewed evidence but blocks compliance publication until a later live check succeeds.
* After 12/12 source-bounded drafts and 48/48 unique image prompts passed owner-authorized content review, one Gemini `gemini-3.1-flash-image` batch was submitted. This is asynchronous media production only; localizations, visual QA, Tier B publication approval and scheduling remain blocked.
* The submitted batch completed with 48 keyed responses and no provider errors. Blog Core selected one approved image per key, stored 48 WebP assets (hero plus three paragraph-bound images per article), and retained the two extra provider image parts outside the published asset set.

## 2026-09-01 — YAS daily article and explicit X schedules

* `yas.ooo` publishes native content-store articles once per day at 09:00 `Europe/Warsaw`. The initial cleaned schedule contains 16 unique public jobs from 2026-09-02 through 2026-09-17; ready drafts run first and queued legacy rewrites retain their canonical slugs.
* An internal `yas-evidence-social-preview` record is not an article and is never scheduled. Exact evidence-pattern duplicates are collapsed before scheduling; the retained canonical draft is the more complete generated version.
* LinkedIn remains an independent daily 10:00 schedule. Explicitly prepared X work items publish once per day at 17:00 `Europe/Warsaw` through their own reviewed queue, not through the generic article-to-social cadence. The earlier 15:00 slot is superseded.
* The YAS Zernio connection is mapped specifically to the `YASflows` X account inside the `YAS` profile, not the same-named account inside `Default`. The X scheduled worker accepts both evidence-derived and article-derived reviewed work items; if a mapping is ever absent, a due item remains `SCHEDULED` for retry rather than becoming `ERROR`.
* The current finite X queue contains 48 reviewed items, one per day from 2026-09-02 through 2026-10-19 at 17:00 Warsaw time. Generic X cadence remains disabled so no parallel article-derived X post can duplicate this explicit queue.
* The same dedicated Zernio `YAS` profile maps Instagram account `yas.flows` for Blog Core site `12`, alongside its existing X mapping. All 27 complete seven-slide vacancy carousels are explicitly scheduled in Zernio, one per day at 18:00 `Europe/Warsaw`, from 2026-09-02 through 2026-09-28. Each row retains the provider timestamp and logical Warsaw slot in `content_json.publicationSchedule`.
* This is a finite reviewed carousel schedule, not a generic Instagram cadence: the generic worker consumes ordinary `post` assets and must not be treated as an executor for `instagram_vacancy_carousel`. Generic Instagram and Reel cadences remain disabled, preventing additional unreviewed Instagram output. The three rendered Reels remain `DRAFT` and unscheduled.
* The Zernio `YAS` profile also maps Reddit username `AiStartupGuy` and Threads username `yas.flows` to Blog Core site `12`. The seven reviewed Reddit text posts are explicitly scheduled one per day at 18:00 `Europe/Warsaw` from 2026-09-02 through 2026-09-08: four in `r/automation` and three in `r/GetStartups`.
* Zernio is the provider source of truth for Reddit communities and Pinterest boards. Reddit routing remains creative-scoped, but before submission Blog Core fetches the selected account's `/reddit-subreddits` list and fails closed when the reviewed target is not available there; the connection-level default is only a legacy fallback. Every scheduled draft stores its own provider-verified subreddit and current rule snapshot.
* The scheduled Reddit posts contain no external link, company mention, offer or CTA. Unavailable communities are not used, `r/SaaS` is excluded because its current rules prohibit AI-generated text, and a discovered reply is never silently submitted as a comment or routed to a generic default community.
* Reddit and Threads generic cadences remain disabled and neither channel is in the active automatic-channel list. The current Reddit delivery is a finite reviewed schedule; the Threads connection is mapped only and does not authorize or schedule its fourteen existing drafts.
* Generic topic discovery remains disabled for `yas.ooo`. The active evidence/vacancy contour and GSC recommendations are its upstream topic sources; neither recommendation source bypasses the draft and explicit scheduling lifecycle.

## 2026-09-01 — SoloCruz Pinterest is mapped through its dedicated Zernio profile

* Blog Core site `7` (`solocruz.com`) uses the Pinterest account `solocruzcom` from the dedicated Zernio profile `Solocruz`; the unrelated `myugc_studio` Pinterest account in Zernio's `Default` profile must not be selected for SoloCruz.
* The Zernio-reported default public board is `SoloCruz`. Its account and board identifiers are stored in the existing site-scoped Zernio connection, and the same board is registered in the site's Pinterest strategy.
* Connection and board mapping do not authorize content production or delivery. SoloCruz Pinterest automation remains disabled with a daily target of zero until the complete contextual Pin ledger, destinations and unique image prompts are reviewed and approved; no Pin was generated, queued or published during connection setup.

## 2026-09-01 — Article-derived Pinterest production uses a complete Pin ledger

* A native article-derived Pin is a complete record: one public source article, short mobile overlay, Pin title, description, CTA, alt text, search phrases, exact destination and a context-specific 2:3 scene. A carousel may supply an editorial topic, but its slides are not copied as Pins.
* Gemini image batches generate only the unique photographic backgrounds. Exact overlay text and a site-owned logo are added deterministically after collection, preventing misspelled hooks, invented logos and unreadable mobile typography. Collection produces reviewable `DRAFT` rows only; it never schedules or publishes.
* The universal `deploy/pinterest_pin_batch.py` runner validates public source ownership, field limits, a nine-word overlay maximum, destination URLs and global uniqueness before submission. Its deterministic IDs and preserved provider batch metadata make reseeding idempotent and prevent duplicate image-batch charges.
* SoloCruz has one approved 45-Pin English ledger derived from 15 public articles, with three distinct audience/search angles per article. Four owner-viewed preview images are retained; the remaining backgrounds were generated with `gemini-3.1-flash-image`. Semantic QA rejected two first-pass scenes and accepted their specifically re-prompted corrections. All 45 assets are unique 1000×1500 `DRAFT` records; Pinterest delivery remains disabled until owner visual review and explicit scheduling.

## 2026-09-01 — SoloCruz article Pins use one approved finishing frame

* SoloCruz article-derived Pins use a top-only navy-to-blue gradient headline panel followed by the photographic scene all the way to the bottom edge. The exact short hook is large, uppercase and mobile-readable, with a contextual turquoise emphasis. The site-owned full logo is centered over the lower part of the photograph.
* Rejected/deprecated for this site: footer fields of any colour, separate bottom brand panels, text placed directly over the photograph, generated logo approximations and free-form per-Pin layout selection. These experiments did not match the owner-approved visual direction.
* The logo source is site-scoped configuration, not a domain branch in the universal engine. The supplied `logo600.svg` contains a simulated checkerboard rather than real transparency; production preparation must derive a true-alpha colour mark and retain a white separation edge before compositing it. Never place the raw checkerboard square on a Pin.
* Existing paid photographic backgrounds remain reusable edit targets. Changing the finish must not trigger another provider image generation or discard the stored background.
* The approved finish is executable through the universal `deploy/pinterest_pin_batch.py` collector and site-scoped `deploy/solocruz_pinterest_finish.json`. Exact line breaks and the turquoise line are configuration for every Pin; the runner contains no SoloCruz/domain branch.
* All 41 batch-backed SoloCruz drafts were recomposed from their saved Gemini responses with this finish. The four owner-approved previews remain byte-identical to their backup, all 45 records remain `DRAFT`, and no Pin was scheduled or published.
* Provider images may contain uniform dark or light technical edge/spacer bands. The deterministic crop removes such substantial bands before fitting the photograph, so no accidental footer or blank field survives and the image still reaches the bottom edge.
* Headline fitting must validate the rendered glyph boxes, not only total nominal text height. Every adjacent line requires at least 18 pixels of measured visual separation at 1000×1500; the normal proportional gap is 20% of the selected font size with a 20-pixel floor. The earlier 5–8-pixel spacing was defective and is superseded.

## 2026-09-01 — SoloCruz approved Pins have an explicit three-slot publication schedule

* The 45 approved article-derived Pins are scheduled directly through the mapped SoloCruz Zernio Pinterest account and board, three per logical Warsaw day at 15:00, 19:00 and 24:00. A logical `24:00` is represented as `00:00` on the following calendar date with the `Europe/Warsaw` offset.
* The current finite schedule covers logical dates 2026-09-02 through 2026-09-16; the final `24:00` slot executes at 2026-09-17 00:00 Warsaw time.
* Each `visual_pins.concept_json.publicationSchedule` records provider time, timezone, logical date, logical slot and sequence. The review panel exposes the provider timestamp for scheduled Pins.
* This finite schedule does not enable ongoing Pinterest generation. `pinterest_strategies.enabled` and `daily_pin_target` remain disabled/zero so Blog Core cannot create or publish extra Pins after the approved 45.

## 2026-09-02 — EPR Scan is a reviewed multilingual native content-store site

* EPR Scan is Blog Core site `20`, rooted at `/var/www/eprscan`, with English canonical content and only German, French and Spanish translations. Russian and Italian are not part of this site.
* Blog Core owns editorial records under `/blog/{slug}`; EPR Scan remains authoritative for its design, renderer, route system, checker, legal/product pages, metadata, hreflang and sitemap.
* Superseded: EPR Scan no longer uses `publication_contract:reviewed_multilingual_compliance`. Its `publication_contract:source_audited_multilingual_compliance` marker fails closed without EN/DE/FR/ES, 2–5 live official sources, a complete claim ledger, translation number/structure/link parity, SEO checks and browser QA.
* The EPR Scan prebuild independently validates the publication payload and rejects executable HTML. A systemd path unit rebuilds and restarts the existing EPR Scan service only after an explicit valid publication; recommendations and drafts are never deployed.
* Non-blog native content filenames now include the complete normalized target path, preventing collisions between nested routes that share a final slug.
* `sc-domain:eprscan.eu` is saved but disabled in Blog Core with verified `no_access`; enable collection only after the site owner grants the configured service account access and verification succeeds. Bing ownership/submission remains an external owner-side gate.
* Public SEO regression coverage is 60 indexable plus 16 private routes across EN/DE/FR/ES. Public equivalents require one server-rendered H1, self-canonical, reciprocal four-language hreflang plus English `x-default`, and sitemap membership; private account/check/report/recovery routes require `noindex` and sitemap exclusion. RU/IT alternates are rejected.
* Localized EPR Scan code generation must translate catalogued composite JSX fragments as well as ordinary text nodes. `npm run translations:check` is the durable guard against English catalog residue in generated DE/FR/ES source.
* Superseded: the TOR roadmap is no longer blocked on a human compliance reviewer. Eleven substantive recommendations were materialized, source-audited and published; operational recommendations remain separate from content.
* Translated route existence alone is not proof of verification. Blog DE/FR/ES routes require a passing source/translation audit before sitemap and hreflang inclusion. Public metadata must identify automated official-source verification transparently and must never invent a human reviewer.
* EPR Scan now has populated English `/guides`, `/countries`, `/marketplaces`, `/tools` and `/company` trust hubs, visible breadcrumbs, curated related links, Organization/WebSite schema, and route-aware language navigation. No `/templates` hub exists until a real asset exists.
* TOR funnel events coexist with the original product events. Purchase and registration-assistance completion are recorded server-side; assessment/order identifiers are pseudonymized before persistence and excluded from optional third-party analytics.
* EPR Scan has an enabled weekly read-only SEO crawl on Monday 06:15 UTC plus randomized delay. It combines the fixed multilingual/release contracts with a dynamic sitemap/internal-link crawl, persists compact pass/fail history under `/var/lib/eprscan/seo-crawl`, and leaves content/publication untouched.
* EPR Scan editorial images bypass the Vinext image redirector and use direct static WebP delivery; above-the-fold heroes are preloaded. This avoids a production `/_next/image` 302-to-HTTP hop. New breadcrumb/related-card colors meet Lighthouse contrast checks, and `app/icon.png` is a 64px/2.1KB favicon rather than the former 512px/129KB payload.
* EPR Scan defers the optional `web-vitals` client module until browser idle time and applies `content-visibility:auto` with intrinsic sizing to below-the-fold sections. Explicit background surfaces preserve WCAG contrast when skipped content is audited. The initial analytics-tracker chunk fell from 10,978 to 2,147 bytes and the deferred metrics chunk is 7,962 bytes.
* The EPR Scan Lighthouse release check uses three attempts by default: median Performance/LCP, minimum Accessibility/SEO, and maximum CLS. This keeps the strict 2.5-second LCP threshold without allowing one unusually fast run to mask a regression. It remains a manual release gate, not part of the low-priority weekly systemd crawl; production RUM is authoritative for real-user LCP/CLS/INP.

## 2026-09-02 — EPR Scan first content wave is source-audited and published

* The approved PPWR timing draft plus the remaining ten substantive TOR roadmap articles are materialized as 11 English `PUBLISHED` jobs. Recommendations `41`–`51` are `IMPLEMENTED`; obsolete human-review recommendation `40` is `DISMISSED`; only topic-discovery recommendation `39` remains open.
* Every article has a source-bounded brief, three article images, five FAQ items and four or five contextual internal links. Existing PPWR, country, marketplace and checker routes remain source-authoritative; the new records target only `/blog/{slug}`.
* One Gemini `gemini-3.7-flash` batch produced exactly 33 structurally validated localizations: 11 German, 11 French and 11 Spanish. No Russian or Italian localization exists.
* Draft-store validation now accepts complete DE/FR/ES localizations on an unpublished English source while keeping the private preview English-only, `noindex`, no-store and outside the sitemap. This replaces the first-pass-only rule that rejected every localized draft.
* Superseded: no human compliance or language reviewer is required. Codex performs claim-by-claim comparison with open official sources and deterministic EN/DE/FR/ES structure, number and link checks; public copy transparently says `Official sources verified`.
* All 11 English articles and 33 DE/FR/ES variants are public. Report `eprscan-source-audit-2026-09-02-v1` passed for every job; the 44 article URLs are indexable and four blog hubs plus all article URLs are present in the sitemap. RU/IT remain absent.
* Publication removes the stale private draft-store record after the public record is durable, preventing published content from continuing to compile as a draft preview.
## 2026-09-05 — SoloCruz episodes 02–24 require production-grade prompts and engagement design

* Current production-writing source is the Google Sheet tab `Episodes 02-24 Detailed` (sheetId `394342257`) in spreadsheet `1LWI2SFMB3Ghg_mtsmoD4pTH3CAxMq9BdNqfmPC7t3bk`. It deliberately begins at episode 02 and contains 23 episodes / 72 new ten-second prompts; episode 01 is not restated or rewritten there.
* Every episode carries its own first-seconds hook, retention progression and exact caption/pinned-comment provocation. Engagement copy stays outside generated pixels and dialogue unless the story itself motivates it; do not repeat a generic follow CTA in every episode.
* Each ten-second prompt is a complete production prompt, not a synopsis: exact timed scene direction, cast/reference boundary, essential camera rules, scene-specific physical continuity, dialogue attribution, ambience, output restrictions and final-frame continuity. Repeated generic directing theory is intentionally excluded. The authoritative 2026-09-06 concise pass reduced the 72 active prompts from an average of 5,396 to 1,721 characters while preserving every timed three-shot scene and exact dialogue.
* Episode 02 is now `Она не пассажир`. The former booking-list, tablet-scrolling and cabin-chain plot was rejected as dull and unclear. Security believes Cruz is an unlisted passenger; an event host summons her to a packed theatre, where she is revealed as the ship's invited cruise expert whose knowledge and performances provide her cabin. The chief who came to remove her ends in the front row; two microphone taps echo the opening door knocks.
* Generator prompt `Episodes 02-24 Detailed!H2` must be self-contained and use only information visible in its attached references: the door reference shows the closed door and security characters through its window, and the separate Cruz reference defines her design. Never tell the generator that a `pilot` or an episode performs an action, and never rely on unseen episode history. The referenced door opens once; no phone, tablet or other unlisted prop appears.
* The former `24 Episodes v3` tab is now labelled `24 Episodes v3 — SYNOPSIS ONLY`; it is planning context, not generator input. v2 remains rejected.
* Corrected episode 02 clip 01 reference semantics: multiple attached references define Cruz identity/outfit, the exact cabin/door geometry and Marcus identity. They are not assumed to be first/final boundary frames. The prompt permits a new camera composition inside the referenced set but forbids redesigning it, adding handheld objects, duplicating the entrance or opening it twice. One door moves monotonically from closed to approximately 60 degrees exactly once.
* The first corrected wording triggered Google's known-person image safety classifier. The generator-facing revision now describes Cruz and Marcus only as original fictional stylized 3D model sheets and requests series-design continuity (hair silhouette, palette, wardrobe, proportions) rather than exact identity or face replication. Environment and one-door geometry remain strictly reference-bound.
* That revision still triggered the same classifier. A plausible text-side collision is the heroine name `Cruz`, which can be interpreted as a known-person surname when combined with a portrait reference. Episode 02 clip 01 now contains no character names or known-person terminology at all; it uses only `fictional heroine` and `fictional security chief`. If the same error persists, the trigger is in at least one attached image rather than the prompt, so references must be tested individually instead of weakening motion physics.
* Superseded diagnosis: the user's character references are original non-real people, and the name was not established as the cause. The remaining prompt-side risk was likeness-transfer language itself: `character sheet defines`, `facial design`, skin/eye/body descriptors, `recognizable`, `reproduce` and repeated portrait-reference authority. H2 now avoids all face, likeness and person-replication wording. It requests continuity only for hairstyle, costume, officer uniform and the established animated set while preserving the one-door physics.
* H2 was subsequently rebuilt using character-only vocabulary. It contains no person/people/human/man/woman/identity/face/portrait/celebrity/famous/known/realistic/real terms and no character names. References are described only as fictional 3D character-design and set-design sources.
* The character-only vocabulary rule now applies to every active production prompt in `Episodes 02-24 Detailed!H2:K24`, not only H2. All 72 active prompts explicitly identify the on-screen cast as original fictional 3D characters and describe references as character/costume/set design sources; the 20 end-of-episode placeholder cells remain unchanged. A post-write readback verified zero occurrences of the human, portrait, realism or known-person trigger vocabulary used in the safety audit.
* Superseded audit state: on 2026-09-06 the former prompts scored approximately 52% against the user-provided 30-second SoloCruz comedy formula. The user then approved the proposed hybrid rewrite, so that score no longer describes the current production sheet.
* Current hybrid episode contract: every episode contains a self-contained cruise microstory with an event hook at 0–2 seconds, location and one concrete desire by second 6, a first failed attempt by second 13, a worsening second attempt by second 21, a completed local payoff by second 27, a funny visual callback at seconds 27–30, and only then a compact mystery/romance/Marcus tag. The ongoing three-line serial remains canonical and is not replaced by unrelated sketch plots.
* `Episodes 02-24 Detailed!C2:F24` and `H2:K24` were rewritten to this hybrid contract: 23 metadata rows, 72 generator prompts, nine edited shots in each 30-second episode and twelve in episodes 08, 16 and 24. Every ten-second prompt specifies exactly three clean-cut shots with one simple physical action per shot and a visible action/reaction at least every 1.5–2 seconds. Episode 02 still continues the finished pilot, but its single referenced door now opens exactly once within the first two seconds and is never replayed.
* Each episode now records both a specific comment prompt and the exact `This reel will be sent to ... because ...` audience rationale. Dialogue remains 5–31 words per episode, all 23 hooks occupy the literal 0–2-second block, every episode has two escalating attempts and a visual callback, and all active prompts remain free of the audited human/portrait/known-person vocabulary. The rewrite did not generate or publish media.

## 2026-09-05 — SoloCruz serial: authoritative three-line premise and existing pilot

* User-authoritative premise: (A) mysterious cruise expert Cruz, her hidden past and forced long-term life aboard, opposed chiefly by security chief Marcus; (B) changing passengers with independent life stories, including SoloCruz connections; (C) a slowly developing romance with a solo traveller who also conceals his past. These lines must intertwine without replacing the show with a different investigation.
* The user has an existing first episode: Cruz talks about living aboard for free 300 days per year and cruise secrets; ship security knocks at her cabin, and she invites viewers to follow for the resolution. Preserve that finished pilot. The actual media, exact duration and final frame have not been inspected; episode 2 begins with the same door knock/opening and needs a visual match before generation.
* Rejected: v2's suitcase/archive/mother storyline was an unauthorized change of the core story. The v2 sheet tabs now explicitly say REJECTED, and `docs/SOLOCRUZ_SERIES_V2.md` is marked rejected. Its mother mystery, Elias-as-Adrian's-brother and altered red watch are not canonical.
* Current review adaptation: `24 Episodes v3` (1319016408) and `Series Bible v3` (271825949) in spreadsheet `1LWI2SFMB3Ghg_mtsmoD4pTH3CAxMq9BdNqfmPC7t3bk`; local script `docs/SOLOCRUZ_SERIES_V3.md`. Original Season 1/Characters are preserved. 24 total positions = existing pilot plus 23 rewrites, with 72 new ten-second clips; pilot length remains unknown.
* v3 retains and maps original passenger, loyalty-offer, corridor, gala, storm, Evelyn and Adrian-revelation beats. Detailed new backstory is a proposed script, not user-approved historical fact. Marcus remains the principal antagonist even during limited cooperation; affection does not instantly excuse Adrian's deception.
* Entertainment-first adult 3D animation, not iPhone UGC. Episode-level hooks/payoffs, connected clips, short dialogue, prop continuity and earned character changes remain required. Sparse organic brand dialogue; retain the pilot CTA but do not add it routinely. 'Free' cruise claims must not become universal factual guarantees or gambling advice.
* No video generation, scheduling, publication or production-code change was performed for this rewrite.

## 2026-09-06 — YAS AI film hybrid short-episode production sheet

* Spreadsheet `1-Nn5AxeDEXm3MqJ95-0apfIFqWj-mKyqFO-pjPipMrk` now has a first-position authoritative production tab `Episodes 01-24 Detailed` (sheetId `1055500211`). The original `Лист1` remains unchanged as the concise source outline.
* The 24-episode series preserves the twelve original problem/solution business pairs, YAS's travel transitions, the Jaguar E-Type and the recurring mysterious-character line. Episodes are grouped into three eight-episode seasons; episodes 08, 16 and 24 are 40-second finales, while the other 21 episodes are 30 seconds.
* The hybrid structure is adapted from the SoloCruz formula without importing cruise subject matter: every episode opens on a literal physical hook at 0–2 seconds, establishes one operational goal by second 6, uses two worsening attempts, resolves one self-contained business problem, delivers a visual callback, then adds only a compact next-case or mystery tag.
* The tab contains 75 complete ten-second generator prompts. Every prompt specifies exactly three clean-cut shots, one main physical action per shot, visible change every 1.5–2 seconds, detailed object/contact continuity, short exact English dialogue, bounded fictional screen-character references, no narrator and no generated promotional overlays. Ordinary episodes contain nine shots; the three finales contain twelve.
* The authoritative prompt form is concise: each cell contains only the reference/cast boundary, exact timed three-shot staging, compact camera rules, physics relevant to the props in that scene, and audio/output constraints. Repeated generic directing theory is intentionally excluded. The 2026-09-06 cleanup reduced the 75 active prompts from an average of 4,853 to 1,630 characters while preserving the full staging and dialogue.
* Every episode records a comment question plus a specific `This reel will be sent to ... because ...` rationale. The original outline is not overwritten, and no video, social draft, schedule or publication was created by this rewrite.

## 2026-09-05 — SoloCruz animated serial v2 direction (plot rejected; see v3 above)

* The user rejected iPhone UGC for the Cruz serial. This series uses the existing adult stylized 3D character designs in the source spreadsheet, not photorealistic phone footage. The earlier standalone UGC direction below is historical and must not be applied to this serial.
* Superseded v2 review script: 24 episodes across three eight-episode seasons; 21 episodes of 30 seconds and three season finales of 40 seconds, assembled from 75 connected ten-second clips. v3 instead preserves the existing pilot and supplies 72 new clips. Each episode, not each generation clip, remains the dramatic unit.
* Superseded: v2's family/mother mystery is rejected. Entertainment, Cruz's own past, changing passenger lives and romance lead in v3. Do not impose a brand mention, sales explanation or CTA in every episode.
* Source spreadsheet `1LWI2SFMB3Ghg_mtsmoD4pTH3CAxMq9BdNqfmPC7t3bk`: new tabs `24 Episodes v2` (1301293975) and `Series Bible v2` (1790453071), preserving all original tabs. Local text version: `docs/SOLOCRUZ_SERIES_V2.md`.
* Detailed staging, object custody, continuity and short attributed dialogue are required. Script timings are design targets, not verified media durations; no generation, queue or publication was authorized or performed for this rewrite.

## 2026-09-05 — SoloCruz short-form Reel creative direction (historical; superseded for the animated serial)

* SoloCruz Reels sell the emotional upside of travelling with a compatible cruise companion: shared reactions, laughter, photos and stories, with cabin-cost splitting as a secondary benefit. They must not frame the service through danger, cancelled travel, fear of strangers or an explanation-first sales funnel.
* The approved short-form direction is bright, joyful, photorealistic 10-second vertical stories with one immediate pattern interrupt or social question. Strong reusable formats are: `This is not a Tinder date`, `The best cruise upgrade costs less`, `Would we survive one cabin?`, shared-reaction travel moments, and playful cabin-mate character scenes.
* SoloCruz Reel footage must look like spontaneous premium iPhone UGC recorded by a friend on the cruise: handheld vertical framing, natural exposure shifts, real imperfect reactions and intimate proximity. Do not use cinematic, commercial, glossy-ad, studio-lit or stock-footage direction.
* Spoken audio is selected by the scene: use short, natural on-camera lines from the heroines when their interaction carries the hook or twist; use a warm, pleasant female voiceover for an internal thought or an emotional travel moment. Either delivery is brief, conversational and emotionally observant, never a sales-announcer delivery; on-screen copy remains a separate exact overlay.
* Generated visual footage must contain no readable title, caption, logo, UI or watermark. Any exact hook or brand copy is added separately by the renderer so text remains correct and legible.
* The first six standalone Omni review Reels are stored in production under `data/social_assets/7/solocruz-ugc-omni-20260905/` and mirrored as noindex review assets under `ugc-omni-20260905/instagram/`. They are all 10.005-second 720×1280 H.264/AAC files: `not-a-tinder-date`, `best-upgrade`, `survive-one-cabin`, `shared-reaction`, `cruise-person`, and `two-main-characters`. They are not social-post rows and are neither scheduled nor published.
## 2026-09-06 — yas.ooo X delivery fails inside the X-specific Zernio path

* Blog Core site `12` (`yas.ooo`) has a valid stored X account mapping but no site-specific Zernio key, so it falls back to the server-side `ZERNIO_API_KEY`.
* Superseded: a 401 from the read-only `/accounts` probe does not establish that the shared key is unusable for publication. YAS successfully submitted Threads through Zernio with that same key after an X failure. LinkedIn is YAS's only direct publisher; its other mapped social destinations use Zernio.
* Scheduled X submissions from 2026-09-02 through 2026-09-06 all failed with HTTP 403, while their public media URLs returned HTTP 200. Zernio's activity log identifies the stable cause as `account_disconnected`: X account `YASflows` has an expired or revoked platform token. Reconnect the X account in Zernio, then refresh the mapped account ID from `GET /v1/accounts` before requeueing failed work items.
* `run_scheduled_evidence_x_publications` changes a failed due work item from `SCHEDULED` to `ERROR`; it does not retry that row after the X-specific connection problem is repaired. Recovery therefore requires correcting the X destination in Zernio and explicitly requeueing the failed items.
* Resolved later on 2026-09-06: the owner reauthorized `YASflows` in Zernio, the existing account ID remained valid, and all five failed items were resubmitted immediately and reconciled to `PUBLISHED`. The remaining 43 future X items retained their schedules.
## 2026-09-06 — X thread media must be attached to the root thread item

* For a Zernio X payload with `platformSpecificData.threadItems`, top-level `content` and `mediaItems` are not the published root tweet. Attach the intended cover to `threadItems[0].mediaItems`; later items remain text-only unless they have their own explicit media.
* The prior Blog Core payload attached X media only at the top level. Single tweets displayed their image, but multi-tweet threads published without it even though Zernio stored the top-level asset and reported `media_count: 1`.
* Resolved and deployed on 2026-09-06: the universal Zernio request builder now places supplied media in `threadItems[0].mediaItems` whenever a thread sequence exists, while retaining top-level `mediaItems` for ordinary single posts.
## 2026-09-06 — Social copy is authored naturally and normalized before delivery

* Every social-copy generation prompt must ask for direct, natural prose at generation time. It must prohibit long dashes, arrows, smart quotes, Markdown emphasis, generic AI filler, formulaic `not X but Y` reversals, generic `PROBLEM`/`SOLUTION` labels, fake quotations, vague hype and generic engagement bait.
* Publication performs a final deterministic typography normalization even after prompt validation: em/en/minus dashes become the ordinary hyphen, arrows become `to`, smart quotes become straight quotes, non-breaking spaces become ordinary spaces, and Markdown emphasis markers are removed. This is a safety net, not a substitute for correct generation instructions.
* X threads carry their existing creative on the root tweet through `threadItems[0].mediaItems`; top-level `mediaItems` is reserved for a single X post.

## 2026-09-07 — Queued publication failures use durable email alerts

* Failed due publication attempts across Blog Core's website and social delivery queues create durable email-alert records. Waiting for a connection or source is operational waiting, not a failure alert.
* Delivery reuses the VPS local sendmail/Exim path already used by SoloCruz. The recipient and optional sender live only in protected environment variables; no SMTP secret is stored in Blog Core data or documentation.
* Each failure event has a stable queue-record/slot fingerprint, so a scheduler pass or refined provider error wording cannot repeatedly email the same failure. Unsent alerts remain queued and retry with bounded backoff. Asynchronous Zernio failures discovered during reconciliation use the same path.
* Production publication alerts are delivered to the protected configured recipient through local Exim. Preserve destination-level provider fields such as Zernio `platforms[].errorMessage`; a top-level `failed` status alone is not an actionable alert.

## 2026-09-08 — Legacy NOMADeira editorial-plan rows are not publication-ready

* NOMADeira rows sourced from `nomadeira_editorial_plan` may carry the old boolean `generationBlockedUntilSourceReview=true` without the newer `complianceCluster` and `pageBrief` contracts. The earlier compliance generation/scheduling guards recognized only `complianceCluster`, so legacy rows could be generated or scheduled even though their source review was still explicitly blocked. This gap is closed: the legacy blocking flags now independently stop both generation and scheduling/publication.
* The native typed-page publisher correctly rejects such a row because it lacks the approved intent, SEO/H1/direct-answer fields, editorial ownership/review dates, source references, internal CTA and review/QA approvals. Do not synthesize these approvals from generated prose or bypass the publisher. Migrate the legacy row into the current evidence contract and complete its real reviews before rescheduling.
* The eight NOMADeira editorial-plan rows formerly scheduled for 8–15 September 2026 now use `2026-09-08-editorial-plan-migration-v1`. They are private `BLOCKED_EVIDENCE` tasks with no schedule, active draft, localization or active hero reference. Their original intent, route, locale and required-authority requirements remain preserved; no source, claim, review, approval or QA state was inferred.
* `/madeira-residence-registration-eu/` is `CANONICAL_REVIEW_REQUIRED` because it may overlap the existing Phase-A CRUE guide. The other seven are `CANONICAL_CHECKED` but still require source collection and verified claims before generation.

## 2026-09-08 — NOMADeira EU registration guide uses the editorial-plan canonical

* Replaced: the canonical review for `/madeira-residence-registration-eu/` is complete. That route is the sole published CRUE-supporting guide; the unpublished Phase-A job `madeira-crue-eu-residence-certificate` is canceled as superseded and must not be revived as a second public page.
* The guide's high-risk evidence boundary uses the current AIMA registration-certificate page together with the gov.pt service page. It covers only listed nationality and stay scope, the 30-day period after the first three months, the responsible `Câmara Municipal`, identity evidence and AIMA's alternative evidence categories. It never infers individual eligibility, appointment availability, processing time, acceptance, fees or unstated local procedure.
* NOMADeira renders contextual links already embedded in `draftHtml`. For this published record the native payload's duplicate `internalLinks` array is cleared after the atomic write, while the reviewed link ledger remains in Blog Core for validation. Otherwise NOMADeira adds the same contextual link a second time.
* NOMADeira's sitemap is a static Next.js build artifact. Publishing a new filesystem-backed record requires a successful NOMADeira production build and service restart before the route and its localized alternates appear in `/sitemap.xml`.
## 2026-09-06 — SoloCruz's central free-cabin premise

* Cruz lives in guest cabins that remain unsold or become vacant after cancellations, moving before the next assignment. The cabin may be empty in inventory, but it is not hers: unauthorized occupancy creates safety-manifest, housekeeping, inventory and removal consequences, which is why she hides from ship security.
* The pilot's security knock flows directly into episode 2, `Пустая на бумаге`. Cruz does not open the door in its first clip. Security identifies the cabin as registered empty, leaves to obtain Marcus and an override key, and Cruz performs a practiced exit. Marcus arrives seconds late, finds the remaining pillow indentation and says, `She was here.`
* The earlier explanation based on a fully valid paid booking, public guest-expert status, accumulated credits or a cabin supplied for speaking is superseded as the central secret. Such devices must not erase the unauthorized-empty-cabin premise or make Marcus's pursuit illogical.

## 2026-09-12 — Independent native blogs for Karp and Veselova Veronika

* `karpaleksei.com` (site `17`) and `veselovaveronika.com` (site `19`) are independent `native_content_store` targets. Their code, data, database and renderer processes must never share a write boundary.
* Karp uses code `/var/www/karp-preview`, content root `/var/lib/karp-preview/data`, generated artifacts `/var/lib/karp-preview/generated`, PostgreSQL database `karp_preview`, project id `karp-aleksei-jade-mills-homepage-ms4qtdi3` and artifact port `3045`.
* Veronika uses code `/var/www/veronika-preview`, content root `/var/lib/veronika-preview/data`, generated artifacts `/var/lib/veronika-preview/generated`, PostgreSQL database `veronika_preview`, project id `veselova-veronika` and artifact port `3055`.
* `sites.root_path` remains the code root. The separate optional `sites.content_root_path` owns native Blog Core JSON under `<content_root_path>/blog-core/{drafts,published}`. Falling back to `<root_path>/data/blog-core` remains supported for older native sites.
* Both sites are RU-first with an English `/en` variant. Their renderers keep the existing native blog header, footer, typography and listing-card structure. Published JSON adds native `/blog/{slug}` and `/en/blog/{slug}` pages; `/content-preview/{jobId}` reads drafts and is always `noindex`.
* A live verification article requested for visual/operator review is not disposable test data. Leave it published until the operator explicitly requests removal. Karp's persistent verification article is `Как выбрать новостройку в Казани` at `/blog/kak-vybrat-novostroyku-v-kazani`, with English at `/en/blog/how-to-choose-a-new-development-in-kazan`.
* Structured-copy deduplication is multilingual. Its normalization key must retain Unicode letters; an ASCII-only `[^a-z0-9]` key erases Cyrillic and other non-Latin article paragraphs and list items instead of merely removing duplicates.
* Karp's active verification article is a complete native RU/EN publication, not the former five-paragraph fixture: eight sections, three inline images, a comparison table, seven-step checklist and six FAQ entries. When a native record has the same localized title as an existing placeholder card, the renderer replaces that card in place rather than adding a duplicate.
* Karp native articles extend the site's established black, ivory and muted-gold editorial language. Structured components are deliberately styled rather than left to browser defaults: bordered evidence tables, numbered checklist cards, serif pull quotes, two-column contents and accessible plus/minus FAQ rows, with single-column/mobile-scroll adaptations below 760px.
* Karp's blog index markup is tag-sensitive: native cards must remain `span.blog-list__item`. Never clone runtime property-card anchors or replace the outer tag. Update a matching placeholder in place and use an absolutely positioned inner anchor for article navigation; any populated date needs card-scoped block spacing.
* Veronika's first persistent native publication is `Как сформировать техническое задание на частный дом` at `/blog/kak-sformirovat-tehnicheskoe-zadanie-na-chastnyj-dom`, localized at `/en/blog/how-to-write-a-brief-for-a-private-house`. It uses the existing approved Veronika house/brief/location/engineering media and remains published until explicitly removed.
* Veronika's native article components use only the approved solid maroon `#6b1730`; depth comes from translucent white layers, borders and the existing white/rose editorial hierarchy, never a second solid maroon. Her blog-index cards follow the same tag-sensitive `span.blog-list__item` preservation and inner overlay-link contract as Karp.
* Resolved global Veronika contact-section layout: on viewports from 561px the title, primary CTA and messenger row form one horizontally centered group placed below the section midpoint; the section retains its authored 850px height and portrait background. On mobile, the primary contact CTA is intrinsic-width rather than full-width and matches the Home hero CTA's 59.2px height and `22px 50px` padding; its width grows only for its longer label. The rule belongs to the shared published-site materializer, not native article CSS, and its artifact presentation version must be bumped and all routes warmed after changes.
* Each site's dynamic sitemap reads the same published store and adds only the available RU/EN article routes. Drafts never enter the sitemap.
