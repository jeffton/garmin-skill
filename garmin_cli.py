#!/usr/bin/env python3
"""
Garmin Connect CLI wrapper for Clawdbot skill.
Usage: python3 garmin_cli.py <command> [args]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

GARMIN_LIB_PATH = os.environ.get('GARMIN_LIB_PATH', '')
if GARMIN_LIB_PATH:
    sys.path.insert(0, GARMIN_LIB_PATH)

try:
    from garminconnect import Garmin
except ImportError:
    Garmin = None

CONFIG_DIR = os.path.expanduser('~/.config/garmin')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'credentials.json')

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return None

def save_credentials(email, password):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump({'email': email, 'password': password}, f)
    os.chmod(CREDENTIALS_FILE, 0o600)

def get_client():
    creds = load_credentials()
    if not creds:
        return None, "No credentials. Run: garmin_cli.py login <email> <password>"
    
    client = Garmin(creds['email'], creds['password'])
    try:
        client.login()
        return client, None
    except Exception as e:
        return None, str(e)

def format_duration(seconds):
    if seconds is None:
        return "N/A"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m}m"

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
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        today = datetime.now().strftime('%Y-%m-%d')
        data = client.get_user_summary(today)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_activities(days=7):
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now()
        activities = []
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            day_acts = client.get_activities_by_date(date, date)
            activities.extend(day_acts)
        return {"status": "success", "activities": activities[:50]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_steps(days=1):
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now()
        data = []
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            day_data = client.get_steps_data(date)
            data.append({"date": date, "steps": day_data})
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_sleep(date=None):
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        sleep_data = client.get_sleep_data(date)
        result = {"date": date}
        result.update(parse_sleep_data(sleep_data))
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_summary():
    """Get comprehensive daily summary."""
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        user_summary = client.get_user_summary(today)
        sleep_data = client.get_sleep_data(yesterday)
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
            },
            "sleep": parse_sleep_data(sleep_data),
            "vo2_max": training_status.get("mostRecentVO2Max", {}).get("generic", {}).get("vo2MaxValue") if training_status else None,
        }
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Garmin Connect CLI")
    parser.add_argument("command", help="Command: login, status, today, activities, steps, sleep, summary")
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
    elif cmd == "today":
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
    elif cmd == "summary":
        result = cmd_summary()
    else:
        result = {"status": "error", "message": f"Unknown command: {cmd}"}

    print(json.dumps(result, default=str))

if __name__ == "__main__":
    main()
