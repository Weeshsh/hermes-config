---
name: icloud-calendar
description: Manage iCloud calendars through CalDAV.
version: 0.2.0
author: mikolaj, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [iCloud, Calendar, CalDAV, Automation]
    related_skills: []
---

# iCloud Calendar

Manage allowed iCloud calendars through the included CalDAV script. This skill
does not grant access to blocked calendars or bypass the configured write
restrictions. It requires Python with the `caldav` and `vobject` packages.

## When to Use

- List iCloud calendars.
- Read today's events.
- Search events.
- Create, update, or delete events in the configured write calendar.

Don't use for: accessing blocked calendars (klasa, praca) or writing to calendars other than the configured write calendar.

## Prerequisites

Install the Python dependencies:

```bash
pip install caldav vobject
```

Set these secrets in `~/.hermes/.env`:

```
ICLOUD_USERNAME=your@icloud.com
ICLOUD_PASSWORD=your_app_specific_password
```

Optionally set the writable calendar and blocked calendars:

```
ICLOUD_WRITE_CALENDAR=kalendarz agenta
ICLOUD_BLOCKED_CALENDARS=klasa,praca
```

The script uses the iCloud CalDAV endpoint: `https://caldav.icloud.com`

## How to Run

Use the `terminal` tool from the skill directory. The script requires `uv` to run:

```python
terminal(
    command="uv run --with caldav --with vobject python /home/mikolaj/Desktop/projekty/hermes/skills/icloud-calendar/scripts/connect-to-icloud.py <command>",
    timeout=30
)
```

## Quick Reference

```
list_calendars
today
list_events --calendar NAME --days N
create_event --calendar NAME --title TITLE --start ISO8601 --end ISO8601
search --query TEXT
update_event --calendar NAME --uid UID [--title TITLE] [--start ISO8601] [--end ISO8601]
delete_event --calendar NAME --uid UID
```

## Procedure

1. Confirm the requested calendar is not in the blocked set (`klasa`, `praca`).
2. Confirm write operations target `ICLOUD_WRITE_CALENDAR` only.
3. Invoke the script through `terminal` with `uv run`.
4. Return the JSON output without inventing fields or results.
5. For destructive operations (update, delete), show the target calendar, event title, and UID before execution.
6. Parse ISO8601 datetime strings using `datetime.fromisoformat()`.

## Pitfalls

- The script blocks calendars named `klasa` and `praca` — reads return empty.
- Writes are restricted to `ICLOUD_WRITE_CALENDAR` only; other calendars raise `PermissionError`.
- Missing credentials produce a JSON error and exit code 1.
- The script uses Europe/Warsaw timezone for all datetime conversions.
- Requires `vobject` package — without it, event parsing fails with `NoneType has no attribute 'vevent'`.

## Verification

```bash
uv run --with caldav --with vobject python /home/mikolaj/Desktop/projekty/hermes/skills/icloud-calendar/scripts/connect-to-icloud.py list_calendars
```

A successful check returns a JSON array of allowed calendars. It must not return:
- `Missing ICLOUD_USERNAME or ICLOUD_PASSWORD`
- `Failed to connect to iCloud`