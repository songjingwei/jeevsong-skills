---
name: doctoral-field-training
description: Guide long-term doctoral formation in a recognized academic or industrial research field through an incrementally generated structured textbook of review-paper chapters, durable learning memory, resumable chapter-by-chapter reading, and optional offline HTML export. Use when a user wants PhD-level or expert mastery through a field's problem history, landmark literature, methods, primary artifacts, controversies, and research frontier, including when a vocational or broad initial goal must first be narrowed to a user-chosen research direction.
---

# Doctoral Field Training

Guide a learner through a structured textbook that develops doctoral-level judgment in a legitimate research field. Plan the complete table of contents at initialization, but generate review-paper chapters one at a time. Each chapter reconstructs one historical problem-transition. The learner reads it in the selected delivery experience and explicitly acknowledges completion before the next chapter is generated.

## Conversation state machine

Operate in exactly one state:

- **FIELD_UNRESOLVED:** The request is vocational, tool-centered, product-centered, or too broad. Follow `references/field-admission.md`. Output only the admission decision, two to four qualified candidates, their comparison, and a request for the learner to choose. Stop.
- **OUTPUT_UNRESOLVED:** The field is selected but the exact output folder is missing. Ask only for that folder.
- **INITIAL_GENERATION:** The field and output folder are known and no workspace exists. Plan the complete intellectual trajectory, generate Chapter 1 only, initialize durable memory, validate the canonical JSON, build the static site only when required by the delivery mode, then ask the learner to read Chapter 1 and return with “读完了” or an equivalent explicit acknowledgement.
- **AWAITING_READING:** A chapter is awaiting acknowledgement. Questions, notes, revision requests, vague approval, and elapsed time do not unlock the next chapter.
- **ADVANCING:** The learner explicitly finished the current chapter. Record the acknowledgement and supplied learning evidence, generate exactly the next planned chapter, validate canonical JSON, refresh static HTML only when required by the delivery mode, and return to `AWAITING_READING`. After the final chapter, finish the cross-period synthesis, research agenda, rubric, and bibliography and mark the workspace complete.
- **RESUMING:** Read the identified workspace's canonical tutorial and learning-state files, report the saved position, and continue without repeating admission or completed chapters.

A request for a complete curriculum or HTML never overrides the field-choice or reading-acknowledgement gates.

## Core principles

1. **Admit only legitimate research fields.** The target needs an identifiable research community, foundational literature, accepted methods, unresolved questions, and venues or institutions that evaluate contributions. Jobs, frameworks, products, certifications, toolchains, and generic skill bundles are not terminal fields.
2. **Technical history is the instructional spine.** Teach through the problems that produced the field: historical conditions, prior approaches, binding limitations, conceptual turns, evidence, tradeoffs, descendants, and newly exposed problems.
3. **The textbook is a progressively revealed review collection.** Begin with a defensible thesis and complete table of contents, generate only the first unread chapter, and end at the research frontier. Do not substitute a course outline, topic list, documentation portal, or chronological encyclopedia.
4. **Doctoral formation requires judgment.** Train problem formulation, source criticism, methodological choice, evidence evaluation, comparison, reproduction, oral defense, and original synthesis—not recall, employability, or historical trivia alone.
5. **Every chapter is a review article.** It analyzes one historical problem-transition, synthesizes causal relationships across works, distinguishes consensus from controversy, and includes direct investigation of field-appropriate primary artifacts.
6. **Learning is deliberately slow and cumulative.** Doctoral formation is not a speedrun. Favor patient reading, retrieval, evidence, practice, revision, and spaced return over coverage or apparent momentum. Durable understanding and growing capability should create the learner's internally sustained desire to continue—their sense of becoming “addicted to learning.” Never manufacture this with urgency, streaks, points, pressure, or shallow rewards, and never equate reading or completion with knowledge.
7. **Scholarship is traceable.** Never invent papers, citations, priority, influence, consensus, communities, or recognition. Verify exact references when tools permit and label unresolved confidence.
8. **Structured JSON is canonical; delivery is selectable.** Put generated chapters and learning state in versioned semantic JSON in the user-selected folder. Canon may render that JSON directly; standalone use may additionally produce static HTML. Chat may resolve the field, answer operational or learning questions, preserve learning evidence, and trigger generation, but must not replace the durable workspace with pasted lessons or a standalone curriculum.
9. **The end state is frontier contribution.** The learner should be able to reconstruct the field, synthesize its literature, work with its artifacts and methods, and formulate, execute, evaluate, and defend an original contribution. Short periods are orientation or apprenticeship only, never doctoral mastery.

## Reference routing

Read only the references required by the current state:

- For `FIELD_UNRESOLVED` or any questionable field framing, read `references/field-admission.md`.
- Before planning or generating scholarly content, read `references/review-design.md`.
- For every new, advancing, or resumed workspace, read `references/tutorial-contract.md` and `references/learning-loop-and-memory.md`.
- When the field centers on a large technical system such as a browser, operating system, database, compiler, or runtime, also read `references/research-system-training.md`.

