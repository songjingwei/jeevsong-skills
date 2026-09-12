#!/usr/bin/env node
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

const root = resolve(import.meta.dirname, '..')
const temporary = mkdtempSync(join(tmpdir(), 'jeevsong-skills-build-'))
const executable = process.platform === 'win32' ? 'tsc.cmd' : 'tsc'
const compiler = join(root, 'node_modules', '.bin', executable)
const generatedFiles = ['build-tutorial.js', 'manage-progress.js', 'progress.js', 'tutorial.js']

try {
  const result = spawnSync(compiler, ['-p', join(root, 'tsconfig.json'), '--outDir', temporary], {
    cwd: root,
    encoding: 'utf8'
  })
  if (result.status !== 0) {
    process.stderr.write(result.stdout)
    process.stderr.write(result.stderr)
    process.exitCode = result.status ?? 1
  } else {
    const stale = generatedFiles.filter((file) => {
      const expected = readFileSync(join(temporary, file))
      const committed = readFileSync(join(root, 'skills', 'doctoral-field-training', 'scripts', file))
      return !expected.equals(committed)
    })
    if (stale.length) {
      process.stderr.write(`Generated skill scripts are stale: ${stale.join(', ')}. Run npm run build.\n`)
      process.exitCode = 1
    } else {
      process.stdout.write('Generated skill scripts match their TypeScript sources.\n')
    }
  }
} finally {
  rmSync(temporary, { recursive: true, force: true })
}
