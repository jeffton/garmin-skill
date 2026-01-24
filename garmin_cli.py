#!/usr/bin/env python3
"""Garmin Connect CLI wrapper for Clawdbot skill.

Outputs JSON by default (stable for scripting). Use `--format text` for a
human-friendly summary.

Examples:
  ./garmin_cli.py status
  ./garmin_cli.py summary
  ./garmin_cli.py --format text summary
  ./garmin_cli.py sleep 2026-01-17
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

GARMIN_LIB_PATH = os.environ.get("GARMIN_LIB_PATH", "")
if GARMIN_LIB_PATH:
    sys.path.insert(0, GARMIN_LIB_PATH)

try:
    from garminconnect import Garmin
except ImportError:
    Garmin = None

CONFIG_DIR = os.path.expanduser("~/.config/garmin")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.json")


def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None


def save_credentials(email, password):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as file:
        json.dump({"email": email, "password": password}, file)
    os.chmod(CREDENTIALS_FILE, 0o600)


def get_client():
    creds = load_credentials()
    if not creds:
        return None, f"No credentials. Run: garmin_cli.py login <email> <password> (stores in {CREDENTIALS_FILE})"

    client = Garmin(creds["email"], creds["password"])
    try:
        client.login()
        return client, None
    except Exception as exc:
        return None, str(exc)


def format_duration(seconds):
    if seconds is None:
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def parse_sleep_data(sleep_data):
    """Parse sleep data - used by both cmd_sleep and cmd_summary."""
    if not isinstance(sleep_data, dict):
        return {}

    daily = sleep_data.get("dailySleepDTO", {})

    result = {
        "total_seconds": daily.get("sleepTimeSeconds", 0),
        "total_formatted": format_duration(daily.get("sleepTimeSeconds")),
        "deep_seconds": daily.get("deepSleepSeconds", 0),
        "light_seconds": daily.get("lightSleepSeconds", 0),
        "rem_seconds": daily.get("remSleepSeconds", 0),
        "awake_seconds": daily.get("awakeSleepSeconds", 0),
        "resting_heart_rate": sleep_data.get("restingHeartRate"),
        "avg_overnight_hrv": sleep_data.get("avgOvernightHrv"),
        "hrv_status": sleep_data.get("hrvStatus"),
        "sleep_score": daily.get("sleepScores", {}).get("overall", {}).get("value"),
    }

    return result


def cmd_login(email, password):
    client = Garmin(email, password)
    try:
        client.login()
        save_credentials(email, password)
        return {"status": "success", "message": f"Logged in as {email}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_status():
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    return {"status": "success", "logged_in": True}


def cmd_today():
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        data = client.get_user_summary(today)
        return {"status": "success", "data": data}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_activities(days=7):
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now()
        activities = []
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            day_acts = client.get_activities_by_date(date, date)
            activities.extend(day_acts)
        return {"status": "success", "activities": activities[:50]}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_steps(days=1):
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now()
        data = []
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = client.get_steps_data(date)
            data.append({"date": date, "steps": day_data})
        return {"status": "success", "data": data}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_sleep(date=None):
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        sleep_data = client.get_sleep_data(date)
        result = {"date": date}
        result.update(parse_sleep_data(sleep_data))
        return {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_summary():
    """Get comprehensive daily summary."""
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        user_summary = client.get_user_summary(today)
        # Use today's sleep record so the score matches Garmin's "Sleep today" view.
        sleep_data = client.get_sleep_data(today)
        training_status = client.get_training_status(today)

        result = {
            "date": today,
            "steps": user_summary.get("totalSteps", 0),
            "distance_km": round(user_summary.get("totalDistanceMeters", 0) / 1000, 1),
            "calories": user_summary.get("totalKilocalories", 0),
            "heart_rate": {
                "resting": user_summary.get("restingHeartRate", 0),
                "max": user_summary.get("maxHeartRate", 0),
            },
            "body_battery": {
                "highest": user_summary.get("bodyBatteryHighestValue", 0),
                "lowest": user_summary.get("bodyBatteryLowestValue", 0),
                "most_recent": user_summary.get("bodyBatteryMostRecentValue"),
            },
            "sleep": parse_sleep_data(sleep_data),
            "vo2_max": (
                training_status.get("mostRecentVO2Max", {}).get("generic", {}).get("vo2MaxValue")
                if training_status
                else None
            ),
            "last_sync": user_summary.get("lastSyncTimestampGMT"),
        }

        return {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_sleep_week(days=7):
    """Get sleep data for the last N days (default 7) for weekly averages."""
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now()
        records = []

        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            try:
                sleep_data = client.get_sleep_data(date)
                parsed = parse_sleep_data(sleep_data)
                parsed["date"] = date

                # Also get body battery from daily summary
                try:
                    daily = client.get_user_summary(date)
                    parsed["body_battery_high"] = daily.get("bodyBatteryHighestValue")
                    parsed["body_battery_low"] = daily.get("bodyBatteryLowestValue")
                except Exception:
                    parsed["body_battery_high"] = None
                    parsed["body_battery_low"] = None

                records.append(parsed)
            except Exception:
                # Skip days with no data
                continue

        # Calculate averages (excluding None values)
        def avg(key):
            values = [r.get(key) for r in records if r.get(key) is not None]
            return round(sum(values) / len(values), 1) if values else None

        averages = {
            "sleep_score": avg("sleep_score"),
            "avg_overnight_hrv": avg("avg_overnight_hrv"),
            "body_battery_high": avg("body_battery_high"),
            "resting_heart_rate": avg("resting_heart_rate"),
            "days_with_data": len(records),
        }

        return {
            "status": "success",
            "data": {
                "records": records,
                "averages": averages,
            },
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def format_pace(seconds_per_km):
    """Convert seconds per km to MM:SS format."""
    if seconds_per_km is None or seconds_per_km <= 0:
        return "N/A"
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    return f"{minutes}:{seconds:02d}"


def cmd_run(activity_id=None):
    """Get detailed running activity with laps and comparison to recent runs."""
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        # If no activity_id, find the most recent running activity
        if activity_id is None:
            today = datetime.now()
            found = None
            for i in range(30):  # Look back 30 days
                date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                day_acts = client.get_activities_by_date(date, date)
                for act in day_acts:
                    if act.get("activityType", {}).get("typeKey") == "running":
                        found = act
                        break
                if found:
                    break
            if not found:
                return {"status": "error", "message": "No running activities found in last 30 days"}
            activity_id = found.get("activityId")
            activity = found
        else:
            # Fetch the specific activity
            activities = client.get_activities(0, 100)
            activity = next((a for a in activities if a.get("activityId") == activity_id), None)
            if not activity:
                return {"status": "error", "message": f"Activity {activity_id} not found"}

        # Get lap splits
        splits = client.get_activity_splits(activity_id)
        laps = []
        for lap in splits.get("lapDTOs", []):
            distance = lap.get("distance", 0)
            duration = lap.get("duration", 0)
            pace_sec = (duration / distance * 1000) if distance > 0 else 0
            laps.append({
                "lap": lap.get("lapIndex"),
                "distance_m": round(distance),
                "duration_sec": round(duration),
                "duration_formatted": format_duration(duration),
                "pace_sec_per_km": round(pace_sec, 1),
                "pace_formatted": format_pace(pace_sec),
                "avg_hr": lap.get("averageHR"),
                "max_hr": lap.get("maxHR"),
                "avg_power": lap.get("averagePower"),
                "cadence": round(lap.get("averageRunCadence", 0)),
                "elevation_gain": lap.get("elevationGain"),
            })

        # Get recent running activities for comparison
        recent_runs = []
        today = datetime.now()
        count = 0
        for i in range(60):  # Look back 60 days
            if count >= 5:
                break
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            day_acts = client.get_activities_by_date(date, date)
            for act in day_acts:
                if act.get("activityType", {}).get("typeKey") != "running":
                    continue
                if act.get("activityId") == activity_id:
                    continue  # Skip current activity
                dist = act.get("distance", 0)
                dur = act.get("duration", 0)
                pace = (dur / dist * 1000) if dist > 0 else 0
                recent_runs.append({
                    "date": act.get("startTimeLocal", "")[:10],
                    "name": act.get("activityName"),
                    "distance_km": round(dist / 1000, 2),
                    "duration_min": round(dur / 60, 1),
                    "pace_sec_per_km": round(pace, 1),
                    "pace_formatted": format_pace(pace),
                    "avg_hr": act.get("averageHR"),
                    "aerobic_te": round(act.get("aerobicTrainingEffect", 0), 1),
                    "vo2_max": act.get("vO2MaxValue"),
                })
                count += 1
                if count >= 5:
                    break

        # Build main activity data
        dist = activity.get("distance", 0)
        dur = activity.get("duration", 0)
        pace = (dur / dist * 1000) if dist > 0 else 0

        result = {
            "activity_id": activity_id,
            "name": activity.get("activityName"),
            "date": activity.get("startTimeLocal"),
            "distance_km": round(dist / 1000, 2),
            "duration_sec": round(dur),
            "duration_formatted": format_duration(dur),
            "pace_sec_per_km": round(pace, 1),
            "pace_formatted": format_pace(pace),
            "avg_hr": activity.get("averageHR"),
            "max_hr": activity.get("maxHR"),
            "calories": activity.get("calories"),
            "avg_power": activity.get("avgPower"),
            "cadence": round(activity.get("averageRunningCadenceInStepsPerMinute", 0)),
            "elevation_gain": activity.get("elevationGain"),
            "aerobic_te": round(activity.get("aerobicTrainingEffect", 0), 1),
            "anaerobic_te": round(activity.get("anaerobicTrainingEffect", 0), 1),
            "vo2_max": activity.get("vO2MaxValue"),
            "training_load": round(activity.get("activityTrainingLoad", 0), 1),
            "laps": laps,
            "recent_runs": recent_runs,
        }

        return {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def print_text(command: str, result: dict):
    status = result.get("status")
    if status != "success":
        print(result.get("message", "Error"))
        return

    if command in {"summary", "stats"}:
        data = result.get("data", {})
        hr = data.get("heart_rate", {})
        bb = data.get("body_battery", {})
        sleep = data.get("sleep", {})

        print(f"Dato: {data.get('date')}")
        print(f"Skridt: {data.get('steps')}")
        print(f"Distance: {data.get('distance_km')} km")
        print(f"Kalorier: {data.get('calories')}")
        print(f"Hvilepuls: {hr.get('resting')}")
        print(f"Max puls: {hr.get('max')}")
        print(f"Body Battery: {bb.get('lowest')} → {bb.get('highest')}")
        if sleep:
            print(f"Søvn: {sleep.get('total_formatted')} (score: {sleep.get('sleep_score')})")
        if data.get("vo2_max") is not None:
            print(f"VO2 max: {data.get('vo2_max')}")
        return

    if command == "sleep":
        data = result.get("data", {})
        print(f"Dato: {data.get('date')}")
        print(f"Søvn: {data.get('total_formatted')} (score: {data.get('sleep_score')})")
        if data.get("resting_heart_rate") is not None:
            print(f"Hvilepuls: {data.get('resting_heart_rate')}")
        if data.get("avg_overnight_hrv") is not None:
            print(f"HRV: {data.get('avg_overnight_hrv')} ({data.get('hrv_status')})")
        return

    if command == "status":
        print("OK: logged in")
        return

    if command == "steps":
        for row in result.get("data", []):
            print(f"{row.get('date')}: {row.get('steps')}")
        return

    if command == "activities":
        activities = result.get("activities", [])
        print(f"Aktiviteter: {len(activities)}")
        for act in activities[:10]:
            name = act.get("activityName") or act.get("activityType", {}).get("typeKey") or "Activity"
            start = act.get("startTimeLocal") or ""
            dist = act.get("distance")
            if dist is not None:
                dist = round(dist / 1000, 2)
                print(f"- {start}: {name} ({dist} km)")
            else:
                print(f"- {start}: {name}")
        return

    if command in {"today", "daily"}:
        data = result.get("data", {})
        print(f"Dato: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Skridt: {data.get('totalSteps')}")
        print(f"Distance: {round((data.get('totalDistanceMeters', 0) or 0) / 1000, 1)} km")
        print(f"Kalorier: {data.get('totalKilocalories')}")
        return

    if command == "run":
        data = result.get("data", {})
        print(f"🏃 {data.get('name')} — {data.get('date', '')[:10]}")
        print(f"Distance: {data.get('distance_km')} km")
        print(f"Tid: {data.get('duration_formatted')} (pace {data.get('pace_formatted')}/km)")
        print(f"Puls: {data.get('avg_hr')} snit / {data.get('max_hr')} max")
        print(f"VO2 Max: {data.get('vo2_max')} | Aerobic TE: {data.get('aerobic_te')}")
        print()

        laps = data.get("laps", [])
        if laps:
            print("Laps:")
            for lap in laps:
                dist_label = f"{lap['distance_m']}m" if lap['distance_m'] < 1000 else "1 km"
                print(f"  {lap['lap']}: {lap['duration_formatted']} ({lap['pace_formatted']}/km) | HR {lap['avg_hr']} | {lap.get('avg_power', '-')}W")
            print()

        recent = data.get("recent_runs", [])
        if recent:
            print("Seneste løb:")
            for run in recent:
                print(f"  {run['date']}: {run['distance_km']} km @ {run['pace_formatted']}/km | HR {run['avg_hr']} | VO2 {run['vo2_max']}")
        return

    print(json.dumps(result, ensure_ascii=False, default=str, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Garmin Connect CLI")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("command", help="Command: login, status, today, daily, activities, steps, sleep, sleep-week, run, summary, stats")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Command arguments")

    args = parser.parse_args()
    cmd = args.command

    if Garmin is None:
        result = {"status": "error", "message": "garminconnect not installed"}
    elif cmd == "login":
        if len(args.args) != 2:
            result = {"status": "error", "message": "Usage: login <email> <password>"}
        else:
            result = cmd_login(args.args[0], args.args[1])
    elif cmd == "status":
        result = cmd_status()
    elif cmd in {"today", "daily"}:
        result = cmd_today()
    elif cmd == "activities":
        days = int(args.args[0]) if args.args else 7
        result = cmd_activities(days)
    elif cmd == "steps":
        days = int(args.args[0]) if args.args else 1
        result = cmd_steps(days)
    elif cmd == "sleep":
        date = args.args[0] if args.args else None
        result = cmd_sleep(date)
    elif cmd == "sleep-week":
        days = int(args.args[0]) if args.args else 7
        result = cmd_sleep_week(days)
    elif cmd == "run":
        activity_id = int(args.args[0]) if args.args and not args.args[0].startswith("-") else None
        result = cmd_run(activity_id)
    elif cmd in {"summary", "stats"}:
        result = cmd_summary()
    else:
        result = {"status": "error", "message": f"Unknown command: {cmd}"}

    if args.format == "text":
        print_text(cmd, result)
    else:
        print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
