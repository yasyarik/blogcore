#!/usr/bin/env python3
"""Verify GSC access and submit a sitemap through the official API."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account


WEBMASTERS_API = "https://www.googleapis.com/webmasters/v3"
URL_INSPECTION_API = (
    "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
)
WEBMASTERS_SCOPE = "https://www.googleapis.com/auth/webmasters"
ALLOWED_PERMISSIONS = {"siteOwner", "siteFullUser"}
BLOCKED_EXIT = 75
DEFAULT_INSPECTION_URLS = (
    "https://georivo.com/",
    "https://georivo.com/how-it-works",
    "https://georivo.com/coverage",
    "https://georivo.com/pricing",
    "https://georivo.com/templates",
    "https://georivo.com/examples",
    "https://georivo.com/embed",
)


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_status(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def request_json(method, url, access_token, **kwargs):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    response = requests.request(method, url, headers=headers, timeout=45, **kwargs)
    try:
        payload = response.json() if response.content else {}
    except ValueError:
        payload = {"raw": response.text[:1000]}
    if response.status_code >= 400:
        message = (
            payload.get("error", {}).get("message")
            if isinstance(payload.get("error"), dict)
            else None
        )
        raise RuntimeError(
            f"Google API HTTP {response.status_code}: {message or response.reason}"
        )
    return payload


def load_credentials(path):
    credentials = service_account.Credentials.from_service_account_file(
        str(path),
        scopes=[WEBMASTERS_SCOPE],
    )
    credentials.refresh(Request())
    return credentials


def verify_public_sitemap(url):
    response = requests.get(
        url,
        headers={"User-Agent": "BlogCoreGSCSubmit/1.0 (+https://blog.yas.ooo)"},
        timeout=45,
    )
    response.raise_for_status()
    body = response.content
    if b"<urlset" not in body and b"<sitemapindex" not in body:
        raise RuntimeError("public sitemap response is not a sitemap XML document")
    return {
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "contentType": response.headers.get("content-type", ""),
    }


def search_analytics_window(access_token, encoded_site, start_date, end_date):
    payload = request_json(
        "POST",
        f"{WEBMASTERS_API}/sites/{encoded_site}/searchAnalytics/query",
        access_token,
        json={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["date"],
            "dataState": "all",
            "rowLimit": 1000,
        },
    )
    rows = payload.get("rows", [])
    return {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "daysWithData": len(rows),
        "clicks": sum(float(row.get("clicks", 0)) for row in rows),
        "impressions": sum(float(row.get("impressions", 0)) for row in rows),
    }


def search_performance(access_token, encoded_site):
    # Search Console data can lag. Exclude today and yesterday from both
    # comparison windows so an incomplete day cannot create a false drop.
    current_end = datetime.now(timezone.utc).date() - timedelta(days=2)
    current_start = current_end - timedelta(days=27)
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=27)
    current = search_analytics_window(
        access_token,
        encoded_site,
        current_start,
        current_end,
    )
    previous = search_analytics_window(
        access_token,
        encoded_site,
        previous_start,
        previous_end,
    )
    pages = request_json(
        "POST",
        f"{WEBMASTERS_API}/sites/{encoded_site}/searchAnalytics/query",
        access_token,
        json={
            "startDate": current_start.isoformat(),
            "endDate": current_end.isoformat(),
            "dimensions": ["page"],
            "dataState": "all",
            "rowLimit": 25,
        },
    ).get("rows", [])
    return {
        "current28Days": current,
        "previous28Days": previous,
        "topPages": [
            {
                "page": (row.get("keys") or [""])[0],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0),
            }
            for row in pages
        ],
        "note": "No rows means Search Console has no reportable data for the period.",
    }


def inspect_urls(access_token, site_url, inspection_urls):
    inspected = []
    for url in inspection_urls:
        try:
            payload = request_json(
                "POST",
                URL_INSPECTION_API,
                access_token,
                json={
                    "inspectionUrl": url,
                    "siteUrl": site_url,
                    "languageCode": "en-US",
                },
            )
            status = (
                payload.get("inspectionResult", {})
                .get("indexStatusResult", {})
            )
            inspected.append(
                {
                    "url": url,
                    "verdict": status.get("verdict"),
                    "coverageState": status.get("coverageState"),
                    "robotsTxtState": status.get("robotsTxtState"),
                    "indexingState": status.get("indexingState"),
                    "lastCrawlTime": status.get("lastCrawlTime"),
                    "pageFetchState": status.get("pageFetchState"),
                    "googleCanonical": status.get("googleCanonical"),
                    "userCanonical": status.get("userCanonical"),
                }
            )
        except Exception as error:
            inspected.append(
                {
                    "url": url,
                    "error": str(error),
                }
            )
    return inspected


def submit(
    credentials_path,
    site_url,
    sitemap_url,
    status_path,
    inspection_urls,
):
    result = {
        "checkedAt": stamp(),
        "siteUrl": site_url,
        "sitemapUrl": sitemap_url,
        "status": "checking",
    }
    try:
        result["sitemap"] = verify_public_sitemap(sitemap_url)
        credentials = load_credentials(credentials_path)
        result["serviceAccount"] = credentials.service_account_email
        sites = request_json(
            "GET",
            f"{WEBMASTERS_API}/sites",
            credentials.token,
        ).get("siteEntry", [])
        properties = {
            item.get("siteUrl"): item.get("permissionLevel")
            for item in sites
            if item.get("siteUrl")
        }
        permission = properties.get(site_url)
        result["permissionLevel"] = permission
        if permission not in ALLOWED_PERMISSIONS:
            result["status"] = "blocked"
            result["reason"] = (
                f"service account has no full access to Search Console property {site_url}"
            )
            result["availableProperties"] = sorted(properties)
            write_status(status_path, result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return BLOCKED_EXIT

        encoded_site = quote(site_url, safe="")
        encoded_feed = quote(sitemap_url, safe="")
        request_json(
            "PUT",
            f"{WEBMASTERS_API}/sites/{encoded_site}/sitemaps/{encoded_feed}",
            credentials.token,
        )
        submitted = request_json(
            "GET",
            f"{WEBMASTERS_API}/sites/{encoded_site}/sitemaps/{encoded_feed}",
            credentials.token,
        )
        result["status"] = "submitted"
        result["submittedAt"] = stamp()
        result["apiRecord"] = {
            key: submitted.get(key)
            for key in (
                "path",
                "lastSubmitted",
                "isPending",
                "isSitemapsIndex",
                "lastDownloaded",
                "warnings",
                "errors",
            )
            if key in submitted
        }
        result["monitoringErrors"] = []
        try:
            result["searchPerformance"] = search_performance(
                credentials.token,
                encoded_site,
            )
        except Exception as error:
            result["monitoringErrors"].append(
                f"search performance: {error}"
            )
        result["indexInspection"] = inspect_urls(
            credentials.token,
            site_url,
            inspection_urls,
        )
        write_status(status_path, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        result["status"] = "error"
        result["reason"] = str(error)
        write_status(status_path, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--credentials",
        type=Path,
        default=Path(
            os.getenv(
                "GSC_SERVICE_ACCOUNT_FILE",
                "/var/www/blog.yas.ooo/keys/gsc-service-account.json",
            )
        ),
    )
    parser.add_argument("--site-url", default="sc-domain:georivo.com")
    parser.add_argument(
        "--sitemap-url",
        default="https://georivo.com/sitemap.xml",
    )
    parser.add_argument(
        "--status-file",
        type=Path,
        default=Path("/var/www/blog.yas.ooo/data/georivo-gsc-status.json"),
    )
    parser.add_argument(
        "--inspect-url",
        action="append",
        dest="inspection_urls",
        help=(
            "Canonical URL to inspect. Repeat for multiple URLs. "
            "Defaults to Georivo's primary public product and collection URLs."
        ),
    )
    args = parser.parse_args()
    environment_urls = tuple(
        url.strip()
        for url in os.getenv("GSC_INSPECTION_URLS", "").split(",")
        if url.strip()
    )
    inspection_urls = tuple(args.inspection_urls or environment_urls)
    if not inspection_urls:
        inspection_urls = DEFAULT_INSPECTION_URLS
    sys.exit(
        submit(
            args.credentials,
            args.site_url,
            args.sitemap_url,
            args.status_file,
            inspection_urls,
        )
    )
