from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from weiboSpider.weibo_spider.spider import Spider


def last_crawl_date(user_id: str, output_dir: Path = Path("weibo")) -> str:
    csv_path = output_dir / f"{user_id}.csv"
    if not csv_path.exists():
        return "now"

    lines = [line for line in csv_path.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) <= 1:
        return "now"
    return lines[-1].split(",")[6].split()[0]


def crawl_blogs(user_id: str, *, cookie: str | None = None) -> None:
    cookie_value = cookie or os.getenv("WEIBO_COOKIE")
    if not cookie_value:
        raise ValueError("Weibo cookie is required. Set WEIBO_COOKIE or pass cookie.")

    config_path = PROJECT_ROOT / "weiboSpider" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config.update(
        {
            "cookie": cookie_value,
            "user_id_list": [user_id],
            "write_mode": ["csv"],
            "end_date": last_crawl_date(user_id),
        }
    )
    Spider(config).start()


def iter_user_ids(path: Path = Path("user_id_list.txt")) -> list[str]:
    return [
        line.split()[1]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


if __name__ == "__main__":
    for uid in iter_user_ids():
        print(uid)
        crawl_blogs(user_id=uid)
