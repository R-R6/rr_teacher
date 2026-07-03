<template>
  <div class="login-page">
    <section class="login-hero">
      <div>
        <p class="section-kicker">Industrial Console</p>
        <h1>把产品维护这件事<br />从查库变成管理。</h1>
        <p>
          这个控制台面向单人开发者，聚焦内容维护、OCR 质量、运行状态和成本核对。
          不做花哨的大屏，而是把每天真正会用到的数据和操作拉到一处。
        </p>
      </div>

      <div class="login-hero__ledger">
        <div class="ledger-row"><span>Question Ops</span><span>检索 / 编辑 / 删除保护</span></div>
        <div class="ledger-row"><span>OCR Review</span><span>原图 / 结果 / 人工修正</span></div>
        <div class="ledger-row"><span>Cost Watch</span><span>引擎 / 日期 / 用户维度</span></div>
        <div class="ledger-row"><span>Runtime Check</span><span>环境开关 / 健康摘要 / 数据规模</span></div>
      </div>
    </section>

    <section class="login-panel">
      <form class="login-card" @submit.prevent="submitLogin">
        <p class="login-card__eyebrow">Developer Access</p>
        <h2>后台登录</h2>
        <p>使用已配置白名单的系统账号进入控制台。</p>

        <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

        <div class="field-group">
          <label class="field-label" for="username">用户名</label>
          <input id="username" v-model.trim="form.username" class="text-input" autocomplete="username" />
        </div>

        <div class="field-group">
          <label class="field-label" for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            class="text-input"
            type="password"
            autocomplete="current-password"
          />
        </div>

        <div class="actions-row" style="margin-top: 8px;">
          <button class="primary-button" :disabled="loading" type="submit">
            {{ loading ? '登录中...' : '进入控制台' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi, authApi } from '@/api/admin.js'
import { DEFAULT_ROUTE } from '@/config/navigation.js'
import { clearAuthState, setAuthSession } from '@/stores/auth.js'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const form = reactive({
  username: '',
  password: '',
})

async function submitLogin() {
  if (!form.username || !form.password) {
    errorMessage.value = '请输入用户名和密码。'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const loginData = await authApi.login({
      username: form.username,
      password: form.password,
    })
    setAuthSession({
      accessToken: loginData.access_token,
      refreshToken: loginData.refresh_token,
      user: loginData.user,
    })
    const adminMe = await adminApi.getAdminMe()
    setAuthSession({
      accessToken: loginData.access_token,
      refreshToken: loginData.refresh_token,
      user: {
        ...loginData.user,
        ...adminMe,
      },
    })
    router.push(DEFAULT_ROUTE)
  } catch (error) {
    clearAuthState()
    errorMessage.value = error.message || '登录失败，请检查账号权限。'
  } finally {
    loading.value = false
  }
}
</script>
