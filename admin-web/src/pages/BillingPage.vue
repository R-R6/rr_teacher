<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <section class="metric-strip">
      <MetricCard label="免费已确认" :value="summary.free_used" caption="前 10 名免费种子名额" />
      <MetricCard label="9.9 待支付" :value="summary.paid_locked" caption="已锁定但未完成支付" />
      <MetricCard label="9.9 已支付" :value="summary.paid_paid" caption="已转化为终身权益" />
      <MetricCard label="剩余名额" :value="remainingSlots" caption="免费与付费名额合计剩余" />
    </section>

    <PanelCard title="种子计划摘要" eyebrow="Seed Offer">
      <div class="summary-grid summary-grid--three">
        <div class="mini-card">
          <p class="field-label">活动</p>
          <strong>{{ offer.name || '种子计划' }}</strong>
          <small>{{ offer.code || 'seed_2026_round_1' }}</small>
        </div>
        <div class="mini-card">
          <p class="field-label">状态</p>
          <StatusPill :tone="offer.status === 'active' ? 'success' : 'neutral'">{{ offer.status || 'pending' }}</StatusPill>
        </div>
        <div class="mini-card">
          <p class="field-label">价格</p>
          <strong>{{ formatMoney(offer.amount_cents) }}</strong>
          <small>{{ offer.currency || 'CNY' }} / 支付窗口 {{ offer.payment_window_minutes || 30 }} 分钟</small>
        </div>
      </div>

      <div class="actions-row">
        <button :class="activeTab === 'eligibilities' ? 'primary-button' : 'ghost-button'" @click="switchTab('eligibilities')">资格</button>
        <button :class="activeTab === 'orders' ? 'primary-button' : 'ghost-button'" @click="switchTab('orders')">订单</button>
        <button :class="activeTab === 'entitlements' ? 'primary-button' : 'ghost-button'" @click="switchTab('entitlements')">权益</button>
        <button class="ghost-button" @click="refreshCurrentTab">刷新</button>
      </div>
    </PanelCard>

    <PanelCard v-if="activeTab === 'eligibilities'" title="种子资格" eyebrow="Eligibility Ledger">
      <div class="filters">
        <div class="field-group">
          <label class="field-label">状态</label>
          <select v-model="eligibilityFilters.status" class="select-input" @change="loadEligibilities(1)">
            <option value="">全部</option>
            <option value="locked">待支付</option>
            <option value="converted">已转化</option>
            <option value="expired">已释放</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
      </div>
      <ListStateSummary
        :title="`共 ${eligibilities.total} 条资格`"
        :subtitle="`第 ${eligibilities.page} 页 / 每页 ${pageSize} 条`"
        :chips="eligibilityFilters.status ? [`状态：${eligibilityFilters.status}`] : []"
      />
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>类型</th>
              <th>状态</th>
              <th>槽位</th>
              <th>过期时间</th>
              <th>转化时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in eligibilities.items" :key="item.id">
              <td>
                <strong>{{ item.nickname || item.username || item.user_id }}</strong>
                <small>{{ item.user_id }}</small>
              </td>
              <td>{{ eligibilityTypeLabel(item.type) }}</td>
              <td><StatusPill :tone="statusTone(item.status)">{{ eligibilityStatusLabel(item.status) }}</StatusPill></td>
              <td>{{ item.slot_no || '-' }}</td>
              <td>{{ formatDateTime(item.expires_at) }}</td>
              <td>{{ formatDateTime(item.converted_at) }}</td>
              <td>
                <div class="table-actions">
                  <button :disabled="item.status !== 'locked'" @click="releaseEligibility(item)">释放资格</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationControls :page="eligibilities.page" :page-size="pageSize" :total="eligibilities.total" @prev="loadEligibilities(eligibilities.page - 1)" @next="loadEligibilities(eligibilities.page + 1)" />
    </PanelCard>

    <PanelCard v-if="activeTab === 'orders'" title="支付订单" eyebrow="Order Ledger">
      <div class="filters">
        <div class="field-group">
          <label class="field-label">状态</label>
          <select v-model="orderFilters.status" class="select-input" @change="loadOrders(1)">
            <option value="">全部</option>
            <option value="pending">待支付</option>
            <option value="paid">已支付</option>
            <option value="closed">已关闭</option>
            <option value="expired">已过期</option>
            <option value="refunded">已退款</option>
          </select>
        </div>
      </div>
      <ListStateSummary
        :title="`共 ${orders.total} 条订单`"
        :subtitle="`第 ${orders.page} 页 / 每页 ${pageSize} 条`"
        :chips="orderFilters.status ? [`状态：${orderFilters.status}`] : []"
      />
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>订单</th>
              <th>用户</th>
              <th>商品</th>
              <th>状态</th>
              <th>金额</th>
              <th>交易号</th>
              <th>支付时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in orders.items" :key="item.id">
              <td>
                <strong>{{ item.order_no }}</strong>
                <small>{{ item.id }}</small>
              </td>
              <td>
                <strong>{{ item.nickname || item.username || item.user_id }}</strong>
                <small>{{ item.user_id }}</small>
              </td>
              <td>
                <strong>{{ item.product_type }}</strong>
                <small>{{ item.channel }}</small>
              </td>
              <td><StatusPill :tone="statusTone(item.status)">{{ orderStatusLabel(item.status) }}</StatusPill></td>
              <td>{{ formatMoney(item.amount_total) }}</td>
              <td><small>{{ item.transaction_id || '-' }}</small></td>
              <td>{{ formatDateTime(item.paid_at || item.expires_at) }}</td>
              <td>
                <div class="table-actions">
                  <button :disabled="item.status !== 'pending'" @click="closeOrder(item)">关闭订单</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationControls :page="orders.page" :page-size="pageSize" :total="orders.total" @prev="loadOrders(orders.page - 1)" @next="loadOrders(orders.page + 1)" />
    </PanelCard>

    <PanelCard v-if="activeTab === 'entitlements'" title="终身权益" eyebrow="Entitlement Ledger">
      <div class="mini-card">
        <div class="two-column-form">
          <div class="field-group">
            <label class="field-label">用户 ID</label>
            <input v-model.trim="grantForm.user_id" class="text-input" placeholder="输入要发放权益的用户 ID" />
          </div>
          <div class="field-group">
            <label class="field-label">来源</label>
            <select v-model="grantForm.source" class="select-input">
              <option value="manual_grant">后台手动发放</option>
              <option value="seed_free">种子免费</option>
              <option value="seed_paid">种子付费</option>
            </select>
          </div>
        </div>
        <div class="field-group" style="margin-top: 14px;">
          <label class="field-label">备注</label>
          <textarea v-model.trim="grantForm.notes" class="text-area" placeholder="记录人工发放原因"></textarea>
        </div>
        <div class="actions-row" style="justify-content: flex-end; margin-top: 14px;">
          <button class="primary-button" :disabled="granting" @click="grantEntitlement">{{ granting ? '发放中...' : '发放终身权益' }}</button>
        </div>
      </div>

      <div class="filters">
        <div class="field-group">
          <label class="field-label">状态</label>
          <select v-model="entitlementFilters.status" class="select-input" @change="loadEntitlements(1)">
            <option value="">全部</option>
            <option value="active">已生效</option>
            <option value="revoked">已撤销</option>
          </select>
        </div>
      </div>
      <ListStateSummary
        :title="`共 ${entitlements.total} 条权益`"
        :subtitle="`第 ${entitlements.page} 页 / 每页 ${pageSize} 条`"
        :chips="entitlementFilters.status ? [`状态：${entitlementFilters.status}`] : []"
      />
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>权益</th>
              <th>状态</th>
              <th>来源</th>
              <th>订单</th>
              <th>开始时间</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in entitlements.items" :key="item.id">
              <td>
                <strong>{{ item.nickname || item.username || item.user_id }}</strong>
                <small>{{ item.user_id }}</small>
              </td>
              <td>{{ item.type }}</td>
              <td><StatusPill :tone="item.active ? 'success' : statusTone(item.status)">{{ item.active ? '生效中' : item.status }}</StatusPill></td>
              <td>{{ sourceLabel(item.source) }}</td>
              <td><small>{{ item.order_id || '-' }}</small></td>
              <td>{{ formatDateTime(item.starts_at) }}</td>
              <td>{{ formatDateTime(item.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationControls :page="entitlements.page" :page-size="pageSize" :total="entitlements.total" @prev="loadEntitlements(entitlements.page - 1)" @next="loadEntitlements(entitlements.page + 1)" />
    </PanelCard>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import ListStateSummary from '@/components/ListStateSummary.vue'
import MetricCard from '@/components/MetricCard.vue'
import PanelCard from '@/components/PanelCard.vue'
import StatusPill from '@/components/StatusPill.vue'
import { formatDateTime } from '@/utils/format.js'

const pageSize = 20
const feedback = ref('')
const feedbackTone = ref('success')
const activeTab = ref('eligibilities')
const loading = ref(false)
const granting = ref(false)

const offer = reactive({})
const summary = reactive({
  free_used: 0,
  paid_locked: 0,
  paid_paid: 0,
  paid_expired: 0,
})
const eligibilities = reactive({ total: 0, page: 1, items: [] })
const orders = reactive({ total: 0, page: 1, items: [] })
const entitlements = reactive({ total: 0, page: 1, items: [] })
const eligibilityFilters = reactive({ status: '' })
const orderFilters = reactive({ status: '' })
const entitlementFilters = reactive({ status: '' })
const grantForm = reactive({
  user_id: '',
  source: 'manual_grant',
  notes: '',
})

const remainingSlots = computed(() => {
  const freeLeft = Math.max(Number(offer.free_total || 0) - Number(summary.free_used || 0), 0)
  const paidLeft = Math.max(Number(offer.paid_total || 0) - Number(summary.paid_locked || 0) - Number(summary.paid_paid || 0), 0)
  return freeLeft + paidLeft
})

const PaginationControls = defineComponent({
  props: {
    page: { type: Number, required: true },
    pageSize: { type: Number, required: true },
    total: { type: Number, required: true },
  },
  emits: ['prev', 'next'],
  setup(props, { emit }) {
    return () => h('div', { class: 'actions-row', style: 'justify-content: space-between; margin-top: 18px;' }, [
      h('span', { class: 'mono-chip' }, `共 ${props.total} 条`),
      h('div', { class: 'actions-row' }, [
        h('button', { class: 'ghost-button', disabled: props.page <= 1, onClick: () => emit('prev') }, '上一页'),
        h('button', { class: 'ghost-button', disabled: props.page * props.pageSize >= props.total, onClick: () => emit('next') }, '下一页'),
      ]),
    ])
  },
})

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

function formatMoney(cents) {
  const amount = Number(cents || 0) / 100
  return `¥${amount.toFixed(amount % 1 === 0 ? 0 : 2)}`
}

function statusTone(status) {
  if (['active', 'converted', 'paid'].includes(status)) return 'success'
  if (['locked', 'pending'].includes(status)) return 'warning'
  if (['expired', 'closed', 'cancelled', 'refunded', 'revoked'].includes(status)) return 'neutral'
  return 'neutral'
}

function eligibilityTypeLabel(type) {
  return {
    free_seed: '免费种子',
    paid_seed_9_9: '9.9 种子',
  }[type] || type || '-'
}

function eligibilityStatusLabel(status) {
  return {
    locked: '待支付',
    converted: '已转化',
    expired: '已释放',
    cancelled: '已取消',
  }[status] || status || '-'
}

function orderStatusLabel(status) {
  return {
    pending: '待支付',
    paid: '已支付',
    closed: '已关闭',
    expired: '已过期',
    refunded: '已退款',
  }[status] || status || '-'
}

function sourceLabel(source) {
  return {
    seed_free: '种子免费',
    seed_paid: '种子付费',
    manual_grant: '后台手动',
  }[source] || source || '-'
}

function applyList(target, data = {}) {
  target.total = data.total || 0
  target.page = data.page || 1
  target.items = data.items || []
}

async function loadSummary() {
  const data = await adminApi.getBillingSeedSummary()
  Object.assign(offer, data.offer || {})
  Object.assign(summary, data.summary || {})
}

async function loadEligibilities(nextPage = eligibilities.page) {
  const data = await adminApi.listBillingEligibilities({
    page: nextPage,
    page_size: pageSize,
    status: eligibilityFilters.status,
  })
  applyList(eligibilities, data)
}

async function loadOrders(nextPage = orders.page) {
  const data = await adminApi.listBillingOrders({
    page: nextPage,
    page_size: pageSize,
    status: orderFilters.status,
  })
  applyList(orders, data)
}

async function loadEntitlements(nextPage = entitlements.page) {
  const data = await adminApi.listBillingEntitlements({
    page: nextPage,
    page_size: pageSize,
    status: entitlementFilters.status,
  })
  applyList(entitlements, data)
}

async function refreshCurrentTab() {
  loading.value = true
  try {
    await loadSummary()
    if (activeTab.value === 'eligibilities') await loadEligibilities()
    if (activeTab.value === 'orders') await loadOrders()
    if (activeTab.value === 'entitlements') await loadEntitlements()
  } catch (error) {
    applyFeedback(error.message || '计费数据加载失败。', 'error')
  } finally {
    loading.value = false
  }
}

async function switchTab(tab) {
  activeTab.value = tab
  await refreshCurrentTab()
}

async function closeOrder(order) {
  if (!window.confirm(`确认关闭订单 ${order.order_no}？`)) return
  try {
    await adminApi.closeBillingOrder(order.id)
    applyFeedback('订单已关闭。')
    await refreshCurrentTab()
  } catch (error) {
    applyFeedback(error.message || '关闭订单失败。', 'error')
  }
}

async function releaseEligibility(item) {
  if (!window.confirm(`确认释放第 ${item.slot_no || '-'} 个种子资格？`)) return
  try {
    await adminApi.releaseBillingEligibility(item.id)
    applyFeedback('资格已释放。')
    await refreshCurrentTab()
  } catch (error) {
    applyFeedback(error.message || '释放资格失败。', 'error')
  }
}

async function grantEntitlement() {
  if (!grantForm.user_id) {
    applyFeedback('请先填写用户 ID。', 'error')
    return
  }
  granting.value = true
  try {
    await adminApi.grantBillingEntitlement({
      user_id: grantForm.user_id,
      source: grantForm.source,
      notes: grantForm.notes || undefined,
    })
    grantForm.user_id = ''
    grantForm.notes = ''
    applyFeedback('终身权益已发放。')
    await loadSummary()
    await loadEntitlements(1)
  } catch (error) {
    applyFeedback(error.message || '权益发放失败。', 'error')
  } finally {
    granting.value = false
  }
}

onMounted(refreshCurrentTab)
</script>
