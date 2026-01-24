# AGENTS.md - Garmin Skill

## Repo
- GitHub: https://github.com/jeffton/garmin-skill
- Branch: master

## Om denne skill
CLI-wrapper til Garmin Connect API. Henter søvn, aktiviteter, body battery, HRV, steps osv.

## Struktur
- `garmin_cli.py` - Hovedscript med alle commands
- `venv/` - Python virtual environment (ikke committet)
- `SKILL.md` - Clawdbot skill-dokumentation

## Credentials
Garmin login gemmes i `~/.config/garmin/credentials.json` (krypteret, ikke i repo).

## Commands
- `status` - Check login
- `today` / `daily` - Dagens overblik
- `sleep [date]` - Søvndata for en dato
- `sleep-week [days]` - Søvndata for N dage med gennemsnit
- `run [activity_id]` - Detaljeret løbeaktivitet med laps og sammenligning
- `summary` / `stats` - Komplet dagsoverblik
- `activities [days]` - Aktiviteter

## Push policy
Ændringer må gerne pushes direkte til master. Skill'en bruges kun af Clawdbot og har ingen eksterne afhængigheder.
