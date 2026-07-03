<template>
  <transition name="drawer">
    <div v-if="open" class="drawer">
      <button class="drawer__mask" @click="$emit('close')" aria-label="关闭详情"></button>
      <aside class="drawer__panel">
        <header class="drawer__header">
          <div>
            <p v-if="eyebrow" class="drawer__eyebrow">{{ eyebrow }}</p>
            <h3 class="drawer__title">{{ title }}</h3>
          </div>
          <button class="ghost-button" @click="$emit('close')">关闭</button>
        </header>
        <div class="drawer__body">
          <slot />
        </div>
      </aside>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  open: Boolean,
  title: String,
  eyebrow: String,
})

defineEmits(['close'])
</script>
