# SEO_MEMORY.md

## Current SEO behavior

* Hosted custom-domain blogs serve `robots.txt` allowing all and pointing to `/sitemap.xml` on the current Host.
* Hosted custom-domain blogs serve `sitemap.xml` with `/blog/` plus public imported/generated `content_jobs` when jobs exist.
* If a hosted site has no public content jobs, hosted `sitemap.xml` falls back to `/blog/visual-chaos-in-ai-product-cards/`.
* Local install writes `sitemap-blog.xml` in the target root and appends that sitemap to `robots.txt` if it is not already present.
* Generated previews under `/previews/{site_id}/blog/` are for review and should not be treated as final SEO deployment.

## Content behavior

* The current sample article is placeholder content about visual chaos in product pages.
* Topic discovery produces signals and queued article ideas as `content_jobs`; draft generation exists as a job action, but automatic final publishing is not complete.
* Article ideas should use trend/discussion hooks to explain audience questions/problems and connect them to the site's offer, expertise, or editorial point of view.
* Existing blog imports preserve original URL/canonical/source metadata and captured HTML in `content_jobs.status=IMPORTED` without changing live files.
* Imported existing blogs should remain canonical on their original source URLs by default. Blog Core is the dashboard/control plane for those blogs and should publish new/updated content back into the same original locations and URL structure.
* Blogs created from scratch by Blog Core follow a different model: Blog Core can be the canonical public host/publisher for those sites.
* For local imported sites, SEO money pages can be part of the import inventory, not only `/blog/` articles. `yas.wine` includes imported `wine-countries` and `wine-regions` pages alongside multilingual blog pages.
* `airep24.com` legacy factory migration keeps SEO money-page work in Blog Core as first-class content jobs. As of 2026-07-04, AIREP24 has 4 imported live SEO money pages and 36 queued SEO money-page jobs across EN/DE/ES/FR, with intended publish paths stored in `sources_json.targetPath`.
* `yas.ooo` now has an indexable `/use-cases/` hub with canonical use-case URLs for Shopify conversion/performance recovery, AI support and sales operations, founder MVP/operator delivery, and technical advisory. The native Next content-store maps `use_case`/SEO-money-page jobs to that section rather than adding them to `/blog/`; both blog and use-case publications are included in the source sitemap.
* Discovery now routes only explicitly classified, service-aligned `seo_money_page` ideas to `/use-cases/<slug>/`; all other editorial ideas use `/blog/<slug>/`. This is enforced when jobs are queued, not inferred later from their title.
* YAS native `sitemap.xml` is dynamic. It reads Blog Core's published content store on request, so an explicit Publish action exposes the new canonical blog/use-case route without requiring a Next build.
* Georivo topic research must use broad Google Trends parent clusters as demand evidence, then transform them into original decision-led editorial angles about location context, interactive 3D, drone alternatives, remote buyers, and geospatial trust. Do not present low-volume exact phrases as statistically reliable trends or copy raw queries into titles.
* Georivo multilingual SEO uses EN at `/blog/` and DE/ES/FR/RU at `/{language}/blog/`. Every generated variant has its own canonical URL; article pages expose hreflang only for translations that actually exist, with EN as `x-default`; the native sitemap lists each real language URL with the same alternate set.

## Known SEO gaps

* Replaced/deprecated 2026-07-03: The older statement "Dynamic article sitemap expansion is not implemented yet" is no longer true for hosted CNAME blogs. Hosted sitemap expansion now includes public imported/generated content jobs.
* Local static `/blog` install still writes the sample shell and does not yet export imported/generated content jobs as final static article pages.
* Canonical tags for hosted blog pages are not explicitly documented/implemented in memory yet.
* Hosted imported article rendering stores the original canonical/source URL in `content_jobs.published_url` and `sources_json`, but current rendering does not yet emit canonical tags from that stored URL. This matters mainly if imported content is exposed through a Blog Core-hosted preview/mirror; the preferred imported-blog model is publishing back to the original site.
* Automated custom-domain HTTPS is not implemented; this affects production SEO readiness for external CNAME sites.
* Replaced/deprecated 2026-07-24: The old statement that the discovery Google source is Google News RSS is no longer current. Product Discovery uses Google autocomplete/search-demand signals, while manual editorial research may use Google Trends as a separate relative-demand input. Blog Core still has no official Google Trends API integration.
