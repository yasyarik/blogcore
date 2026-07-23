# INTEGRATIONS.md

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
* The site renderer owns its public header, footer, layout, schema markup, canonical URL, index, and sitemap. Blog Core owns editorial state and generated assets.
* Relative Blog Core article assets under `/sites/{site_id}/article-assets/` must be resolved against `https://blog.yas.ooo` by the native renderer; they must not be interpreted as source-site paths.
* Georivo uses this contract as site 14. Its renderer is deployed at `/var/www/georivo-blog`, listens on loopback port `13340`, and serves public `/blog/` plus noindex `/content-preview/{job_id}` pages through `georivo.com`.
* Georivo's content context covers interactive photorealistic 3D location stories for real estate, Property Showcase, Neighborhood Story, Arrival Guide, programmed camera routes, protected links, domain-bound embeds, and post-playback live exploration. Discovery must use the complete stored context and uniqueness checks, not only the homepage headline.

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
* LinkedIn personal profiles use `POST /api/sites/{site_id}/social-connections/linkedin/connect`, which starts OAuth with `openid profile w_member_social` and the configured callback `https://blog.yas.ooo/oauth/linkedin/callback`. The callback exchanges the code server-side, resolves `/v2/userinfo`, and stores the issued access token plus `urn:li:person:<sub>`. Application credentials remain only in ignored server `.env` variables `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, and `LINKEDIN_OAUTH_REDIRECT_URI`.
* Social text/creative adaptation is handled before publishing through `social_posts`. The endpoint `POST /api/sites/{site_id}/content-jobs/{job_id}/social-drafts` generates channel-specific drafts only for channels that are both selected in Distribution and configured/connected in Setup. If no active channel exists, the endpoint returns `400` and does not create drafts. When drafts are allowed, it stores `language`, `max_chars`, `char_count`, `include_link`, `validation_json`, and marks the matching `content_jobs.{channel}_status` as `drafted`.
* Social draft generation must preserve the article language. It reads `content_jobs.sources_json.language` for imported/localized pages and falls back to the first configured site language.
* Current strict social text limits: LinkedIn 3000 chars, Telegram 4096 chars, X/Twitter 280 chars per post, Tumblr 4096 chars, Pinterest description 500 chars, Instagram caption 2200 chars, Threads post text 500 UTF-8 bytes, and Reddit draft body 8000 chars/title 300 chars. Drafts are normalized and shortened before storage if Gemini returns over-limit text. For Threads, `social_posts.char_count` stores the UTF-8 byte count and validation JSON stores both `charCount` and `byteCount`. Instagram also has a practical generated-caption target of 700 characters, with at most three hashtags.
* Pinterest drafts store a native Pin creative in `social_posts.content_json.pin`: `pinTitle` (<=100 chars), `description` (<=500), `overlayText` (<=80), `altText` (<=250), `imagePrompt` (<=1000), a real generated 2:3 JPEG `imageUrl`, `recommendedSize=1000x1500`, and optional `destinationUrl`. The prompt treats Pinterest as evergreen search/discovery, not a post teaser.
* Instagram drafts store a native carousel creative in `social_posts.content_json.instagramCarousel`: one shared carousel caption, 5-10 slides, per-slide headline/subtext/image prompt/alt text for image generation/review, generated `imageUrl`, `imageMimeType=image/jpeg`, and `visualSpec.aspectRatio=4:5`. Gemini Image is called through the Gemini Interactions API with `GEMINI_API_KEY` or `GOOGLE_API_KEY`; optional `GEMINI_IMAGE_MODEL` can override the default image model. Generated JPEG slide files are written under ignored `data/social_assets/{site_id}/{job_id}/instagram/` and served by `/sites/{site_id}/social-assets/{job_id}/instagram/{filename}`. The review page is `/sites/{site_id}/social-posts/{post_id}/instagram-carousel`.
* Replaced/deprecated 2026-07-13: Instagram-only intermediary credentials. Instagram now uses the shared per-site Zernio transport alongside X/Twitter, Pinterest, Threads, and Reddit; Blog Core does not call Instagram Graph API directly.
* Threads is configured through the per-site Zernio mapping. Threads drafts select `question`, `observation`, `contrarian`, `micro_story`, or `objection_answer`; they remain short, conversational, and non-promotional with at most one hashtag. Media is one natural 4:5 JPEG with no overlay text/logo/UI screenshot under ignored `data/social_assets/{site_id}/{job_id}/threads/image-01.jpg`. The review page is `/sites/{site_id}/social-posts/{post_id}/threads`.
* Explicit `POST /api/sites/{site_id}/content-jobs/{job_id}/social-publish/zernio` submits ready Zernio-channel drafts. It is intentionally separate from draft generation and does not send anything without an operator action. Account mappings, a Pinterest board, and a Reddit subreddit must be present where relevant.
* The old YAS Wine prompt is not copied literally because it contains wine-only rules. Blog Core uses a universal prompt contract populated from connected site context and topic strategy.

Pending parity work after the initial backbone:

* Port real LinkedIn, Telegram, X/Twitter, and Tumblr publishing routes.
* Port OAuth flows for providers that need OAuth, scoped to `site_id`.
* Port autopublish runner and scheduled topic discovery runner.
* Port final publish renderer/localization/sitemap/GSC behavior into the hosted/local Blog Core publishing model.

## Gemini podcast TTS

* Podcast production is configured per site in `podcast_settings`: enabled state, host label, Gemini voice name, voice direction, and target duration. No credential is stored in this table; Gemini uses the server-side `GEMINI_API_KEY` or `GOOGLE_API_KEY` already used by the factory.
* `POST /api/sites/{site_id}/podcast-episodes` creates a reviewable episode from a selected article. Blog Core first produces a spoken script with the text model, then sends chunked transcript text to Gemini TTS and assembles mono 24 kHz WAV audio under ignored `data/podcast_assets/{site_id}/{episode_id}/`.
* The default TTS model is `gemini-3.1-flash-tts-preview`; `GEMINI_TTS_MODEL` can override it. Gemini TTS is preview software and can occasionally fail transiently, so chunk-level retry is implemented. Do not store API keys or generated audio in Git.
* Supported selected voice names are Gemini prebuilt voices. They are site-specific voice profiles combined with direction such as pace/tone; they are not custom voice cloning. Google Cloud Custom Voice is a separate product/access path and requires a dedicated future adapter if enabled.
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
