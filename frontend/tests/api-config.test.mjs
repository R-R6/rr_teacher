import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import {
  DEFAULT_API_BASE,
  normalizeApiBase,
  resolveApiBase,
} from '../src/utils/config.js'

const currentCloudRunBase = 'https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com'
const apiSource = readFileSync(new URL('../src/utils/api.js', import.meta.url), 'utf8')

test('api base defaults to the current CloudRun backend', () => {
  assert.equal(DEFAULT_API_BASE, currentCloudRunBase)
  assert.equal(resolveApiBase({}), currentCloudRunBase)
})

test('api base can be injected at build time and normalized', () => {
  assert.equal(
    resolveApiBase({ VITE_API_BASE: 'https://staging.example.com/' }),
    'https://staging.example.com',
  )
  assert.equal(normalizeApiBase(' https://api.example.com// '), 'https://api.example.com')
})

test('api helpers import the configured API base instead of hardcoding it', () => {
  assert.match(apiSource, /from ['"]\.\/config\.js['"]/)
  assert.doesNotMatch(apiSource, /chem-backend-268016-4-1440725000\.sh\.run\.tcloudbase\.com/)
})
