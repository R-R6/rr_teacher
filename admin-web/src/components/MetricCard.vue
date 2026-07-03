<template>
  <article class="metric-card">
    <p class="metric-card__label">{{ label }}</p>
    <div class="metric-card__value-row">
      <strong class="metric-card__value">{{ value }}</strong>
      <span v-if="accent" class="metric-card__accent">{{ accent }}</span>
    </div>
    <p v-if="caption" class="metric-card__caption">{{ caption }}</p>
  </article>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  accent: String,
  caption: String,
})
</script>
