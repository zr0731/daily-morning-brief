from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .bark_client import push as bark_push
from .deepseek_client import chat

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
ARCHIVE = ROOT / "archive"
FEEDBACK = ROOT / "feedback"

TASKS = [
    ("task1_game_ideas.md", "壹｜游戏创意"),
    ("task2_parable.md", "贰｜概念寓言"),
    ("task3_business.md", "叁｜商业故事"),
]

CST = timezone(timedelta(hours=8))


def today_cst() -> date:
    return datetime.now(CST).date()


def load_prompt(name: str, today: date, yesterday_feedback: str) -> str:
    text = (PROMPTS / name).read_text(encoding="utf-8")
    text = text.replace("{{TODAY}}", today.isoformat())
    if "{{YESTERDAY_FEEDBACK}}" in text:
        block = yesterday_feedback.strip() or "（暂无昨日反馈，按通用偏好自由发挥。）"
        text = text.replace("{{YESTERDAY_FEEDBACK}}", block)
    # strip markdown title lines for cleaner LLM input? keep full file as instructions
    return text


def read_yesterday_feedback(today: date) -> str:
    yesterday = today - timedelta(days=1)
    path = FEEDBACK / f"{yesterday.isoformat()}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    # also accept pending.md manually maintained
    pending = FEEDBACK / "pending.md"
    if pending.exists():
        content = pending.read_text(encoding="utf-8").strip()
        if content:
            return content
    return ""


def ensure_feedback_stub(today: date, repo_web: str | None) -> Path:
    path = FEEDBACK / f"{today.isoformat()}.md"
    if not path.exists():
        tpl = (FEEDBACK / "_template.md").read_text(encoding="utf-8")
        path.write_text(tpl.replace("{{DATE}}", today.isoformat()), encoding="utf-8")
    return path


def build_newspaper(today: date, sections: list[tuple[str, str]]) -> str:
    lines = [
        f"# 晨间简报 · {today.isoformat()}",
        "",
        "---",
        "",
    ]
    for title, body in sections:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def bark_body_from_markdown(md: str) -> str:
    """Bark 正文长度有限：保留结构，略压缩空行。"""
    text = re.sub(r"\n{3,}", "\n\n", md)
    # remove leading # title duplication in push
    return text.strip()


def feedback_edit_url(repo_web: str | None, today: date) -> str | None:
    if not repo_web:
        return None
    base = repo_web.rstrip("/")
    # GitHub web editor deep link
    return f"{base}/edit/main/feedback/{today.isoformat()}.md"


def run(*, dry_run: bool = False) -> Path:
    today = today_cst()
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    FEEDBACK.mkdir(parents=True, exist_ok=True)

    yesterday_fb = read_yesterday_feedback(today)
    ensure_feedback_stub(today, os.environ.get("REPO_WEB_URL"))

    sections: list[tuple[str, str]] = []
    for filename, title in TASKS:
        prompt = load_prompt(filename, today, yesterday_fb if "task1" in filename else "")
        if dry_run:
            body = f"[dry-run] 将请求 DeepSeek，prompt 长度 {len(prompt)}"
        else:
            body = chat(prompt)
        sections.append((title, body))

    newspaper = build_newspaper(today, sections)
    out = ARCHIVE / f"{today.isoformat()}.md"
    out.write_text(newspaper, encoding="utf-8")

    repo_web = os.environ.get("REPO_WEB_URL")
    edit_url = feedback_edit_url(repo_web, today)
    archive_url = None
    if repo_web:
        archive_url = f"{repo_web.rstrip('/')}/blob/main/archive/{today.isoformat()}.md"

    # Bark 有长度限制：推「导读 + 链接」，完整报纸在 archive/
    digest_parts = [f"晨间简报 {today.isoformat()}", ""]
    for title_sec, body in sections:
        digest_parts.append(f"【{title_sec}】")
        snippet = re.sub(r"\s+", " ", body.strip())[:280]
        digest_parts.append(snippet + ("…" if len(body.strip()) > 280 else ""))
        digest_parts.append("")
    digest_parts.append("——")
    if archive_url:
        digest_parts.append(f"读全文（报纸）：{archive_url}")
    if edit_url:
        digest_parts.append(f"给游戏创意打分：{edit_url}")
    else:
        digest_parts.append(f"打分文件：feedback/{today.isoformat()}.md")
    push_body = "\n".join(digest_parts)
    title = f"晨间简报 {today.isoformat()}"
    if dry_run:
        print(newspaper)
        print("--- bark digest ---")
        print(push_body)
        print("[dry-run] skip bark")
    else:
        # 点通知先打开报纸全文；打分链接在正文内
        ok, detail = bark_push(title, push_body, url=archive_url or edit_url)
        print("bark:", ok, detail)

    print("archived:", out)
    return out


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    run(dry_run=os.environ.get("DRY_RUN") == "1")
