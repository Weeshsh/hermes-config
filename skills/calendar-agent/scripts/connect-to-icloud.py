import os
import sys
import json
import argparse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Any, Optional
import caldav

ICLOUD_CALDAV_URL = "https://caldav.icloud.com"
WRITE_CALENDAR_NAME = os.getenv("ICLOUD_WRITE_CALENDAR", "kalendarz agenta")

blocked_calendars = {"klasa", "praca"}


TZ_UTC2 = ZoneInfo("Europe/Warsaw")


def to_utc2(dt: Any) -> Any:
    if dt is None or not isinstance(dt, datetime):
        return dt
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ_UTC2)
    return dt.astimezone(TZ_UTC2)


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
            start = datetime.now(TZ_UTC2).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
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
            start_val = vevent.dtstart.value if hasattr(vevent, "dtstart") else None
            end_val = vevent.dtend.value if hasattr(vevent, "dtend") else None

            if start_val is not None:
                start_val = to_utc2(start_val).isoformat()
            if end_val is not None:
                end_val = to_utc2(end_val).isoformat()

            return {
                "title": str(vevent.summary.value)
                if hasattr(vevent, "summary")
                else "No title",
                "start": start_val,
                "end": end_val,
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
            start = to_utc2(start)
            end = to_utc2(end)
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
                start = datetime.now(TZ_UTC2) - timedelta(days=365)
                end = datetime.now(TZ_UTC2) + timedelta(days=365)
                for event in cal.date_search(start, end):
                    data = self._parse_event(event, cal_name)
                    if query.lower() in data.get("title", "").lower():
                        result.append(data)
            except Exception:
                pass
        return result

    def update_event(
        self,
        calendar_name: str,
        event_uid: str,
        title: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cal = self._get_calendar(calendar_name, require_write=True)
            search_start = datetime.now() - timedelta(days=5)
            search_end = datetime.now() + timedelta(days=30)
            events = cal.date_search(start=search_start, end=search_end)

            event = next(
                (e for e in events if str(e.instance.vevent.uid.value) == event_uid),
                None,
            )

            if not event:
                return {
                    "success": False,
                    "error": f"Event with UID '{event_uid}' not found in calendar '{calendar_name}'",
                }

            vevent = event.instance.vevent
            updated = False

            if title is not None:
                vevent.summary.value = title
                updated = True
            if start is not None:
                vevent.dtstart.value = to_utc2(start)
                updated = True
            if end is not None:
                vevent.dtend.value = to_utc2(end)
                updated = True
            if location is not None:
                vevent.location.value = location
                updated = True
            if description is not None:
                vevent.description.value = description
                updated = True

            if not updated:
                return {"success": False, "error": "No fields provided for update"}

            event.save()
            return {
                "success": True,
                "message": f"Event '{event_uid}' updated in '{calendar_name}'",
            }
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_event(self, calendar_name: str, event_uid: str) -> dict[str, Any]:
        try:
            cal = self._get_calendar(calendar_name, require_write=True)

            start = datetime.now() - timedelta(days=5)
            end = datetime.now() + timedelta(days=30)
            events = cal.date_search(start=start, end=end)

            event = next(
                (e for e in events if str(e.instance.vevent.uid.value) == event_uid),
                None,
            )

            if not event:
                return {
                    "success": False,
                    "error": f"Event with UID '{event_uid}' not found in calendar '{calendar_name}'",
                }

            # Delete the fresh instance
            event.delete()

            return {
                "success": True,
                "message": f"Event '{event_uid}' deleted from '{calendar_name}'",
            }
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error: {str(e)}"}


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

    ue = subparsers.add_parser("update_event")
    ue.add_argument("--calendar", required=True)
    ue.add_argument("--uid", required=True)
    ue.add_argument("--title")
    ue.add_argument("--start")
    ue.add_argument("--end")

    de = subparsers.add_parser("delete_event")
    de.add_argument("--calendar", required=True)
    de.add_argument("--uid", required=True)

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
        elif args.command == "update_event":
            start_dt = datetime.fromisoformat(args.start) if args.start else None
            end_dt = datetime.fromisoformat(args.end) if args.end else None
            result = gk.update_event(
                args.calendar,
                args.uid,
                title=args.title,
                start=start_dt,
                end=end_dt,
            )
        elif args.command == "delete_event":
            result = gk.delete_event(args.calendar, args.uid)
        else:
            result = {"error": f"Unknown command: {args.command}"}

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()
