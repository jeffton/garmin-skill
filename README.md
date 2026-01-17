# Garmin Skill for Clawdbot

Fetch and display Garmin Connect data from your personal health and fitness dashboard.

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
git clone https://github.com/YOUR_USERNAME/garmin-skill.git
cd garmin-skill

# Install dependencies
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

# Today's summary
./garmin_cli.py today

# Daily stats (steps, HR, body battery)
./garmin_cli.py daily

# Last 7 days of activities
./garmin_cli.py activities

# Step count for today
./garmin_cli.py steps

# Sleep data
./garmin_cli.py sleep 2026-01-17

# Detailed stats (VO2 max, training load)
./garmin_cli.py stats
```

All commands output JSON.

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
