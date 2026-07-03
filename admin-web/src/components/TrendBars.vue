<template>
  <div class="trend-bars">
    <div
      v-for="item in normalizedItems"
      :key="item.key"
      class="trend-bars__item"
      :title="`${item.label}: ${item.value}`"
    >
      <div class="trend-bars__bar-shell">
        <div class="trend-bars__bar" :style="{ height: `${item.ratio}%` }"></div>
      </div>
      <div class="trend-bars__meta">
        <span class="trend-bars__label">{{ item.label }}</span>
        <span class="trend-bars__value">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  labelKey: {
    type: String,
    default: 'label',
  },
  valueKey: {
    type: String,
    default: 'value',
  },
})

const normalizedItems = computed(() => {
  const max = Math.max(...props.items.map((item) => Number(item[props.valueKey] || 0)), 1)
  return props.items.map((item, index) => {
    const value = Number(item[props.valueKey] || 0)
    return {
      key: item.key || `${index}-${item[props.labelKey]}`,
      label: item[props.labelKey],
      value,
      ratio: Math.max((value / max) * 100, value ? 12 : 4),
    }
  })
})
</script>
