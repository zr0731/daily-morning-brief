from __future__ import annotations

import os
import time
from typing import Any

import requests

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
# 短暂不可用 / 限流时重试
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}


def chat(prompt: str, *, api_key: str | None = None, model: str | None = None) -> str:
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY")
    payload: dict[str, Any] = {
        "model": model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    attempts = int(os.environ.get("DEEPSEEK_RETRIES") or "4")
    last: requests.Response | None = None
    for i in range(attempts):
        last = requests.post(API_URL, json=payload, headers=headers, timeout=180)
        if last.status_code not in RETRY_STATUSES:
            last.raise_for_status()
            data = last.json()
            return data["choices"][0]["message"]["content"].strip()
        if i + 1 >= attempts:
            break
        # 2s, 4s, 8s …
        time.sleep(2 ** (i + 1))
    assert last is not None
    last.raise_for_status()
    raise RuntimeError(f"DeepSeek 失败: HTTP {last.status_code}")
