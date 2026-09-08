"""Focused tests for accurate calendar alignment and safe generated SVGs."""

from datetime import date, timedelta
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

SPEC = importlib.util.spec_from_file_location("activity", Path(__file__).resolve().parents[1] / "scripts/update_activity.py")
activity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(activity)


def fixture():
    start = date(2026, 1, 1)  # Thursday: a partial first week must retain its row.
    days = [{"date": (start + timedelta(days=i)).isoformat(),
             "weekday": (start + timedelta(days=i)).isoweekday() % 7,
             "contributionCount": 2 if i == 0 else 0,
             "contributionLevel": "SECOND_QUARTILE" if i == 0 else "NONE"}
            for i in range(10)]
    return {"username": "shrawaniGawade", "date": "2026-01-10", "repositories": 3,
            "stars": 5, "languages": [("C<&\"", 2)],
            "calendar": {"totalContributions": 2, "weeks": [
                {"firstDay": "2026-01-01", "contributionDays": days[:3]},
                {"firstDay": "2026-01-04", "contributionDays": days[3:]},
            ]}}


class ActivityTests(unittest.TestCase):
    def test_mobile_preserves_every_desktop_date_count_across_bands(self):
        data = fixture()
        start = date(2025, 9, 9)
        days = [{"date": (start + timedelta(days=i)).isoformat(),
                 "weekday": (start + timedelta(days=i)).isoweekday() % 7,
                 "contributionCount": 1 if i % 9 == 0 else 0,
                 "contributionLevel": "FIRST_QUARTILE" if i % 9 == 0 else "NONE"}
                for i in range(365)]
        data["calendar"] = {"totalContributions": sum(day["contributionCount"] for day in days),
                            "weeks": [{"contributionDays": days}]}
        data["date"] = days[-1]["date"]
        def cells(content):
            return [node for node in ET.fromstring(content).iter() if "data-date" in node.attrib]
        desktop = cells(activity.garden_svg(data))
        mobile = cells(activity.garden_mobile_svg(data))
        self.assertEqual([(node.attrib["data-date"], node.attrib["data-count"]) for node in desktop],
                         [(node.attrib["data-date"], node.attrib["data-count"]) for node in mobile])
        self.assertEqual(len(mobile), 365)
        self.assertTrue(all(88 <= float(node.attrib["x"]) <= 530 for node in mobile))
        band_rows = {int((float(node.attrib["y"]) - 145) // 241) for node in mobile}
        self.assertEqual(band_rows, {0, 1, 2})

    def test_partial_week_uses_real_weekday_and_advances_on_sunday(self):
        root = ET.fromstring(activity.garden_svg(fixture()))
        cells = {node.attrib["data-date"]: node for node in root.iter() if "data-date" in node.attrib}
        first = cells["2026-01-01"]
        sunday = cells["2026-01-04"]
        self.assertEqual(float(first.attrib["y"]), 205.6)
        self.assertEqual(float(sunday.attrib["y"]), 140)
        self.assertGreater(float(sunday.attrib["x"]), float(first.attrib["x"]))
        self.assertEqual(len(cells), 10)
        self.assertEqual(sum(int(cell.attrib["data-count"]) for cell in cells.values()), 2)

    def test_dynamic_text_is_escaped_in_all_stats_variants(self):
        for mobile in (False, True):
            content = activity.stats_svg(fixture(), mobile)
            root = ET.fromstring(content)
            self.assertIn('C<&"', "".join(root.itertext()))
            self.assertNotIn("<script", content)

    def test_rejects_bad_weekday_missing_day_and_wrong_total(self):
        for mutation in ("weekday", "missing", "total"):
            data = fixture()["calendar"]
            if mutation == "weekday":
                data["weeks"][0]["contributionDays"][0]["weekday"] = 0
            elif mutation == "missing":
                data["weeks"][0]["contributionDays"].pop()
            else:
                data["totalContributions"] = 99
            with self.assertRaises(ValueError):
                activity.calendar_days(data)

    def test_invalid_output_does_not_replace_existing_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "stats.svg").write_text("original")
            with self.assertRaises(ET.ParseError):
                activity.write_outputs(target, {"stats.svg": "<svg/>", "bad.svg": "<svg>"})
            self.assertEqual((target / "stats.svg").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
