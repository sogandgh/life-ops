---
name: resume-tailor
description: Assess a job description against the user's resume and, only if needed, tailor their LaTeX resume and build a numbered PDF. Use whenever the user pastes a job description, shares a job posting URL, asks "am I a good fit / what are my chances" for a role, asks to tailor or customize their resume for a job, or runs /resume-tailor.
argument-hint: "[optional: a job posting URL, or paste the job description]"
---

# Resume Tailor

Two jobs, in this order: **honestly assess fit**, then **tailor only what needs tailoring** —
with the user's explicit approval on every single change.

The hard requirement: **the resume must never say anything untrue.** Treat that as
inviolable. A weaker match honestly stated is the correct output; an inflated resume is a
failure of the task even if the user seems to want a higher score.

## Requirements

| Needs | Why |
|---|---|
| A master resume in **LaTeX** (`.tex`) | The source of truth this skill reads, edits a copy of, and compiles |
| **Docker**, with the `texlive/texlive` image | The build engine. Full TeX Live, so no package or font is ever missing. The image is pulled automatically on first build (several GB, one time) |
| *or* a local **`pdflatex`** | Fallback if Docker isn't running. A minimal distribution like BasicTeX often fails on missing packages or font outlines — see `scripts/SETUP.md` |

**Fit assessment needs none of this.** Steps 1–6 (fetch the posting, assess fit, propose
edits) work against a resume in any readable format — `.tex`, `.md`, `.txt`, `.pdf`, `.docx`.
Only Step 7, building the PDF, requires LaTeX plus an engine.

So when the user has no `.tex` source or no engine, still do the valuable part: assess and
propose the edits, then say plainly which piece you can't do and why. Never quietly skip the
build, and never improvise a Markdown-to-PDF converter as a substitute.

---

## Where your data lives

Resolve the workspace once, at the start of every run:

1. If `${user_config.workspace}` is a real absolute path, that is the workspace.
2. Otherwise — it's blank, or it still reads as a literal `${user_config...}` placeholder
   because the user never configured it — use `${CLAUDE_PLUGIN_DATA}`.

This skill's files live in `<workspace>/resume-tailor/`:

| What | Where |
|---|---|
| Skill settings | `config.json` |
| Generated resumes — **both** `<Name>-N.pdf` and its `<Name>-N.tex` | `output/` |
| Saved job descriptions | `job-descriptions/` |
| Application log | `applications.md` |

The **master resume stays where the user keeps it** — usually in their own repo — and its
path is recorded in `config.json`. Never move it into the workspace, and never write into
`${CLAUDE_PLUGIN_ROOT}`.

## STEP 0 — First-run setup

If `<workspace>/resume-tailor/config.json` is missing, ask for what you need and write it:

1. **Path to your master LaTeX resume (`.tex`)?** This is what the skill is built around. If
   they hand you a `.md`, `.txt`, `.pdf` or `.docx` instead, accept it — record it and note
   in `config.json` that PDF generation is unavailable, so later runs don't keep asking.
2. **Name for generated files?** Used only for the filename stem, e.g. `Jane_Doe_Resume`.
3. **How many pages should the resume be?** Default 1; two is normal for longer careers.

If the resume is `.tex`, confirm an engine exists before promising a PDF —
`docker info` succeeding, or `command -v pdflatex`. If neither is available, point them at
`${CLAUDE_PLUGIN_ROOT}/skills/resume-tailor/scripts/SETUP.md` and carry on with the
assessment; a missing engine blocks only the build.

```json
{
  "resume_path": "/Users/you/projects/resume/resume.tex",
  "file_stem": "Jane_Doe_Resume",
  "page_limit": 1,
  "can_build_pdf": true
}
```

Read `config.json` at the start of every later run. If `resume_path` no longer exists, say so
and ask for the current path rather than guessing.

---

## Workflow

### 1. Get the job description

Accept pasted text, a local file path, or a URL. If the input is only a company + title with
no detail, say so and ask for the posting text — do not assess from a job title alone.

**For a URL, try exactly two things, in this order:**

**1a. WebFetch the URL — one attempt.** If it returns the full posting, move on.

**1b. If WebFetch fails, go straight to the browser.** Do not WebSearch. Do not go hunting
for similar or alternate reqs on the same careers site, and do not fetch a pile of
neighboring job IDs — search results for job boards are stale, most of what you find will be
dead, and it burns the user's time to produce nothing.

Career sites (Workday, Greenhouse, Lever, iCIMS, and most large-company portals) commonly
serve automated fetchers a shell page while rendering the real posting only for a logged-in
human session. **Treat every one of these as "WebFetch was blocked," not as fact about the
job:**

- "This job has been filled" / "no longer accepting applications"
- HTTP 403, 410, or 404
- A page with the right `<title>` but no requirements in the body
- A cookie wall or bot-check interstitial

