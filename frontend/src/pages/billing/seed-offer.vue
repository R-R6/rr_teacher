<template>
  <view class="seed-page">
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <view class="nav-back" @tap="goBack">‹</view>
        <text class="nav-title">种子计划</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <view class="hero-section">
        <view class="hero-topline">
          <text class="hero-kicker">首批老师专属</text>
          <text class="hero-status" :class="statusTone">{{ statusText }}</text>
        </view>
        <text class="hero-title">终身权益种子名额</text>
        <text class="hero-subtitle">前 10 名免费开通，第 11-50 名享 9.9 元终身资格。</text>

        <view class="price-row">
          <view class="price-main">
            <text class="price-symbol">¥</text>
            <text class="price-number">9.9</text>
            <text class="price-tail">终身</text>
          </view>
          <view class="price-note">
            <text>名额以成功领取资格为准</text>
            <text>未支付资格 {{ offer.payment_window_minutes }} 分钟后释放</text>
          </view>
        </view>
      </view>

      <view class="quota-strip">
        <view class="quota-item">
          <text class="quota-num">{{ freeLeft }}</text>
          <text class="quota-label">免费剩余</text>
        </view>
        <view class="quota-divider"></view>
        <view class="quota-item">
          <text class="quota-num">{{ paidLeft }}</text>
          <text class="quota-label">9.9 剩余</text>
        </view>
        <view class="quota-divider"></view>
        <view class="quota-item">
          <text class="quota-num">{{ paidConfirmed }}</text>
          <text class="quota-label">已确认</text>
        </view>
      </view>

      <view class="state-card" :class="statusTone">
        <view class="state-mark"></view>
        <view class="state-copy">
          <text class="state-title">{{ stateTitle }}</text>
          <text class="state-desc">{{ stateDesc }}</text>
          <text v-if="expiresAtText" class="state-time">支付保留至 {{ expiresAtText }}</text>
        </view>
      </view>

      <view class="rules-panel">
        <text class="section-title">活动规则</text>
        <view class="rule-row">
          <text class="rule-index">01</text>
          <view class="rule-copy">
            <text class="rule-title">先领资格，再判定名额</text>
            <text class="rule-desc">不按注册时间占坑，只有点击领取成功才会进入本轮排序。</text>
          </view>
        </view>
        <view class="rule-row">
          <text class="rule-index">02</text>
          <view class="rule-copy">
            <text class="rule-title">免费用户不进入支付</text>
            <text class="rule-desc">拿到前 10 名资格后，系统直接开通同一类终身权益。</text>
          </view>
        </view>
        <view class="rule-row">
          <text class="rule-index">03</text>
          <view class="rule-copy">
            <text class="rule-title">支付后仍以后端确认为准</text>
            <text class="rule-desc">微信支付完成后会回查订单状态，确认后再展示权益结果。</text>
          </view>
        </view>
      </view>

      <view class="rights-panel">
        <text class="section-title">终身权益包含</text>
        <view class="rights-grid">
          <view class="right-item">
            <text class="right-dot"></text>
            <text class="right-text">拍题识别与人工校对</text>
          </view>
          <view class="right-item">
            <text class="right-dot"></text>
            <text class="right-text">题库管理与错题沉淀</text>
          </view>
          <view class="right-item">
            <text class="right-dot"></text>
            <text class="right-text">智能组卷与 Word 导出</text>
          </view>
          <view class="right-item">
            <text class="right-dot"></text>
            <text class="right-text">后续基础功能升级</text>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <view class="bottom-action">
      <button class="primary-btn" :class="{ disabled: actionDisabled }" :disabled="actionDisabled" @tap="handlePrimaryAction">
        <text>{{ actionText }}</text>
      </button>
      <text class="action-hint">{{ actionHint }}</text>
    </view>
  </view>
</template>

<script>
import { billingAPI } from '../../utils/api.js'
import { isPaymentConfirmed, payWithWechatAndConfirm } from '../../utils/wechat-payment.js'

