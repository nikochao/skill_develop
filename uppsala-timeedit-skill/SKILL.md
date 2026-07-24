---
name: uppsala-timeedit-calendar
summary: Generate a Uppsala TimeEdit calendar subscription URL from a Ladok screenshot using local Python scripts.
---

# Skill: Uppsala TimeEdit Calendar

## Purpose

This Skill orchestrates a local workflow to:

1. Read a Ladok screenshot.
2. Extract semester and course details.
3. Confirm low-confidence detections with the user.
4. Run Playwright-based TimeEdit automation.
5. Return a calendar subscription URL and Google Calendar instructions.

## Safety and privacy rules

- Never ask for username or password.
- Never automate MFA.
- Never expose cookies or tokens.
- Keep all execution local.

## Required runtime

- Python 3.12+
- Playwright + Chromium
- Pydantic

## Orchestration contract

The Skill coordinates scripts in this order:

1. `scripts/extract_courses.py`
2. `scripts/search_timeedit.py`
3. `scripts/create_schedule.py`
4. `scripts/extract_subscription.py`

The Skill should pass structured JSON between scripts and request user confirmation when confidence is low.

## Output contract

Final response should include:

- Detected courses
- Unmatched courses
- Subscription URL
- Google Calendar subscription steps

## Non-goals

- No MCP server in v1
- No backend API
- No database
- No cloud deployment
