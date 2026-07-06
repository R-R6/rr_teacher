import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const pageSource = readFileSync(path.join(rootDir, '../src/pages/SystemStatusPage.vue'), 'utf-8')

test('system status page uses Chinese labels for runtime switches', () => {
  assert.match(pageSource, />调试模式</)
  assert.match(pageSource, />接口文档</)
  assert.doesNotMatch(pageSource, />Debug</)
  assert.doesNotMatch(pageSource, />Swagger</)
})
