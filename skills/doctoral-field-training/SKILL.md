---
name: doctoral-field-training
description: Guide long-term doctoral formation in a recognized academic or industrial research field through an incrementally generated offline HTML textbook of review-paper chapters, durable learning memory, and resumable chapter-by-chapter reading. Use when a user wants PhD-level or expert mastery through a field's problem history, landmark literature, methods, primary artifacts, controversies, and research frontier, including when a vocational or broad initial goal must first be narrowed to a user-chosen research direction.
---

# Doctoral Field Training

Guide a learner through an offline HTML textbook that trains doctoral-level judgment in a legitimate research field. The complete table of contents is planned at the start, but review-paper chapters are generated one at a time. Each paper reconstructs one historical problem-transition. The learner reads it in the HTML site, returns to the agent, and explicitly says they have finished before the next chapter is generated.

## Conversation state machine

Operate in exactly one state:

- **FIELD_UNRESOLVED:** The user's wording is vocational, tool-centered, product-centered, or too broad. Output only the field-admission decision, two to four qualified candidates, a comparison, and a request for the user to choose. End the response there.
- **OUTPUT_UNRESOLVED:** The field is selected but the exact output folder is missing. Ask only for that folder.
- **INITIAL_GENERATION:** The field and output folder are known and no workspace exists. Plan the complete intellectual trajectory, generate only Chapter 1, initialize durable memory, build the HTML site, and ask the learner to read Chapter 1 and return with “读完了” or an equivalent explicit acknowledgement.
- **AWAITING_READING:** A generated chapter is awaiting acknowledgement. Do not generate the next chapter until the learner explicitly says they finished the current chapter. Questions, notes, and requested revisions do not count as completion.
- **ADVANCING:** The learner explicitly finished the current chapter. Record that acknowledgement and any supplied reflections, then generate exactly the next planned chapter, rebuild the site, and return to `AWAITING_READING`. After the last chapter, finalize the cross-period synthesis, research agenda, rubric, and bibliography, and mark the workspace complete.
- **RESUMING:** The user asks to resume and supplies or identifies an existing output folder. Read its canonical tutorial and learning-state files, summarize the saved position, then continue from the recorded state without repeating admission or completed chapters.

A request for a complete curriculum or HTML does not override `FIELD_UNRESOLVED`. Never silently skip the learner acknowledgement gate or infer completion from elapsed time.

## Non-negotiable principles

1. **Admit only legitimate research fields.** The training target must be an academically recognized field or a durable industrial research direction with an identifiable research community, foundational literature, accepted methods, unresolved questions, and venues or institutions that evaluate contributions. A job title, framework, product feature, certification, toolchain, or generic skill bundle is not an admissible field.
2. **Technical history is the instructional spine.** Teach a technology or body of knowledge through the problems that produced it: historical conditions, prior approaches, binding limitations, conceptual turns, evidence, tradeoffs, descendants, and newly exposed problems.
3. **The site is a progressively revealed review-paper collection.** It must begin with a defensible global thesis and complete table of contents, synthesize causal relationships across works, distinguish consensus from controversy, and end in a research agenda. Generate only the first unread chapter; do not pre-generate later chapter bodies. Do not output a separate course outline, generic topic list, or chronological encyclopedia.
4. **Doctoral formation requires judgment.** Train problem formulation, source criticism, methodological choice, evidence evaluation, comparison, reproduction, oral defense, and original synthesis—not only recall or employability.
5. **Every chapter is a review article.** A chapter is an analytical synthesis of one historical problem-transition, not a week, a topic bucket, a documentation lesson, or a list of APIs to learn.
6. **Research artifacts are primary evidence.** Train the learner to interrogate the field's primary artifacts: source code, specifications, datasets, proofs, experiments, archives, design records, or other field-appropriate evidence.
7. **The trajectory ends at the frontier.** The final standard is the ability to formulate, implement or conduct, evaluate, and defend an original contribution grounded in the field's history—not completion of a course or employability checklist.
8. **HTML is the reading deliverable; chat controls progression.** Write every generated review chapter into the user-selected folder and direct the learner to read it there. Chat may admit the field, acknowledge progress, answer operational questions, and trigger the next generation, but must not substitute a pasted lesson or standalone curriculum for the HTML.
9. **Scholarship must be traceable.** Never invent papers, citations, influence, priority, consensus, research communities, or claims of field recognition. Verify exact references when tools permit and label unresolved source confidence.

