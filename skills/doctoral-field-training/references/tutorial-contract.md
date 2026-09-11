# Tutorial content and HTML contract

Read this reference whenever producing a tutorial website.

## Content model

The tutorial is a scholarly narrative, not a documentation portal assembled from independent topics. Its top-level thesis explains how the field changed as successive approaches encountered limits. Chapters are ordered by causal dependence and historical transition.

The source `tutorial.json` must conform to `assets/tutorial.schema.json`. In particular:

- `fieldQualification` records the user's original framing, the admission decision, the accepted or user-chosen research field, the selection method, and concrete evidence that the field is recognized. Do not create tutorial data for an agent-selected field.
- `abstract` states the field, scope, organizing thesis, and doctoral outcome.
- `scope` defines inclusion, exclusion, and historical boundaries.
- `reviewMethod` explains how sources were selected and verified.
- `researchQuestions` state the questions the review will answer.
- `researchPractice` defines the primary artifacts, apprenticeship sequence, and frontier contribution that make the program research training rather than coursework.
- `chapters` each represent one defensible transition in the problem genealogy.
- `crossChapterSynthesis` compares transitions and resolves the main thesis.
- `openProblems` connect unresolved tensions to researchable questions.
- `doctoralRubric` defines observable standards of judgment.

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

## HTML behavior

The generated output is a self-contained static site:

```text
<user-specified-folder>/
├── index.html
├── assets/
│   └── styles.css
└── data/
    └── tutorial.json
```

The site must:

- Open directly from `index.html` without a build step or server.
- Preserve the full tutorial in semantic HTML.
- Provide a table of contents with stable chapter anchors.
- Show citation-confidence labels.
- Require no JavaScript; the table of contents is the complete learning outline and navigation system.
- Avoid remote fonts, CDNs, analytics, and network dependencies.
- Remain readable at narrow and wide viewport sizes.

The review frame must visibly distinguish the user's original goal from the admitted research field. A reader should be able to see why the target is a research direction rather than a job-skills curriculum.

## Verification checklist

Before handoff:

1. Validate the source JSON.
2. Confirm all three managed output files exist.
3. Confirm the field-admission statement, tutorial title, every chapter, synthesis, open problems, rubric, and bibliography appear in `index.html`.
4. Confirm navigation anchors are unique and point to existing sections.
5. Confirm special characters are escaped rather than interpreted as markup.
6. Open the site in a browser when available and inspect at least one desktop and one narrow viewport.
