"""Search and match courses in Uppsala TimeEdit."""

import asyncio
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, TimeoutError, async_playwright

SCHEDULE_URL = "https://cloud.timeedit.net/uu/web/wr_student/ri1Q4.html"
PROFILE_DIR = Path(__file__).resolve().parents[2] / ".timeedit-browser"
SEARCH_INPUT = 'input[name="fftext"]'
SEARCH_RESULTS = "#objectsearchresult .searchObject"


def read_request() -> dict[str, Any]:
    """Read and validate confirmed course data from standard input."""
    data = json.load(sys.stdin)
    courses = data.get("courses")
    if not isinstance(courses, list):
        raise ValueError("'courses' must be a list")

    for course in courses:
        if not isinstance(course, dict):
            raise ValueError("Each course must be an object")
        for field in ("course_code", "course_name", "instance_code"):
            if not isinstance(course.get(field), str) or not course[field].strip():
                raise ValueError(f"Each course needs a confirmed '{field}'")
        study_period = course.get("study_period")
        if not isinstance(study_period, dict):
            raise ValueError("Each course needs a confirmed 'study_period'")
        for field in ("start_date", "end_date"):
            try:
                date.fromisoformat(study_period[field])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Each course needs a valid '{field}' in YYYY-MM-DD format"
                ) from error

    return data


def matching_candidates(course: dict[str, Any], candidates: list[str]) -> list[str]:
    """Match TimeEdit's course-term-instance identifier exactly."""
    start = date.fromisoformat(course["study_period"]["start_date"])
    term = f"{'H' if start.month >= 7 else 'V'}{start.year % 100:02d}"
    identifier = re.compile(
        rf"^{re.escape(course['course_code'])}-{term}-"
        rf"{re.escape(course['instance_code'])}(?:[.,\s]|$)",
        re.IGNORECASE,
    )
    return [candidate for candidate in candidates if identifier.search(candidate)]


async def open_search_page(context: BrowserContext) -> Page:
    """Open TimeEdit and wait while the user completes login when required."""
    page = context.pages[0] if context.pages else await context.new_page()
    await page.goto(SCHEDULE_URL)
    search = page.locator(SEARCH_INPUT)

    try:
        await search.wait_for(timeout=30_000)
    except TimeoutError:
        print(
            "Complete Uppsala login and MFA in the Chromium window.",
            file=sys.stderr,
        )
        await page.wait_for_url(
            re.compile(r"^https://cloud\.timeedit\.net/uu/web(?:/.*)?$"),
            timeout=600_000,
        )
        await page.goto(SCHEDULE_URL)
        await search.wait_for(timeout=30_000)

    return page


async def search(page: Page, query: str) -> list[str]:
    """Submit one TimeEdit search and return its visible candidate labels."""
    result_box = page.locator("#objectsearchresult")
    previous = await result_box.inner_text()
    search_input = page.locator(SEARCH_INPUT)
    await search_input.fill(query)
    await search_input.press("Enter")

    try:
        await page.wait_for_function(
            """([selector, oldText]) => {
                const result = document.querySelector(selector);
                return result && result.innerText !== oldText;
            }""",
            arg=["#objectsearchresult", previous],
            timeout=5_000,
        )
    except TimeoutError:
        pass

    return [
        " ".join(text.split())
        for text in await page.locator(SEARCH_RESULTS).all_inner_texts()
        if text.strip()
    ]


async def search_courses(
    page: Page,
    courses: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Search confirmed courses without choosing ambiguous candidates."""
    matched: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    not_found: list[dict[str, Any]] = []

    for course in courses:
        candidates = await search(page, course["course_code"])
        if not candidates:
            candidates = await search(page, course["course_name"])
        exact_matches = matching_candidates(course, candidates)

        if len(exact_matches) == 1:
            matched.append({**course, "timeedit_match": exact_matches[0]})
        elif exact_matches:
            ambiguous.append({"course": course, "candidates": exact_matches})
        elif candidates:
            ambiguous.append({"course": course, "candidates": candidates})
        else:
            not_found.append(course)

    return {
        "matched_courses": matched,
        "ambiguous_courses": ambiguous,
        "not_found_courses": not_found,
    }


async def run() -> None:
    """Launch a local persistent browser and emit search results as JSON."""
    request = read_request()
    async with async_playwright() as playwright:
        context = await playwright.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
        )
        try:
            page = await open_search_page(context)
            result = await search_courses(page, request["courses"])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            await context.close()


def main() -> None:
    """Run the async TimeEdit search workflow."""
    try:
        asyncio.run(run())
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
