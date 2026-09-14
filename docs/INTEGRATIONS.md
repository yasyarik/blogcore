# INTEGRATIONS.md

## Native content-store publisher contract — published 2026-09-14

* Replaces the prepared-only note below. Commit `c112a3e` is live: republishing
  preserves the first non-empty `publishedAt`, exports
  `pageBrief.contentProfile`, and refuses to overwrite malformed, wrong-shape or
  different-job native JSON.
* The 11-case test extracts only the four publisher functions into a temporary
  store with a fake locale query. It never imports Flask, opens the production
  DB or mutates a real content record.
* This is not a retroactive metadata repair. Historical dates may be restored
  only from their exact protected recovery records after separately checking
  current article state.

## Personal media-plan Telegram reminders

* A site's Telegram connection may additionally store `reminder_chat_id`, the numeric private chat of the person responsible for live Reels. The owner must message the bot before the connection test can resolve that private chat.
* `chat_id` remains the Telegram publication channel and `reminder_chat_id` remains the private reminder recipient. Never fall back from the latter to the former.
* Only media-plan rows whose execution mode is `human-owner` or `manual-owner` generate reminders. Factory-owned articles, carousels, Telegram posts and Threads posts do not create personal-action alerts.
* Each live Reel has deduplicated reminders 24 hours before the recording deadline, three hours before publication and at publication time. Sent/error state is persisted in `agent_media_plan_reminder_events`.

## Publication failure email alerts

* Every failed due publication from the website, generic social, shared carousel, Instagram Reel, TikTok carousel, evidence-X, Threads, and Facebook queues is persisted as an email-alert event. Waiting-for-connection and no-source states are not failures.
* Blog Core uses the same local `/usr/sbin/sendmail` to Exim delivery path already proven by SoloCruz. It does not add another email provider or store SMTP credentials in SQLite.
* `PUBLICATION_ALERT_EMAIL_TO` enables delivery. `PUBLICATION_ALERT_EMAIL_FROM` optionally overrides the sender identity. Both belong only in the protected production environment.
* A stable event fingerprint based on the queue record/slot prevents duplicate messages for the same failed attempt even when a provider later supplies more precise error wording. Failed email delivery remains queued and retries with exponential backoff capped at one hour.
* The email contains the site, queue/channel, content title and IDs, UTC failure time, provider error, and a link to the site's Blog Core control panel. Zernio failures reported asynchronously during reconciliation enter the same alert path.

## Universal Google Search Console collection

* Per-site GSC configuration uses an exact URL-prefix property such as `https://example.com/` or a domain property such as `sc-domain:example.com`.
* Blog Core uses the server-managed service account with the read-only Search Console scope. It never stores, renders, logs or commits credentials or their filesystem paths.
* Setup verifies that the service account can see the selected property and then enables automatic finalized-data collection. Query and page metrics are retained separately; no false complete query/page join is inferred.

## SEO Agent reporting and topic discovery

* The `/agent` control point reads channel connection state and publication records already owned by Blog Core; it does not probe or mutate third-party accounts while rendering the dashboard.
* Scheduled audits run from `scheduler.py` no more than once per 30 minutes. Demand discovery is intentionally omitted from routine 30-minute runs; manual smart audits or explicitly enabled per-site autonomy may invoke the existing popular-search/Reddit Discovery pipeline.
* Optional Telegram summaries use protected environment variables `AGENT_TELEGRAM_BOT_TOKEN` and `AGENT_TELEGRAM_CHAT_ID`. Never store or render their values. Telegram is outbound reporting only and has no inbound command handler.
* Auto-created content remains a normal `content_jobs.status=QUEUED` record and must pass the normal generate, preview, validate, and publish boundaries.
* `POST /api/agent/sites/{site_id}/discover-topics` runs demand discovery for one site from an explicit recommendation action. It returns topic recommendations with source evidence and duplicate validation; it does not create or publish content jobs.
* Agent error analysis reads failed Blog Core content/social records and classifies the stored failure text locally. Rendering `/agent` remains read-only and never probes external providers.

* CabinJoin site `15` uses `native_content_store` publication into the shared CabinJoin content root. On 2026-07-27 Blog Core published the new boat-owner/operator page and replaced organiser copy across EN/RU/FR/ES/DE. CabinJoin consumes only explicitly published records at the exact stored target path; no locale or content fallback is permitted.

## Native content-store typed route contract

Native JSON records preserve `contentType` and `targetPath`.

Supported normalized values:

* `blog` -> `/blog/{slug}/`
* `guide` -> `/guides/{slug}/`
* `template` -> `/templates/{slug}/`
* `example` -> `/examples/{slug}/`
* `integration_guide` -> `/embed/{slug}/`
* `use_case` -> `/use-cases/{slug}/`

