#!/usr/bin/env python3
"""Build a self-contained doctoral tutorial site from structured JSON."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


MANAGED_FILES = (
    Path("index.html"),
    Path("assets/styles.css"),
    Path("data/tutorial.json"),
)
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_STATUSES = {
    "verified",
    "canonical-but-unverified-in-this-session",
    "candidate",
}


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_list(items: list[str], css_class: str = "") -> str:
    class_attr = f' class="{escaped(css_class)}"' if css_class else ""
    body = "".join(f"<li>{escaped(item)}</li>" for item in items)
    return f"<ul{class_attr}>{body}</ul>"


def render_works(works: list[dict[str, str]]) -> str:
    if not works:
        return '<p class="muted">No works assigned to this section.</p>'
    rows = []
    for work in works:
        citation = escaped(work["citation"])
        url = work.get("url")
        if url:
            citation = (
                f'<a href="{escaped(url)}" target="_blank" '
                f'rel="noreferrer">{citation}</a>'
            )
        rows.append(
            "<li>"
            f'<span class="source-status status-{escaped(work["status"])}">'
            f'{escaped(work["status"])}</span>'
            f"<strong>{citation}</strong>"
            f"<p>{escaped(work['role'])}</p>"
            "</li>"
        )
    return f'<ol class="works">{"".join(rows)}</ol>'


def render_prior_approaches(approaches: list[dict[str, str]]) -> str:
    cards = []
    for approach in approaches:
        cards.append(
            '<article class="approach-card">'
            f"<h4>{escaped(approach['name'])}</h4>"
            f"<p><strong>Contribution.</strong> {escaped(approach['contribution'])}</p>"
            f"<p><strong>Binding limitation.</strong> {escaped(approach['limitation'])}</p>"
            "</article>"
        )
    return f'<div class="approach-grid">{"".join(cards)}</div>'


def render_chapter(chapter: dict[str, object], number: int) -> str:
    turning_point = chapter["turningPoint"]
    assert isinstance(turning_point, dict)
    return f"""
    <section class="chapter" id="{escaped(chapter['id'])}">
      <header class="chapter-header">
        <div>
          <p class="eyebrow">Chapter {number} · {escaped(chapter['period'])}</p>
          <h2>{escaped(chapter['title'])}</h2>
        </div>
      </header>
      <div class="section-block">
        <h3>1. Historical situation</h3>
        <p>{escaped(chapter['historicalSituation'])}</p>
      </div>
      <div class="section-block problem-block">
        <h3>2. Central problem</h3>
        <p>{escaped(chapter['centralProblem'])}</p>
      </div>
      <div class="section-block">
        <h3>3. Prior approaches and binding limitations</h3>
        {render_prior_approaches(chapter['priorApproaches'])}
      </div>
      <div class="section-block turning-point">
        <p class="eyebrow">The turning point</p>
        <h3>4. {escaped(turning_point['name'])}</h3>
        <p><strong>Core idea.</strong> {escaped(turning_point['idea'])}</p>
        <p><strong>Why it worked.</strong> {escaped(turning_point['whyItWorked'])}</p>
      </div>
      <div class="section-block">
        <h3>5. Method, mechanism, or argument</h3>
        <p>{escaped(chapter['methodAndMechanism'])}</p>
      </div>
      <div class="section-block">
        <h3>6. Evidence and evaluation</h3>
        <p>{escaped(chapter['evidenceAndEvaluation'])}</p>
      </div>
      <div class="section-block">
        <h3>7. Limitations and debates</h3>
        {render_list(chapter['limitationsAndDebates'])}
      </div>
      <div class="section-block">
        <h3>8. Downstream influence and newly visible problems</h3>
        {render_list(chapter['downstreamInfluence'])}
      </div>
      <div class="section-block synthesis-block">
        <h3>9. Doctoral synthesis</h3>
        <p>{escaped(chapter['doctoralSynthesis'])}</p>
      </div>
      <div class="section-block">
        <h3>10. Primary-artifact investigation</h3>
        <p>{escaped(chapter['primaryArtifactInvestigation'])}</p>
      </div>
      <div class="section-block">
        <h3>11. Learning tasks</h3>
        {render_list(chapter['learningTasks'], "task-list")}
      </div>
      <div class="mastery-gate">
        <p class="eyebrow">Mastery gate</p>
        <h3>12. Required performance</h3>
        <p>{escaped(chapter['masteryGate'])}</p>
      </div>
      <div class="section-block">
        <h3>13. Works for this transition</h3>
        {render_works(chapter['works'])}
      </div>
    </section>
    """


def render_html(data: dict[str, object]) -> str:
    chapters = data["chapters"]
    rubric = data["doctoralRubric"]
    qualification = data["fieldQualification"]
    research_practice = data["researchPractice"]
    assert isinstance(chapters, list)
    assert isinstance(rubric, list)
    assert isinstance(qualification, dict)
    assert isinstance(research_practice, dict)
    nav = "".join(
        f'<li><a href="#{escaped(chapter["id"])}">'
        f'{index}. {escaped(chapter["title"])}</a></li>'
        for index, chapter in enumerate(chapters, 1)
    )
    chapter_html = "".join(
        render_chapter(chapter, index)
        for index, chapter in enumerate(chapters, 1)
    )
    rubric_rows = "".join(
        f"<tr><th scope=\"row\">{escaped(item['capability'])}</th>"
        f"<td>{escaped(item['standard'])}</td></tr>"
        for item in rubric
    )
    return f"""<!doctype html>
