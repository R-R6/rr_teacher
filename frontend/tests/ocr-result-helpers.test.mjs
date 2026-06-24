import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const helperSource = await readFile(new URL('../src/utils/ocr-result-helpers.js', import.meta.url), 'utf8')
const helperModule = await import(`data:text/javascript;base64,${Buffer.from(helperSource).toString('base64')}`)

const {
  buildQuestionContent,
  buildOcrEditData,
  getNextOptionLabel,
  getQualitySummary,
  shouldSuggestSupplementalFigure,
  parseOptionsFromText,
  removeOptionsFromText,
  sortOptionsByLabel,
} = helperModule

test('buildQuestionContent prefers structured question text and appends options', () => {
  const content = buildQuestionContent({
    result_text: 'A short truncated line',
    structured: {
      question_text: '下列说法正确的是',
      options: [
        { label: 'A', text: '氯化钠属于氧化物' },
        { label: 'B', text: '硫酸属于酸' },
      ],
      blocks: [
        { type: 'text', content: '下列说法正确的是' },
      ],
    },
  })

  assert.equal(
    content,
    '下列说法正确的是\nA. 氯化钠属于氧化物\nB. 硫酸属于酸',
  )
})

test('buildQuestionContent falls back to the longest non-empty candidate when structured text is absent', () => {
  const content = buildQuestionContent({
    result_text: '乙烯能使酸性高锰酸钾溶液褪色',
    result_latex: '乙烯能使酸性高锰酸钾溶液褪色，说明乙烯具有还原性',
    structured: {
      question_text: '',
      blocks: [],
      options: [],
    },
  })

  assert.equal(content, '乙烯能使酸性高锰酸钾溶液褪色，说明乙烯具有还原性')
})

test('getQualitySummary marks low confidence or manual-review results as needing review', () => {
  const reviewState = getQualitySummary({
    confidence: 0.72,
    structured: {
      needs_human_review: true,
    },
  })

  assert.deepEqual(reviewState, {
    label: '识别质量：需复核',
    note: '仅供参考',
    needsReview: true,
  })
})

test('shouldSuggestSupplementalFigure returns true when a figure is detected but no figure image is attached', () => {
  const shouldSuggest = shouldSuggestSupplementalFigure({
    content: '根据如图所示装置回答问题',
    images: [],
    structured: {
      figure_analysis: {
        has_figure: true,
        should_keep_original: true,
      },
    },
  })

  assert.equal(shouldSuggest, true)
})

test('parseOptionsFromText parses A. B. style options from text', () => {
  const text = `下列说法正确的是
A. 氯化钠属于氧化物
B. 硫酸属于酸
C. 氢氧化钠属于碱
D. 碳酸钙属于盐`

  const options = parseOptionsFromText(text)
  assert.equal(options.length, 4)
  assert.equal(options[0].label, 'A')
  assert.equal(options[0].text, '氯化钠属于氧化物')
  assert.equal(options[1].label, 'B')
  assert.equal(options[1].text, '硫酸属于酸')
})

test('parseOptionsFromText handles Chinese separators ． and 、', () => {
  const text = `下列说法正确的是
A．氯化钠属于氧化物
B、硫酸属于酸`

  const options = parseOptionsFromText(text)
  assert.equal(options.length, 2)
  assert.equal(options[0].label, 'A')
  assert.equal(options[0].text, '氯化钠属于氧化物')
  assert.equal(options[1].label, 'B')
  assert.equal(options[1].text, '硫酸属于酸')
})

test('parseOptionsFromText parses multiple options on one OCR line', () => {
  const text = '下列物质属于盐的是 A. NaCl B. H2SO4 C．NaOH D、CaCO3'

  const options = parseOptionsFromText(text)
  assert.deepEqual(options, [
    { label: 'A', text: 'NaCl' },
    { label: 'B', text: 'H2SO4' },
    { label: 'C', text: 'NaOH' },
    { label: 'D', text: 'CaCO3' },
  ])
  assert.equal(removeOptionsFromText(text), '下列物质属于盐的是')
})

test('parseOptionsFromText tolerates noisy OCR markers before B and C', () => {
  const text = '【2306】材料是人类赖以生存和发展的物质基础，下列材料主要成分属于有机物的是 A5 6B. 不锈钢 OC. 石英光导纤维 D. 聚酯纤维'

  const options = parseOptionsFromText(text)
  assert.deepEqual(options, [
    { label: 'B', text: '不锈钢' },
    { label: 'C', text: '石英光导纤维' },
    { label: 'D', text: '聚酯纤维' },
  ])
})

test('parseOptionsFromText returns empty array for text without options', () => {
  const text = '这是一道没有选项的简答题，请回答下列问题。'
  const options = parseOptionsFromText(text)
  assert.equal(options.length, 0)
})

test('parseOptionsFromText deduplicates options with same label', () => {
  const text = `A. 第一个选项
A. 重复的选项
B. 第二个选项`

  const options = parseOptionsFromText(text)
  assert.equal(options.length, 2)
  // 应该保留最后一个
  assert.equal(options[0].text, '重复的选项')
})

test('removeOptionsFromText removes option lines from text', () => {
  const text = `下列说法正确的是
A. 氯化钠属于氧化物
B. 硫酸属于酸
C. 氢氧化钠属于碱
这是一些额外的文字`

  const result = removeOptionsFromText(text)
  assert.equal(result, '下列说法正确的是\n这是一些额外的文字')
})

test('removeOptionsFromText returns unchanged text when no options present', () => {
  const text = '这是一道没有选项的简答题。'
  const result = removeOptionsFromText(text)
  assert.equal(result, text)
})

test('buildOcrEditData prefers doubao structured data for edit form', () => {
  const result = buildOcrEditData({
    rawContent: '下列物质属于盐的是\nA. 错误选项',
    engine: 'doubao_vision',
    recordId: 'rec-1',
    imageUrl: 'https://example.com/q.png',
    focusFigure: true,
    structured: {
      question_text: '下列物质属于盐的是',
      options: [
        { label: 'A', text: 'NaCl' },
        { label: 'B', text: 'H2SO4' },
      ],
    },
  })

  assert.deepEqual(result, {
    content: '下列物质属于盐的是\nA. 错误选项',
    options: [
      { label: 'A', text: 'NaCl' },
      { label: 'B', text: 'H2SO4' },
    ],
    question_type: 'choice',
    source_image_url: 'https://example.com/q.png',
    ocr_record_id: 'rec-1',
    focusFigure: true,
  })
})

test('getNextOptionLabel fills the first missing middle label', () => {
  const next = getNextOptionLabel([
    { label: 'A', text: '石墨烯' },
    { label: 'B', text: '不锈钢' },
    { label: 'D', text: '聚酯纤维' },
  ])

  assert.equal(next, 'C')
})

test('sortOptionsByLabel keeps option rows in label order', () => {
  const sorted = sortOptionsByLabel([
    { label: 'D', text: '聚酯纤维' },
    { label: 'B', text: '不锈钢' },
    { label: 'C', text: '石英光导纤维' },
  ])

  assert.deepEqual(sorted, [
    { label: 'B', text: '不锈钢' },
    { label: 'C', text: '石英光导纤维' },
    { label: 'D', text: '聚酯纤维' },
  ])
})
