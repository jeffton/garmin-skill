---
name: garmin
description: Fetch Garmin Connect data - activities, sleep, heart rate, steps, training stats.
homepage: https://github.com/jeffton/garmin-skill
metadata:
  clawdbot:
    emoji: "⌚"
    version: "0.1.1"
    tags: ["health", "fitness", "garmin", "wearable"]
    requires:
      bins: ["python3", "garmin_cli.py"]
---

# garmin

Fetch personal health and fitness data from Garmin Connect.

## Install

```bash
pip install garminconnect
```

## Setup

1. Login to Garmin Connect:
   ```bash
   ./garmin_cli.py login <email> <password>
   ```

2. Credentials stored in `~/.config/garmin/credentials.json`
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
