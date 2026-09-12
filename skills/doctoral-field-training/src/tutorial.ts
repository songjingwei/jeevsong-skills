import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import type { JsonObject } from './progress.js'

const MANAGED_FILES = ['index.html', 'assets/styles.css', 'data/tutorial.json', 'data/learning-state.json']
const ID_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/
const SOURCE_STATUSES = new Set(['verified', 'canonical-but-unverified-in-this-session', 'candidate'])

function utcNow(): string {
  return new Date().toISOString()
}

function escaped(value: unknown): string {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#x27;')
}

function titleCase(value: unknown): string {
  return String(value).replaceAll('-', ' ').replace(/\b\w/g, (character) => character.toUpperCase())
}

function renderList(items: string[], cssClass = ''): string {
  const classAttribute = cssClass ? ` class="${escaped(cssClass)}"` : ''
  return `<ul${classAttribute}>${items.map((item) => `<li>${escaped(item)}</li>`).join('')}</ul>`
}

function renderWorks(works: JsonObject[]): string {
  if (!works.length) return '<p class="muted">No works assigned to this section.</p>'
  const rows = works.map((work) => {
    const citation = work.url
      ? `<a href="${escaped(work.url)}" target="_blank" rel="noreferrer">${escaped(work.citation)}</a>`
      : escaped(work.citation)
    return `<li><span class="source-status status-${escaped(work.status)}">${escaped(work.status)}</span><strong>${citation}</strong><p>${escaped(work.role)}</p></li>`
  })
  return `<ol class="works">${rows.join('')}</ol>`
}

function renderPriorApproaches(approaches: JsonObject[]): string {
  return `<div class="approach-grid">${approaches.map((approach) =>
    `<article class="approach-card"><h4>${escaped(approach.name)}</h4><p><strong>Contribution.</strong> ${escaped(approach.contribution)}</p><p><strong>Binding limitation.</strong> ${escaped(approach.limitation)}</p></article>`
  ).join('')}</div>`
}

function renderChapter(chapter: JsonObject, number: number): string {
  const turningPoint = chapter.turningPoint
  return `
    <section class="chapter" id="${escaped(chapter.id)}">
      <header class="chapter-header"><div><p class="eyebrow">Chapter ${number} · ${escaped(chapter.period)}</p><h2>${escaped(chapter.title)}</h2></div></header>
      <div class="section-block"><h3>1. Historical situation</h3><p>${escaped(chapter.historicalSituation)}</p></div>
      <div class="section-block problem-block"><h3>2. Central problem</h3><p>${escaped(chapter.centralProblem)}</p></div>
      <div class="section-block"><h3>3. Prior approaches and binding limitations</h3>${renderPriorApproaches(chapter.priorApproaches)}</div>
      <div class="section-block turning-point"><p class="eyebrow">The turning point</p><h3>4. ${escaped(turningPoint.name)}</h3><p><strong>Core idea.</strong> ${escaped(turningPoint.idea)}</p><p><strong>Why it worked.</strong> ${escaped(turningPoint.whyItWorked)}</p></div>
      <div class="section-block"><h3>5. Method, mechanism, or argument</h3><p>${escaped(chapter.methodAndMechanism)}</p></div>
      <div class="section-block"><h3>6. Evidence and evaluation</h3><p>${escaped(chapter.evidenceAndEvaluation)}</p></div>
      <div class="section-block"><h3>7. Limitations and debates</h3>${renderList(chapter.limitationsAndDebates)}</div>
      <div class="section-block"><h3>8. Downstream influence and newly visible problems</h3>${renderList(chapter.downstreamInfluence)}</div>
      <div class="section-block synthesis-block"><h3>9. Doctoral synthesis</h3><p>${escaped(chapter.doctoralSynthesis)}</p></div>
      <div class="section-block"><h3>10. Primary-artifact investigation</h3><p>${escaped(chapter.primaryArtifactInvestigation)}</p></div>
      <div class="section-block"><h3>11. Learning tasks</h3>${renderList(chapter.learningTasks, 'task-list')}</div>
      <div class="mastery-gate"><p class="eyebrow">Mastery gate</p><h3>12. Required performance</h3><p>${escaped(chapter.masteryGate)}</p></div>
      <div class="section-block"><h3>13. Works for this transition</h3>${renderWorks(chapter.works)}</div>
    </section>`
}

