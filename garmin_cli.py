#!/usr/bin/env python3
"""Garmin Connect CLI wrapper for OpenClaw skill.

Examples:
  ./garmin_cli.py status
  ./garmin_cli.py summary
  ./garmin_cli.py sleep
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


def _simplify_phrase(phrase: str | None):
    """Convert Garmin feedback phrase identifiers into a nicer label."""
    if not phrase:
        return None
    # Examples: PRODUCTIVE_2, UNPRODUCTIVE, MAINTAINING
    base = phrase.split("_")[0]
    return base.replace("-", "_").replace(" ", "_").title().replace("_", " ")


def parse_training_status(training_status: dict | None):
    """Parse training status & training load from get_training_status()."""
    if not isinstance(training_status, dict):
        return {"training_status": None, "training_load": None}

    status_block = (training_status.get("mostRecentTrainingStatus") or {}).get("latestTrainingStatusData") or {}
    # The dict is keyed by deviceId; pick the first (primary device in practice).
    device_payload = next(iter(status_block.values()), None)

    training_status_out = None
    training_load_out = None

    if isinstance(device_payload, dict):
        phrase = device_payload.get("trainingStatusFeedbackPhrase")
        since_date = device_payload.get("sinceDate")
        training_status_out = {
            "phrase": phrase,
            "label": _simplify_phrase(phrase),
            "since_date": since_date,
            "sport": device_payload.get("sport"),
        }

        acute = device_payload.get("acuteTrainingLoadDTO") or {}
        if isinstance(acute, dict) and acute:
            training_load_out = {
                "acute_load": acute.get("dailyTrainingLoadAcute"),
                "chronic_load": acute.get("dailyTrainingLoadChronic"),
                "target_min": acute.get("minTrainingLoadChronic"),
                "target_max": acute.get("maxTrainingLoadChronic"),
                "ratio": acute.get("dailyAcuteChronicWorkloadRatio"),
                "acwr_percent": acute.get("acwrPercent"),
                "acwr_status": acute.get("acwrStatus"),
            }

    return {
        "training_status": training_status_out,
        "training_load": training_load_out,
    }


def parse_training_readiness(training_readiness: object):
    """Parse get_training_readiness() output (usually a list with one element)."""
    if isinstance(training_readiness, list) and training_readiness:
        item = training_readiness[0]
    elif isinstance(training_readiness, dict):
        item = training_readiness
    else:
        return None

    if not isinstance(item, dict):
        return None

    return {
        "score": item.get("score"),
        "level": item.get("level"),
        "timestamp_local": item.get("timestampLocal"),
        "sleep_score": item.get("sleepScore"),
        "recovery_time_min": item.get("recoveryTime"),
        "acute_load": item.get("acuteLoad"),
        "feedback_short": item.get("feedbackShort"),
    }


def parse_weekly_intensity_minutes(weekly: object, week_start: str, week_end: str):
    """Parse weekly intensity minutes aggregates."""
    if not isinstance(weekly, list) or not weekly:
        return None

    # Choose the latest week aggregate returned.
    item = weekly[-1]
    if not isinstance(item, dict):
        return None

    moderate = item.get("moderateValue")
    vigorous = item.get("vigorousValue")
    total = None
    if moderate is not None and vigorous is not None:
        # Garmin counts vigorous minutes double.
        total = int(moderate) + int(vigorous) * 2

    return {
        "week_start": item.get("calendarDate") or week_start,
        "week_end": week_end,
        "goal": item.get("weeklyGoal"),
        "moderate": moderate,
        "vigorous": vigorous,
        "total": total,
    }


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

        training_status_raw = None
        training_readiness_raw = None
        weekly_intensity_raw = None

        try:
            training_status_raw = client.get_training_status(today)
        except Exception:
            training_status_raw = None

        try:
            training_readiness_raw = client.get_training_readiness(today)
        except Exception:
            training_readiness_raw = None

        # Weekly intensity minutes (current week)
        try:
            dt_today = datetime.now()
            week_start_dt = dt_today - timedelta(days=dt_today.weekday())  # Monday
            week_start = week_start_dt.strftime("%Y-%m-%d")
            week_end = dt_today.strftime("%Y-%m-%d")
            weekly_intensity_raw = client.get_weekly_intensity_minutes(week_start, week_end)
        except Exception:
            week_start = None
            week_end = None
            weekly_intensity_raw = None

        ts_parsed = parse_training_status(training_status_raw)

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
            "stress": {
                "average": user_summary.get("averageStressLevel"),
                "qualifier": user_summary.get("stressQualifier"),
            },
            "sleep": parse_sleep_data(sleep_data),
            "vo2_max": (
                (training_status_raw or {}).get("mostRecentVO2Max", {}).get("generic", {}).get("vo2MaxValue")
                if training_status_raw
                else None
            ),
            "training_status": ts_parsed.get("training_status"),
            "training_load": ts_parsed.get("training_load"),
            "training_readiness": parse_training_readiness(training_readiness_raw),
            "intensity_minutes": (
                parse_weekly_intensity_minutes(weekly_intensity_raw, week_start or "", week_end or "")
                if week_start and week_end
                else None
            ),
            "last_sync": user_summary.get("lastSyncTimestampGMT"),
        }

        return {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def cmd_sleep():
    """Get sleep data for the last N days (default 7) for weekly averages."""
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now()
        records = []

        for i in range(7):
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



def main():
    parser = argparse.ArgumentParser(description="Garmin Connect CLI")
    parser.add_argument("command", help="Command: login, status, activities, sleep, run, summary")
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
    elif cmd == "activities":
        days = int(args.args[0]) if args.args else 7
        result = cmd_activities(days)
    elif cmd == "sleep":
        result = cmd_sleep()
    elif cmd == "run":
        activity_id = int(args.args[0]) if args.args and not args.args[0].startswith("-") else None
        result = cmd_run(activity_id)
    elif cmd == "summary":
        result = cmd_summary()
    else:
        result = {"status": "error", "message": f"Unknown command: {cmd}"}

    print(json.dumps(result, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
