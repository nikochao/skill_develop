"""Extract and normalize TimeEdit calendar subscription URLs."""

import asyncio
import json
import sys
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import Page, TimeoutError, async_playwright

from search_timeedit import PROFILE_DIR

SUBSCRIBE_LINK = "Prenumerera"
PERIOD_SELECT = 'select[name="periodical"]'


def read_request() -> str:
    """Read and validate a generated TimeEdit schedule URL."""
    data = json.load(sys.stdin)
    schedule_url = data.get("schedule_url")
    if not isinstance(schedule_url, str):
        raise ValueError("'schedule_url' must be a string")
    parsed = urlparse(schedule_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "cloud.timeedit.net"
        or not parsed.path.startswith("/uu/web/wr_student/")
        or not parsed.path.endswith(".html")
    ):
        raise ValueError("'schedule_url' is not a Uppsala TimeEdit schedule")
    return schedule_url


def subscription_result(https_url: str) -> dict[str, Any]:
    """Normalize a TimeEdit HTTPS iCalendar URL."""
    parsed = urlparse(https_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "cloud.timeedit.net"
        or not parsed.path.endswith(".ics")
    ):
        raise ValueError("TimeEdit did not provide a valid HTTPS .ics URL")

    return {
        "subscription_url": parsed._replace(scheme="webcal").geturl(),
        "https_subscription_url": https_url,
        "google_calendar_url": None,
        "google_calendar_steps": [
            "Open Google Calendar in a desktop browser.",
            "Next to Other calendars, choose Add other calendars > From URL.",
            "Paste https_subscription_url and choose Add calendar.",
        ],
    }


async def open_subscription(page: Page, schedule_url: str) -> None:
    """Open a schedule and its subscription dialog, waiting for login if needed."""
    await page.goto(schedule_url)
    subscribe = page.get_by_role("link", name=SUBSCRIBE_LINK).first
    try:
        await subscribe.wait_for(timeout=30_000)
    except TimeoutError:
        print(
            "Complete Uppsala login and MFA in the Chromium window.",
            file=sys.stderr,
        )
        await page.wait_for_url(
            "https://cloud.timeedit.net/uu/web**",
            timeout=600_000,
        )
        await page.goto(schedule_url)
        await subscribe.wait_for(timeout=30_000)
    await subscribe.click()


async def extract_subscription(page: Page, schedule_url: str) -> dict[str, Any]:
    """Select the full schedule period and extract its subscription URL."""
    await open_subscription(page, schedule_url)
    period = page.locator(PERIOD_SELECT)
    await period.wait_for(timeout=10_000)
    option_count = await period.locator("option").count()
    if option_count == 0:
        raise ValueError("TimeEdit did not provide a subscription period")
    await period.select_option(index=option_count - 1)
    return subscription_result(await period.input_value())


async def run() -> None:
    """Launch TimeEdit and print normalized subscription data as JSON."""
    schedule_url = read_request()
    async with async_playwright() as playwright:
        context = await playwright.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
        )
        try:
            page = context.pages[0] if context.pages else await context.new_page()
            result = await extract_subscription(page, schedule_url)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            await context.close()


def main() -> None:
    """Run the async subscription extraction workflow."""
    try:
        asyncio.run(run())
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Unable to extract subscription: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
