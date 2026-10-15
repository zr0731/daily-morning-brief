from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .deepseek_client import chat
from .pushplus_client import push as pushplus_push

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
    return text


def read_yesterday_feedback(today: date) -> str:
    yesterday = today - timedelta(days=1)
    path = FEEDBACK / f"{yesterday.isoformat()}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
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


def build_push_content(today: date, newspaper: str) -> str:
    footer = (
        "\n\n---\n"
        f"任务一打分：请在电脑打开仓库 `feedback/{today.isoformat()}.md` 填写后提交"
        "（次日生成会读昨日反馈）。\n"
    )
    return newspaper.rstrip() + footer


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

    title = f"晨间简报 {today.isoformat()}"
    push_content = build_push_content(today, newspaper)

    if dry_run:
        print(newspaper)
        print("--- pushplus preview chars ---", len(push_content))
        print("[dry-run] skip pushplus")
    else:
        # 单条过长时按栏目拆成多条，避免微信侧截断
        max_chars = int(os.environ.get("PUSHPLUS_MAX_CHARS") or "18000")
        if len(push_content) <= max_chars:
            ok, detail = pushplus_push(title, push_content)
            print("pushplus:", ok, detail)
        else:
            for sec_title, body in sections:
                part = f"# {title}\n\n## {sec_title}\n\n{body.strip()}\n"
                ok, detail = pushplus_push(f"{title} · {sec_title}", part)
                print("pushplus:", sec_title, ok, detail)

    print("archived:", out)
    return out


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    run(dry_run=os.environ.get("DRY_RUN") == "1")
