---
name: garmin
description: Fetch and display Garmin Connect data (activities, steps, sleep, heart rate, training load, VO2 max, and more).
homepage: https://github.com/cyberjunky/python-garminconnect
metadata: {"clawdbot":{"emoji":"⌚","version":"0.1.0","tags":["health","fitness","wearable","garmin"],"requires":{"bins":["python3","garmin_cli.py"]},"install":[{"id":"pip","kind":"pip","package":"garminconnect","label":"Install garminconnect (pip)"},{"id":"manual","kind":"manual","steps":["Copy garmin_cli.py to your path","Run: garmin_cli.py login <email> <password>"],"label":"Manual install"}]}}
---

# garmin

Fetch personal health and fitness data from Garmin Connect.

## Setup

1. Install the Garmin Connect library:
   ```bash
   pip install garminconnect
   ```

2. Login to Garmin Connect:
   ```bash
   ./garmin_cli.py login <email> <password>
   ```

   Or globally:
   ```bash
   sudo mv garmin_cli.py /usr/local/bin/garmin_cli.py
   garmin_cli.py login din@email.dk ditpassword
   ```

3. Credentials are stored in `~/.config/garmin/credentials.json`.

## Commands

| Command | Description |
|---------|-------------|
| `garmin_cli.py status` | Check if logged in |
| `garmin_cli.py today` | Get today's user summary |
| `garmin_cli.py daily` | Get daily stats (steps, HR, body battery) |
| `garmin_cli.py activities [days]` | Get activities (default: last 7 days) |
| `garmin_cli.py steps [days]` | Get step count (default: today) |
| `garmin_cli.py sleep [date]` | Get sleep data (YYYY-MM-DD, default: today) |
| `garmin_cli.py stats` | Get detailed stats (VO2 max, training load, etc.) |
| `garmin_cli.py summary` | Comprehensive daily summary (steps, sleep, HR, body battery, stress) |

## Examples

```bash
# Login
garmin_cli.py login din@email.dk ditpassword

# Check status
garmin_cli.py status

# Get today's summary
garmin_cli.py today

# Get last 14 days of activities
garmin_cli.py activities 14

# Get sleep data for specific date
garmin_cli.py sleep 2026-01-15

# Get detailed stats (VO2 max, training load, etc.)
garmin_cli.py stats

# Comprehensive daily summary
garmin_cli.py summary
```

## Data Available

- **Daily Summary**: Steps, distance, calories, floors, intensity minutes, body battery
- **Activities**: running, cycling, swimming, walking, etc.
- **Daily stats**: steps, distance, calories, floors
- **Heart rate**: resting HR, max HR, HRV, body battery
- **Sleep**: sleep duration, SpO2, HRV, resting heart rate
- **Training**: VO2 max, training load, training effect
- **Stress**: stress levels throughout the day, body battery

## Notes

- Requires Garmin Connect credentials (email + password).
- API may be rate-limited; avoid excessive requests.
- Credentials are stored in plain JSON; protect the file.
