# Georivo Content Factory Plan

This plan extracts the Blog Core and content-factory scope from
`Georivo_TZ_Detailed_SEO_Content_Product_System_v1.0_RU.docx`.
Changes to the Georivo product application, landing-page design, pricing,
checkout, account area, or product UI are explicitly out of scope.

## 1. Durable scope

* Georivo remains one existing Blog Core site and native content store. Do not reconnect or import it again.
* Blog Core owns planning, generation, localization, validation, preview, approval state, publishing, and publication logs.
* The Georivo adapter owns native presentation and routes. It reuses the live site's header, footer, stylesheet, typography, and responsive behavior.
* One canonical task generates complete EN content first and then sequential DE, ES, FR, and RU localizations. Locales are child records, not separate dashboard tasks.
* The dashboard is single-user. Do not add users, roles, permissions, or RBAC. Control publication with workflow statuses, mandatory checks, explicit Publish, and audit logs.

## 2. Native content types and URLs

| Content type | Base route | Purpose |
| --- | --- | --- |
| Blog article | `/blog/{slug}/` | Editorial and trend-led authority content |
| Guide | `/guides/{slug}/` | Evergreen decision and how-to guidance |
| Template | `/templates/{slug}/` | Reusable working assets with instructions and examples |
| Example | `/examples/{slug}/` | Curated, evidence-led examples |
| Integration guide | `/embed/{slug}/` | Platform-specific embedding and validation instructions |
| Use case | `/use-cases/{slug}/` | Problem, workflow, suitability, limitations, and outcome |

Each route must also work under `/{language}/...` for configured non-default
languages. The content type and canonical target path are fixed task inputs and
must not be collapsed into Blog.

## 3. Universal factory contract

* Use lowercase ASCII slugs and one URL per primary intent.
* Give a direct answer in the first 50-80 words.
* Generate useful, non-commodity content from the complete site context, user intent, and verified source material.
* Separate verified facts, product claims, and illustrative examples.
* Include suitability, limitations, or "not for" guidance appropriate to the page type.
* Require at least four useful contextual internal links when the verified URL inventory supports them.
* Add author/reviewer labels, created/updated dates, and source references as content metadata. These are trust fields, not application roles.
* Provide three curated "Recommended next" links selected by intent, not merely latest publication date.
* Preserve complete article structure, TOC, hero and inline media, table/list where useful, FAQ where useful, and native CTA placement.
* Validate every language independently for completeness, structure, links, metadata, and unsupported claims.
* Preview is always `noindex,nofollow`. Only explicitly published, approved, HTTP 200 pages enter sitemap.
* Emit self-canonical and hreflang only for variants that actually exist; EN is `x-default`.

## 4. Type-specific contracts

### Guides

* Answer a concrete decision or implementation question.
* Include prerequisites, decision criteria, limitations, and next action.
* Avoid treating Georivo as a replacement for every other property-media layer.

### Templates

* State the intended user, result, required inputs, and usage steps.
* Provide a complete usable template plus one worked example.
* Explain customization, limitations, and the relevant Georivo workflow.

### Examples

* Establish the real or illustrative context explicitly.
* Show approach, observable result, and transferable lesson.
* Do not fabricate client names, metrics, addresses, screenshots, or outcomes.

### Integration guides

* Use only current, verified platform instructions and supplied embed code.
* Include prerequisites, placement steps, validation, common failures, and rollback/removal.
* Never invent interface labels, plugin names, or code.
* Publish the `/embed/` hub only after at least three useful integration guides exist.

### Use cases

* Lead with the operational problem and decision context.
* Explain workflow, suitability, limitations, and expected outcome without unsupported ROI claims.

## 5. Initial Georivo guide cluster

### Wave 1

1. `/guides/what-is-a-3d-property-flyover/`
2. `/guides/3d-property-flyover-vs-drone-video/`
3. `/guides/which-property-listings-need-an-aerial-view/`

### Wave 2

1. `/guides/3d-property-flyover-vs-virtual-tour/`
2. `/guides/how-to-show-nearby-amenities-on-a-property-listing/`
3. `/guides/how-to-add-a-3d-map-to-a-real-estate-website/`

### Wave 3

1. `/guides/how-to-market-a-property-to-remote-buyers/`
2. `/guides/real-estate-listing-media-checklist/`

Special editorial rules:

* Drone comparisons must remain neutral and decision-led.
* Flyovers explain exterior/location context; virtual tours explain interiors.
* POI and distance claims must be verified or clearly marked hypothetical.
* The media checklist must position Georivo as complementary, not universally substitutive.
* Suitability scorecards are not legal, financial, valuation, or investment advice.

## 6. Specialized collections

* `/templates/`: property showcase, neighborhood story, and arrival guide.
* `/examples/`: four curated examples with verified or clearly illustrative context.
* `/embed/wordpress/`, `/embed/webflow/`, `/embed/wix/`, and `/embed/squarespace/`.
* Do not queue or publish these pages merely because the adapter supports them. Each requires an approved task and verified source brief.

## 7. Delivery phases

1. Native contract: preserve content type and target path, collision-safe storage, routes, locale switching, canonical, hreflang, preview, and sitemap.
2. Editorial policy: per-site terminology, CTA, verified URL map, product claims, prohibited claims, and source inventory.
3. Typed generation: type-specific schemas, prompts, validation, trust metadata, internal-link planning, and Recommended next.
4. Georivo briefs: create and review the guide, template, example, integration, and use-case briefs from the approved clusters.
5. Publication QA: desktop/mobile visual checks, links, assets, structured data, status codes, indexability, sitemap, and Search Console submission.
6. Measurement: query/page tracking, refresh candidates, stale-source checks, and non-destructive content updates.

## 8. Acceptance criteria

* Existing `/blog/` URLs and all current locales remain unchanged.
* Identical slugs may coexist in different content types without record or route collision.
* Language switching stays on the same content type and slug.
* Empty collection hubs are `noindex` and absent from sitemap.
* Published hubs and pages have correct canonical/hreflang and appear in sitemap.
* Preview never becomes indexable or public by generation alone.
* No change is made to the product site's native routes or design outside the adapter proxy paths.
