import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const adminApiSource = readFileSync(path.join(rootDir, '../src/api/admin.js'), 'utf-8')
const usersPageSource = readFileSync(path.join(rootDir, '../src/pages/UsersPage.vue'), 'utf-8')

test('adminApi exposes user OCR usage and quota profile endpoints', () => {
  assert.match(adminApiSource, /getUserOcrUsage\(id/)
  assert.match(adminApiSource, /updateUserQuotaProfile\(id, payload\)/)
})

test('UsersPage shows quota profile controls and OCR usage details', () => {
  assert.match(usersPageSource, /套餐与 OCR 用量/)
  assert.match(usersPageSource, /saveQuotaProfile/)
  assert.match(usersPageSource, /userUsage\.usage_logs/)
  assert.match(usersPageSource, /userUsage\.paid_engine_status/)
  assert.match(usersPageSource, /daily_ocr_limit/)
})
