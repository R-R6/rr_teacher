<template>
  <view class="mistakes-page">
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <view class="nav-back" @tap="goBack">‹</view>
        <text class="nav-title">❌ 错题本</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 统计 -->
      <view class="stats-row">
        <view class="stat-box">
          <text class="stat-num">{{ mistakeStats.total || 0 }}</text>
          <text class="stat-label">总错题</text>
        </view>
        <view class="stat-box">
          <text class="stat-num">{{ mistakeStats.mastered || 0 }}</text>
          <text class="stat-label">已掌握</text>
        </view>
        <view class="stat-box">
          <text class="stat-num">{{ mistakeStats.unmastered || 0 }}</text>
          <text class="stat-label">待复习</text>
        </view>
      </view>

      <!-- 错题列表 -->
      <view v-if="loading" class="loading-state">
        <view class="loading-spinner"></view>
      </view>

      <view v-else-if="mistakes.length === 0" class="empty-state">
        <text class="empty-icon">🎉</text>
        <text class="empty-text">暂无错题</text>
        <text class="empty-hint">太棒了，继续保持！</text>
      </view>

      <view v-else class="mistake-list">
        <view v-for="item in mistakes" :key="item.id" class="mistake-card">
          <view class="mc-header">
            <view class="mc-type" :style="{ background: getTypeColor(item.question_type) }">
              {{ getTypeName(item.question_type) }}
            </view>
            <text class="mc-count">错误 {{ item.wrong_count }} 次</text>
            <view v-if="item.is_mastered" class="mc-mastered">✓ 已掌握</view>
          </view>
          <text class="mc-content">{{ latexToUnicode(item.content) }}</text>
          <view class="mc-tags" v-if="item.tags && item.tags.length">
            <text v-for="(tag, i) in item.tags.slice(0, 3)" :key="i" class="mc-tag">{{ tag.name }}</text>
          </view>
          <view class="mc-actions">
            <view class="mc-btn practice" @tap="retryOne(item)">
              <text>🔄 重做</text>
            </view>
            <view v-if="!item.is_mastered" class="mc-btn master" @tap="markMastered(item)">
              <text>✓ 标记掌握</text>
            </view>
            <view class="mc-btn delete" @tap="deleteMistake(item)">
              <text>🗑️</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 加载更多 -->
      <view v-if="mistakes.length > 0 && mistakes.length < total" class="load-more" @tap="loadMore">
        <text>加载更多</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { mistakesAPI } from '../../utils/api.js'
import { QUESTION_TYPES, latexToUnicode } from '../../utils/util.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      mistakes: [],
      total: 0,
      page: 1,
      loading: false,
      mistakeStats: {},
    }
  },
  onLoad() {
    try {
      const sysInfo = uni.getSystemInfoSync()
      this.statusBarHeight = sysInfo.statusBarHeight || 20
    } catch (e) { this.statusBarHeight = 20 }
    this.navHeight = this.statusBarHeight + 44
  },
  onShow() {
    this.page = 1
    this.loadMistakes()
    this.loadStats()
  },
  methods: {
    latexToUnicode,
    getTypeName(type) { return QUESTION_TYPES[type]?.label || type },
    getTypeColor(type) { return QUESTION_TYPES[type]?.color || '#6B7280' },

    async loadMistakes() {
      this.loading = true
      try {
        const res = await mistakesAPI.list({ page: this.page, page_size: 20 })
        this.mistakes = this.page === 1 ? (res.items || []) : [...this.mistakes, ...(res.items || [])]
        this.total = res.total || 0
      } catch (e) {}
      this.loading = false
    },

    async loadStats() {
      try {
        this.mistakeStats = await mistakesAPI.getStats()
      } catch (e) {}
    },

    loadMore() {
      this.page++
      this.loadMistakes()
    },

    goBack() { uni.navigateBack() },

    async markMastered(item) {
      try {
        await mistakesAPI.markMastered(item.id)
        item.is_mastered = true
        this.loadStats()
        uni.showToast({ title: '已标记掌握', icon: 'success' })
      } catch (e) {}
    },

    async deleteMistake(item) {
      uni.showModal({
        title: '确认删除',
        content: '确定从错题本中删除此题？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await mistakesAPI.delete(item.id)
              this.mistakes = this.mistakes.filter(m => m.id !== item.id)
              this.total--
              this.loadStats()
              uni.showToast({ title: '已删除', icon: 'success' })
            } catch (e) {}
          }
        },
      })
    },

    retryOne(item) {
      uni.navigateTo({
        url: `/pages/practice/question?mode=mistakes&question_id=${item.question_id}`
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.mistakes-page { min-height: 100vh; background: #F7FAFC; }
.nav-bar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: linear-gradient(135deg, #E53E3E, #FC8181);
}
.nav-content { height: 88rpx; display: flex; align-items: center; padding: 0 32rpx; }
.nav-back { font-size: 40rpx; color: #fff; padding-right: 16rpx; }
.nav-title { font-size: 34rpx; font-weight: 700; color: #fff; }
.scroll-area { height: 100vh; }

.stats-row {
  display: flex; gap: 16rpx; padding: 20rpx 24rpx;
}
.stat-box {
  flex: 1; background: #fff; border-radius: 16rpx;
  padding: 20rpx; text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.stat-num { display: block; font-size: 36rpx; font-weight: 700; color: #1E293B; }
.stat-label { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }

.mistake-list { padding: 0 24rpx; }
.mistake-card {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.mc-header { display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx; }
.mc-type {
  font-size: 20rpx; color: #fff; padding: 4rpx 12rpx; border-radius: 6rpx;
}
.mc-count { font-size: 22rpx; color: #E53E3E; font-weight: 500; }
.mc-mastered { font-size: 22rpx; color: #38A169; font-weight: 500; }
.mc-content { font-size: 26rpx; color: #1E293B; line-height: 1.6; display: block; margin-bottom: 8rpx; }
.mc-tags { display: flex; gap: 8rpx; margin-bottom: 12rpx; }
.mc-tag {
  font-size: 20rpx; color: #2B6CB0; background: rgba(43,108,176,0.08);
  padding: 4rpx 12rpx; border-radius: 6rpx;
}
.mc-actions { display: flex; gap: 12rpx; }
.mc-btn {
  padding: 10rpx 20rpx; border-radius: 10rpx;
  font-size: 24rpx; background: #F1F5F9;
  &.practice { color: #2B6CB0; }
  &.master { color: #38A169; }
  &.delete { color: #94A3B8; }
}

.empty-state { text-align: center; padding: 80rpx 0; }
.empty-icon { font-size: 48rpx; display: block; margin-bottom: 12rpx; }
.empty-text { display: block; font-size: 28rpx; color: #94A3B8; }
.empty-hint { display: block; font-size: 24rpx; color: #CBD5E1; margin-top: 8rpx; }
.load-more {
  text-align: center; padding: 24rpx; font-size: 26rpx; color: #2B6CB0;
}
.loading-state { text-align: center; padding: 60rpx 0; }
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid #E2E8F0; border-top-color: #2B6CB0;
  border-radius: 50%; animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