Native adapters must route the same path below each configured non-default
language prefix, keep previews on the adapter's `noindex` preview endpoint, and
look up published records by `contentType + slug`. Published filenames must be
collision-safe across content types.

## Public site scanner

* Fetches the homepage with `urllib.request` and user agent `YASBlogCore/0.1 (+https://blog.yas.ooo)`.
* Captures title, meta description, CSS URLs, inline style blocks, body class, colors, fonts, nav/header/footer HTML.
* Absolutizes relative `src`, `href`, `poster`, and `action` attributes in captured chrome.
* Avoids using hero-like headers as site chrome if the captured header includes hero classes or `<h1>`.

## Native blog rendering

If scanned CSS contains `.section`, `.blog-card`, `.blog-carousel`, and `.container`, Blog Core renders native-pattern blog markup. Otherwise it falls back to generic `blog-core-*` classes.

## Hosted CNAME routing

* `sites.custom_blog_domain` stores the external blog host.
* `sites.hosted_blog_enabled=1` enables Host-based routing.
* Unknown non-admin Host requests are matched to `custom_blog_domain`; if no site matches, return 404.
* Hosted blogs serve `/`, `/blog/`, `/blog-core.css`, `/robots.txt`, `/sitemap.xml`, and sample article route.

## DNS/CNAME checks

* `check_cname_status()` resolves the custom blog domain and compares IPs to `HOSTED_BLOG_IPS` or `CNAME_TARGET` resolution.
* Status values: `not_configured`, `active`, `wrong_target`, `dns_pending`.

## Topic discovery

* `Scan design` also infers the site's topic profile. When Gemini is configured, Blog Core asks Gemini to produce `direction`, `categoryHint`, `contentContext`, and `topicStrategy` from the scanned homepage title, description, header/nav, footer, brand, and domain.
* Auto-inferred topic profile values are written only into empty settings by normal scans so manual overrides are preserved. A deterministic metadata fallback is used when Gemini is unavailable.
* Popular search signals use Google autocomplete/search suggestions with a query derived from the site's Discovery direction/category hint/topic profile. This is a non-news search-demand source, not Google News RSS and not the official Google Trends API.
* Popular search suggestions are deduplicated, filtered for broad/non-local/non-promotional/non-navigation intent, relevance-scored against normalized topic query candidates, and only positive-score items are returned. The selected range does not affect Google autocomplete suggestions; it only affects Reddit.
* Discovery topic query candidates normalize common short/compound terms (`AI`, `UGC`, `user generated content`, `e-commerce`) before source fetches.
* Discovery topic query candidates are built from the full site context: scanned profile/settings plus existing content job titles, descriptions, categories, slugs, and URL paths. Multilingual sites prefer English/canonical records when available.
* Query candidates prioritize multiword content/product clusters and configured vertical signals over single generic tokens. Career/vendor autocomplete tails such as jobs, salaries, engineers, and developer searches are filtered out.
* Reddit signals use Reddit search RSS with `sort=top` and time range mapping across several normalized query candidates. Only `/comments/` discussion URLs with a strong site-topic anchor and contextual title match are returned; broad matches on generic words and accidental substrings are rejected.
* Reddit may rate-limit with `429 Too Many Requests`; source failures are returned as API `warnings` and must not render as selectable cards.
* The topic signal API returns a backward-compatible combined `signals` list plus source-specific `sources.popularSearches` and `sources.reddit` blocks. Each source block includes `signals`, `warnings`, and `meta` with `raw`, `kept`, `filteredGlobal`, `filteredRelevance`, `deduped`, `limit`, and `rangeApplies`. `sources.popularSearches.rangeApplies=false`; `sources.reddit.rangeApplies=true` and includes the Reddit bucket (`week`, `month`, or `year`).
* The Discovery UI uses all usable returned signals automatically. It should show deep-analysis status and compact source counts/warnings, not a manual checklist of raw topic cards. The idea-generation button is disabled until signal analysis completes.
* `POST /api/sites/{site_id}/article-ideas` generates reviewable idea candidates from selected Discovery signals and returns `rejectedSimilar` for topics filtered as too similar to existing site content. It must not create `content_jobs`.
* Article idea generation uses a Google Search Central 2026-informed journalist/SEO prompt. The prompt treats trend/search/Reddit items as audience signals, not titles, and asks Gemini to create non-commodity, site-specific topics with `target_query_cluster`, `business_relevance`, `unique_site_context`, and `duplicate_check` fields.
* Article idea validation applies a site editorial policy before ideas are shown. The policy rejects obsolete years, copied signal titles, generic review/listicle/comparison/buyer-framework formats, and build/setup/configuration/tutorial formats unless the site's stable profile/settings explicitly allow those formats. Existing content is used for context and duplicate checks, not to authorize bad formats.
* `target_query_cluster` values and the visible idea source line are normalized before returning to the UI. Raw autocomplete modifiers such as `best`, `top`, `review`, `comparison`, and obsolete years are stripped/rejected so they do not leak into article cards, slugs, or downstream planning.
* Article idea validation deduplicates against already accepted ideas in the same response using semantic comparable text plus editorial diversity fields such as `topic_axis` and `audience_problem`, not only exact title matching.
* Article idea generation returns `counts` with `generated`, `accepted`, `rejected`, `signals`, `passes`, and `safetyCap`. Gemini can run multiple passes until a pass adds no new valid ideas or the technical safety cap/max-pass guard is reached; there is no product target count.
* `POST /api/sites/{site_id}/article-ideas/queue` creates `content_jobs.status=QUEUED` only for operator-selected ideas and reruns the similarity check before writing jobs.