const DEFAULT_OFFER = {
  free_total: 10,
  paid_total: 40,
  payment_window_minutes: 30,
  status: 'pending',
}

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      loading: true,
      submitting: false,
      loadFailed: false,
      offer: { ...DEFAULT_OFFER },
      summary: {
        free_used: 0,
        paid_locked: 0,
        paid_paid: 0,
        paid_expired: 0,
      },
      eligibility: null,
      entitlement: null,
      currentOrder: null,
    }
  },
  computed: {
    hasEntitlement() {
      return this.entitlement?.status === 'active' || this.entitlement?.active === true
    },
    freeLeft() {
      return Math.max((this.offer.free_total || 0) - (this.summary.free_used || 0), 0)
    },
    paidLeft() {
      const locked = this.summary.paid_locked || 0
      const paid = this.summary.paid_paid || 0
      return Math.max((this.offer.paid_total || 0) - locked - paid, 0)
    },
    paidConfirmed() {
      return this.summary.paid_paid || 0
    },
    isPaidEligibility() {
      return this.eligibility?.type === 'paid_seed_9_9'
    },
    isActivityEnded() {
      return this.offer.status === 'ended' || (!this.freeLeft && !this.paidLeft && !this.eligibility && !this.hasEntitlement)
    },
    statusTone() {
      if (this.loadFailed) return 'muted'
      if (this.hasEntitlement) return 'success'
      if (this.isPaidEligibility) return 'warning'
      if (this.isActivityEnded) return 'danger'
      return 'active'
    },
    statusText() {
      if (this.loading) return '读取中'
      if (this.loadFailed) return '待开放'
      if (this.hasEntitlement) return '已开通'
      if (this.isPaidEligibility) return '待支付'
      if (this.isActivityEnded) return '已结束'
      return '可领取'
    },
    stateTitle() {
      if (this.loadFailed) return '服务暂未开放'
      if (this.hasEntitlement) return '终身权益已开通'
      if (this.eligibility?.type === 'free_seed') return '你已拿到免费资格'
      if (this.isPaidEligibility) return '你已锁定 9.9 元资格'
      if (this.isActivityEnded) return '本轮名额已结束'
      return '现在可以领取资格'
    },
    stateDesc() {
      if (this.loadFailed) return '购买入口已准备好，等待后端计费接口上线后即可领取和支付。'
      if (this.hasEntitlement) return '权益状态来自服务端结果，后续无需重复领取。'
      if (this.eligibility?.type === 'free_seed') return '免费资格会由服务端直接转换为终身权益。'
      if (this.isPaidEligibility) return '请在保留时间内完成微信支付，支付后系统会再次确认订单状态。'
      if (this.isActivityEnded) return '前 50 名种子资格已发放完毕，感谢关注。'
      return '点击后系统会按当前成功领取顺序判定免费或 9.9 元资格。'
    },
    expiresAtText() {
      const value = this.eligibility?.expires_at || this.currentOrder?.expires_at
      if (!value) return ''
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return ''
      const month = date.getMonth() + 1
      const day = date.getDate()
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${month}月${day}日 ${hours}:${minutes}`
    },
    actionText() {
      if (this.submitting) return '处理中...'
      if (this.loadFailed) return '服务暂未开放'
      if (this.hasEntitlement) return '已拥有终身权益'
      if (this.isActivityEnded) return '本轮活动已结束'
      if (this.isPaidEligibility) return '微信支付 9.9 元'
      return '领取种子资格'
    },
    actionHint() {
      if (this.isPaidEligibility) return '支付完成，正在确认权益；最终状态以后端订单为准'
      if (this.hasEntitlement) return '感谢成为首批体验老师'
      return '首期仅支持微信小程序内微信支付'
    },
    actionDisabled() {
      return this.submitting || this.loadFailed || this.hasEntitlement || this.isActivityEnded
    },
  },
  onLoad() {
    try {
      const sysInfo = uni.getSystemInfoSync()
      this.statusBarHeight = sysInfo.statusBarHeight || 20
    } catch (e) {
      this.statusBarHeight = 20
    }
    this.navHeight = this.statusBarHeight + 44
  },
  onShow() {
    this.loadSeedOffer()
  },
  methods: {
    goBack() {
      uni.navigateBack({
        fail: () => uni.switchTab({ url: '/pages/profile/profile' }),
      })
    },
    normalizeSeedOffer(data = {}) {
      const offer = data.offer || data
      const summary = data.summary || offer.summary || {}
      const entitlements = data.entitlements || []

      this.offer = {
        ...DEFAULT_OFFER,
        ...offer,
      }
      this.summary = {
        free_used: summary.free_used || 0,
        paid_locked: summary.paid_locked || 0,
        paid_paid: summary.paid_paid || 0,
        paid_expired: summary.paid_expired || 0,
      }
      this.eligibility = data.eligibility || offer.eligibility || null
      this.currentOrder = data.order || data.current_order || offer.order || null
      this.entitlement = data.entitlement || entitlements.find((item) => item.type === 'lifetime_access' && item.status === 'active') || null
    },
    async loadSeedOffer() {
      this.loading = true
      try {
        const data = await billingAPI.getSeedOffer()
        this.normalizeSeedOffer(data || {})
        this.loadFailed = false
      } catch (error) {
        this.loadFailed = true
      } finally {
        this.loading = false
      }
    },
    async handlePrimaryAction() {
      if (this.actionDisabled) return
      if (this.isPaidEligibility) {
        await this.startWechatPay(this.currentOrder)
      } else {
        await this.claimSeedOffer()
      }
    },
    async claimSeedOffer() {
      this.submitting = true
      uni.showLoading({ title: '领取中...' })
      try {
        const result = await billingAPI.claimSeedOffer()
        this.normalizeSeedOffer(result || {})
        uni.hideLoading()

        const order = result?.order || result?.current_order || null
        if (result?.eligibility?.type === 'paid_seed_9_9' || order) {
          await this.startWechatPay(order)
        } else {
          uni.showToast({ title: '资格已确认', icon: 'success' })
          await this.loadSeedOffer()
        }
      } catch (error) {
        uni.hideLoading()
        uni.showToast({ title: error?.message || '领取失败', icon: 'none' })
      } finally {
        this.submitting = false
      }
    },
    async startWechatPay(existingOrder) {
      this.submitting = true
      uni.showLoading({ title: '准备支付...' })
      try {
        const order = existingOrder || await billingAPI.createOrder({
          product_type: 'seed_paid_lifetime',
          channel: 'wechat_miniapp',
        })
        const orderId = order?.id || order?.order_id
        const paymentParams = order?.payment_params || order?.payment?.params || order?.wechat_payment

        uni.hideLoading()
        const confirmed = await payWithWechatAndConfirm({
          orderId,
          paymentParams,
          confirmOrder: (id) => billingAPI.getOrder(id),
        })

        this.currentOrder = confirmed
        await this.loadSeedOffer()
        if (isPaymentConfirmed(confirmed, this.entitlement)) {
          uni.showToast({ title: '订单已确认', icon: 'success' })
        } else {
          uni.showToast({ title: '支付结果等待确认', icon: 'none' })
        }
      } catch (error) {
        uni.hideLoading()
        const message = String(error?.errMsg || error?.message || '')
        const isCancel = message.includes('cancel') || message.includes('取消')
        uni.showToast({ title: isCancel ? '已取消支付' : '支付未完成', icon: 'none' })
        await this.loadSeedOffer()
      } finally {
        this.submitting = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.seed-page {
  min-height: 100vh;
  background: #F5F6FA;
}
.nav-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: #FFFFFF;
  box-shadow: 0 2rpx 12rpx rgba(31, 41, 55, 0.06);
}
.nav-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
}
.nav-back {
  min-width: 88rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-left: -16rpx;
  padding-right: 8rpx;
  font-size: 48rpx;
  font-weight: 600;
  color: #1F2937;
  line-height: 1;
  &:active { opacity: 0.65; }
}
.nav-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1F2937;
}
.scroll-area { height: 100vh; }
.hero-section {
  margin: 24rpx;
  padding: 36rpx 32rpx;
  border-radius: 24rpx;
  color: #FFFFFF;
  background: linear-gradient(135deg, #4A6CF7 0%, #8B5CF6 58%, #F59E0B 130%);
  box-shadow: 0 12rpx 32rpx rgba(74, 108, 247, 0.22);
}
.hero-topline,
.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}
.hero-kicker {
  font-size: 24rpx;
  opacity: 0.86;
}
.hero-status {
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
  background: rgba(255,255,255,0.18);
}
.hero-title {
  display: block;
  margin-top: 28rpx;
  font-size: 44rpx;
  font-weight: 800;
  line-height: 1.2;
}
.hero-subtitle {
  display: block;
  margin-top: 14rpx;
  font-size: 26rpx;
  line-height: 1.7;
  opacity: 0.88;
}
.price-row {
  margin-top: 32rpx;
  align-items: flex-end;
}
.price-main {
  display: flex;
  align-items: baseline;
  flex-shrink: 0;
}
.price-symbol {
  font-size: 28rpx;
  font-weight: 700;
}
.price-number {
  font-size: 72rpx;
  font-weight: 900;
  line-height: 1;
}
.price-tail {
  margin-left: 8rpx;
  font-size: 24rpx;
  font-weight: 600;
}
.price-note {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
  font-size: 22rpx;
  opacity: 0.84;
}
.quota-strip {
  margin: 0 24rpx 24rpx;
  padding: 28rpx 0;
  display: flex;
  background: #FFFFFF;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.quota-item {
  flex: 1;
  text-align: center;
}
.quota-num {
  display: block;
  font-size: 36rpx;
  font-weight: 800;
  color: #4A6CF7;
}
.quota-label {
  display: block;
  margin-top: 4rpx;
  font-size: 22rpx;
  color: #6B7280;
}
.quota-divider {
  width: 1rpx;
  background: #EEF0F5;
}
.state-card,
.rules-panel,
.rights-panel {
  margin: 0 24rpx 24rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.state-card {
  display: flex;
  gap: 20rpx;
  border: 2rpx solid #EEF0F5;
}
.state-mark {
  width: 14rpx;
  border-radius: 999rpx;
  background: #4A6CF7;
  flex-shrink: 0;
}
.state-card.success .state-mark { background: #10B981; }
.state-card.warning .state-mark { background: #F59E0B; }
.state-card.danger .state-mark { background: #EF4444; }
.state-card.muted .state-mark { background: #9CA3AF; }
.state-copy {
  flex: 1;
}
.state-title,
.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1F2937;
}
.state-desc,
.state-time {
  display: block;
  margin-top: 10rpx;
  font-size: 25rpx;
  color: #6B7280;
  line-height: 1.65;
}
.state-time {
  color: #F59E0B;
  font-weight: 600;
}
.rule-row {
  display: flex;
  gap: 20rpx;
  padding-top: 26rpx;
}
.rule-index {
  width: 56rpx;
  height: 56rpx;
  border-radius: 16rpx;
  background: #EEF2FF;
  color: #4A6CF7;
  font-size: 22rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.rule-copy {
  flex: 1;
}
.rule-title {
  display: block;
  font-size: 27rpx;
  font-weight: 650;
  color: #1F2937;
}
.rule-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.65;
}
.rights-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 24rpx;
}
.right-item {
  min-height: 76rpx;
  padding: 18rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #F8FAFF;
  border-radius: 16rpx;
}
.right-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #10B981;
  flex-shrink: 0;
}
.right-text {
  font-size: 24rpx;
  color: #374151;
  line-height: 1.45;
}
.bottom-spacer {
  height: 176rpx;
}
.bottom-action {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  z-index: 90;
  padding: 18rpx 24rpx;
  padding-bottom: calc(24rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: rgba(255,255,255,0.96);
  box-shadow: 0 -4rpx 20rpx rgba(31, 41, 55, 0.08);
}
.primary-btn {
  height: 92rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #4A6CF7, #8B5CF6);
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  line-height: normal;
  &:active { opacity: 0.86; }
}
.primary-btn::after { border: none; }
.primary-btn.disabled {
  background: #CBD5E1;
  color: #FFFFFF;
}
.action-hint {
  display: block;
  margin-top: 10rpx;
  font-size: 22rpx;
  color: #9CA3AF;
  text-align: center;
}
</style>
