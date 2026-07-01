# SEO_MEMORY.md

## Current SEO behavior

* Hosted custom-domain blogs serve `robots.txt` allowing all and pointing to `/sitemap.xml` on the current Host.
* Hosted custom-domain blogs serve `sitemap.xml` with `/blog/` and the sample article URL.
* Local install writes `sitemap-blog.xml` in the target root and appends that sitemap to `robots.txt` if it is not already present.
* Generated previews under `/previews/{site_id}/blog/` are for review and should not be treated as final SEO deployment.

## Content behavior

* The current sample article is placeholder content about visual chaos in product pages.
* Topic discovery produces signals and queued article ideas; it does not yet publish full articles automatically.
* Article ideas should use trend/discussion hooks to explain audience questions/problems and connect them to the site's offer, expertise, or editorial point of view.

## Known SEO gaps

* Dynamic article sitemap expansion is not implemented yet.
* Canonical tags for hosted blog pages are not explicitly documented/implemented in memory yet.
* Automated custom-domain HTTPS is not implemented; this affects production SEO readiness for external CNAME sites.
* Google source is Google News RSS search, not official Google Trends API.
