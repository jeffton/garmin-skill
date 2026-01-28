# Garmin Skill for Moltbot

Fetch personal health and fitness data from Garmin Connect. Note this skill is 100% vibe coded from within Moltbot (using Claude Opus and Codex) and available commands may change. I may or may not get around to doing a proper refactor.

## Features

- **Daily Summary**: Steps, calories, distance, heart rate, body battery
- **Activities**: Running, cycling, swimming, strength training with detailed stats
- **Sleep Data**: Duration, quality, HRV, weekly averages
- **Training Metrics**: VO2 max, training load, training readiness, training status
- **Run Analysis**: Lap splits, pace, HR, power, cadence, comparison with recent runs

## Installation

```bash
# Clone this repo
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

## Commands

All commands output JSON. Arguments are positional: `activities 1` not `activities --days 1`.

| Command | Description |
|---------|-------------|
| `login <email> <password>` | Login to Garmin Connect |
| `status` | Check login status |
| `today` | Today's quick overview |
| `summary` | Comprehensive daily summary (sleep, steps, HR, body battery, VO2 max, training metrics) |
| `activities [days]` | Recent activities (default: 7) |
| `steps [days]` | Step count (default: 1) |
| `sleep [days]` | Sleep data with weekly averages (default: 7) |
| `run [activity_id]` | Detailed run analysis with laps and comparison (default: latest run) |

### Examples

```bash
./garmin_cli.py status              # Check login
./garmin_cli.py summary             # Full daily summary
./garmin_cli.py activities 1        # Today's activities only
./garmin_cli.py sleep-week          # 7-day sleep with averages
./garmin_cli.py run                 # Latest run with lap analysis
./garmin_cli.py run 21647187521     # Specific run by activity ID
```

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
