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
* The Discovery UI must show source-specific counts/warnings and must not imply the selected period affects search-demand autocomplete signals.
* `POST /api/sites/{site_id}/article-ideas` generates reviewable idea candidates from selected Discovery signals and returns `rejectedSimilar` for topics filtered as too similar to existing site content. It must not create `content_jobs`.
* Article idea generation returns `counts` with `generated`, `accepted`, `rejected`, `signals`, `passes`, and `safetyCap`. Gemini can run multiple passes until a pass adds no new valid ideas or the technical safety cap/max-pass guard is reached; there is no product target count.
* `POST /api/sites/{site_id}/article-ideas/queue` creates `content_jobs.status=QUEUED` only for operator-selected ideas and reruns the similarity check before writing jobs.

## Jobs

* `publish_jobs` stores queued/completed/failed jobs.
* Current job kinds include `install-blog`, `topic-plan`, and `article-ideas`.
* `article-ideas` stores selected signals, selected idea drafts, and duplicate-filter results as JSON in `message` after ideas are queued.

## YAS Wine factory parity target

Blog Core is being adapted toward feature parity with `/var/www/content-factory-yaswine`:

* Article production queue is stored in `content_jobs` with per-site status, draft, FAQ, sources, and social publish fields.
* Job logs are stored in `content_job_logs`.
* Imported legacy factory jobs keep `sources_json.migratedFrom` and `sources_json.oldFactoryJobId`. Generate actions for those rows must delegate to the source factory API and sync the validated result back into Blog Core; they must not run the generic Blog Core generator.
* Distribution settings are per site in `autopublish_settings` and `topic_discovery_settings`.
* Social channel connections and credentials are stored per site in `social_connections`; do not use one global OAuth state for all sites. The Setup tab provides per-provider credential forms and `Test connect` actions. Secrets are never rendered back into the dashboard.
* Social connection tests currently use provider API probes: Telegram `getMe/getChat`, LinkedIn `userinfo`, X `/2/users/me`, Tumblr OAuth 1.0 `user/info`, Pinterest API v5 `user_account`, and Threads `/me`. Instagram stores third-party intermediary credentials; a full publish/connect probe needs the intermediary API contract.
* Social text/creative adaptation is handled before publishing through `social_posts`. The endpoint `POST /api/sites/{site_id}/content-jobs/{job_id}/social-drafts` generates channel-specific drafts only for channels that are both selected in Distribution and configured/connected in Setup. If no active channel exists, the endpoint returns `400` and does not create drafts. When drafts are allowed, it stores `language`, `max_chars`, `char_count`, `include_link`, `validation_json`, and marks the matching `content_jobs.{channel}_status` as `drafted`.
* Social draft generation must preserve the article language. It reads `content_jobs.sources_json.language` for imported/localized pages and falls back to the first configured site language.
* Current strict social text limits: LinkedIn 3000 chars, Telegram 4096 chars, X/Twitter 280 chars, Tumblr 4096 chars, Pinterest description 500 chars, Instagram caption 2200 chars, and Threads post text 500 UTF-8 bytes. Drafts are normalized and shortened before storage if Gemini returns over-limit text, so stored `social_posts.char_count` must be `<= max_chars`. For Threads, `social_posts.char_count` stores the UTF-8 byte count and validation JSON stores both `charCount` and `byteCount`. Instagram also has a practical generated-caption target of 700 characters, with at most three hashtags.
* Pinterest drafts store a native pin creative in `social_posts.content_json.pin`: `pinTitle` (<=100 chars), `description` (<=500), `overlayText` (<=80), `altText` (<=250), `imagePrompt` (<=1000), `imageAspectRatio=2:3`, `recommendedSize=1000x1500`, and optional `destinationUrl`.
* Instagram drafts store a native carousel creative in `social_posts.content_json.instagramCarousel`: one shared carousel caption, 5-10 slides, per-slide headline/subtext/image prompt/alt text for image generation/review, generated `imageUrl`, `imageMimeType=image/jpeg`, and `visualSpec.aspectRatio=4:5`. Gemini Image is called through the Gemini Interactions API with `GEMINI_API_KEY` or `GOOGLE_API_KEY`; optional `GEMINI_IMAGE_MODEL` can override the default image model. Generated JPEG slide files are written under ignored `data/social_assets/{site_id}/{job_id}/instagram/` and served by `/sites/{site_id}/social-assets/{job_id}/instagram/{filename}`. The review page is `/sites/{site_id}/social-posts/{post_id}/instagram-carousel`.
* Instagram publishing is expected to call a third-party intermediary publishing server using per-site intermediary credentials (`api_key`, `api_base_url`, optional `instagram_profile`). Blog Core should not call Instagram Graph API directly unless this product decision is explicitly replaced.
* Threads is configured as a separate per-site provider with `access_token` and optional `threads_user_id`. Threads drafts use a Threads-specific prompt and byte validation: short conversational question/opinion, not promotional ad copy, at most one hashtag. Threads media is generated separately as one natural 4:5 JPEG with no overlay text/logo/UI screenshot and stored under ignored `data/social_assets/{site_id}/{job_id}/threads/image-01.jpg`; metadata is stored in `social_posts.content_json.threads.mediaUrls`. The review page is `/sites/{site_id}/social-posts/{post_id}/threads`.
* The old YAS Wine prompt is not copied literally because it contains wine-only rules. Blog Core uses a universal prompt contract populated from connected site context and topic strategy.

Pending parity work after the initial backbone:

* Port real LinkedIn, Telegram, X/Twitter, and Tumblr publishing routes.
* Port OAuth flows for providers that need OAuth, scoped to `site_id`.
* Port autopublish runner and scheduled topic discovery runner.
* Port final publish renderer/localization/sitemap/GSC behavior into the hosted/local Blog Core publishing model.

## Existing blog import

* Per-site import endpoints scan existing public `/blog/` URLs from `sitemap_index.xml`, `sitemap.xml`, `sitemap-blog.xml`, `/blog/sitemap.xml`, and `/blog/` links for external sites.
* If `sites.root_path` points to a readable local webroot, import discovery uses direct filesystem inventory instead of public fetch. It imports multilingual `/blog/` pages and SEO money pages under `wine-countries` and `wine-regions`, preserving each page's canonical URL and local file path.
* Replaced/deprecated 2026-07-03: The old limitation that `yas.wine` import only found 61 English `/blog/` URLs is obsolete for local webroot imports.
* Import creates `content_jobs` with `status=IMPORTED`, `published_url` set to the original canonical/source URL, saved metadata in `sources_json`, and captured article HTML in `draft_html`.
* Import is non-destructive: it does not delete, overwrite, or publish files into the target site root.
* For imported existing blogs, target publishing should update/create content in the same original site locations and URL structure. Blog Core should be the dashboard/control plane, not an indexed second copy by default.
* Hosted Blog Core rendering can currently list imported/generated jobs in `/blog/`, include them in `/sitemap.xml`, and serve `/blog/{slug}/` from saved job HTML. For imported blogs this should be treated as preview/mirror behavior until canonical/noindex or publish-back-in-place rules are implemented; for Blog Core-created blogs it can be the public hosting path.
