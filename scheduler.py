#!/usr/bin/env python3
"""Run due Blog Core article and social publications."""

import time

from app import init_db, run_scheduled_content_publications, run_scheduled_social_publications


def main():
    init_db()
    while True:
        try:
            result = run_scheduled_content_publications()
            if result["due"]:
                print(f"scheduled-publications {result}", flush=True)
            social_result = run_scheduled_social_publications()
            if social_result["due"]:
                print(f"scheduled-social-publications {social_result}", flush=True)
        except Exception as error:
            print(f"scheduled-publications worker error: {error}", flush=True)
        time.sleep(60)


if __name__ == "__main__":
    main()
