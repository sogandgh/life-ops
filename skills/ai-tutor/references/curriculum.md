# Curriculum — Software Engineer → AI Engineer

The full concept list this skill teaches. Each topic has a depth tag:

- **[MASTER]** — the learner should do this well and explain it cold.
- **[WORKING]** — the learner should build with it competently.
- **[LITERACY]** — the learner only needs to *discuss* it; do not drill it.

Teach in module order; it lines up with the project layers in `project.md`. Assume no prior
AI/ML knowledge unless the learner profile says otherwise, but verify quickly rather than
re-explaining what the learner clearly already has.

**Depth tags are defaults.** The learner profile in the plan file overrides them. Read it
before planning a session and adjust:

- A gap the learner named, or a topic central to their target role, gets promoted — spend
  real time and quiz it hard.
- Something they already do professionally gets demoted to a quick verification.
- Modules 3, 4, and 6 are the usual centre of gravity: retrieval quality, evaluation, and
  production ops are where most engineers new to this lane are actually thin, and they're
  what separates a demo from a system.

Whenever you change a topic's depth, note it in the profile so later sessions stay
consistent.

---

## Module 0 — Foundations & mental model [MASTER]

- What an LLM is, conceptually: a next-token predictor trained on text.
- Tokens and tokenization; why text is counted in tokens; effect on cost/limits.
- The context window: what it is, why it's finite.
- The API call: request/response, the system / user / assistant roles, conversation history
  as input.
- Generation controls: temperature, top-p, max tokens, stop sequences.
- Determinism: why the same prompt can vary.
- Streaming responses; why streaming matters for UX.
- Cost & latency model: priced per input/output token; what drives latency.
- Multimodal input at a high level.
- Hallucination: what it is, why it happens, why grounding reduces it.

## Module 1 — Prompting & context engineering [MASTER]

- Anatomy of a good prompt; system vs user prompt.
- Few-shot / in-context learning.
- Chain-of-thought / reasoning prompts and when they help.
- Structured output: JSON mode / tool-use for valid, parseable output.
- Prompt templates and variables.
- Context construction; the "lost in the middle" problem.
- Prompt versioning and management.
- Prompt injection and defenses [WORKING] — the core LLM security issue.

## Module 2 — Embeddings & vector search [MASTER]

- What an embedding is; vector space; dimensionality.
- Similarity metrics: cosine, dot product, Euclidean.
- Embedding models: choosing one, dimensions, max input length.
- Vector databases: what they store and do.
- Approximate nearest-neighbor / HNSW [LITERACY] — idea only.
- Metadata filtering before/with vector search.

## Module 3 — Retrieval-augmented generation (RAG) [MASTER]

- Why RAG exists: grounding in private/fresh/large data; less hallucination.
- Chunking: why size dominates quality; structure-aware chunking; overlap; protecting atomic
  units (tables, code).
- Keyword search: BM25 / TF-IDF intuition.
- Hybrid search and fusion (e.g. reciprocal rank fusion); why hybrid wins.
- Reranking: bi-encoder vs cross-encoder; retrieve-many-then-rerank-few.
- Contextual retrieval: prepending document context to chunks.
- Query transformation [WORKING]: rewriting, multi-query, HyDE.
- End-to-end RAG pipeline.
- Advanced patterns [LITERACY]: graph RAG, parent-document, agentic retrieval.

## Module 4 — Evaluation [MASTER]

- Why eval is central: non-determinism; "looks better" isn't evidence.
- Offline eval sets / golden datasets.
- RAG metrics: context recall/precision, faithfulness, answer relevance.
- LLM-as-judge and calibration against human labels.
- Regression testing; evals in CI.
- Prompt/version A/B testing.
- Human evaluation and labeling [WORKING].
- Public benchmarks (MMLU, etc.) [LITERACY] — weak proxy for your task.

## Module 5 — Agents & orchestration [MASTER]

- What an agent is: plan → call tool → observe → decide, in a loop.
- Function / tool calling mechanics.
- Patterns: ReAct, reflection, planning.
- Memory: short-term (conversation), long-term (persistent).
- Termination/control: stopping conditions, loop limits.
- Error recovery: failed or garbage tool outputs.
- Agent vs chain vs single call — pick the simplest that works.
- Multi-agent systems [WORKING].
- MCP (Model Context Protocol) [WORKING].
- Agent frameworks (LangGraph, LlamaIndex) [WORKING] — teach AFTER a hand-built loop, so they
  see what's abstracted.

## Module 6 — Production engineering for LLMs / LLMOps [MASTER]

For most engineers arriving from a non-AI background this is the thinnest area relative to
the job. Check the learner profile, and if it is thin here, spend real time.

- Observability & tracing (Langfuse, LangSmith).
- Cost management: tracking spend; caching; model routing; prompt compression.
- Latency optimization: streaming, parallel calls, smaller models.
- Reliability: retries, fallbacks, timeouts, rate limits.
- Caching: exact-match and semantic.
- Guardrails & output validation.
- Structured output enforcement in production.
- Content safety / moderation [WORKING].
- Prompt & pipeline versioning and deployment.
- Production monitoring: drift, regressions.
- Security & governance — prompt injection, data leakage, PII, permission-aware retrieval
  (chunks must not cross access boundaries), auditability. Promote this to **[MASTER]** for
  any learner coming from a regulated or security-sensitive domain (payments, health, gov,
  infra); it turns their existing background into a differentiator.

## Module 7 — Application & integration layer [WORKING]

- Building the service around the model (leverages existing backend skills).
- TypeScript for the AI app layer — the lane's default alongside Python.
- Streaming UIs; handling streamed responses.
- Async/concurrency for many LLM calls.
- Data ingestion pipelines for RAG corpora.
- Integrating with enterprise systems (CRM, ticketing, finance, docs).

## Module 8 — ML & model-building literacy [LITERACY — discuss only]

Cover so the learner can hold a conversation; do not drill math or code.

- How LLMs are made: pretraining, then post-training / RLHF.
- Fine-tuning: full vs LoRA/PEFT; when to fine-tune vs RAG vs prompt.
- Distillation and quantization: what and why.
- Transformers & attention: one-paragraph intuition, no math.
- Classical ML basics: supervised/unsupervised, classification/regression, train/test,
  overfitting — and when classical ML beats an LLM.
- Open vs closed models; self-hosting [LITERACY].

Goal: the learner can *recommend the right approach* (prompt / RAG / fine-tune / classical
ML) for a problem. That judgment is what's tested, not the ability to train anything.

## Module 9 — Meta-skills [WORKING]

- Reading papers/blogs at the right altitude.
- Tracking tooling and the frontier.
- Building a portfolio: a shipped, evaluated project beats certificates.
- Decomposing ambiguous problems into scoped AI solutions.
