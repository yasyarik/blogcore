from __future__ import annotations

import os
import re
import subprocess
import threading
import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")
_alert_lock = threading.Lock()
_last_alert_at: dict[str, float] = {}


def _profile(hint: str | None) -> tuple[str, str]:
    normalized = (hint or "").lower()
    if "georivo" in normalized or "georivo.com" in normalized:
        return "GEORIVO", "Georivo"
    return "", "Blog core"


def _value(*names: str) -> str:
    for name in names:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return ""


def gemini_keys(hint: str | None = None) -> tuple[str, str, str]:
    suffix, label = _profile(hint)
    if suffix:
        primary = _value(f"GEMINI_API_KEY_{suffix}", f"GOOGLE_API_KEY_{suffix}")
        fallback = _value(
            f"GEMINI_API_KEY_{suffix}_FALLBACK",
            f"GOOGLE_API_KEY_{suffix}_FALLBACK",
            "GEMINI_API_KEY_FALLBACK",
            "GOOGLE_API_KEY_FALLBACK",
        )
    else:
        primary = _value("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_TEXT_API_KEY")
        fallback = _value("GEMINI_API_KEY_FALLBACK", "GOOGLE_API_KEY_FALLBACK")
    return primary, fallback, label


def _retryable(error: BaseException) -> bool:
    status = getattr(error, "code", None) or getattr(error, "status_code", None)
    if status in {401, 403, 408, 429, 500, 502, 503, 504}:
        return True
    message = str(error).lower()
    if re.search(r"\b(?:401|403|408|429|500|502|503|504)\b", message):
        return True
    return any(token in message for token in (
        "api key not valid", "invalid api key", "permission_denied", "quota",
        "resource_exhausted", "billing", "rate limit", "timed out", "timeout",
        "temporarily unavailable", "connection reset", "connection refused", "network is unreachable",
    ))


def _safe_error(error: BaseException) -> str:
    message = re.sub(r"(?:AQ\.|AIza)[A-Za-z0-9._-]+", "[redacted-key]", str(error))
    return " ".join(message.split())[:1200]


def _send_alert(profile: str, operation: str, error: BaseException) -> None:
    recipient = (os.environ.get("GEMINI_FAILOVER_ALERT_EMAIL") or "").strip()
    if not recipient:
        return
    cooldown = max(1, int(os.environ.get("GEMINI_FAILOVER_ALERT_COOLDOWN_MINUTES", "60") or 60)) * 60
    now = time.time()
    with _alert_lock:
        if now - _last_alert_at.get(profile, 0.0) < cooldown:
            return
        _last_alert_at[profile] = now
    sender = (os.environ.get("PUBLICATION_ALERT_EMAIL_FROM") or "AiRep24 <info@airep24.com>").strip()
    subject = f"[{profile}] Gemini primary key failed - fallback activated"
    message = (
        f"To: {recipient}\nFrom: {sender}\nSubject: {subject}\n"
        "Content-Type: text/plain; charset=UTF-8\n\n"
        f"{profile} switched one Gemini request to the configured fallback key.\n\n"
        f"Operation: {operation}\nError: {_safe_error(error)}\n\n"
        "No API keys are included in this message. The next request will try the primary key again.\n"
    )
    try:
        subprocess.run(
            ["/usr/sbin/sendmail", "-t"], input=message.encode("utf-8"), timeout=15,
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def call_with_gemini_failover(operation: str, hint: str | None, callback: Callable[[str], T]) -> T:
    primary, fallback, profile = gemini_keys(hint)
    if not primary:
        raise RuntimeError(f"Gemini API key is not configured for {profile}")
    try:
        return callback(primary)
    except Exception as error:
        if not fallback or fallback == primary or not _retryable(error):
            raise
        _send_alert(profile, operation, error)
        return callback(fallback)
