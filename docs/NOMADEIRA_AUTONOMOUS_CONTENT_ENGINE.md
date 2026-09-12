# NOMADeira autonomous content engine — Blog Core implementation contract

Updated: 2026-08-29
Machine contract: `GET https://nomadeira.com/api/blog-core/content-engine`

## Blog Core ownership boundary

Implement the engine as a generic, site-scoped Blog Core subsystem. The database tables, scheduler, source adapters, claim validator, candidate scorer, hook validator, package schema and review UI must work for future sites without naming Madeira. NOMADeira is the first site profile: its source registry, knowledge families, scoring weights, locales, risk policy and channel targets come from the versioned NOMADeira contract. Do not add `if domain == "nomadeira.com"` branches to the shared engine.

The current generic `social_operation_settings` path is not this implementation: it replenishes X/Threads/Reddit from search/discussion signals and already published articles. Preserve it for its existing sites, but do not route NOMADeira through it until it accepts verified knowledge claims, Madeira-native entity/relationship candidates and the expanded channel package contract below.

## 1. Outcome

Blog Core must maintain a continuously replenished, source-backed Madeira knowledge graph and turn it into:

- complete multilingual articles for NOMADeira;
- Instagram Reels, carousels and Stories;
- TikTok videos and photo carousels;
- YouTube Shorts;
- X posts, threads and polls;
- Threads posts;
- Pinterest pins and carousels;
- Facebook and LinkedIn posts where the subject fits.

This is not a calendar filled with generic topics. It is a production system:

`official Madeira sources → claims → entities and relationships → story candidates → hooks → channel packages → review queue → publication → performance learning → new candidates`

The system is autonomous in research, change detection, graph growth, scoring, deduplication, briefing, drafting and queue replenishment. Public publication remains separately gated by risk and channel policy.

## 2. Product rule

Every idea must start with Madeira itself:

`Madeira entity × verified fact × relationship × angle × native format × locale`

An entity can be a place, species, person, event, object, law, tax, provider, product, activity, piece of infrastructure or ordinary routine. Trends may change the edit, sound or format, but they must not choose the subject.

Reject an idea when the same script still works after replacing Madeira with another destination.

## 3. Required persistent model

Implement these records in Blog Core's database. Names may follow the existing code style, but the meanings must remain intact.

### `knowledge_sources`

- `id`, `site_id`, `owner`, `url`, `source_class`;
- knowledge families and retrieval adapter;
- polling cadence, robots/terms state and media-rights policy;
- `etag`, `last_modified`, body hash, last success/error/change dates;
- active/paused state and priority.

### `knowledge_entities`

- stable entity ID, type, canonical name and aliases;
- localized names;
- coordinates or administrative area where relevant;
- parent and related entities;
- first/last verified dates.

### `knowledge_claims`

- one atomic claim, never an article paragraph;
- entity ID and source IDs/URLs;
- exact supporting excerpt kept privately for audit;
- `checked_at`, `valid_from`, `valid_until`, precision and confidence;
- freshness class: `live`, `volatile`, `annual` or `durable`;
- risk class, visual-rights state and approved locales;
- for tax/legal/medical/safety: year/effective date, scope, conditions, exceptions, legal citation and reviewer.

### `knowledge_edges`

- source and target entity/claim IDs;
- relationship type;
- supporting claim IDs;
- verification and confidence state.

### `content_candidates`

- entity, claim and relationship IDs;
- native angle and audience state;
- hook family, proposed payoff and visual mechanism;
- score breakdown;
- novelty fingerprint;
- rejection reason or workflow state.

### `content_briefs`

- approved factual spine and prohibited overclaims;
- hook, open loop and payoff with claim IDs;
- channel, format, locale and CTA intent;
- script/slides/shot list;
- media and rights plan;
- canonical destination decision;
- expiry and review requirements.

### `content_packages`

- final channel-native copy and assets;
- source disclosure and commercial disclosure;
- alt text, destination URL and scheduled date;
- validation report, approval state, remote publication ID and metrics.

### `content_performance`

- 24-hour, 7-day and 28-day observations;
- reach, completion, shares, saves, meaningful comments, clicks and downstream tool starts;
- the exact entity/claim/angle/hook/format fingerprint that produced the result.

