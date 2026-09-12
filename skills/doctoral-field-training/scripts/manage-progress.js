#!/usr/bin/env node
import { resolve } from 'node:path';
import { completeCurrent, loadWorkspace, remember, statusSummary, writeJson } from './progress.js';
function usage() {
    throw new Error('usage: manage-progress.js <status|remember|complete> --output <folder> [options]');
}
function parseArgs(argv) {
    const command = argv.shift();
    if (!command || !['status', 'remember', 'complete'].includes(command))
        usage();
    const memoryOptions = ['--reflection', '--question', '--misconception', '--mastery-evidence'];
    const allowedOptions = {
        status: new Set(['--output']),
        remember: new Set(['--output', '--chapter', ...memoryOptions]),
        complete: new Set(['--output', '--acknowledgement', ...memoryOptions])
    };
    const values = new Map();
    while (argv.length) {
        const key = argv.shift();
        if (!key.startsWith('--') || !argv.length)
            usage();
        if (!allowedOptions[command].has(key))
            throw new Error(`${key} is not valid for ${command}`);
        const value = argv.shift();
        const list = values.get(key) ?? [];
        list.push(value);
        values.set(key, list);
    }
    return { command, values };
}
function required(values, key) {
    const value = values.get(key)?.at(-1);
    if (!value)
        throw new Error(`${key} is required`);
    return value;
}
function memoryInput(values) {
    return {
        reflections: values.get('--reflection') ?? [],
        questions: values.get('--question') ?? [],
        misconceptions: values.get('--misconception') ?? [],
        masteryEvidence: values.get('--mastery-evidence') ?? []
    };
}
export function main(argv = process.argv.slice(2)) {
    try {
        const { command, values } = parseArgs([...argv]);
        const output = resolve(required(values, '--output'));
        const { tutorial, state } = loadWorkspace(output);
        if (command === 'complete') {
            completeCurrent(state, required(values, '--acknowledgement'), memoryInput(values));
            writeJson(`${output}/data/learning-state.json`, state);
        }
        else if (command === 'remember') {
            const input = memoryInput(values);
            if (!Object.values(input).some((items) => items?.length)) {
                throw new Error('remember requires at least one memory value');
            }
            remember(state, values.get('--chapter')?.at(-1), input);
            writeJson(`${output}/data/learning-state.json`, state);
        }
        process.stdout.write(`${JSON.stringify(statusSummary(tutorial, state), null, 2)}\n`);
        return 0;
    }
    catch (error) {
        process.stderr.write(`error: ${error.message}\n`);
        return 1;
    }
}
process.exitCode = main();
