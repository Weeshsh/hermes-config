import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import caldav

ICLOUD_CALDAV_URL = "https://caldav.icloud.com"
WRITE_CALENDAR_NAME = os.getenv("ICLOUD_WRITE_CALENDAR", "kalendarz agenta")

blocked_calendars = {"klasa", "praca"}


class iCloudGatekeeper:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = None
        self.principal = None
        self.calendars = {}

    def connect(self) -> bool:
        try:
            self.client = caldav.DAVClient(
                url=ICLOUD_CALDAV_URL, username=self.username, password=self.password
            )
            self.principal = self.client.principal()
            self._load_calendars()
            return True
        except Exception:
            return False

    def _load_calendars(self):
        calendars = self.principal.calendars()
        self.calendars = {}
        for cal in calendars:
            name = cal.name or "Unnamed"
            self.calendars[name] = cal

    def list_calendars(self) -> list[dict[str, Any]]:
        result = []
        for name, cal in self.calendars.items():
            if name in blocked_calendars:
                continue
            result.append(
                {
                    "name": name,
                    "write_access": name == WRITE_CALENDAR_NAME,
                    "read_access": True,
                }
            )
        return result

    def _get_calendar(self, name: str, require_write: bool = False) -> Optional[Any]:
        if name in blocked_calendars or name not in self.calendars:
            return None
        if require_write and name != WRITE_CALENDAR_NAME:
            raise PermissionError(
                f"Write access denied for '{name}'. Only '{WRITE_CALENDAR_NAME}' allows writes."
            )
        return self.calendars[name]

    def list_events(
        self, calendar_name: Optional[str] = None, days: int = 7
    ) -> list[dict[str, Any]]:
        result = []
        if calendar_name:
            if calendar_name in blocked_calendars:
                return []
            cal = self._get_calendar(calendar_name)
            calendars_to_check = {calendar_name: cal} if cal else {}
        else:
            calendars_to_check = {
                name: cal
                for name, cal in self.calendars.items()
                if name not in blocked_calendars
            }

        for cal_name, cal in calendars_to_check.items():
            if not cal:
                continue
            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=days)

            try:
                events = cal.date_search(start, end)
                for event in events:
                    result.append(self._parse_event(event, cal_name))
            except Exception as e:
                result.append({"error": str(e), "calendar": cal_name})

        return sorted(result, key=lambda x: x.get("start", "") or "")

    def today(self) -> list[dict[str, Any]]:
        return self.list_events(days=1)

    def _parse_event(self, event, calendar_name: str) -> dict[str, Any]:
        try:
            vevent = event.instance.vevent
            return {
                "title": str(vevent.summary.value)
                if hasattr(vevent, "summary")
                else "No title",
                "start": vevent.dtstart.value.isoformat()
                if hasattr(vevent, "dtstart")
                else None,
                "end": vevent.dtend.value.isoformat()
                if hasattr(vevent, "dtend")
                else None,
                "calendar": calendar_name,
                "uid": str(vevent.uid.value) if hasattr(vevent, "uid") else None,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_event(
        self,
        calendar_name: str,
        title: str,
        start: datetime,
        end: datetime,
        location: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cal = self._get_calendar(calendar_name, require_write=True)
            cal.save_event(
                dtstart=start,
                dtend=end,
                summary=title,
                location=location,
                description=description,
            )
            return {
                "success": True,
                "message": f"Event '{title}' created in '{calendar_name}'",
            }
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search(self, query: str) -> list[dict[str, Any]]:
        result = []
        for cal_name, cal in self.calendars.items():
            if cal_name in blocked_calendars:
                continue
            try:
                start = datetime.now() - timedelta(days=365)
                end = datetime.now() + timedelta(days=365)
                for event in cal.date_search(start, end):
                    data = self._parse_event(event, cal_name)
                    if query.lower() in data.get("title", "").lower():
                        result.append(data)
            except Exception:
                pass
        return result


def main():
    parser = argparse.ArgumentParser(description="iCloud Calendar Gatekeeper")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list_calendars")
    subparsers.add_parser("today")

    le = subparsers.add_parser("list_events")
    le.add_argument("--calendar")
    le.add_argument("--days", type=int, default=7)

    ce = subparsers.add_parser("create_event")
    ce.add_argument("--calendar", required=True)
    ce.add_argument("--title", required=True)
    ce.add_argument("--start", required=True)
    ce.add_argument("--end", required=True)

    se = subparsers.add_parser("search")
    se.add_argument("--query", required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    username = os.getenv("ICLOUD_USERNAME")
    password = os.getenv("ICLOUD_PASSWORD")

    if not username or not password:
        print(json.dumps({"error": "Missing ICLOUD_USERNAME or ICLOUD_PASSWORD"}))
        sys.exit(1)

    gk = iCloudGatekeeper(username, password)
    if not gk.connect():
        print(json.dumps({"error": "Failed to connect to iCloud"}))
        sys.exit(1)

    try:
        if args.command == "list_calendars":
            result = gk.list_calendars()
        elif args.command == "list_events":
            result = gk.list_events(args.calendar, args.days)
        elif args.command == "today":
            result = gk.today()
        elif args.command == "create_event":
            result = gk.create_event(
                args.calendar,
                args.title,
                datetime.fromisoformat(args.start),
                datetime.fromisoformat(args.end),
            )
        elif args.command == "search":
            result = gk.search(args.query)
        else:
            result = {"error": f"Unknown command: {args.command}"}

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()
