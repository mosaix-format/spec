---
title: "Why one note at a time"
updated: 2026-09-04
tags: [post, evidence]
summary: "Measurements from a code-generation study: when each note carries its own context, the input a model needs per task stays flat as the corpus grows, and small local models produce correct output where cloud models without the format fail."
keywords: [atomic notes, bounded context, token cost, local models, code generation, task decomposition, conformance, benchmark]
entities:
  - {name: Mosaix Format, type: project}
status: sourced
rev: 0a1b2c3d4e5f
---

# Why one note at a time

## The scene

A team maintains 200 notes about a market. An agent needs to answer one question: who supplies a specific component. The question is in one note, and that note says so in its summary. But the agent has no way to know which note matters, so it receives all 200.

At 200 notes the cost is tolerable. At 2,000 it is not. The input grows linearly with the corpus, the answer does not get better, and the bill does. Worse, the longer the context, the more likely the model is to pick up a stale paragraph three screens away and contradict the note that actually answers the question.

This is not a retrieval problem. A retrieval layer can shrink the window, but it still selects chunks of text that carry no metadata about themselves — no summary, no declared entities, no explicit dependencies. The model receives raw text and must infer what it is about. The format of the notes does not help.

## The hypothesis

If each note carries its own context — a summary that says what it contains, entities that say what it is about, typed relations, and explicit links to the notes it depends on — then the input needed for a task on that note is the note itself plus its direct dependencies. That input does not grow with the size of the corpus. It is bounded by the note, not by the vault.

The Mosaix Format prescribes exactly this: nine frontmatter keys on every note (§3.1 of the specification), a graph of wikilinks (§4), and a rule that one note answers one question (R1). The question is whether the prescription works in practice, and what it costs.

## How we measured

We ran a code-generation study. The task was to produce a complete Python package — ten dataclasses, four enums, serialisation, a test suite, packaging — split into 28 atomic tasks. Each task had a written contract specifying its purpose, its inputs, its output file, and its dependencies on other tasks. Each task received roughly 600 tokens of context. The same package was also generated in a single prompt containing the full specification, roughly 7,800 tokens.

We measured the token-compression ratio on a 30-function benchmark (TCG-30): the format achieved a 5.72x reduction (±0.20, N=5 runs, 95% confidence interval). The per-unit cost stayed flat at roughly 600 tokens per task regardless of corpus size, while the full-context baseline grew from roughly 544 tokens for a single function to roughly 4,055 tokens for thirty.

These measurements are ours. They have not yet been replicated by a third party. A public benchmark is in preparation (see "What's next" on the project home page).

**What was controlled.** The model, the API endpoint, the temperature (0), and the evaluation criteria (structure correct, tests passing) were held constant across all runs. The variable was the input: one task at a time versus the full specification at once. In the end-to-end runs of the same study, 53 of 56 tasks completed correctly (94.6%), 20 of 20 at the first attempt; running independent tasks in parallel gave a 1.79x wall-clock speedup.

**What was not controlled.** The task contracts were written by the same person who designed the format. The study covers code generation, not knowledge retrieval. The tasks are deterministic (there is one correct output per task), which favours bounded context; open-ended tasks may behave differently.

| Condition | Context per task | Tasks completed | Cost | Frozen correct |
|---|---|---|---|---|
| Full spec, single prompt, 6 cloud models | ~7,800 tok | varies by model | $0.002–0.233 | 0 of 6 models |
| One task at a time, same 6 cloud models | ~600 tok | 28/28, all models | $0.003–0.319 | 6 of 6 models |
| One task at a time, 8 models from 4B to Opus | ~600 tok | 28/28, all models | $0.00–1.09 | 8 of 8 models |

## The result that matters most: local models

Six cloud models received the full specification in a single prompt. None produced a package with correct frozen/mutable annotations. Four of six did not generate the entry point file. The strongest model, DeepSeek V4 Flash, came closest at 27 out of 28 tests passing, but still missed the frozen constraint.

The same six models, given one task at a time with roughly 600 tokens of context each, all completed 28 out of 28 tasks with frozen annotations correct.

Then we ran the same tasks on local models, on a consumer GPU with 12 GB of VRAM, at zero API cost. Qwen 3.5 9B scored 40 out of 40 on pytest (100%), the first local model to reach a perfect score on this suite. Gemma 4 E2B, a 2-billion-parameter model, scored 45 out of 47 (96%); the two failures were a frozen annotation on one type and a test the model invented with incorrect logic — the source code it produced was structurally correct. Qwen 3.5 4B scored 28 out of 28 tasks completed. Eight models from 4B to Opus all completed 28 out of 28 on the same task set. Claude Opus 4.6 cost $1.09 per run; DeepSeek V4 Flash cost $0.003 for identical output.

This is the consequence that matters most. When the context per task is small and self-contained, the model becomes a per-agent choice. A 4-billion-parameter model on a laptop produces the same package that a flagship API model does. The data does not leave the machine. The cost per run is zero.

We do not claim that small models are always sufficient. The tasks were deterministic and well-specified. On ambiguous or creative tasks the advantage of a larger model may reassert itself. What the measurements show is that for tasks with a clear contract, the contract matters more than the parameter count. The dominant source of failure in the initial runs was not the models — it was an ambiguity in our own task contracts. When we fixed that ambiguity, models that had previously failed began producing correct output without any change to their weights or configuration.

## What the format does not do

The format does not make a model more capable. It does not replace retrieval: a vault of 10,000 notes still needs a way to find the right one. It does not make facts true: a note marked "sourced" with a wrong number is still wrong. It does not guarantee that an agent will use the metadata correctly.

What it does is make the content of each note verifiable from the note itself. The summary says what the note contains; the entities say what it is about; the links say what it depends on; the rev hash says whether the metadata is current. A checker (§10) can verify all of this from the files, offline, with no dependencies. The format turns implicit conventions into explicit, testable structure.

## Further reading

The full specification is at [spec.html](spec.html). The reference checker, `audit_reference.py`, is in the repository. Both are licensed under CC BY-SA 4.0.
