---
name: garmin
description: Fetch Garmin Connect health and fitness data (activities, sleep, heart rate, steps, training stats). Use when you need Garmin Connect metrics.
license: MIT
compatibility: Python 3.8+ with garminconnect; requires Garmin Connect account and network access.
metadata:
  homepage: https://github.com/jeffton/garmin-skill
  emoji: "⌚"
  version: 0.1.1
  tags:
    - health
    - fitness
    - garmin
    - wearable
---

# garmin

Fetch personal health and fitness data from Garmin Connect.

## Install

```bash
pip install -r requirements.txt
```

Requires: Python 3.8+, garminconnect library.

## Setup

Login to Garmin Connect:
```bash
./garmin_cli.py login <email> <password>
```

Credentials stored in `~/.config/garmin/credentials.json`.

## Commands

| Command | Description |
|---------|-------------|
| `./garmin_cli.py status` | Check if logged in |
| `./garmin_cli.py today` | Get today's user summary |
| `./garmin_cli.py daily` | Get daily stats |
| `./garmin_cli.py activities [days]` | Get activities |
| `./garmin_cli.py steps [days]` | Get step count |
| `./garmin_cli.py sleep [date]` | Get sleep data |
| `./garmin_cli.py stats` | Get detailed stats |
| `./garmin_cli.py summary` | Comprehensive daily summary |

## Examples

```bash
# Login
./garmin_cli.py login din@email.dk ditpassword

# Check status
./garmin_cli.py status

# Today's summary
./garmin_cli.py today

# Sleep data
./garmin_cli.py sleep 2026-01-15

# Comprehensive summary
./garmin_cli.py summary
```

## Data Available

- **Daily**: Steps, distance, calories, floors, body battery
- **Sleep**: Duration, deep/light/REM, sleep score, HRV
- **Heart rate**: Resting, max, HRV, body battery
- **Activities**: Running, cycling, swimming, etc.
- **Training**: VO2 max, training load
- **Stress**: Levels, body battery impact

## Notes

- Requires Garmin Connect credentials.
- API rate-limited; avoid spam.
- Protect credentials file.
- All commands output JSON.