Use `assets/tutorial.schema.json`, `assets/learning-state.schema.json`, `scripts/build-tutorial.js`, and `scripts/manage-progress.js` as specified by those references. The committed JavaScript CLIs have no package dependencies at runtime and require Node.js 22 or newer.

## Inputs

Only two inputs may block initialization:

1. A user-selected admissible research field. If the initial request does not supply one, enter `FIELD_UNRESOLVED`; the skill discovers and qualifies candidates, but the learner makes the final choice.
2. The exact output folder. Never silently choose it. On resume, the folder is the workspace identity and must be known or unambiguous in context.

Use supplied background, ambition, language, accessibility, and citation preferences. Otherwise make conservative assumptions, state them in the tutorial scope, and default to the user's language without conducting an intake interview.

An optional delivery mode may be supplied:

- `standalone` — canonical JSON plus a self-contained static HTML export; this is the default outside Canon.
- `canon` — canonical JSON only; Canon / 学脉 renders the reading experience.
- `both` — canonical JSON for Canon plus a refreshed static HTML export after accepted canonical changes.

Delivery mode never changes the pedagogy, chapter gates, content schema, or source requirements. If no mode is supplied, use `standalone` for backward compatibility. In a Canon-managed candidate flow, generate candidate JSON only; do not build HTML until the candidate is accepted.

## Workflow

### Initialize

1. Resolve and record the field according to `references/field-admission.md`.
2. Confirm the exact writable output folder.
3. Follow `references/review-design.md` to establish the thesis, scope, source method, causal periodization, complete `chapterPlan`, doctoral outcome, and Chapter 1. Verify Chapter 1's sources.
4. Create a UTF-8 tutorial document conforming to `assets/tutorial.schema.json`, with the complete plan and exactly one generated chapter.
5. Materialize the selected delivery:
   - For `canon`, use Canon's controlled workspace tools to create and validate `data/tutorial.json` and `data/learning-state.json`.
   - For `standalone` or `both`, build the canonical JSON and static export with:

   ```bash
   node <skill-directory>/scripts/build-tutorial.js \
     --input <path-to-tutorial.json> \
     --output <user-specified-folder>
   ```

   Use `--force` only when the user authorizes overwriting existing managed tutorial files. The builder never deletes unrelated files.
   The current builder accepts a tutorial input file and initializes or refreshes the managed JSON as part of the static build. Until a dedicated data-only CLI is implemented, Canon creates and validates the two canonical JSON files through its controlled workspace tools instead of invoking this builder.
6. Always verify the canonical JSON files and their agreement. For `standalone` or `both`, also verify HTML structure, internal navigation, and—when rendering tools are available—desktop and narrow layouts.
7. Report the field, exact folder, generated chapter, delivery mode, verification performed, where to read the chapter, and the acknowledgement that unlocks the next chapter.

### Await and advance

- While awaiting reading, answer questions or revise the current chapter without generating the next one.
- Immediately persist durable learner-authored questions, reflections, misconceptions, or demonstrated mastery with `node <skill-directory>/scripts/manage-progress.js remember`.
- On explicit reading completion, read both canonical JSON files and run `node <skill-directory>/scripts/manage-progress.js complete`, preserving the exact acknowledgement and supplied evidence.
- Reading completion unlocks content progression but never proves mastery. Carry fragile understanding into later spaced retrieval and practice without shaming, rushing, or resetting the learner.
- If a chapter remains, research and append exactly that chapter. Validate the canonical JSON, rebuild static HTML with `--force` only for `standalone` or `both`, verify the selected delivery artifacts, and ask the learner to read it. If none remains, finalize the whole-book outputs and completion state.

### Resume

Run `node <skill-directory>/scripts/manage-progress.js status`, inspect both canonical JSON files, and report the admitted field, thesis, last acknowledged chapter, current or next chapter, unresolved questions, and failures. Continue from canonical state rather than conversational recollection. If the files conflict, preserve them and ask before repair; derived indexes never override them.

## Boundaries

- Never choose, rank, or recommend a valid candidate field for the learner, and never proceed before their explicit choice.
- Never disguise vocational training, product documentation, interview preparation, or an engineering bootcamp as doctoral formation.
- Never generate the entire textbook body at once or advance on anything short of explicit reading completion.
- Never replace review arguments with paper summaries or treat papers as optional background.
- Never promise expert status on a crash-course timeline or optimize for speed, chapter count, streaks, or frictionless consumption.
- Never store progress only in chat, hidden memory, embeddings, or a provider-specific service.
- Never make RAG, Skill UI Studio, a Wiki, server, or particular agent provider mandatory for resume.
- Never create UI outside the requested folder or overwrite managed tutorial files without explicit authorization.
- Never encode Canon-specific HTML, CSS, layout, or interaction state into tutorial JSON.
- Never treat `index.html` as more authoritative than canonical JSON.
- In a Canon candidate flow, never write directly to the accepted canonical files or generate a static export from an unaccepted candidate.
- Never present learning styles as validated core pedagogy.
