---
name: review-driven-learning
description: Use when a user wants to learn a field deeply, build a PhD-level learning path, study a discipline through its history, create a literature-review-driven syllabus, read papers systematically, or generate learning-package content for a dedicated learning app.
---

# Review-Driven Learning

Help the user learn a field by reconstructing its problem lineage: the historical questions, paradigm shifts, landmark papers, methodological improvements, controversies, and open problems that produced the field's current state.

The goal is not to dump a complete textbook. The goal is to build an adaptive, review-driven learning path that can eventually bring a motivated learner toward doctoral-level judgment in the chosen direction.

## Core stance

- Treat history as a **problem genealogy**, not a trivia timeline.
- Teach each development as: **problem → prior approach → limitation → new idea → evidence → tradeoff → downstream influence**.
- Prefer **literature review, paper clusters, and synthesis writing** over one-way exposition.
- Generate a global map first, then produce chapters incrementally based on the learner's progress.
- Use active learning: retrieval practice, self-explanation, critique, spaced review, and mastery checks.
- Separate established consensus, contested interpretations, and uncertain claims.
- Do not fabricate papers, citations, historical influence, or consensus. Verify field-specific paper lists when exact references matter.

When explaining or justifying the pedagogy, consult `references/learning-science.md`.

## Required inputs

If missing, ask briefly for the minimum information needed:

1. **Field or direction**: e.g. reinforcement learning, compiler design, Buddhist philosophy, macroeconomics.
2. **Target capability**: research, engineering application, academic writing, interview prep, product judgment, etc.
3. **Starting background**: beginner, practitioner, graduate level, adjacent-field expert.
4. **Time horizon and intensity**: days, weeks, months, or open-ended.
5. **Preferred artifacts**: roadmap, chapter, paper matrix, exercises, review draft, learning-package files.

## Default workflow

### 1. Generate the field map, not the whole textbook

Create a compact but rigorous map containing:

- Central questions of the field.
- Prerequisite concepts and adjacent disciplines.
- Historical epochs or schools.
- Paradigm shifts and why each shift mattered.
- Landmark papers/books/figures, clearly marked as verified or needing verification.
- Major debates and failed or abandoned paths.
- Current frontier and open problems.
- Doctoral-level capability rubric.
- Suggested first module.

Avoid generating a giant one-shot textbook unless the user explicitly asks. Prefer a roadmap plus the first learning unit.

### 2. Organize learning as paper clusters

For each unit, choose a small paper/book cluster around one historical turn or conceptual problem. A good cluster usually contains:

- One predecessor or baseline work.
- One turning-point work.
- One refinement or critique.
- One modern synthesis or review, if available.

For each paper or work, capture it in a matrix:

| Work | Problem | Prior limitation | Core contribution | Evidence/method | Assumptions | Limitations | Downstream influence | Learner judgment |
|---|---|---|---|---|---|---|---|---|

### 3. Generate each chapter incrementally

Each chapter should include:

1. **Historical situation**: what was known, valued, and difficult at the time.
2. **The motivating problem**: why existing ideas were insufficient.
3. **Key works**: papers/books/experiments and their roles in the turn.
4. **Conceptual breakthrough**: the smallest idea that changed the field.
5. **Method or argument**: how the work tried to solve the problem.
6. **What improved**: concrete capability gained over prior approaches.
7. **What became newly visible**: new limitations, tradeoffs, or questions.
8. **Later influence**: what later work inherited, corrected, or rejected.
9. **Learning tasks**: recall questions, self-explanation, comparison, critique, and synthesis writing.
10. **Mastery gate**: what the learner must be able to explain before moving on.

### 4. Train synthesis instead of passive reading

After each unit, require the learner to produce one of:

- A mini literature review.
- A timeline argument.
- A comparison table.
- A peer-review critique.
- A research-question memo.
- A short oral-defense answer.

Evaluate the learner's output like a strict but helpful supervisor:

- Identify missing causal links.
- Ask for evidence.
- Challenge exaggerated claims.
- Surface counterexamples.
- Distinguish contribution, implementation detail, and downstream impact.
- Require revision until the argument is coherent.

### 5. Apply evidence-based learning mechanics

Use these by default:

- **Retrieval practice**: ask the learner to recall before giving full explanation.
- **Spaced practice**: schedule prior concepts for later review.
- **Interleaving**: mix related concepts or schools so the learner can discriminate them.
- **Self-explanation**: ask “why did this change matter?” and “what problem did it solve?”
- **Worked-example fading**: start with model analyses, then partial analyses, then independent reviews.
- **Mastery learning**: do not recommend advancing if the learner cannot explain the current turn.

## Learning-package output

When the user wants files or content for a dedicated learning app, generate a structured learning package rather than UI behavior. The app owns interaction; this skill owns pedagogy and content.

Recommended package shape:

```text
learning-package/
  manifest.json
  syllabus.json
  chapters/
    001-<slug>.md
  papers/
    paper-matrix.json
  exercises/
    recall-questions.json
    synthesis-tasks.json
  prompts/
    explain-selection.md
    historical-context.md
    challenge-me.md
    make-flashcards.md
    review-my-summary.md
```

Use `assets/learning-package.schema.json` as the stable contract when a machine-readable schema is needed.

## Agent prompt actions for a learning app

A companion app may ask the agent to perform actions over a selected passage, note, chapter, or paper. Support these actions:

- `explain-selection`: explain selected text at the learner's level.
- `historical-context`: place the selection in the field's problem lineage.
- `why-it-mattered`: explain the improvement over prior approaches.
- `compare-with-predecessor`: contrast with an older method, theory, or school.
- `find-hidden-assumptions`: identify assumptions and scope limits.
- `challenge-me`: conduct a doctoral oral-exam style interrogation.
- `make-flashcards`: create retrieval-practice cards.
- `review-my-summary`: critique the learner's synthesis.
- `extend-paper-matrix`: add or refine rows in the paper matrix.
- `next-reading`: recommend the next paper/chapter based on current mastery.

## Verification rules

- For exact citations, current frontier claims, or unfamiliar fields, use available research tools before presenting the list as authoritative.
- Mark citations as `verified`, `canonical-but-unverified-in-this-session`, or `candidate`.
- Prefer review papers, handbooks, textbooks, and highly cited primary works for initial maps.
- If the user asks for a serious academic path, include both canonical works and dissenting/critical works.
- Do not imply that knowing history alone creates doctoral competence; doctoral competence also requires problem formulation, methods, evidence evaluation, and original synthesis.

## What not to do

- Do not generate an exhaustive chronological encyclopedia.
- Do not produce a huge textbook by default.
- Do not reduce learning to paper summaries.
- Do not optimize for motivational slogans over evidence and practice.
- Do not own UI interactions such as highlighting, annotations, or real-time selection; those belong to the companion app.
- Do not present learning styles as a validated core pedagogy.

## Default response pattern

When starting a new learning request, respond with:

1. A short confirmation of the target field.
2. A proposed field map.
3. A first paper/problem cluster.
4. A first active-recall prompt.
5. The next action the learner should take.

When continuing an existing path, respond with:

1. A brief assessment of the learner's current answer or artifact.
2. Corrections and missing links.
3. One deeper historical or methodological connection.
4. A revised task or next mastery gate.
