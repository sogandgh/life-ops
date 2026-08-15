---
name: meal-plan
description: Generate a fresh weekly meal plan (7 days x breakfast/lunch/dinner/snack) drawn from the user's own Lose It! food journal, scaled to a daily calorie target. Use whenever the user asks for a meal plan, weekly plan, what to eat this week, or runs /meal-plan.
argument-hint: "[optional: a daily calorie target, e.g. 1800]"
---

# Weekly Meal Plan

Build the user a **new 7-day meal plan** using **only meals they have actually eaten**,
scaled to a daily calorie target. The whole point: every day is a coherent set of real meals
(real breakfasts, lunches, dinners that go together), never a random pile of unrelated foods.

## Requirements

| Needs | Why |
|---|---|
| A **Lose It!** account with logged meals | The plan is built from the user's own food journal. This skill reads the Lose It! CSV export; other trackers are not supported |
| **Python 3** | Runs the bundled importer. Standard library only — nothing to install |

Without a Lose It! export there is nothing to plan from. If the user doesn't use Lose It!,
say so directly rather than improvising a plan from invented meals — the whole premise is
that every meal is one they've actually eaten.

---

## Where your data lives

Resolve the workspace once, at the start of every run:

1. If `${user_config.workspace}` is a real absolute path, that is the workspace.
2. Otherwise — it's blank, or it still reads as a literal `${user_config...}` placeholder
   because the user never configured it — use `${CLAUDE_PLUGIN_DATA}`.

This skill's files live in `<workspace>/meal-plan/`:

| File | What it is |
|---|---|
| `meals.json` | The user's real logged meals — the only source of meals to plan from |
| `profile.json` | Calorie target and standing food preferences |
| `history.jsonl` | One line per approved week, so weeks don't repeat |

Bundled read-only references ship with the plugin under `${CLAUDE_PLUGIN_ROOT}/skills/meal-plan/`:
`references/meals-schema.md`, `assets/meals.example.json`, `scripts/import_lose_it.py`.
Never write into `${CLAUDE_PLUGIN_ROOT}` — it is replaced whenever the plugin updates.

---

## STEP 0 — First-run setup

Check for `<workspace>/meal-plan/meals.json`. **If it's missing, there is nothing to plan
from** — set it up before anything else.

Ask the user to export their Lose It! food log: **Lose It! web app → Settings → Export
Data**, which downloads a CSV. Then run the bundled importer:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/meal-plan/scripts/import_lose_it.py" \
    <export.csv> -o "<workspace>/meal-plan/meals.json"
