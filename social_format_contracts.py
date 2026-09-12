"""Immutable editorial contracts for YAS social formats.

Formats are deliberately mutually exclusive. A blog insight can never be
silently promoted to a vacancy case, and a vacancy case cannot fall back to a
generic article visual.
"""

VACANCY_EVIDENCE_CASE = "vacancy_evidence_case"
BLOG_INSIGHT = "blog_insight"
CONTRACT_VERSION = "yas-x-formats-2026-08-30"

CONTRACTS = {
    VACANCY_EVIDENCE_CASE: {
        "label": "Vacancy evidence case",
        "source_kind": "evidence_case",
        "requires": ("evidenceCaseId", "sourceUrl", "companyName", "companyLogo", "economics"),
        "visual": "verified employer logo, concrete problem hook, bespoke system, human decision gate, fully labelled illustrative hours and base-pay capacity",
    },
    BLOG_INSIGHT: {
        "label": "Blog insight",
        "source_kind": "content_job",
        "requires": ("sourceJobId",),
        "visual": "article-specific mechanism illustration; no employer logo or time/money claim unless the article itself supplies verified evidence",
    },
}


def make_contract_metadata(content_format, **values):
    if content_format not in CONTRACTS:
        raise ValueError("Unsupported social format")
    payload = {"format": content_format, "contractVersion": CONTRACT_VERSION, **values}
    missing = [key for key in CONTRACTS[content_format]["requires"] if not payload.get(key)]
    if missing:
        raise ValueError(f"{content_format} requires: {', '.join(missing)}")
    return payload
