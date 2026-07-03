<template>
  <section class="panel-card">
    <header v-if="title || eyebrow" class="panel-card__header">
      <div>
        <p v-if="eyebrow" class="panel-card__eyebrow">{{ eyebrow }}</p>
        <h3 v-if="title" class="panel-card__title">{{ title }}</h3>
      </div>
      <slot name="header" />
    </header>
    <div class="panel-card__body">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: String,
  eyebrow: String,
})
</script>