<html lang="{escaped(data['language'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escaped(data['abstract'])}">
  <title>{escaped(data['title'])}</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to tutorial</a>
  <header class="hero">
    <div class="hero-inner">
      <p class="eyebrow">Doctoral Field Training · {escaped(data['field'])}</p>
      <h1>{escaped(data['title'])}</h1>
      <p class="hero-summary">{escaped(data['abstract'])}</p>
      <div class="outcome-card">
        <span>Doctoral outcome</span>
        <strong>{escaped(data['doctoralOutcome'])}</strong>
      </div>
    </div>
  </header>
  <div class="layout">
    <aside class="sidebar" aria-label="Tutorial navigation">
      <nav>
        <p class="nav-title">Review architecture</p>
        <ol>
          <li><a href="#review-frame">Scope and method</a></li>
          <li><a href="#research-practice">Research practice</a></li>
          <li><a href="#problem-lineage">Problem lineage</a></li>
          {nav}
          <li><a href="#cross-synthesis">Cross-period synthesis</a></li>
          <li><a href="#research-frontier">Research frontier</a></li>
          <li><a href="#doctoral-rubric">Doctoral rubric</a></li>
          <li><a href="#bibliography">Bibliography</a></li>
        </ol>
      </nav>
    </aside>
    <main id="main-content">
      <section class="front-matter" id="review-frame">
        <p class="eyebrow">Review frame</p>
        <h2>Scope, thesis, and method</h2>
        <div class="field-admission">
          <p class="eyebrow">Field admission</p>
          <h3>{escaped(qualification['admittedResearchField'])}</h3>
          <dl>
            <dt>Original direction</dt>
            <dd>{escaped(qualification['requestedDirection'])}</dd>
            <dt>Decision</dt>
            <dd>{escaped(str(qualification['decision']).replace('-', ' ').title())}</dd>
            <dt>Selection</dt>
            <dd>{escaped(str(qualification['selectionMethod']).replace('-', ' ').title())}</dd>
            <dt>Rationale</dt>
            <dd>{escaped(qualification['rationale'])}</dd>
          </dl>
          <h4>Recognition evidence</h4>
          {render_list(qualification['recognitionEvidence'])}
          <h4>Adjacent research fields</h4>
          {render_list(qualification['adjacentFields'])}
        </div>
        <h3>Scope</h3>
        <p>{escaped(data['scope'])}</p>
        <h3>Organizing thesis</h3>
        <p>{escaped(data['thesis'])}</p>
        <h3>Review method</h3>
        <p>{escaped(data['reviewMethod'])}</p>
        <h3>Research questions</h3>
        {render_list(data['researchQuestions'])}
        <h3>Prerequisites</h3>
        {render_list(data['prerequisites'])}
      </section>
      <section class="closing-section" id="research-practice">
        <p class="eyebrow">Research apprenticeship</p>
        <h2>From primary artifacts to the frontier</h2>
        <h3>Primary artifacts</h3>
        {render_list(research_practice['primaryArtifacts'])}
        <h3>Apprenticeship sequence</h3>
        {render_list(research_practice['apprenticeshipSequence'])}
        <h3>Frontier contribution</h3>
        <p>{escaped(research_practice['frontierContribution'])}</p>
      </section>
      <section class="lineage" id="problem-lineage">
        <p class="eyebrow">Problem genealogy</p>
        <h2>How the field changes</h2>
        <ol class="lineage-list">
          {''.join(f'<li><a href="#{escaped(chapter["id"])}"><span>{index}</span><strong>{escaped(chapter["title"])}</strong><small>{escaped(chapter["period"])}</small></a></li>' for index, chapter in enumerate(chapters, 1))}
        </ol>
      </section>
      {chapter_html}
      <section class="closing-section" id="cross-synthesis">
        <p class="eyebrow">Across the literature</p>
        <h2>Cross-period synthesis</h2>
        <p>{escaped(data['crossChapterSynthesis'])}</p>
      </section>
      <section class="closing-section" id="research-frontier">
        <p class="eyebrow">Research agenda</p>
        <h2>Open problems</h2>
        {render_list(data['openProblems'], "open-problems")}
      </section>
      <section class="closing-section" id="doctoral-rubric">
        <p class="eyebrow">Assessment</p>
        <h2>Doctoral capability rubric</h2>
        <div class="table-wrap"><table><thead><tr><th>Capability</th><th>Doctoral standard</th></tr></thead><tbody>{rubric_rows}</tbody></table></div>
      </section>
      <section class="closing-section" id="bibliography">
        <p class="eyebrow">Source trail</p>
        <h2>Bibliography</h2>
        {render_works(data['bibliography'])}
      </section>
    </main>
  </div>
