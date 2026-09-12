# Tutorial content and delivery contract

Read this reference whenever producing or revising a tutorial workspace.

## Canonical source and rendering seam

`data/tutorial.json` and `data/learning-state.json` are the canonical, inspectable sources. They describe tutorial semantics and learning state, not a particular UI tree.

Two rendering Adapters consume the same contract:

- Canon / 学脉 renders the structured JSON as its interactive React Reader.
- The static exporter renders a self-contained `index.html` for standalone reading, archiving, or sharing.

Static HTML is a reproducible projection. It never overrides canonical JSON and its absence does not make a Canon workspace invalid.

## Delivery modes

| Mode | Canonical JSON | Static HTML | Intended use |
|---|---:|---:|---|
| `canon` | Required | No | Canon-managed reading and revision |
| `standalone` | Required | Required | Use without Canon |
| `both` | Required | Required after acceptance | Canon plus portable export |

Outside Canon, default to `standalone`. A Canon candidate run always generates candidate JSON only, even if the Workspace normally uses `both`; rebuild the export after acceptance.

## Content model

The tutorial is a progressively revealed scholarly narrative, not a documentation portal assembled from independent topics. Its top-level thesis explains how the field changed as successive approaches encountered limits. The complete chapter plan is ordered by causal dependence and historical transition, while chapter bodies are generated one at a time.

The canonical `data/tutorial.json` must conform to `assets/tutorial.schema.json`. In particular:

- `fieldQualification` records the user's original framing, the admission decision, the accepted or user-chosen research field, the selection method, and concrete evidence that the field is recognized. Do not create tutorial data for an agent-selected field.
- `abstract` states the field, scope, organizing thesis, and doctoral outcome.
- `scope` defines inclusion, exclusion, and historical boundaries.
- `reviewMethod` explains how sources were selected and verified.
- `researchQuestions` state the questions the review will answer.
- `researchPractice` defines the primary artifacts, apprenticeship sequence, and frontier contribution that make the program research training rather than coursework.
- `chapterPlan` declares the complete trajectory with stable IDs, periods, transition summaries, dependencies, and source requirements.
- `chapters` contains only generated review articles. At initialization it contains exactly Chapter 1; each acknowledgement appends exactly one next planned chapter.
- `crossChapterSynthesis` compares transitions and resolves the main thesis.
- `openProblems` connect unresolved tensions to researchable questions.
- `doctoralRubric` defines observable standards of judgment.

The current v1 schema remains readable during migration. Its next version must add stable semantic content-block IDs so renderers and revision tools can address content without depending on HTML structure.

Target selection identity:

```ts
interface ContentSelection {
  chapterId: string
  blockId: string
  startOffset: number
  endOffset: number
  baseRevisionId: string
}
```

A block ID must remain stable when its text is revised. JSON must not contain Canon-specific DOM selectors, CSS class names, pixel positions, or layout instructions.

## Chapter contract

Every chapter requires:

| Field | Purpose |
|---|---|
| `historicalSituation` | What actors knew, valued, and could build at the time |
| `centralProblem` | The problem that constrained progress |
| `priorApproaches` | What existed, what it contributed, and why it was insufficient |
| `turningPoint` | The smallest idea or work that changed the field |
| `methodAndMechanism` | How the new approach works or argues |
| `evidenceAndEvaluation` | Evidence used and standards by which it should be judged |
| `limitationsAndDebates` | Scope limits, critiques, failures, and competing interpretations |
| `downstreamInfluence` | What later work inherited, corrected, or rejected |
| `doctoralSynthesis` | The judgment the learner should now be able to defend |
| `primaryArtifactInvestigation` | Direct work with source, specifications, data, proofs, experiments, archives, or other primary evidence |
| `learningTasks` | Retrieval, comparison, critique, reproduction, and synthesis |
| `masteryGate` | Observable performance required before advancing |
| `works` | Traceable sources and their role in the transition |

## Source integrity

Use `verified` only when the citation was checked against a reliable source in the current run. Use `canonical-but-unverified-in-this-session` for well-established references not checked in the current run. Use `candidate` for provisional reading leads.

Bibliographic entries should contain enough information to locate the work. Prefer DOI or stable publisher/repository URLs when verified. Do not use citation count as a substitute for explaining a work's role.

## Static HTML export behavior

For `standalone` and `both`, the generated export is a self-contained static site:

```text
<user-specified-folder>/
├── index.html
├── assets/
│   └── styles.css
└── data/
    ├── tutorial.json
    └── learning-state.json
```

The static export must:

- Open directly from `index.html` without a build step or server.
- Preserve all generated tutorial content in semantic HTML.
- Show the complete table of contents with stable chapter anchors and visibly distinguish available, read, and planned chapters.
- Show the current reading state and tell the learner to return to the agent after finishing the available chapter.
- Show citation-confidence labels.
- Require no JavaScript; the table of contents is the complete learning outline and navigation system.
- Avoid remote fonts, CDNs, analytics, and network dependencies.
- Remain readable at narrow and wide viewport sizes.

Canon mode does not require these presentation files. Canon applies its own visual system, interaction design, selection controls, and version-review UI while preserving the tutorial's semantic order and source integrity.

The review frame must visibly distinguish the user's original goal from the admitted research field. A reader should be able to see why the target is a research direction rather than a job-skills curriculum.

## Verification checklist

Before handoff in every delivery mode:

1. Validate the source JSON.
2. Confirm `data/tutorial.json` and `data/learning-state.json` exist and agree on the plan, generated chapters, statuses, and current chapter.
3. Confirm stable semantic IDs are unique for the active schema version.
4. Confirm field admission, title, complete plan, generated chapters, sources, and learning gates are present in canonical data.

For `standalone` and `both`, additionally:

5. Confirm `index.html` and required local assets exist.
6. Confirm every generated chapter appears in `index.html`.
7. Confirm navigation anchors are unique and point to existing sections.
8. Confirm special characters are escaped rather than interpreted as markup.
9. Open the export in a browser when available and inspect at least one desktop and one narrow viewport.

For a Canon candidate, additionally verify the candidate target, base revision, schema validity, diff, and impact summary. Do not rebuild static HTML before acceptance.
