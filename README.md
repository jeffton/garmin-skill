# Garmin Skill for Clawdbot

Fetch and display Garmin Connect data from your personal health and fitness dashboard.

This skill is designed to be published to ClawdHub: it keeps local environment
artifacts (like `venv/`) out of git and ships only the CLI + docs.

## Features

- **Daily Summary**: Steps, calories, distance, heart rate, stress, body battery
- **Activities**: Running, cycling, swimming, and more with detailed stats
- **Sleep Data**: Sleep duration and quality metrics
- **Training Stats**: VO2 max, training load, training effect
- **Heart Rate**: Resting HR, HRV, and continuous monitoring

## Installation

### Option 1: ClawdHub (Recommended)

Browse and install from https://clawdhub.com

### Option 2: Manual Install

```bash
# Clone/download this repo
git clone https://github.com/jeffton/garmin-skill.git
cd garmin-skill

# Install dependencies (recommended: in a virtualenv)
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Make executable
chmod +x garmin_cli.py

# Login to Garmin Connect
./garmin_cli.py login your@email.com yourpassword
```

## Usage

```bash
# Check login status
./garmin_cli.py status

# Today's summary (alias: daily)
./garmin_cli.py today
./garmin_cli.py daily

# Comprehensive daily summary (alias: stats)
./garmin_cli.py summary
./garmin_cli.py stats

# Last 7 days of activities
./garmin_cli.py activities

# Step count for today
./garmin_cli.py steps

# Sleep data
./garmin_cli.py sleep 2026-01-17

# Human-friendly output
./garmin_cli.py --format text summary
```

All commands output JSON by default.

## Credentials

Credentials are stored in `~/.config/garmin/credentials.json` (mode 600).

**Security Note**: The credentials file contains your Garmin password in plain text. Protect it accordingly.

## Requirements

- Python 3.8+
- `garminconnect` library
- Garmin Connect account

## License

MIT License - See LICENSE file for details.

## Credits

- Built on [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) by @cyberjunky
- Inspired by Clawdbot skill ecosystem
