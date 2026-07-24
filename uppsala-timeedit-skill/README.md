# Uppsala TimeEdit Skill

Local-first Codex Skill for generating a Uppsala TimeEdit calendar subscription URL from a Ladok screenshot.

## Scope (Phase 1)

This repository is scaffolded for a local workflow. No backend, database, or cloud service is required.

### Key constraints

- Local execution only.
- No paid services required.
- Never ask for Uppsala credentials.
- Never automate MFA.
- Python scripts perform browser automation; the Skill orchestrates the workflow.

## Planned workflow

1. Parse Ladok screenshot and extract semester + courses.
2. Ask user to confirm uncertain course detections.
3. Open TimeEdit with Playwright.
4. Search and add confirmed courses.
5. Generate timetable for semester.
6. Extract calendar subscription URL.
7. Return matches, mismatches, and Google Calendar instructions.

## Project structure

```text
uppsala-timeedit-skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   ├── extract_courses.py
│   ├── search_timeedit.py
│   ├── create_schedule.py
│   ├── extract_subscription.py
│   └── utils.py
├── references/
│   ├── selectors.md
│   └── ladok_examples/
└── tests/
```

## Local setup

1. Use Python 3.12+.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Notes

- The current editor environment is using Python 3.11; this repository targets 3.12+ for runtime.
- Selector details for TimeEdit should be documented in `references/selectors.md` before browser automation hardening.
