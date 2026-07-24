import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from search_timeedit import matching_candidates, read_request


class ReadRequestTest(unittest.TestCase):
    def test_reads_confirmed_courses(self) -> None:
        source = io.StringIO(
            '{"courses":[{"course_code":"1MD036","course_name":"Example",'
            '"instance_code":"11612","study_period":{'
            '"start_date":"2026-08-31","end_date":"2027-01-17"}}]}'
        )

        with patch("sys.stdin", source):
            request = read_request()

        self.assertEqual(request["courses"][0]["course_code"], "1MD036")

    def test_matches_course_term_and_instance(self) -> None:
        course = {
            "course_code": "1MD036",
            "instance_code": "11612",
            "study_period": {"start_date": "2026-08-31"},
        }
        candidates = [
            "1MD036-H25-11612, Previous instance",
            "1MD036-H26-11612, Requested instance",
        ]

        self.assertEqual(
            matching_candidates(course, candidates),
            ["1MD036-H26-11612, Requested instance"],
        )


if __name__ == "__main__":
    unittest.main()
