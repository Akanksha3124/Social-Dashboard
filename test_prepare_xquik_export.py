import csv
import json
import tempfile
import unittest
from pathlib import Path

from prepare_xquik_export import XquikExportError, convert_export, normalize_rows


class PrepareXquikExportTest(unittest.TestCase):
    def test_normalize_rows_maps_xquik_metrics(self):
        rows = normalize_rows(
            [
                {
                    "id": "tweet-1",
                    "created_at": "2026-07-04T09:30:00Z",
                    "text": "Launch notes",
                    "view_count": "100",
                    "like_count": "12",
                    "reply_count": "3",
                }
            ]
        )

        self.assertEqual(rows[0]["id"], "tweet-1")
        self.assertEqual(rows[0]["title"], "Launch notes")
        self.assertEqual(rows[0]["hour"], "9")
        self.assertEqual(rows[0]["day_of_week"], "Saturday")
        self.assertEqual(rows[0]["engagement_rate"], "0.1500")
        self.assertEqual(rows[0]["like_ratio"], "0.1200")
        self.assertEqual(rows[0]["platform"], "Xquik")

    def test_normalize_rows_rejects_bad_metrics(self):
        with self.assertRaisesRegex(XquikExportError, "Expected a numeric metric"):
            normalize_rows([{"text": "Bad metric", "views": "many"}])

    def test_convert_export_writes_clean_dashboard_csv(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            source = root / "xquik.jsonl"
            output = root / "data" / "cleaned" / "xquik_clean.csv"
            source.write_text(
                json.dumps(
                    {
                        "tweet_id": "tweet-2",
                        "created_at": "2026-07-05",
                        "tweet_text": "Second row",
                        "views": 50,
                        "likes": 5,
                        "comments": 1,
                    }
                ),
                encoding="utf-8",
            )

            count = convert_export(source, output)

            self.assertEqual(count, 1)
            with output.open(newline="", encoding="utf-8") as output_file:
                rows = list(csv.DictReader(output_file))
            self.assertEqual(rows[0]["id"], "tweet-2")
            self.assertEqual(rows[0]["month"], "July")


if __name__ == "__main__":
    unittest.main()
