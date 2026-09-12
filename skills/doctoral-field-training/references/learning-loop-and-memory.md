# Learning loop and durable memory

Read this reference whenever initializing, advancing, or resuming a tutorial workspace.

## Ownership

The skill owns the learning state machine and the semantic memory contract. It decides what counts as a chapter, when another chapter may be generated, what learning evidence is worth retaining, and how remembered context affects later chapters.

Skill UI Studio may provide storage, retrieval, selection, annotation, and RAG infrastructure, but it is an optional adapter. The output folder is the portable source of truth so the learner can resume with another compatible agent or without Studio.

## Canonical files

```text
<output-folder>/
├── index.html
├── assets/styles.css
└── data/
    ├── tutorial.json
    └── learning-state.json
```

`tutorial.json` contains the global review design, complete chapter plan, and only the chapter bodies generated so far. `learning-state.json` contains progression, acknowledgements, learner memory, provenance, and an append-only event trail. Treat embeddings, RAG chunks, summaries, and Wiki pages as derived views that can be rebuilt from these files.

## Reading protocol

The protocol is intentionally unhurried. Its objective is durable knowledge and a self-sustaining desire to learn, not rapid content consumption. Pacing should follow comprehension: a learner may reread, investigate evidence, reproduce a result, revise an explanation, or remain with one difficult transition for as long as needed. Favor a small number of connected ideas learned deeply over broad but fragile familiarity. Do not use streaks, points, urgency, artificial scarcity, or other compulsive mechanics as a substitute for intellectual progress.

1. Initialization generates the complete table of contents and Chapter 1 only.
2. The HTML tells the learner which chapter is available and that later chapters are planned.
3. The agent waits while the learner reads outside the conversation.
4. An explicit statement such as “读完了”, “这一章读完了”, or “I finished the chapter” acknowledges reading. A question, revision request, “继续解释”, “好的”, or mere passage of time does not.
5. Record the acknowledgement before generating exactly one next chapter.
6. Acknowledging reading unlocks content progression; it does not assert mastery.
7. After the final acknowledgement, finalize the whole-book synthesis and mark the workspace complete.

Reading acknowledgement is a navigation signal, not a speed target or certificate of knowledge. When learner evidence shows fragile understanding, carry the relevant question, misconception, retrieval prompt, or practice need into later spaced returns. Do not shame, rush, or reset the learner; help them experience progress through increasingly independent explanation and use of the material.

If the learner reports that they did not understand a chapter, preserve the question or misconception and answer or revise the current chapter. Do not advance unless they also clearly say they finished reading it.

Use `node <skill-directory>/scripts/manage-progress.js remember` as soon as a durable question, reflection, misconception, or mastery observation appears. This operation does not change chapter progression.

## Memory contract

Persist only durable learning information:

- admitted field, original motivation, doctoral outcome, constraints, and stable preferences;
- planned, available, read, stale, failed, and completed states;
- exact reading acknowledgements and timestamps;
- learner-authored questions, reflections, notes, and requested revisions;
- demonstrated mastery with evidence, confidence, and provenance;
- misconceptions and unresolved questions, clearly labeled as such;
- source and chapter IDs that influenced later generation.

Do not infer mastery from reading. Do not silently turn ordinary conversation into durable memory. Never store secrets or unrelated personal details. Preserve the learner's wording for claims about their own understanding; keep agent inference separately labeled.

Later chapter generation should retrieve only relevant memory: the global thesis, causal dependencies, accepted earlier chapters, stable preferences, unresolved questions that the new chapter can illuminate, and evidenced mastery needed to calibrate exposition. Record the memory IDs used. Do not dump the full history into every prompt.

## Resume protocol

The durable resume handle is the output-folder path. A future conversation should accept requests such as:

```text
$doctoral-field-training resume /path/to/tutorial
```

Read and validate both canonical JSON files, then report the admitted field and textbook thesis, last chapter acknowledged as read, chapter currently available or ready to generate, and relevant unresolved questions or failures. Continue from that state. If canonical files disagree, do not guess: preserve them, report the conflict, and repair only with user approval. If a derived RAG or Wiki index disagrees, rebuild the derived view from canonical files.

## Optional Studio integration

When Skill UI Studio is available, declare the `learning.research-reader` profile and map the canonical records to its memory interface. Studio may enable selection questions, region questions, sidebar questions, diffs, and semantic retrieval. These interactions must write accepted durable results back to the canonical files or a lossless export compatible with them. Studio failure must not prevent local HTML reading or file-based resume.
