import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from create_schedule import schedule_range


class ScheduleRangeTest(unittest.TestCase):
    def test_uses_earliest_start_and_latest_end(self) -> None:
        courses = [
            {
                "study_period": {
                    "start_date": "2026-08-31",
                    "end_date": "2026-11-01",
                }
            },
            {
                "study_period": {
                    "start_date": "2026-11-02",
                    "end_date": "2027-01-17",
                }
            },
        ]

        self.assertEqual(
            schedule_range(courses),
            {
                "start_date": "2026-08-31",
                "end_date": "2027-01-17",
            },
        )


if __name__ == "__main__":
    unittest.main()