export function renderHtml(data: JsonObject, state: JsonObject): string {
  const generatedIds = new Set(data.chapters.map((chapter: JsonObject) => chapter.id))
  const statuses = Object.fromEntries(state.chapters.map((item: JsonObject) => [item.id, item.status]))
  const navigation = data.chapterPlan.map((item: JsonObject, index: number) => generatedIds.has(item.id)
    ? `<li><a href="#${escaped(item.id)}">${index + 1}. ${escaped(item.title)} <small>${escaped(statuses[item.id])}</small></a></li>`
    : `<li class="planned-chapter"><span>${index + 1}. ${escaped(item.title)}</span><small>${escaped(statuses[item.id])}</small></li>`
  ).join('')
  const current = data.chapterPlan.find((item: JsonObject) => item.id === state.currentChapterId)
  const currentTitle = current?.title ?? 'Textbook complete'
  const completedCount = state.chapters.filter((item: JsonObject) => item.status === 'read').length
  const progression = state.status === 'awaiting-reading'
    ? '<p class="progress-instruction">Read the available chapter, then return to the agent and say <strong>“读完了”</strong> or <strong>“I finished this chapter.”</strong> The next chapter will be generated then.</p>'
    : state.status === 'ready-to-generate'
      ? '<p class="progress-instruction">Return to the agent to generate the next planned chapter.</p>'
      : '<p class="progress-instruction">All planned chapters have been read.</p>'
  const lineage = data.chapterPlan.map((item: JsonObject, index: number) => generatedIds.has(item.id)
    ? `<li><a href="#${escaped(item.id)}"><span>${index + 1}</span><strong>${escaped(item.title)}</strong><small>${escaped(item.period)} · ${escaped(statuses[item.id])}</small></a></li>`
    : `<li class="planned-chapter"><span>${index + 1}</span><strong>${escaped(item.title)}</strong><small>${escaped(item.period)} · ${escaped(statuses[item.id])}</small></li>`
  ).join('')
  const rubricRows = data.doctoralRubric.map((item: JsonObject) => `<tr><th scope="row">${escaped(item.capability)}</th><td>${escaped(item.standard)}</td></tr>`).join('')
  const finalSections = state.status === 'complete' ? `
      <section class="closing-section" id="cross-synthesis"><p class="eyebrow">Across the literature</p><h2>Cross-period synthesis</h2><p>${escaped(data.crossChapterSynthesis)}</p></section>
      <section class="closing-section" id="research-frontier"><p class="eyebrow">Research agenda</p><h2>Open problems</h2>${renderList(data.openProblems, 'open-problems')}</section>
      <section class="closing-section" id="doctoral-rubric"><p class="eyebrow">Assessment</p><h2>Doctoral capability rubric</h2><div class="table-wrap"><table><thead><tr><th>Capability</th><th>Doctoral standard</th></tr></thead><tbody>${rubricRows}</tbody></table></div></section>
      <section class="closing-section" id="bibliography"><p class="eyebrow">Source trail</p><h2>Bibliography</h2>${renderWorks(data.bibliography)}</section>` : ''
  const qualification = data.fieldQualification
  const researchPractice = data.researchPractice
  return `<!doctype html>
<html lang="${escaped(data.language)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="${escaped(data.abstract)}"><title>${escaped(data.title)}</title><link rel="stylesheet" href="assets/styles.css"></head>
<body>
  <a class="skip-link" href="#main-content">Skip to tutorial</a>
  <header class="hero"><div class="hero-inner"><p class="eyebrow">Doctoral Field Training · ${escaped(data.field)}</p><h1>${escaped(data.title)}</h1><p class="hero-summary">${escaped(data.abstract)}</p><div class="outcome-card"><span>Doctoral outcome</span><strong>${escaped(data.doctoralOutcome)}</strong></div></div></header>
  <div class="layout">
    <aside class="sidebar" aria-label="Tutorial navigation"><nav><p class="nav-title">Review architecture</p><ol><li><a href="#review-frame">Scope and method</a></li><li><a href="#research-practice">Research practice</a></li><li><a href="#problem-lineage">Problem lineage</a></li>${navigation}</ol></nav></aside>
    <main id="main-content">
      <section class="front-matter" id="review-frame"><p class="eyebrow">Review frame</p><h2>Scope, thesis, and method</h2>
        <div class="field-admission"><p class="eyebrow">Field admission</p><h3>${escaped(qualification.admittedResearchField)}</h3><dl><dt>Original direction</dt><dd>${escaped(qualification.requestedDirection)}</dd><dt>Decision</dt><dd>${escaped(titleCase(qualification.decision))}</dd><dt>Selection</dt><dd>${escaped(titleCase(qualification.selectionMethod))}</dd><dt>Rationale</dt><dd>${escaped(qualification.rationale)}</dd></dl><h4>Recognition evidence</h4>${renderList(qualification.recognitionEvidence)}<h4>Adjacent research fields</h4>${renderList(qualification.adjacentFields)}</div>
        <h3>Scope</h3><p>${escaped(data.scope)}</p><h3>Organizing thesis</h3><p>${escaped(data.thesis)}</p><h3>Review method</h3><p>${escaped(data.reviewMethod)}</p><h3>Research questions</h3>${renderList(data.researchQuestions)}<h3>Prerequisites</h3>${renderList(data.prerequisites)}</section>
      <section class="closing-section" id="research-practice"><p class="eyebrow">Research apprenticeship</p><h2>From primary artifacts to the frontier</h2><h3>Primary artifacts</h3>${renderList(researchPractice.primaryArtifacts)}<h3>Apprenticeship sequence</h3>${renderList(researchPractice.apprenticeshipSequence)}<h3>Frontier contribution</h3><p>${escaped(researchPractice.frontierContribution)}</p></section>
      <section class="lineage" id="problem-lineage"><p class="eyebrow">Problem genealogy</p><h2>How the field changes</h2><div class="reading-progress"><strong>${completedCount} of ${data.chapterPlan.length} chapters read</strong><span>Current: ${escaped(currentTitle)}</span>${progression}</div><ol class="lineage-list">${lineage}</ol></section>
      ${data.chapters.map((chapter: JsonObject, index: number) => renderChapter(chapter, index + 1)).join('')}
      ${finalSections}
    </main>
  </div>
</body>
</html>`
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

function validateStringArray(value: unknown, path: string, errors: string[], allowEmpty = false): void {
  if (!Array.isArray(value) || (!allowEmpty && !value.length)) {
    errors.push(`${path} must be ${allowEmpty ? 'an' : 'a non-empty'} array`)
  } else if (!value.every(isNonEmptyString)) {
    errors.push(`${path} must contain only non-empty strings`)
  }
}

export function validate(data: unknown): string[] {
  if (!data || typeof data !== 'object' || Array.isArray(data)) return ['tutorial root must be an object']
  const value = data as JsonObject
  const errors: string[] = []
  for (const key of ['title', 'field', 'language', 'doctoralOutcome', 'abstract', 'scope', 'thesis', 'reviewMethod', 'crossChapterSynthesis']) {
    if (!isNonEmptyString(value[key])) errors.push(`${key} must be a non-empty string`)
  }
  for (const key of ['researchQuestions', 'chapterPlan', 'chapters', 'openProblems', 'doctoralRubric', 'bibliography']) {
    if (!Array.isArray(value[key]) || !value[key].length) errors.push(`${key} must contain at least one item`)
  }
  validateStringArray(value.prerequisites, 'prerequisites', errors, true)
  validateStringArray(value.researchQuestions, 'researchQuestions', errors)
  validateStringArray(value.openProblems, 'openProblems', errors)

  const qualification = value.fieldQualification
  if (!qualification || typeof qualification !== 'object' || Array.isArray(qualification)) {
    errors.push('fieldQualification must be an object')
  } else {
    for (const key of ['requestedDirection', 'decision', 'admittedResearchField', 'selectionMethod', 'rationale']) {
      if (!isNonEmptyString(qualification[key])) errors.push(`fieldQualification.${key} must be a non-empty string`)
    }
    if (!['accepted', 'reframed', 'narrowed'].includes(qualification.decision)) errors.push('fieldQualification.decision is invalid')
    if (!['accepted-as-stated', 'chosen-by-user'].includes(qualification.selectionMethod)) errors.push('fieldQualification.selectionMethod is invalid')
    if (['reframed', 'narrowed'].includes(qualification.decision) && qualification.selectionMethod !== 'chosen-by-user') {
      errors.push('reframed or narrowed fields require selectionMethod chosen-by-user')
    }
    validateStringArray(qualification.recognitionEvidence, 'fieldQualification.recognitionEvidence', errors)
    validateStringArray(qualification.adjacentFields, 'fieldQualification.adjacentFields', errors, true)
    if (qualification.admittedResearchField !== value.field) errors.push('field must equal fieldQualification.admittedResearchField')
  }

  const practice = value.researchPractice
  if (!practice || typeof practice !== 'object' || Array.isArray(practice)) {
    errors.push('researchPractice must be an object')
  } else {
    validateStringArray(practice.primaryArtifacts, 'researchPractice.primaryArtifacts', errors)
    validateStringArray(practice.apprenticeshipSequence, 'researchPractice.apprenticeshipSequence', errors)
    if (!isNonEmptyString(practice.frontierContribution)) errors.push('researchPractice.frontierContribution must be a non-empty string')
  }

  const planIds: string[] = []
  if (Array.isArray(value.chapterPlan)) value.chapterPlan.forEach((item: unknown, index: number) => {
    const path = `chapterPlan item ${index + 1}`
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      errors.push(`${path} must be an object`)
      return
    }
    const plan = item as JsonObject
    for (const key of ['id', 'title', 'period', 'transitionSummary']) if (!isNonEmptyString(plan[key])) errors.push(`${path}.${key} must be a non-empty string`)
    if (typeof plan.id === 'string' && !ID_PATTERN.test(plan.id)) errors.push(`${path}.id must use lowercase kebab-case`)
    if (planIds.includes(plan.id)) errors.push(`duplicate chapterPlan id: ${plan.id}`)
    validateStringArray(plan.dependsOn, `${path}.dependsOn`, errors, true)
    validateStringArray(plan.sourceRequirements, `${path}.sourceRequirements`, errors)
    for (const dependency of Array.isArray(plan.dependsOn) ? plan.dependsOn : []) {
      if (!planIds.includes(dependency)) errors.push(`${path}.dependsOn must reference an earlier chapter`)
    }
    if (typeof plan.id === 'string') planIds.push(plan.id)
  })

  const chapterIds: string[] = []
  if (Array.isArray(value.chapters)) value.chapters.forEach((item: unknown, index: number) => {
    const path = `chapter ${index + 1}`
    if (!item || typeof item !== 'object' || Array.isArray(item)) return errors.push(`${path} must be an object`)
    const chapter = item as JsonObject
    for (const key of ['id', 'title', 'period', 'historicalSituation', 'centralProblem', 'methodAndMechanism', 'evidenceAndEvaluation', 'doctoralSynthesis', 'primaryArtifactInvestigation', 'masteryGate']) {
      if (!isNonEmptyString(chapter[key])) errors.push(`${path}.${key} must be a non-empty string`)
    }
    if (typeof chapter.id === 'string' && !ID_PATTERN.test(chapter.id)) errors.push(`${path}.id must use lowercase kebab-case`)
    if (chapterIds.includes(chapter.id)) errors.push(`duplicate chapter id: ${chapter.id}`)
    if (typeof chapter.id === 'string') chapterIds.push(chapter.id)
    for (const key of ['limitationsAndDebates', 'downstreamInfluence', 'learningTasks']) validateStringArray(chapter[key], `${path}.${key}`, errors)
    if (!Array.isArray(chapter.priorApproaches) || !chapter.priorApproaches.length) errors.push(`${path}.priorApproaches must be a non-empty array`)
    else chapter.priorApproaches.forEach((approach: JsonObject, approachIndex: number) => {
      for (const key of ['name', 'contribution', 'limitation']) if (!isNonEmptyString(approach?.[key])) errors.push(`${path}.priorApproaches item ${approachIndex + 1} requires ${key}`)
    })
    for (const key of ['name', 'idea', 'whyItWorked']) if (!isNonEmptyString(chapter.turningPoint?.[key])) errors.push(`${path}.turningPoint requires ${key}`)
    validateWorks(chapter.works, `${path}.works`, errors)
  })
  if (chapterIds.join('\0') !== planIds.slice(0, chapterIds.length).join('\0')) errors.push('chapters must be a contiguous prefix of chapterPlan')
  validateWorks(value.bibliography, 'bibliography', errors)
  if (Array.isArray(value.doctoralRubric)) value.doctoralRubric.forEach((item: JsonObject, index: number) => {
    for (const key of ['capability', 'standard']) if (!isNonEmptyString(item?.[key])) errors.push(`doctoralRubric item ${index + 1} requires ${key}`)
  })
  return errors
}

