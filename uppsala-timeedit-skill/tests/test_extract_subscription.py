import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from extract_subscription import subscription_result


class SubscriptionResultTest(unittest.TestCase):
    def test_normalizes_timeedit_url(self) -> None:
        https_url = (
            "https://cloud.timeedit.net/uu/web/wr_student/example.ics"
        )

        result = subscription_result(https_url)

        self.assertEqual(
            result["subscription_url"],
            "webcal://cloud.timeedit.net/uu/web/wr_student/example.ics",
        )
        self.assertEqual(result["https_subscription_url"], https_url)
        self.assertIsNone(result["google_calendar_url"])

    def test_rejects_missing_subscription_url(self) -> None:
        with self.assertRaises(ValueError):
            subscription_result("")


if __name__ == "__main__":
    unittest.main()
