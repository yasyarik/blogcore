#!/usr/bin/env python3
"""Queue CabinJoin's approved shared-trip and organiser SEO money pages.

This script uses Blog Core's normal queue endpoint so duplicate detection and
the native content-store lifecycle remain the source of truth.
"""

import argparse
import json
import urllib.request


SITE_ID = 15
TRAVELLER_LINKS = [
    {"url": "/trips"},
    {"url": "/how-it-works"},
    {"url": "/safety"},
    {"url": "/for-organizers"},
]
ORGANISER_LINKS = [
    {"url": "/for-organizers"},
    {"url": "/boats"},
    {"url": "/trips"},
    {"url": "/how-it-works"},
    {"url": "/safety"},
]
PRODUCT_FACTS = {
    "marketplaceModel": "CabinJoin is a request-led marketplace for yacht travel. It does not own vessels or operate voyages.",
    "travellerFlow": "A traveller can request a place or cabin in an already organised yacht trip.",
    "organiserFlow": "A verified organiser can open a public trip only after securing a specific chartered yacht, then define places and rules and review traveller requests.",
    "bookingBoundary": "A request is not an instant booking. Availability and participation require organiser or operator confirmation before payment is captured.",
    "serviceBoundary": "The organiser, owner, or named supplier remains responsible for the actual trip and the skipper retains navigational safety authority.",
}


def brief(*, path, h1, description, answer, outline, cta, links, audience, keyword):
    return {
        "targetPath": path,
        "primaryIntent": keyword,
        "seoTitle": h1,
        "metaDescription": description,
        "h1": h1,
        "directAnswer": answer,
        "outline": outline,
        "contentDetails": {**PRODUCT_FACTS, "audience": audience},
        "primaryCta": cta,
        "approvedInternalLinks": links,
        "editorial": {
            "author": "CabinJoin editorial team",
            "reviewer": "CabinJoin product team",
            "owner": "CabinJoin",
            "reviewDueAt": "2027-02-06",
            "reviewCadence": "Every 6 months",
            "factCheckedAt": "2026-08-06",
        },
        "sourceReferences": [
            {
                "id": "cabinjoin-how-it-works",
                "title": "How CabinJoin Works",
                "publisher": "CabinJoin",
                "publicUrl": "https://cabinjoin.com/how-it-works",
                "accessedAt": "2026-08-06",
                "supports": "Request-led trip, confirmation, and payment workflow.",
            },
            {
                "id": "cabinjoin-organisers",
                "title": "For Yacht Trip Organisers",
                "publisher": "CabinJoin",
                "publicUrl": "https://cabinjoin.com/for-organizers",
                "accessedAt": "2026-08-06",
                "supports": "Confirmed-charter requirement and organiser responsibility for public trips.",
            },
        ],
        "approvals": {
            "editorialReview": True,
            "productFactCheck": True,
            "seoReview": True,
            "browserQa": True,
        },
    }


