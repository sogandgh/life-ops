#!/usr/bin/env python3
"""Turn a food-tracking CSV export into the meals.json this skill plans from.

Works with exports from Lose It!, MyFitnessPal, Cronometer, and most other trackers —
columns are matched by alias, case-insensitively, so exact header text doesn't matter.

    import_food_log.py <export.csv> -o <meals.json>

Rows are grouped into meals by (date, meal type): everything logged as Tuesday's dinner
becomes one dinner. Identical meals logged on different days collapse into a single entry
with times_logged counting how often it was eaten.

Options:
    -o, --output      where to write meals.json (default: ./meals.json)
    --top N           keep only the N most-logged meals per category (default: all)
    --min-calories N  drop meals under N calories (default: 50)
    --dry-run         print a summary, write nothing
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date

# Header aliases, lowercased. First match wins.
FIELDS = {
    "date": ["date", "day", "logged date", "date logged"],
    "meal": ["type", "meal", "meal name", "meal type", "category", "group"],
    "name": ["name", "food", "food name", "description", "item", "product"],
    "qty": ["quantity", "qty", "amount", "servings", "serving size", "number of servings"],
    "units": ["units", "unit", "measure", "serving", "serving unit"],
    "calories": ["calories", "cal", "kcal", "energy", "energy (kcal)", "calories (kcal)"],
    "protein": ["protein", "protein (g)", "protein g"],
    "carb": ["carbohydrates", "carbs", "carb", "carbohydrates (g)", "carbs (g)", "net carbs (g)"],
    "fat": ["fat", "fat (g)", "fat g", "total fat (g)"],
}

CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snacks"]

MEAL_ALIASES = {
    "breakfast": "Breakfast",
    "morning": "Breakfast",
    "lunch": "Lunch",
    "midday": "Lunch",
    "noon": "Lunch",
    "dinner": "Dinner",
    "supper": "Dinner",
    "evening": "Dinner",
    "snack": "Snacks",
    "snacks": "Snacks",
}


def map_columns(headers):
    """Match CSV headers to our field names. Returns {field: header}."""
    normalized = {h.strip().lower(): h for h in headers if h}
    found = {}
    for field, aliases in FIELDS.items():
        for alias in aliases:
            if alias in normalized:
                found[field] = normalized[alias]
                break
    return found


def to_float(value):
    """Parse a number out of a cell, tolerating '1,024', '12 g', '--', and ''."""
    if value is None:
        return 0.0
    text = str(value).strip().replace(",", "")
    if not text or text in {"-", "--", "N/A", "n/a"}:
        return 0.0
    cleaned = "".join(c for c in text if c.isdigit() or c in ".-")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def normalize_meal(value):
    """Map a tracker's meal label onto one of our four categories."""
    text = str(value or "").strip().lower()
    if text in MEAL_ALIASES:
        return MEAL_ALIASES[text]
    for alias, category in MEAL_ALIASES.items():
        if alias in text:
            return category
    return None


def read_rows(path, columns):
    """Yield (date, category, food-dict) for each usable CSV row."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            category = normalize_meal(row.get(columns["meal"], ""))
            if category is None:
                continue
            name = str(row.get(columns["name"], "")).strip()
            if not name:
                continue
            food = {
                "name": name,
                "qty": str(row.get(columns.get("qty", ""), "") or "1").strip(),
                "units": str(row.get(columns.get("units", ""), "") or "serving").strip(),
                "cal": round(to_float(row.get(columns["calories"]))),
            }
            for macro in ("protein", "carb", "fat"):
                if macro in columns:
                    food[macro] = round(to_float(row.get(columns[macro])), 1)
            yield str(row.get(columns["date"], "")).strip(), category, food


def build_meals(path, columns, min_calories):
    """Group rows into meals, then collapse duplicates across days."""
    # (date, category) -> [food, ...]
    sittings = defaultdict(list)
    for day, category, food in read_rows(path, columns):
        sittings[(day, category)].append(food)

    # category -> signature -> meal
    collapsed = {category: {} for category in CATEGORIES}
    for (_, category), foods in sittings.items():
        calories = sum(f["cal"] for f in foods)
        if calories < min_calories:
            continue
        signature = tuple(sorted((f["name"].lower(), f["qty"], f["units"]) for f in foods))
        existing = collapsed[category].get(signature)
        if existing:
            existing["times_logged"] += 1
            continue
        meal = {
            "calories": calories,
            "protein": round(sum(f.get("protein", 0) for f in foods)),
            "carb": round(sum(f.get("carb", 0) for f in foods)),
            "fat": round(sum(f.get("fat", 0) for f in foods)),
            "times_logged": 1,
            "foods": foods,
        }
        collapsed[category][signature] = meal
    return collapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path", help="food-tracker CSV export")
    parser.add_argument("-o", "--output", default="meals.json", help="output path (default: meals.json)")
    parser.add_argument("--top", type=int, default=0, help="keep only the N most-logged meals per category")
    parser.add_argument("--min-calories", type=int, default=50, help="drop meals under N calories (default: 50)")
    parser.add_argument("--dry-run", action="store_true", help="print a summary, write nothing")
    args = parser.parse_args()

    try:
        with open(args.csv_path, newline="", encoding="utf-8-sig") as handle:
            headers = next(csv.reader(handle))
    except OSError as err:
        sys.exit(f"ERROR: cannot read {args.csv_path}: {err}")
    except StopIteration:
        sys.exit(f"ERROR: {args.csv_path} is empty")

    columns = map_columns(headers)
    missing = [f for f in ("date", "meal", "name", "calories") if f not in columns]
    if missing:
        sys.exit(
            f"ERROR: could not find a column for: {', '.join(missing)}\n"
            f"  Headers seen: {', '.join(h for h in headers if h)}\n"
            f"  Rename the relevant columns to match one of these and re-run:\n"
            + "\n".join(f"    {f}: {', '.join(FIELDS[f])}" for f in missing)
        )

    collapsed = build_meals(args.csv_path, columns, args.min_calories)

    meals = {}
    for category in CATEGORIES:
        entries = sorted(collapsed[category].values(), key=lambda m: -m["times_logged"])
        if args.top:
            entries = entries[: args.top]
        meals[category] = sorted(entries, key=lambda m: m["calories"])

    total = sum(len(v) for v in meals.values())
    if not total:
        sys.exit("ERROR: no meals found. Check that the meal-type column holds values like 'Breakfast'/'Lunch'/'Dinner'/'Snack'.")

    print(f"Matched columns: {', '.join(f'{k}={v}' for k, v in columns.items())}")
    for category in CATEGORIES:
        print(f"  {category:<10} {len(meals[category]):>4} distinct meals")
    print(f"  {'TOTAL':<10} {total:>4}")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return

    payload = {
        "source": args.csv_path,
        "generated": date.today().isoformat(),
        "note": "Distinct meals as actually logged. times_logged = how often this exact meal was eaten.",
        "meals": meals,
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    print(f"\nWROTE: {args.output}")


if __name__ == "__main__":
    main()
