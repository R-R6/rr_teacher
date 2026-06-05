<template>
  <view class="profile-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">👤 我的</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <view class="avatar">
          <text class="avatar-text">{{ (user?.nickname || user?.username || '?')[0] }}</text>
        </view>
        <view class="user-info">
          <text class="user-name">{{ user?.nickname || user?.username || '未登录' }}</text>
          <view class="user-role" :class="user?.role">
            {{ user?.role === 'teacher' ? '👨‍🏫 教师' : '🎓 学生' }}
          </view>
          <text class="user-school" v-if="user?.school">{{ user.school }}</text>
        </view>
      </view>

      <!-- 统计 -->
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-num">{{ stats.questions }}</text>
          <text class="stat-label">题目</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ stats.papers }}</text>
          <text class="stat-label">试卷</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ stats.ocr }}</text>
          <text class="stat-label">OCR识别</text>
        </view>
      </view>

      <!-- 功能列表 -->
      <view class="menu-card">
        <view class="menu-item" @tap="goTo('/pages/tags/tags')">
          <text class="menu-icon">🏷️</text>
          <text class="menu-text">标签管理</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @tap="initTags">
          <text class="menu-icon">🌱</text>
          <text class="menu-text">初始化预设标签</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-card">
        <view class="menu-item" @tap="viewAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于系统</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 退出登录 -->
      <view class="logout-btn" @tap="handleLogout">
        <text>退出登录</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { tagsAPI, questionsAPI, papersAPI, ocrAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      user: null,
      stats: { questions: 0, papers: 0, ocr: 0 },
    }
  },
  onLoad() {
    const sysInfo = uni.getSystemInfoSync()
    this.statusBarHeight = sysInfo.statusBarHeight || 20
    this.navHeight = this.statusBarHeight + 44
  },
  onShow() {
    const info = uni.getStorageSync('user_info')
    this.user = info ? (typeof info === 'string' ? JSON.parse(info) : info) : null
    this.loadStats()
  },
  methods: {
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
    goTo(url) {
      uni.navigateTo({ url })
    },
    viewAbout() {
      uni.showModal({
        title: '高中化学教学辅助系统',
        content: '版本 1.0.0\n\n功能：拍照OCR识别化学题目、管理题库、智能组卷、导出Word试卷\n\n技术栈：uni-app + FastAPI + Pix2Text',
        showCancel: false,
      })
    },
    async initTags() {
      uni.showModal({
        title: '初始化标签',
        content: '将创建预设的高中化学标签，已有标签不会重复。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await tagsAPI.seed()
              uni.showToast({ title: '初始化成功', icon: 'success' })
            } catch (e) {}
          }
        },
      })
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
}
.avatar-text {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
}
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
.menu-card {
  background: #fff;
  border-radius: 20rpx;
  margin: 0 24rpx 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
  &:last-child { border-bottom: none; }
  &:active { background: #FAFBFC; }
}
.menu-icon { font-size: 32rpx; margin-right: 16rpx; }
.menu-text { flex: 1; font-size: 28rpx; color: #374151; }
.menu-arrow { font-size: 32rpx; color: #D1D5DB; }
.logout-btn {
  margin: 40rpx 24rpx;
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
</style>
