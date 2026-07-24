#!/usr/bin/env python3
"""Verify GSC access and submit a sitemap through the official API."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account


WEBMASTERS_API = "https://www.googleapis.com/webmasters/v3"
WEBMASTERS_SCOPE = "https://www.googleapis.com/auth/webmasters"
ALLOWED_PERMISSIONS = {"siteOwner", "siteFullUser"}
BLOCKED_EXIT = 75


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


def submit(credentials_path, site_url, sitemap_url, status_path):
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
    args = parser.parse_args()
    sys.exit(
        submit(
            args.credentials,
            args.site_url,
            args.sitemap_url,
            args.status_file,
        )
    )
