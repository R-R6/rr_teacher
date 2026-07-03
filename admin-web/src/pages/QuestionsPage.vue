<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="题目筛选" eyebrow="Query Plane">
      <div class="filters">
        <div class="field-group field-group--grow">
          <label class="field-label">关键词</label>
          <input v-model.trim="filters.keyword" class="text-input" placeholder="题干、答案、来源" />
        </div>
        <div class="field-group">
          <label class="field-label">题型</label>
          <select v-model="filters.question_type" class="select-input">
            <option value="">全部</option>
            <option value="choice">选择题</option>
            <option value="fill">填空题</option>
            <option value="experiment">实验题</option>
            <option value="calculation">计算题</option>
            <option value="short_answer">简答题</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">难度</label>
          <input v-model.number="filters.difficulty" class="text-input" type="number" min="1" max="20" />
        </div>
        <div class="field-group">
          <label class="field-label">作者关键词</label>
          <input v-model.trim="filters.author_keyword" class="text-input" placeholder="用户名或昵称" />
        </div>
        <div class="field-group">
          <label class="field-label">校对状态</label>
          <select v-model="filters.is_verified" class="select-input">
            <option value="">全部</option>
            <option value="true">已校对</option>
            <option value="false">未校对</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">标签</label>
          <select v-model="filters.tag_id" class="select-input">
            <option value="">全部</option>
            <option v-for="tag in allTags" :key="tag.id" :value="tag.id">{{ tag.name }}</option>
          </select>
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="loadQuestions(1)">查询</button>
          <button class="ghost-button" @click="resetFilters">重置</button>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="题库结果" eyebrow="Data Grid">
      <ListStateSummary
        :title="resultMeta.totalLabel"
        :subtitle="`${resultMeta.rangeLabel} · ${resultMeta.filterLabel}`"
        :chips="activeFilterItems"
      />

      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>题目</th>
              <th>题型</th>
              <th>作者</th>
              <th>难度</th>
              <th>状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>
                <strong>{{ truncate(row.content, 46) }}</strong>
                <small>{{ row.source || '未填写来源' }}</small>
              </td>
              <td>{{ questionTypeLabel(row.question_type) }}</td>
              <td>
                <strong>{{ row.author_name || '未知' }}</strong>
                <small>{{ row.author_id }}</small>
              </td>
              <td>{{ difficultyLabel(row.difficulty) }}</td>
              <td>
                <div class="tag-cloud">
                  <StatusPill :tone="row.is_verified ? 'success' : 'warning'">
                    {{ row.is_verified ? '已校对' : '未校对' }}
                  </StatusPill>
                  <StatusPill tone="neutral">附图 {{ row.image_count }}</StatusPill>
                </div>
              </td>
              <td>{{ formatDateTime(row.updated_at || row.created_at) }}</td>
              <td>
                <div class="table-actions">
                  <button @click="openQuestion(row)">查看</button>
                  <button @click="startEditing(row)">编辑</button>
                  <button @click="removeQuestion(row)">删除</button>
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
        <span class="mono-chip">{{ loading ? '同步题库结果中...' : `共 ${total} 条` }}</span>
        <div class="actions-row">
          <button class="ghost-button" :disabled="page <= 1" @click="loadQuestions(page - 1)">上一页</button>
          <button class="ghost-button" :disabled="page * pageSize >= total" @click="loadQuestions(page + 1)">下一页</button>
        </div>
      </div>
    </PanelCard>

    <DrawerPanel :open="drawerOpen" title="题目详情" eyebrow="Question Review" @close="closeDrawer">
      <div v-if="selectedQuestion" class="page-stack">
        <div class="actions-row" style="justify-content: space-between;">
          <div class="tag-cloud">
            <StatusPill :tone="selectedQuestion.is_verified ? 'success' : 'warning'">
              {{ selectedQuestion.is_verified ? '已校对' : '未校对' }}
            </StatusPill>
            <StatusPill tone="neutral">{{ questionTypeLabel(selectedQuestion.question_type) }}</StatusPill>
            <StatusPill tone="neutral">{{ difficultyLabel(selectedQuestion.difficulty) }}</StatusPill>
          </div>
          <button class="ghost-button" @click="editing = !editing">{{ editing ? '取消编辑' : '进入编辑' }}</button>
        </div>

        <template v-if="editing">
          <div class="field-group">
            <label class="field-label">题干</label>
            <textarea v-model="draft.content" class="text-area"></textarea>
          </div>
          <div class="two-column-form">
            <div class="field-group">
              <label class="field-label">题型</label>
              <select v-model="draft.question_type" class="select-input">
                <option value="choice">选择题</option>
                <option value="fill">填空题</option>
                <option value="experiment">实验题</option>
                <option value="calculation">计算题</option>
                <option value="short_answer">简答题</option>
              </select>
            </div>
            <div class="field-group">
              <label class="field-label">难度</label>
              <input v-model.number="draft.difficulty" class="text-input" type="number" min="1" max="20" />
            </div>
          </div>
          <div class="field-group">
            <label class="field-label">答案</label>
            <textarea v-model="draft.answer" class="text-area"></textarea>
          </div>
          <div class="field-group">
            <label class="field-label">解析</label>
            <textarea v-model="draft.analysis" class="text-area"></textarea>
          </div>
          <div class="field-group">
            <label class="field-label">来源</label>
            <input v-model="draft.source" class="text-input" />
          </div>
          <div class="inline-checkboxes">
            <label class="inline-checkbox">
              <input v-model="draft.is_verified" type="checkbox" />
              <span>标记为已校对</span>
            </label>
            <label class="inline-checkbox">
              <input v-model="draft.is_public" type="checkbox" />
              <span>允许公开给其他老师</span>
            </label>
          </div>
          <div class="field-group">
            <label class="field-label">标签</label>
            <div class="inline-checkboxes">
              <label v-for="tag in allTags" :key="tag.id" class="inline-checkbox">
                <input v-model="draft.tag_ids" :value="tag.id" type="checkbox" />
                <span>{{ tag.name }}</span>
              </label>
            </div>
          </div>
          <div class="actions-row">
            <button class="primary-button" @click="saveQuestion">保存修改</button>
          </div>
        </template>

        <template v-else>
          <img v-if="selectedQuestion.images?.[0]?.image_url" :src="selectedQuestion.images[0].image_url" alt="" class="hero-image" />
          <div class="copy-block">{{ selectedQuestion.content }}</div>
          <div class="summary-grid summary-grid--two">
            <div class="mini-card">
              <p class="field-label">答案</p>
              <div class="copy-block">{{ selectedQuestion.answer || '—' }}</div>
            </div>
            <div class="mini-card">
              <p class="field-label">解析</p>
              <div class="copy-block">{{ selectedQuestion.analysis || '—' }}</div>
            </div>
          </div>
          <div>
            <p class="field-label">标签</p>
            <div class="tag-cloud">
              <span v-for="tag in selectedQuestion.tags" :key="tag.id" class="tag-chip">{{ tag.name }}</span>
            </div>
          </div>
          <div v-if="selectedQuestion.images?.length" class="page-stack">
            <p class="field-label">附图</p>
            <div class="image-grid">
              <img v-for="image in selectedQuestion.images" :key="image.id" :src="image.image_url" alt="" />
            </div>
          </div>
        </template>
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
import { difficultyLabel, formatDateTime, questionTypeLabel, truncate, yesNoLabel } from '@/utils/format.js'

