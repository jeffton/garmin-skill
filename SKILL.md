---
name: garmin
description: Fetch Garmin Connect health and fitness data (activities, sleep, heart rate, steps, training stats). Use when you need Garmin Connect metrics.
license: MIT
compatibility: Python 3.8+ with garminconnect; requires Garmin Connect account and network access.
metadata:
  homepage: https://github.com/jeffton/garmin-skill
  emoji: "⌚"
  version: 0.2.0
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
/root/clawd/skills/garmin/garmin_cli.py login <email> <password>
```

## Commands

| Command | Description |
|---------|-------------|
| `status` | Check login status |
| `today` | Today's summary |
| `summary` | Comprehensive daily summary (sleep, steps, HR, body battery, VO2 max, training metrics) |
| `activities [days]` | Recent activities (default: 7 days) |
| `steps [days]` | Step count (default: 1 day) |
| `sleep [date]` | Sleep data for a specific date (default: today) |
| `sleep-week [days]` | Sleep data for last N days with weekly averages (default: 7) |
| `run [activity_id]` | Detailed running activity with laps and comparison |

**Note:** Arguments are positional (no flags). Example: `activities 1` not `activities --days 1`.

## Summary output

The `summary` command includes:
- Steps, distance, calories
- Heart rate (resting, max)
- Body battery (low → high)
- Sleep (hours, score)
- VO2 max
- **Training Status**: Productive/Unproductive + since date
- **Training Readiness**: Score 0-100 + level
- **Training Load**: Acute load, target range, ACWR ratio
- **Intensity Minutes**: Weekly total vs goal
- Last sync timestamp

## Run command

The `run` command provides detailed running analysis:
- Lap splits with pace, HR, power, cadence
- Comparison with last 5 running activities
- VO2 Max trend, training effect, training load

```bash
# Latest run
/root/clawd/skills/garmin/garmin_cli.py --format text run

# Specific activity
/root/clawd/skills/garmin/garmin_cli.py run 21647187521
```

## Examples

```bash
# Check status
garmin_cli.py status

# Today's activities only
garmin_cli.py activities 1

# Last 7 days activities (default)
garmin_cli.py activities

# Comprehensive summary (JSON)
garmin_cli.py summary

# Comprehensive summary (text)
garmin_cli.py --format text summary

# 7-day sleep with averages
garmin_cli.py sleep-week

# Latest running activity
garmin_cli.py --format text run
```

Full path: `/root/clawd/skills/garmin/garmin_cli.py`

## Notes

- Requires Garmin Connect credentials
- API rate-limited
- Sync timestamp shows when watch last synced
