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
* Popular search suggestions are deduplicated, filtered for broad/non-local/non-promotional/non-navigation intent, relevance-scored against the site topic seed, and only positive-score items are returned. The selected range does not affect Google autocomplete suggestions; it only affects Reddit.
* Reddit signals use Reddit search RSS with `sort=top` and time range mapping. Only `/comments/` discussion URLs with a strong site-topic anchor and contextual title match are returned; broad matches on generic words are rejected.
* Reddit may rate-limit with `429 Too Many Requests`; source failures are returned as API `warnings` and must not render as selectable cards.
* The topic signal API returns `counts` and `warnings` separately from `signals`; UI should show warnings as notes only.
* `POST /api/sites/{site_id}/article-ideas` generates reviewable idea candidates from selected Discovery signals and returns `rejectedSimilar` for topics filtered as too similar to existing site content. It must not create `content_jobs`.
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
* Social connection tests currently use provider API probes: Telegram `getMe/getChat`, LinkedIn `userinfo`, X `/2/users/me`, and Tumblr OAuth 1.0 `user/info`.
* Social text adaptation is handled before publishing through `social_posts`. The endpoint `POST /api/sites/{site_id}/content-jobs/{job_id}/social-drafts` generates channel-specific drafts only for channels that are both selected in Distribution and configured/connected in Setup. If no active channel exists, the endpoint returns `400` and does not create drafts. When drafts are allowed, it stores `language`, `max_chars`, `char_count`, `include_link`, `validation_json`, and marks the matching `content_jobs.{channel}_status` as `drafted`.
* Social draft generation must preserve the article language. It reads `content_jobs.sources_json.language` for imported/localized pages and falls back to the first configured site language.
* Current strict social text limits: LinkedIn 3000 chars, Telegram 4096 chars, X/Twitter 280 chars, Tumblr 4096 chars. Drafts are normalized and shortened before storage if Gemini returns over-limit text, so stored `social_posts.char_count` must be `<= max_chars`.
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
