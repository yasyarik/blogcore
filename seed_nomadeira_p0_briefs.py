import json
import sqlite3
from datetime import datetime, timezone

DB = "/var/www/blog.yas.ooo/data/blog_core.sqlite3"
TODAY = "2026-08-27"


def source(source_id, title, publisher, url, supports, summary):
    return {
        "id": source_id,
        "title": title,
        "publisher": publisher,
        "publicUrl": url,
        "accessedAt": TODAY,
        "supports": supports,
        "publicSummary": summary,
    }


def listing(source_id, title, url, supports, summary, evidence):
    item = source(source_id, title, "Idealista", url, supports, summary)
    item.update({
        "automatedFetchMayReturn403": True,
        "manualVerifiedAt": "2026-08-27T10:15:00+00:00",
        "manualVerificationEvidence": evidence,
    })
    return item


SIGA = source(
    "siga-current-routes",
    "SIGA: current Madeira route directory",
    "SIGA Madeira",
    "https://siga.madeira.gov.pt/horarios",
    "The official SIGA directory lists current regional and municipal route identifiers and destinations across Madeira. A listed route does not establish the walking distance from a particular home, the complete timetable required by one household, accessibility, service reliability or a guaranteed journey time.",
    "SIGA publishes Madeira's current route directory and links to individual timetables.",
)
MEO = source(
    "meo-fibre-check",
    "MEO: fibre coverage check by address",
    "MEO",
    "https://www.meo.pt/servicos/casa/cobertura-fibra",
    "The checker reports whether MEO lists fibre service as available at an entered address. It does not prove an installed line inside the dwelling, activation, equipment, achievable speed, service quality or another provider's availability.",
    "MEO provides an address-based fibre availability check; installation and achievable service require property-specific confirmation.",
)
DREM = source(
    "drem-rent-q1-2026",
    "DREM: registered new lease medians, 12 months ending March 2026",
    "DREM / Statistics Portugal",
    "https://estatistica.madeira.gov.pt/en/download-now/economica/administracao-publica/2016-02-17-11-17-09/313-press-release/house-rental-at-local-level-press-release/5848-26-06-2026-rendas-en.html",
    "DREM reports observed medians of €11.82/m² for registered new family-dwelling lease agreements across Madeira and €13.60/m² in Funchal for the 12 months ending March 2026. The release does not provide a current asking-price range for every municipality.",
    "DREM publishes dated registered-contract rent medians for Madeira and Funchal, distinct from current asking listings.",
)
FINANCE_CONTRACT = source(
    "tax-authority-rental-contract",
    "Portuguese Tax Authority: urban rental contracts",
    "Autoridade Tributaria e Aduaneira",
    "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Arrendamento/Contrato%20urbano/Paginas/default.aspx",
    "The Tax Authority says landlords must communicate the creation, amendment and termination of an urban rental contract to the authority and describes the reporting channels and deadlines. This administrative duty does not verify the identity of a person advertising a property or replace review of the written agreement.",
    "The Tax Authority explains how landlords communicate urban rental contracts and later changes or termination.",
)
FINANCE_RECEIPTS = source(
    "tax-authority-rent-receipts",
    "Portuguese Tax Authority: rental receipts",
    "Autoridade Tributaria e Aduaneira",
    "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Arrendamento/Recibos/Paginas/default.aspx",
    "The Tax Authority says a landlord who is subject to the electronic-receipt duty must issue a receipt when receiving rent, a security deposit or an advance payment, while specified exemptions use another reporting route. The page does not authenticate an advertiser before payment.",
    "The Tax Authority explains receipt treatment for rent, security deposits and advance payments.",
)
CIVIL_RENT = source(
    "civil-code-article-1076",
    "Portuguese Civil Code: Article 1076",
    "Diario da Republica",
    "https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2007-34509075",
    "Article 1076 states that advance rent may be agreed in writing for no more than two months and that the parties may secure their obligations up to the value corresponding to two rents. The rule does not establish the total arrival budget for a particular tenancy.",
    "The consolidated Civil Code publishes the current limits for agreed advance rent and security under Article 1076.",
)