## Jobs

* `publish_jobs` stores queued/completed/failed jobs.
* Current job kinds include `install-blog`, `topic-plan`, and `article-ideas`.
* `article-ideas` stores selected signals, selected idea drafts, and duplicate-filter results as JSON in `message` after ideas are queued.

## Source-authoritative factory bindings

* `site_factory_bindings` connects a Blog Core site to a compatible local source factory. A binding includes the factory name, loopback base URL, native publishing-path prefix, and `source_site_authoritative` ownership mode.
* For a bound site, a new Blog Core queue item remains the dashboard record, but `Generate` first creates its corresponding source job through `POST /api/jobs`; its native job ID is saved in `sources_json.oldFactoryJobId`.
* Blog Core then uses the source factory's job detail, preview, generate, and publish endpoints. It synchronizes result/status data but never publishes generic files into the source webroot or replaces the source template.
* PipsAlerts binding: `content-factory-pipsalerts` at `http://127.0.0.1:13095`, with native guide routes at `/guides/{slug}/`. The factory and Next site live on the same VPS at `/var/www/content-factory-pipsalerts` and `/var/www/pipsalerts`; do not store credentials in this document.
* SoloCruz binding: `content-factory-solocruz` at `http://127.0.0.1:12838`, with native public blog routes under `/blog/{slug}/` and localized counterparts. Its local webroot is `/var/www/solocruz.com`. The source factory uses server-only `SITE_MODE=seo_waitlist` and site configuration to render preview/publish in its existing public-page system; do not record credentials from its `.env`.
* SoloCruz source-factory blog generation uses 6-8 H2 sections, no more than 12 H3 sections, and five contextual `/blog/` internal links. The factory must not require invented non-blog URLs when its job contract supplies only blog context.
* SoloCruz native SEO pages are nested routes while generated article assets live in `/blog/`. Its renderer must rewrite relative generated image names to absolute `/blog/{filename}` URLs before publishing; otherwise hero and inline image requests resolve inside the nested page directory and 404.
* Native static source-factory pages must use the connected site's own locale-aware header, footer, CSS, and interaction script extracted from its published homepage. Factory fallback chrome is allowed only when no native page chrome can be found; it must not replace an existing site design.
* When native static chrome includes a language selector, its links must be generated from published versions of the current canonical page, not copied homepage locale URLs. If the article has only one published locale, omit the selector rather than sending readers to a localized homepage. Copy the source homepage's favicon, Apple touch icon, and manifest links into the generated page head.
* A multilingual SoloCruz publication is complete only when a native job exists and is `PUBLISHED` for every intended locale under one canonical group. After the final locale is published, re-publish the group so each page's hreflang/language selector contains all real article URLs.
* SoloCruz native SEO blog publication rebuilds the relevant locale `/blog/` index and feed. It must preserve manually authored cards and maintain factory-generated cards in a marked block instead of replacing the source index layout. Generated article pages expose `og:image` so index cards can resolve their hero image.
* The SoloCruz GSC submit adapter calls the Search Console Sitemaps API after native publication, but the current configured service-account file is absent. Public sitemap/robots availability is not evidence of successful GSC submission.
* 2026-07-21 adapter audit: YAS Wine, My UGC Studio, LaycanMatch, and PipsAlerts published samples have native header/footer; their image handling is native to their distinct adapters (My UGC's hero is CSS-background based). AIREP24 uses its separate live-template adapter. One old AIREP24 French source job still claims a removed `/fr/features/...` URL; it must be corrected as a content migration, never republished over the current English page automatically.
* YAS Wine binding: `content-factory-yaswine` at `http://127.0.0.1:3199`, with native article and SEO-section publication in `/var/www/yaswine`. Blog Core links the factory's primary `jobs` records; entries also present in `seo_jobs` are identified as `seo_money_page` but continue to use the same native job API. The factory's article template is kept at a private path outside the public webroot via `FACTORY_ARTICLE_TEMPLATE_PATH`; `/blog/template.html` must remain unavailable publicly.
* My UGC Studio binding: `content-factory` at `http://127.0.0.1:3099`, with native blog URLs under `/blog/{slug}.html`. The source factory remains responsible for multilingual generation, its own static output, and publishing.
* LaycanMatch binding: `content-factory-laycanmatch` at `http://127.0.0.1:13157`. Existing native routes include `/resources/`, `/features/`, `/use-cases/`, and `/comparisons/`; Blog Core preserves an existing job's native `targetPath` instead of moving it under a generic blog route.
* AIREP24 binding: `content-factory-airep24` at `http://127.0.0.1:12631`, with native product, feature, use-case, comparison, and blog route support. Its source-template preview adapter remains the authority for draft preview rendering.
* `POST /api/sites/{site_id}/source-factory/sync` synchronizes a bound source factory's inventory into Blog Core without generating, publishing, changing a source page, or creating a public mirror. Matching is by existing source job ID, canonical URL path, then slug. It can safely be rerun.
* `POST /api/sites/{site_id}/source-factory/backfill` is the inverse one-time migration for imported records that predate their source factory: it creates only `NEW` source jobs with the preserved type, locale, canonical group, and target path, then stores the source IDs in Blog Core. It never generates or publishes and is safe to rerun because already linked records are skipped.
* Source-factory lifecycle requests resolve the endpoint from `site_factory_bindings` first. The old factory-name endpoint map is only a fallback for records created before bindings existed.
* Explicitly scheduled article jobs use `content_jobs.scheduled_for` and the separate `blog-yas-core-scheduler` PM2 worker. At the scheduled UTC time it starts native generation, waits for the source factory to return a draft, then publishes through that same source factory. This worker never creates or publishes social posts. Only jobs with an explicit timestamp are eligible.

## Native content-store sites

* `sites.access_type=native_content_store` identifies a first-party site whose factory is Blog Core itself. It is not a source-authoritative imported-site binding.
* Generation uses the universal Blog Core article schema, four article images, and validation. Draft preview writes `{root_path}/data/blog-core/drafts/{job_id}.json`; explicit publication writes `{root_path}/data/blog-core/published/{slug}.json`.
* A multilingual native-store record has one base `language`, the configured `languages`, and a `translations` object keyed by locale. Blog Core stores generated variants in `content_job_localizations`; each variant preserves the canonical slug and image filenames while translating the complete validated structured article.
* The site renderer owns its public header, footer, layout, schema markup, canonical URL, index, and sitemap. Blog Core owns editorial state and generated assets.
* EPR Scan uses this contract as site `20` for `/blog/{slug}` only. Its language set is exactly `en`, `de`, `fr`, `es`; the site-level `source_audited_multilingual_compliance` contract requires complete variants, a claim-by-claim ledger over 2–5 live official sources, translation number/structure/link parity, SEO checks and browser QA. It does not require or imply a human reviewer. See `docs/EPRSCAN_INTEGRATION.md`.
* The 2026-09-02 EPR Scan TOR produced 11 source-audited blog jobs and 33 DE/FR/ES localizations. Recommendations remain proposals until explicitly materialized; recommendation creation never authorizes generation or publication.
* EPR Scan blog indexing is fail-closed on the automated audit record. Russian and Italian are never generated as site languages. Static localized routes retain their separate page-level manifest until migrated to the same evidence contract.
* EPR Scan runs a weekly read-only production crawl from its own systemd timer. In addition to the fixed release contract, it discovers every sitemap page and internal target, so newly approved Blog Core articles are automatically covered; failures are persisted and visible in the systemd journal but do not trigger publication or mutation.
* EPR Scan's strict Lighthouse check is a separate three-attempt release gate (median Performance/LCP, minimum Accessibility/SEO, maximum CLS). Do not place it in the low-priority weekly service: synthetic timings were materially distorted there. Real-user LCP/CLS/INP are collected through the protected first-party analytics path.
* Blog Core-owned renderers use shared `native_site_chrome.py` to read current source header/footer and stylesheet links from `sites.homepage_url` with a short cache. The saved `site_theme_profiles` scan is a fallback, not the ongoing public chrome authority.
* Relative Blog Core article assets under `/sites/{site_id}/article-assets/` must be resolved against `https://blog.yas.ooo` by the native renderer; they must not be interpreted as source-site paths.
* Georivo uses this contract as site 14. Its renderer is deployed at `/var/www/georivo-blog`, listens on loopback port `13340`, and serves EN at `/blog/`, DE/ES/FR/RU at `/{language}/blog/`, plus noindex `/content-preview/{job_id}?lang={language}` pages through `georivo.com`.
* Georivo's content context covers interactive photorealistic 3D location stories for real estate, Property Showcase, Neighborhood Story, Arrival Guide, programmed camera routes, protected links, domain-bound embeds, and post-playback live exploration. Discovery must use the complete stored context and uniqueness checks, not only the homepage headline.
* Georivo presentation parity is source-contract based. The renderer loads the source compiled CSS and source assets, uses the exact source header/footer class structure, and supplies only namespaced journal/article styles. Its mobile breakpoint retains the source `Menu`/`.nav-links.open` interaction rather than substituting a separate blog navigation.
* Georivo's first typed rollout contains 19 canonical records: 8 Guides, 3 Templates, 4 Examples, and 4 Integration guides. Each record contains DE/ES/FR/RU translations under one EN task. The public sitemap contains all 95 typed language URLs.
* Typed draft generation runs a structured author pass followed by a structured factual-editor pass. Deterministic post-processing restores the approved direct answer, H1/meta, standalone safety section, approved contextual links, three intent-selected Recommended next links, and required table/list/image/FAQ structure before final validation.
* Article validation rejects visible model-control artifacts as well as malformed JSON. A syntactically valid response containing code fences, chain-of-thought markers, `json_block`, or final-output narration must fail generation and be regenerated, not silently published.
* `deploy/georivo/audit_content_plan.py` is the independent static/public contract audit. `deploy/georivo/visual-test.js` is the browser gate for 19 pages across five desktop locales plus one mobile EN viewport per page (114 checks). Lazy images must be scrolled into view and decoded before they are judged broken.
* The daily `georivo-content-audit.timer` reruns the public audit. It does not generate, edit, or publish content.
* Replaced/deprecated 2026-07-25: Georivo GSC submission is no longer blocked by access.
* The factory service account has `siteFullUser` on `sc-domain:georivo.com`. `deploy/georivo/gsc_submit.py` successfully submitted and read back `https://georivo.com/sitemap.xml` through the official API with zero warnings/errors; initial processing returned `isPending=true`.
* `deploy/georivo/gsc_submit.py` validates the public XML, authenticates with the ignored service-account credential, checks `sites.list` for `siteOwner` or `siteFullUser`, submits through the official Webmasters v3 endpoint, reads back the sitemap record, and writes atomic runtime status. After submission it queries two complete 28-day Search Analytics windows, top page URLs, and URL Inspection for the configured canonical URL set. It never creates or verifies a Search Console property and does not persist query text.
* `georivo-gsc-submit.timer` retries daily. Controlled missing access exits `75`; systemd accepts that code so the timer remains healthy. Credential, public-sitemap, network, and unexpected API failures exit `1`.

## YAS Source Scanner draft ingestion

* `POST /api/integrations/source-scanner/sites/{site_id}/drafts` accepts a finished Studio article for the Scanner editorial project connected to that Blog Core site.
* It requires `X-Source-Scanner-Token`, matching the server-side shared secret. Do not log or document the value.
* The caller provides stable scanner article and project IDs, finished HTML, source attribution, optional hero/FAQ metadata and language metadata. Scanner media URLs are public `scan.yas.ooo` URLs so native previews can render them where supported.
* The first request creates a Blog Core `DRAFT`; repeat requests update the same unpublished task using `source_scanner_drafts` idempotency mapping. It never invokes generation, publication or social distribution.
* A request that would overwrite a `PUBLISHED` task is rejected; create a new Studio draft for a new live revision.
* `yas.ooo` retains its native YAS content-store preview preparation. Other sites receive a safe Blog Core `DRAFT` without assuming their publishing adapter or local filesystem contract.

## YAS Wine factory parity target

Blog Core is being adapted toward feature parity with `/var/www/content-factory-yaswine`:

* Article production queue is stored in `content_jobs` with per-site status, draft, FAQ, sources, and social publish fields.
* Job logs are stored in `content_job_logs`.
* Imported legacy factory jobs keep `sources_json.migratedFrom` and `sources_json.oldFactoryJobId`. Generate actions for those rows must delegate to the source factory API and sync the validated result back into Blog Core; they must not run the generic Blog Core generator.
* Distribution settings are per site in `autopublish_settings` and `topic_discovery_settings`.
* Social channel connections and credentials are stored per site in `social_connections`; do not use one global OAuth state for all sites. The Setup tab provides per-provider credential forms and `Test connect` actions. Secrets are never rendered back into the dashboard.
* Social connection tests use provider API probes for LinkedIn, Telegram, and Tumblr. X/Twitter, Pinterest, Instagram, Threads, and Reddit use the per-site Zernio connection: Blog Core calls `GET /accounts` with the server-default `ZERNIO_API_KEY` or a site override, then requires an explicit account ID mapping for every active channel. Do not document or render API keys.
* LinkedIn uses `POST /api/sites/{site_id}/social-connections/linkedin/connect`, which starts OAuth with `r_basicprofile w_member_social rw_organization_admin w_organization_social` and the configured callback `https://blog.yas.ooo/oauth/linkedin/callback`. The callback exchanges the code server-side, resolves the member through `/v2/me`, discovers eligible Company Pages through `/rest/organizationAcls`, and stores the issued access token plus both member and selected publishing identity URNs. A short-lived Secure callback cookie keeps OAuth state valid across multiple Gunicorn workers. Application credentials remain site-scoped encrypted values with the legacy ignored server environment as fallback; secrets are never rendered or documented.
* Automatic LinkedIn source selection accepts `PUBLISHED` jobs and live `IMPORTED` jobs with a non-empty `published_url`. Imported localized blog-index URLs ending at the configured `blog_path` are excluded. This eligibility expansion is LinkedIn-specific and does not broaden other social channels.
* Social text/creative adaptation is handled before publishing through `social_posts`. The endpoint `POST /api/sites/{site_id}/content-jobs/{job_id}/social-drafts` generates channel-specific drafts only for channels that are both selected in Distribution and configured/connected in Setup. If no active channel exists, the endpoint returns `400` and does not create drafts. When drafts are allowed, it stores `language`, `max_chars`, `char_count`, `include_link`, `validation_json`, and marks the matching `content_jobs.{channel}_status` as `drafted`.
* Social draft generation must preserve the article language. It reads `content_jobs.sources_json.language` for imported/localized pages and falls back to the first configured site language.
* Current strict social text limits: LinkedIn 3000 chars, Telegram photo caption 1024 chars, X/Twitter 280 chars per post, Tumblr 4096 chars, Pinterest description 500 chars, Instagram caption 2200 chars, Threads post text 500 UTF-8 bytes, and Reddit draft body 8000 chars/title 300 chars. Drafts are normalized and shortened before storage if Gemini returns over-limit text. For Threads, `social_posts.char_count` stores the UTF-8 byte count and validation JSON stores both `charCount` and `byteCount`. Instagram also has a practical generated-caption target of 700 characters, with at most three hashtags.
* Pinterest drafts store a native Pin creative in `social_posts.content_json.pin`: `pinTitle` (<=100 chars), `description` (<=500), `overlayText` (<=80), `altText` (<=250), `imagePrompt` (<=1000), a real generated 2:3 JPEG `imageUrl`, `recommendedSize=1000x1500`, and optional `destinationUrl`. The prompt treats Pinterest as evergreen search/discovery, not a post teaser.
* Instagram drafts store a native carousel creative in `social_posts.content_json.instagramCarousel`: one shared carousel caption, 5-10 slides, per-slide headline/subtext/image prompt/alt text for image generation/review, generated `imageUrl`, `imageMimeType=image/jpeg`, and `visualSpec.aspectRatio=4:5`. Gemini Image is called through the Gemini Interactions API with `GEMINI_API_KEY` or `GOOGLE_API_KEY`; optional `GEMINI_IMAGE_MODEL` can override the default image model. Generated JPEG slide files are written under ignored `data/social_assets/{site_id}/{job_id}/instagram/` and served by `/sites/{site_id}/social-assets/{job_id}/instagram/{filename}`. The review page is `/sites/{site_id}/social-posts/{post_id}/instagram-carousel`.
* Replaced/deprecated 2026-07-13: Instagram-only intermediary credentials. Instagram now uses the shared per-site Zernio transport alongside X/Twitter, Pinterest, Threads, and Reddit; Blog Core does not call Instagram Graph API directly.
* Threads is configured through the per-site Zernio mapping. Threads drafts select `question`, `observation`, `contrarian`, `micro_story`, or `objection_answer`; they remain short, conversational, and non-promotional with at most one hashtag. Media is one natural 4:5 JPEG with no overlay text/logo/UI screenshot under ignored `data/social_assets/{site_id}/{job_id}/threads/image-01.jpg`. The review page is `/sites/{site_id}/social-posts/{post_id}/threads`.
* Explicit `POST /api/sites/{site_id}/content-jobs/{job_id}/social-publish/zernio` submits ready Zernio-channel drafts. It is intentionally separate from draft generation and does not send anything without an operator action. Account mappings, a Pinterest board, and a Reddit subreddit must be present where relevant.
* The old YAS Wine prompt is not copied literally because it contains wine-only rules. Blog Core uses a universal prompt contract populated from connected site context and topic strategy.

Pending parity work after the initial backbone:

* Port real X/Twitter and Tumblr publishing routes. LinkedIn and Telegram publish directly from Blog Core; Zernio is not used for either connector.
* Port OAuth flows for providers that need OAuth, scoped to `site_id`.
* Port autopublish runner and scheduled topic discovery runner.
* Port final publish renderer/localization/sitemap/GSC behavior into the hosted/local Blog Core publishing model.

## Gemini podcast TTS

* Podcast production is configured per site in `podcast_settings`: enabled state, host label, Gemini voice name, voice direction, and target duration. No credential is stored in this table; Gemini uses the server-side `GEMINI_API_KEY` or `GOOGLE_API_KEY` already used by the factory.
* `POST /api/sites/{site_id}/podcast-episodes` creates a reviewable episode from a selected article. Blog Core first produces a spoken script with the text model, then sends chunked transcript text to Gemini TTS and assembles mono 24 kHz WAV audio under ignored `data/podcast_assets/{site_id}/{episode_id}/`.
* The default TTS model is `gemini-3.1-flash-tts-preview`; `GEMINI_TTS_MODEL` can override it. Gemini TTS is preview software and can occasionally fail transiently, so chunk-level retry is implemented. Do not store API keys or generated audio in Git.
* Supported selected voice names are Gemini prebuilt voices. They are site-specific voice profiles combined with direction such as pace/tone; they are not custom voice cloning. Google Cloud Custom Voice is a separate product/access path and requires a dedicated future adapter if enabled.

## Gemini Lyria brand music for Reels

* Blog Core creates per-site reviewable brand soundtracks with the Gemini Developer API model `lyria-3-clip-preview`. It is configured through server-side `GEMINI_MUSIC_API_KEY` when present, otherwise the existing server-side Gemini key resolution; no API key is persisted in SQLite or rendered in the dashboard.
* `reel_music_tracks` stores direction, vocal hook, model, review status, returned lyric/structure text, duration, and activation state. The ignored MP3 is stored under `data/reel_music/{site_id}/{track_id}/brand-track.mp3` and served only through its controlled Blog Core asset route.
* The default output is a 30-second Lyria Clip. It must be prompted as an original composition without imitation of a particular existing song, performer, film, or musical. Do not substitute an arbitrary external audio file as a fallback.
* Only one soundtrack can be `ACTIVE` for a site. It affects future Blog Core Instagram Reel renders only. The compositor loops/trims it across the Reel's complete duration and fades only at its boundaries. It remains audible as a low bed throughout, then ducks beneath every actual Gemini narration interval; sequential scene WAV timing prevents voice clips from overlapping. This continuous-ducked contract replaces/deprecates narrator-exclusive hard muting and never retroactively changes an assembled Reel or source-site page.
* Audio review is available in the Podcast tab through `/sites/{site_id}/podcasts/{episode_id}/audio/episode.wav`. Explicit publication creates the Blog Core URL `/podcasts/{site_id}/{episode_id}` and includes it in `/podcasts/{site_id}/feed.xml`.
* Blog Core-hosted podcast publication does not alter an imported source site's design or template. Publishing/embed back into an imported source site needs an explicit native source-factory adapter.

## Existing blog import

* Per-site import endpoints scan existing public `/blog/` URLs from `sitemap_index.xml`, `sitemap.xml`, `sitemap-blog.xml`, `/blog/sitemap.xml`, and `/blog/` links for external sites.
* If `sites.root_path` points to a readable local webroot, import discovery uses direct filesystem inventory instead of public fetch. It imports multilingual `/blog/` pages and SEO money pages under `wine-countries` and `wine-regions`, preserving each page's canonical URL and local file path.
* Replaced/deprecated 2026-07-03: The old limitation that `yas.wine` import only found 61 English `/blog/` URLs is obsolete for local webroot imports.
* Import creates `content_jobs` with `status=IMPORTED`, `published_url` set to the original canonical/source URL, saved metadata in `sources_json`, and captured article HTML in `draft_html`.
* Import is non-destructive: it does not delete, overwrite, or publish files into the target site root.
* For imported existing blogs, target publishing should update/create content in the same original site locations and URL structure. Blog Core should be the dashboard/control plane, not an indexed second copy by default.
* Hosted Blog Core rendering can currently list imported/generated jobs in `/blog/`, include them in `/sitemap.xml`, and serve `/blog/{slug}/` from saved job HTML. For imported blogs this should be treated as preview/mirror behavior until canonical/noindex or publish-back-in-place rules are implemented; for Blog Core-created blogs it can be the public hosting path.
# Central search notification and monitoring (2026-08-03)

* Publication validation stays inside Blog Core and runs before the published record is committed. The same transaction queues a search-notification job for configured sites.
* The scheduler invokes `deploy/search/search_sites.py notify`: GSC sitemap notification is event-driven; CabinJoin also sends the exact published URL to IndexNow using its protected host environment. Failures are explicit and retry at most five times.
* `deploy/search/search_sites.py monitor` reads GSC performance and representative URL Inspection data for every configured site without submitting sitemaps. Each site has an independent protected status file and one site's error does not prevent the other from running.
* Secrets remain in protected VPS files. Do not write keys, service-account identities, or raw environment values into Git or memory.
# Vertex AI image editing for Reel layers

* Service account authentication uses `VERTEX_AI_SERVICE_ACCOUNT_FILE`; never store its JSON contents in Git or project memory.
* Required project role for native Imagen editing: `roles/aiplatform.user`.
* Non-secret configuration: `VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`, and `VERTEX_IMAGEN_EDIT_MODEL`.
* The documented `imagen-3.0-capability-001` explicit-mask endpoint may return model-access `404` even with correct IAM. Blog Core treats that as model unavailability and uses scene-referenced isolated matte generation, never unconstrained scene editing.
* The fallback still uses the real production scene as an image reference; final coordinates, scale, collision handling, and contact treatment are owned by Blog Core.

# Gemini logo references for Reels (2026-08-13)

* Final brand-resolution scenes receive the connected site's verified source-owned logo as an image reference to the Gemini image request.
* Prefer a local brand SVG when available and rasterize it to a high-resolution transparent PNG before the multimodal request. Do not use screenshots or raster files that contain a baked checkerboard background.
* The image prompt requires one exact, contextual use on a plausible physical touchpoint. The renderer does not stamp, redraw, or corner-overlay the logo.
* The final camera trajectory must reveal the full branded context before the cut.
# NOMADeira content-engine handoff (2026-08-29)

* NOMADeira exposes a versioned machine contract at `https://nomadeira.com/api/blog-core/content-engine`.
* Consume it together with `https://nomadeira.com/api/blog-core/i18n-manifest` and `https://nomadeira.com/api/blog-core/editorial-plan`.
* Human implementation and acceptance criteria live in `docs/NOMADEIRA_AUTONOMOUS_CONTENT_ENGINE.md`.
* Legacy `nomadeira_editorial_plan` blocking flags are authoritative even when a row predates `complianceCluster`. `generationBlockedUntilSourceReview=true` blocks generation; either that flag or `publicationBlocked=true` blocks scheduling/publication. Migration into the current contract never infers sources, verified claims, reviews, approvals or QA from generated prose.
* The NOMADeira canonical EU registration guide is `/madeira-residence-registration-eu/` with DE, UK and RU variants in the same native record. The unused `/madeira-crue-eu-residence-certificate` candidate was never published and is canceled as superseded.
* NOMADeira's native renderer receives contextual link sentences inside `draftHtml`; when publishing this record, clear the duplicate native-payload `internalLinks` array after the store write. A production Next.js build and `nomadeira` service restart are required to refresh the statically generated sitemap after a new record is published.
* The contract contains no credentials. Source collectors, social publishers and media generation continue to use server-side configuration only.
* Do not create a canonical article for every social candidate. Route a candidate into a new/refreshed page only after canonical-intent and completeness checks pass.
# EPR Scan draft review handoff (2026-09-02)

* Blog Core writes English approval drafts to EPR Scan's private draft store separately from the strict published store.
* EPR Scan exposes a native-design review surface at `/content-preview/{jobId}`. It is `noindex`, no-store, excluded from the sitemap and visibly labelled as unpublished.
* An accepted English draft is the source for one Gemini Batch localization run to German, French and Spanish. Russian and Italian are not target locales. The first wave completed as 11 EN drafts plus exactly 11 DE, 11 FR and 11 ES variants.
* Watching the draft store may rebuild the native preview, but it does not publish an article. Public `/blog/{slug}` routes still require the full reviewed multilingual publication contract.
* Localized draft payloads are valid input to the private sync. The current preview intentionally renders the English source only; translations remain stored for later named-language review and do not enter public routes or SEO surfaces.

## Karp and Veselova Veronika native content stores

* Blog Core site `17` writes to `/var/lib/karp-preview/data/blog-core`; site `19` writes to `/var/lib/veronika-preview/data/blog-core`. Their application code roots stay `/var/www/karp-preview` and `/var/www/veronika-preview`.
* Each isolated Next renderer reads only its own `BUILD_YAS_DATA_DIR/blog-core`. It augments the existing native `/blog` card grid and renders published article routes with the site's existing chrome. Draft review uses `/content-preview/{jobId}` with `noindex,nofollow,noarchive`.
* After publication Blog Core warms the Karp artifact process on `127.0.0.1:3045` or the Veronika artifact process on `127.0.0.1:3055`; it no longer uses the former shared Build YAS port for these sites.
