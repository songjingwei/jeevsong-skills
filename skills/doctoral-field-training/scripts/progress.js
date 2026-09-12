import { readFileSync, renameSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
function utcNow() {
    return new Date().toISOString();
}
function readJson(path) {
    let value;
    try {
        value = JSON.parse(readFileSync(path, 'utf8'));
    }
    catch (error) {
        const code = error.code;
        if (code === 'ENOENT')
            throw new Error(`missing canonical file: ${path}`);
        throw new Error(`invalid JSON in ${path}: ${error.message}`);
    }
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
        throw new Error(`${path} must contain an object`);
    }
    return value;
}
export function writeJson(path, value) {
    const temporary = `${path}.tmp`;
    writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
    renameSync(temporary, path);
}
export function loadWorkspace(output) {
    const root = resolve(output);
    const tutorial = readJson(`${root}/data/tutorial.json`);
    const state = readJson(`${root}/data/learning-state.json`);
    if (state.schemaVersion !== 'doctoral-field-training/state/v1') {
        throw new Error('unsupported learning-state schemaVersion');
    }
    if (tutorial.field !== state.field) {
        throw new Error('tutorial and learning state disagree about the field');
    }
    if (!Array.isArray(tutorial.chapterPlan) || !Array.isArray(state.chapters)) {
        throw new Error('tutorial plan or learning-state chapters are invalid');
    }
    if (tutorial.chapterPlan.map((item) => item.id).join('\0') !== state.chapters.map((item) => item.id).join('\0')) {
        throw new Error('tutorial plan and learning-state chapter IDs disagree');
    }
    return { tutorial, state };
}
export function statusSummary(tutorial, state) {
    const titles = Object.fromEntries(tutorial.chapterPlan.map((item) => [item.id, item.title]));
    const read = state.chapters.filter((item) => item.status === 'read').map((item) => item.id);
    const unresolvedQuestions = [];
    const records = state.memory?.chapterRecords;
    if (records && typeof records === 'object' && !Array.isArray(records)) {
        for (const [chapterId, record] of Object.entries(records)) {
            if (record?.unresolvedQuestions?.length) {
                unresolvedQuestions.push({ chapterId, questions: record.unresolvedQuestions });
            }
        }
    }
    const currentChapterId = typeof state.currentChapterId === 'string' ? state.currentChapterId : null;
    return {
        field: state.field,
        thesis: tutorial.thesis,
        status: state.status,
        lastReadChapter: read.length ? { id: read.at(-1), title: titles[read.at(-1)] } : null,
        currentChapter: currentChapterId ? { id: currentChapterId, title: titles[currentChapterId] } : null,
        unresolvedQuestions
    };
}
function appendMemory(record, key, values) {
    const target = (record[key] ??= []);
    if (!Array.isArray(target))
        throw new Error(`memory record ${key} must be an array`);
    target.push(...values.map((text) => ({ text, source: 'learner', at: utcNow() })));
}
function eventsOf(state) {
    const events = (state.events ??= []);
    if (!Array.isArray(events))
        throw new Error('learning-state events must be an array');
    return events;
}
export function completeCurrent(state, acknowledgement, input = {}) {
    if (state.status !== 'awaiting-reading') {
        throw new Error('no available chapter is awaiting reading acknowledgement');
    }
    const currentId = state.currentChapterId;
    if (typeof currentId !== 'string')
        throw new Error('learning state has no current chapter');
    if (!Array.isArray(state.chapters))
        throw new Error('learning-state chapters must be an array');
    const currentIndex = state.chapters.findIndex((item) => item.id === currentId);
    if (currentIndex < 0 || state.chapters[currentIndex].status !== 'available') {
        throw new Error('current chapter is not available');
    }
    const record = state.memory?.chapterRecords?.[currentId];
    if (!record || typeof record !== 'object' || Array.isArray(record)) {
        throw new Error('current chapter has no memory record');
    }
    const now = utcNow();
    state.chapters[currentIndex].status = 'read';
    state.chapters[currentIndex].readAt = now;
    appendMemory(record, 'acknowledgements', [acknowledgement]);
    appendMemory(record, 'reflections', input.reflections ?? []);
    appendMemory(record, 'questions', input.questions ?? []);
    appendMemory(record, 'unresolvedQuestions', input.questions ?? []);
    appendMemory(record, 'misconceptions', input.misconceptions ?? []);
    appendMemory(record, 'masteryEvidence', input.masteryEvidence ?? []);
    eventsOf(state).push({ type: 'chapter-read', chapterId: currentId, at: now, acknowledgement });
    if (currentIndex + 1 < state.chapters.length) {
        const nextItem = state.chapters[currentIndex + 1];
        nextItem.status = 'ready';
        state.currentChapterId = nextItem.id;
        state.status = 'ready-to-generate';
    }
    else {
        state.currentChapterId = null;
        state.status = 'complete';
    }
    state.updatedAt = now;
}
export function remember(state, chapterId, input) {
    const targetId = chapterId ?? state.currentChapterId;
    if (typeof targetId !== 'string') {
        throw new Error('no chapter was supplied and the workspace has no current chapter');
    }
    const record = state.memory?.chapterRecords?.[targetId];
    if (!record || typeof record !== 'object' || Array.isArray(record)) {
        throw new Error(`unknown chapter memory record: ${targetId}`);
    }
    appendMemory(record, 'reflections', input.reflections ?? []);
    appendMemory(record, 'questions', input.questions ?? []);
    appendMemory(record, 'unresolvedQuestions', input.questions ?? []);
    appendMemory(record, 'misconceptions', input.misconceptions ?? []);
    appendMemory(record, 'masteryEvidence', input.masteryEvidence ?? []);
    const now = utcNow();
    eventsOf(state).push({
        type: 'memory-recorded',
        chapterId: targetId,
        at: now,
        counts: {
            reflections: input.reflections?.length ?? 0,
            questions: input.questions?.length ?? 0,
            misconceptions: input.misconceptions?.length ?? 0,
            masteryEvidence: input.masteryEvidence?.length ?? 0
        }
    });
    state.updatedAt = now;
}