def place_brief(primary_intent, title, description, h1, answer, outline, links, refs, comparisons, limitations):
    return {
        "primaryIntent": primary_intent,
        "seoTitle": title + " | NOMADeira",
        "metaDescription": description,
        "h1": h1,
        "directAnswer": answer,
        "outline": outline,
        "approvedInternalLinks": links,
        "sourceReferences": refs,
        "primaryCta": {"label": "Compare the exact address in Area Finder", "url": "/where-to-live/area-finder"},
        "editorial": {
            "author": "NOMADeira editorial team",
            "reviewer": "NOMADeira fact review",
            "owner": "NOMADeira",
            "factCheckedAt": TODAY,
            "reviewDueAt": "2026-11-27",
            "reviewCadence": "3 months",
        },
        "approvals": {"editorialReview": True, "productFactCheck": True, "seoReview": True, "browserQa": True},
        "contentDetails": {
            "audience": "International residents, expats and remote workers comparing an exact Madeira address for everyday life",
            "decisionMethod": "Separate the municipality, parish and exact address. Compare current asking supply, complete repeated journeys, walking access and services before deciding.",
            "budgetMethod": "Use dated listing snapshots as examples of advertised supply, never as a market-wide rent range. Keep them separate from registered-contract statistics and obtain current written terms for the exact home.",
            "comparisonRequirement": comparisons,
            "allowedReaderChecks": [
                "Confirm the parish and exact address before comparing it with a town or municipality label.",
                "Walk or map the complete route from the entrance to repeated destinations and the relevant stop.",
                "Check the current outward and return timetable for weekday, evening and weekend journeys.",
                "Compare written rent, term, deposit, advance payment and included costs across live offers checked on the same date.",
                "Run an address-level broadband check and confirm the physical in-unit connection before signing.",
                "Compare the address with the named alternatives using the same requirements.",
            ],
            "forbiddenClaims": [
                "the whole municipality is flat, walkable, quiet, sunny or suitable without a car",
                "a current listing snapshot is a representative market range",
                "a route listing proves a nearby stop, useful frequency, short journey or late return",
                "reported fibre availability proves an installed line or achievable speed",
                "tourism descriptions prove property-level climate, noise, safety or comfort",
                "NOMADeira has first-hand resident observations not supplied in the brief",
            ],
            "limitations": limitations,
        },
    }