```

Read `${CLAUDE_PLUGIN_ROOT}/skills/meal-plan/references/meals-schema.md` for the flags, the
output format, and what to do when a column doesn't match. Don't invent a meals file on the
user's behalf.

Then check for `<workspace>/meal-plan/profile.json`. If it's missing, ask — briefly, in one
message — and write their answers to it:

1. **Daily calorie target?** If they don't know one, say so plainly: this skill plans to a
   number, it doesn't compute one from body stats. Suggest they get a target from their
   tracking app or a doctor, and offer to use a placeholder for now that they can change any
   time.
2. **Which meal is the big one** — dinner for most people, but not everyone.
3. **Anything you don't eat?** Allergies, dislikes, vegetarian/vegan/halal/kosher, etc.
4. **Any cuisines or staples you want to see regularly?**

```json
{
  "daily_calories": 2000,
  "main_meal": "Dinner",
  "exclusions": ["shellfish"],
  "favor": ["Persian", "Mexican"],
  "notes": "free text"
}
```

Re-read `profile.json` at the start of every later run and honor it. If the user contradicts
it in conversation ("actually make it 1700 this week"), use the new value for this plan and
ask whether to update the profile — don't silently rewrite it.

## Calorie target

- A number in the invocation (e.g. `/meal-plan 1800`) wins for this run.
- Otherwise use `daily_calories` from `profile.json`.
- State the number you used in one line and note they can override it.

Never infer a target from weight, goals, or body stats, and never volunteer one — that's
medical territory and not what this skill is for. Plan to the number you were given.

## Avoiding repeats (history)

The skill keeps a memory of past plans in `<workspace>/meal-plan/history.jsonl` — one JSON
line per generated week:

```json
{"date":"YYYY-MM-DD","calories":2000,"used":{"Breakfast":["meal label"],"Lunch":[],"Dinner":[],"Snacks":[]}}
```

**Before planning:** read `history.jsonl` and look at the **last 3 weeks** of entries.

- Treat every meal used in those weeks as "recently used."
- Do **not** reuse a recently-used breakfast/lunch/dinner this week unless you'd otherwise run
  out of options that fit the calorie target. Snacks may repeat more freely.
- If nearly everything fitting the target has been used recently, pick the
  **least-recently-used** ones and say so — don't get stuck.

**After the plan is approved:** append one new line recording today's date, the calorie
target, and the meal labels you used. This is what makes next week different. Keep the file
append-only; never rewrite past lines.

Identify a meal by a short label (e.g. the first/main food name) so history stays readable
and matching is fuzzy-but-good-enough.

---

## How to build the plan

1. **Read `meals.json`, `profile.json`, and `history.jsonl`.**

2. For **each of the 7 days**, pick one Breakfast, one Lunch, one Dinner, and (if it fits)
   one Snack so the day's total lands **roughly around the target** — the target is a loose
   guide, not a strict number, and within ~100–150 cal is totally fine. Don't agonize.

   - **The main meal carries the day.** Whichever meal `profile.json` names as `main_meal`
     should be at least **40% of the daily target** (so ~800 cal on a 2000-cal target). Pick
     one that already clears that bar and build the rest of the day around it.
   - The other meals are lighter: the two secondary meals moderate, **snack small** (~10% of
     target, or skip it if the day's already about right).
   - **Do NOT fractionally rescale meals to hit a number** (no "x1.06 portion" stuff).
     Present meals at their real logged portions. The only portion adjustments allowed are
     natural, whole-ish ones a person would actually make (1 egg vs 2 eggs, a half vs whole
     sandwich) — and only if it reads naturally, never to chase a calorie total.
   - If the target is so low that no main meal fits, say so and suggest a higher target
     rather than shrinking everything.

3. **Variety first — this matters a lot, don't let the week feel repetitive.** Hard rules:

   - No exact meal more than **twice** in the week, and never on back-to-back days.
   - **Cap repeated base ingredients:** the same starch/base (rice, bread, oatmeal, pasta)
     appears in **at most 2–3 days total** across the whole week — NOT 4+. Same for a hero
     protein; don't lean on the same chicken/beef/tuna every day. Spread them out, don't
     cluster.
   - **Vary the format day to day:** rotate breakfast styles (egg plate vs oats vs yogurt vs
     breakfast sandwich) and main-meal bases (rice dish vs pasta vs sandwich/wrap vs stew) so
     consecutive days don't feel the same. Most of the 7 days should look distinctly
     different.
   - Respect cross-week history too (don't echo recent weeks).
   - **Grocery cost is a SECONDARY, soft consideration** — mild overlap is fine to keep the
     list manageable, but never sacrifice the variety caps above for it. When in doubt,
     choose variety.

4. **Keep meals simple & familiar:** favor straightforward meals exactly as the user logged
   them — don't invent elaborate new recipes or fancy combos. **"Simple" means easy and
   familiar, NOT few-ingredient.** A traditional dish with five components (a stew served
   with rice, yogurt, and salad) is simple to someone who cooks it weekly. Never skip a
   multi-component meal for looking complicated, especially anything matching the `favor`
   list in `profile.json` — those are staples and should show up regularly across the week.

5. **Protein is NOT a target.** Use it only as a faint tiebreaker between two otherwise
   equally good options. Never sacrifice variety, meal coherence, or calorie-fit to chase
   protein, and don't keep picking high-protein meals — many real meals are naturally
   low-protein and that's fine. (If the user explicitly asks for higher protein, that's a
   constraint for this run; honor it.)

6. **Honor `exclusions` from `profile.json` absolutely** — an allergy or a dietary rule is
   never overridden for variety or calorie fit. If a listed exclusion makes the plan
   impossible, say so instead of quietly breaking it.

7. If the user names a constraint for this run ("no fish this week", "more one-pot meals",
   vegetarian, a different calorie number), honor it when selecting.

---

## Output format

Start with one line: the daily calorie target used and a note they can override it
(`/meal-plan 1700`, or just ask for tweaks).

Then a list per day. For each meal **list every component food with its real portion and the
brand if the data has one**, then the meal's **calories and protein**. Use the exact `qty` +
`units` from `meals.json` (e.g. "120 g", "1 large", "2 tbsp"), and include the brand when
it's part of the food's name — if a food was logged without one (avocado, egg), just give the
portion. Don't reduce a meal to a vague phrase; give the actual items and amounts so it's
shoppable and cookable.

**Show protein** for each meal and as a **day total**, using each meal's `protein` field. Some
meals have partial protein data (a component was logged without macros) — when a day's
protein is built from any such meal, mark the day total with a `~` to show it's a floor.
Example shape:

```
## Monday — ~1,490 cal · ~96 g protein
**Breakfast (~230 cal · 18 g P)**
  - 2 large eggs
  - 1 slice Whole Wheat Bread
  - 40 g avocado
**Dinner (~640 cal · 45 g P)**
  - 140 g salmon
  - 1 cup jasmine rice (cooked)
  - 0.5 cup mixed salad
```

End with:

- A one-line **weekly summary** (avg daily calories, avg protein).
- A short **grocery list** grouped by aisle, deduped across the week, so the plan is
  actionable.

Keep it scannable. This is a plan they'll cook from, not a report.

---

## Review & adjust before saving (required)

**Do NOT append to `history.jsonl` yet.** This is a draft. After presenting the plan,
explicitly ask whether they want changes:

> "Want any adjustments before I lock this in? You can swap a specific meal (e.g. *'swap
> Tuesday dinner'* or *'replace it with something lighter'*), change a whole day, adjust the
> calorie target, or say *'looks good'* to save it."

Then handle their response:

- **Swap a meal** — pick a different real meal of the same type that fits that day's target
  (and respects the history/variety rules); re-show just the changed day with updated totals.
- **Modify a day** — rebuild that day's meals to the target or to their request.
- **Change the calorie target** — regenerate affected days.
- Keep looping: apply changes, show what changed, and ask again if there's anything else.
- When they're satisfied ("looks good" / "save" / "that's it"), proceed to save.

Only honor swaps using **real meals from `meals.json`** at their real portions, unless the
user explicitly asks you to invent something new — keep meals coherent.

## Save

Once the user approves the **final** plan, **append one line to `history.jsonl`** (see
"Avoiding repeats") recording today's date, the calorie target, and the meal labels actually
used in the approved plan. Confirm in one line that it was saved, so next week's plan will
differ. If the user never approves, do not save.
