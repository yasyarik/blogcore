# BUSINESS_CONTEXT.md

## Product

Blog Core is a universal blog/content factory layer. It connects existing websites, scans their public design, and creates a matching blog area without requiring a rebuild of the original website.

## Audience

* Operators managing many sites/content factories.
* Site owners who need SEO/blog content but do not want to modify their main stack deeply.
* External sites that can add a CNAME but cannot provide direct filesystem or CMS access.

## Current value proposition

* Connect any public site by URL.
* Scan and reuse its visual structure.
* Preview a matching blog shell.
* Publish locally for VPS-hosted sites or host via CNAME for external sites.
* Discover trend/discussion signals and queue article ideas per site.

## Durable product rules

* CNAME hosting is the preferred path for arbitrary external sites.
* Technical setup must not dominate the site factory page; keep it accessible through settings.
* Main factory workflow should be topic discovery, article ideas, and jobs.
* Deleting a connected site must not delete installed files from a client/root site.
