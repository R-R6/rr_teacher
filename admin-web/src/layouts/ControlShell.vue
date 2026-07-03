<template>
  <div class="shell">
    <aside class="shell__rail">
      <div class="brand-block">
        <p class="brand-block__eyebrow">Developer Console</p>
        <h1>化学教学后台</h1>
        <p>面向单人维护的内容、运行与成本中台。</p>
      </div>

      <nav class="nav-list">
        <RouterLink
          v-for="item in NAV_ITEMS"
          :key="item.key"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-item__icon"><IconGlyph :name="item.icon" /></span>
          <span>
            <strong>{{ item.label }}</strong>
            <small>{{ item.caption }}</small>
          </span>
        </RouterLink>
      </nav>

      <div class="rail-footer">
        <div class="identity-chip">
          <span class="identity-chip__dot"></span>
          <div>
            <strong>{{ auth.state.user?.nickname || auth.state.user?.username || '未登录' }}</strong>
            <small>白名单后台账号</small>
          </div>
        </div>
        <button class="ghost-button ghost-button--full" @click="logout">
          <IconGlyph name="logout" />
          <span>退出后台</span>
        </button>
      </div>
    </aside>

    <main class="shell__main">
      <header class="shell__topbar">
        <div>
          <p class="shell__topbar-eyebrow">Ops Ledger</p>
          <h2>{{ currentTitle }}</h2>
          <p class="shell__topbar-subtitle">{{ currentSubtitle }}</p>
        </div>
        <div class="shell__topbar-meta">
          <span>{{ todayLabel }}</span>
          <span class="mono-chip">{{ auth.state.user?.username || 'anonymous' }}</span>
        </div>
      </header>

      <section class="shell__content">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import IconGlyph from '@/components/IconGlyph.vue'
import { NAV_ITEMS } from '@/config/navigation.js'
import { clearAuthState, useAuthStore } from '@/stores/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const currentTitle = computed(() => route.meta.title || '后台控制台')
const currentSubtitle = computed(() => route.meta.subtitle || '集中处理内容、成本和运行问题。')
const todayLabel = computed(() =>
  new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  }).format(new Date())
)

function logout() {
  clearAuthState()
  router.push('/login')
}
</script>
