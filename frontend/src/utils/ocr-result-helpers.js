const FIGURE_KEYWORD_RE = /(如图|流程图|装置图|结构图|示意图|下图|上图)/

function normalizeText(value) {
  return String(value || '').replace(/\r/g, '').trim()
}

function buildOptionsText(options) {
  if (!Array.isArray(options)) return ''
  return options
    .map((option, index) => {
      const text = normalizeText(option?.text)
      if (!text) return ''
      const label = normalizeText(option?.label) || String.fromCharCode(65 + index)
      return `${label}. ${text}`
    })
    .filter(Boolean)
    .join('\n')
}

function buildBlocksText(blocks) {
  if (!Array.isArray(blocks)) return ''
  return blocks
    .map((block) => {
      if (!block || block.type === 'figure' || block.type === 'image') return ''
      return normalizeText(block.latex || block.content)
    })
    .filter(Boolean)
    .join('\n')
}

function mergeQuestionAndOptions(questionText, optionsText) {
  const base = normalizeText(questionText)
  const optionLines = normalizeText(optionsText)
  if (!base) return optionLines
  if (!optionLines) return base
  if (base.includes('A.') || base.includes('A．')) return base
  return `${base}\n${optionLines}`.trim()
}

function pickLongest(candidates) {
  return candidates
    .map(normalizeText)
    .filter(Boolean)
    .sort((left, right) => right.length - left.length)[0] || ''
}

export function buildQuestionContent(data = {}) {
  const structured = data.structured || {}
  const optionsText = buildOptionsText(structured.options)
  const mergedStructuredText = mergeQuestionAndOptions(structured.question_text, optionsText)
  const blocksText = buildBlocksText(structured.blocks)

  if (mergedStructuredText) {
    if (
      blocksText &&
      normalizeText(structured.question_text) &&
      blocksText.includes(normalizeText(structured.question_text)) &&
      blocksText.length > mergedStructuredText.length + 8
    ) {
      return blocksText
    }
    return mergedStructuredText
  }

  return pickLongest([
    data.result_text,
    blocksText,
    data.result_latex,
  ])
}

export function getQualitySummary({ confidence = 0, structured = {} } = {}) {
  const score = Number(confidence || 0)
  const needsReview = Boolean(structured?.needs_human_review) || score < 0.8

  if (needsReview) {
    return {
      label: '识别质量：需复核',
      note: '仅供参考',
      needsReview: true,
    }
  }

  if (score >= 0.95) {
    return {
      label: '识别质量：较高',
      note: '仅供参考',
      needsReview: false,
    }
  }

  return {
    label: '识别质量：一般',
    note: '仅供参考',
    needsReview: false,
  }
}

export function shouldSuggestSupplementalFigure({
  content = '',
  images = [],
  structured = {},
  result_text = '',
  result_latex = '',
} = {}) {
  if (Array.isArray(images) && images.length > 0) return false

  const figureAnalysis = structured?.figure_analysis || {}
  const mergedText = [
    content,
    result_text,
    result_latex,
    structured?.question_text,
  ]
    .map(normalizeText)
    .filter(Boolean)
    .join('\n')

  const modelSuggests =
    Boolean(figureAnalysis.has_figure) &&
    (Boolean(figureAnalysis.should_keep_original) || figureAnalysis.extractable === false)

  return modelSuggests || FIGURE_KEYWORD_RE.test(mergedText)
}

// 选项标记：A. xxx / A．xxx / A、xxx。兼容少量 OCR 噪声，如 6B.、OC.。
const OPTION_MARKER_RE = /(^|[\s\d])([O0]?)([A-D])[.．、:：]\s*/g
const OPTION_LABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

function findOptionMarkers(line) {
  const markers = []
  const optionMarkerRe = new RegExp(OPTION_MARKER_RE.source, 'g')
  let match
  while ((match = optionMarkerRe.exec(line)) !== null) {
    const prefix = match[1] || ''
    const noise = match[2] || ''
    const label = match[3]
    if (noise && label !== 'C') continue
    const rawStart = match.index + prefix.length
    markers.push({
      label,
      rawStart,
      markerStart: rawStart + noise.length,
      textStart: optionMarkerRe.lastIndex,
    })
  }
  return markers
}

