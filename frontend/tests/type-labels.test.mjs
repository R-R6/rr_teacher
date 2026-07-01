import test from 'node:test'
import assert from 'node:assert/strict'

import { buildTypeConfigs } from '../src/utils/type-config.js'

const fallbackTypes = {
  choice: { label: 'choice-default', color: '#1', icon: 'A' },
  fill: { label: 'fill-default', color: '#2', icon: 'B' },
  experiment: { label: 'experiment-default', color: '#3', icon: 'C' },
  calculation: { label: 'calculation-default', color: '#4', icon: 'D' },
  short_answer: { label: 'short-default', color: '#5', icon: 'E' },
}

test('buildTypeConfigs maps sorted type tags onto the five core question types', () => {
  const configs = buildTypeConfigs([
    { name: '简答提升', tag_type: 'type', sort_order: 5 },
    { name: '计算训练', tag_type: 'type', sort_order: 4 },
    { name: '单项选择', tag_type: 'type', sort_order: 1 },
    { name: '实验探究', tag_type: 'type', sort_order: 3 },
    { name: '基础填空', tag_type: 'type', sort_order: 2 },
  ], fallbackTypes)

  assert.equal(configs.choice.label, '单项选择')
  assert.equal(configs.fill.label, '基础填空')
  assert.equal(configs.experiment.label, '实验探究')
  assert.equal(configs.calculation.label, '计算训练')
  assert.equal(configs.short_answer.label, '简答提升')
  assert.equal(configs.choice.color, '#1')
})

test('buildTypeConfigs falls back when some type tags are missing', () => {
  const configs = buildTypeConfigs([
    { name: '单项选择', tag_type: 'type', sort_order: 1 },
    { name: '实验探究', tag_type: 'type', sort_order: 3 },
  ], fallbackTypes)

  assert.equal(configs.choice.label, '单项选择')
  assert.equal(configs.fill.label, '实验探究')
  assert.equal(configs.experiment.label, 'experiment-default')
  assert.equal(configs.short_answer.label, 'short-default')
})
