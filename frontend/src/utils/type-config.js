const CORE_TYPE_KEYS = ['choice', 'fill', 'experiment', 'calculation', 'short_answer']

export function buildTypeConfigs(tags = [], fallbackTypes = {}) {
  const typeTags = (tags || [])
    .filter((tag) => !tag.tag_type || tag.tag_type === 'type')
    .slice()
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))

  const configs = {}
  CORE_TYPE_KEYS.forEach((key, index) => {
    const fallback = fallbackTypes[key] || {}
    configs[key] = {
      ...fallback,
      label: typeTags[index]?.name || fallback.label || key,
    }
  })
  return configs
}