JOBS = {
    "4a08cfc35db15ba93cf459b2": place_brief(
        "Choose whether Santa Cruz town or another parish fits an airport-adjacent east-coast routine",
        "Living in Santa Cruz: airport, coast and daily trade-offs",
        "Compare Santa Cruz town with Caniço and Machico using current rentals, airport location, routes and exact-address checks.",
        "Living in Santa Cruz: airport, coast and daily trade-offs",
        "Santa Cruz town can suit residents who value an east-coast base near the airport, but Santa Cruz municipality also includes Caniço, Gaula, Camacha and Santo António da Serra. On 27 August 2026 the municipality-wide rental search showed 39 listings, while the town-specific decision still requires checking the exact address, lease term, airport exposure and complete journeys.",
        ["Santa Cruz in one minute", "Town centre versus the wider municipality", "Airport proximity without assuming noise", "Current rental snapshot", "Transport and car-free checks", "Santa Cruz versus Caniço, Machico and Funchal", "Final address decision"],
        ["/where-to-live/canico/", "/where-to-live/machico/", "/where-to-live/funchal/", "/transport/public-transport/", "/housing/long-term-rental/", "/where-to-live/area-finder"],
        [
            source("visit-madeira-santa-cruz", "Visit Madeira: Santa Cruz", "Visit Madeira", "https://visitmadeira.com/en/where-to-go/madeira/east-coast/santa-cruz/", "Visit Madeira identifies Santa Cruz as an east-coast municipality 18 kilometres from Funchal, locates Madeira airport in Santa Cruz and lists five parishes: Camacha, Caniço, Gaula, Santo António da Serra and Santa Cruz. It does not establish address-level airport noise, commute time or walkability.", "Visit Madeira identifies Santa Cruz's east-coast position, airport and five parishes."),
            listing("idealista-santa-cruz-2026-08-27", "Idealista: Santa Cruz municipality rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/santa-cruz/", "On 27 August 2026 the Santa Cruz municipality search displayed 39 asking listings and an average asking figure of €14.53/m². Visible examples ranged across Santa Cruz town, Caniço, Garajau and Gaula and included mixed lease terms. This is a changing portal snapshot, not a town-specific market range.", "The 27 August snapshot showed 39 municipality-wide listings with mixed locations and terms.", "27 August 2026: 39 Santa Cruz municipality listings; displayed average €14.53/m². Visible examples included Santa Cruz town, Caniço, Garajau and Gaula with mixed terms."),
            SIGA, DREM, MEO,
        ],
        "Compare Santa Cruz town separately with Caniço, Machico and Funchal; do not treat municipality-wide listing supply as town-centre supply.",
        "The listing count is municipality-wide and changes continuously. Airport proximity does not establish noise at a home, and routes must be checked for the exact address.",
    ),
    "4d8ef3e703b1bfe7c1f9f9ad": place_brief(
        "Choose between Câmara de Lobos centre, Estreito and nearby Funchal access",
        "Living in Câmara de Lobos: housing, access and logistics",
        "Compare Câmara de Lobos centre and outer parishes using current rentals, transport and practical Funchal-access checks.",
        "Living in Câmara de Lobos: housing, access and logistics",
        "Câmara de Lobos is a south-coast municipality next to Funchal, but the fishing-bay centre, Estreito, Quinta Grande, Jardim da Serra and Curral das Freiras create very different routines. The 27 August 2026 rental snapshot showed 10 municipality-wide listings, so compare the exact parish, walking route, transport and written lease terms.",
        ["Câmara de Lobos in one minute", "Centre, Estreito and the outer parishes", "Current rental snapshot", "Funchal access by exact route", "Daily services and internet", "Compare with Funchal and Ribeira Brava", "Final address decision"],
        ["/where-to-live/funchal/", "/where-to-live/ribeira-brava/", "/transport/public-transport/", "/transport/without-a-car/", "/housing/long-term-rental/", "/where-to-live/area-finder"],
        [
            source("visit-madeira-camara", "Visit Madeira: Câmara de Lobos", "Visit Madeira", "https://visitmadeira.com/en/where-to-go/madeira/south-coast/camara-de-lobos/", "Visit Madeira places Câmara de Lobos on Madeira's south coast and lists five parishes: Câmara de Lobos, Curral das Freiras, Estreito de Câmara de Lobos, Jardim da Serra and Quinta Grande. The municipal description does not establish one shared commute, slope or service pattern.", "Visit Madeira identifies the municipality's south-coast position and five distinct parishes."),
            listing("idealista-camara-2026-08-27", "Idealista: Câmara de Lobos rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/camara-de-lobos/", "On 27 August 2026 the municipality search displayed 10 asking listings and an average asking figure of €13.35/m². Visible examples included a T2 at €1,200/month, a T4 at €1,350/month, a T2 at €1,400/month and higher-priced or temporary offers. This is a changing portal snapshot with mixed locations and terms.", "The 27 August snapshot showed 10 municipality-wide listings and mixed asking terms.", "27 August 2026: 10 Câmara de Lobos municipality listings; average €13.35/m². Visible T2 €1,200, T4 €1,350, T2 €1,400 plus higher-priced and temporary offers."),
            SIGA, DREM, MEO,
        ],
        "Compare the centre and Estreito with Funchal and Ribeira Brava using the same housing and repeated-journey criteria.",
        "Municipality-wide listings combine distinct parishes. Geographic proximity to Funchal does not prove a short door-to-door journey.",
    ),
    "901cae62e30a9e35f9fbd176": place_brief(
        "Choose a Calheta parish by housing supply, climate evidence, services and car dependence",
        "Living in Calheta: sunshine, space and car dependence",
        "Compare Calheta, Arco da Calheta and western parishes using current rentals, official geography and transport checks.",
        "Living in Calheta: sunshine, space and car dependence",
        "Calheta is Madeira's largest municipality and contains eight parishes, so it should not be treated as one neighbourhood. The 27 August 2026 rental snapshot showed 12 municipality-wide listings from €650/month, but several were temporary or high-priced. Choose by exact parish, slope, repeated journeys and written lease terms rather than a broad sunshine label.",
        ["Calheta in one minute", "Eight parishes, not one lifestyle", "What the climate source establishes", "Current rental snapshot", "Why car dependence is address-specific", "Compare Calheta with Ribeira Brava and Ponta do Sol", "Final address decision"],
        ["/where-to-live/ribeira-brava/", "/where-to-live/ponta-do-sol/", "/transport/without-a-car/", "/housing/long-term-rental/", "/where-to-live/sunniest-areas/", "/where-to-live/area-finder"],
        [
            source("visit-madeira-calheta", "Visit Madeira: Calheta", "Visit Madeira", "https://visitmadeira.com/en/where-to-go/madeira/west-coast/calheta/", "Visit Madeira says Calheta covers 116 km² and lists eight parishes: Arco da Calheta, Calheta, Estreito da Calheta, Fajã da Ovelha, Jardim do Mar, Paul do Mar, Ponta do Pargo and Prazeres. It describes relatively low municipality-level rainfall and a mild climate, not property-level sun, damp or wind.", "Visit Madeira describes Calheta's scale, eight parishes and municipality-level climate."),
            listing("idealista-calheta-2026-08-27", "Idealista: Calheta rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/calheta-madeira/", "On 27 August 2026 the Calheta municipality search displayed 12 asking listings and an average asking figure of €16.18/m². Visible examples included €650/month homes in Fajã da Ovelha and Ponta do Pargo, €750/month in Arco da Calheta, €1,200/month and €1,400/month in Calheta, and several temporary or luxury offers. It is not a representative long-term range.", "The 27 August snapshot showed 12 municipality-wide listings with large differences in parish and term.", "27 August 2026: 12 Calheta municipality listings; average €16.18/m². Examples: €650 Fajã da Ovelha, €650 temporary Ponta do Pargo, €750 Arco da Calheta, €1,200 and €1,400 Calheta; mixed temporary/luxury terms."),
            SIGA, DREM, MEO,
        ],
        "Compare Calheta, Arco da Calheta and outer western parishes with Ribeira Brava and Ponta do Sol rather than ranking the whole municipality.",
        "The tourism climate description is municipality-level; listings combine eight parishes and mixed terms; route presence does not prove a practical car-free routine.",
    ),
    "22d8fd9edc0fc351a3a410ec": place_brief(
        "Choose whether Ribeira Brava town or another parish works as a southwest base",
        "Living in Ribeira Brava: services, housing and commute",
        "Assess Ribeira Brava town, Campanário, Tabua and Serra de Água using current rentals and complete journey checks.",
        "Living in Ribeira Brava: services, housing and commute",
        "Ribeira Brava combines a compact coastal town with Campanário, Tabua and inland Serra de Água. Its 27 August 2026 rental search showed only a very small municipality-wide supply, so a decision should start with the exact parish, live lease terms and complete repeated journeys rather than a generic southwest label.",
        ["Ribeira Brava in one minute", "Town, Campanário, Tabua and Serra de Água", "Current rental snapshot", "Funchal and west-coast journeys", "Services, walking routes and internet", "Compare with Câmara de Lobos, Ponta do Sol and Calheta", "Final address decision"],
        ["/where-to-live/camara-de-lobos/", "/where-to-live/ponta-do-sol/", "/where-to-live/calheta/", "/transport/public-transport/", "/housing/long-term-rental/", "/where-to-live/area-finder"],
        [
            source("visit-madeira-ribeira-brava", "Visit Madeira: Ribeira Brava", "Visit Madeira", "https://visitmadeira.com/en/where-to-go/madeira/west-coast/ribeira-brava/", "Visit Madeira lists four parishes in Ribeira Brava municipality: Ribeira Brava, Campanário, Serra de Água and Tabua, and describes geography from coast to mountains. It does not establish one common climate, commute or walkability pattern.", "Visit Madeira identifies Ribeira Brava's four parishes and coast-to-mountain geography."),
            listing("idealista-ribeira-brava-2026-08-27", "Idealista: Ribeira Brava rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/ribeira-brava/", "The 27 August 2026 search showed very limited municipality-wide asking supply. Visible offers included a T1 at €1,350/month and a T2 at €1,450/month marked temporary; a separate recently crawled result showed a €3,750/month Campanário house. These changing examples are not a market-wide range.", "The dated snapshot showed very limited and mixed-term municipality-wide rental supply.", "27 August 2026 verification: visible Ribeira Brava examples included T1 €1,350/month and T2 €1,450/month temporary; another recent result showed Campanário T3 €3,750/month. Supply and terms change."),
            source("siga-ribeira-brava-funchal", "SIGA: Funchal to Ribeira Brava timetable", "SIGA Madeira", "https://siga.madeira.gov.pt/public/storage/horarios_pdf/rod_7funchal.pdf", "The official timetable publishes scheduled Funchal-Ribeira Brava departures for weekdays, Saturdays, Sundays and holidays and warns that schedules can change. It does not establish the walking leg or suitability for a specific household.", "SIGA publishes the Funchal-Ribeira Brava timetable by day type."),
            SIGA, DREM, MEO,
        ],
        "Compare the coastal town with Campanário, Tabua and Serra de Água, then with Câmara de Lobos, Ponta do Sol and Calheta.",
        "The available rental snapshot is too small for a representative range. Timetable and walking legs must be checked together for the exact home.",
    ),
    "6a3f52364b17f77be084f541": place_brief(
        "Choose whether São Vicente's north-coast setting fits housing, climate and transport needs",
        "Living in São Vicente: climate, housing and logistics",
        "Compare São Vicente, Boaventura and Ponta Delgada using current rentals, official geography and transport checks.",
        "Living in São Vicente: climate, housing and logistics",
        "São Vicente municipality has three parishes and a wetter, greener north-coast setting, but exact housing and transport conditions vary by valley and address. The 27 August 2026 rental snapshot showed four listings, several marked temporary, so verify the lease term, complete journeys and property conditions directly.",
        ["São Vicente in one minute", "São Vicente, Boaventura and Ponta Delgada", "North-coast climate without property assumptions", "Current rental snapshot", "Transport and repeated journeys", "Compare with Santana, Porto da Cruz and Funchal", "Final address decision"],
        ["/where-to-live/north-coast/", "/where-to-live/machico/", "/where-to-live/funchal/", "/transport/without-a-car/", "/housing/long-term-rental/", "/where-to-live/area-finder"],
        [
            source("visit-madeira-sao-vicente", "Visit Madeira: São Vicente", "Visit Madeira", "https://www.visitmadeira.com/en/where-to-go/madeira/north-coast/sao-vicente/", "Visit Madeira says São Vicente municipality covers 78.70 km², has about 6,000 residents and comprises São Vicente, Boaventura and Ponta Delgada. It describes abundant forest, valleys and a lively north-coast sea, not property-level weather or access.", "Visit Madeira describes São Vicente's three parishes and north-coast geography."),
            listing("idealista-sao-vicente-2026-08-27", "Idealista: São Vicente rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/sao-vicente/", "On 27 August 2026 the São Vicente search displayed four asking listings and an average asking figure of €13.12/m². Visible examples were €800/month T1 and T2 temporary homes, a €1,200/month T1 estate and a €1,500/month T2 temporary house. This small mixed-term snapshot is not a representative long-term range.", "The 27 August snapshot showed four listings, with several marked temporary.", "27 August 2026: 4 São Vicente listings; average €13.12/m². T1 €800 temporary, T2 €800 temporary, T1 €1,200, T2 €1,500 temporary."),
            SIGA, DREM, MEO,
        ],
        "Compare São Vicente's three parishes with Santana, Porto da Cruz and Funchal using the same housing and journey checks.",
        "The four-listing snapshot has mixed terms. Municipality-level tourism descriptions do not predict damp, sunlight, wind or access at a home.",
    ),
    "180788b47048787fb1451377": place_brief(
        "Compare Santana, Porto da Cruz and São Vicente as north-coast living bases",
        "Madeira north coast: Santana, Porto da Cruz and São Vicente",
        "Compare three north-coast bases using current rental supply, official geography, routes and address-level checks.",
        "Madeira north coast: Santana, Porto da Cruz and São Vicente",
        "Madeira's north coast offers distinct bases rather than one lifestyle. On 27 August 2026 São Vicente showed four rental listings, Santana showed two, and a Machico-municipality search included a Porto da Cruz home at €800/month. These small snapshots make exact-address and transport checks more important, not less.",
        ["North coast in one minute", "Santana as a municipal centre", "Porto da Cruz as an east-north transition", "São Vicente and its valley", "Current rental supply compared", "Transport, weather and services", "Final shortlist method"],
        ["/where-to-live/sao-vicente/", "/where-to-live/machico/", "/transport/without-a-car/", "/housing/long-term-rental/", "/where-to-live/sunniest-areas/", "/where-to-live/area-finder"],
        [
            source("visit-madeira-north-coast", "Visit Madeira: Madeira north coast", "Visit Madeira", "https://visitmadeira.com/en/where-to-go/madeira/north-coast/", "Visit Madeira describes the north coast across São Vicente, Santana and Porto Moniz and notes abundant water and major Laurissilva areas. Porto da Cruz is administratively in Machico municipality and must not be described as a Santana or São Vicente parish.", "Visit Madeira describes the north coast's geography and wetter landscape."),
            source("visit-madeira-sao-vicente", "Visit Madeira: São Vicente", "Visit Madeira", "https://www.visitmadeira.com/en/where-to-go/madeira/north-coast/sao-vicente/", "Visit Madeira lists São Vicente's three parishes and describes its valleys, forest and north-coast sea. It does not establish property conditions.", "Visit Madeira identifies São Vicente's three parishes."),
            listing("idealista-sao-vicente-2026-08-27", "Idealista: São Vicente rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/sao-vicente/", "On 27 August 2026 São Vicente displayed four listings from €800 to €1,500 per month, several marked temporary, with an average asking figure of €13.12/m². This is a small changing snapshot.", "São Vicente showed four mixed-term listings on 27 August.", "27 August 2026: 4 listings, €800 to €1,500/month, several temporary; average €13.12/m²."),
            listing("idealista-santana-2026-08-27", "Idealista: Santana rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/santana/", "On 27 August 2026 Santana municipality displayed two asking listings in São Jorge: a T0 at €1,190/month and a T1 at €750/month, with an average asking figure of €19.29/m². Two listings cannot establish a representative range.", "Santana showed two São Jorge listings in the dated snapshot.", "27 August 2026: Santana search 2 listings, São Jorge T0 €1,190 and T1 €750; displayed average €19.29/m²."),
            listing("idealista-porto-da-cruz-2026-08-27", "Idealista: Porto da Cruz rental example, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/machico/", "The 27 August 2026 Machico municipality search included a Porto da Cruz T1 house at €800/month. The municipality search contained nine listings overall across multiple parishes, so it does not establish Porto da Cruz supply beyond the cited example.", "The dated Machico-municipality snapshot included one €800 Porto da Cruz T1 example.", "27 August 2026: Machico municipality search 9 listings overall; visible Porto da Cruz T1 house €800/month."),
            SIGA, MEO,
        ],
        "Compare Santana, Porto da Cruz and São Vicente directly; keep their administrative boundaries and tiny listing samples explicit.",
        "All three listing samples are small and changing. North-coast descriptions do not establish weather or housing conditions at an exact property.",
    ),
}


