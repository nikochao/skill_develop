---
name: uppsala-timeedit-calendar
description: Read course names, codes, and study dates from a Ladok screenshot with AI vision, then generate a Uppsala TimeEdit calendar subscription URL. Use when a user provides a Ladok course screenshot or asks to create or subscribe to a Uppsala TimeEdit schedule.
---

# Uppsala TimeEdit Calendar

## Workflow

1. Inspect the attached Ladok screenshot directly with vision. If only a local path is provided, open that image with the available image-viewing tool. Do not run OCR.
2. Extract only text visibly supported by the screenshot into:

```json
{
  "semester": null,
  "courses": [
    {
      "course_code": "1AB123",
      "course_name": "Example course",
      "study_period": {
        "start_date": "2026-08-31",
        "end_date": "2027-01-17"
      }
    }
  ]
}
```

3. Use `null` for every unreadable or uncertain field. Never infer missing characters, dates, semester, or course codes.
4. Show the extracted data to the user and ask them to fill or correct all `null` or uncertain course fields. Continue after every course has a confirmed `course_code`, `course_name`, `start_date`, and `end_date`; `semester` may remain `null`.
5. Pass the confirmed JSON to `scripts/search_timeedit.py` on standard input.
6. If the search returns multiple matches, ask the user to choose. Never select an ambiguous match automatically.
7. Pass confirmed matches through `scripts/create_schedule.py`, then run `scripts/extract_subscription.py`.

## Semester normalization

- Normalize `Autumn YYYY` or `HT YYYY` to `Autumn YYYY`.
- Normalize `Spring YYYY` or `VT YYYY` to `Spring YYYY`.
- Use `null` when no semester label is visible. Do not derive a semester from study dates.

## Confirmation rules

- Preserve the spelling shown in the screenshot.
- Treat partially obscured, cropped, or visually ambiguous fields as `null`.
- If nothing is uncertain, continue without an extra confirmation step.
- If the image is unavailable or unreadable, ask the user to attach a clearer screenshot.

## Safety

- Never ask for a username, password, or MFA code.
- Never expose cookies or tokens.
- Keep execution local.

## Final response schema

Return `detected_courses`, `unmatched_courses`, `ambiguous_courses`, `subscription_url`, `https_subscription_url`, `google_calendar_url`, and short numbered `google_calendar_steps`.
