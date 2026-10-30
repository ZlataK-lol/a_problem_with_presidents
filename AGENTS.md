# AGENTS.md

## Commands
```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 analyze.py
```

## Rules
- Don't edit the source CSV.
- Use calendar math (`relativedelta`), not `/ 365`.
- Leave living presidents out of rankings and statistics.
- Run the tests and regenerate `report.pdf` before committing.