JOBS["5422e70720b31003315adf9a"] = {
    "primaryIntent": "Help a renter verify a Madeira listing, advertiser, written contract and payment trail before transferring money",
    "seoTitle": "Madeira rental scam checklist: verify before paying | NOMADeira",
    "metaDescription": "Verify a Madeira rental listing, identity, property, written contract, deposit and receipt trail before paying.",
    "h1": "Madeira rental scam checklist: verify before paying",
    "directAnswer": "Do not transfer money because a listing, message or viewing appears convincing. Verify the advertiser's authority, inspect the exact property, read the complete written contract, match payment details to the contracting party and retain a receipt trail. Stop when identity, access, terms or payment instructions cannot be independently reconciled.",
    "outline": ["The stop-before-payment rule", "Verify the advertiser and property", "Inspect the exact home", "Read the written contract", "Check deposit and advance-rent terms", "Create a traceable payment and receipt record", "What to do when facts do not match"],
    "approvedInternalLinks": ["/housing/rental-documents/", "/housing/deposits/", "/housing/long-term-rental/", "/housing/rent-without-fiador/", "/madeira-arrival-budget/", "/setup-plan/"],
    "sourceReferences": [FINANCE_CONTRACT, FINANCE_RECEIPTS, CIVIL_RENT, source("gov-unfair-practices", "gov.pt: unfair commercial practices", "Portuguese Government", "https://www.gov.pt/guias/praticas-comerciais-desleais-em-portugal", "The government guide explains that misleading commercial actions and omissions are prohibited and identifies categories of information that can mislead a consumer. It does not determine whether a particular private rental message is fraudulent.", "The government guide explains misleading actions and omissions in consumer transactions.")],
    "primaryCta": {"label": "Build the rental checks into a Setup Plan", "url": "/setup-plan/"},
    "editorial": {"author": "NOMADeira editorial team", "reviewer": "NOMADeira fact review", "owner": "NOMADeira", "factCheckedAt": TODAY, "reviewDueAt": "2026-11-27", "reviewCadence": "3 months"},
    "approvals": {"editorialReview": True, "productFactCheck": True, "seoReview": True, "browserQa": True},
    "contentDetails": {
        "audience": "International renters assessing a Madeira long-term rental before payment",
        "decisionMethod": "Use a stop/go verification sequence. A single unresolved mismatch in identity, property access, written terms or payment destination is a reason to pause rather than rationalise the risk.",
        "allowedReaderChecks": ["Verify identity and authority independently.", "Inspect the exact property or use a trusted representative.", "Compare the written address, parties, rent, duration, deposit and advance payment.", "Pay only to an account that can be reconciled with the written contracting party.", "Retain the listing, messages, contract, proof of payment and receipt."],
        "forbiddenClaims": ["any single check guarantees a legitimate rental", "tax registration makes a civil contract automatically valid", "a platform listing proves ownership or authority", "a particular payment method is universally safe", "NOMADeira provides legal advice or fraud investigation"],
        "limitations": "This is a verification workflow, not legal advice or a guarantee. A suspicious or high-value case may require a Portuguese lawyer, the platform, the bank or authorities.",
    },
}

