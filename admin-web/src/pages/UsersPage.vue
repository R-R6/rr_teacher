<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="用户筛选" eyebrow="Identity Ledger">
      <div class="filters">
        <div class="field-group field-group--grow">
          <label class="field-label">关键词</label>
          <input v-model.trim="filters.keyword" class="text-input" placeholder="用户名、昵称、学校、手机号" />
        </div>
        <div class="field-group">
          <label class="field-label">角色</label>
          <select v-model="filters.role" class="select-input">
            <option value="">全部</option>
            <option value="teacher">教师</option>
            <option value="student">学生</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">状态</label>
          <select v-model="filters.is_active" class="select-input">
            <option value="">全部</option>
            <option value="true">启用</option>
            <option value="false">禁用</option>
          </select>
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="loadUsers(1)">查询用户</button>
          <button class="ghost-button" @click="resetFilters">重置</button>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="用户列表" eyebrow="Identity Grid">
      <ListStateSummary
        :title="resultMeta.totalLabel"
        :subtitle="`${resultMeta.rangeLabel} · ${resultMeta.filterLabel}`"
        :chips="activeFilterItems"
      />

      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>角色</th>
              <th>学校</th>
              <th>内容产出</th>
              <th>状态</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in rows" :key="user.id">
              <td>
                <strong>{{ user.nickname || user.username }}</strong>
                <small>{{ user.username }}</small>
              </td>
              <td>{{ user.role }}</td>
              <td>{{ user.school || '未填写' }}</td>
              <td>
                <small>题目 {{ user.question_count }} / 试卷 {{ user.paper_count }} / OCR {{ user.ocr_count }}</small>
              </td>
              <td><StatusPill :tone="user.is_active ? 'success' : 'danger'">{{ user.is_active ? '启用' : '禁用' }}</StatusPill></td>
              <td>{{ formatDateTime(user.created_at) }}</td>
              <td>
                <div class="table-actions">
                  <button @click="openUser(user)">查看</button>
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
        <span class="mono-chip">{{ loading ? '同步用户结果中...' : `共 ${total} 条` }}</span>
        <div class="actions-row">
          <button class="ghost-button" :disabled="page <= 1" @click="loadUsers(page - 1)">上一页</button>
          <button class="ghost-button" :disabled="page * pageSize >= total" @click="loadUsers(page + 1)">下一页</button>
        </div>
      </div>
    </PanelCard>

    <DrawerPanel :open="drawerOpen" title="用户详情" eyebrow="Ownership Detail" @close="drawerOpen = false">
      <div v-if="selectedUser" class="page-stack">
        <div class="summary-grid summary-grid--two">
          <div class="mini-card">
            <p class="field-label">基础信息</p>
            <strong>{{ selectedUser.nickname || selectedUser.username }}</strong>
            <small>{{ selectedUser.role }} / {{ selectedUser.phone || '无手机号' }}</small>
          </div>
          <div class="mini-card">
            <p class="field-label">学校</p>
            <strong>{{ selectedUser.school || '未填写' }}</strong>
            <small>{{ selectedUser.is_active ? '账号启用中' : '账号已禁用' }}</small>
          </div>
        </div>

        <div class="summary-grid summary-grid--three">
          <div class="mini-card">
            <p class="field-label">题目数</p>
            <strong style="font-size: 28px;">{{ selectedUser.question_count }}</strong>
          </div>
          <div class="mini-card">
            <p class="field-label">试卷数</p>
            <strong style="font-size: 28px;">{{ selectedUser.paper_count }}</strong>
          </div>
          <div class="mini-card">
            <p class="field-label">OCR 次数</p>
            <strong style="font-size: 28px;">{{ selectedUser.ocr_count }}</strong>
          </div>
        </div>

        <div class="copy-block">
          用户 ID：{{ selectedUser.id }}
          <br />
          注册时间：{{ formatDateTime(selectedUser.created_at) }}
          <br />
          更新时间：{{ formatDateTime(selectedUser.updated_at) }}
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
import { formatDateTime, yesNoLabel } from '@/utils/format.js'

const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const drawerOpen = ref(false)
const selectedUser = ref(null)
const feedback = ref('')
const feedbackTone = ref('success')
const loading = ref(false)
const filters = reactive({
  keyword: '',
  role: '',
  is_active: '',
})

const activeFilterItems = computed(() =>
  describeActiveFilters(filters, {
    keyword: '关键词',
    role: '角色',
    is_active: {
      label: '状态',
      format: (value) => yesNoLabel(value, '启用', '禁用'),
    },
  })
)

const resultMeta = computed(() =>
  buildResultMeta({
    total: total.value,
    page: page.value,
    pageSize,
    noun: '位用户',
    activeFilterCount: activeFilterItems.value.length,
  })
)

const emptyState = computed(() =>
  buildEmptyState({
    noun: '用户',
    hasFilters: activeFilterItems.value.length > 0,
    defaultHint:
      activeFilterItems.value.length > 0
        ? '可以尝试放宽角色、状态或关键词条件。'
        : '当前还没有可见用户数据，请先准备联调账号或真实注册记录。',
  })
)

const showEmptyState = computed(() => !loading.value && feedbackTone.value !== 'error' && rows.value.length === 0)

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

function resetFilters() {
  filters.keyword = ''
  filters.role = ''
  filters.is_active = ''
  loadUsers(1)
}

async function loadUsers(nextPage = page.value) {
  loading.value = true
  try {
    page.value = nextPage
    const data = await adminApi.listUsers({
      page: page.value,
      page_size: pageSize,
      keyword: filters.keyword,
      role: filters.role,
      is_active: filters.is_active === '' ? undefined : filters.is_active,
    })
    rows.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function openUser(user) {
  selectedUser.value = await adminApi.getUserDetail(user.id)
  drawerOpen.value = true
}

onMounted(async () => {
  try {
    await loadUsers()
  } catch (error) {
    applyFeedback(error.message || '用户列表加载失败。', 'error')
  }
})
</script>