IDEAS = [
    {
        "title": "Solo Sailing Holidays for Singles",
        "angle": "A decision page for solo travellers who want to join a planned shared yacht trip without booking a whole yacht.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/solo-sailing-holidays/",
            h1="Solo Sailing Holidays for Singles",
            description="Explore how solo travellers can request a place on an organised shared yacht trip through CabinJoin.",
            answer="Solo travellers can use CabinJoin to explore organised yacht trips and request a place or cabin without arranging a whole yacht. Each listing should explain the journey and available places. A request is reviewed by the organiser or operator, so availability and participation are confirmed before payment is captured. CabinJoin does not operate the voyage or guarantee a place.",
            outline=["Who solo sailing holidays suit", "How to join an organised trip", "Cabin, berth, and shared-space expectations", "What to check before requesting a place", "How confirmation and payment work", "Limitations and suitability", "How CabinJoin fits the journey"],
            cta={"label": "Explore trips", "url": "/trips"},
            links=TRAVELLER_LINKS,
            audience="Solo travellers considering a shared sailing holiday.",
            keyword="solo sailing holidays; sailing holidays for singles",
        ),
    },
    {
        "title": "Cabin Charter Sailing",
        "angle": "A practical commercial page for travellers choosing a cabin or place on an organised yacht trip instead of arranging a full private charter.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/cabin-charter-sailing/",
            h1="Cabin Charter Sailing: Join an Organised Yacht Trip",
            description="Understand cabin charter sailing and how CabinJoin lets travellers request a place in an organised yacht trip.",
            answer="Cabin charter sailing means joining a shared yacht trip by requesting an individual place or cabin rather than chartering the entire vessel with a private group. On CabinJoin, travellers can review an organiser-led trip and send a request. The organiser or operator must confirm participation before payment is captured, and the named supplier remains responsible for the voyage itself.",
            outline=["What cabin charter sailing means", "Cabin or place versus a whole-yacht charter", "What varies between real trips", "Questions to ask before making a request", "Confirmation, payment, and responsibility", "Limitations and suitability", "How CabinJoin supports the decision"],
            cta={"label": "Explore trips", "url": "/trips"},
            links=TRAVELLER_LINKS,
            audience="Travellers comparing a shared place or cabin with a private yacht charter.",
            keyword="cabin charter sailing; cabin charter sailing holidays",
        ),
    },
    {
        "title": "Group Sailing Trips",
        "angle": "A decision page for a traveller selecting a small organised yacht journey and assessing the route, group, and request process.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/group-sailing-trips/",
            h1="Group Sailing Trips: Find a Place on a Shared Yacht Journey",
            description="Learn how organised group sailing trips work and what to check before requesting a place through CabinJoin.",
            answer="A group sailing trip brings travellers together around a real organiser-led yacht journey rather than a generic invitation to travel. CabinJoin lets a traveller review the available trip information and request a place or cabin. The organiser or operator remains responsible for the trip, reviews participation requests, and confirms availability before payment is captured. CabinJoin does not operate the yacht.",
            outline=["How an organised group sailing trip works", "Choosing a trip by practical fit", "What to understand about the organiser and crew", "A request is not an instant booking", "How to prepare before joining", "Limitations and suitability", "How CabinJoin helps travellers discover trips"],
            cta={"label": "Explore trips", "url": "/trips"},
            links=TRAVELLER_LINKS,
            audience="Travellers evaluating an organised shared sailing trip.",
            keyword="group sailing trips; small group sailing trips",
        ),
    },
    {
        "title": "Join a Sailing Trip Alone",
        "angle": "A direct-answer page for first-time solo travellers who need to understand whether and how they can request a place in an organised sailing trip.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/join-a-sailing-trip-alone/",
            h1="How to Join a Sailing Trip Alone",
            description="A practical guide to requesting a place on an organised sailing trip as a solo traveller through CabinJoin.",
            answer="You can join a sailing trip alone by choosing an organised journey that suits your needs and sending a request for a place or cabin. CabinJoin does not treat that request as an instant booking. The organiser or operator reviews it and must confirm availability and participation before payment is captured. The trip supplier and skipper remain responsible for the actual voyage and navigational safety.",
            outline=["Can one person join a sailing trip", "How to assess a trip before requesting", "Experience, comfort, and crew expectations", "The request and confirmation sequence", "Questions worth asking before payment", "Limitations and suitability", "Where CabinJoin helps"],
            cta={"label": "Explore trips", "url": "/trips"},
            links=TRAVELLER_LINKS,
            audience="First-time solo travellers considering an organised sailing trip.",
            keyword="join a sailing trip alone; can I join a sailing trip alone",
        ),
    },
    {
        "title": "How to Organise a Sailing Holiday",
        "angle": "A commercial workflow page for an organiser moving from a confirmed yacht charter to a well-defined public sailing trip.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/organise-a-sailing-holiday/",
            h1="How to Organise a Sailing Holiday After Chartering a Yacht",
            description="Plan a group sailing holiday after securing a yacht charter, then create a real public trip and manage requests with CabinJoin.",
            answer="Organising a sailing holiday starts with securing a suitable yacht charter, then defining a workable journey, available places, and rules for the people who may join. CabinJoin supports the public-trip and request-management stage after that charter exists. It does not charter the yacht, guarantee applicants, or operate the voyage. The organiser, supplier, and skipper retain their respective responsibilities.",
            outline=["Start with a confirmed charter", "Define the trip before inviting participants", "Set places, expectations, and rules", "Publish a real trip rather than a generic invitation", "Review requests and confirm participation", "Limitations and suitability", "How CabinJoin supports organisers"],
            cta={"label": "Explore the organiser flow", "url": "/for-organizers"},
            links=ORGANISER_LINKS,
            audience="People who have secured or are securing a yacht charter for a group journey.",
            keyword="how to organise a sailing holiday; how to organize a sailing holiday",
        ),
    },
    {
        "title": "Create a Public Sailing Trip",
        "angle": "A product-led decision page for a verified organiser with a confirmed charter who needs to turn it into a real public trip.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/create-a-public-sailing-trip/",
            h1="Create a Public Sailing Trip From a Confirmed Charter",
            description="See how a verified organiser can create a real public sailing trip after securing a specific chartered yacht.",
            answer="A public CabinJoin trip begins only after a verified organiser has secured a specific chartered yacht. The organiser can define the journey, available places, and clear rules, then review traveller requests before confirming participation. CabinJoin provides the marketplace workflow for presenting the trip and handling requests. It does not supply the yacht, guarantee demand, or operate the voyage.",
            outline=["Why a public trip needs a real charter first", "What makes a trip ready to publish", "Places, rules, and clear expectations", "How traveller requests are handled", "What CabinJoin does and does not do", "Limitations and suitability", "The organiser's next practical step"],
            cta={"label": "Explore the organiser flow", "url": "/for-organizers"},
            links=ORGANISER_LINKS,
            audience="Verified organisers preparing to open a confirmed charter to travellers.",
            keyword="create a public sailing trip; organise a group sailing trip",
        ),
    },
    {
        "title": "Find People for a Yacht Charter",
        "angle": "A decision page for an organiser with a confirmed charter who needs a controlled way to invite and review potential participants.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/find-people-for-yacht-charter/",
            h1="How to Find People for a Confirmed Yacht Charter",
            description="Learn how organisers can open a confirmed yacht charter as a public CabinJoin trip and manage traveller requests.",
            answer="After securing a yacht charter, an organiser can create a public CabinJoin trip, explain the journey and available places, and review traveller requests before confirming participation. This gives prospective travellers enough context to decide whether to request a place, while the organiser retains control over acceptance. CabinJoin does not guarantee applicants, availability, a completed crew, or the underlying charter service.",
            outline=["The difference between a charter and a public trip", "Define who the trip is for", "Make places and expectations clear", "Review requests before confirming anyone", "Avoid promises a listing cannot support", "Limitations and suitability", "How CabinJoin supports controlled crew building"],
            cta={"label": "Explore the organiser flow", "url": "/for-organizers"},
            links=ORGANISER_LINKS,
            audience="Organisers with a confirmed yacht charter who want to form a suitable crew.",
            keyword="find people for yacht charter; find crew for yacht charter",
        ),
    },
    {
        "title": "Fill Empty Cabins on a Yacht Charter",
        "angle": "A commercial page explaining how an organiser can publish genuine open places only after a charter is confirmed, without making availability promises.",
        "source": "approved_cabinjoin_demand_research",
        "contentType": "use_case",
        "pageBrief": brief(
            path="/fill-empty-cabins-yacht-charter/",
            h1="How to Fill Empty Cabins on a Confirmed Yacht Charter",
            description="Turn open places on a confirmed yacht charter into a public CabinJoin trip and review participant requests responsibly.",
            answer="An organiser with a confirmed yacht charter can publish a real CabinJoin trip with the available places and trip rules, then review requests before confirming participants. The listing should explain the trip without implying that a request is an instant booking. CabinJoin does not guarantee availability or operate the yacht, and the organiser or supplier remains responsible for the actual voyage.",
            outline=["Only publish places backed by a confirmed charter", "Describe the trip clearly before opening places", "Set rules that help the right people self-select", "Review requests rather than promising a booking", "Keep supplier and organiser responsibilities clear", "Limitations and suitability", "How CabinJoin supports the workflow"],
            cta={"label": "Explore the organiser flow", "url": "/for-organizers"},
            links=ORGANISER_LINKS,
            audience="Organisers deciding how to fill open places on a confirmed charter.",
            keyword="fill empty cabins yacht charter; share a yacht charter",
        ),
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    args = parser.parse_args()
    request = urllib.request.Request(
        f"{args.base_url.rstrip('/')}/api/sites/{SITE_ID}/article-ideas/queue",
        data=json.dumps({"range": "manual-demand-research", "signals": [], "ideas": IDEAS}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        print(response.read().decode())


if __name__ == "__main__":
    main()
