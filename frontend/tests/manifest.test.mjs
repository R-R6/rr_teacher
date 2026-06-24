import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'


const manifest = JSON.parse(readFileSync(new URL('../src/manifest.json', import.meta.url), 'utf8'))

test('mp-weixin manifest does not declare invalid camera permission', () => {
  const permission = manifest['mp-weixin']?.permission || {}
  assert.equal(Object.hasOwn(permission, 'scope.camera'), false)
})