function validateWorks(value: unknown, path: string, errors: string[]): void {
  if (!Array.isArray(value) || !value.length) {
    errors.push(`${path} must contain at least one work`)
    return
  }
  value.forEach((item: unknown, index: number) => {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      errors.push(`${path} item ${index + 1} must be an object`)
      return
    }
    const work = item as JsonObject
    for (const key of ['citation', 'role', 'status']) if (!isNonEmptyString(work[key])) errors.push(`${path} item ${index + 1} requires ${key}`)
    if (typeof work.status === 'string' && !SOURCE_STATUSES.has(work.status)) errors.push(`${path} item ${index + 1} has an invalid status`)
    if (work.url) {
      try {
        if (!['http:', 'https:'].includes(new URL(String(work.url)).protocol)) throw new Error()
      } catch {
        errors.push(`${path} item ${index + 1} has an unsafe URL`)
      }
    }
  })
}

export const STYLES = `
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
.lineage-list a,.lineage-list .planned-chapter { display:grid; grid-template-columns:2.3rem 1fr auto; gap:1rem; align-items:center; padding:1rem; border:1px solid var(--line); }
.lineage-list a { background:var(--card); text-decoration:none; }
.lineage-list span { display:grid; place-items:center; width:2.2rem; height:2.2rem; border-radius:50%; color:#fff; background:var(--accent); }
.lineage-list small,.lineage-list .planned-chapter { color:var(--muted); }
.lineage-list .planned-chapter { border-style:dashed; background:transparent; }
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
`.trim()

