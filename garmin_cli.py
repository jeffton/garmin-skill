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
        return {"status": "success", "data": sleep_data}
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
    else:
        result = {"status": "error", "message": f"Unknown command: {cmd}"}
    
    print(json.dumps(result, default=str))

if __name__ == '__main__':
    main()
