#!/usr/bin/env python3
"""Queue and schedule CabinJoin's supporting editorial cluster.

The posts support existing direct SEO pages. They are not new money pages and
must remain explanatory: CabinJoin facilitates request-led trips but does not
own boats, operate voyages, or guarantee participation.
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


SITE_ID = 15
FIRST_PUBLICATION = datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)
CADENCE = timedelta(days=3)


def idea(title, slug, angle):
    return {
        "title": title,
        "targetPath": f"/blog/{slug}/",
        "contentType": "blog",
        "source": "approved_cabinjoin_supporting_cluster",
        "angle": angle,
    }


IDEAS = [
    idea("Can You Go Sailing Alone? What Solo Travellers Should Know Before Joining a Group Trip", "can-you-go-sailing-alone", "Answer the practical solo-traveller question without framing a request as an instant booking. Cover suitability, what a traveller should check, organiser confirmation and skipper responsibility. Link contextually to /solo-sailing-holidays/ and /join-a-sailing-trip-alone/."),
    idea("What Is Cabin Charter Sailing? A Practical Guide to Shared Yacht Trips", "what-is-cabin-charter-sailing", "Explain the distinction between a single place/cabin on an organised trip and chartering an entire yacht. Cover shared spaces, real-trip variables and confirmation boundaries. Link to /cabin-charter-sailing/ and /group-sailing-trips/."),
    idea("Do You Need Sailing Experience to Join a Yacht Trip?", "do-you-need-sailing-experience-to-join-a-yacht-trip", "Give a cautious decision framework: experience expectations vary by trip, ask the organiser, and the skipper remains responsible for navigation and safety. Do not promise suitability. Link to /join-a-sailing-trip-alone/ and /safety/."),
    idea("How Much Does a Shared Sailing Holiday Cost? What Changes the Price", "shared-sailing-holiday-cost", "Explain cost drivers without inventing price bands: route, season, cabin, yacht, duration, inclusions and trip-specific terms. State that availability and payment follow confirmation. Link to /solo-sailing-holidays/ and /cabin-charter-sailing/."),
    idea("How to Choose the Right Sailing Trip: Route, Crew, Pace and Cabin", "how-to-choose-the-right-sailing-trip", "Create a practical checklist for evaluating an organised trip: route, pace, group fit, cabin/place, rules, comfort and organiser communication. Link to /group-sailing-trips/ and /trips/."),
    idea("What to Pack for a One-Week Sailing Holiday", "what-to-pack-for-a-one-week-sailing-holiday", "Provide an evergreen packing framework for an organised sailing trip, noting that climate, route, vessel and organiser guidance vary. Link to /solo-sailing-holidays/ and /trips/."),
    idea("How Shared Cabins Work on a Sailing Trip: Privacy, Expectations and Etiquette", "how-shared-cabins-work-on-a-sailing-trip", "Explain cabins, berths, common spaces, privacy, communication and respectful group expectations without assuming any particular vessel layout. Link to /cabin-charter-sailing/ and /group-sailing-trips/."),
    idea("How to Plan a Group Sailing Holiday: Yacht, Route, Crew and Responsibilities", "how-to-plan-a-group-sailing-holiday", "Support organisers after a charter is secured: define a workable trip, roles, places, rules and request process. Preserve the boundary that CabinJoin does not charter or operate the yacht. Link to /organise-a-sailing-holiday/ and /for-organizers/."),
    idea("What to Decide Before You Open Places on a Confirmed Yacht Charter", "what-to-decide-before-opening-places-on-a-yacht-charter", "Give organisers a pre-publication checklist: genuine charter, route, dates, capacity, suitability, rules, supplier terms and a fair request-review process. Link to /create-a-public-sailing-trip/ and /find-people-for-yacht-charter/."),
    idea("How to Write a Clear Trip Description That Attracts the Right Crew", "how-to-write-a-clear-sailing-trip-description", "Explain how to accurately describe a real trip so travellers can self-select: route, pace, space, expectations and non-negotiables. No claim that a listing guarantees applicants. Link to /create-a-public-sailing-trip/ and /for-organizers/."),
    idea("How to Handle Participant Requests for a Group Sailing Trip", "how-to-handle-participant-requests-for-a-group-sailing-trip", "Explain a respectful request workflow: assess practical fit, communicate clearly, confirm only when appropriate, and distinguish requests from bookings. Link to /find-people-for-yacht-charter/ and /how-it-works/."),
    idea("How to Fill Empty Yacht Cabins Without Creating the Wrong Expectations", "how-to-fill-empty-yacht-cabins-responsibly", "Explain how organisers can present genuine open places from a confirmed charter while being precise about availability, eligibility and confirmation. Link to /fill-empty-cabins-yacht-charter/ and /for-organizers/."),
]


def post_json(url, payload):
    request = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    parser.add_argument("--first-publication", default=FIRST_PUBLICATION.isoformat())
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    result = post_json(
        f"{base_url}/api/sites/{SITE_ID}/article-ideas/queue",
        {"range": "approved-cabinjoin-editorial-cluster", "signals": [], "ideas": IDEAS},
    )
    jobs = result.get("jobs", [])
    if len(jobs) != len(IDEAS):
        raise RuntimeError(f"expected {len(IDEAS)} queued jobs, received {len(jobs)}: {result}")
    first = datetime.fromisoformat(args.first_publication.replace("Z", "+00:00"))
    if first.tzinfo is None:
        raise ValueError("first publication must include a timezone")
    schedule = []
    for index, job in enumerate(jobs):
        when = (first + index * CADENCE).astimezone(timezone.utc).isoformat(timespec="seconds")
        scheduled = post_json(
            f"{base_url}/api/sites/{SITE_ID}/content-jobs/{job['id']}/schedule",
            {"scheduledFor": when},
        )
        schedule.append({"id": job["id"], "title": job.get("title"), "scheduledFor": scheduled["scheduledFor"]})
    print(json.dumps({"queued": len(jobs), "schedule": schedule}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
