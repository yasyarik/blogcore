#!/usr/bin/env python3
"""Apply the approved three-day native publication cadence to LaycanMatch."""

import argparse
import json
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


SITE_ID = 8
FIRST_PUBLICATION = datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)
CADENCE = timedelta(days=3)
JOB_IDS = [
    "ece137d4a170f41632ac5c45",
    "997207fa0c3d35a9d25bc2bc",
    "865025a6a3f1d5d6fb04eea7",
    "4b3e30a01ea623d99d6cd4a5",
    "59ebd3410a1a34a6f023bf2c",
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
    first = datetime.fromisoformat(args.first_publication.replace("Z", "+00:00"))
    if first.tzinfo is None:
        raise ValueError("first publication must include a timezone")
    scheduled = []
    for index, job_id in enumerate(JOB_IDS):
        when = (first + index * CADENCE).astimezone(timezone.utc).isoformat(timespec="seconds")
        result = post_json(
            f"{args.base_url.rstrip('/')}/api/sites/{SITE_ID}/content-jobs/{job_id}/schedule",
            {"scheduledFor": when},
        )
        scheduled.append({"jobId": job_id, "scheduledFor": result["scheduledFor"]})
    print(json.dumps({"scheduled": scheduled}, indent=2))


if __name__ == "__main__":
    main()
