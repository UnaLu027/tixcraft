#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_URL = "https://tixcraft.com/activity/detail/26_dxs"


@dataclass
class Snapshot:
    digest: str
    text: str


def http_get(url: str, timeout: int = 10) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="ignore")


def http_post_json(url: str, payload: dict, timeout: int = 10) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout):  # noqa: S310
        return


def compact_text(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def make_snapshot(html: str) -> Snapshot:
    text = compact_text(html)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return Snapshot(digest=digest, text=text)


def looks_available(text: str) -> bool:
    positive = ["立即購票", "available", "buy", "選購", "購票"]
    negative = ["已售完", "sold out", "暫無票券", "coming soon"]
    if any(word in text for word in negative):
        return False
    return any(word in text for word in positive)


def notify(message: str, webhook_url: str | None) -> None:
    print(message)
    if webhook_url:
        http_post_json(webhook_url, {"content": message})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor ticket page changes.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Activity page URL")
    parser.add_argument("--interval", type=int, default=30, help="Polling interval seconds")
    parser.add_argument("--discord-webhook", default=os.getenv("DISCORD_WEBHOOK_URL"))
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    previous: Snapshot | None = None
    while True:
        try:
            html = http_get(args.url)
            current = make_snapshot(html)
            if previous and current.digest != previous.digest:
                notify(f"🔄 頁面內容有變化：{args.url}", args.discord_webhook)
            if looks_available(current.text):
                notify(f"🎟️ 可能有票了，請立刻確認：{args.url}", args.discord_webhook)
            previous = current
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"[WARN] 檢查失敗: {exc}", file=sys.stderr)
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