function writeText(path: string, content: string): void {
  mkdirSync(dirname(path), { recursive: true })
  const temporary = `${path}.tmp`
  writeFileSync(temporary, `${content}\n`, 'utf8')
  renameSync(temporary, path)
}

function initializeState(data: JsonObject): JsonObject {
  if (data.chapters.length !== 1 || data.chapters[0].id !== data.chapterPlan[0].id) {
    throw new Error('a new workspace must contain the complete chapterPlan and Chapter 1 only')
  }
  const now = utcNow()
  const firstId = data.chapterPlan[0].id
  return {
    schemaVersion: 'doctoral-field-training/state/v1', field: data.field, status: 'awaiting-reading', currentChapterId: firstId,
    chapters: data.chapterPlan.map((item: JsonObject, index: number) => ({ id: item.id, status: index === 0 ? 'available' : 'planned', ...(index === 0 ? { generatedAt: now } : {}) })),
    memory: {
      learner: { requestedDirection: data.fieldQualification.requestedDirection, admittedResearchField: data.fieldQualification.admittedResearchField, doctoralOutcome: data.doctoralOutcome, preferences: [] },
      chapterRecords: Object.fromEntries(data.chapterPlan.map((item: JsonObject) => [item.id, { acknowledgements: [], reflections: [], questions: [], masteryEvidence: [], misconceptions: [], unresolvedQuestions: [], memoryUsed: [] }]))
    },
    events: [{ type: 'chapter-generated', chapterId: firstId, at: now }], updatedAt: now
  }
}

