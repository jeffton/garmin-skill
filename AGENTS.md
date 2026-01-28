# AGENTS.md - Garmin Skill

## Repo
- GitHub: https://github.com/jeffton/garmin-skill
- Branch: main

## About this skill
CLI wrapper for the Garmin Connect API. Fetches sleep, activities, body battery, HRV, steps, etc.

## Structure
- `garmin_cli.py` - Main script with all commands
- `venv/` - Python virtual environment (not committed)
- `SKILL.md` - Moltbot skill documentation

## Credentials
Garmin login is stored in `~/.config/garmin/credentials.json` (not in repo).

## Commands
- `status` - Check login
- `today` / `daily` - Today's overview
- `sleep [date]` - Sleep data for a date
- `sleep-week [days]` - Sleep data for N days with averages
- `run [activity_id]` - Detailed running activity with laps and comparison
- `summary` / `stats` - Complete daily overview
- `activities [days]` - Activities

## Push policy
Changes may be pushed directly to master. The skill is only used by Moltbot and has no external dependencies.
