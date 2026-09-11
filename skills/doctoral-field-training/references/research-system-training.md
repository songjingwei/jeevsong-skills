# Doctoral training for large technical systems

Read this reference when the selected field centers on an evolving software or hardware system, including browsers, operating systems, databases, compilers, runtimes, networks, or distributed systems.

## Required trajectory

The review collection must integrate four strands from the beginning:

1. **Problem history:** reconstruct why the system exists and why each major architectural transition became necessary.
2. **Research literature:** synthesize foundational papers, competing approaches, evaluations, critiques, and later reinterpretations.
3. **Artifact archaeology:** inspect the relevant specifications, source trees, tests, design documents, issue history, commits, benchmarks, and traces.
4. **Frontier participation:** progress from reproducing established results to instrumenting the system, testing a hypothesis, and proposing an evidence-backed contribution.

Do not present these as four disconnected courses. Every historical review must connect its period's problem and alternatives to evidence visible in the surviving artifacts.

## Source-mastery ladder

Advance through observable capabilities:

1. Build or run a researchable version of the system and locate its major subsystems.
2. Trace one behavior vertically from external contract or specification through implementation, runtime behavior, tests, and observable output.
3. Reproduce a historical behavior, failure, benchmark, or design tradeoff.
4. Read design records, issue discussions, and commits to reconstruct why an implementation changed.
5. Instrument and modify a subsystem; design tests that distinguish the intended effect from regressions and confounders.
6. Compare the implementation with competing systems or earlier versions using a defensible evaluation method.
7. Derive a research question from a historically persistent limitation, implement or conduct the investigation, and defend the result.

Codebase size is not a reason to replace source work with API tutorials. Choose vertical slices that preserve causal depth.

## Review-article chapter standard

Each chapter covers one consequential transition and must answer:

- What historical constraints and assumptions defined the problem?
- Which approaches competed, and what evidence exposed their limits?
- Which technical or conceptual decision changed the system?
- How was the decision evaluated, adopted, contested, or revised?
- Where does that decision live in present-day specifications and artifacts?
- What source-level investigation lets the learner verify the account?
- Which unresolved consequence leads toward the current frontier?

The chapter must synthesize sources into an argument. A chronology, paper-by-paper summary, documentation walkthrough, or feature list does not meet the standard.

## Field-specific application

Derive the periodization and artifact set only after the user selects a field. Research that field's actual history, communities, primary evidence, methods, and frontier; do not reuse the history or subsystem map of a prior example.

Choose evidence appropriate to the selected system. It may include standards and proposals, peer-reviewed research, contemporary technical records, architecture and security documents, source code, tests, bugs, commits, benchmarks, traces, hardware artifacts, or operational datasets. Verify historical priority and causal influence instead of inferring them from the system's current architecture.

The terminal capability must also be field-specific. It should combine historical reconstruction, explanation of consequential accepted and rejected designs, command of relevant primary artifacts, defensible evaluation, and credible participation in future research or optimization. Do not prescribe source-code mastery when source code is not a primary artifact of the chosen field; substitute the field's real research materials and practices.

## Failure patterns

Reject outputs dominated by framework APIs, ordinary application projects, build tooling, interview questions, or short weekly checklists. Those may appear only as prerequisites or incidental exercises when they directly support research capability; they cannot define the collection's spine or outcome.
