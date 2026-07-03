<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="统计窗口" eyebrow="Budget Window">
      <div class="filters">
        <div class="field-group">
          <label class="field-label">统计天数</label>
          <select v-model.number="days" class="select-input">
            <option :value="7">近 7 天</option>
            <option :value="14">近 14 天</option>
            <option :value="30">近 30 天</option>
          </select>
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="loadUsage">刷新成本面板</button>
        </div>
      </div>
    </PanelCard>

    <section class="metric-strip">
      <MetricCard label="总调用量" :value="totals.total" caption="统计窗口内的 OCR 请求总数" />
      <MetricCard label="失败量" :value="totals.failed" caption="失败请求越高，越需要排查引擎或图片源质量" />
      <MetricCard label="引擎数" :value="usage.by_engine.length" caption="当前统计窗口内被调用过的 OCR 引擎" />
      <MetricCard label="活跃用户数" :value="usage.by_user.length" caption="至少有一次 OCR 调用的用户数" />
    </section>

    <div class="page-grid page-grid--two">
      <PanelCard title="按天调用趋势" eyebrow="Day Ledger">
        <TrendBars :items="usage.days" label-key="date" value-key="total" />
      </PanelCard>

      <PanelCard title="按引擎汇总" eyebrow="Engine Share">
        <div class="list-block">
          <div v-for="engine in usage.by_engine" :key="engine.engine" class="stat-row">
            <div class="split-copy">
              <strong>{{ engine.engine }}</strong>
              <small>失败 {{ engine.failed }}</small>
            </div>
            <strong>{{ engine.total }}</strong>
          </div>
        </div>
      </PanelCard>
    </div>

    <div class="page-grid page-grid--two">
      <PanelCard title="按用户汇总" eyebrow="User Pressure">
        <table class="data-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>总调用</th>
              <th>失败</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in usage.by_user" :key="user.user_id">
              <td>{{ user.username }}</td>
              <td>{{ user.total }}</td>
              <td>{{ user.failed }}</td>
            </tr>
          </tbody>
        </table>
      </PanelCard>

      <PanelCard title="按日期与引擎明细" eyebrow="Detailed Trace">
        <table class="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>引擎</th>
              <th>调用</th>
              <th>失败</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in usage.by_day_engine" :key="`${item.usage_day}-${item.engine}`">
              <td>{{ item.usage_day }}</td>
              <td>{{ item.engine }}</td>
              <td>{{ item.total }}</td>
              <td>{{ item.failed }}</td>
            </tr>
          </tbody>
        </table>
      </PanelCard>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import MetricCard from '@/components/MetricCard.vue'
import PanelCard from '@/components/PanelCard.vue'
import TrendBars from '@/components/TrendBars.vue'

const days = ref(7)
const usage = reactive({
  days: [],
  by_engine: [],
  by_day_engine: [],
  by_user: [],
})
const feedback = ref('')
const feedbackTone = ref('success')

const totals = computed(() => ({
  total: usage.by_day_engine.reduce((sum, item) => sum + Number(item.total || 0), 0),
  failed: usage.by_day_engine.reduce((sum, item) => sum + Number(item.failed || 0), 0),
}))

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

async function loadUsage() {
  try {
    const data = await adminApi.getOcrUsage(days.value)
    usage.days = data.days || []
    usage.by_engine = data.by_engine || []
    usage.by_day_engine = data.by_day_engine || []
    usage.by_user = data.by_user || []
  } catch (error) {
    applyFeedback(error.message || '成本监控加载失败。', 'error')
  }
}

onMounted(loadUsage)
</script>