const filters = reactive({
  keyword: '',
  question_type: '',
  difficulty: '',
  author_keyword: '',
  is_verified: '',
  tag_id: '',
})

const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const drawerOpen = ref(false)
const selectedQuestion = ref(null)
const allTags = ref([])
const editing = ref(false)
const draft = reactive({
  content: '',
  answer: '',
  analysis: '',
  question_type: 'choice',
  difficulty: 3,
  source: '',
  is_verified: false,
  is_public: false,
  tag_ids: [],
})
const feedback = ref('')
const feedbackTone = ref('success')
const loading = ref(false)

const hasError = computed(() => feedbackTone.value === 'error' && Boolean(feedback.value))

const activeFilterItems = computed(() =>
  describeActiveFilters(filters, {
    keyword: '关键词',
    question_type: {
      label: '题型',
      format: questionTypeLabel,
    },
    difficulty: {
      label: '难度',
      format: difficultyLabel,
    },
    author_keyword: '作者',
    is_verified: {
      label: '校对',
      format: (value) => yesNoLabel(value, '已校对', '未校对'),
    },
    tag_id: {
      label: '标签',
      format: (value) => allTags.value.find((tag) => tag.id === value)?.name || String(value),
    },
  })
)

const resultMeta = computed(() =>
  buildResultMeta({
    total: total.value,
    page: page.value,
    pageSize,
    noun: '道题目',
    activeFilterCount: activeFilterItems.value.length,
  })
)