function normalizeOptionList(options) {
  if (!Array.isArray(options)) return []
  return options
    .map((option, index) => {
      const label = normalizeText(option && option.label).toUpperCase() || String.fromCharCode(65 + index)
      const text = normalizeText(option && option.text)
      if (!text) return null
      return { label, text }
    })
    .filter(Boolean)
}

function optionLabelIndex(label) {
  return OPTION_LABELS.indexOf(String(label || '').toUpperCase())
}

export function sortOptionsByLabel(options) {
  if (!Array.isArray(options)) return []
  return options
    .map((option, index) => ({ option, index }))
    .sort((left, right) => {
      const leftIndex = optionLabelIndex(left.option && left.option.label)
      const rightIndex = optionLabelIndex(right.option && right.option.label)
      const normalizedLeft = leftIndex >= 0 ? leftIndex : OPTION_LABELS.length + left.index
      const normalizedRight = rightIndex >= 0 ? rightIndex : OPTION_LABELS.length + right.index
      return normalizedLeft - normalizedRight
    })
    .map(item => item.option)
}

export function getNextOptionLabel(options) {
  const usedLabels = new Set(
    (Array.isArray(options) ? options : [])
      .map(option => String((option && option.label) || '').toUpperCase())
      .filter(Boolean)
  )
  for (const label of OPTION_LABELS) {
    if (!usedLabels.has(label)) return label
  }
  return String(usedLabels.size + 1)
}

export function parseOptionsFromText(text) {
  if (!text || typeof text !== 'string') {
    return []
  }

  const labelMap = new Map() // 用于去重，保留最后一个

  text.replace(/\r/g, '').split('\n').forEach((line) => {
    const markers = findOptionMarkers(line)
    markers.forEach((marker, index) => {
      const nextMarker = markers[index + 1]
      const optionText = line
        .slice(marker.textStart, nextMarker ? nextMarker.rawStart : line.length)
        .trim()
      if (optionText) {
        labelMap.set(marker.label, {
          label: marker.label,
          text: optionText,
        })
      }
    })
  })

  return sortOptionsByLabel(Array.from(labelMap.values()))
}

export function buildOcrEditData(data = {}) {
  const structured = data.structured || {}
  const rawContent = normalizeText(data.rawContent || data.content || '')
  const structuredOptions = data.engine === 'doubao_vision'
    ? normalizeOptionList(structured.options)
    : []
  const parsedOptions = sortOptionsByLabel(structuredOptions.length ? structuredOptions : parseOptionsFromText(rawContent))
  const structuredQuestionText = normalizeText(structured.question_text)
  const cleanedContent = parsedOptions.length ? removeOptionsFromText(rawContent) : rawContent
  const structuredContent = parsedOptions.length
    ? mergeQuestionAndOptions(structuredQuestionText, buildOptionsText(parsedOptions))
    : structuredQuestionText
  const content = rawContent || structuredContent || cleanedContent

  const result = {
    content,
    options: parsedOptions,
    source_image_url: data.imageUrl || data.source_image_url || '',
    ocr_record_id: data.recordId || data.ocr_record_id || '',
    focusFigure: Boolean(data.focusFigure),
  }

  if (parsedOptions.length) {
    result.question_type = 'choice'
  }

  return result
}

export function removeOptionsFromText(text) {
  if (!text || typeof text !== 'string') {
    return ''
  }

  return text
    .replace(/\r/g, '')
    .split('\n')
    .map((line) => {
      const markers = findOptionMarkers(line)
      if (!markers.length) return line
      const prefix = line.slice(0, markers[0].rawStart).trim()
      return prefix
    })
    .filter(line => line.trim())
    .join('\n')
    .trim()
}
