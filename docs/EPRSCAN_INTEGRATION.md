# EPR Scan ↔ Blog Core integration

## Scope

* Production site: `https://eprscan.eu` (`/var/www/eprscan` on the VPS).
* Blog Core site: `id=20`, `access_type=native_content_store`, manual publication.
* Locales: English canonical at root, plus German `/de`, French `/fr`, and Spanish `/es`. Russian and Italian are intentionally excluded.
* Blog Core owns editorial records for `/blog/{slug}`. EPR Scan owns rendering, routes, native design, metadata, JSON-LD, language navigation and sitemap output.
* Existing PPWR, country, marketplace, checker, privacy, terms and account routes remain source-authoritative; Blog Core must not replace them.

## Publication contract

EPR Scan uses the site capability marker `publication_contract:reviewed_multilingual_compliance`. Blog Core blocks a blog publication unless it has complete EN/DE/FR/ES variants; a named author and real reviewer; `lastReviewedAt`, `rulesetVersion`, and a dated change log; 2–5 official HTTPS sources with exact public support/legal-point notes; and explicit editorial, product-fact and SEO approvals.

The EPR Scan prebuild independently repeats the locale/evidence checks and rejects executable HTML. Recommendations are never compiled, and drafts may be compiled only into the private `noindex` review surface described below; neither can enter public article routes. This is intentionally stricter than ordinary legacy-compatible Blog Core articles.

## English draft approval contract

Before localization or publication, Blog Core may hand off one English source draft to EPR Scan's native review route `/content-preview/{jobId}`. The preview is explicitly labelled unpublished, uses `noindex` and no-store, and is omitted from the sitemap. It does not satisfy or bypass the publication contract.

The current workflow is: generate English, obtain explicit visual/editorial approval, then translate that accepted source in one batch to German, French and Spanish. Do not create Russian or Italian variants. The first draft under this contract is `When does the PPWR apply to ecommerce sellers?` (`5c9fda97f3ca8c064871e6a6`); it has no translations and remains unpublished.

EPR Scan owns the presentation of semantic article HTML. Contents, figures, data tables, workflows, quotes, recommended links and FAQs use native responsive components. Mobile table labels are derived from the localized table headers, so future DE/FR/ES articles do not inherit English-only UI labels. Empty review metadata is omitted from draft previews rather than displayed as `Pending`; published articles still require every real review field through the strict publication contract.

Declared `internalLinks` are also a presentation contract: EPR Scan identifies the matching in-body link paragraph and renders it as a visible contextual-reading card beside the relevant section. Matching removes only a supported locale prefix for comparison and preserves the localized paragraph and anchor copy. A one-item `recommendedNext` action uses a compact CTA layout. Acceptance requires every contextual and CTA destination to return HTTP 200.

## Runtime handoff

Blog Core writes approval drafts to `/var/www/eprscan/data/blog-core/drafts` and explicit publications to `/var/www/eprscan/data/blog-core/published`. The enabled `eprscan-blog-core-content.path` systemd unit watches both stores, invokes the appropriate fail-closed sync validation, runs the TypeScript check and production build, then restarts only the existing `eprscan` PM2 process. Draft media is imported into EPR Scan-owned `/images/blog-core/{jobId}/` paths so it remains compatible with the native image CSP.

```bash
systemctl status eprscan-blog-core-content.path
journalctl -u eprscan-blog-core-content.service
cd /var/www/eprscan
RELEASE_BASE_URL=https://eprscan.eu node scripts/check-blog-core-integration.mjs
npm run translations:check
```

`eprscan-seo-crawl.timer` runs the same production checks every Monday at 06:15 UTC with up to 30 minutes of randomized delay. It also crawls every current sitemap URL and all discovered internal targets, so future approved Blog Core articles enter the check automatically. The last compact result is `/var/lib/eprscan/seo-crawl/last.json`, append-only run history is `/var/lib/eprscan/seo-crawl/history.ndjson`, and full output is in `journalctl -u eprscan-seo-crawl.service`. A failed crawl leaves the oneshot unit failed and records `status=failed`; it never publishes or changes site content.

## SEO/content rollout

The first content wave should remain narrow and evidence-led: PPWR timelines and transition questions, seller/importer/representative roles, marketplace and fulfilment scenarios, and reviewed Germany/France/Poland workflows. Each legal page needs a direct answer, role and sales-flow distinctions, an actionable checklist, concrete examples, known gaps, and exact primary sources. Do not mass-produce EU-country templates or publish until the real reviewer has approved the content and translations.

Google Search Console/Bing ownership and sitemap submission are external provider gates. Public robots/sitemap and HTML verification are not proof of a successful property connection; record provider evidence separately when the site owner grants access.

As of 2026-09-02, `sc-domain:eprscan.eu` is saved in Blog Core but disabled with `no_access` after a real permission check. Grant the Blog Core service account reported by the Setup panel access to that exact domain property, then use **Verify access** and collect finalized data. Bing Webmaster Tools ownership/submission still requires owner-side provider access and has not been represented as complete.

The production integration checker covers 60 translated public variants, 10 populated English directory/trust routes and 16 private routes. English is indexable at root. A DE/FR/ES equivalent enters hreflang and the sitemap only after an explicit page-level language and legal approval record names both reviewers; otherwise it remains accessible with a self-canonical and `noindex`. Country pages additionally require a real public reviewer profile before they may claim reviewed/public status. RU/IT routes and alternates are forbidden. Empty blog hubs remain `noindex` until at least one valid Blog Core article exists.

The crawlable English information architecture now includes `/guides`, `/countries`, `/marketplaces`, `/tools` and the `/company` trust cluster (about, methodology, editorial policy, coverage and contact). Existing substantive pages expose visible breadcrumbs and curated related links. English-only directories do not advertise nonexistent translated routes in the language selector.

The TOR analytics names are emitted alongside the original product funnel names: `seo_landing_view`, `checker_start`, `flow_added`, `free_result_view`, `paid_report_checkout`, server-confirmed `purchase`, and server-confirmed `registration_assist_submit`. Order and assessment identifiers are hashed before first-party persistence and omitted from optional third-party analytics. `template_download` is intentionally absent until a real downloadable template exists.

The substantive TOR editorial roadmap is now materialized as 11 English draft jobs: PPWR dates and roles, small sellers, marketplace boundaries, Amazon/Etsy/Shopify/non-EU flows and the DE/FR/PL country guides. One translation batch created all 33 DE/FR/ES variants. The queue-health and reviewer-governance recommendations remain open and were not converted into articles. Every draft remains unpublished and must pass the publication contract above.

The private draft payload may contain complete DE/FR/ES localizations after English approval. EPR Scan validates and imports those variants as unpublished data but keeps `/content-preview/{jobId}` English-only for copy review. Draft localizations never create public locale routes, sitemap entries or hreflang by themselves.

Performance release validation uses three Lighthouse attempts per representative page and keeps the TOR limits unchanged: median LCP must be at most 2.5 seconds, median Performance at least 90, the lowest Accessibility/SEO score at least 90, and maximum CLS at most 0.1. Optional Web Vitals code loads during browser idle time and below-the-fold sections use intrinsic `content-visibility` containment. Lighthouse is deliberately not run inside the low-priority weekly systemd crawl because host scheduling and the external CDN path distort lab timings; the protected first-party RUM dashboard remains the field source for LCP, CLS and INP.

Remaining external gates are assignment of a named compliance reviewer with a public profile, named language reviewers for each DE/FR/ES page approval, and owner access for Google Search Console and Bing Webmaster Tools. These gates must not be represented as completed by code or AI identities.
