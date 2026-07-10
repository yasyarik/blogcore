# PROJECT_MEMORY.md

This file is the durable memory of the project.
It must be updated after every meaningful task.

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
* Auth: No application-level auth is implemented in the MVP.
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

* `data/blog_core.sqlite3` is ignored; Git commits do not preserve connected sites/jobs/theme profiles.
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

## 9. Do not repeat

* Do not rely on local `/blog` installation for third-party sites; use CNAME hosting unless the local webroot is truly available.
* Do not delete installed target-site `/blog` files when removing a connected site from Blog Core.
* Do not commit SQLite database, generated previews, virtualenv, logs, or secrets.
* Do not treat Reddit availability as guaranteed; build and test degraded states.
* Do not assume chat context has all prior decisions; read memory first.
* Do not silently delete outdated memory. Mark replaced/deprecated and add the current version.
* Do not design imported-blog workflows as public mirrors by default. Preserve the source site's URLs and publish back in place unless the user explicitly asks for a cutover.
* Do not present raw Discovery signals as finished article topics. They are inputs for the journalist/SEO article idea generator.
* Do not let existing bad/generated content grant permission for future generic review/tutorial/listicle topics. Site editorial policy is inferred from stable site profile/settings, while existing content is used for context and duplicate checks.
