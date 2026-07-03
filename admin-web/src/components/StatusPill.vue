<template>
  <span class="status-pill" :data-tone="tone">
    <slot />
  </span>
</template>

<script setup>
defineProps({
  tone: {
    type: String,
    default: 'neutral',
  },
})
</script>
