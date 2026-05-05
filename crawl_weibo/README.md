# Weibo Crawling Utilities

This folder contains the scripts used to collect Weibo timelines, comments, and ranking lists for the opinion-dynamics experiments.

## Requirements

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Most crawling commands require a valid Weibo mobile cookie. Do not commit real cookies. Pass one through the environment:

```bash
export WEIBO_COOKIE='SUB=...'
```

PowerShell:

```powershell
$env:WEIBO_COOKIE="SUB=..."
```

## Scripts

Fetch a Weibo V influence rank list:

```bash
python crawl_weibo/fetch_weibo_rank.py --field-id 1034 --date 202604 --output crawl_weibo/data/weibo_rank_1034_202604.txt
```

Crawl timelines for users listed in `user_id_list.txt`:

```bash
python crawl_weibo/crawl_blogs.py
```

Crawl hot comments for a CSV export in `duplicates/<user_id>.csv`:

```bash
python crawl_weibo/get_comments.py 7582893032
```

The comment crawler writes JSON Lines to `comment/comment_<user_id>.json`.

## Data Hygiene

Generated crawl outputs, cookies, logs, and local caches are ignored by the root `.gitignore`. Review any generated data before publishing it.

## Vendored Crawler

`weiboSpider/` contains vendored third-party crawler code from the Weibo crawler ecosystem. Keep the upstream attribution and license information with the repository if this code is published.

Suggested citation for the vendored crawler:

```bibtex
@misc{weibospider2020,
  author = {Lei Chen, Zhengyang Song, schaepher, minami9, bluerthanever, MKSP2015, moqimoqidea, windlively, eggachecat, mtuwei, codermino, duangan1},
  title = {{Weibo Spider}},
  howpublished = {\url{https://github.com/dataabc/weiboSpider}},
  year = {2020}
}
```
