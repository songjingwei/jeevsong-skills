#!/usr/bin/env node
import { resolve } from 'node:path';
import { buildTutorial } from './tutorial.js';
function parseArgs(argv) {
    let input;
    let output;
    let force = false;
    while (argv.length) {
        const key = argv.shift();
        if (key === '--force') {
            force = true;
            continue;
        }
        const value = argv.shift();
        if (!value)
            throw new Error(`missing value for ${key}`);
        if (key === '--input')
            input = value;
        else if (key === '--output')
            output = value;
        else
            throw new Error(`unknown option: ${key}`);
    }
    if (!input)
        throw new Error('--input is required');
    if (!output)
        throw new Error('--output is required');
    return { input: resolve(input), output: resolve(output), force };
}
export function main(argv = process.argv.slice(2)) {
    try {
        const args = parseArgs([...argv]);
        buildTutorial(args.input, args.output, args.force);
        process.stdout.write(`Built tutorial: ${args.output}/index.html\n`);
        return 0;
    }
    catch (error) {
        process.stderr.write(`error: ${error.message}\n`);
        return 1;
    }
}
process.exitCode = main();
