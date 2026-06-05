<template>
  <view class="questions-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">📚 题库管理</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 搜索栏 -->
      <view class="search-bar">
        <view class="search-input-wrap">
          <text class="search-icon">🔍</text>
          <input class="search-input" v-model="keyword" placeholder="搜索题目关键词" @confirm="loadQuestions(1)" />
          <text v-if="keyword" class="clear-btn" @tap="keyword = ''; loadQuestions(1)">✕</text>
        </view>
      </view>

      <!-- 筛选栏 -->
      <scroll-view scroll-x class="filter-bar">
        <view :class="['filter-tag', selectedType === '' ? 'active' : '']" @tap="selectedType = ''; loadQuestions(1)">全部</view>
        <view :class="['filter-tag', selectedType === key ? 'active' : '']"
              v-for="(t, key) in types" :key="key"
              @tap="selectedType = key; loadQuestions(1)">
          {{ t.label }}
        </view>
      </scroll-view>

      <!-- 题目列表 -->
      <view v-if="loading" class="loading-state">
        <view class="loading-spinner"></view>
      </view>
      <view v-else-if="questions.length === 0" class="empty-state">
        <text class="empty-icon">📭</text>
        <text class="empty-text">暂无题目</text>
      </view>
      <view v-else class="question-list">
        <view v-for="q in questions" :key="q.id" class="q-card" @tap="goDetail(q.id)">
          <view class="q-top">
            <view class="q-type" :style="{ background: getTypeColor(q.question_type) }">
              {{ getTypeName(q.question_type) }}
            </view>
            <view class="q-stars">
              <text v-for="i in 5" :key="i" :class="i <= q.difficulty ? 'star-on' : 'star-off'">★</text>
            </view>
            <view class="q-verified" v-if="q.is_verified">✓ 已核实</view>
          </view>
          <text class="q-content">{{ truncate(q.content, 80) }}</text>
          <view class="q-bottom">
            <text class="q-source" v-if="q.source">来源: {{ q.source }}</text>
            <text class="q-time">{{ formatTime(q.created_at) }}</text>
          </view>
          <view class="q-tags" v-if="q.tags && q.tags.length">
            <text class="q-tag" v-for="tag in q.tags.slice(0, 3)" :key="tag.id">{{ tag.name }}</text>
          </view>
        </view>
      </view>

      <!-- 分页 -->
      <view class="pagination" v-if="total > pageSize">
        <view class="page-btn" :class="{ disabled: page <= 1 }" @tap="page > 1 && loadQuestions(page - 1)">上一页</view>
        <text class="page-info">{{ page }} / {{ Math.ceil(total / pageSize) }}</text>
        <view class="page-btn" :class="{ disabled: page >= Math.ceil(total / pageSize) }"
              @tap="page < Math.ceil(total / pageSize) && loadQuestions(page + 1)">下一页</view>
      </view>
    </scroll-view>

    <!-- 添加按钮 -->
    <view class="fab-btn" @tap="goCreate">
      <text class="fab-icon">＋</text>
    </view>
  </view>
</template>

<script>
import { questionsAPI } from '../../utils/api.js'
import { truncate, formatTime, QUESTION_TYPES } from '../../utils/util.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      questions: [],
      keyword: '',
      selectedType: '',
      page: 1,
      pageSize: 10,
      total: 0,
      loading: false,
      types: QUESTION_TYPES,
    }
  },
  onLoad() {
    const sysInfo = uni.getSystemInfoSync()
    this.statusBarHeight = sysInfo.statusBarHeight || 20
    this.navHeight = this.statusBarHeight + 44
  },
  onShow() {
    this.loadQuestions(1)
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
    async loadQuestions(p) {
      const token = uni.getStorageSync('access_token')
      if (!token) return
      this.page = p || 1
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.keyword) params.keyword = this.keyword
        if (this.selectedType) params.question_type = this.selectedType
        const res = await questionsAPI.list(params)
        this.questions = res.items || []
        this.total = res.total || 0
      } catch (e) {
        // handled
      }
      this.loading = false
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/question-detail/question-detail?id=${id}` })
    },
    goCreate() {
      uni.navigateTo({ url: '/pages/question-edit/question-edit' })
    },
  },
}
</script>

<style lang="scss" scoped>
.questions-page {
  min-height: 100vh;
  background: #F5F6FA;
}
.nav-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: linear-gradient(135deg, #4A6CF7 0%, #6B8AFF 100%);
}
.nav-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
}
.nav-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
}
.scroll-area {
  height: 100vh;
}
.search-bar {
  padding: 20rpx 24rpx 0;
}
.search-input-wrap {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 40rpx;
  padding: 0 24rpx;
  height: 80rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.search-icon { font-size: 28rpx; margin-right: 12rpx; }
.search-input {
  flex: 1;
  font-size: 28rpx;
  height: 80rpx;
}
.clear-btn {
  font-size: 28rpx;
  color: #9CA3AF;
  padding: 8rpx;
}
.filter-bar {
  white-space: nowrap;
  padding: 16rpx 24rpx;
}
.filter-tag {
  display: inline-block;
  padding: 10rpx 24rpx;
  border-radius: 32rpx;
  font-size: 24rpx;
  color: #6B7280;
  background: #fff;
  margin-right: 12rpx;
  border: 2rpx solid transparent;
  &.active {
    color: #4A6CF7;
    border-color: #4A6CF7;
    background: rgba(74,108,247,0.06);
  }
}
.question-list {
  padding: 0 24rpx;
}
.q-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #FAFBFC; }
}
.q-top {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}
.q-type {
  font-size: 22rpx;
  color: #fff;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  font-weight: 500;
}
.q-stars { font-size: 20rpx; }
.star-on { color: #F59E0B; }
.star-off { color: #E5E7EB; }
.q-verified {
  font-size: 22rpx;
  color: #22C55E;
  margin-left: auto;
}
.q-content {
  font-size: 26rpx;
  color: #374151;
  line-height: 1.6;
  display: block;
  margin-bottom: 10rpx;
}
.q-bottom {
  display: flex;
  justify-content: space-between;
}
.q-source { font-size: 22rpx; color: #9CA3AF; }
.q-time { font-size: 22rpx; color: #D1D5DB; }
.q-tags {
  display: flex;
  gap: 8rpx;
  margin-top: 12rpx;
}
.q-tag {
  font-size: 20rpx;
  color: #4A6CF7;
  background: rgba(74,108,247,0.08);
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  padding: 24rpx 0 40rpx;
}
.page-btn {
  padding: 12rpx 28rpx;
  background: #fff;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #4A6CF7;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  &.disabled { color: #D1D5DB; }
}
.page-info { font-size: 26rpx; color: #6B7280; }
.fab-btn {
  position: fixed;
  right: 32rpx;
  bottom: 200rpx;
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #4A6CF7, #6B8AFF);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(74,108,247,0.4);
  z-index: 50;
  &:active { transform: scale(0.95); }
}
.fab-icon {
  font-size: 44rpx;
  color: #fff;
  font-weight: 300;
}
.loading-state {
  text-align: center;
  padding: 60rpx 0;
}
.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid #E5E7EB;
  border-top-color: #4A6CF7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state {
  text-align: center;
  padding: 80rpx 0;
}
.empty-icon { font-size: 48rpx; display: block; margin-bottom: 12rpx; }
.empty-text { font-size: 28rpx; color: #9CA3AF; }
</style>
