function hasMeaningfulValue(value) {
  if (value === undefined || value === null || value === '') return false
  if (Array.isArray(value)) return value.length > 0
  return true
}

function resolveConfigEntry(config) {
  if (typeof config === 'string') {
    return {
      label: config,
      format: (value) => String(value),
    }
  }
  return {
    label: config?.label || '',
    format: config?.format || ((value) => String(value)),
  }
}

export function describeActiveFilters(filters, configMap) {
  return Object.entries(configMap).flatMap(([key, config]) => {
    const value = filters?.[key]
    if (!hasMeaningfulValue(value)) return []
    const { label, format } = resolveConfigEntry(config)
    return [{ key, label, value: format(value) }]
  })
}

export function buildResultMeta({ total = 0, page = 1, pageSize = 20, noun = '条数据', activeFilterCount = 0 }) {
  if (!total) {
    return {
      totalLabel: `共 0 ${noun}`,
      rangeLabel: '当前没有可展示的数据',
      filterLabel: activeFilterCount > 0 ? `已启用 ${activeFilterCount} 个筛选条件` : '未启用筛选条件',
    }
  }

  const start = (Math.max(page, 1) - 1) * pageSize + 1
  const end = Math.min(total, start + pageSize - 1)

  return {
    totalLabel: `共 ${total} ${noun}`,
    rangeLabel: `当前显示第 ${start}-${end} 条`,
    filterLabel: activeFilterCount > 0 ? `已启用 ${activeFilterCount} 个筛选条件` : '未启用筛选条件',
  }
}

export function buildEmptyState({ noun = '数据', hasFilters = false, defaultHint = '请稍后重试。' }) {
  if (hasFilters) {
    return {
      title: `未找到符合筛选条件的 ${noun}`,
      detail: defaultHint,
    }
  }

  return {
    title: `当前还没有${noun}数据`,
    detail: defaultHint,
  }
}
