import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../src/pages/question-edit/question-edit.vue', import.meta.url), 'utf8')

test('question edit separates book and knowledge tags from type and difficulty controls', () => {
  assert.match(source, /教材版本/)
  assert.match(source, /知识点标签/)
  assert.doesNotMatch(source, /tagCategories:\s*\[\s*'教材',\s*'知识点',\s*'题型标签',\s*'难度标签'\s*\]/)
})

test('question edit does not offer type and difficulty again inside the generic tag picker', () => {
  assert.match(source, /bookTags|selectedBookTag/)
  assert.match(source, /knowledgeTags|selectedKnowledgeTags/)
  assert.doesNotMatch(source, /tagCategoryKeys:\s*\[\s*'book',\s*'knowledge',\s*'type',\s*'difficulty'\s*\]/)
})
