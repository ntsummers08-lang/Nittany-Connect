import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "research_events.py"
spec = importlib.util.spec_from_file_location("event_research", MODULE)
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)


class EventRadarTests(unittest.TestCase):
    def setUp(self):
        self.today = date.today()
        self.next_week = (self.today + timedelta(days=7)).isoformat()
        self.horizon = self.today + timedelta(days=45)

    def test_rejects_nonpublisher_urls(self):
        self.assertTrue(radar.host_allowed("https://cpa.psu.edu/events/example"))
        self.assertFalse(radar.host_allowed("https://psu.edu.bad-site.example/events"))
        self.assertFalse(radar.host_allowed("http://cpa.psu.edu/events/example"))
        self.assertFalse(radar.host_allowed("https://evil.example/events"))

    def test_rejects_missing_or_past_dates(self):
        sample = {"title": "Example only", "date": "2020-01-01",
                  "officialUrl": "https://cpa.psu.edu/events/example"}
        self.assertIsNone(radar.normalize(sample, self.today, self.horizon))
        sample["date"] = "no-date"
        self.assertIsNone(radar.normalize(sample, self.today, self.horizon))

    def test_candidates_need_review_and_tags_filtered(self):
        event = radar.normalize({
            "title": "Demo-only event",
            "date": self.next_week,
            "officialUrl": "https://cpa.psu.edu/events/demo-only",
            "tags": ["Music & Arts", "Invented Tag"],
            "startTime": "25:99",
        }, self.today, self.horizon)
        self.assertIsNotNone(event)
        self.assertFalse(event["verified"])
        self.assertIsNone(event["startTime"])
        self.assertEqual(event["tags"], ["Music & Arts"])

    def test_deduplication_key(self):
        a = {"title": "Campus Music Night!", "date": "2027-01-10"}
        b = {"title": "campus music night", "date": "2027-01-10"}
        self.assertEqual(radar.event_key(a), radar.event_key(b))


if __name__ == "__main__":
    unittest.main()
