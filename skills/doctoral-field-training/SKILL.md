---
name: doctoral-field-training
description: Generate a complete offline HTML collection of review-paper-style tutorials for doctoral formation in a recognized academic or industrial research field. Use when a user wants PhD-level or expert mastery through a field's problem history, landmark literature, methods, primary artifacts, controversies, and research frontier, including when a vocational or broad initial goal must first be narrowed to a user-chosen research direction.
---

# Doctoral Field Training

Generate an offline HTML site that trains doctoral-level judgment in a legitimate research field. The site is a collection of interconnected review papers: each paper reconstructs one historical problem-transition, and the table of contents is the learning outline from precursors to the research frontier.

## Hard state boundary

Operate in exactly one of two states:

- **FIELD_UNRESOLVED:** The user's wording is vocational, tool-centered, product-centered, or too broad. Output only the field-admission decision, two to four qualified candidates, a comparison, and a request for the user to choose. End the response there.
- **FIELD_SELECTED:** The user explicitly chose a candidate, or originally named an admissible research field. Generate the complete review-paper collection site under the requirements below. If the output folder is missing, ask only for that folder.

Never combine these states in one response. A request for a complete curriculum or HTML does not override `FIELD_UNRESOLVED`.

## Non-negotiable principles

1. **Admit only legitimate research fields.** The training target must be an academically recognized field or a durable industrial research direction with an identifiable research community, foundational literature, accepted methods, unresolved questions, and venues or institutions that evaluate contributions. A job title, framework, product feature, certification, toolchain, or generic skill bundle is not an admissible field.
2. **Technical history is the instructional spine.** Teach a technology or body of knowledge through the problems that produced it: historical conditions, prior approaches, binding limitations, conceptual turns, evidence, tradeoffs, descendants, and newly exposed problems.
3. **The site is a review-paper collection.** It must make a defensible global thesis, define scope and selection method, synthesize causal relationships across works, distinguish consensus from controversy, and end in a research agenda. Do not output a separate course outline, generic topic list, or chronological encyclopedia.
4. **Doctoral formation requires judgment.** Train problem formulation, source criticism, methodological choice, evidence evaluation, comparison, reproduction, oral defense, and original synthesis—not only recall or employability.
5. **Every chapter is a review article.** A chapter is an analytical synthesis of one historical problem-transition, not a week, a topic bucket, a documentation lesson, or a list of APIs to learn.
6. **Research artifacts are primary evidence.** Train the learner to interrogate the field's primary artifacts: source code, specifications, datasets, proofs, experiments, archives, design records, or other field-appropriate evidence.
7. **The trajectory ends at the frontier.** The final standard is the ability to formulate, implement or conduct, evaluate, and defend an original contribution grounded in the field's history—not completion of a course or employability checklist.
8. **HTML is the only training deliverable.** After the field and output folder are known, write the complete static review collection into that folder. Do not substitute interactive coaching, a chat-based lesson, a standalone curriculum, or pasted HTML.
9. **Scholarship must be traceable.** Never invent papers, citations, influence, priority, consensus, research communities, or claims of field recognition. Verify exact references when tools permit and label unresolved source confidence.

When the selected field centers on a large technical system such as a browser, operating system, database, compiler, or runtime, read `references/research-system-training.md`. When producing HTML, read `references/tutorial-contract.md` and use `assets/tutorial.schema.json` plus `scripts/build_tutorial.py`.

## Inputs

Only two inputs may block generation:

1. A user-selected admissible research field. The initial wording may instead be a job, technology, product, or broad interest; in that case run `FIELD_UNRESOLVED` and wait for the user's choice.
2. The exact output folder. If it is missing after the field is selected, ask only for that folder. Do not silently choose a destination.

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

### 4. Compose the review-paper collection

The complete site must contain these sections in order:

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

Every analytical chapter must use this internal order:

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

Do not advance merely because the learner has read the material. Advance when the learner can reconstruct the causal transition, defend its evidence, compare alternatives, and identify a researchable gap.

### 5. Produce the complete HTML collection

After the field is selected and the output folder is known:

1. Confirm that the requested direction passed the admission gate and, when a choice set was required, that the learner explicitly selected one field.
2. Confirm the exact output folder is known and writable.
3. Read `references/tutorial-contract.md`.
4. Research and verify the field-specific content before finalizing exact citations.
5. Create a UTF-8 `tutorial.json` that conforms to `assets/tutorial.schema.json`.
6. Run:

   ```bash
   python3 <skill-directory>/scripts/build_tutorial.py \
     --input <path-to-tutorial.json> \
     --output <user-specified-folder>
   ```

   Add `--force` only when the user authorizes overwriting existing managed tutorial files. The builder never deletes unrelated files.
7. Verify that `index.html`, `assets/styles.css`, and `data/tutorial.json` exist.
8. Inspect the HTML structure and internal navigation. When browser or rendering tools are available, open the generated site and check desktop and narrow layouts.
9. Report the exact output folder, generated files, verification performed, and any citations still awaiting verification.

The generated site must work from local files without a server or package installation. It must use semantic HTML, keyboard-accessible navigation, readable typography, and responsive layout. The complete scholarly content and navigation must work without JavaScript.

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
- Do not stop after presenting an outline when the field and output folder are known; generate the complete HTML review collection.
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

After the field is accepted as stated or explicitly chosen, ask for the output folder if it is missing. Once it is known, create and verify the complete site, then return only a concise handoff with the selected field, output path, generated files, verification performed, and how to open `index.html`.
