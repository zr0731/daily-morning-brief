from __future__ import annotations

import os
from typing import Any

import requests

API_URL = "https://www.pushplus.plus/send"


def push(title: str, content: str, *, template: str = "markdown") -> tuple[bool, str]:
    token = (os.environ.get("PUSHPLUS_TOKEN") or "").strip()
    if not token:
        return False, "缺少 PUSHPLUS_TOKEN"

    payload: dict[str, Any] = {
        "token": token,
        "title": title[:100],
        "content": content,
        "template": template,
        "channel": "wechat",
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=60)
        data = r.json() if r.content else {}
        code = data.get("code")
        if r.ok and code == 200:
            return True, f"pushplus ok msgId={data.get('data')}"
        return False, f"HTTP {r.status_code} code={code} msg={data.get('msg') or r.text[:200]}"
    except requests.RequestException as e:
        return False, str(e)
