# Life Ops

A growing collection of personal skills for [Claude Code](https://claude.com/claude-code) — the useful, non-code parts of running a life.

| Skill | What it does | Needs |
| --- | --- | --- |
| `ai-tutor` | Teaches a working software engineer AI engineering — LLMs, RAG, retrieval, evaluation, agents, LLMOps — through one real project, quizzing you and remembering where you left off. | — |
| `meal-plan` | Builds a 7-day meal plan from meals you've actually eaten, scaled to a calorie target, with a grocery list. | [Lose It!](https://www.loseit.com/), Python 3 |
| `resume-tailor` | Assesses a job posting against your resume, tailors it only where needed with your approval, and builds a numbered PDF. | LaTeX resume; Docker or `pdflatex` |

## Install

```
/plugin marketplace add sogandgh/life-ops
/plugin install life-ops
```

Then say what you want — "plan my meals for the week", "am I a good fit for this job?" — or call a skill directly with `/ai-tutor`, `/meal-plan`, `/resume-tailor`.

## Your stuff goes in `~/life-ops/`

```
~/life-ops/
├── ai-tutor/progress.md        # created for you on first session
├── meal-plan/
│   ├── meals.json              # your Lose It! export, imported
│   ├── profile.json            # calorie target, foods to avoid
│   └── history.jsonl           # past weeks, so plans don't repeat
└── resume-tailor/
    ├── config.json             # where your resume is, filename, page limit
    ├── output/                 # generated PDFs + their .tex sources
    ├── job-descriptions/       # saved postings
    └── applications.md         # what you applied to
```

Each skill creates what it needs and asks for the rest on first run. There's nothing to configure up front.

Two things you supply:

- **`meal-plan`** — export your food log from the Lose It! web app (**Settings → Export Data**) and hand over the CSV. The skill imports it. Other trackers aren't supported.
- **`resume-tailor`** — tell it where your `.tex` resume lives. It stays put and is never modified; edits go to a copy. PDF building needs Docker (it pulls `texlive/texlive` on first build) or a local `pdflatex` — see [`SETUP.md`](skills/resume-tailor/scripts/SETUP.md). Without either, you still get the fit assessment and proposed edits.

## Adding a skill

Drop a directory under `skills/` with a `SKILL.md` and it's picked up. Keep data in `~/life-ops/<skill-name>/` and ask for what you need on first run.

## License

MIT
