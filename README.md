# Life Ops

A growing collection of personal skills for [Claude Code](https://claude.com/claude-code) — the useful, non-code parts of running a life.

Every skill is generic. Nothing is tied to a particular person, machine, or directory: if a skill needs your resume, your food log, or a calorie target, it asks you the first time and remembers the answer.

| Skill | What it does | Requires |
| --- | --- | --- |
| `ai-tutor` | Helps a working software engineer learn AI engineering. Teaches LLMs, RAG, retrieval, evaluation, agents and LLMOps in plain language, quizzes you, and walks you through one real project — remembering where you left off between sessions. | nothing |
| `meal-plan` | Builds a 7-day meal plan from meals **you have actually eaten**, scaled to your calorie target, with variety rules and a grocery list. | a **Lose It!** account, Python 3 |
| `resume-tailor` | Honestly assesses a job posting against your resume, then tailors it only where needed — with your approval on every change — and builds a numbered PDF. | a **LaTeX** resume, Docker or `pdflatex` (for PDFs only) |

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
│   ├── meals.json           # your real meals, imported from Lose It!
│   ├── profile.json         # calorie target and food preferences
│   └── history.jsonl        # one line per approved week, so weeks don't repeat
└── resume-tailor/
    ├── config.json          # path to your master resume, filename stem, page limit
    ├── output/              # generated Name-N.pdf + Name-N.tex pairs
    ├── job-descriptions/    # saved postings
    └── applications.md      # log of what you applied to
```

Nothing else needs configuring up front. Each skill handles its own setup on first use, described below.

### `ai-tutor` — no setup, no dependencies

The first session asks about your background, target role, weak spots, available time, and what corpus you want the project built over. Those answers go into a learner profile in `progress.md` and shape which modules go deep — an engineer who already ships agents skips ahead; one who's never made an API call starts at Module 0.

Every later session reads that file and resumes where you stopped, opening with a quiz on whatever you were shaky on last time.

### `meal-plan` — requires Lose It!

**This skill works with the [Lose It!](https://www.loseit.com/) app specifically.** Other food trackers aren't supported. It plans only from meals you've genuinely logged, which is what keeps a day coherent — real breakfasts and real dinners, never a pile of foods assembled to hit a calorie number.

**You need:**

- A **Lose It!** account with meals logged in it
- **Python 3** — for the bundled importer. Standard library only, nothing to install

**Setup.** Export your food log from the Lose It! web app (**Settings → Export Data**), then:

```bash
python3 skills/meal-plan/scripts/import_lose_it.py <export.csv> -o meals.json
```

The importer groups rows into meals by date and meal type, collapses meals you've eaten on multiple days into one entry with a `times_logged` count, and skips sub-50-calorie sittings. Use `--dry-run` to preview, `--top N` to keep only your most-logged meals, `--min-calories N` to change the floor.

Roughly 5 breakfasts, 5 lunches, 6 dinners and 4 snacks is enough for the variety rules to work. Below that the week starts repeating.

The skill then asks for your calorie target, which meal is your main one, anything you don't eat, and any cuisines you want to see regularly — saved to `profile.json`. It plans to the target you give it and will not calculate one for you from body stats.

See `skills/meal-plan/references/meals-schema.md` for the data format and `skills/meal-plan/assets/meals.example.json` for a working sample.

### `resume-tailor` — requires LaTeX (for PDFs)

Built around a **LaTeX resume**. On first run it asks for the path to your master `.tex` file, a filename stem for generated files (e.g. `Jane_Doe_Resume`), and a page limit (default 1). Your master file stays where it is and is never modified — approved edits are applied to a copy.

**You need, to generate PDFs:**

- A master resume in **LaTeX** (`.tex`)
- **Docker** — the preferred engine. Builds run inside the `texlive/texlive` image, the full TeX Live distribution, so no package or font is ever missing and nothing LaTeX-related has to be installed on your machine. The image is pulled automatically on first build (several GB, one time only)
- **or a local `pdflatex`** — used as a fallback when Docker isn't running. Be warned that minimal distributions like BasicTeX often need a round of `sudo tlmgr install` and can still fail on missing font outlines; `brew install --cask mactex` avoids that

See `skills/resume-tailor/scripts/SETUP.md` for the details.

**The assessment doesn't need any of that.** Judging fit against a posting and proposing edits works on a resume in any readable format — `.md`, `.txt`, `.pdf`, `.docx`. Only the PDF build needs LaTeX and an engine, and the skill tells you plainly when it can't do that step rather than skipping it silently.

---

## Notes

- **Plugin updates replace the install directory.** That's why data lives in the workspace or the plugin data directory, never next to the skills.
- **`resume-tailor` will not lie for you.** It refuses to add skills you don't have, change dates or metrics, or inflate scope — even if asked. A weak match stated honestly is the intended output.

## Adding a skill

Drop a directory under `skills/` containing a `SKILL.md` with `name` and `description` frontmatter, and it's picked up — no manifest change needed. Two conventions worth keeping:

- Resolve the workspace the same way the existing skills do (`${user_config.workspace}`, falling back to `${CLAUDE_PLUGIN_DATA}`) and store data under `<workspace>/<skill-name>/`.
- Ask for what you need on first run and persist it, rather than adding another enable-time prompt to `plugin.json`.

## License

MIT — see [LICENSE](LICENSE).
