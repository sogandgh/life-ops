# meals.json — schema and how to create one

This skill plans only from meals the user has **actually eaten**. That data lives in
`<workspace>/meal-plan/meals.json`. Without it there is nothing to plan from, so creating it
is the first-run task.

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

## Three ways to create the file

### 1. Import a food-tracker export (best, if they have one)

Most tracking apps export CSV. The bundled importer matches columns by alias, so exports from
Lose It!, MyFitnessPal, Cronometer and others generally work as-is:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/meal-plan/scripts/import_food_log.py" \
    <export.csv> -o "<workspace>/meal-plan/meals.json"
```

It groups rows into meals by date + meal type, collapses meals eaten on multiple days into
one entry with `times_logged`, and drops sub-50-calorie sittings (a lone black coffee is not
a breakfast). Useful flags: `--dry-run` to preview, `--top N` to keep only the N most-logged
meals per category, `--min-calories N` to change the floor.

If it can't find a column it prints the headers it saw and the aliases it accepts — tell the
user which column to rename, don't guess at the data.

Typical export paths: Lose It! → web app, Settings → Export Data. MyFitnessPal → web app,
Settings → Export Data → Nutrition. Cronometer → Settings → Account → Export Data. If the
user isn't sure, ask them to find the export in their app rather than sending them to a URL
that may have moved.

### 2. Point at an existing file

If they already have meals.json somewhere, copy it into the workspace (or ask whether they'd
rather the workspace point at their location).

### 3. Build it by hand, conversationally

Viable and often pleasant — ask for their regular meals a category at a time:

> "List the breakfasts you actually eat, with rough portions. Five or six is plenty to start."

Estimate calories and macros for each, **show the estimates and get them confirmed**, then
write the file. Set `times_logged` from how often they say they eat it (weekly → 4, rarely →
1). Aim for at least 5 breakfasts, 5 lunches, 6 dinners, 4 snacks — below that the variety
rules can't be satisfied and the week will feel repetitive. It's fine to start small and add
more later; say so rather than making them grind through thirty meals up front.

## Adding meals later

New meals can be appended to the right category at any time. Keep the sort order and give
realistic `times_logged` values — the planner reads it as "how much of a staple is this."
