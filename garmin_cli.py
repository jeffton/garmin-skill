#!/usr/bin/env python3
"""
Garmin Connect CLI wrapper for Clawdbot skill.
Usage: python3 garmin_cli.py <command> [args]
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Allow override of garminconnect import path via env
GARMIN_LIB_PATH = os.environ.get('GARMIN_LIB_PATH', '')
if GARMIN_LIB_PATH:
    sys.path.insert(0, GARMIN_LIB_PATH)

from garminconnect import Garmin

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
        return None, "No credentials found. Run: garmin_cli.py login <email> <password>"
    
    client = Garmin(creds['email'], creds['password'])
    try:
        client.login()
        return client, None
    except Exception as e:
        return None, str(e)

def format_duration(seconds):
    """Convert seconds to human-readable format."""
    if seconds is None:
        return "N/A"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m}m"

def cmd_login(email, password):
    save_credentials(email, password)
    client = Garmin(email, password)
    try:
        client.login()
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
        
        # Parse comprehensive sleep data
        result = {"date": date}
        
        if isinstance(sleep_data, dict):
            daily = sleep_data.get("dailySleepDTO", {})
            
            # Duration breakdown
            result["total_seconds"] = daily.get("sleepTimeSeconds", 0)
            result["total_formatted"] = format_duration(result["total_seconds"])
            result["deep_seconds"] = daily.get("deepSleepSeconds", 0)
            result["light_seconds"] = daily.get("lightSleepSeconds", 0)
            result["rem_seconds"] = daily.get("remSleepSeconds", 0)
            result["awake_seconds"] = daily.get("awakeSleepSeconds", 0)
            result["nap_seconds"] = daily.get("napTimeSeconds", 0)
            
            # Percentages
            result["deep_percent"] = daily.get("deepPercentage")
            result["light_percent"] = daily.get("lightPercentage")
            result["rem_percent"] = daily.get("remPercentage")
            
            # Scores
            scores = daily.get("sleepScores", {})
            if scores:
                overall = scores.get("overall", {})
                result["sleep_score"] = overall.get("value")
                result["sleep_score_qualifier"] = overall.get("qualifierKey")
                
                result["score_duration"] = scores.get("totalDuration", {}).get("qualifierKey")
                result["score_stress"] = scores.get("stress", {}).get("qualifierKey")
                result["score_awake"] = scores.get("awakeCount", {}).get("qualifierKey")
                result["score_rem"] = scores.get("remPercentage", {}).get("qualifierKey")
                result["score_light"] = scores.get("lightPercentage", {}).get("qualifierKey")
                result["score_deep"] = scores.get("deepPercentage", {}).get("qualifierKey")
                result["score_restlessness"] = scores.get("restlessness", {}).get("qualifierKey")
            
            # Feedback/insights
            result["feedback"] = daily.get("sleepScoreFeedback")
            result["insight"] = daily.get("sleepScoreInsight")
            
            # HRV and physiology
            result["resting_heart_rate"] = sleep_data.get("restingHeartRate")
            result["avg_overnight_hrv"] = sleep_data.get("avgOvernightHrv")
            result["hrv_status"] = sleep_data.get("hrvStatus")
            result["avg_respiration"] = daily.get("averageRespirationValue")
            result["restless_moments"] = sleep_data.get("restlessMomentsCount")
            result["sleep_stress"] = daily.get("avgSleepStress")
            
            # Timestamps
            result["start_gmt"] = daily.get("sleepStartTimestampGMT")
            result["end_gmt"] = daily.get("sleepEndTimestampGMT")
            result["duration_confirmed"] = daily.get("sleepWindowConfirmed")
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_daily_stats():
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        stats = {
            "user_summary": client.get_user_summary(today),
            "steps": client.get_steps_data(today),
            "heart_rates": client.get_heart_rates(today),
        }
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_stats():
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        stats = {
            "user_profile": client.get_user_profile(),
            "stats": client.get_stats(today),
            "body_composition": client.get_body_composition(today),
            "vo2_max": client.get_vo2_max(today),
            "training_load": client.get_training_status(today),
        }
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_daily_summary():
    """Get comprehensive daily summary including sleep, steps, HR, body battery."""
    client, err = get_client()
    if err:
        return {"status": "error", "message": err}
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        user_summary = client.get_user_summary(today)
        steps_data = client.get_steps_data(today)
        heart_rates = client.get_heart_rates(today)
        
        # Get sleep from last night (if available)
        sleep_data = client.get_sleep_data(yesterday)
        
        result = {
            "date": today,
            "steps": user_summary.get("totalSteps", 0),
            "distance_meters": user_summary.get("totalDistanceMeters", 0),
            "calories": {
                "total": user_summary.get("totalKilocalories", 0),
                "active": user_summary.get("activeKilocalories", 0),
            },
            "heart_rate": {
                "resting": user_summary.get("restingHeartRate", 0),
                "min": user_summary.get("minHeartRate", 0),
                "max": user_summary.get("maxHeartRate", 0),
            },
            "sleep": {},
            "body_battery": {
                "highest": user_summary.get("bodyBatteryHighestValue", 0),
                "lowest": user_summary.get("bodyBatteryLowestValue", 0),
                "at_wake": user_summary.get("bodyBatteryAtWakeTime", 0),
            },
            "stress": {
                "average": user_summary.get("averageStressLevel", 0),
                "max": user_summary.get("maxStressLevel", 0),
            },
            "floors": {
                "ascended": user_summary.get("floorsAscendedInMeters", 0),
            },
            "intensity_minutes": {
                "moderate": user_summary.get("moderateIntensityMinutes", 0),
                "vigorous": user_summary.get("vigorousIntensityMinutes", 0),
            },
        }
        
        # Parse sleep data
        if sleep_data and isinstance(sleep_data, dict):
            start = sleep_data.get('startTimeGMT', '')
            end = sleep_data.get('endTimeGMT', '')
            if start and end:
                try:
                    s = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    e = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    total_sec = (e - s).total_seconds()
                    result["sleep"]["total_seconds"] = total_sec
                    result["sleep"]["formatted"] = f"{int(total_sec//3600)}h {int((total_sec%3600)//60)}m"
                except:
                    pass
            
            result["sleep"]["resting_heart_rate"] = sleep_data.get("restingHeartRate")
            result["sleep"]["avg_overnight_hrv"] = sleep_data.get("avgOvernightHrv")
            result["sleep"]["hrv_status"] = sleep_data.get("hrvStatus")
            result["sleep"]["avg_spo2"] = sleep_data.get("averageSpO2")
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: garmin_cli.py <command> [args]"}))
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'login':
        if len(sys.argv) != 4:
            print(json.dumps({"status": "error", "message": "Usage: garmin_cli.py login <email> <password>"}))
            sys.exit(1)
        result = cmd_login(sys.argv[2], sys.argv[3])
    elif cmd == 'status':
        result = cmd_status()
    elif cmd == 'today':
        result = cmd_today()
    elif cmd == 'activities':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        result = cmd_activities(days)
    elif cmd == 'steps':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        result = cmd_steps(days)
    elif cmd == 'sleep':
        date = sys.argv[2] if len(sys.argv) > 2 else None
        result = cmd_sleep(date)
    elif cmd == 'daily':
        result = cmd_daily_stats()
    elif cmd == 'stats':
        result = cmd_stats()
    elif cmd == 'summary':
        result = cmd_daily_summary()
    else:
        result = {"status": "error", "message": f"Unknown command: {cmd}"}
    
    print(json.dumps(result, default=str))

if __name__ == '__main__':
    main()
