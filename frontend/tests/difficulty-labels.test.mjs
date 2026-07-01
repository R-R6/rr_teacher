import test from 'node:test'
import assert from 'node:assert/strict'

import { buildDifficultyLabels } from '../src/utils/difficulty.js'

const fallbackLevels = {
  1: { label: 'default-1' },
  2: { label: 'default-2' },
  3: { label: 'default-3' },
  4: { label: 'default-4' },
  5: { label: 'default-5' },
}

test('buildDifficultyLabels expands beyond the default five levels when more difficulty tags exist', () => {
  const labels = buildDifficultyLabels([
    { name: 'custom-3', tag_type: 'difficulty', sort_order: 3 },
    { name: 'custom-1', tag_type: 'difficulty', sort_order: 1 },
    { name: 'custom-2', tag_type: 'difficulty', sort_order: 2 },
    { name: 'custom-5', tag_type: 'difficulty', sort_order: 5 },
    { name: 'custom-4', tag_type: 'difficulty', sort_order: 4 },
    { name: 'custom-6', tag_type: 'difficulty', sort_order: 6 },
  ], fallbackLevels)

  assert.deepEqual(labels, ['custom-1', 'custom-2', 'custom-3', 'custom-4', 'custom-5', 'custom-6'])
})

test('buildDifficultyLabels falls back to default labels for missing difficulty slots', () => {
  const labels = buildDifficultyLabels([
    { name: 'custom-1', tag_type: 'difficulty', sort_order: 1 },
    { name: 'custom-4', tag_type: 'difficulty', sort_order: 4 },
  ], fallbackLevels)

  assert.deepEqual(labels, ['custom-1', 'custom-4', 'default-3', 'default-4', 'default-5'])
})
