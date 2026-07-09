<template>
  <view class="profile-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">👤 我的</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 用户信息卡片（点击编辑） -->
      <view class="user-card" @tap="showEditModal = true">
        <view class="avatar">
          <image v-if="user?.avatar_url" class="avatar-img" :src="user.avatar_url" mode="aspectFill" />
          <text v-else class="avatar-text">{{ (user?.nickname || user?.username || '?')[0] }}</text>
        </view>
        <view class="user-info">
          <text class="user-greeting">你好</text>
          <text class="user-name">{{ user?.nickname || user?.username || '未登录' }}</text>
          <view class="user-role" :class="user?.role">
            {{ user?.role === 'teacher' ? '教师' : '学生' }}
          </view>
          <text class="user-school" v-if="user?.school">{{ user.school }}</text>
        </view>
        <text class="edit-arrow">编辑 ›</text>
      </view>

      <!-- 种子计划：主转化区 -->
      <view class="billing-hero" @tap="openSeedOffer">
        <view class="billing-hero-glow"></view>
        <view class="billing-hero-top">
          <text class="billing-hero-kicker">首批老师专属</text>
          <text class="billing-hero-badge">限前 50 名</text>
        </view>
        <text class="billing-hero-title">种子计划 · 终身权益</text>
        <text class="billing-hero-desc">前 10 名免费开通，第 11-50 名 9.9 元终身资格</text>
        <view class="billing-hero-footer">
          <view class="billing-hero-price">
            <text class="billing-hero-price-label">低至</text>
            <text class="billing-hero-price-symbol">¥</text>
            <text class="billing-hero-price-num">9.9</text>
            <text class="billing-hero-price-tail">终身</text>
          </view>
          <view class="billing-hero-cta">
            <text>立即查看</text>
          </view>
        </view>
      </view>

      <!-- 使用数据：次要信息 -->
      <view class="usage-section">
        <view v-if="quota.limit > 0" class="usage-block">
          <text class="usage-block-title">今日用量</text>
          <view class="quota-card">
            <view class="quota-header">
              <view class="quota-title-wrap">
                <text class="quota-title">{{ quotaTitle }}</text>
                <text class="quota-subtitle">{{ quotaSubtitle }}</text>
              </view>
              <text class="quota-date">{{ today }}</text>
            </view>
            <view class="quota-progress-wrap">
              <view class="quota-bar-bg">
                <view class="quota-bar-fill" :style="{ width: quotaPercent + '%', background: quotaColor }"></view>
              </view>
              <text class="quota-count" :style="{ color: quotaColor }">{{ quota.used }}<text class="quota-total"> / {{ quota.limit }}</text></text>
            </view>
            <text class="quota-hint">{{ quotaHint }}</text>
          </view>
        </view>

        <view class="usage-block">
          <text class="usage-block-title">累计数据</text>
          <view class="stats-card">
            <view class="stat-item">
              <text class="stat-num">{{ stats.questions }}</text>
              <text class="stat-label">累计题目</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
              <text class="stat-num">{{ stats.papers }}</text>
              <text class="stat-label">累计试卷</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
              <text class="stat-num">{{ stats.ocr }}</text>
              <text class="stat-label">OCR 记录</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 辅助操作区 -->
      <view class="secondary-section">
        <view class="menu-row" @tap="showAbout = true">
          <text class="menu-label">关于小睿化学</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-row logout-row" @tap="handleLogout">
          <text class="menu-label logout-label">退出登录</text>
        </view>
      </view>

      <text class="page-footer">小睿化学 v1.0.0</text>

      <view style="height: 40rpx;"></view>
    </scroll-view>

    <!-- 关于弹窗 -->
    <view v-if="showAbout" class="sheet-mask" @tap="showAbout = false">
      <view class="sheet about-sheet" @tap.stop>
        <view class="sheet-handle"></view>
        <text class="sheet-title">关于小睿化学</text>
        <text class="about-body">高中化学教学辅助小程序，拍照识别题目、智能组卷导出，老师备课学生的刷题好帮手。</text>
        <view class="sheet-btn-primary" @tap="showAbout = false">
          <text class="btn-text">知道了</text>
        </view>
      </view>
    </view>

    <!-- 编辑个人资料弹窗 -->
    <view v-if="showEditModal" class="sheet-mask" @tap="showEditModal = false">
      <view class="sheet" @tap.stop>
        <view class="sheet-handle"></view>
        <text class="sheet-title">编辑个人资料</text>

        <view class="profile-avatar-wrap">
          <button class="avatar-pick-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
            <image v-if="editAvatarUrl" class="avatar-preview" :src="editAvatarUrl" mode="aspectFill" />
            <image v-else-if="user?.avatar_url" class="avatar-preview" :src="user.avatar_url" mode="aspectFill" />
            <view v-else class="avatar-empty">
              <text class="avatar-plus">+</text>
            </view>
          </button>
          <text class="avatar-label">点击更换头像</text>
        </view>

        <view class="field" style="margin-top: 28rpx;">
          <input class="field-input" type="nickname" v-model="editNickname" :placeholder="user?.nickname || '请输入昵称'" placeholder-class="placeholder" />
        </view>

        <view class="sheet-btn-primary" @tap="saveProfile">
          <text class="btn-text">保存</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { questionsAPI, papersAPI, ocrAPI, authAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      user: null,
      stats: { questions: 0, papers: 0, ocr: 0 },
      quota: { used: 0, limit: 0, remaining: 0, engineId: '', engineName: '', engineLabel: '' },
      showEditModal: false,
      showAbout: false,
      editNickname: '',
      editAvatarUrl: '',
    }
  },
  computed: {
    today() {
      const d = new Date()
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    quotaTitle() {
      if (!this.quota.engineLabel) return '今日 OCR 额度'
      return `${this.quota.engineLabel} · 今日额度`
    },
    quotaSubtitle() {
      if (this.quota.engineName) return this.quota.engineName
      if (this.quota.engineId === 'doubao_vision') return '豆包视觉 · 复杂题结构化识别'
      if (this.quota.engineId === 'pix2text_online') return 'Pix2Text · 公式高精度识别'
      return '拍题识别服务'
    },
    quotaPercent() {
      if (!this.quota.limit) return 0
      return Math.min(Math.round((this.quota.used / this.quota.limit) * 100), 100)
    },
    quotaColor() {
      if (this.quotaPercent >= 100) return '#EF4444'
      if (this.quotaPercent >= 80) return '#F59E0B'
      return '#6366F1'
    },
    quotaHint() {
      const r = this.quota.remaining
      if (r === null || r === undefined) return '额度不限'
      if (r <= 0) return '今日额度已用完，明天再来吧'
      if (r <= 3) return `仅剩 ${r} 次，省着点用哦`
      return `剩余 ${r} 次，够用的`
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
    this.loadUserInfo()
    this.loadStats()
    this.loadQuota()
  },
  methods: {
    loadUserInfo() {
      const info = uni.getStorageSync('user_info')
      this.user = info ? (typeof info === 'string' ? JSON.parse(info) : info) : null
      authAPI.getMe().then(res => {
        this.user = res
        uni.setStorageSync('user_info', JSON.stringify(res))
      }).catch(() => {})
    },
    async loadStats() {
      try {
        const [q, p, o] = await Promise.all([
          questionsAPI.list({ page: 1, page_size: 1 }),
          papersAPI.list({ page: 1, page_size: 1 }),
          ocrAPI.history({ page: 1, page_size: 1 }),
        ])
        this.stats.questions = q.total || 0
        this.stats.papers = p.total || 0
        this.stats.ocr = o.total || 0
      } catch (e) {}
    },
    async loadQuota() {
      try {
        const res = await ocrAPI.listEngines()
        const engines = res?.engines || []
        // 找到第一个有 quota 的付费引擎（doubao_vision 或 pix2text_online）
        const paid = engines.find((e) => e.quota && e.quota.limit > 0)
        if (paid) {
          this.quota = {
            used: paid.quota.used || 0,
            limit: paid.quota.limit || 0,
            remaining: paid.quota.remaining,
            engineId: paid.id || '',
            engineName: paid.name || '',
            engineLabel: paid.label || '',
          }
        } else {
          this.quota = { used: 0, limit: 0, remaining: 0, engineId: '', engineName: '', engineLabel: '' }
        }
      } catch (e) {}
    },
    openSeedOffer() {
      uni.navigateTo({ url: '/pages/billing/seed-offer' })
    },
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('access_token')
            uni.removeStorageSync('refresh_token')
            uni.removeStorageSync('user_info')
            uni.reLaunch({ url: '/pages/login/login' })
          }
        },
      })
    },
    onChooseAvatar(e) {
      if (e.detail.avatarUrl) this.editAvatarUrl = e.detail.avatarUrl
    },
    async saveProfile() {
      uni.showLoading({ title: '保存中...' })
      try {
        let avatarUrl = ''
        if (this.editAvatarUrl) {
          // #ifdef MP-WEIXIN
          if (wx && wx.cloud) {
            const r = await new Promise((res, rej) => {
              wx.cloud.uploadFile({
                cloudPath: `avatars/${Date.now()}_${Math.random().toString(36).slice(2,8)}.jpg`,
                filePath: this.editAvatarUrl, success: res, fail: rej
              })
            })
            avatarUrl = r.fileID
          }
          // #endif
        }
        const updateData = {}
        if (this.editNickname) updateData.nickname = this.editNickname
        if (avatarUrl) updateData.avatar_url = avatarUrl
        if (Object.keys(updateData).length > 0) {
          const updatedUser = await authAPI.updateMe(updateData)
          uni.setStorageSync('user_info', JSON.stringify(updatedUser))
          this.user = updatedUser
        }
        uni.hideLoading()
        this.showEditModal = false
        uni.showToast({ title: '保存成功', icon: 'success' })
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: '保存失败', icon: 'none' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: #F5F6FA;
}
.nav-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
}
.nav-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
}
.nav-title { font-size: 34rpx; font-weight: 700; color: #fff; }
.scroll-area { height: 100vh; }
.user-card {
  margin: 24rpx 24rpx 20rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx 36rpx;
  display: flex;
  align-items: center;
  gap: 28rpx;
  color: #1F2937;
  box-shadow: 0 4rpx 20rpx rgba(15, 23, 42, 0.06);
  border: 1rpx solid #EEF2FF;
  &:active { background: #FAFAFF; }
}
.avatar {
  width: 100rpx;
  height: 100rpx;
  background: #F3F4F6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  border: 3rpx solid #EDE9FE;
}
.avatar-img { width: 100rpx; height: 100rpx; border-radius: 50%; }
.avatar-text { font-size: 40rpx; font-weight: 700; color: #7C3AED; }
.user-greeting {
  display: block;
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 2rpx;
}
.user-name { display: block; font-size: 34rpx; font-weight: 700; color: #111827; margin-bottom: 8rpx; }
.user-role {
  display: inline-block;
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: #F3E8FF;
  color: #7C3AED;
  margin-bottom: 4rpx;
}
.user-school { display: block; font-size: 22rpx; color: #6B7280; }
.edit-arrow { font-size: 24rpx; color: #9CA3AF; flex-shrink: 0; }

/* 种子计划主转化区 */
.billing-hero {
  position: relative;
  margin: 0 24rpx 32rpx;
  padding: 32rpx 28rpx 28rpx;
  border-radius: 24rpx;
  overflow: hidden;
  background: linear-gradient(135deg, #2563EB 0%, #4F46E5 45%, #7C3AED 100%);
  box-shadow: 0 16rpx 40rpx rgba(37, 99, 235, 0.25);
  &:active { opacity: 0.92; }
}
.billing-hero-glow {
  position: absolute;
  top: -60rpx;
  right: -40rpx;
  width: 220rpx;
  height: 220rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
  pointer-events: none;
}
.billing-hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}
.billing-hero-kicker {
  font-size: 22rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.88);
  letter-spacing: 1rpx;
}
.billing-hero-badge {
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
}
.billing-hero-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
}
.billing-hero-desc {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.5;
}
.billing-hero-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 28rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.18);
}
.billing-hero-price {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}
.billing-hero-price-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.75);
  margin-right: 4rpx;
}
.billing-hero-price-symbol {
  font-size: 24rpx;
  font-weight: 700;
  color: #FDE68A;
}
.billing-hero-price-num {
  font-size: 44rpx;
  font-weight: 800;
  color: #FDE68A;
  line-height: 1;
}
.billing-hero-price-tail {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.88);
  margin-left: 4rpx;
}
.billing-hero-cta {
  padding: 14rpx 28rpx;
  border-radius: 999rpx;
  background: #fff;
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.12);
  text {
    font-size: 26rpx;
    font-weight: 700;
    color: #6D28D9;
  }
}

