# meals.json — schema and how to create one

This skill plans only from meals the user has **actually eaten**, imported from their
**Lose It!** food journal. That data lives in `<workspace>/meal-plan/meals.json`. Without it
there is nothing to plan from, so creating it is the first-run task.

## Schema

```json
{
  "source": "where this came from (free text)",
  "generated": "2026-08-14",
  "note": "free text",
  "meals": {
    "Breakfast": [ /* meal objects */ ],
    "Lunch":     [ /* meal objects */ ],
    "Dinner":    [ /* meal objects */ ],
    "Snacks":    [ /* meal objects */ ]
  }
}
```

A **meal object** is one whole thing the user ate at one sitting:

| Field | Type | Notes |
|---|---|---|
| `calories` | number | Total for the meal |
| `protein` / `carb` / `fat` | number | Grams, summed from components. May be `0` or partial where the source lacked macros |
| `times_logged` | number | How often this exact meal was eaten. Higher = more of a staple |
| `foods` | array | The component items |

Each entry in `foods`:

| Field | Type | Notes |
|---|---|---|
| `name` | string | Include the brand if it's part of how the food was logged |
| `qty` | string | e.g. `"2"`, `"0.5"`, `"140"` |
| `units` | string | e.g. `"large"`, `"cup"`, `"g"`, `"slice"` |
| `cal` | number | Calories for this component |
| `protein` / `carb` / `fat` | number | Optional; omit when the source had no macros |

Sort each category by `calories` ascending. See `assets/meals.example.json` for a small
working file.

**Why whole meals matter:** each entry is a real combination the user genuinely ate, so
selecting whole entries guarantees the day is coherent — real breakfasts and real dinners,
never a pile of unrelated foods assembled to hit a number.

## Creating the file from Lose It!

**Requirements: a Lose It! account with logged meals, and Python 3** (standard library only).
Other food trackers are not supported.

### 1. Export from Lose It!

In the **Lose It! web app → Settings → Export Data**. That downloads a CSV of the food log
with columns like:

```
Date, Name, Icon, Type, Quantity, Units, Calories, Fat (g), Protein (g), Carbohydrates (g)
```

If the user can't find the export, have them look in the app's settings rather than sending
them to a URL that may have moved.

### 2. Run the importer

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/meal-plan/scripts/import_lose_it.py" \
    <export.csv> -o "<workspace>/meal-plan/meals.json"
```

It groups rows into meals by date + meal type (everything logged as Tuesday's dinner becomes
one dinner), collapses meals eaten on multiple days into one entry with `times_logged`, and
drops sub-50-calorie sittings — a lone black coffee is not a breakfast.

| Flag | Effect |
|---|---|
| `--dry-run` | Print the summary, write nothing |
| `--top N` | Keep only the N most-logged meals per category |
| `--min-calories N` | Change the 50-calorie floor |

Columns are matched case-insensitively and by alias, so small changes to Lose It!'s export
format won't break the import. If a required column still can't be found, the script prints
the headers it saw and the aliases it accepts — tell the user which column to rename rather
than guessing at the data.

### How much data is enough

The variety rules need roughly 5 breakfasts, 5 lunches, 6 dinners and 4 snacks to work with.
Below that the week will feel repetitive — say so plainly and suggest logging more before
planning, rather than producing a plan that repeats.

### If the file needs writing by hand

Nothing stops a correctly-shaped `meals.json` from being written directly to the schema
above — but only do that if the user asks. **Never estimate meals into existence to work
around a missing export**, since the skill's entire premise is that every meal is one they
have actually eaten.

## Adding meals later

New meals can be appended to the right category at any time. Keep the sort order and give
realistic `times_logged` values — the planner reads it as "how much of a staple is this."