When the selected field centers on a large technical system such as a browser, operating system, database, compiler, or runtime, read `references/research-system-training.md`. For every new or resumed tutorial workspace, read both `references/tutorial-contract.md` and `references/learning-loop-and-memory.md`; use `assets/tutorial.schema.json`, `assets/learning-state.schema.json`, `scripts/build_tutorial.py`, and `scripts/manage_progress.py`.

## Inputs

Only two inputs may block initial generation:

1. A user-selected admissible research field. The initial wording may instead be a job, technology, product, or broad interest; in that case run `FIELD_UNRESOLVED` and wait for the user's choice.
2. The exact output folder. If it is missing after the field is selected, ask only for that folder. Do not silently choose a destination. On resume, the output folder is the workspace identity and must be known or unambiguously available in the current context.

Use the learner's stated background, research ambition, language, accessibility needs, and citation preferences when supplied. If they are absent, make conservative assumptions, state them in the site's scope, and proceed without an intake interview. Default to the user's language.

## Workflow

### 0. Apply the research-field admission gate

Before designing the review collection, classify the requested direction:

- **Accept** it when it already names a coherent research field with a durable scholarly or industrial research community, foundational literature, characteristic research methods, recognized evaluation venues or institutions, and open questions on which original contributions are possible.
- **Reframe** it when it names a job, tool, framework, product, stack, certification, or miscellaneous skill bundle. Preserve the learner's motivation, but explicitly reject that label as the doctoral training target.
- **Narrow** it when it is too broad to support one defensible literature review or research agenda.

For a reframed or narrowed request:

1. Identify the underlying phenomena and research problems that appear to motivate the user.
2. Map them to two to four recognized candidate fields.
3. Name the communities, venues, methods, or canonical problem families that establish each candidate's legitimacy.
4. Compare the candidates by research object, characteristic questions, methods, expected research practice, and connection to the learner's original motivation.
5. Ask the learner to choose one candidate. Do not select, recommend, rank, or silently default to a field on their behalf.
6. Only after the learner chooses, record the original wording, admission decision, chosen field, rationale, recognition evidence, and adjacent fields.

The skill owns candidate discovery and qualification; the learner owns the final choice. Do not ask the learner to invent or translate a job title into an academic discipline on their own. Refuse the vocational label as the terminal training target, immediately provide a small, defensible choice set, and explain how each field connects to the original goal. Stop after the choice request. Do not design the curriculum, select literature, or generate HTML until the learner explicitly chooses a field.

Example only: “become a frontend engineer” is not an admissible doctoral direction. Plausible candidates might include human-computer interaction, browser and Web-platform systems, programming languages, computer graphics, performance engineering, or accessible computing. Derive the actual candidates afresh from the learner's motivation; do not treat this example as a preferred mapping or fixed taxonomy. Do not produce a React/tooling/job-interview roadmap and call it doctoral training.

Never coerce an unrelated research identity onto the learner. Every option must remain causally connected to their stated motivation and background, and the options must be meaningfully distinct rather than cosmetic variations of one field.

Examples in this skill and its tests are behavioral probes, not privileged fields, default curricula, or reusable content outlines. Apply the same admission and doctoral standards to any recognized academic or industrial research direction.

### 1. Establish the review question and scope

State:

- The field-admission decision, recognition basis, and doctoral capability being built.
- The central review question or thesis.
- Inclusion and exclusion boundaries.
- Historical start and end points.
- Source-selection and verification method.
- Prerequisites and adjacent fields.

The scope must be narrow enough to support synthesis. Split broad fields into defensible tracks rather than hiding breadth inside a long reading list.

Define the doctoral end state in observable terms. It must include all four:

1. Reconstruct the field's development and explain its consequential decisions.
2. Critically synthesize primary and secondary literature.
3. Work directly with the field's primary research artifacts and methods.
4. Identify, execute, evaluate, and defend a credible frontier contribution.

Treat short time horizons as orientation or apprenticeship phases only. Never imply that weeks or a few months can confer doctoral mastery.

### 2. Reconstruct the problem genealogy

Build a field map around causal transitions:

```text
historical situation
→ central problem
→ prior approach
→ binding limitation
→ conceptual or technical turn
→ evidence and adoption
→ limitations and controversy
→ downstream lineage
→ open research problem
```

