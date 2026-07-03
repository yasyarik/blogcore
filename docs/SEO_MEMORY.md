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

## Known SEO gaps

* Replaced/deprecated 2026-07-03: The older statement "Dynamic article sitemap expansion is not implemented yet" is no longer true for hosted CNAME blogs. Hosted sitemap expansion now includes public imported/generated content jobs.
* Local static `/blog` install still writes the sample shell and does not yet export imported/generated content jobs as final static article pages.
* Canonical tags for hosted blog pages are not explicitly documented/implemented in memory yet.
* Hosted imported article rendering stores the original canonical/source URL in `content_jobs.published_url` and `sources_json`, but current rendering does not yet emit canonical tags from that stored URL. This matters mainly if imported content is exposed through a Blog Core-hosted preview/mirror; the preferred imported-blog model is publishing back to the original site.
* Automated custom-domain HTTPS is not implemented; this affects production SEO readiness for external CNAME sites.
* Google source is Google News RSS search, not official Google Trends API.
