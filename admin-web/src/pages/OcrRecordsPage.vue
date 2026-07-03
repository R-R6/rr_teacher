<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="OCR 记录筛选" eyebrow="Recognition Trace">
      <div class="filters">
        <div class="field-group">
          <label class="field-label">引擎</label>
          <select v-model="filters.engine" class="select-input">
            <option value="">全部</option>
            <option value="tesseract">tesseract</option>
            <option value="pix2text_online">pix2text_online</option>
            <option value="doubao_vision">doubao_vision</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">状态</label>
          <select v-model="filters.status" class="select-input">
            <option value="">全部</option>
            <option value="ok">正常</option>
            <option value="corrected">已修正</option>
            <option value="empty">空结果</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">开始日期</label>
          <input v-model="filters.date_from" class="text-input" type="date" />
        </div>
        <div class="field-group">
          <label class="field-label">结束日期</label>
          <input v-model="filters.date_to" class="text-input" type="date" />
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="loadRecords(1)">查询记录</button>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="OCR 记录列表" eyebrow="Recognition Ledger">
      <ListStateSummary
        :title="resultMeta.totalLabel"
        :subtitle="`${resultMeta.rangeLabel} · ${resultMeta.filterLabel}`"
        :chips="activeFilterItems"
      />

      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>记录</th>
              <th>用户</th>
              <th>引擎</th>
              <th>状态</th>
              <th>置信度</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>
                <strong>{{ row.id }}</strong>
                <small>{{ row.result_text_preview || '无文本预览' }}</small>
              </td>
              <td>
                <strong>{{ row.nickname || row.username }}</strong>
                <small>{{ row.user_id }}</small>
              </td>
              <td>{{ row.engine }}</td>
              <td><StatusPill :tone="row.status === 'ok' ? 'success' : row.status === 'corrected' ? 'warning' : 'danger'">{{ row.status }}</StatusPill></td>
              <td>{{ row.confidence ?? '—' }}</td>
              <td>{{ formatDateTime(row.created_at) }}</td>
              <td>
                <div class="table-actions">
                  <button @click="openRecord(row)">查看</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="showEmptyState" class="empty-panel">
        <strong>{{ emptyState.title }}</strong>
        <p>{{ emptyState.detail }}</p>
      </div>

      <div class="actions-row" style="justify-content: space-between; margin-top: 18px;">
        <span class="mono-chip">{{ loading ? '同步 OCR 记录中...' : `共 ${total} 条` }}</span>
        <div class="actions-row">
          <button class="ghost-button" :disabled="page <= 1" @click="loadRecords(page - 1)">上一页</button>
          <button class="ghost-button" :disabled="page * pageSize >= total" @click="loadRecords(page + 1)">下一页</button>
        </div>
      </div>
    </PanelCard>

    <DrawerPanel :open="drawerOpen" title="OCR 记录详情" eyebrow="Correction Desk" @close="drawerOpen = false">
      <div v-if="selectedRecord" class="page-stack">
        <img v-if="selectedRecord.origin_image_url" :src="selectedRecord.origin_image_url" alt="" class="hero-image" />
        <div class="summary-grid summary-grid--two">
          <div class="mini-card">
            <p class="field-label">引擎</p>
            <strong>{{ selectedRecord.engine }}</strong>
            <small>置信度 {{ selectedRecord.confidence ?? '—' }}</small>
          </div>
          <div class="mini-card">
            <p class="field-label">用户</p>
            <strong>{{ selectedRecord.nickname || selectedRecord.username }}</strong>
            <small>{{ selectedRecord.user_id }}</small>
          </div>
        </div>

        <div class="field-group">
          <label class="field-label">LaTeX 结果</label>
          <textarea v-model="correction.corrected_latex" class="text-area"></textarea>
        </div>
        <div class="field-group">
          <label class="field-label">纯文本结果</label>
          <textarea v-model="correction.corrected_text" class="text-area"></textarea>
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="saveCorrection">保存修正</button>
        </div>

        <div class="summary-grid summary-grid--two">
          <div class="mini-card">
            <p class="field-label">原始 LaTeX</p>
            <div class="copy-block">{{ selectedRecord.ocr_result_latex || '—' }}</div>
          </div>
          <div class="mini-card">
            <p class="field-label">原始文本</p>
            <div class="copy-block">{{ selectedRecord.ocr_result_text || '—' }}</div>
          </div>
        </div>

        <div v-if="selectedRecord.images?.length" class="page-stack">
          <p class="field-label">附图</p>
          <div class="image-grid">
            <img v-for="image in selectedRecord.images" :key="image.id" :src="image.image_url" alt="" />
          </div>
        </div>
      </div>
    </DrawerPanel>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import DrawerPanel from '@/components/DrawerPanel.vue'
