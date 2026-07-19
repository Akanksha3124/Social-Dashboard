import csv
import json
import sys
from datetime import datetime
from pathlib import Path


OUTPUT_FIELDS = [
    "id",
    "title",
    "published_at",
    "views",
    "likes",
    "comments",
    "hour",
    "day_of_week",
    "month",
    "engagement_rate",
    "like_ratio",
    "platform",
]


ALIASES = {
    "id": ("id", "tweet_id", "post_id"),
    "title": ("text", "title", "content", "tweet_text", "full_text"),
    "published_at": ("created_at", "published_at", "timestamp", "date"),
    "views": ("views", "view_count", "impressions", "impression_count"),
    "likes": ("likes", "like_count", "favorite_count"),
    "comments": ("comments", "reply_count", "comment_count"),
}


class XquikExportError(ValueError):
    pass


def read_rows(path):
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise XquikExportError(f"{path} is empty.")
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as source:
            return [dict(row) for row in csv.DictReader(source)]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        rows = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise XquikExportError(
                    f"Invalid JSONL on line {line_number}: {exc.msg}."
                ) from exc
        return _object_rows(rows)
    if isinstance(parsed, dict):
        for key in ("data", "items", "results", "tweets"):
            value = parsed.get(key)
            if isinstance(value, list):
                return _object_rows(value)
        return [parsed]
    if isinstance(parsed, list):
        return _object_rows(parsed)
    raise XquikExportError("Expected CSV, JSON, or JSONL input.")


def normalize_rows(rows):
    clean_rows = []
    for index, row in enumerate(rows, start=1):
        normalized = {str(key).lower(): value for key, value in row.items()}
        title = str(_first(normalized, "title", "")).strip()
        if not title:
            continue
        published_at = _parse_datetime(_first(normalized, "published_at", ""))
        views = _positive_int(_first(normalized, "views", 0))
        likes = _positive_int(_first(normalized, "likes", 0))
        comments = _positive_int(_first(normalized, "comments", 0))
        safe_views = views if views > 0 else 1
        clean_rows.append(
            {
                "id": str(_first(normalized, "id", f"xquik_{index:05d}")),
                "title": title,
                "published_at": published_at.isoformat(),
                "views": str(views),
                "likes": str(likes),
                "comments": str(comments),
                "hour": str(published_at.hour),
                "day_of_week": published_at.strftime("%A"),
                "month": published_at.strftime("%B"),
                "engagement_rate": f"{((likes + comments) / safe_views):.4f}",
                "like_ratio": f"{(likes / safe_views):.4f}",
                "platform": "Xquik",
            }
        )
    if not clean_rows:
        raise XquikExportError("No rows with text content were found.")
    return clean_rows


def write_rows(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def convert_export(source_path, output_path):
    rows = normalize_rows(read_rows(source_path))
    write_rows(rows, output_path)
    return len(rows)


def _object_rows(rows):
    if not all(isinstance(row, dict) for row in rows):
        raise XquikExportError("Every input row must be an object.")
    return rows


def _first(row, field, default):
    for alias in ALIASES[field]:
        if alias in row and row[alias] not in ("", None):
            return row[alias]
    return default


def _parse_datetime(value):
    raw = str(value).strip()
    if not raw:
        return datetime(1970, 1, 1)
    for candidate in (raw, raw.replace("Z", "+00:00")):
        try:
            return datetime.fromisoformat(candidate).replace(tzinfo=None)
        except ValueError:
            continue
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, pattern)
        except ValueError:
            continue
    raise XquikExportError(f"Unsupported timestamp value: {raw}.")


def _positive_int(value):
    try:
        return max(0, int(float(str(value).replace(",", "").strip() or "0")))
    except ValueError as exc:
        raise XquikExportError(f"Expected a numeric metric, got {value!r}.") from exc


def main(argv):
    if len(argv) != 3:
        print(
            "Usage: python prepare_xquik_export.py <xquik-export> "
            "<data/cleaned/xquik_clean.csv>",
            file=sys.stderr,
        )
        return 2
    try:
        count = convert_export(Path(argv[1]), Path(argv[2]))
    except XquikExportError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Converted {count} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
