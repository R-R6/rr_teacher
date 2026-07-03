import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildEmptyState,
  buildResultMeta,
  describeActiveFilters,
} from '../src/utils/list-state.js'

test('describeActiveFilters keeps meaningful filters and formats values', () => {
  const items = describeActiveFilters(
    {
      keyword: '氧化还原',
      difficulty: 3,
      is_verified: 'false',
      tag_id: '',
      page: 1,
    },
    {
      keyword: '关键词',
      difficulty: {
        label: '难度',
        format: (value) => `难度 ${value}`,
      },
      is_verified: {
        label: '校对状态',
        format: (value) => (value === 'true' ? '已校对' : '未校对'),
      },
    }
  )

  assert.deepEqual(items, [
    { key: 'keyword', label: '关键词', value: '氧化还原' },
    { key: 'difficulty', label: '难度', value: '难度 3' },
    { key: 'is_verified', label: '校对状态', value: '未校对' },
  ])
})

test('buildResultMeta reports total, visible range and filter summary', () => {
  assert.deepEqual(
    buildResultMeta({
      total: 48,
      page: 2,
      pageSize: 20,
      noun: '道题目',
      activeFilterCount: 3,
    }),
    {
      totalLabel: '共 48 道题目',
      rangeLabel: '当前显示第 21-40 条',
      filterLabel: '已启用 3 个筛选条件',
    }
  )
})

test('buildEmptyState distinguishes filtered and initial empty cases', () => {
  assert.deepEqual(
    buildEmptyState({
      noun: 'OCR 记录',
      hasFilters: true,
      defaultHint: '尝试放宽日期范围或切换引擎后再查询。',
    }),
    {
      title: '未找到符合筛选条件的 OCR 记录',
      detail: '尝试放宽日期范围或切换引擎后再查询。',
    }
  )

  assert.deepEqual(
    buildEmptyState({
      noun: '试卷',
      hasFilters: false,
      defaultHint: '可以先在小程序完成组卷，或使用联调数据补充样本。',
    }),
    {
      title: '当前还没有试卷数据',
      detail: '可以先在小程序完成组卷，或使用联调数据补充样本。',
    }
  )
})
