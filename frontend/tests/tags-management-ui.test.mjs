import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../src/pages/tags/tags.vue', import.meta.url), 'utf8')

test('tags page exposes visible edit and move actions instead of only long press delete', () => {
  assert.match(source, /edit/i)
  assert.match(source, /moveTag|shiftTag|swapTag/)
  assert.doesNotMatch(source, /itemList:\s*\['删除标签'\]/)
})

test('tags page includes an editing surface for renaming tags', () => {
  assert.match(source, /editingTag|editForm/)
  assert.match(source, /modal|dialog|popup/)
})
