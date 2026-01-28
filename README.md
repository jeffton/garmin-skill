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

See [SKILL.md](SKILL.md) for commands and usage.

## License

MIT - Built on [python-garminconnect](https://github.com/cyberjunky/python-garminconnect)
