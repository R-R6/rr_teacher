<template>
  <div class="page-stack">
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="actions-row">
      <button class="ghost-button" @click="loadPage">
        <IconGlyph name="refresh" />
        <span>刷新仪表盘</span>
      </button>
      <span class="mono-chip">{{ loading ? 'loading' : 'stable' }}</span>
    </div>

    <section class="metric-strip">
      <MetricCard label="题目总数" :value="summary.question_count ?? '—'" caption="题库累计沉淀的题目数量" />
      <MetricCard label="标签总数" :value="summary.tag_count ?? '—'" caption="教材、知识点、题型与难度标签" />
      <MetricCard label="试卷总数" :value="summary.paper_count ?? '—'" caption="已创建的试卷及导出容器" />
      <MetricCard
        label="今日 OCR 调用"
        :value="summary.ocr_total_today ?? '—'"
        :accent="`失败 ${summary.ocr_failed_today ?? 0}`"
        caption="按 usage_log 汇总的当日 OCR 请求"
      />
    </section>

    <div class="page-grid page-grid--two">
      <PanelCard title="最近 7 天 OCR 趋势" eyebrow="Usage Trace">
        <TrendBars :items="trend.days" label-key="date" value-key="total" />
      </PanelCard>

      <PanelCard title="近期风险" eyebrow="Action Queue">
        <div class="risk-list">
          <article v-for="risk in risks.items" :key="risk.title" class="risk-item">
            <div class="actions-row" style="justify-content: space-between;">
              <strong>{{ risk.title }}</strong>
              <StatusPill :tone="risk.level === 'ok' ? 'success' : 'warning'">{{ risk.level }}</StatusPill>
            </div>
            <p class="muted-text" style="margin: 8px 0 0;">{{ risk.detail }}</p>
          </article>
        </div>
      </PanelCard>
    </div>

    <div class="page-grid page-grid--two">
      <PanelCard title="内容健康摘要" eyebrow="Content Ledger">
        <div class="summary-grid summary-grid--two">
          <div class="mini-card">
            <p class="field-label">未校对题目</p>
            <strong style="font-size: 30px;">{{ summary.unverified_question_count ?? 0 }}</strong>
            <p class="muted-text">优先处理 OCR 入库后尚未复核的内容。</p>
          </div>
          <div class="mini-card">
            <p class="field-label">后台可见用户</p>
            <strong style="font-size: 30px;">{{ summary.user_count ?? 0 }}</strong>
            <p class="muted-text">用于核对内容归属与 OCR 使用分布。</p>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="引擎趋势明细" eyebrow="Engine Breakdown">
        <div class="list-block">
          <div
            v-for="item in trend.items.slice(0, 8)"
            :key="`${item.usage_day}-${item.engine}`"
            class="stat-row"
          >
            <div class="split-copy">
              <strong>{{ item.engine }}</strong>
              <small>{{ item.usage_day }}</small>
            </div>
            <div class="split-copy" style="text-align: right;">
              <strong>{{ item.total }}</strong>
              <small>失败 {{ item.failed }}</small>
            </div>
          </div>
        </div>
      </PanelCard>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import IconGlyph from '@/components/IconGlyph.vue'
import MetricCard from '@/components/MetricCard.vue'
import PanelCard from '@/components/PanelCard.vue'
import StatusPill from '@/components/StatusPill.vue'
import TrendBars from '@/components/TrendBars.vue'

const loading = ref(false)
const errorMessage = ref('')
const summary = reactive({})
const trend = reactive({ days: [], items: [] })
const risks = reactive({ items: [] })

async function loadPage() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [summaryData, trendData, riskData] = await Promise.all([
      adminApi.getDashboardSummary(),
      adminApi.getDashboardTrend(),
      adminApi.getRecentRisks(),
    ])
    Object.assign(summary, summaryData)
    trend.days = trendData.days || []
    trend.items = trendData.items || []
    risks.items = riskData.items || []
  } catch (error) {
    errorMessage.value = error.message || '仪表盘加载失败。'
  } finally {
    loading.value = false
  }
}

onMounted(loadPage)
</script>
