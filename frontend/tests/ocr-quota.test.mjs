import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'


const apiSource = readFileSync(new URL('../src/utils/api.js', import.meta.url), 'utf8')
const ocrPage = readFileSync(new URL('../src/pages/ocr/ocr.vue', import.meta.url), 'utf8')

test('upload helper surfaces backend quota detail messages', () => {
  assert.match(apiSource, /body\.detail/)
  assert.match(apiSource, /_toastShown/)
})

test('ocr page shows quota-specific recognition errors', () => {
  assert.match(ocrPage, /error\?\.message\s*\|\|\s*error\?\.detail/)
  assert.match(ocrPage, /disabled_reason/)
  assert.match(ocrPage, /额度/)
})
