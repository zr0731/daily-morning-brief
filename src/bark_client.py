from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import requests


def push(
    title: str,
    body: str,
    *,
    url: str | None = None,
    group: str | None = None,
) -> tuple[bool, str]:
    server = (os.environ.get("BARK_SERVER") or "https://api.day.app").rstrip("/")
    key = os.environ.get("BARK_DEVICE_KEY") or ""
    if not key:
        return False, "缺少 BARK_DEVICE_KEY"

    group = group or os.environ.get("BARK_GROUP") or "每日简报"
    max_chars = int(os.environ.get("BARK_MAX_BODY_CHARS") or "3500")
    title = title[:120]
    body = body[:max_chars]

    payload: dict[str, Any] = {
        "title": title,
        "body": body,
        "group": group,
        "level": "active",
    }
    if url:
        payload["url"] = url

    endpoint = f"{server}/{key}"
    try:
        r = requests.post(endpoint, json=payload, timeout=30)
        if r.ok:
            return True, f"POST {endpoint} ok"
        # fallback GET
        path = f"{server}/{key}/{quote(title)}/{quote(body)}"
        r2 = requests.get(path, timeout=30)
        if r2.ok:
            return True, "GET fallback ok"
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except requests.RequestException as e:
        return False, str(e)
