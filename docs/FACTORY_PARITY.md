# FACTORY_PARITY.md

This document maps the existing `content-factory-yaswine` functionality into the universal Blog Core architecture.

## Goal

Blog Core must provide the same operational capabilities as the current YAS Wine content factory, but per connected site and without wine-only assumptions.

## Source factory capabilities to preserve

| Area | YAS Wine implementation | Blog Core target |
| --- | --- | --- |
| Article queue | `jobs` table with topic, slug, status, draft, FAQ, sources, visibility, publish URL | `content_jobs` with `site_id` and the same lifecycle fields |
| Job logs | `job_logs` table keyed by `job_id` | `content_job_logs` keyed by `job_id` and `site_id` |
| Generation modes | product, engagement, lead magnet flags | Same flags per job and per topic discovery settings |
| Article generation | Gemini text model, JSON article output, strict validation, internal links, FAQ, sources | Same contract, but prompt must use connected site context instead of wine-only rules |
| Images | Gemini image model, hero/inline images, WebP optimization | Same concept, stored under the connected site's blog media path or hosted Blog Core assets |
| Publish to site | Render HTML, canonical, OG/Twitter, FAQ/source blocks, sitemap updates, localized pages | Same SEO contract, but target is either local `root_path` install or hosted CNAME blog |
| Localization | Publish enabled locales from env/site settings | Per-site `languages` setting |
| Topic discovery | Reddit, Google Suggest, DuckDuckGo, scoring, settings, scheduled runs | Per-site topic discovery settings and runs; UI can additionally show live Google/Reddit signals |
| Autopublish | settings, runs, schedule windows, channel choices | Per-site `autopublish_settings` and `autopublish_runs` |
| Social channels | LinkedIn, Telegram, X/Twitter, Tumblr | Same channel list per site; credentials/connections must be scoped by `site_id` |
| Channel options | Include/exclude article link per channel | Same per-site options |
| Social post records | `social_posts` table | `social_posts` with `site_id` and `job_id` |
| OAuth | LinkedIn and Tumblr OAuth | OAuth callbacks must resolve site context and store credentials per site |
| GSC/sitemap | Submit sitemaps and keep sitemap XML consistent | Same per site/domain when credentials are available |

## Important adaptation rule

Do not copy the YAS Wine prompt literally into Blog Core. The YAS Wine prompt contains wine-only constraints and must be converted into a reusable prompt template with these inputs:

* site brand
* site domain/origin
* site content context
* topic strategy
* enabled languages
* context links
* selected channels
* product/engagement/lead magnet mode flags

## UX target

The Blog Core manage page should be organized as a production dashboard:

1. Topic signals and article ideas.
2. Article production queue.
3. Distribution channels and channel connection status.
4. Autopublish schedule.
5. Technical setup hidden behind settings.

The UI may be improved, but feature parity and data contracts take priority over cosmetic changes.