function loadAndSyncState(data: JsonObject, outputPath: string): JsonObject {
  const statePath = join(outputPath, 'data/learning-state.json')
  if (!existsSync(statePath)) return initializeState(data)
  let state: JsonObject
  try { state = JSON.parse(readFileSync(statePath, 'utf8')) } catch (error) { throw new Error(`invalid learning state: ${(error as Error).message}`) }
  if (!state || typeof state !== 'object' || Array.isArray(state)) throw new Error('learning state root must be an object')
  if (state.schemaVersion !== 'doctoral-field-training/state/v1') throw new Error('unsupported learning-state schemaVersion')
  if (state.field !== data.field) throw new Error('tutorial field conflicts with saved learning state')
  if (!Array.isArray(state.chapters)) throw new Error('learning state chapters must be an array')
  if (state.chapters.map((item: JsonObject) => item.id).join('\0') !== data.chapterPlan.map((item: JsonObject) => item.id).join('\0')) throw new Error('chapterPlan conflicts with saved learning state')
  const generatedIds = new Set(data.chapters.map((chapter: JsonObject) => chapter.id))
  const newlyGenerated = state.chapters.filter((item: JsonObject) => generatedIds.has(item.id) && !item.generatedAt)
  if (newlyGenerated.length > 1 || newlyGenerated.some((item: JsonObject) => item.status !== 'ready')) throw new Error('generate exactly the one chapter marked ready')
  if (newlyGenerated.length) {
    const now = utcNow()
    const item = newlyGenerated[0]
    item.status = 'available'; item.generatedAt = now
    state.status = 'awaiting-reading'; state.currentChapterId = item.id
    const events = (state.events ??= [])
    if (!Array.isArray(events)) throw new Error('learning-state events must be an array')
    events.push({ type: 'chapter-generated', chapterId: item.id, at: now }); state.updatedAt = now
  }
  return state
}

export function buildTutorial(inputPath: string, outputPath: string, force = false): void {
  let data: unknown
  try { data = JSON.parse(readFileSync(inputPath, 'utf8')) } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') throw new Error(`input file does not exist: ${inputPath}`)
    throw new Error(`invalid JSON: ${(error as Error).message}`)
  }
  const errors = validate(data)
  if (errors.length) throw new Error(`invalid tutorial data:\n- ${errors.join('\n- ')}`)
  const tutorial = data as JsonObject
  const existing = MANAGED_FILES.filter((path) => existsSync(join(outputPath, path)))
  if (existing.length && !force) throw new Error(`managed output already exists (${existing.join(', ')}); pass --force to overwrite`)
  const state = loadAndSyncState(tutorial, outputPath)
  writeText(join(outputPath, 'index.html'), renderHtml(tutorial, state))
  writeText(join(outputPath, 'assets/styles.css'), STYLES)
  writeText(join(outputPath, 'data/tutorial.json'), JSON.stringify(tutorial, null, 2))
  writeText(join(outputPath, 'data/learning-state.json'), JSON.stringify(state, null, 2))
}
