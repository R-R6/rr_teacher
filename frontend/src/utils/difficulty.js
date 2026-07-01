export function buildDifficultyLabels(tags = [], fallbackLevels = {}, minCount = 5) {
  const difficultyTags = (tags || [])
    .filter((tag) => !tag.tag_type || tag.tag_type === 'difficulty')
    .slice()
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))

  const count = Math.max(minCount, difficultyTags.length)
  const labels = []
  for (let i = 0; i < count; i++) {
    labels.push(difficultyTags[i]?.name || fallbackLevels[i + 1]?.label || '')
  }
  return labels
}
