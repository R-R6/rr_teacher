import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const globalCss = readFileSync(path.join(rootDir, '../src/styles/global.css'), 'utf-8')

test('drawer layout keeps detail panel scrollable to the bottom', () => {
  assert.match(
    globalCss,
    /\.drawer__panel\s*\{[\s\S]*min-height:\s*0;/
  )
  assert.match(
    globalCss,
    /\.drawer__body\s*\{[\s\S]*flex:\s*1;[\s\S]*min-height:\s*0;[\s\S]*overflow:\s*auto;/
  )
})
