# Social-Dashboard
A Python-based social media analytics dashboard that collects, cleans, and visualizes YouTube engagement data. Features automated data pipelines, EDA notebooks, heatmaps, charts, SQLite integration, and an interactive HTML dashboard for performance analysis.

## Xquik Export Prep

Use `prepare_xquik_export.py` to convert Xquik CSV, JSON, or JSONL tweet
exports into the cleaned dashboard schema:

```bash
python prepare_xquik_export.py xquik-export.jsonl data/cleaned/xquik_clean.csv
```

The converter maps text, timestamp, view, like, and comment fields, derives
hour, day, month, engagement rate, and like ratio columns, and skips rows
without text content.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

Validate the converter with:

```bash
python test_prepare_xquik_export.py
```
