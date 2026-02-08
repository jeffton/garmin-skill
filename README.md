# Garmin Skill for OpenClaw

Fetch personal health and fitness data from Garmin Connect. Note this skill is 100% vibe coded from within OpenClaw (using Claude Opus and Codex) and available commands may change. I may or may not get around to doing a proper refactor.

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

## Credit

Built on [python-garminconnect](https://github.com/cyberjunky/python-garminconnect)
