#!/usr/bin/env python3
import csv
import json
import os
import re
from collections import defaultdict


CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "text.csv"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "test.json")


COMMON_CORRECTIONS = {
    r"\btumeric\b": "turmeric",
    r"\bTumeric\b": "Turmeric",
    r"\bigredient\b": "ingredient",
    r"\bigredients\b": "ingredients",
    r"\bthunb\b": "thumb",
    r"\bsezed\b": "sized",
    r"\bdaliy\b": "daily",
    r"\bcruhed\b": "crushed",
    r"\bStair\b": "Stir",
    r"\bminute\b": "minutes",
    r"\bmintues\b": "minutes",
    r"\bbefoer\b": "before",
    r"\bapply cider\b": "apple cider",
    r"\bapply\b": "apple",
    r"\bAAdd\b": "Add",
    r"\bincoporate\b": "incorporate",
    r"\bEpsom\b": "Epsom",
    r"\bvaselline\b": "vaseline",
    r"\bgal\b": "gel",
    r"\boli\b": "oil",
    r"\bofeucalyptus\b": "of eucalyptus",
    r"\bsecongthr\b": "seconds then",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    s = text.strip()
    # standardize spacing
    s = re.sub(r"\s+", " ", s)
    # light punctuation spacing
    s = s.replace(" ,", ",").replace(" .", ".")
    # apply common corrections
    for pattern, repl in COMMON_CORRECTIONS.items():
        s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    # unify units spacing
    s = s.replace(" ml", " ml").replace(" tbsp", " tbsp").replace(" tsp", " tsp")
    return s


def slugify(text: str) -> str:
    s = normalize_text(text).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip('-')
    return s or "item"


def read_csv_grouped(path: str):
    items = []
    current = None

    with open(path, newline='', encoding='utf-8') as f:
        # Detect the real header row (first row whose first cell equals 'Items')
        raw_reader = csv.reader(f)
        header = None
        rows = []
        for row in raw_reader:
            if not any(cell.strip() for cell in row):
                continue  # skip fully empty rows
            if header is None and len(row) >= 5 and row[0].strip() == 'Items':
                header = row
                continue
            if header is not None:
                rows.append(row)

        if header is None:
            return []

        # Build dict rows safely using detected header
        reader = (dict(zip(header, r + [""] * (len(header) - len(r)))) for r in rows)
        for row in reader:
            title = (row.get('Items') or '').strip()
            ing = (row.get('Ingredients') or '').strip()
            proc = (row.get('Procedures/Processing') or '').strip()
            app = (row.get('Application') or '').strip()
            prog = (row.get('Prognosis') or '').strip()

            if title:
                # start a new remedy
                if current:
                    items.append(current)
                current = {
                    'id': slugify(title),
                    'title': normalize_text(title),
                    'ingredients': [],
                    'preparation': [],
                    'application': [],
                    'prognosis': None,
                }

            if not current:
                # ignore leading empty rows if any
                continue

            if ing:
                current['ingredients'].append(normalize_text(ing))
            if proc:
                # split by common delimiters if present
                steps = [s for s in re.split(r"\s*[,;]\s*|\s*\n\s*", proc) if s]
                for step in steps:
                    current['preparation'].append(normalize_text(step))
            if app:
                # applications are generally sentence fragments; keep as lines
                parts = [p.strip() for p in re.split(r"\s*\n\s*", app) if p.strip()]
                for p in parts:
                    current['application'].append(normalize_text(p))
            if prog and not current['prognosis']:
                current['prognosis'] = normalize_text(prog)

    if current:
        items.append(current)

    # de-duplicate consecutive identical steps/lines
    for it in items:
        def dedupe(seq):
            seen = []
            for v in seq:
                if not seen or seen[-1] != v:
                    seen.append(v)
            return seen
        it['ingredients'] = dedupe([v for v in it['ingredients'] if v])
        it['preparation'] = dedupe([v for v in it['preparation'] if v])
        it['application'] = dedupe([v for v in it['application'] if v])

    return items


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = read_csv_grouped(CSV_PATH)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(data)} remedies to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()


