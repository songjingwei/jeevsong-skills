#!/usr/bin/env python3
"""Build a self-contained doctoral tutorial site from structured JSON."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


MANAGED_FILES = (
    Path("index.html"),
    Path("assets/styles.css"),
    Path("data/tutorial.json"),
    Path("data/learning-state.json"),
)
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_STATUSES = {
    "verified",
    "canonical-but-unverified-in-this-session",
    "candidate",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def render_html(data: dict[str, object], state: dict[str, object]) -> str:
    chapters = data["chapters"]
    chapter_plan = data["chapterPlan"]
    rubric = data["doctoralRubric"]
    qualification = data["fieldQualification"]
    research_practice = data["researchPractice"]
    assert isinstance(chapters, list)
    assert isinstance(chapter_plan, list)
    assert isinstance(rubric, list)
    assert isinstance(qualification, dict)
    assert isinstance(research_practice, dict)
    generated_ids = {chapter["id"] for chapter in chapters}
    state_items = state["chapters"]
    assert isinstance(state_items, list)
    statuses = {item["id"]: item["status"] for item in state_items}
    nav = "".join(
        (
            f'<li><a href="#{escaped(item["id"])}">'
            f'{index}. {escaped(item["title"])} '
            f'<small>{escaped(statuses[item["id"]])}</small></a></li>'
            if item["id"] in generated_ids
            else f'<li class="planned-chapter"><span>{index}. '
            f'{escaped(item["title"])}</span><small>{escaped(statuses[item["id"]])}</small></li>'
        )
        for index, item in enumerate(chapter_plan, 1)
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
    current_id = state.get("currentChapterId")
    current_title = next(
        (item["title"] for item in chapter_plan if item["id"] == current_id),
        "Textbook complete",
    )
    completed_count = sum(1 for status in statuses.values() if status == "read")
    progression = (
        '<p class="progress-instruction">Read the available chapter, then return '
        'to the agent and say <strong>“读完了”</strong> or '
        '<strong>“I finished this chapter.”</strong> The next chapter will be generated then.</p>'
        if state["status"] == "awaiting-reading"
        else '<p class="progress-instruction">Return to the agent to generate the next planned chapter.</p>'
        if state["status"] == "ready-to-generate"
        else '<p class="progress-instruction">All planned chapters have been read.</p>'
    )
    final_sections = ""
    if state["status"] == "complete":
        final_sections = f"""
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
        """
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
        <div class="reading-progress">
          <strong>{completed_count} of {len(chapter_plan)} chapters read</strong>
          <span>Current: {escaped(current_title)}</span>
          {progression}
        </div>
        <ol class="lineage-list">
          {''.join((f'<li><a href="#{escaped(item["id"])}"><span>{index}</span><strong>{escaped(item["title"])}</strong><small>{escaped(item["period"])} · {escaped(statuses[item["id"]])}</small></a></li>' if item["id"] in generated_ids else f'<li class="planned-chapter"><span>{index}</span><strong>{escaped(item["title"])}</strong><small>{escaped(item["period"])} · {escaped(statuses[item["id"]])}</small></li>') for index, item in enumerate(chapter_plan, 1))}
        </ol>
      </section>
      {chapter_html}
      {final_sections}
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
        "chapterPlan",
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

    chapter_plan = data.get("chapterPlan")
    plan_ids: list[str] = []
    if not isinstance(chapter_plan, list) or not chapter_plan:
        errors.append("chapterPlan must contain at least one item")
    else:
        for index, item in enumerate(chapter_plan, 1):
            context = f"chapterPlan item {index}"
            if not isinstance(item, dict):
                errors.append(f"{context} must be an object")
                continue
            for key in ("id", "title", "period", "transitionSummary"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"{context}.{key} must be a non-empty string")
            item_id = item.get("id")
            if isinstance(item_id, str):
                if not ID_PATTERN.fullmatch(item_id):
                    errors.append(f"{context}.id must use lowercase kebab-case")
                elif item_id in plan_ids:
                    errors.append(f"duplicate chapterPlan id: {item_id}")
                else:
                    plan_ids.append(item_id)
            dependencies = item.get("dependsOn")
            if not isinstance(dependencies, list) or not all(
                isinstance(dependency, str) and dependency.strip()
                for dependency in dependencies
            ):
                errors.append(f"{context}.dependsOn must be an array of IDs")
            sources = item.get("sourceRequirements")
            if not isinstance(sources, list) or not sources or not all(
                isinstance(source, str) and source.strip() for source in sources
            ):
                errors.append(
                    f"{context}.sourceRequirements must be a non-empty array"
                )
        known_ids: set[str] = set()
        for index, item in enumerate(chapter_plan, 1):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            for dependency in item.get("dependsOn", []):
                if dependency not in known_ids:
                    errors.append(
                        f"chapterPlan item {index}.dependsOn must reference an earlier chapter"
                    )
            known_ids.add(item["id"])

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

    if plan_ids and isinstance(chapters, list):
        generated_ids = [
            chapter.get("id") for chapter in chapters if isinstance(chapter, dict)
        ]
        if generated_ids != plan_ids[: len(generated_ids)]:
            errors.append("chapters must be a contiguous prefix of chapterPlan")

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
:root { color-scheme:light; --ink:#171717; --muted:#65615b; --paper:#f3f0e9; --card:#fffefa; --line:#cfc9bd; --accent:#7a2f24; --green:#31483c; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; color:var(--ink); background:var(--paper); font-family:Georgia,"Times New Roman",serif; line-height:1.7; }
a { color:var(--green); text-underline-offset:.2em; }
.skip-link { position:absolute; left:-999px; top:1rem; background:#fff; padding:.75rem 1rem; z-index:10; }
.skip-link:focus { left:1rem; }
.hero { background:var(--card); color:var(--ink); padding:clamp(3rem,7vw,6rem) 1.5rem; border-bottom:1px solid var(--line); }
.hero-inner { max-width:1100px; margin:auto; }
.hero h1 { max-width:900px; margin:.35rem 0 1rem; font-size:clamp(2.45rem,6vw,5rem); line-height:1.02; letter-spacing:-.035em; }
.hero-summary { max-width:760px; color:var(--muted); font-size:1.15rem; }
.eyebrow,.nav-title { font-family:ui-sans-serif,system-ui,sans-serif; font-size:.74rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
.outcome-card { max-width:760px; margin-top:2rem; padding:1rem 1.2rem; border-left:3px solid var(--accent); background:var(--paper); display:grid; gap:.3rem; }
.outcome-card span { color:var(--muted); font:700 .72rem ui-sans-serif,system-ui,sans-serif; text-transform:uppercase; letter-spacing:.1em; }
.layout { max-width:1280px; margin:auto; display:grid; grid-template-columns:270px minmax(0,820px); gap:clamp(2rem,5vw,5rem); padding:3rem 1.5rem 7rem; }
.sidebar { position:sticky; top:1rem; align-self:start; max-height:calc(100vh - 2rem); overflow:auto; font-family:ui-sans-serif,system-ui,sans-serif; font-size:.88rem; }
.sidebar ol { list-style:none; padding:0; margin:0; }
.sidebar a { display:block; padding:.38rem 0; color:var(--muted); text-decoration:none; }
.sidebar a:hover,.sidebar a:focus { color:var(--accent); }
.sidebar small { margin-left:.35rem; color:var(--muted); }
.sidebar .planned-chapter { display:grid; gap:.1rem; padding:.38rem 0; color:var(--muted); }
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
.lineage-list .planned-chapter { display:grid; grid-template-columns:2.3rem 1fr auto; gap:1rem; align-items:center; padding:1rem; color:var(--muted); border:1px dashed var(--line); background:transparent; }
.reading-progress { margin:1.25rem 0 1.75rem; padding:1.2rem 1.35rem; border:1px solid var(--line); background:var(--card); display:grid; gap:.35rem; }
.progress-instruction { margin:.35rem 0 0; color:var(--muted); }
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


def initialize_state(data: dict[str, object]) -> dict[str, object]:
    chapters = data["chapters"]
    plan = data["chapterPlan"]
    qualification = data["fieldQualification"]
    assert isinstance(chapters, list)
    assert isinstance(plan, list)
    assert isinstance(qualification, dict)
    if len(chapters) != 1 or chapters[0]["id"] != plan[0]["id"]:
        raise ValueError(
            "a new workspace must contain the complete chapterPlan and Chapter 1 only"
        )
    now = utc_now()
    first_id = plan[0]["id"]
    return {
        "schemaVersion": "doctoral-field-training/state/v1",
        "field": data["field"],
        "status": "awaiting-reading",
        "currentChapterId": first_id,
        "chapters": [
            {
                "id": item["id"],
                "status": "available" if index == 0 else "planned",
                **({"generatedAt": now} if index == 0 else {}),
            }
            for index, item in enumerate(plan)
        ],
        "memory": {
            "learner": {
                "requestedDirection": qualification["requestedDirection"],
                "admittedResearchField": qualification["admittedResearchField"],
                "doctoralOutcome": data["doctoralOutcome"],
                "preferences": [],
            },
            "chapterRecords": {
                item["id"]: {
                    "acknowledgements": [],
                    "reflections": [],
                    "questions": [],
                    "masteryEvidence": [],
                    "misconceptions": [],
                    "unresolvedQuestions": [],
                    "memoryUsed": [],
                }
                for item in plan
            },
        },
        "events": [
            {
                "type": "chapter-generated",
                "chapterId": first_id,
                "at": now,
            }
        ],
        "updatedAt": now,
    }


def load_and_sync_state(
    data: dict[str, object], output_path: Path
) -> dict[str, object]:
    state_path = output_path / "data/learning-state.json"
    if not state_path.exists():
        return initialize_state(data)
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid learning state: {error}") from error
    if not isinstance(state, dict):
        raise ValueError("learning state root must be an object")
    if state.get("schemaVersion") != "doctoral-field-training/state/v1":
        raise ValueError("unsupported learning-state schemaVersion")
    if state.get("field") != data["field"]:
        raise ValueError("tutorial field conflicts with saved learning state")

    plan = data["chapterPlan"]
    chapters = data["chapters"]
    state_chapters = state.get("chapters")
    if not isinstance(plan, list) or not isinstance(chapters, list):
        raise ValueError("invalid tutorial plan")
    if not isinstance(state_chapters, list):
        raise ValueError("learning state chapters must be an array")
    plan_ids = [item["id"] for item in plan]
    if [item.get("id") for item in state_chapters] != plan_ids:
        raise ValueError("chapterPlan conflicts with saved learning state")

    generated_ids = {chapter["id"] for chapter in chapters}
    newly_generated = [
        item
        for item in state_chapters
        if item["id"] in generated_ids and "generatedAt" not in item
    ]
    if len(newly_generated) > 1 or any(
        item.get("status") != "ready" for item in newly_generated
    ):
        raise ValueError("generate exactly the one chapter marked ready")
    if newly_generated:
        now = utc_now()
        item = newly_generated[0]
        item["status"] = "available"
        item["generatedAt"] = now
        state["status"] = "awaiting-reading"
        state["currentChapterId"] = item["id"]
        events = state.setdefault("events", [])
        events.append(
            {"type": "chapter-generated", "chapterId": item["id"], "at": now}
        )
        state["updatedAt"] = now
    return state


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

    state = load_and_sync_state(data, output_path)
    write_text(output_path / "index.html", render_html(data, state))
    write_text(output_path / "assets/styles.css", STYLES)
    write_text(
        output_path / "data/tutorial.json",
        json.dumps(data, ensure_ascii=False, indent=2),
    )
    write_text(
        output_path / "data/learning-state.json",
        json.dumps(state, ensure_ascii=False, indent=2),
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