The user is often already logged into the careers site, which is exactly why the browser
succeeds where WebFetch does not.

**Browser retrieval (see the `claude-in-chrome` skill for tool loading):**

1. `tabs_context_mcp` first — always.
2. Open the posting in a **new** tab (`tabs_create_mcp` / `navigate`). Do not reuse or read
   the user's existing tabs unless they explicitly ask you to.
3. These pages hydrate async. An immediate `get_page_text` often returns a near-empty `<main>`
   even though the job is live — that is a loading state, not a dead posting. Wait a few
   seconds, scroll down once to force render, then `get_page_text` again. Take a screenshot
   if the text extraction still looks empty; an "Apply now" button on screen means the req is
   open regardless of what WebFetch claimed.
4. Close the tab you opened when you have the text.

**Only if the browser also fails** should you ask the user to paste the text. Say plainly
what you tried and what each attempt returned.

Save the raw text to `job-descriptions/<company>-<role>.md` so later runs can diff against
it. Record the job ID, posted date, location, salary range, and URL alongside the
requirements — and if you had to fall back to the browser, note that in the file, so a later
run doesn't re-conclude from a stale WebFetch that the posting is dead.

A posting's **posted date** is worth surfacing in the assessment: applying within the first
days of a fresh req is a genuine, if modest, advantage and is worth mentioning.

### 2. Read the master resume

Read the file at `resume_path` in full before saying anything about fit. Never assess from
memory or from a previous session's summary.

### 3. Assess fit — keep it short

**Hard budget: the entire assessment is under 150 words, before the edits block.** Being
brief is part of being right here. No preamble, no recap of what you just fetched, no
narrating your process. Lead with the verdict.

Exact shape — two lines and a short table, nothing else:

```
**Fit:** solid — <one clause on why>
**Chance:** 25–35% for an interview

| Requirement | Status |
|---|---|
| Java/Spring | 🟡 real but ended 2022; last 4 years Python |
| Data experimentation | ❌ nothing on resume |

Everything else covered. **Biggest gap:** Java recency — wording can't fix it.
```

Rules:

- **Table lists only 🟡 and ❌ rows.** Never enumerate what they already cover — end with
  "Everything else covered." A table of ten ✅ rows is the single biggest source of bloat. Cap
  at five rows; if more than five things are missing, it's a poor fit — say that instead.
- **Chance** is a percentage range for getting an interview. Anchor low: a good-but-imperfect
  match at a competitive company is 15–30%, not 70%. Missing hard requirements (years, a
  required language, clearance, location, visa) moves it down hard.
- **Stay in scope.** Assess the resume against the posting. Don't drift into referrals,
  networking, recruiter outreach, or application strategy unless the user asks for it.
- **One line on the biggest gap**, and say plainly if tailoring cannot fix it.
- Skip a "what's strong" section entirely. If something is a genuine standout, it goes in the
  one-clause why on the Fit line.
- If it's a poor fit, say so in one line and recommend not applying. Don't soften it.

### 4. Decide whether the resume needs changes at all

Often it doesn't. If the master resume already covers the posting well, say **"No changes
needed"**, build the PDF from the master as-is, and stop. Do not invent edits to look useful.

Propose changes only when there is a concrete, specific reason tied to the posting: a keyword
the ATS will screen on that is true but buried, a bullet whose emphasis is wrong for this
role, a skills line ordered against this job, or content worth cutting to make room.

### 5. Propose edits — compact, numbered, still one-by-one approval

**Max four edits. One line of WHY each. No commentary around the block.**

```
[1] Summary — surface Java/Spring
    WHY: Posting's named stack; your summary says Python only.
    NOW: ...7 years of experience building backend systems in Python, focused on...
    NEW: ...7 years building high-scale backend services in Python and Java/Spring, focused on...

[2] Skills — Spring to front of Backend & Data
    WHY: ATS screens on Spring; currently third.
    NOW: Django, FastAPI, Spring, GraphQL, ...
    NEW: Spring, Django, FastAPI, GraphQL, ...
```

Then one line: `Reply: all / 1,2 / none`. **Apply nothing until they answer.**

Add a `TRUTH CHECK:` line **only** for an edit that isn't a pure reorder or cut — i.e.
anything that rewords a claim. Pure reorders don't need one. The check still happens in your
head every time; it just doesn't always need printing.

**Length discipline.** A resume tuned to its page limit has no slack — roughly 25 added
characters wraps a line and can push content onto another page. So:

- Prefer length-neutral edits. When adding words, cut a similar number elsewhere in the same
  sentence.
- If an edit must add length, pair it with the cut that pays for it *in the same proposal*,
  so the user approves both together.
- Never propose four additive edits and discover the overflow at build time. That wastes a
  full round trip.

