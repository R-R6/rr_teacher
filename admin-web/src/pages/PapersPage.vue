<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="试卷检索" eyebrow="Paper Trace">
      <div class="filters">
        <div class="field-group field-group--grow">
          <label class="field-label">关键词</label>
          <input v-model.trim="keyword" class="text-input" placeholder="试卷标题或副标题" />
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="loadPapers(1)">查询试卷</button>
          <button class="ghost-button" @click="resetFilters">重置</button>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="试卷列表" eyebrow="Paper Ledger">
      <ListStateSummary
        :title="resultMeta.totalLabel"
        :subtitle="`${resultMeta.rangeLabel} · ${resultMeta.filterLabel}`"
        :chips="activeFilterItems"
      />

      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>试卷</th>
              <th>作者</th>
              <th>题量</th>
              <th>时长 / 分值</th>
              <th>导出</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="paper in rows" :key="paper.id">
              <td>
                <strong>{{ paper.title }}</strong>
                <small>{{ paper.subtitle || '无副标题' }}</small>
              </td>
              <td>{{ paper.author_name || '未知' }}</td>
              <td>{{ paper.question_count }}</td>
              <td>{{ paper.exam_duration }} 分钟 / {{ paper.total_score }} 分</td>
              <td>
                <div class="tag-cloud">
                  <StatusPill :tone="paper.word_url ? 'success' : 'neutral'">试卷 {{ paper.word_url ? '已导出' : '未导出' }}</StatusPill>
                  <StatusPill :tone="paper.answer_word_url ? 'success' : 'neutral'">答案 {{ paper.answer_word_url ? '已导出' : '未导出' }}</StatusPill>
                </div>
              </td>
              <td>{{ formatDateTime(paper.created_at) }}</td>
              <td>
                <div class="table-actions">
                  <button @click="removePaper(paper)">删除</button>
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
        <span class="mono-chip">{{ loading ? '同步试卷结果中...' : `共 ${total} 条` }}</span>
        <div class="actions-row">
          <button class="ghost-button" :disabled="page <= 1" @click="loadPapers(page - 1)">上一页</button>
          <button class="ghost-button" :disabled="page * pageSize >= total" @click="loadPapers(page + 1)">下一页</button>
        </div>
      </div>
    </PanelCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import ListStateSummary from '@/components/ListStateSummary.vue'
import PanelCard from '@/components/PanelCard.vue'
import StatusPill from '@/components/StatusPill.vue'
import { buildEmptyState, buildResultMeta, describeActiveFilters } from '@/utils/list-state.js'
import { formatDateTime } from '@/utils/format.js'

const rows = ref([])
const keyword = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const feedback = ref('')
const feedbackTone = ref('success')
const loading = ref(false)

const activeFilterItems = computed(() =>
  describeActiveFilters(
    { keyword: keyword.value },
    {
      keyword: '关键词',
    }
  )
)

const resultMeta = computed(() =>
  buildResultMeta({
    total: total.value,
    page: page.value,
    pageSize,
    noun: '份试卷',
    activeFilterCount: activeFilterItems.value.length,
  })
)

const showEmptyState = computed(() => !loading.value && feedbackTone.value !== 'error' && rows.value.length === 0)

const emptyState = computed(() =>
  buildEmptyState({
    noun: '试卷',
    hasFilters: activeFilterItems.value.length > 0,
    defaultHint:
      activeFilterItems.value.length > 0
        ? '可以尝试缩短关键词，或改用标题中的核心词重新检索。'
        : '当前还没有试卷样本，可以先在小程序完成一次组卷。',
  })
)

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

function resetFilters() {
  keyword.value = ''
  loadPapers(1)
}

async function loadPapers(nextPage = page.value) {
  loading.value = true
  try {
    page.value = nextPage
    const data = await adminApi.listPapers({ page: page.value, page_size: pageSize, keyword: keyword.value })
    rows.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function removePaper(paper) {
  if (!window.confirm(`确定删除试卷「${paper.title}」吗？`)) return
  try {
    await adminApi.deletePaper(paper.id)
    applyFeedback('试卷已删除。')
    await loadPapers()
  } catch (error) {
    applyFeedback(error.message || '试卷删除失败。', 'error')
  }
}

onMounted(async () => {
  try {
    await loadPapers()
  } catch (error) {
    applyFeedback(error.message || '试卷列表加载失败。', 'error')
  }
})
</script>
