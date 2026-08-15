# Project — The App We Build Together

The learner learns by building **one** app, grown in layers. Each layer is where the concepts
from the matching curriculum module get applied. Teach the concepts for a layer → quiz → the
learner builds that layer → review. By the end it's a real, shipped, evaluated, monitored app
they can show in interviews.

## What it is

**A retrieval-augmented assistant over a corpus the learner chooses.** Pick the corpus in
session one so it's never the blocker — their own notes, recipes, work docs, a hobby archive,
anything text. The corpus doesn't matter; the layers do.

## Stack guidance

- Ask what they already write fluently and start there; Python is the common default. If they
  don't have a strong preference, use Python.
- Introduce **TypeScript from Layer 6** (Module 7) — it's the AI-eng default for the app
  layer. Skip this if the learner profile says they already work in it.
- Use a hosted model API and a managed vector store. Introduce a framework only *after* the
  learner has hand-built the raw version, so they understand what it abstracts.
- The learner writes the code. Guide and review; don't hand over finished code.

## The layers

**Layer 0 — Project setup** (first session only)
Before any AI code, set up the repo so the whole project is version-controlled and backed up
from day one. Have the learner:
- Create a new repo on their git host of choice.
- Initialize git locally, connect the remote, and make a first commit (a README stub is
  enough).

This repo IS the portfolio artifact — the Layer 8 README and design writeup live here, and
Layer 7 will add CI to it. Standing rule from here on: **commit at the end of every layer**
with a clear message (e.g. "Layer 3: structure-aware chunking"). One clean commit per layer
becomes a visible learning history.

**Layer 1 — Foundations + first LLM call** (Module 0)
Make a basic API call. See tokens, the system/user/assistant roles, temperature, and
streaming in action. Outcome: a script that talks to a model.

**Layer 2 — Embeddings + naive retrieval** (Module 2)
Embed the corpus, store vectors, embed a question, find the top-k closest chunks, paste them
into a prompt, get a grounded answer. Whole-document, no real chunking yet — that's
deliberate. Outcome: end-to-end semantic Q&A.

**Layer 3 — Real chunking** (Module 3, part 1)
Replace whole-doc embedding with structure + size-band chunking: split at headings, split big
sections, merge tiny ones, never split a table or code block. Outcome: visibly better, more
precise answers.

**Layer 4 — Better retrieval: hybrid + rerank** (Module 3, part 2)
Add keyword (BM25) search, fuse it with semantic search, then add a reranker over the top
candidates. Outcome: the learner sees and can explain the quality jump; understands
bi-encoder vs cross-encoder firsthand.

**Layer 5 — Evaluation** (Module 4)
Write ~20 question/answer pairs. Build an eval (point them at `ragas`) that scores retrieval
recall and answer faithfulness. Re-run it against Layer 2 vs Layer 4 and watch the numbers
move. Outcome: "I think it's better" becomes "recall went 0.6 → 0.89." This is the highest-
leverage layer in the whole project — make it solid.

**Layer 6 — Agent** (Module 5; introduce TypeScript / Module 7)
Hand-build the agent loop: tool calling, memory, multi-step questions, error recovery. Give
it tools (search-the-KB from Layer 4, a calculator, maybe one API call). Optionally rebuild
on a framework to compare. Outcome: a multi-step agent the learner wrote from scratch.

**Layer 7 — Production ops** (Module 6)
Instrument it: tracing (Langfuse/LangSmith), cost/latency logging, output guardrails, forced
structured output, retry + fallback, and the Layer-5 eval running in CI as a regression gate.
Outcome: "demo" becomes "production." If the learner comes from a security-sensitive domain,
lean into the security/governance angle — it's a differentiator.

**Layer 8 — Polish & portfolio** (Modules 8 + 9)
Clean README and a short "design decisions" writeup (why hybrid+rerank, why these chunk
rules, what the eval showed). Cover the literacy-only topics here by having the learner
*write* the rationale for prompt-vs-RAG-vs-fine-tune. Outcome: a portfolio piece, and the
raw material for a conference talk or blog post if they want one.

## Reminder

Finishing beats perfection. A rough version of all eight layers beats a polished Layer 3 they
never get past. The shipped artifact is the point.