### 6. Truthfulness rules (do not negotiate these with yourself)

**Allowed without asking (still needs approval, but is not a truth risk):**

- Reordering bullets, sections, or skill-list items
- Rewording a true statement to use the posting's vocabulary for a technology already on the
  resume (e.g. "REST API design" → "RESTful microservice APIs" when the work was
  microservices)
- Shifting emphasis within a bullet that describes real work
- Cutting bullets, projects, or skills to make room
- Tightening prose

**Forbidden — never propose these, even if the user asks:**

- Adding a language, framework, tool, or platform not already on the resume
- Changing or adding any number, metric, percentage, date, title, or company
- Inflating scope ("led a team" when the resume says "mentored a junior engineer")
- Claiming years of experience the timeline doesn't support
- Adding degrees, certifications, or publications
- Restating a side project as professional experience

**Gray zone — ask, never assume:** if the posting wants something the user plausibly did but
the resume doesn't mention (e.g. Kafka, on-call, A/B testing), ask directly, naming the
employers from their resume: *"Posting wants Kafka — did you do that at <employer> or
<employer>?"* Add it only from their answer, in their facts.

**Cap this at two questions, one line each, and never let them block the build.** State the
default up front — "unanswered means I leave it out" — then proceed. Silence is a valid
answer; leaving something out is always the safe failure.

If the user asks you to add something untrue, decline that one item in a sentence, note the
honest alternative ("we can surface your PyTorch work instead"), and continue with the rest
of the edits.

### 7. Build the PDF

Only for a `.tex` master (`can_build_pdf: true`). For any other format, hand back the edited
content and say plainly that PDF generation needs a LaTeX source — don't improvise a
converter.

Never overwrite the master resume. Copy it, apply approved edits to the copy, then run:

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/resume-tailor/scripts/build_pdf.sh" <path-to-edited.tex> \
    --out-dir "<workspace>/resume-tailor/output" \
    --base "<file_stem from config.json>" \
    --pages <page_limit from config.json>
```

The script picks the next free number and writes **two files** into the output directory:

- `<stem>-N.pdf` — what gets submitted
- `<stem>-N.tex` — the exact LaTeX source that produced it

Always keep both. The `.tex` is what makes a past resume re-editable and diffable against the
master, so never build a PDF from a temp file you then discard, and never delete the `.tex`
as cleanup. If you ever hand-edit an existing `output/*.tex`, rebuild through the script so
the pair stays in sync rather than editing the PDF's source out from under it.

It prints both paths. If it reports a missing LaTeX package or no engine at all, see
`${CLAUDE_PLUGIN_ROOT}/skills/resume-tailor/scripts/SETUP.md`.

After building, check the `PAGES:` line — it must match `page_limit`.

**If it overflowed:**

1. `pdftotext -f <limit+1> -l <limit+1> <pdf> -` to see exactly what spilled. It's usually one
   or two orphan lines, not a real page of content.
2. Fix it yourself by trimming the edit that added the length — do not hand the user an
   overflowing PDF and ask what to cut. Tightening prose is already approved territory.
3. The script has no overwrite flag; it always takes the next free number. **Delete the
   defective pair before rebuilding** so the number is reused and a broken PDF never sits in
   `output/` where it could get submitted. (This is the one exception to "never delete the
   `.tex`" — it applies to a failed build that was never delivered, never to a resume the
   user has.)
4. If two attempts don't fit, stop and propose a specific cut. Don't keep iterating silently.

Say in one line that it overflowed and what you trimmed. Don't narrate the whole debugging
path.

### 8. Log it

Append a row to `<workspace>/resume-tailor/applications.md` (create with a header if
missing):

```markdown
| PDF | Company | Role | Date | Fit | Chance | Changes made |
|---|---|---|---|---|---|---|
| Resume-3 | Acme | Sr SWE, Payments | 2026-08-06 | Strong | 30–40% | Summary reorder, skills reorder |
```

Then, in **three lines total**: resume number, both paths (PDF and `.tex`), one line on what
changed. If nothing changed, the line is "Changes: none — master as-is" and it goes **first**,
not buried under explanation.

---

## Tone

Be the friend who tells them the truth — briefly. Don't inflate the odds to be nice, and
don't talk them out of a stretch role worth a shot.

**Brevity is a hard requirement, not a style preference.** Long output is this skill's main
failure mode. Concretely:

- No preamble, no "here's what I found," no recap of steps you just took.
- Never re-explain something already said this session.
- Lead with the answer. If the user asks "did you make the changes," the first word is yes or
  no.
- No closing paragraph offering four next steps. One offer, one line, or none.
- Tables only for 🟡/❌ rows and the edit diffs. Prose gets bullets, not paragraphs.
- Stay on assessing and tailoring; that's the job.

A complete run — assessment, edits, build, log — should read in under a minute.