## 4. Source ingestion

Start with the source families in `docs/SOCIAL_CONTENT_ENGINE.md`. The first graph target is 1,000 high-quality nodes, not indiscriminate crawling.

Supported collectors:

1. official JSON/API;
2. RSS or Atom;
3. XML sitemap plus respectful page fetch;
4. official HTML page change monitoring;
5. manually supplied law, report, archive or primary document.

Every fetch must:

- identify itself honestly;
- obey robots, rate limits and source terms;
- store retrieval time and content hash;
- skip unchanged bodies;
- never bypass authentication, paywalls or technical controls;
- keep media rights separate from factual citation rights.

Search Console, user questions, Google Trends and platform trend tools are demand or packaging signals. They do not become factual sources.

## 5. Extraction and verification

The extractor receives one changed source document and returns atomic claim proposals. It must not write posts.

### Extractor instruction

```text
You are the NOMADeira evidence extractor. Use only the supplied source document.
Return atomic claims about named Madeira entities. For every claim preserve the
exact scope, date/year, units, uncertainty, conditions and exceptions. Separate
stable facts from live status, prices, schedules and availability. Do not infer
causality, popularity, safety, eligibility or a recommendation unless the source
explicitly establishes it. Return source offsets/excerpts for private audit and
suggest entity relationships only when the same evidence supports them.
```

Verification rules:

- primary/official evidence wins;
- a provider source can prove its own package terms, not independent superiority;
- a tourism promotion page cannot prove an absolute claim;
- comparison claims require comparable measures and dates;
- mutable claims receive an expiry;
- conflicting sources remain visibly conflicted and cannot enter automatic drafting;
- generated imagery never verifies a claim.

## 6. Self-replenishment loop

Run the following jobs:

### Daily

1. poll sources due for change detection;
2. extract only new/changed material;
3. expire live and volatile claims;
4. build candidates from new claims, changed claims and unused graph relationships;
5. fill category/format/language queue deficits;
6. generate and validate briefs until each configured queue target is met;
7. create low-risk drafts and send gated subjects to approval.

### Weekly

- discover new official Madeira sources and entities;
- audit graph coverage across the nine knowledge families;
- find questions Search Console/site search/users ask but current pages do not answer;
- inspect successful nodes for unused factual relationships;
- merge aliases and near-duplicate entities;
- refresh source and media-rights policies.

### Monthly

- audit annual/tax/legal claims and upcoming effective dates;
- review category balance and stale canonical pages;
- retire failed format patterns without deleting their history;
- update weights from 28-day performance.

The scheduler must be idempotent. A source URL/body hash, claim fingerprint, candidate fingerprint and package fingerprint must each be unique within their scope.

## 7. Candidate generation

For each verified node, generate only angles supported by its relationships:

1. what it is;
2. why it is here;
3. how it works;
4. what changed;
5. where it can be seen;
6. what it changes for residents or visitors;
7. what it costs or requires;
8. what people misunderstand;
9. what unexpected person/place/law/object it connects to;
10. recognition or guessing game;
11. a valid comparison using the same measure;
12. what happens next.

Score candidates from 0 to 100 using surprise, Madeira uniqueness, visual strength, story depth, usefulness, source quality, expandability and freshness. The machine contract supplies the weights. A candidate below 72 is not briefed.

Maintain inventory quotas so one easy category cannot crowd out the rest. A sensible first weekly mix is:

- 20% nature/geology/biodiversity;
- 15% history/archive/people;
- 15% culture/food/traditions;
- 10% engineering/infrastructure;
- 15% practical life/providers/areas;
- 10% tax/law/administration;
- 10% activities;
- 5% timely statistics/events.

This is a diversity guard, not a rigid publishing calendar.

## 8. Hook engine

Hooks are generated from the factual tension after verification. Each hook object must contain:

- `hook`;
- `promise`;
- `openLoop`;
- `payoff`;
- `payoffClaimIds`;
- `risk`;
- two rejected, weaker alternatives and why they were rejected.

### Hook families

- hidden mechanism: “This forest is also part of Madeira's water system.”
- impossible contrast: “Why are marine fossils hundreds of metres above the ocean?”
- number with consequence;
- time travel;
- map reveal;
- myth with the omitted condition restored;
- archive-object mystery;
- before/after;
- name or local-word origin;
- “why does this exist?”;
- “what changes if...?”;
- a practical decision test.

