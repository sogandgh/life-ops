# Life Ops

A growing collection of personal skills for [Claude Code](https://claude.com/claude-code) — the useful, non-code parts of running a life.

Every skill is generic. Nothing is tied to a particular person, machine, or directory: if a skill needs your resume, your food log, or a calorie target, it asks you the first time and remembers the answer.

| Skill | What it does |
| --- | --- |
| `ai-tutor` | A stateful AI-engineering tutor for software engineers. Teaches LLMs, RAG, retrieval, evaluation, agents and LLMOps in plain language, quizzes you, and walks you through one real project — remembering where you left off between sessions. |
| `meal-plan` | Builds a 7-day meal plan from meals **you have actually eaten**, scaled to your calorie target, with variety rules and a grocery list. |
| `resume-tailor` | Assesses a job posting against your resume, then tailors it only where needed — with your approval on every change — and builds a numbered PDF. Uses your Latex resume |

---

## Install

```
/plugin marketplace add sogandgh/life-ops
/plugin install life-ops
```

Or point Claude Code at a local clone:

```bash
git clone https://github.com/sogandgh/life-ops.git
```

```
/plugin marketplace add ./life-ops
/plugin install life-ops
```

Then invoke a skill by name — `/ai-tutor`, `/meal-plan`, `/resume-tailor` — or just describe what you want ("plan my meals for the week", "am I a good fit for this job?") and Claude will pick the right one.

---

## Configuration

### The one setting: your workspace

When you enable the plugin, Claude Code asks for a **workspace directory** — where these skills keep your data (tutor progress, meal history, generated resumes).

**You can leave it blank.** Everything then goes in the plugin's own data directory (`~/.claude/plugins/data/life-ops/`), which survives plugin updates. Set a workspace only if you want your data somewhere you'll back up or sync, e.g. `~/Documents/life-ops`.

To change it later: `/plugin` → Life Ops → configure. The value is stored in `~/.claude/settings.json` under `pluginConfigs`.

Your data is laid out like this:

```
<workspace>/
├── ai-tutor/
│   └── progress.md          # concept tracker, project state, session log
├── meal-plan/
│   ├── meals.json           # your real meals — the planner's source data
│   ├── profile.json         # calorie target and food preferences
│   └── history.jsonl        # one line per approved week, so weeks don't repeat
└── resume-tailor/
    ├── config.json          # path to your master resume, filename stem, page limit
    ├── output/              # generated Name-N.pdf + Name-N.tex pairs
    ├── job-descriptions/    # saved postings
    └── applications.md      # log of what you applied to
```

Nothing else needs configuring up front. Each skill handles its own setup on first use, described below.

### `ai-tutor` — no setup

The first session asks about your background, target role, weak spots, available time, and what corpus you want the project built over. Those answers go into a learner profile in `progress.md` and shape which modules go deep. Every later session reads that file and resumes where you stopped.

### `meal-plan` — needs your food log

This is the one skill with a real prerequisite: it plans **only from meals you've actually eaten**, so it needs `meals.json`. On first run it offers three ways to create one:

1. **Import a tracker export** (best). Most food-tracking apps export CSV — Lose It!, MyFitnessPal, Cronometer and others generally work as-is, since the importer matches columns by alias:

   ```bash
   python3 skills/meal-plan/scripts/import_food_log.py <export.csv> -o meals.json
   ```

   It groups rows into meals by date and meal type, collapses repeats into one entry with a `times_logged` count, and skips sub-50-calorie sittings. Use `--dry-run` to preview.

2. **Point at an existing** `meals.json` if you already have one.

3. **Build it conversationally** — list the meals you actually eat and Claude estimates the calories with you. Five or six per category is enough to start.

See `skills/meal-plan/references/meals-schema.md` for the format and `skills/meal-plan/assets/meals.example.json` for a working sample.

It then asks for your calorie target, which meal is your main one, anything you don't eat, and any cuisines you want to see regularly — saved to `profile.json`. The skill plans to the target you give it; it will not calculate one for you.

### `resume-tailor` — needs your resume

On first run it asks for:

- **Path to your master resume.** A `.tex` source enables PDF generation. `.md` / `.txt` works for assessment and edit proposals but can't be built into a PDF. Your master file stays where it is and is never modified — edits are applied to a copy.
- **A filename stem** for generated files, e.g. `Jane_Doe_Resume`.
- **A page limit**, default 1.

**PDF generation needs a LaTeX engine.** The build script prefers Docker with the `texlive/texlive` image, so nothing LaTeX-related has to be installed on your machine; it falls back to a local `pdflatex` if one exists. See `skills/resume-tailor/scripts/SETUP.md`. Skip this entirely if your resume isn't LaTeX — assessment and tailoring still work.

---

## Notes

- **Nothing in this repo contains personal data.** The only bundled data file is a synthetic meals example. Your resume, food log, and progress live in your workspace, outside the plugin.
- **Plugin updates replace the install directory.** That's why data lives in the workspace or the plugin data directory, never next to the skills.

## Adding a skill

Drop a directory under `skills/` containing a `SKILL.md` with `name` and `description` frontmatter, and it's picked up — no manifest change needed. Two conventions worth keeping:

- Resolve the workspace the same way the existing skills do (`${user_config.workspace}`, falling back to `${CLAUDE_PLUGIN_DATA}`) and store data under `<workspace>/<skill-name>/`.
- Ask for what you need on first run and persist it, rather than adding another enable-time prompt to `plugin.json`.

## License

MIT — see [LICENSE](LICENSE).