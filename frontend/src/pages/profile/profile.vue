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
          <text class="user-name">{{ user?.nickname || user?.username || '未登录' }}</text>
          <view class="user-role" :class="user?.role">
            {{ user?.role === 'teacher' ? '教师' : '学生' }}
          </view>
          <text class="user-school" v-if="user?.school">{{ user.school }}</text>
        </view>
        <text class="edit-arrow">编辑 ›</text>
      </view>

      <!-- 统计 -->
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

      <!-- OCR 额度卡片 -->
      <view v-if="quota.limit > 0" class="quota-card">
        <view class="quota-header">
          <text class="quota-title">今日 OCR 额度</text>
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

      <!-- 种子计划入口 -->
      <view class="billing-card" @tap="openSeedOffer">
        <view class="billing-icon">
          <view class="billing-icon-core"></view>
        </view>
        <view class="billing-copy">
          <view class="billing-title-row">
            <text class="billing-title">种子计划 · 终身权益</text>
            <text class="billing-badge">限前 50 名</text>
          </view>
          <text class="billing-desc">前 10 名免费，第 11-50 名 9.9 元终身开通</text>
        </view>
        <text class="billing-arrow">›</text>
      </view>

      <!-- 关于小睿化学 -->
      <view class="intro-card">
        <text class="intro-title">🧪 关于小睿化学</text>
        <text class="intro-body">高中化学教学辅助小程序，拍照识别题目、智能组卷导出，老师备课学生的刷题好帮手。</text>
        <text class="intro-version">v1.0.0</text>
      </view>

      <!-- 退出登录 -->
      <view class="logout-btn" @tap="handleLogout">
        <text>退出登录</text>
      </view>

      <view style="height: 40rpx;"></view>
    </scroll-view>

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
      quota: { used: 0, limit: 0, remaining: 0 },
      showEditModal: false,
      editNickname: '',
      editAvatarUrl: '',
    }
  },
  computed: {
    today() {
      const d = new Date()
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    quotaPercent() {
      if (!this.quota.limit) return 0
      return Math.min(Math.round((this.quota.used / this.quota.limit) * 100), 100)
    },
    quotaColor() {
      if (this.quotaPercent >= 100) return '#EF4444'
      if (this.quotaPercent >= 80) return '#F59E0B'
      return '#10B981'
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
          }
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
  margin: 24rpx;
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  align-items: center;
  gap: 28rpx;
  color: #fff;
}
.avatar {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}
.avatar-img { width: 100rpx; height: 100rpx; border-radius: 50%; }
.avatar-text { font-size: 40rpx; font-weight: 700; color: #fff; }
.user-name { display: block; font-size: 32rpx; font-weight: 700; margin-bottom: 4rpx; }
.user-role {
  display: inline-block;
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: rgba(255,255,255,0.2);
  margin-bottom: 4rpx;
}
.user-school { display: block; font-size: 22rpx; opacity: 0.8; }
.edit-arrow { font-size: 24rpx; color: rgba(255,255,255,0.7); flex-shrink: 0; }

/* 统计 */
.stats-card {
  display: flex;
  background: #fff;
  border-radius: 20rpx;
  margin: 0 24rpx 24rpx;
  padding: 32rpx 0;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.stat-item { flex: 1; text-align: center; }
.stat-num { display: block; font-size: 36rpx; font-weight: 700; color: #8B5CF6; }
.stat-label { display: block; font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }
.stat-divider { width: 1rpx; background: #F3F4F6; }

/* OCR 额度卡片 */
.quota-card {
  margin: 0 24rpx 24rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx 28rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.quota-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}
.quota-title { font-size: 28rpx; font-weight: 600; color: #1F2937; }
.quota-date { font-size: 24rpx; color: #9CA3AF; }
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

/* 种子计划入口 */
.billing-card {
  margin: 0 24rpx 24rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  border: 2rpx solid #EEF2FF;
  &:active { background: #F8FAFF; }
}
.billing-icon {
  width: 76rpx;
  height: 76rpx;
  border-radius: 22rpx;
  background: linear-gradient(135deg, #4A6CF7, #8B5CF6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.billing-icon-core {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 0 10rpx rgba(255,255,255,0.22);
}
.billing-copy {
  flex: 1;
  min-width: 0;
}
.billing-title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-wrap: wrap;
}
.billing-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}
.billing-badge {
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  background: #FEF3C7;
  color: #B45309;
  font-size: 20rpx;
  font-weight: 600;
}
.billing-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.45;
}
.billing-arrow {
  font-size: 36rpx;
  color: #9CA3AF;
  flex-shrink: 0;
}

/* 关于小睿化学 */
.intro-card {
  margin: 0 24rpx 24rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.intro-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 12rpx;
}
.intro-body {
  display: block;
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
}
.intro-version {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 16rpx;
}

/* 退出登录 */
.logout-btn {
  margin: 16rpx 24rpx 0;
  padding: 28rpx 0;
  text-align: center;
  background: #fff;
  border-radius: 16rpx;
  color: #EF4444;
  font-size: 30rpx;
  font-weight: 500;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #FEF2F2; }
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
