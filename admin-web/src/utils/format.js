const QUESTION_TYPE_LABELS = {
  choice: '选择题',
  fill: '填空题',
  experiment: '实验题',
  calculation: '计算题',
  short_answer: '简答题',
}

export function formatDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function truncate(text, length = 60) {
  const value = String(text || '')
  return value.length > length ? `${value.slice(0, length)}…` : value
}

export function questionTypeLabel(type) {
  return QUESTION_TYPE_LABELS[type] || type || '未分类'
}

export function difficultyLabel(level) {
  const value = Number(level || 0)
  return value > 0 ? `难度 ${value}` : '未设定'
}

export function toneByStatus(status) {
  if (status === 'ok' || status === true) return 'success'
  if (status === 'warning' || status === 'notice') return 'warning'
  if (status === 'danger' || status === 'failed' || status === false) return 'danger'
  return 'neutral'
}

export function yesNoLabel(value, positive = '是', negative = '否') {
  return value === true || value === 'true' ? positive : negative
}
