import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { buildDownloadUrl } from '../src/utils/api.js'
import { buildWordFileName } from '../src/utils/export-word.js'

const paperDetail = readFileSync(new URL('../src/pages/paper-detail/paper-detail.vue', import.meta.url), 'utf8')
const papers = readFileSync(new URL('../src/pages/papers/papers.vue', import.meta.url), 'utf8')
const exportWord = readFileSync(new URL('../src/utils/export-word.js', import.meta.url), 'utf8')

test('paper detail export delegates URL normalization to buildDownloadUrl', () => {
  assert.doesNotMatch(paperDetail, /API_BASE/)
  assert.match(paperDetail, /const url = buildDownloadUrl\(rawUrl\)/)
})

test('paper detail export shares Word through WeChat file message', () => {
  assert.match(paperDetail, /exportWordToWechat/)
  assert.doesNotMatch(paperDetail, /openDocument\(/)
})

test('paper list export shares Word through WeChat file message', () => {
  assert.match(papers, /exportWordToWechat/)
  assert.doesNotMatch(papers, /openDocument\(/)
})

test('word export helper checks failed download status', () => {
  assert.match(exportWord, /statusCode\s*!==\s*200/)
  assert.match(exportWord, /Word download failed with status/)
})

test('word export helper uses WeChat file sharing with document fallback', () => {
  assert.match(exportWord, /shareFileMessage/)
  assert.match(exportWord, /openDocument/)
})

test('word export helper prepares a docx path before sharing on mobile', () => {
  assert.match(exportWord, /USER_DATA_PATH/)
  assert.match(exportWord, /copyFile/)
})

test('download url builder preserves signed COS query strings', () => {
  const signedUrl = 'https://bucket.cos.ap-guangzhou.myqcloud.com/exports/paper.docx?q-signature=abc%2B123&q-key-time=1;2'
  assert.equal(buildDownloadUrl(signedUrl), signedUrl)
})

test('word filename builder creates a docx filename safe for sharing', () => {
  assert.equal(buildWordFileName('Chem/Test:Paper', 'paper'), 'Chem_Test_Paper_paper.docx')
})
