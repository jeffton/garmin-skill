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
| `activities [days]` | Recent activities |
| `steps [days]` | Step count |
| `sleep [date]` | Sleep data for a specific date |
| `sleep-week [days]` | Sleep data for last N days with weekly averages |
| `run [activity_id]` | Detailed running activity with laps and comparison |

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
/root/clawd/skills/garmin/garmin_cli.py status

# Comprehensive summary (JSON)
/root/clawd/skills/garmin/garmin_cli.py summary

# Comprehensive summary (text)
/root/clawd/skills/garmin/garmin_cli.py --format text summary

# 7-day sleep with averages
/root/clawd/skills/garmin/garmin_cli.py sleep-week

# Latest running activity
/root/clawd/skills/garmin/garmin_cli.py --format text run
```

## Notes

- Requires Garmin Connect credentials
- API rate-limited
- Sync timestamp shows when watch last synced
