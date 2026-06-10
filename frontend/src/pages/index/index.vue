<template>
  <view class="home-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">🧪 小睿化学</text>
        <text class="nav-subtitle">Hi，{{ nickname }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 欢迎卡片 -->
      <view class="welcome-card">
        <view class="welcome-left">
          <text class="welcome-text">教学好帮手</text>
          <text class="welcome-desc">拍照识别 · 智能组卷 · 一键导出</text>
        </view>
        <view class="welcome-icon">📸</view>
      </view>

      <!-- 核心功能入口 -->
      <view class="section-title">核心功能</view>
      <view class="feature-grid">
        <view class="feature-item" @tap="goTo('/pages/ocr/ocr')">
          <view class="feature-icon" style="background: linear-gradient(135deg, #4A6CF7, #6B8AFF)">📷</view>
          <text class="feature-name">拍照识别</text>
          <text class="feature-desc">OCR智能识别化学题目</text>
        </view>
        <view class="feature-item" @tap="goTo('/pages/questions/questions')">
          <view class="feature-icon" style="background: linear-gradient(135deg, #8B5CF6, #A78BFA)">📚</view>
          <text class="feature-name">题库管理</text>
          <text class="feature-desc">海量题目分类管理</text>
        </view>
        <view class="feature-item" @tap="goTo('/pages/paper-create/paper-create')">
          <view class="feature-icon" style="background: linear-gradient(135deg, #22C55E, #4ADE80)">📝</view>
          <text class="feature-name">智能组卷</text>
          <text class="feature-desc">手动/自动组合试卷</text>
        </view>
        <view class="feature-item" @tap="goTo('/pages/papers/papers')">
          <view class="feature-icon" style="background: linear-gradient(135deg, #F59E0B, #FBBF24)">📄</view>
          <text class="feature-name">导出试卷</text>
          <text class="feature-desc">Word格式直接打印</text>
        </view>
      </view>

      <!-- 最近题目 -->
      <view class="section-header">
        <text class="section-title">最近题目</text>
        <text class="section-more" @tap="goTo('/pages/questions/questions')">查看全部 ></text>
      </view>
      <view v-if="recentQuestions.length === 0" class="empty-state">
        <text class="empty-icon">📭</text>
        <text class="empty-text">暂无题目</text>
        <text class="empty-hint">点击上方「拍照识别」开始添加</text>
      </view>
      <view v-else class="question-list">
        <view v-for="q in recentQuestions" :key="q.id" class="question-card" @tap="goDetail(q.id)">
          <view class="q-header">
            <view class="q-type" :style="{ background: getTypeColor(q.question_type) }">{{ getTypeName(q.question_type) }}</view>
            <view class="q-difficulty">
              <text v-for="i in 5" :key="i" :class="i <= q.difficulty ? 'star-on' : 'star-off'">★</text>
            </view>
          </view>
          <text class="q-content">{{ truncate(q.content, 60) }}</text>
          <text class="q-time">{{ formatTime(q.created_at) }}</text>
        </view>
      </view>

      <!-- 快捷操作 -->
      <view class="section-title">快捷操作</view>
      <view class="quick-actions">
        <view class="action-item" @tap="goTo('/pages/tags/tags')">
          <text class="action-icon">🏷️</text>
          <text class="action-text">标签管理</text>
        </view>
        <view class="action-item" @tap="initTags">
          <text class="action-icon">🌱</text>
          <text class="action-text">初始化标签</text>
        </view>
        <view class="action-item" @tap="goTo('/pages/paper-create/paper-create?mode=auto')">
          <text class="action-icon">⚡</text>
          <text class="action-text">快速组卷</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { questionsAPI, tagsAPI } from '../../utils/api.js'
import { truncate, formatTime, QUESTION_TYPES } from '../../utils/util.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      nickname: '老师',
      recentQuestions: [],
    }
  },
  onShow() {
    const info = uni.getStorageSync('user_info')
    if (info) {
      const user = typeof info === 'string' ? JSON.parse(info) : info
      this.nickname = user.nickname || user.username || '老师'
    }
    this.loadRecentQuestions()
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
  methods: {
    truncate,
    formatTime,
    getTypeName(type) {
      return QUESTION_TYPES[type]?.label || type
    },
    getTypeColor(type) {
      return QUESTION_TYPES[type]?.color || '#6B7280'
    },
    async loadRecentQuestions() {
      const token = uni.getStorageSync('access_token')
      if (!token) return
      try {
        const res = await questionsAPI.list({ page: 1, page_size: 3 })
        this.recentQuestions = res.items || []
      } catch (e) {
        console.log('加载题目失败:', e)
      }
    },
    goTo(url) {
      if (url.includes('switchTab') || ['/pages/questions/questions', '/pages/papers/papers', '/pages/index/index'].includes(url)) {
        uni.switchTab({ url })
      } else {
        uni.navigateTo({ url })
      }
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/question-detail/question-detail?id=${id}` })
    },
    async initTags() {
      uni.showModal({
        title: '初始化标签',
        content: '将创建预设的高中化学标签（教材、知识点、题型、难度），已有的标签不会重复创建。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await tagsAPI.seed()
              uni.showToast({ title: '标签初始化成功', icon: 'success' })
            } catch (e) {
              // handled
            }
          }
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: #F5F6FA;
}
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: linear-gradient(135deg, #4A6CF7 0%, #6B8AFF 100%);
}
.nav-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  justify-content: space-between;
}
.nav-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
}
.nav-subtitle {
  font-size: 26rpx;
  color: rgba(255,255,255,0.85);
}
.scroll-area {
  height: 100vh;
}
.welcome-card {
  margin: 24rpx;
  background: linear-gradient(135deg, #4A6CF7 0%, #7C3AED 100%);
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}
.welcome-text {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  margin-bottom: 8rpx;
}
.welcome-desc {
  display: block;
  font-size: 24rpx;
  opacity: 0.85;
}
.welcome-icon {
  font-size: 60rpx;
}
.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
  padding: 24rpx 32rpx 16rpx;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx 16rpx;
}
.section-more {
  font-size: 24rpx;
  color: #4A6CF7;
}
.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
  padding: 0 24rpx;
}
.feature-item {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  &:active { transform: scale(0.98); }
}
.feature-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-bottom: 16rpx;
}
.feature-name {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 4rpx;
}
.feature-desc {
  display: block;
  font-size: 22rpx;
  color: #9CA3AF;
}
.empty-state {
  text-align: center;
  padding: 60rpx 0;
}
.empty-icon { font-size: 48rpx; display: block; margin-bottom: 12rpx; }
.empty-text { display: block; font-size: 28rpx; color: #9CA3AF; }
.empty-hint { display: block; font-size: 24rpx; color: #D1D5DB; margin-top: 8rpx; }

.question-list {
  padding: 0 24rpx;
}
.question-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #FAFBFC; }
}
.q-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}
.q-type {
  font-size: 22rpx;
  color: #fff;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  font-weight: 500;
}
.q-difficulty { font-size: 20rpx; }
.star-on { color: #F59E0B; }
.star-off { color: #E5E7EB; }
.q-content {
  font-size: 26rpx;
  color: #374151;
  line-height: 1.6;
  display: block;
  margin-bottom: 8rpx;
}
.q-time {
  font-size: 22rpx;
  color: #9CA3AF;
}

.quick-actions {
  display: flex;
  gap: 16rpx;
  padding: 0 24rpx 40rpx;
}
.action-item {
  flex: 1;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx 16rpx;
  text-align: center;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #FAFBFC; }
}
.action-icon { display: block; font-size: 36rpx; margin-bottom: 8rpx; }
.action-text { font-size: 24rpx; color: #374151; }
.practice-entry {
  display: flex; align-items: center; justify-content: space-between;
  margin: 0 24rpx 20rpx; background: linear-gradient(135deg, #2B6CB0, #3182CE);
  border-radius: 20rpx; padding: 32rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(43,108,176,0.3);
  &:active { opacity: 0.9; }
}
.practice-title { display: block; font-size: 32rpx; font-weight: 700; color: #fff; }
.practice-desc { display: block; font-size: 24rpx; color: rgba(255,255,255,0.75); margin-top: 4rpx; }
.practice-arrow { font-size: 36rpx; color: rgba(255,255,255,0.6); }
</style>
