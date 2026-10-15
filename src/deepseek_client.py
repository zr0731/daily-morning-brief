from __future__ import annotations

import os
import time
from typing import Any

import requests

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
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
    last_err = "unknown"
    for i in range(attempts):
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=180)
        if resp.status_code in RETRY_STATUSES:
            last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
            if i + 1 < attempts:
                time.sleep(2 ** (i + 1))
                continue
            resp.raise_for_status()

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            last_err = f"{e}; body={resp.text[:300]}"
            raise requests.HTTPError(last_err, response=resp) from e

        data = resp.json()
        choices = data.get("choices")
        if choices:
            return choices[0]["message"]["content"].strip()

        # 偶发 200 但无 choices（网关异常 JSON）→ 重试
        last_err = f"响应无 choices: {str(data)[:300]}"
        if i + 1 < attempts:
            time.sleep(2 ** (i + 1))
            continue
        raise RuntimeError(last_err)

    raise RuntimeError(last_err)
