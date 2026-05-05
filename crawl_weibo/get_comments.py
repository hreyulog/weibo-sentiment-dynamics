from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path

import requests


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
)


def read_posts(input_csv: Path) -> dict[str, dict[str, str]]:
    posts: dict[str, dict[str, str]] = {}
    with input_csv.open("r", encoding="utf-8", newline="") as handle:
        csv_reader = csv.DictReader(handle)
        for row in csv_reader:
            post_id = row.get("weibo_id") or row.get("微博id")
            if not post_id:
                continue
            posts[post_id] = {
                "content": row.get("content") or row.get("微博正文") or "",
                "time": row.get("time") or row.get("发布时间") or "",
                "likes": row.get("likes") or row.get("点赞数") or "0",
                "comments_num": row.get("comments_num") or row.get("评论数") or "0",
            }
    return posts


def existing_post_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()

    ids: set[str] = set()
    with output_path.open("r", encoding="utf-8") as reader:
        for row in reader:
            if not row.strip():
                continue
            json_obj = json.loads(row)
            ids.add(str(json_obj.get("post_id") or json_obj.get("id")))
    return ids


def crawl_post_comments(post_id: str, headers: dict[str, str], *, timeout: int = 20) -> list[dict]:
    comments: list[dict] = []
    page = 1
    max_id = ""
    tag_re = re.compile(r"<[^>]+>", re.S)

    while True:
        if page == 1:
            url = f"https://m.weibo.cn/comments/hotflow?id={post_id}&mid={post_id}&max_id_type=0"
        else:
            if max_id == "0":
                break
            url = (
                f"https://m.weibo.cn/comments/hotflow?id={post_id}&mid={post_id}"
                f"&max_id_type=0&max_id={max_id}"
            )

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("ok") == 0:
            break

        data = payload.get("data", {})
        for item in data.get("data", []):
            comments.append(
                {
                    "id": item["user"]["id"],
                    "comment": tag_re.sub("", item.get("text", "")),
                    "time": item.get("created_at", ""),
                    "likes": item.get("like_count", 0),
                }
            )
        page += 1
        max_id = str(data.get("max_id", "0"))

    return comments


def get_comments(
    user_id: str,
    *,
    input_dir: Path = Path("duplicates"),
    output_dir: Path = Path("comment"),
    cookie: str | None = None,
) -> None:
    cookie_value = cookie or os.getenv("WEIBO_COOKIE")
    if not cookie_value:
        raise ValueError("Weibo cookie is required. Set WEIBO_COOKIE or pass --cookie.")

    input_csv = input_dir / f"{user_id}.csv"
    output_path = output_dir / f"comment_{user_id}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    posts = read_posts(input_csv)
    seen_ids = existing_post_ids(output_path)
    headers = {"User-Agent": USER_AGENT, "cookie": cookie_value}

    with output_path.open("a+", encoding="utf-8", newline="\n") as writer:
        for post_id, post in posts.items():
            if post_id in seen_ids:
                continue
            print(post_id)
            comments = crawl_post_comments(post_id, headers)
            writer.write(
                json.dumps(
                    {
                        "post_id": post_id,
                        "user_id": user_id,
                        "content": post["content"],
                        "time": post["time"],
                        "likes": post["likes"],
                        "source_comments_num": post["comments_num"],
                        "crawled_comments_num": len(comments),
                        "comments": comments,
                    },
                    ensure_ascii=False,
                )
            )
            writer.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl hot comments for Weibo CSV exports.")
    parser.add_argument("user_ids", nargs="+", help="User IDs, or CSV filenames whose stem is the user ID.")
    parser.add_argument("--input-dir", default=Path("duplicates"), type=Path)
    parser.add_argument("--output-dir", default=Path("comment"), type=Path)
    parser.add_argument("--cookie", default=None, help="Weibo mobile cookie. Defaults to WEIBO_COOKIE.")
    args = parser.parse_args()

    for user in args.user_ids:
        user_id = Path(user).stem
        print(user_id)
        get_comments(user_id, input_dir=args.input_dir, output_dir=args.output_dir, cookie=args.cookie)


if __name__ == "__main__":
    main()
