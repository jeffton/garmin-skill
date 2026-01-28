# Garmin Skill for Moltbot

Fetch personal health and fitness data from Garmin Connect.

100% vibe coded from within Moltbot (Claude Opus + Codex).

## Installation

```bash
git clone https://github.com/jeffton/garmin-skill.git
cd garmin-skill
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
./garmin_cli.py login your@email.com yourpassword
```

See [SKILL.md](SKILL.md) for commands and usage.

## License

MIT - Built on [python-garminconnect](https://github.com/cyberjunky/python-garminconnect)
