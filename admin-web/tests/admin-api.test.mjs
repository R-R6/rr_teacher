import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const adminApiSource = readFileSync(path.join(rootDir, '../src/api/admin.js'), 'utf-8')

test('adminApi exposes getAdminMe for login handoff', () => {
  assert.match(adminApiSource, /export const authApi = \{[\s\S]*getAdminMe\(\)/)
  assert.match(adminApiSource, /export const adminApi = \{[\s\S]*getAdminMe\(\)/)
})
