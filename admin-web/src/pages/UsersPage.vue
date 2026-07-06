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

        <div>
          <p class="field-label">Quota Profile</p>
          <h3 style="margin: 4px 0 0;">套餐与 OCR 用量</h3>
        </div>

        <div class="summary-grid summary-grid--three">
          <div class="mini-card">
            <p class="field-label">当前套餐</p>
            <strong>{{ activeQuotaProfile.plan_name }}</strong>
            <small>{{ activeQuotaProfile.plan_code }}</small>
          </div>
          <div class="mini-card">
            <p class="field-label">每日额度</p>
            <strong style="font-size: 28px;">{{ formatLimit(activeQuotaProfile.effective_daily_ocr_limit) }}</strong>
            <small>高成本 OCR 引擎</small>
          </div>
          <div class="mini-card">
            <p class="field-label">月度额度</p>
            <strong style="font-size: 28px;">{{ formatLimit(activeQuotaProfile.effective_monthly_ocr_limit) }}</strong>
            <small>留空或 0 表示不限</small>
          </div>
        </div>

        <div v-if="userUsage.paid_engine_status.length" class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th>付费引擎</th>
                <th>今日使用</th>
                <th>今日剩余</th>
                <th>本月使用</th>
                <th>全局剩余</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="engine in userUsage.paid_engine_status" :key="engine.engine">
                <td>{{ engine.engine }}</td>
                <td>{{ engine.used }}</td>
                <td>{{ formatRemaining(engine.remaining) }}</td>
                <td>{{ engine.monthly_used }}</td>
                <td>{{ formatRemaining(engine.global_remaining) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mini-card">
          <div class="two-column-form">
            <div class="field-group">
              <label class="field-label">套餐</label>
              <select v-model="quotaForm.plan_code" class="select-input">
                <option v-for="plan in planOptions" :key="plan.code" :value="plan.code">{{ plan.label }}</option>
              </select>
            </div>
            <div class="field-group">
              <label class="field-label">展示名称</label>
              <input v-model.trim="quotaForm.plan_name" class="text-input" placeholder="例如：种子免费终身" />
            </div>
            <div class="field-group">
              <label class="field-label">每日 OCR 限额</label>
              <input v-model="quotaForm.daily_ocr_limit" class="text-input" type="number" min="0" placeholder="留空使用默认值" />
            </div>
            <div class="field-group">
              <label class="field-label">每月 OCR 限额</label>
              <input v-model="quotaForm.monthly_ocr_limit" class="text-input" type="number" min="0" placeholder="留空表示不限" />
            </div>
            <div class="field-group">
              <label class="field-label">状态</label>
              <select v-model="quotaForm.status" class="select-input">
                <option value="active">启用</option>
                <option value="paused">暂停</option>
                <option value="expired">过期</option>
              </select>
            </div>
            <div class="field-group">
              <label class="field-label">来源</label>
              <select v-model="quotaForm.source" class="select-input">
                <option value="manual">后台配置</option>
                <option value="seed">种子用户</option>
                <option value="payment">支付开通</option>
              </select>
            </div>
          </div>
          <div class="field-group" style="margin-top: 14px;">
            <label class="field-label">备注</label>
            <textarea v-model.trim="quotaForm.notes" class="text-area" placeholder="记录人工调整原因、种子用户来源或后续支付备注"></textarea>
          </div>
          <div class="actions-row" style="justify-content: flex-end; margin-top: 14px;">
            <button class="primary-button" :disabled="quotaSaving" @click="saveQuotaProfile">
              {{ quotaSaving ? '保存中...' : '保存套餐与限额' }}
            </button>
          </div>
        </div>

        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th>引擎</th>
                <th>日期</th>
                <th>状态</th>
                <th>失败原因</th>
                <th>记录时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in userUsage.usage_logs" :key="log.id">
                <td>{{ log.engine }}</td>
                <td>{{ log.usage_day }}</td>
                <td><StatusPill :tone="usageStatusTone(log.status)">{{ usageStatusLabel(log.status) }}</StatusPill></td>
                <td><small>{{ log.error_message || '无' }}</small></td>
                <td>{{ formatDateTime(log.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!usageLoading && userUsage.usage_logs.length === 0" class="empty-panel">
          <strong>暂无高成本 OCR 调用记录</strong>
          <p>该用户在当前统计窗口内还没有触发付费 OCR 引擎。</p>
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
const usageLoading = ref(false)
const quotaSaving = ref(false)
const filters = reactive({
  keyword: '',
  role: '',
  is_active: '',
})
const userUsage = reactive({
  usage_logs: [],
  paid_engine_status: [],
  recent_ocr_records: [],
  quota_profile: null,
})
const quotaForm = reactive({
  plan_code: 'default',
  plan_name: '',
  daily_ocr_limit: '',
  monthly_ocr_limit: '',
  status: 'active',
  source: 'manual',
  notes: '',
})
const planOptions = [
  { code: 'default', label: '默认套餐' },
  { code: 'free_seed', label: '种子免费终身' },
  { code: 'seed_lifetime_9_9', label: '9.9 种子终身' },
  { code: 'manual_trial', label: '人工试用' },
  { code: 'standard', label: '标准套餐' },
  { code: 'custom', label: '自定义套餐' },
]

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
const activeQuotaProfile = computed(() => userUsage.quota_profile || selectedUser.value?.quota_profile || {
  plan_code: 'default',
  plan_name: '默认套餐',
  effective_daily_ocr_limit: 0,
  effective_monthly_ocr_limit: 0,
})

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

function formatLimit(value) {
  const numeric = Number(value || 0)
  return numeric > 0 ? `${numeric} 次` : '不限'
}

function formatRemaining(value) {
  if (value === null || value === undefined) return '不限'
  return `${value} 次`
}

function usageStatusLabel(status) {
  return {
    reserved: '已预约',
    completed: '成功',
    failed: '失败',
    cancelled: '取消',
  }[status] || status || '未知'
}

function usageStatusTone(status) {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'cancelled') return 'neutral'
  return 'warning'
}

function fillQuotaForm(profile = {}) {
  quotaForm.plan_code = profile.plan_code || 'default'
  quotaForm.plan_name = profile.plan_name || ''
  quotaForm.daily_ocr_limit = profile.daily_ocr_limit ?? ''
  quotaForm.monthly_ocr_limit = profile.monthly_ocr_limit ?? ''
  quotaForm.status = profile.status || 'active'
  quotaForm.source = profile.source === 'environment_default' ? 'manual' : (profile.source || 'manual')
  quotaForm.notes = profile.notes || ''
}

function normalizeLimit(value) {
  if (value === '' || value === null || value === undefined) return null
  return Number(value)
}

async function loadUserUsage() {
  if (!selectedUser.value?.id) return
  usageLoading.value = true
  try {
    const data = await adminApi.getUserOcrUsage(selectedUser.value.id, { days: 7, page_size: 10 })
    userUsage.usage_logs = data.usage_logs || []
    userUsage.paid_engine_status = data.paid_engine_status || []
    userUsage.recent_ocr_records = data.recent_ocr_records || []
    userUsage.quota_profile = data.quota_profile || null
    fillQuotaForm(userUsage.quota_profile || selectedUser.value.quota_profile || {})
  } catch (error) {
    applyFeedback(error.message || '用户 OCR 用量加载失败。', 'error')
  } finally {
    usageLoading.value = false
  }
}

async function saveQuotaProfile() {
  if (!selectedUser.value?.id) return
  quotaSaving.value = true
  try {
    const updatedProfile = await adminApi.updateUserQuotaProfile(selectedUser.value.id, {
      plan_code: quotaForm.plan_code,
      plan_name: quotaForm.plan_name || undefined,
      daily_ocr_limit: normalizeLimit(quotaForm.daily_ocr_limit),
      monthly_ocr_limit: normalizeLimit(quotaForm.monthly_ocr_limit),
      status: quotaForm.status,
      source: quotaForm.source,
      notes: quotaForm.notes || undefined,
    })
    selectedUser.value.quota_profile = updatedProfile
    userUsage.quota_profile = updatedProfile
    fillQuotaForm(updatedProfile)
    applyFeedback('用户套餐与 OCR 限额已更新。')
    await loadUserUsage()
  } catch (error) {
    applyFeedback(error.message || '套餐与限额保存失败。', 'error')
  } finally {
    quotaSaving.value = false
  }
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
  fillQuotaForm(selectedUser.value.quota_profile || {})
  drawerOpen.value = true
  await loadUserUsage()
}

onMounted(async () => {
  try {
    await loadUsers()
  } catch (error) {
    applyFeedback(error.message || '用户列表加载失败。', 'error')
  }
})
</script>
