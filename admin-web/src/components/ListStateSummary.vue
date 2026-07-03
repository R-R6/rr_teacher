<template>
  <div class="list-state-summary">
    <div class="list-state-summary__copy">
      <strong>{{ title }}</strong>
      <small>{{ subtitle }}</small>
    </div>
    <div v-if="chips.length" class="tag-cloud">
      <span v-for="chip in chips" :key="chip.key" class="tag-chip tag-chip--soft">
        {{ chip.label }}: {{ chip.value }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  chips: {
    type: Array,
    default: () => [],
  },
})
</script>