### Hook validator

Reject when:

- the payoff does not fully answer the promise;
- the hook needs a superlative the sources do not support;
- urgency or scarcity is invented;
- a tax/legal/health condition was removed for drama;
- fear is used without a concrete, source-backed action;
- it is a generic destination hook with “Madeira” inserted.

## 9. Brief-generation instruction

```text
Create one NOMADeira content brief from the approved entity, claims and graph
relationships only. The first seconds/lines must open a real factual tension.
Delay the answer just long enough to create curiosity, then pay it off completely.
Choose one audience state and one useful consequence. Cite claim IDs beside every
factual beat. Do not invent a resident quote, current scene, provider result,
availability, safety outcome or visual evidence. If the subject needs more context
than the format can hold, route the complete answer to an existing canonical guide
or propose one full article; never create a thin page for the social post.
```

The brief must explain why someone would share or save it. “Interesting” is not an answer; name the social value: surprise, identity, utility, debate, recognition, planning or showing another person something hard to believe.

## 10. Blog decision and output

A social candidate does not automatically get its own URL.

Create or refresh a canonical article only when:

- there is durable search/decision intent;
- a full answer is materially more useful than the social version;
- enough evidence exists for a complete page;
- the intent is not already satisfied by another canonical page.

Otherwise link to the closest relevant guide/tool or use no link.

Before creating a Blog Core task, fetch:

- `/api/blog-core/i18n-manifest` for real routes/locales;
- `/api/blog-core/editorial-plan` for queued canonical work;
- `/api/blog-core/content-engine` for this contract.

Blog output must preserve the existing native NOMADeira JSON contract and publish EN, DE, UK and RU together. Required page quality:

- unique title, meta description, H1 and direct answer;
- useful complete body, not a padded rewrite of a Reel;
- claim-level source list and fact-check date;
- four to six non-repeating contextual internal links when genuinely relevant;
- appropriate tables/callouts/media using existing site classes;
- canonical/hreflang integrity;
- noindex preview, explicit publication and live visual QA.

## 11. Channel adapters

One approved factual spine is adapted, not copied unchanged.

| Channel | Native package |
|---|---|
| Instagram Reel | 20–35 s script, first-frame hook, scene/shot plan, on-screen text, one caption, alt text, cover and 9:16 media brief. |
| Instagram carousel | 6–9 slides: hook, progressive evidence, payoff, useful close; one caption; 4:5 media. |
| Stories | 3–6 frames with poll/quiz/question only when the answer is grounded. |
| TikTok | Faster spoken/visual rhythm, native first-person delivery without invented experience, 9:16. |
| YouTube Short | Search-readable title, tight explanatory script, complete payoff, optional full-guide destination. |
| X | One claim-led post, 3–6-part thread or evidence-backed poll; sources linked in the least disruptive valid way. |
| Threads | Conversational tension or question, no corporate-summary tone, one idea per post. |
| Pinterest | 2:3 visual, search-readable title/description, evergreen destination, explicit alt text. |
| Facebook | Standalone context, useful image/album, discussion question only when genuine. |
| LinkedIn | Infrastructure, economy, remote work, regulation or business mechanism; no forced lifestyle trivia. |

All packages store claim IDs, expiry, rights state and the exact canonical destination.

## 12. Localization

- The claim set is shared and immutable across languages.
- English is the broad-reach social master.
- German, Ukrainian and Russian are transcreated after the concept proves useful or when a local audience need justifies it.
- Do not translate idioms, hooks and calls to action literally.
- Never change numbers, dates, scope, conditions, disclosures or source meaning.
- A long-form publication is incomplete until all four NOMADeira locales exist in one operation.

## 13. Media production

Media priority:

1. owned photo/video;
2. licensed/allowed primary-source material with required attribution;
3. Gemini-generated explanatory media.

Gemini output must include the intended entity, visual mechanism, aspect ratio, safe text zone and exclusions. Store the prompt, model, date and rights state. Generated media may illustrate volcanic formation, a map mechanism or historical atmosphere, but it cannot pose as a current closure, exact tour vehicle, real resident, archive photo or provider evidence.

