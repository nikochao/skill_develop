"""Create semester schedule in TimeEdit from confirmed course selections."""

import asyncio
import json
import sys
from datetime import date
from typing import Any

from playwright.async_api import Page, async_playwright

from search_timeedit import (
    PROFILE_DIR,
    SCHEDULE_URL,
    SEARCH_RESULTS,
    open_search_page,
    search,
)


def read_request() -> list[dict[str, Any]]:
    """Read and validate uniquely matched TimeEdit courses."""
    data = json.load(sys.stdin)
    courses = data.get("matched_courses")
    if not isinstance(courses, list) or not courses:
        raise ValueError("'matched_courses' must be a non-empty list")

    for course in courses:
        if not isinstance(course, dict):
            raise ValueError("Each matched course must be an object")
        for field in ("course_code", "timeedit_match"):
            if not isinstance(course.get(field), str) or not course[field].strip():
                raise ValueError(f"Each matched course needs '{field}'")
        period = course.get("study_period")
        if not isinstance(period, dict):
            raise ValueError("Each matched course needs 'study_period'")
        for field in ("start_date", "end_date"):
            try:
                date.fromisoformat(period[field])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Each matched course needs a valid '{field}'"
                ) from error

    return courses


def schedule_range(courses: list[dict[str, Any]]) -> dict[str, str]:
    """Return the earliest start and latest end date."""
    return {
        "start_date": min(
            course["study_period"]["start_date"] for course in courses
        ),
        "end_date": max(course["study_period"]["end_date"] for course in courses),
    }


async def select_courses(page: Page, courses: list[dict[str, Any]]) -> None:
    """Search and add every uniquely matched course to TimeEdit's basket."""
    for course in courses:
        await search(page, course["course_code"])
        candidate = page.locator(SEARCH_RESULTS).filter(
            has_text=course["timeedit_match"]
        )
        if await candidate.count() != 1:
            raise ValueError(
                f"Expected one TimeEdit result for {course['course_code']}"
            )
        await candidate.click()

    selected = await page.locator("#objectbasket").inner_text()
    missing = [
        course["timeedit_match"].split(",", 1)[0]
        for course in courses
        if course["timeedit_match"].split(",", 1)[0] not in selected
    ]
    if missing:
        raise ValueError(f"Courses were not selected: {', '.join(missing)}")


async def create_schedule(
    page: Page,
    courses: list[dict[str, Any]],
) -> dict[str, Any]:
    """Select matched courses and generate their TimeEdit schedule."""
    await select_courses(page, courses)
    await page.get_by_text("Visa schema", exact=True).click()
    await page.wait_for_load_state("domcontentloaded")
    if page.url == SCHEDULE_URL:
        raise ValueError("TimeEdit did not generate a schedule")

    # ponytail: TimeEdit expands the selected term automatically; automate its
    # date panel only if a real schedule omits dates from this confirmed range.
    return {
        "selected_courses": courses,
        "date_range": schedule_range(courses),
        "schedule_url": page.url,
    }


async def run() -> None:
    """Launch TimeEdit and print the generated schedule as JSON."""
    courses = read_request()
    async with async_playwright() as playwright:
        context = await playwright.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
        )
        try:
            page = await open_search_page(context)
            result = await create_schedule(page, courses)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            await context.close()


def main() -> None:
    """Run the async schedule creation workflow."""
    try:
        asyncio.run(run())
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Unable to create schedule: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
