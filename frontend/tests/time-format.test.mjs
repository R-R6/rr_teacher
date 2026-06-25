import test from 'node:test'
import assert from 'node:assert/strict'

import { parseDateTimeString, formatRelativeTime } from '../src/utils/time.js'

// 后端 naive datetime 经 Pydantic 序列化为 T 分隔(ISO 标准),也会出现空格分隔(SQLite TEXT/str)
// 两种 naive 串都应按"本地时间"解析,不被当作 UTC 多算 8 小时。

test('naive T 分隔时间按本地时间解析', () => {
  const parsed = parseDateTimeString('2026-06-06T15:35:10.848662')
  assert.equal(parsed.getFullYear(), 2026)
  assert.equal(parsed.getMonth(), 5)
  assert.equal(parsed.getDate(), 6)
  assert.equal(parsed.getHours(), 15)
  assert.equal(parsed.getMinutes(), 35)
  assert.equal(parsed.getSeconds(), 10)
})

test('naive 空格分隔时间按本地时间解析', () => {
  const parsed = parseDateTimeString('2026-06-06 15:35:10.848662')
  assert.equal(parsed.getFullYear(), 2026)
  assert.equal(parsed.getMonth(), 5)
  assert.equal(parsed.getDate(), 6)
  assert.equal(parsed.getHours(), 15)
  assert.equal(parsed.getMinutes(), 35)
  assert.equal(parsed.getSeconds(), 10)
})

test('带 Z 的 UTC 串按 UTC 解析(本地小时 = UTC 小时 + 时区偏移)', () => {
  const parsed = parseDateTimeString('2026-06-06T15:35:10.848662Z')
  // UTC 15:35:10,本地小时应为 15 + 本地时区偏移(Asia/Shanghai = +8 → 23)
  assert.equal(parsed.getUTCHours(), 15)
  const offsetHours = -parsed.getTimezoneOffset() / 60
  const expectedLocalHour = (15 + offsetHours + 24) % 24
  assert.equal(parsed.getHours(), expectedLocalHour)
})

test('带 +08:00 时区串按该时区换算为本地时间', () => {
  // 本机若为 UTC+8:15:35+08:00 → 本地 15:35(不偏移)
  const parsed = parseDateTimeString('2026-06-06T15:35:10.848662+08:00')
  const expectedUtcMs = Date.UTC(2026, 5, 6, 15 - 8, 35, 10, 848)
  assert.equal(parsed.getTime(), expectedUtcMs)
})

test('无毫秒的 naive 串仍可解析', () => {
  const parsed = parseDateTimeString('2026-06-06T15:35:10')
  assert.equal(parsed.getHours(), 15)
  assert.equal(parsed.getMinutes(), 35)
  assert.equal(parsed.getSeconds(), 10)
  assert.equal(parsed.getMilliseconds(), 0)
})

test('毫秒不足三位时按毫秒解析', () => {
  const parsed = parseDateTimeString('2026-06-06 15:35:10.5')
  assert.equal(parsed.getMilliseconds(), 500)
})

test('formatRelativeTime 对 naive 时间不额外加 8 小时', () => {
  const result = formatRelativeTime(
    '2026-06-06T15:35:10.848662',
    new Date(2026, 5, 6, 16, 35, 10, 848)
  )
  assert.equal(result, '1小时前')
})

test('formatRelativeTime 对空格分隔 naive 时间结果一致', () => {
  const now = new Date(2026, 5, 6, 16, 35, 10, 848)
  const a = formatRelativeTime('2026-06-06T15:35:10.848662', now)
  const b = formatRelativeTime('2026-06-06 15:35:10.848662', now)
  assert.equal(a, b)
})

test('空值与非法值返回空串', () => {
  assert.equal(formatRelativeTime(null), '')
  assert.equal(formatRelativeTime(''), '')
  assert.equal(formatRelativeTime('not-a-date'), '')
})

test('Date 对象直接透传', () => {
  const d = new Date(2026, 5, 6, 15, 35, 10)
  assert.equal(parseDateTimeString(d), d)
})
