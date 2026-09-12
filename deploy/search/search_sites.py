#!/usr/bin/env python3
"""Run event-driven search notification or read-only multi-site monitoring."""

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "deploy" / "georivo"))

from gsc_submit import submit  # noqa: E402

CONFIG_PATH = Path(__file__).with_name("sites.json")
GSC_CREDENTIALS = BASE_DIR / "keys" / "gsc-service-account.json"


def load_sites():
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    sites = payload.get("sites")
    if not isinstance(sites, list) or not sites:
        raise RuntimeError("Search site configuration is empty")
    return sites


def site_by_id(site_id):
    matches = [site for site in load_sites() if int(site.get("siteId", -1)) == site_id]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one search config for site {site_id}")
    return matches[0]


def read_environment_value(path, key):
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    raise RuntimeError(f"{key} is missing from protected environment")


def submit_indexnow(site, published_url):
    environment_file = site.get("indexNowEnvironmentFile")
    key_name = site.get("indexNowKeyName")
    if not environment_file or not key_name:
        return {"status": "not_configured"}
    parsed = urllib.parse.urlsplit(published_url)
    homepage = urllib.parse.urlsplit(site["sitemapUrl"])
    if parsed.scheme != "https" or parsed.netloc != homepage.netloc:
        raise RuntimeError("Published URL is outside the configured site host")
    key = read_environment_value(environment_file, key_name)
    response = requests.post(
        "https://api.indexnow.org/indexnow",
        json={
            "host": parsed.netloc,
            "key": key,
            "keyLocation": f"https://{parsed.netloc}/{key}.txt",
            "urlList": [published_url],
        },
        timeout=30,
    )
    if response.status_code not in {200, 202}:
        raise RuntimeError(f"IndexNow HTTP {response.status_code}")
    return {"status": "accepted", "httpStatus": response.status_code}


def run_site(site, mode, published_url=None):
    status_file = Path(site["statusFile"])
    status_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    code = submit(
        GSC_CREDENTIALS,
        site["siteUrl"],
        site["sitemapUrl"],
        status_file,
        tuple(site.get("inspectionUrls") or ()),
        mode=mode,
    )
    result = {"siteId": site["siteId"], "name": site["name"], "gscExit": code}
    if mode == "notify" and published_url:
        result["indexNow"] = submit_indexnow(site, published_url)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("notify", "monitor"))
    parser.add_argument("--site-id", type=int)
    parser.add_argument("--published-url")
    args = parser.parse_args()
    if args.mode == "notify":
        if args.site_id is None or not args.published_url:
            parser.error("notify requires --site-id and --published-url")
        results = [run_site(site_by_id(args.site_id), "notify", args.published_url)]
    else:
        results = []
        failed = False
        for site in load_sites():
            try:
                result = run_site(site, "monitor")
                failed = failed or result["gscExit"] not in {0, 75}
                results.append(result)
            except Exception as error:
                failed = True
                results.append({"siteId": site.get("siteId"), "name": site.get("name"), "error": str(error)})
        print(json.dumps({"mode": "monitor", "results": results}, ensure_ascii=False))
        return 1 if failed else 0
    print(json.dumps({"mode": args.mode, "results": results}, ensure_ascii=False))
    return 0 if all(item.get("gscExit") in {0, 75} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