const emptyState = computed(() =>
  buildEmptyState({
    noun: '题目',
    hasFilters: activeFilterItems.value.length > 0,
    defaultHint:
      activeFilterItems.value.length > 0
        ? '可以尝试放宽关键词、题型或校对状态后重新查询。'
        : '题库为空时，可先从小程序 OCR 入库或创建联调数据。',
  })
)

const showEmptyState = computed(() => !loading.value && !hasError.value && rows.value.length === 0)

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

function resetFilters() {
  filters.keyword = ''
  filters.question_type = ''
  filters.difficulty = ''
  filters.author_keyword = ''
  filters.is_verified = ''
  filters.tag_id = ''
  loadQuestions(1)
}

function hydrateDraft(question) {
  draft.content = question.content || ''
  draft.answer = question.answer || ''
  draft.analysis = question.analysis || ''
  draft.question_type = question.question_type || 'choice'
  draft.difficulty = Number(question.difficulty || 3)
  draft.source = question.source || ''
  draft.is_verified = !!question.is_verified
  draft.is_public = !!question.is_public
  draft.tag_ids = (question.tags || []).map((tag) => tag.id)
}

async function loadTags() {
  const data = await adminApi.listTags({})
  allTags.value = Array.isArray(data) ? data : []
}

async function loadQuestions(nextPage = page.value) {
  loading.value = true
  try {
    page.value = nextPage
    const data = await adminApi.listQuestions({
      page: page.value,
      page_size: pageSize,
      keyword: filters.keyword,
      question_type: filters.question_type,
      difficulty: filters.difficulty || undefined,
      author_keyword: filters.author_keyword,
      is_verified: filters.is_verified === '' ? undefined : filters.is_verified,
      tag_id: filters.tag_id,
    })
    rows.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function openQuestion(row) {
  const detail = await adminApi.getQuestionDetail(row.id)
  selectedQuestion.value = detail
  hydrateDraft(detail)
  editing.value = false
  drawerOpen.value = true
}

async function startEditing(row) {
  await openQuestion(row)
  editing.value = true
}

function closeDrawer() {
  drawerOpen.value = false
  editing.value = false
}

async function saveQuestion() {
  try {
    await adminApi.updateQuestion(selectedQuestion.value.id, {
      content: draft.content,
      answer: draft.answer,
      analysis: draft.analysis,
      question_type: draft.question_type,
      difficulty: Number(draft.difficulty),
      source: draft.source,
      is_verified: draft.is_verified,
      is_public: draft.is_public,
      tag_ids: draft.tag_ids,
    })
    applyFeedback('题目更新成功。')
    await openQuestion({ id: selectedQuestion.value.id })
    await loadQuestions(page.value)
  } catch (error) {
    applyFeedback(error.message || '题目更新失败。', 'error')
  }
}

async function removeQuestion(row) {
  if (!window.confirm('确定删除这道题目吗？若仍被试卷或学生记录引用，后端会阻止删除。')) return
  try {
    await adminApi.deleteQuestion(row.id)
    applyFeedback('题目已删除。')
    await loadQuestions(page.value)
    if (selectedQuestion.value?.id === row.id) {
      closeDrawer()
    }
  } catch (error) {
    applyFeedback(error.message || '删除失败。', 'error')
  }
}

onMounted(async () => {
  try {
    await Promise.all([loadTags(), loadQuestions(1)])
  } catch (error) {
    applyFeedback(error.message || '题库加载失败。', 'error')
  }
})
</script>