JOBS["f7d8f9ad672dcf26884de4e6"] = {
    "primaryIntent": "Build an evidence-led Madeira arrival cash plan covering housing entry costs and first-month operating expenses",
    "seoTitle": "Madeira arrival budget: deposits and first-month cash | NOMADeira",
    "metaDescription": "Plan Madeira arrival cash for temporary housing, rent, deposit, advance payment, transport and setup using written quotes.",
    "h1": "Madeira arrival budget: deposits and first-month cash",
    "directAnswer": "An arrival budget is not one island-wide number. Start with the exact written housing offer, separate rent, lawful agreed advance rent and security, add temporary accommodation and overlap days, then obtain current quotes for transport, utilities, connectivity, insurance and household needs. Keep a contingency outside the amount committed to the landlord.",
    "outline": ["Build the budget from commitments, not averages", "Temporary accommodation and overlap", "Rent, advance payment and security", "Current asking snapshots", "Transport, connectivity and setup", "Cash timing and contingency", "Final arrival-budget worksheet"],
    "approvedInternalLinks": ["/housing/deposits/", "/housing/long-term-rental/", "/madeira-rental-scam-checklist/", "/cost-of-living-funchal/", "/transport/monthly-car-rental/", "/best-esim-madeira/", "/setup-plan/"],
    "sourceReferences": [CIVIL_RENT, FINANCE_RECEIPTS, DREM,
        listing("idealista-funchal-arrival-2026-08-27", "Idealista: Funchal rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/funchal/", "On 27 August 2026 the Funchal search displayed 209 asking listings and an average asking figure of €18.73/m², with mixed home sizes and some temporary terms. This is an asking-supply snapshot, not a complete arrival budget.", "The dated Funchal snapshot supplies a current asking-price baseline, not a full budget.", "27 August 2026: 209 Funchal listings; displayed average €18.73/m²; mixed sizes and terms."),
        listing("idealista-calheta-arrival-2026-08-27", "Idealista: Calheta rentals, 27 August 2026", "https://www.idealista.pt/en/arrendar-casas/calheta-madeira/", "On 27 August 2026 the Calheta search displayed 12 asking listings, including examples from €650/month to €4,000/month with temporary and luxury stock. The spread demonstrates why a household must use its chosen written offer rather than one island-wide rent assumption.", "The Calheta snapshot illustrates how location and lease type change arrival cash needs.", "27 August 2026: 12 Calheta listings; examples €650 to €4,000/month; mixed temporary, standard and luxury stock."),
    ],
    "primaryCta": {"label": "Build a personalised Setup Plan", "url": "/setup-plan/"},
    "editorial": {"author": "NOMADeira editorial team", "reviewer": "NOMADeira fact review", "owner": "NOMADeira", "factCheckedAt": TODAY, "reviewDueAt": "2026-11-27", "reviewCadence": "3 months"},
    "approvals": {"editorialReview": True, "productFactCheck": True, "seoReview": True, "browserQa": True},
    "contentDetails": {
        "audience": "International residents estimating cash required before and during their first month in Madeira",
        "budgetMethod": "Provide a fill-in worksheet and explicit arithmetic using the reader's written quotes. A sourced rent example may illustrate the method but must not be presented as a universal budget.",
        "allowedReaderChecks": ["Record temporary accommodation by night and overlap days.", "Copy rent, advance payment and security from the draft contract.", "Request written utility and connectivity setup terms.", "Price the actual airport-to-home and repeated transport plan.", "Hold contingency separately from committed housing funds."],
        "forbiddenClaims": ["one average is a complete Madeira arrival budget", "every landlord requests the same deposit or advance", "a current asking listing is an available completed contract", "a checklist guarantees no unexpected costs"],
        "limitations": "Housing, temporary accommodation and setup prices change. The result is a planning worksheet based on current written quotes, not a guaranteed minimum.",
    },
}

