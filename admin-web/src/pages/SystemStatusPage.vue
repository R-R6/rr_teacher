<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="当前系统状态" eyebrow="Runtime Snapshot">
      <div class="actions-row" style="margin-bottom: 18px;">
        <button class="ghost-button" @click="loadStatus">刷新系统摘要</button>
      </div>
      <div v-if="status" class="summary-grid summary-grid--three">
        <div class="mini-card">
          <p class="field-label">健康状态</p>
          <StatusPill :tone="status.health === 'ok' ? 'success' : 'danger'">{{ status.health }}</StatusPill>
        </div>
        <div class="mini-card">
          <p class="field-label">数据库</p>
          <div class="status-value-stack">
            <strong>{{ status.database?.type }}</strong>
            <small>{{ status.database?.name || '—' }}</small>
            <small>{{ status.database?.host_masked || '—' }}</small>
          </div>
        </div>
        <div class="mini-card">
          <p class="field-label">存储模式</p>
          <div class="status-value-stack">
            <strong>{{ status.storage?.mode }}</strong>
            <small>{{ status.storage?.bucket || '本地文件' }}</small>
          </div>
        </div>
      </div>
    </PanelCard>

    <div class="page-grid page-grid--two" v-if="status">
      <PanelCard title="OCR 与运行开关" eyebrow="Service Switches">
        <div class="list-block">
          <div class="stat-row">
            <strong>默认 OCR 引擎</strong>
            <span>{{ status.ocr?.default_engine }}</span>
          </div>
          <div class="stat-row">
            <strong>调试模式</strong>
            <span>{{ status.runtime?.debug }}</span>
          </div>
          <div class="stat-row">
            <strong>接口文档</strong>
            <span>{{ status.runtime?.swagger_enabled }}</span>
          </div>
          <div class="stat-row">
            <strong>全局限流</strong>
            <span>{{ status.runtime?.rate_limit_per_minute }}</span>
          </div>
          <div class="stat-row">
            <strong>登录限流</strong>
            <span>{{ status.runtime?.login_rate_limit }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="运行数据量" eyebrow="Scale Snapshot">
        <div class="summary-grid summary-grid--two">
          <div class="mini-card">
            <p class="field-label">题目总数</p>
            <strong style="font-size: 32px;">{{ status.runtime?.question_count }}</strong>
          </div>
          <div class="mini-card">
            <p class="field-label">用户总数</p>
            <strong style="font-size: 32px;">{{ status.runtime?.user_count }}</strong>
          </div>
        </div>
      </PanelCard>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import PanelCard from '@/components/PanelCard.vue'
import StatusPill from '@/components/StatusPill.vue'

const status = ref(null)
const feedback = ref('')
const feedbackTone = ref('success')

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

async function loadStatus() {
  try {
    status.value = await adminApi.getSystemStatus()
  } catch (error) {
    applyFeedback(error.message || '系统状态加载失败。', 'error')
  }
}

onMounted(loadStatus)
</script>