/* 使用数据区 */
.usage-section {
  margin: 0 24rpx 28rpx;
}
.usage-block {
  & + & {
    margin-top: 28rpx;
  }
}
.usage-block-title {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: #9CA3AF;
  letter-spacing: 1rpx;
  margin-bottom: 12rpx;
  padding-left: 4rpx;
}
.stats-card {
  display: flex;
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx 0;
  border: 1rpx solid #E5E7EB;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
}
.stat-item { flex: 1; text-align: center; }
.stat-num { display: block; font-size: 32rpx; font-weight: 700; color: #374151; }
.stat-label { display: block; font-size: 22rpx; color: #9CA3AF; margin-top: 6rpx; }
.stat-divider { width: 1rpx; background: #E5E7EB; align-self: stretch; margin: 8rpx 0; }

/* OCR 额度卡片 — 方案 C 中性灰白卡 */
.quota-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx 24rpx 20rpx;
  border: 1rpx solid #E5E7EB;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
}
.quota-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 20rpx;
}
.quota-title-wrap {
  flex: 1;
  min-width: 0;
}
.quota-title { display: block; font-size: 28rpx; font-weight: 700; color: #374151; line-height: 1.35; }
.quota-subtitle { display: block; margin-top: 6rpx; font-size: 22rpx; color: #6B7280; line-height: 1.4; }
.quota-date { font-size: 24rpx; color: #9CA3AF; flex-shrink: 0; padding-top: 2rpx; }
.quota-progress-wrap {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.quota-bar-bg {
  flex: 1;
  height: 16rpx;
  background: #F3F4F6;
  border-radius: 8rpx;
  overflow: hidden;
}
.quota-bar-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 300ms ease-out;
}
.quota-count { font-size: 30rpx; font-weight: 700; flex-shrink: 0; }
.quota-total { font-size: 24rpx; font-weight: 400; color: #9CA3AF; }
.quota-hint {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
  margin-top: 12rpx;
}

/* 辅助操作区 */
.secondary-section {
  margin: 0 24rpx;
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.03);
}
.menu-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 24rpx;
  &:active { background: #F9FAFB; }
  & + & {
    border-top: 1rpx solid #F3F4F6;
  }
}
.menu-label {
  font-size: 28rpx;
  color: #374151;
}
.menu-arrow {
  font-size: 32rpx;
  color: #D1D5DB;
}
.logout-row {
  justify-content: center;
  &:active { background: #FEF2F2; }
}
.logout-label {
  color: #EF4444;
  font-weight: 500;
}
.page-footer {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #C4C9D4;
  margin: 28rpx 24rpx 0;
}
.about-body {
  display: block;
  font-size: 28rpx;
  color: #4B5563;
  line-height: 1.7;
  margin-bottom: 28rpx;
}
.about-sheet .sheet-title {
  margin-bottom: 20rpx;
}

/* 编辑弹窗 */
.sheet-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 200;
}
.sheet {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 20rpx 40rpx;
  padding-bottom: calc(60rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(60rpx + env(safe-area-inset-bottom));
  z-index: 201;
}
.sheet-handle {
  width: 60rpx; height: 8rpx;
  background: #E2E8F0; border-radius: 4rpx;
  margin: 0 auto 24rpx;
}
.sheet-title {
  display: block; font-size: 34rpx; font-weight: 700;
  color: #1E293B; text-align: center; margin-bottom: 28rpx;
}
.profile-avatar-wrap {
  display: flex; flex-direction: column; align-items: center;
}
.avatar-pick-btn {
  width: 144rpx; height: 144rpx; border-radius: 50%;
  background: #F1F5F9; display: flex; align-items: center; justify-content: center;
  padding: 0; margin: 0; line-height: normal;
  border: 3rpx dashed #CBD5E1;
}
.avatar-pick-btn::after { border: none; }
.avatar-preview { width: 144rpx; height: 144rpx; border-radius: 50%; }
.avatar-empty { display: flex; align-items: center; justify-content: center; width: 144rpx; height: 144rpx; }
.avatar-plus { font-size: 56rpx; color: #94A3B8; font-weight: 300; }
.avatar-label { font-size: 22rpx; color: #94A3B8; margin-top: 12rpx; }
.field {
  background: #F1F5F9; border-radius: 14rpx;
  padding: 0 28rpx; height: 92rpx;
  display: flex; align-items: center; margin-bottom: 20rpx;
}
.field-input { flex: 1; height: 92rpx; font-size: 28rpx; color: #1E293B; }
.placeholder { color: #94A3B8; font-size: 28rpx; }
.sheet-btn-primary {
  background: linear-gradient(135deg, #4A6CF7, #6366F1);
  border-radius: 14rpx; height: 88rpx;
  display: flex; align-items: center; justify-content: center;
  margin-top: 12rpx;
  &:active { opacity: 0.85; }
}
.btn-text { color: #fff; font-size: 30rpx; font-weight: 600; }
</style>