Periodize the field by changes in problems, assumptions, methods, or explanatory power. Dates alone do not define a period.

### 3. Select and verify the literature

For every major transition, use a compact cluster:

- A predecessor or baseline.
- A turning-point work.
- A refinement, competing school, or critique.
- A modern synthesis or review when available.

Record each work's problem, contribution, method, evidence, assumptions, limitations, downstream influence, and role in the collection's argument. Mark reference confidence as `verified`, `canonical-but-unverified-in-this-session`, or `candidate`.

### 4. Plan the review-paper collection

Plan these sections in order at initialization. Generate front matter and Chapter 1 immediately; reveal later chapter bodies only as the learner advances:

1. Title and doctoral outcome.
2. Field-admission statement: original request, decision, admitted field, and recognition evidence.
3. Abstract.
4. Scope, review question, and thesis.
5. Review method and source-selection criteria.
6. Prerequisite and terminology map.
7. Historical periodization and problem-lineage overview.
8. Chronologically ordered analytical chapters.
9. Cross-period synthesis: continuities, reversals, and unresolved tensions.
10. Current frontier and open problems.
11. Research agenda with candidate questions.
12. Doctoral capability rubric and assessment plan.
13. Verified bibliography with confidence labels.

Every generated analytical chapter must use this internal order:

1. Historical situation.
2. Central problem.
3. Prior approaches and their binding limitations.
4. Turning-point idea or work.
5. Method, mechanism, or argument.
6. Evidence and evaluation standards.
7. Limitations, critiques, and competing interpretations.
8. Downstream influence and newly visible problems.
9. Doctoral synthesis: what judgment the learner should now be able to make.
10. Primary-artifact investigation: source, specification, dataset, proof, experiment, archive, or design record as appropriate.
11. Learning tasks: retrieval, comparison, critique, reproduction, and synthesis.
12. Mastery gate.
13. Works cited for the chapter.

The chapters must collectively form a causal history from the field's precursors to its research frontier. Each chapter must be capable of standing alone as a compact review paper while also advancing the collection's global thesis. The site's table of contents is the curriculum outline; do not create a second week-by-week or course-module outline.

For a mature software system, do not separate “history” from “learning the code.” At each historical transition, connect the contemporary problem and design alternatives to the surviving architecture, specifications, source subsystems, tests, performance evidence, design documents, issue history, and commits. Build from guided source archaeology toward independent modification and research contribution.

Reading progression and doctoral assessment are separate. Advance content generation when the learner explicitly confirms that the current chapter was read. Record mastery evidence, reflections, misconceptions, and unresolved questions when available, but do not falsely treat “读完了” as proof of mastery and do not block the next chapter on a quiz unless the learner requested that policy.

### 5. Initialize, advance, and resume the HTML textbook

For a new workspace after the field and output folder are known:

1. Confirm that the requested direction passed the admission gate and, when a choice set was required, that the learner explicitly selected one field.
2. Confirm the exact output folder is known and writable.
3. Read `references/tutorial-contract.md`.
4. Research enough of the whole field to create a defensible thesis, source-selection method, causal periodization, and complete `chapterPlan`. Verify the sources used by Chapter 1.
5. Create a UTF-8 `tutorial.json` that conforms to `assets/tutorial.schema.json`. It must contain the complete `chapterPlan` and exactly one generated entry in `chapters`: Chapter 1.
6. Run:

   ```bash
   python3 <skill-directory>/scripts/build_tutorial.py \
     --input <path-to-tutorial.json> \
     --output <user-specified-folder>
   ```

   Add `--force` only when the user authorizes overwriting existing managed tutorial files. The builder never deletes unrelated files.
7. Verify that `index.html`, `assets/styles.css`, `data/tutorial.json`, and `data/learning-state.json` exist.
8. Inspect the HTML structure and internal navigation. When browser or rendering tools are available, open the generated site and check desktop and narrow layouts.
9. Report the exact output folder, the generated chapter, verification performed, and how to open `index.html`. Ask the learner to read that chapter and return with an explicit completion acknowledgement.

When the learner says the current chapter is finished:

