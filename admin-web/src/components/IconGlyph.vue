<template>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path v-for="(segment, index) in segments" :key="index" :d="segment" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
})

const paths = {
  dashboard: ['M3 12.5 12 4l9 8.5', 'M6 10.5V20h12v-9.5', 'M10 20v-5h4v5'],
  questions: ['M6 4h12v16H6z', 'M9 8h6', 'M9 12h6', 'M9 16h4'],
  tags: ['M4 12l8-8 8 8-8 8-8-8z', 'M12 8v8', 'M8 12h8'],
  ocr: ['M5 5h5', 'M14 5h5', 'M5 19h5', 'M14 19h5', 'M8 8h8v8H8z'],
  papers: ['M7 3h8l4 4v14H7z', 'M15 3v5h4', 'M10 13h6', 'M10 17h6'],
  users: ['M16 21v-1.5A3.5 3.5 0 0 0 12.5 16h-1A3.5 3.5 0 0 0 8 19.5V21', 'M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6', 'M18 9.5a2 2 0 1 0 0-4', 'M19.5 21v-1a2.5 2.5 0 0 0-2.5-2.5'],
  cost: ['M4 18 9 12 13 14 20 7', 'M20 7h-4', 'M20 7v4', 'M4 20h16'],
  billing: ['M6 4h12v16H6z', 'M9 8h6', 'M9 12h6', 'M9 16h3', 'M16 16h.01'],
  system: ['M12 3v4', 'M12 17v4', 'M4.9 4.9l2.8 2.8', 'M16.3 16.3l2.8 2.8', 'M3 12h4', 'M17 12h4', 'M4.9 19.1l2.8-2.8', 'M16.3 7.7l2.8-2.8', 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6'],
  logout: ['M10 6V4h9v16h-9v-2', 'M14 12H5', 'M8 9l-3 3 3 3'],
  refresh: ['M20 11a8 8 0 0 0-14.9-3', 'M4 5v3.8h3.8', 'M4 13a8 8 0 0 0 14.9 3', 'M20 19v-3.8h-3.8'],
  search: ['M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14', 'M20 20l-3.5-3.5'],
  edit: ['M4 20h4l10-10-4-4L4 16v4', 'M12 6l4 4'],
  delete: ['M5 7h14', 'M9 7V4h6v3', 'M8 10v7', 'M12 10v7', 'M16 10v7'],
  eye: ['M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12Z', 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6'],
}

const segments = computed(() => paths[props.name] || paths.dashboard)
</script>
