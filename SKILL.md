---
name: garmin
description: Fetch Garmin Connect health and fitness data (activities, sleep, heart rate, training stats). Use when you need Garmin Connect metrics.
license: MIT
compatibility: Python 3.8+ with garminconnect; requires Garmin Connect account and network access.
metadata:
  homepage: https://github.com/jeffton/garmin-skill
  emoji: "⌚"
  version: 0.3.0
  tags:
    - health
    - fitness
    - garmin
    - wearable
---

# garmin

Fetch personal health and fitness data from Garmin Connect.

## Setup

```bash
# Login once
./garmin_cli.py login <email> <password>
```

## Commands

All commands output JSON. Arguments are positional: `activities 1` not `activities --days 1`.

| Command | Description |
|---------|-------------|
| `login <email> <password>` | Login to Garmin Connect |
| `status` | Check login status |
| `summary` | Comprehensive daily summary (sleep, HR, body battery, VO2 max, training metrics) |
| `activities [days]` | Recent activities (default: 7) |
| `sleep` | Sleep data with 7-day averages |
| `run [activity_id]` | Detailed run analysis with laps and comparison (default: latest run) |

## Examples

```bash
./garmin_cli.py status              # Check login
./garmin_cli.py summary             # Full daily summary
./garmin_cli.py activities 1        # Today's activities only
./garmin_cli.py sleep               # 7-day sleep with averages
./garmin_cli.py run                 # Latest run with lap analysis
./garmin_cli.py run 21647187521     # Specific run by activity ID
```

Full path: `/root/clawd/skills/garmin/garmin_cli.py`

## Credentials

Stored in `~/.config/garmin/credentials.json` (mode 600, plaintext).

## Environment

- `GARMIN_LIB_PATH` - Optional path to garminconnect library (if not in venv)