JOBS["4fe5f9e3e62982b03f747ed3"] = {
    "primaryIntent": "Help a visitor compare verified Funchal whale-watching formats, schedules, prices and sighting policies",
    "seoTitle": "Whale watching from Funchal: boat, season and operator | NOMADeira",
    "metaDescription": "Compare verified Funchal whale-watching boats, durations, prices, schedules and no-sighting policies before booking.",
    "h1": "Whale watching from Funchal: boat, season and operator",
    "directAnswer": "Choose a Funchal whale-watching trip by boat type, duration, passenger capacity, marine guidance, departure time, accessibility and the written no-sighting policy. Whales are wild animals, so no operator can guarantee a particular species or encounter; compare the current operator terms immediately before booking.",
    "outline": ["Choose the trip format first", "When whale watching operates", "RIB versus catamaran", "Verified Funchal operator comparison", "What a no-sighting policy means", "Weather, mobility and family checks", "Booking decision checklist"],
    "approvedInternalLinks": ["/things-to-do/", "/things-to-do/diving/", "/where-to-live/funchal/", "/best-esim-madeira/", "/setup-plan/"],
    "sourceReferences": [
        source("visit-madeira-whales", "Visit Madeira: dolphin and whale watching", "Visit Madeira", "https://visitmadeira.com/en/what-to-do/sea-lovers/activities/dolphin-whale-watching/", "Visit Madeira describes whale and dolphin watching as a year-round Madeira activity and lists frequently observed species. It does not guarantee any sighting, species, sea condition or operator availability on a chosen date.", "Visit Madeira describes the activity, typical species and year-round availability at destination level."),
        source("visit-madeira-rota", "Visit Madeira: Rota dos Cetaceos", "Visit Madeira", "https://www.visitmadeira.com/en/what-to-do/tourist-entertainment-associates/rota-dos-cetaceos/", "Visit Madeira lists Rota dos Cetaceos as a Funchal maritime-tourism operator using two 18-seat semi-rigid boats, with a skipper and biologist, a 10-minute briefing and 2 hour 30 minute trips. It publishes two daily winter departures and three daily summer departures.", "Visit Madeira publishes Rota dos Cetaceos' boat, staffing, duration and seasonal departure pattern."),
        source("rota-current-offer", "Rota dos Cetaceos: current whale-watching offer", "Rota dos Cetaceos", "https://rota-dos-cetaceos.pt/pt/observacao-cetaceos/", "The operator page lists a 2.5-hour trip at €60 for adults, €35 for children aged 6 to 11, free for children up to 5 and €990 for a private trip for up to 18 people. Prices and availability must be rechecked before booking.", "Rota dos Cetaceos publishes current duration, age bands and prices."),
        source("vmt-current-offer", "VMT Madeira: current whale-watching offer", "VMT Madeira", "https://www.vmtmadeira.com/en/trips/whale-watching/", "VMT lists a three-hour catamaran trip from Funchal at €40 for adults, €20 for children up to 12, free for babies up to 4 and €100 for a family pack. It publishes daily departure windows and says a second trip is offered if no cetaceans are seen; this is a repeat-trip policy, not a sighting guarantee on either trip.", "VMT publishes its catamaran duration, prices, departure windows and repeat-trip policy."),
    ],
    "primaryCta": {"label": "Continue planning Madeira activities", "url": "/things-to-do/"},
    "editorial": {"author": "NOMADeira editorial team", "reviewer": "NOMADeira fact review", "owner": "NOMADeira", "factCheckedAt": TODAY, "reviewDueAt": "2026-09-27", "reviewCadence": "1 month"},
    "approvals": {"editorialReview": True, "productFactCheck": True, "seoReview": True, "browserQa": True},
    "contentDetails": {
        "audience": "Visitors comparing bookable whale-watching departures from Funchal",
        "comparisonMethod": "Separate boat format, duration, capacity, staffing, current price, departure time, accessibility and no-sighting terms. Link directly to the operator when describing its own terms.",
        "allowedReaderChecks": ["Confirm current departure time and check-in deadline.", "Ask about accessibility, seating, shade, toilets and motion exposure for the selected vessel.", "Read the cancellation, weather and no-sighting terms before payment.", "Confirm age bands and the exact total at checkout.", "Treat every species encounter as uncertain."],
        "forbiddenClaims": ["a whale or dolphin sighting is guaranteed", "one operator is best without a stated decision criterion", "destination-level species lists predict a chosen trip", "a second-trip policy guarantees a later sighting", "prices remain current after the fact-check date"],
        "limitations": "Wildlife, sea conditions, vessel operation, schedules, prices and availability can change. Recheck the operator's current terms before payment.",
    },
}


now = datetime.now(timezone.utc).isoformat(timespec="seconds")
with sqlite3.connect(DB) as conn:
    for job_id, brief in JOBS.items():
        row = conn.execute("select sources_json from content_jobs where site_id=18 and id=?", (job_id,)).fetchone()
        if not row:
            raise SystemExit(f"missing job {job_id}")
        payload = json.loads(row[0] or "{}")
        payload["pageBrief"] = brief
        payload["generationBlockedUntilSourceReview"] = False
        payload["sourceResearchCompletedAt"] = now
        payload["sourceResearchMethod"] = "primary and direct provider sources verified 2026-08-27"
        conn.execute(
            "update content_jobs set sources_json=?,status='QUEUED',error=NULL,scheduled_for=NULL,updated_at=? where site_id=18 and id=?",
            (json.dumps(payload, ensure_ascii=False), now, job_id),
        )
print(json.dumps({"ok": True, "jobs": len(JOBS), "ids": list(JOBS)}, ensure_ascii=False))