## 14. Risk and approval

### Autonomous through draft

- durable low-risk history, geology, culture and mechanisms;
- source ingestion, graph links, scoring, deduplication and localization drafts;
- queue replenishment and performance analysis.

### Mandatory human approval

- tax, law, immigration, medical, safety and emergency topics;
- prices, schedules, trail status, weather, live events and availability;
- “best”, comparative or eligibility conclusions;
- providers, affiliates, sponsorship and commercial claims;
- archive/licensed media whose use has not been pre-cleared.

### Never automate

- invented testimonials or documentary scenes;
- personal-data enrichment;
- hidden advertising;
- mass replies, fake engagement or community manipulation;
- bypassing platform or source restrictions.

## 15. Learning loop

Measure at 24 hours, 7 days and 28 days. Optimise primarily for:

- share rate;
- save rate;
- qualified comment rate;
- completion/retention;
- click rate to the exact relevant destination;
- tool starts and assisted conversions.

The learner may change category, angle, hook family, format, language priority and publication time weights. It must never relax evidence, rights, risk, disclosure or canonical rules.

Use exploration so the engine does not only repeat yesterday's winner: reserve roughly 20% of briefs for high-quality under-tested entities or formats.

## 16. Queue targets and state machine

Recommended initial review-ready inventory:

- 14 Instagram packages;
- 14 TikTok packages;
- 7 YouTube Shorts;
- 14 X packages;
- 14 Threads packages;
- 21 Pinterest packages;
- 7 Facebook packages;
- 4 LinkedIn packages;
- 4 complete or refreshed multilingual blog tasks.

These are queue targets, not mandatory weekly publication counts. The engine replenishes only what falls below target.

State machine:

`DISCOVERED → EXTRACTED → VERIFIED → CANDIDATE → BRIEFED → DRAFTED → MEDIA_READY → AWAITING_APPROVAL → APPROVED → SCHEDULED → PUBLISHED → MEASURED`

Side states: `REFRESH_DUE`, `REJECTED`, `ARCHIVED`, `ERROR`.

## 17. Rollout order

### Phase 1 — graph and auditability

- create tables and source registry;
- seed NOMADeira site configuration;
- ingest the first 200 official entities/claims;
- expose source, claim and candidate review screens;
- no public publishing.

### Phase 2 — autonomous ideas and drafts

- daily change detection and candidate generation;
- hook/brief validators;
- Instagram, TikTok, X, Threads and Pinterest packages;
- Gemini media jobs only after a brief passes rights/risk gates.

### Phase 3 — blog bridge and localization

- canonical-route decision;
- EN/DE/UK/RU article task creation;
- native NOMADeira previews and visual QA;
- Search Console and site-question gap input.

### Phase 4 — distribution and learning

- channel adapters with explicit credentials and approval rules;
- schedule and publication receipts;
- 24 h / 7 d / 28 d metrics;
- controlled weight updates and refresh queue.

## 18. Acceptance criteria

The system is not complete until all of these are demonstrated on NOMADeira:

1. A changed official Madeira page creates versioned claim records without duplicating unchanged claims.
2. One claim expands into several genuinely different, source-backed story candidates.
3. The candidate screen shows entity, source, claim, relationship, score, hook promise and payoff.
4. A weak/generic Madeira-substitution idea is rejected automatically.
5. A stale price or live status cannot reach drafting.
6. A tax/legal candidate cannot pass without scope/year/conditions and approval.
7. At least five channel adapters produce visibly different native packages from one factual spine.
8. Blog creation checks existing canonical intent before it creates a task.
9. One article task produces EN/DE/UK/RU together and previews in the native NOMADeira layout.
10. Generated media is traceable and never presented as evidence.
11. Queue targets replenish idempotently after drafts are approved/rejected/published.
12. Performance data changes creative weights but cannot change trust rules.

## 19. Definition of “autonomous”

Autonomous means the system keeps researching, expanding, refreshing and preparing high-quality work without waiting for someone to invent topics. It does not mean uncontrolled publishing, unsupported claims or automatic participation in communities. The system should always have a fresh, auditable queue of Madeira-native work ready for the allowed next action.