</body>
</html>
"""


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["tutorial root must be an object"]

    string_fields = (
        "title",
        "field",
        "language",
        "doctoralOutcome",
        "abstract",
        "scope",
        "thesis",
        "reviewMethod",
        "crossChapterSynthesis",
    )
    list_fields = (
        "researchQuestions",
        "prerequisites",
        "chapters",
        "openProblems",
        "doctoralRubric",
        "bibliography",
    )
    for key in string_fields:
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be a non-empty string")
    for key in list_fields:
        if not isinstance(data.get(key), list):
            errors.append(f"{key} must be an array")

    qualification = data.get("fieldQualification")
    if not isinstance(qualification, dict):
        errors.append("fieldQualification must be an object")
    else:
        for key in (
            "requestedDirection",
            "decision",
            "admittedResearchField",
            "selectionMethod",
            "rationale",
        ):
            if not isinstance(qualification.get(key), str) or not qualification[key].strip():
                errors.append(f"fieldQualification.{key} must be a non-empty string")
        decision = qualification.get("decision")
        if isinstance(decision, str) and decision not in {"accepted", "reframed", "narrowed"}:
            errors.append("fieldQualification.decision is invalid")
        selection_method = qualification.get("selectionMethod")
        if isinstance(selection_method, str) and selection_method not in {
            "accepted-as-stated",
            "chosen-by-user",
        }:
            errors.append("fieldQualification.selectionMethod is invalid")
        if decision in {"reframed", "narrowed"} and selection_method != "chosen-by-user":
            errors.append(
                "reframed or narrowed fields require selectionMethod chosen-by-user"
            )
        for key in ("recognitionEvidence", "adjacentFields"):
            values = qualification.get(key)
            if not isinstance(values, list):
                errors.append(f"fieldQualification.{key} must be an array")
            elif not all(isinstance(item, str) and item.strip() for item in values):
                errors.append(
                    f"fieldQualification.{key} must contain only non-empty strings"
                )
        evidence = qualification.get("recognitionEvidence")
        if isinstance(evidence, list) and not evidence:
            errors.append("fieldQualification.recognitionEvidence must not be empty")
        admitted_field = qualification.get("admittedResearchField")
        if isinstance(admitted_field, str) and admitted_field != data.get("field"):
            errors.append("field must equal fieldQualification.admittedResearchField")

    for key in ("researchQuestions", "openProblems"):
        values = data.get(key)
        if isinstance(values, list):
            if not values:
                errors.append(f"{key} must contain at least one item")
            elif not all(isinstance(item, str) and item.strip() for item in values):
                errors.append(f"{key} must contain only non-empty strings")

    research_practice = data.get("researchPractice")
    if not isinstance(research_practice, dict):
        errors.append("researchPractice must be an object")
    else:
        for key in ("primaryArtifacts", "apprenticeshipSequence"):
            values = research_practice.get(key)
            if not isinstance(values, list) or not values:
                errors.append(f"researchPractice.{key} must be a non-empty array")
            elif not all(isinstance(item, str) and item.strip() for item in values):
                errors.append(
                    f"researchPractice.{key} must contain only non-empty strings"
                )
        frontier = research_practice.get("frontierContribution")
        if not isinstance(frontier, str) or not frontier.strip():
            errors.append(
                "researchPractice.frontierContribution must be a non-empty string"
            )

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        errors.append("chapters must contain at least one chapter")
        return errors

    chapter_string_fields = (
        "id",
        "title",
        "period",
        "historicalSituation",
        "centralProblem",
        "methodAndMechanism",
        "evidenceAndEvaluation",
        "doctoralSynthesis",
        "primaryArtifactInvestigation",
        "masteryGate",
    )
    chapter_list_fields = (
        "priorApproaches",
        "limitationsAndDebates",
        "downstreamInfluence",
        "learningTasks",
        "works",
    )
    chapter_ids: set[str] = set()
    for index, chapter in enumerate(chapters, 1):
        context = f"chapter {index}"
        if not isinstance(chapter, dict):
            errors.append(f"{context} must be an object")
            continue
        for key in chapter_string_fields:
            if not isinstance(chapter.get(key), str) or not chapter[key].strip():
                errors.append(f"{context}.{key} must be a non-empty string")
        for key in chapter_list_fields:
            if not isinstance(chapter.get(key), list) or not chapter[key]:
                errors.append(f"{context}.{key} must be a non-empty array")
        chapter_id = chapter.get("id")
        if isinstance(chapter_id, str) and chapter_id and not ID_PATTERN.fullmatch(chapter_id):
            errors.append(f"{context}.id must use lowercase kebab-case")
        elif isinstance(chapter_id, str) and chapter_id in chapter_ids:
            errors.append(f"duplicate chapter id: {chapter_id}")
        elif isinstance(chapter_id, str) and chapter_id:
            chapter_ids.add(chapter_id)

        prior_approaches = chapter.get("priorApproaches", [])
        if isinstance(prior_approaches, list):
            for approach_index, approach in enumerate(prior_approaches, 1):
                approach_context = f"{context}.priorApproaches item {approach_index}"
                if not isinstance(approach, dict):
                    errors.append(f"{approach_context} must be an object")
                    continue
                for key in ("name", "contribution", "limitation"):
                    if not isinstance(approach.get(key), str) or not approach[key].strip():
                        errors.append(f"{approach_context} requires {key}")

        turning_point = chapter.get("turningPoint")
        if not isinstance(turning_point, dict):
            errors.append(f"{context}.turningPoint must be an object")
        else:
            for key in ("name", "idea", "whyItWorked"):
                if not isinstance(turning_point.get(key), str) or not turning_point[key].strip():
                    errors.append(f"{context}.turningPoint requires {key}")

        for key in ("limitationsAndDebates", "downstreamInfluence", "learningTasks"):
            values = chapter.get(key, [])
            if isinstance(values, list) and not all(
                isinstance(item, str) and item.strip() for item in values
            ):
                errors.append(f"{context}.{key} must contain only non-empty strings")

    collections: list[tuple[str, object]] = [("bibliography", data.get("bibliography"))]
    if isinstance(chapters, list):
        collections.extend(
            (f"chapter {index}.works", chapter.get("works"))
            for index, chapter in enumerate(chapters, 1)
            if isinstance(chapter, dict)
        )
    for collection_name, works in collections:
        if isinstance(works, list):
            if not works:
                errors.append(f"{collection_name} must contain at least one work")
            for index, work in enumerate(works, 1):
                if not isinstance(work, dict):
                    errors.append(f"{collection_name} item {index} must be an object")
                    continue
                for key in ("citation", "role", "status"):
                    if not isinstance(work.get(key), str) or not work[key].strip():
                        errors.append(f"{collection_name} item {index} requires {key}")
                status = work.get("status")
                if isinstance(status, str) and status not in SOURCE_STATUSES:
                    errors.append(f"{collection_name} item {index} has an invalid status")
                url = work.get("url")
                if url and urlparse(str(url)).scheme not in {"http", "https"}:
                    errors.append(f"{collection_name} item {index} has an unsafe URL")

    rubric = data.get("doctoralRubric")
    if isinstance(rubric, list):
        if not rubric:
            errors.append("doctoralRubric must contain at least one item")
        for index, item in enumerate(rubric, 1):
            if not isinstance(item, dict):
                errors.append(f"doctoralRubric item {index} must be an object")
                continue
            for key in ("capability", "standard"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"doctoralRubric item {index} requires {key}")
    return errors


STYLES = """
:root { color-scheme: light; --ink:#17211b; --muted:#5f6d64; --paper:#f6f3ea; --card:#fffdf7; --line:#d8d2c3; --accent:#9b3d20; --green:#254f3c; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; color:var(--ink); background:var(--paper); font-family:Georgia,"Times New Roman",serif; line-height:1.7; }
a { color:var(--green); text-underline-offset:.2em; }
.skip-link { position:absolute; left:-999px; top:1rem; background:#fff; padding:.75rem 1rem; z-index:10; }
.skip-link:focus { left:1rem; }
.hero { background:var(--ink); color:#fff; padding:clamp(3rem,8vw,7rem) 1.5rem; }
.hero-inner { max-width:1100px; margin:auto; }
.hero h1 { max-width:900px; margin:.35rem 0 1rem; font-size:clamp(2.6rem,7vw,6rem); line-height:.98; letter-spacing:-.045em; }
.hero-summary { max-width:760px; color:#dce3dd; font-size:1.15rem; }
.eyebrow,.nav-title { font-family:ui-sans-serif,system-ui,sans-serif; font-size:.74rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
.outcome-card { max-width:760px; margin-top:2rem; padding:1rem 1.2rem; border-left:4px solid #e79365; background:#ffffff10; display:grid; gap:.3rem; }
.outcome-card span { color:#bdc9c0; font:700 .72rem ui-sans-serif,system-ui,sans-serif; text-transform:uppercase; letter-spacing:.1em; }
.layout { max-width:1280px; margin:auto; display:grid; grid-template-columns:270px minmax(0,820px); gap:clamp(2rem,5vw,5rem); padding:3rem 1.5rem 7rem; }
.sidebar { position:sticky; top:1rem; align-self:start; max-height:calc(100vh - 2rem); overflow:auto; font-family:ui-sans-serif,system-ui,sans-serif; font-size:.88rem; }
.sidebar ol { list-style:none; padding:0; margin:0; }
.sidebar a { display:block; padding:.38rem 0; color:var(--muted); text-decoration:none; }
.sidebar a:hover,.sidebar a:focus { color:var(--accent); }
main { min-width:0; }
h2 { margin:.2rem 0 1.5rem; font-size:clamp(2rem,4vw,3.2rem); line-height:1.08; letter-spacing:-.03em; }
h3 { margin:0 0 .65rem; line-height:1.25; }
.front-matter,.lineage,.chapter,.closing-section { margin-bottom:5rem; }
.front-matter,.closing-section { padding:clamp(1.5rem,4vw,3rem); background:var(--card); border:1px solid var(--line); }
.field-admission { margin:0 0 2rem; padding:1.5rem; background:#e9efe9; border-left:4px solid var(--green); }
.field-admission h3 { font-size:1.55rem; }
.field-admission dl { display:grid; grid-template-columns:minmax(8rem,auto) 1fr; gap:.35rem 1rem; }
.field-admission dt { font-weight:700; }
.field-admission dd { margin:0; }
.lineage-list { padding:0; list-style:none; display:grid; gap:.75rem; }
.lineage-list a { display:grid; grid-template-columns:2.3rem 1fr auto; gap:1rem; align-items:center; padding:1rem; background:var(--card); border:1px solid var(--line); text-decoration:none; }
.lineage-list span { display:grid; place-items:center; width:2.2rem; height:2.2rem; border-radius:50%; color:#fff; background:var(--accent); }
.lineage-list small { color:var(--muted); }
.chapter { border-top:5px solid var(--ink); padding-top:2rem; }
.chapter-header { margin-bottom:2rem; }
.chapter-header h2 { margin-bottom:0; }
.section-block { padding:1.4rem 0; border-top:1px solid var(--line); }
.problem-block { font-size:1.16rem; }
.turning-point,.synthesis-block,.mastery-gate { margin:1.5rem 0; padding:1.5rem; background:#e9efe9; border-left:4px solid var(--green); }
.mastery-gate { background:#f6e5d9; border-color:var(--accent); }
.approach-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }
.approach-card { padding:1rem; background:var(--card); border:1px solid var(--line); }
.approach-card h4 { margin-top:0; }
.task-list li,.open-problems li { margin-bottom:.6rem; }
.works { padding:0; list-style:none; display:grid; gap:1rem; }
.works li { padding:1rem; border:1px solid var(--line); background:var(--card); }
.works p { margin:.35rem 0 0; color:var(--muted); }
.source-status { display:inline-block; margin:0 .6rem .4rem 0; padding:.15rem .45rem; border-radius:999px; background:#e4e4df; font:700 .66rem ui-sans-serif,system-ui,sans-serif; }
.status-verified { color:#fff; background:var(--green); }
.status-candidate { color:#fff; background:var(--accent); }
.table-wrap { overflow-x:auto; }
table { width:100%; border-collapse:collapse; }
th,td { padding:.8rem; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
.muted { color:var(--muted); }
@media (max-width:800px) { .layout { grid-template-columns:1fr; } .sidebar { position:static; max-height:none; } .lineage-list a { grid-template-columns:2.3rem 1fr; } .lineage-list small { grid-column:2; } .field-admission dl { grid-template-columns:1fr; } }
""".strip()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content + "\n", encoding="utf-8")
    temporary.replace(path)


def build(input_path: Path, output_path: Path, force: bool) -> None:
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"input file does not exist: {input_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {error}") from error

    errors = validate(data)
    if errors:
        raise ValueError("invalid tutorial data:\n- " + "\n- ".join(errors))

    existing = [path for path in MANAGED_FILES if (output_path / path).exists()]
    if existing and not force:
        joined = ", ".join(str(path) for path in existing)
        raise ValueError(f"managed output already exists ({joined}); pass --force to overwrite")

    write_text(output_path / "index.html", render_html(data))
    write_text(output_path / "assets/styles.css", STYLES)
    write_text(
        output_path / "data/tutorial.json",
        json.dumps(data, ensure_ascii=False, indent=2),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        build(args.input.resolve(), args.output.resolve(), args.force)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Built tutorial: {args.output.resolve() / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
