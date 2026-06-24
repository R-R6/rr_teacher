import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'


const source = readFileSync(new URL('../src/pages/ocr/ocr.vue', import.meta.url), 'utf8')

test('ocr page has a camera fallback path', () => {
  assert.match(source, /cameraFailed/)
  assert.match(source, /captureWithSystemCamera/)
  assert.match(source, /setCameraInitTimeout/)
  assert.match(source, /sourceType:\s*\['camera'\]/)
})

test('ocr page skips live camera in WeChat DevTools', () => {
  assert.match(source, /cameraFailed:\s*true/)
  assert.match(source, /wx\.getSystemInfoSync/)
  assert.match(source, /platform\s*===\s*['"]devtools['"]/)
  assert.match(source, /brand\s*===\s*['"]devtools['"]/)
  assert.match(source, /cameraErrorText\s*=\s*['"]开发者工具未检测到摄像头['"]/)
})
