from __future__ import annotations

import argparse
from pathlib import Path

import requests


API_URL = "https://v6.bang.weibo.com/aj/newczv/rank"
REFERER = "https://v6.bang.weibo.com/newczv/{field_id}?date={date}&sub_field_id=0&period_type={period_type}&choose_flag=1"


def fetch_rank(field_id: str, date: str, period_type: str, pages: int) -> list[dict]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
            ),
            "Referer": REFERER.format(field_id=field_id, date=date, period_type=period_type),
            "X-Requested-With": "XMLHttpRequest",
        }
    )

    rows: list[dict] = []
    seen: set[str] = set()
    for page in range(1, pages + 1):
        payload = {
            "field_id": field_id,
            "dt": date,
            "page": str(page),
            "show_rank": str((page - 1) * 20),
            "period_type": period_type,
            "lastRankData": "",
        }
        response = session.post(API_URL, data=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "100000":
            raise RuntimeError(f"API error on page {page}: {data}")

        for item in data.get("data", {}).get("rankData", []):
            uid = str(item["uid"])
            if uid in seen:
                continue
            seen.add(uid)
            rows.append(
                {
                    "screen_name": item["screen_name"],
                    "uid": uid,
                    "followers_count": int(item.get("followers_count") or 0),
                    "rank": int(item["rank"]),
                }
            )
    return rows


def write_txt(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as writer:
        for row in sorted(rows, key=lambda item: item["rank"]):
            writer.write(
                f"{row['screen_name']}\t{row['uid']}\t{row['followers_count']}\t{row['rank']}\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch a Weibo V influence rank list as txt.")
    parser.add_argument("--field-id", default="1034")
    parser.add_argument("--date", default="202604")
    parser.add_argument("--period-type", default="month")
    parser.add_argument("--pages", default=10, type=int)
    parser.add_argument("--output", default=Path("data/weibo_rank_1034_202604.txt"), type=Path)
    args = parser.parse_args()

    rows = fetch_rank(args.field_id, args.date, args.period_type, args.pages)
    write_txt(rows, args.output)
    print(f"Saved {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
