/**
 * 通用工具函数
 */

// LaTeX 化学式转 Unicode（用于小程序显示）
export function latexToUnicode(text) {
  if (!text) return ''
  let result = text
  // 下标数字
  result = result.replace(/_\{?0\}?/g, '₀')
  result = result.replace(/_\{?1\}?/g, '₁')
  result = result.replace(/_\{?2\}?/g, '₂')
  result = result.replace(/_\{?3\}?/g, '₃')
  result = result.replace(/_\{?4\}?/g, '₄')
  result = result.replace(/_\{?5\}?/g, '₅')
  result = result.replace(/_\{?6\}?/g, '₆')
  result = result.replace(/_\{?7\}?/g, '₇')
  result = result.replace(/_\{?8\}?/g, '₈')
  result = result.replace(/_\{?9\}?/g, '₉')
  // 上标数字
  result = result.replace(/\^\{?0\}?/g, '⁰')
  result = result.replace(/\^\{?1\}?/g, '¹')
  result = result.replace(/\^\{?2\}?/g, '²')
  result = result.replace(/\^\{?3\}?/g, '³')
  result = result.replace(/\^\{?4\}?/g, '⁴')
  result = result.replace(/\^\{?5\}?/g, '⁵')
  result = result.replace(/\^\{?6\}?/g, '⁶')
  result = result.replace(/\^\{?7\}?/g, '⁷')
  result = result.replace(/\^\{?8\}?/g, '⁸')
  result = result.replace(/\^\{?9\}?/g, '⁹')
  result = result.replace(/\^\{?\+?\}?/g, '⁺')
  result = result.replace(/\^\{-\}?/g, '⁻')
  // 箭头
  result = result.replace(/\\rightarrow/g, '→')
  result = result.replace(/\\leftarrow/g, '←')
  result = result.replace(/\\leftrightarrow/g, '↔')
  // 希腊字母
  result = result.replace(/\\alpha/g, 'α')
  result = result.replace(/\\beta/g, 'β')
  result = result.replace(/\\gamma/g, 'γ')
  result = result.replace(/\\delta/g, 'δ')
  result = result.replace(/\\Delta/g, 'Δ')
  result = result.replace(/\\theta/g, 'θ')
  result = result.replace(/\\lambda/g, 'λ')
  result = result.replace(/\\mu/g, 'μ')
  result = result.replace(/\\pi/g, 'π')
  result = result.replace(/\\sigma/g, 'σ')
  // 其他符号
  result = result.replace(/\\times/g, '×')
  result = result.replace(/\\cdot/g, '·')
  result = result.replace(/\\pm/g, '±')
  result = result.replace(/\\geq/g, '≥')
  result = result.replace(/\\leq/g, '≤')
  result = result.replace(/\\neq/g, '≠')
  result = result.replace(/\\approx/g, '≈')
  // 移除 $ 符号
  result = result.replace(/\$/g, '')
  // 移除剩余的花括号
  result = result.replace(/\{|\}/g, '')
  return result
}

// 题型映射
export const QUESTION_TYPES = {
  choice: { label: '选择题', color: '#4A6CF7', icon: '📋' },
  fill: { label: '填空题', color: '#8B5CF6', icon: '✏️' },
  experiment: { label: '实验题', color: '#22C55E', icon: '🔬' },
  calculation: { label: '计算题', color: '#F59E0B', icon: '🧮' },
  short_answer: { label: '简答题', color: '#EC4899', icon: '📝' },
}

// 难度映射
export const DIFFICULTY_LEVELS = {
  1: { label: '极易', color: '#22C55E' },
  2: { label: '较易', color: '#84CC16' },
  3: { label: '中等', color: '#F59E0B' },
  4: { label: '较难', color: '#F97316' },
  5: { label: '极难', color: '#EF4444' },
}

// 格式化时间
export function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// 防抖
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

// 截断文本
export function truncate(text, maxLen = 50) {
  if (!text || text.length <= maxLen) return text
  return text.substring(0, maxLen) + '...'
}
