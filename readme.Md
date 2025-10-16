# Data generation (Health Aid)

This repository includes a script to convert the CSV into a normalized JSON file for the app.

## Files

- `Natural Health Hacks - Health-Aid.csv` — source data (as shared)
- `scripts/parse_health_aid.py` — parser and normalizer
- `data/health_aid.json` — generated output (84 remedies)

## Run

```bash
python3 "scripts/parse_health_aid.py"
```

The script will write the JSON to `data/health_aid.json`.

## Notes

- The parser fixes some common misspellings and normalizes spacing, but avoids heavy edits; please review content for medical accuracy.
- Grouping logic: a new remedy begins when the `Items` column is non-empty; subsequent rows with an empty `Items` belong to the previous remedy.
- `ingredients` are simple strings for now; we can structure them later as `{name, quantity, unit}`.
