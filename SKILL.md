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
| `summary` | Comprehensive daily summary (sleep, steps, HR, body battery, VO2 max) |
| `activities [days]` | Recent activities |
| `steps [days]` | Step count |
| `sleep [date]` | Sleep data |

## Examples

```bash
# Check status
/root/clawd/skills/garmin/garmin_cli.py status

# Today's summary
/root/clawd/skills/garmin/garmin_cli.py today

# Comprehensive summary
/root/clawd/skills/garmin/garmin_cli.py summary

# Sleep data
/root/clawd/skills/garmin/garmin_cli.py sleep 2026-01-15

# JSON output (default)
/root/clawd/skills/garmin/garmin_cli.py summary

# Text output
/root/clawd/skills/garmin/garmin_cli.py --format text summary

# Aliases
/root/clawd/skills/garmin/garmin_cli.py daily   # same as today
/root/clawd/skills/garmin/garmin_cli.py stats   # same as summary
```

## Notes

- Requires Garmin Connect credentials
- API rate-limited