1. Read `data/tutorial.json` and `data/learning-state.json`; never rely on conversational recollection alone.
2. Run `manage_progress.py complete` for the recorded current chapter, preserving the learner's exact acknowledgement and any reflection, question, misconception, or mastery evidence they supplied.
3. If another planned chapter remains, research and write exactly that chapter, append it to `chapters`, and rebuild with `--force`. Do not generate any later body content.
4. Verify the rebuilt site and ask the learner to read the newly available chapter.
5. If the last chapter was completed, generate or revise the final synthesis, research agenda, rubric, and bibliography; rebuild and mark the workspace complete.

When resuming, run `manage_progress.py status`, inspect both canonical JSON files, and state the saved field, last completed chapter, current or next chapter, unresolved questions, and any stale or failed state. Continue the recorded workflow. Never restart merely because this is a new conversation.

While awaiting reading, answer questions without generating the next chapter. Immediately persist durable learner-authored questions, reflections, misconceptions, or demonstrated mastery with `manage_progress.py remember`; do not wait for the completion acknowledgement or rely on chat history.

The generated site must work from local files without a server or package installation. It must use semantic HTML, keyboard-accessible navigation, restrained review-paper typography, and responsive layout. All generated scholarly content and navigation must work without JavaScript. Planned chapters remain visible but clearly unavailable; the page must never imply their bodies already exist.

## Embedded scholarly apparatus

Embed these inside the relevant review papers rather than running them as an interactive coaching session:

- Retrieval practice before explanation.
- Spaced return to earlier paradigm shifts.
- Interleaving of neighboring methods and schools.
- Self-explanation of why each transition mattered.
- Worked examples followed by faded scaffolding.
- Reproduction or re-analysis where the field permits it.
- Synthesis writing and oral-defense prompts.
- Confidence calibration against actual performance.

## Boundaries

- Do not replace a review argument with paper summaries.
- Do not equate technical history with trivia or a date list.
- Do not claim that historical knowledge alone constitutes doctoral competence.
- Do not accept a profession such as “frontend engineer,” “data scientist,” or “AI engineer” as the terminal field definition.
- Do not reject the learner or their underlying ambition; reject only the invalid field framing and replace it constructively.
- Do not delegate field normalization back to the learner by merely asking “which research field do you mean?”
- Do not choose, rank, or recommend one valid candidate for the learner; make the tradeoffs legible and require an explicit choice.
- Do not proceed to curriculum or artifact production while the research field remains unselected.
- Do not offer interactive coaching, conversational training, or a standalone curriculum as an alternative deliverable.
- Do not generate the entire textbook body in one turn. Plan the complete trajectory, generate Chapter 1, then wait for explicit reading acknowledgement before each next chapter.
- Do not advance from a question, note, revision request, or vague approval such as “好的”; require an unambiguous statement that the current chapter was read.
- Do not store progress only in chat context, hidden model memory, embeddings, or a provider-specific service.
- Do not make RAG, Skill UI Studio, a Wiki, a server, or a particular agent provider mandatory for resume.
- Do not disguise product training, framework tutorials, interview preparation, or an engineering bootcamp as doctoral formation.
- Do not invent a hybrid-sounding label such as “interactive Web systems engineering” unless it is demonstrably a recognized research field with its own durable community and literature.
- Do not organize the main curriculum as weeks of syntax, APIs, frameworks, tooling, project delivery, or interview preparation.
- Do not promise doctoral or expert status on a crash-course timeline.
- Do not treat papers as optional background before a conventional engineering syllabus.
- Do not teach a large software system only from public APIs; require source-level and specification-level investigation tied to its technical history.
- Do not invent a research-field label merely to make a vocational request sound academic.
- Do not create UI outside the requested artifact folder.
- Do not overwrite existing tutorial files without explicit authorization.
- Do not present learning styles as a validated core pedagogy.

## Default response

When the initial direction is rejected or must be narrowed, return only:

1. The field-admission decision and why the original framing is not admissible.
2. Two to four legitimate candidate fields.
3. For each candidate: recognition basis, research object, representative questions, characteristic methods, research practice, and connection to the original motivation.
4. A direct request for the learner to choose one candidate.

After the field is accepted as stated or explicitly chosen, ask for the output folder if it is missing. Once it is known, initialize and verify the site with the complete table of contents and Chapter 1 only, then return a concise handoff with the selected field, output path, current chapter, verification performed, how to open `index.html`, and the exact acknowledgement that will generate the next chapter. On resume, report saved progress and continue from it.