import ListStateSummary from '@/components/ListStateSummary.vue'
import PanelCard from '@/components/PanelCard.vue'
import StatusPill from '@/components/StatusPill.vue'
import { buildEmptyState, buildResultMeta, describeActiveFilters } from '@/utils/list-state.js'
import { formatDateTime } from '@/utils/format.js'

const filters = reactive({
  engine: '',
  status: '',
  date_from: '',
  date_to: '',
})

const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const drawerOpen = ref(false)
const selectedRecord = ref(null)
const correction = reactive({
  corrected_latex: '',
  corrected_text: '',
})
const feedback = ref('')
const feedbackTone = ref('success')
const loading = ref(false)

const hasError = computed(() => feedbackTone.value === 'error' && Boolean(feedback.value))

const activeFilterItems = computed(() =>
  describeActiveFilters(filters, {
    engine: '引擎',
    status: '状态',
    date_from: '开始日期',
    date_to: '结束日期',
  })
)

const resultMeta = computed(() =>
  buildResultMeta({
    total: total.value,
    page: page.value,
    pageSize,
    noun: '条 OCR 记录',
    activeFilterCount: activeFilterItems.value.length,
  })
)

const emptyState = computed(() =>
  buildEmptyState({
    noun: 'OCR 记录',
    hasFilters: activeFilterItems.value.length > 0,
    defaultHint:
      activeFilterItems.value.length > 0
        ? '可以尝试放宽日期范围或切换引擎后重新查询。'
        : '暂无 OCR 样本时，可以先通过联调数据或真实识别记录补充。',
  })
)

const showEmptyState = computed(() => !loading.value && !hasError.value && rows.value.length === 0)

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

async function loadRecords(nextPage = page.value) {
  loading.value = true
  try {
    page.value = nextPage
    const data = await adminApi.listOcrRecords({
      page: page.value,
      page_size: pageSize,
      engine: filters.engine,
      status: filters.status,
      date_from: filters.date_from,
      date_to: filters.date_to,
    })
    rows.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function openRecord(row) {
  const detail = await adminApi.getOcrRecord(row.id)
  selectedRecord.value = detail
  correction.corrected_latex = detail.ocr_result_latex || ''
  correction.corrected_text = detail.ocr_result_text || ''
  drawerOpen.value = true
}

async function saveCorrection() {
  try {
    await adminApi.correctOcrRecord(selectedRecord.value.id, {
      record_id: selectedRecord.value.id,
      corrected_latex: correction.corrected_latex,
      corrected_text: correction.corrected_text,
    })
    applyFeedback('OCR 修正已保存。')
    await openRecord({ id: selectedRecord.value.id })
    await loadRecords(page.value)
  } catch (error) {
    applyFeedback(error.message || 'OCR 修正失败。', 'error')
  }
}

onMounted(async () => {
  try {
    await loadRecords(1)
  } catch (error) {
    applyFeedback(error.message || 'OCR 记录加载失败。', 'error')
  }
})
</script>
