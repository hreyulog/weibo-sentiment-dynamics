# Weibo Opinion Dynamics

Research code and supporting data workflows for the paper:

> Yulong He, Anton V. Proskurnikov, and Artem Sedakov. *Opinion Dynamics Models for Sentiment Evolution in Weibo Blogs*. arXiv:2511.15303, 2025.

This repository collects scripts used to crawl Weibo posts and comments, score Chinese-language sentiment, aggregate sentiment trajectories, and fit opinion-dynamics models for Weibo blogger communities.

## Repository Layout

```text
.
├── crawl_weibo/                     # Weibo crawling utilities and vendored weiboSpider code
├── sentiment_analysis/              # Sentiment model experiments and evaluation scripts
│   ├── bert/                        # BERT-based sentiment experiments
│   ├── bilstm/                      # BiLSTM sentiment training
│   └── naivebayes/                  # Naive Bayes/SnowNLP baselines and datasets
├── opinion_dynamics_mathematica/    # Mathematica notebooks for model fitting and evaluation
├── sentiment.py                     # Apply trained sentiment models to crawled posts/comments
├── get_weighted_avg.py              # Aggregate comment sentiment into time-series values
├── list_bozhu.txt                   # Blogger list used by the aggregation scripts
└── requirements.txt                 # Python dependencies
```

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Some experiments require local model artifacts that are not committed to the repository, such as fine-tuned BERT checkpoints or Weibo word vectors. Set paths through environment variables when needed:

```bash
export WEIBO_SENTIMENT_BERT_PATH=sentiment_analysis/bert_sentiment2
export WEIBO_COOKIE='SUB=...'
```

PowerShell:

```powershell
$env:WEIBO_SENTIMENT_BERT_PATH="sentiment_analysis/bert_sentiment2"
$env:WEIBO_COOKIE="SUB=..."
```

The fine-tuned sentiment BERT model used for this project is available on Hugging Face:

- Model: [hreyulog/weibo-opinion-dynamic-sentiment-bert](https://huggingface.co/hreyulog/weibo-opinion-dynamic-sentiment-bert)

## Typical Workflow

1. Fetch or prepare a list of Weibo users.

```bash
python crawl_weibo/fetch_weibo_rank.py --field-id 1034 --date 202604 --output crawl_weibo/data/weibo_rank_1034_202604.txt
```

2. Crawl blogger timelines with a valid Weibo mobile cookie.

```bash
python crawl_weibo/crawl_blogs.py
```

3. Crawl hot comments for exported Weibo CSV files.

```bash
python crawl_weibo/get_comments.py 7582893032
```

4. Score post and comment sentiment with the trained sentiment model.

```bash
python sentiment.py
```

5. Aggregate sentiment evolution by half-month time bins.

```bash
python get_weighted_avg.py
```

6. Fit and evaluate opinion-dynamics models using the Mathematica notebooks in `opinion_dynamics_mathematica/`.

## Data And Privacy

The dataset for the paper is available on Hugging Face:

- Dataset: [hreyulog/weibo-opinion-dynamic-single-dim](https://huggingface.co/datasets/hreyulog/weibo-opinion-dynamic-single-dim)

The repository may contain small example datasets used for reproducibility. Fresh crawl outputs, cookies, logs, downloaded media, and local model checkpoints are intentionally ignored by `.gitignore`.

Before publishing a derived dataset, verify that it complies with Weibo's terms of service, privacy expectations, and your institution's data-sharing policy.

## Citation

If this code or data workflow helps your research, please cite:

```bibtex
@article{He2026Mapping,
  author  = {He, Yulong and Proskurnikov, Anton V. and Sedakov, Artem},
  title   = {Mapping sentiment dependencies among online influencer communities on {Weibo}},
  journal = {Social Network Analysis and Mining},
  year    = {2026},
  month   = sep,
  doi     = {10.1007/s13278-026-01645-w},
  url     = {https://doi.org/10.1007/s13278-026-01645-w},
  issn    = {1869-5469}
}
```

This repository also vendors Weibo crawling code from `dataabc/weiboSpider`. Please cite it when using the crawling component:

```bibtex
@misc{weibospider2020,
  author = {Lei Chen, Zhengyang Song, schaepher, minami9, bluerthanever, MKSP2015, moqimoqidea, windlively, eggachecat, mtuwei, codermino, duangan1},
  title = {{Weibo Spider}},
  howpublished = {\url{https://github.com/dataabc/weiboSpider}},
  year = {2020}
}
```

## Notes

- `crawl_weibo/weiboSpider/` is vendored third-party crawler code from the Weibo crawler ecosystem. Keep its original license and attribution if you publish the repository.
- Weibo endpoints and cookies can expire or throttle requests. Refresh `WEIBO_COOKIE` when requests start returning empty results or login errors.
- Mathematica notebooks are kept as the source of the opinion-dynamics fitting workflow.
