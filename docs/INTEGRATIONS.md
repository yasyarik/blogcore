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

* Google signals use Google News RSS search with query derived from site context/profile and `when:{days}d`; this is a topic/news signal source, not the official Google Trends API.
* Google signal results are deduplicated, relevance-scored against the site topic seed, and only positive-score items are returned.
* Reddit signals use Reddit search RSS with `sort=top` and time range mapping. Only `/comments/` discussion URLs with a strong site-topic anchor and contextual title match are returned; broad matches on generic words are rejected.
* Reddit may rate-limit with `429 Too Many Requests`; source failures are returned as API `warnings` and must not render as selectable cards.
* The topic signal API returns `counts` and `warnings` separately from `signals`; UI should show warnings as notes only.

## Jobs

* `publish_jobs` stores queued/completed/failed jobs.
* Current job kinds include `install-blog`, `topic-plan`, and `article-ideas`.
* `article-ideas` stores selected signals and generated idea drafts as JSON in `message`.

## YAS Wine factory parity target

Blog Core is being adapted toward feature parity with `/var/www/content-factory-yaswine`:

* Article production queue is stored in `content_jobs` with per-site status, draft, FAQ, sources, and social publish fields.
* Job logs are stored in `content_job_logs`.
* Distribution settings are per site in `autopublish_settings` and `topic_discovery_settings`.
* Social channel connections must be stored per site in `social_connections`; do not use one global OAuth state for all sites.
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
