<template>
  <view class="detail-page" v-if="question">
    <view class="q-header-card">
      <view class="q-meta">
        <view class="q-type" :style="{ background: getTypeColor(question.question_type) }">
          {{ getTypeName(question.question_type) }}
        </view>
        <view class="q-stars">
          <text v-for="i in 5" :key="i" :class="i <= question.difficulty ? 'star-on' : 'star-off'">★</text>
        </view>
      </view>
      <text class="q-source" v-if="question.source">来源：{{ question.source }}</text>
    </view>

    <view class="content-card">
      <text class="card-title">题目内容</text>
      <text class="card-body">{{ question.content }}</text>
    </view>

    <view class="content-card" v-if="question.images && question.images.length">
      <text class="card-title">题目附图</text>
      <scroll-view scroll-x class="figure-scroll">
        <view
          v-for="(img, idx) in question.images"
          :key="img.id || idx"
          class="figure-card"
          @tap="previewFigure(img.image_url)"
        >
          <image :src="img.image_url" class="figure-image" mode="aspectFit" />
          <text class="figure-type">{{ img.image_type || '附图' }}</text>
        </view>
      </scroll-view>
    </view>

    <view class="content-card" v-if="question.options && question.options.length">
      <text class="card-title">选项</text>
      <view v-for="opt in question.options" :key="opt.label" class="option-item">
        <view class="opt-label">{{ opt.label }}</view>
        <text class="opt-text">{{ opt.text }}</text>
      </view>
    </view>

    <view class="content-card answer-card">
      <text class="card-title">答案</text>
      <text class="card-body answer-text">{{ question.answer || '暂无答案' }}</text>
    </view>

    <view class="content-card" v-if="question.analysis">
      <text class="card-title">解析</text>
      <text class="card-body">{{ question.analysis }}</text>
    </view>

    <view class="content-card" v-if="question.tags && question.tags.length">
      <text class="card-title">标签</text>
      <view class="tag-list">
        <text class="tag-item" v-for="tag in question.tags" :key="tag.id">{{ tag.name }}</text>
      </view>
    </view>

    <view class="bottom-actions safe-area-bottom">
      <view class="action-btn btn-edit" @tap="goEdit">编辑</view>
      <view class="action-btn btn-delete" @tap="handleDelete">删除</view>
    </view>
  </view>
</template>

<script>
import { questionsAPI } from '../../utils/api.js'
import { QUESTION_TYPES } from '../../utils/util.js'

export default {
  data() {
    return {
      questionId: '',
      question: null,
    }
  },
  onLoad(options) {
    this.questionId = options.id
    this.loadQuestion()
  },
  methods: {
    getTypeName(type) {
      return QUESTION_TYPES[type]?.label || type
    },
    getTypeColor(type) {
      return QUESTION_TYPES[type]?.color || '#6B7280'
    },
    async loadQuestion() {
      try {
        this.question = await questionsAPI.detail(this.questionId)
      } catch (error) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    previewFigure(url) {
      uni.previewImage({ urls: [url], current: url })
    },
    goEdit() {
      uni.navigateTo({ url: `/pages/question-edit/question-edit?id=${this.questionId}` })
    },
    handleDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这道题目吗？此操作不可撤销。',
        confirmColor: '#EF4444',
        success: async (res) => {
          if (!res.confirm) return
          try {
            await questionsAPI.delete(this.questionId)
            uni.showToast({ title: '已删除', icon: 'success' })
            setTimeout(() => uni.navigateBack(), 500)
          } catch (error) {}
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background: #F5F6FA;
  padding: 24rpx;
  padding-bottom: 140rpx;
}

.q-header-card,
.content-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.q-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 8rpx;
}

.q-type {
  font-size: 24rpx;
  color: #fff;
  padding: 6rpx 20rpx;
  border-radius: 10rpx;
  font-weight: 500;
}

.q-stars {
  font-size: 22rpx;
}

.star-on {
  color: #F59E0B;
}

.star-off {
  color: #E5E7EB;
}

.q-source {
  font-size: 24rpx;
  color: #9CA3AF;
}

.answer-card {
  border-left: 6rpx solid #22C55E;
}

.card-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 16rpx;
}

.card-body {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.8;
  white-space: pre-wrap;
}

.answer-text {
  color: #059669;
  font-weight: 600;
}

.figure-scroll {
  white-space: nowrap;
}

.figure-card {
  display: inline-block;
  width: 280rpx;
  height: 280rpx;
  margin-right: 16rpx;
  background: #F3F4F6;
  border-radius: 12rpx;
  position: relative;
  overflow: hidden;
}

.figure-image {
  width: 100%;
  height: 100%;
}

.figure-type {
  position: absolute;
  bottom: 8rpx;
  left: 8rpx;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 20rpx;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
}

.option-item:last-child {
  border-bottom: none;
}

.opt-label {
  width: 48rpx;
  height: 48rpx;
  background: #4A6CF7;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 600;
  line-height: 48rpx;
  flex-shrink: 0;
}

.opt-text {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.6;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-item {
  font-size: 24rpx;
  color: #4A6CF7;
  background: rgba(74, 108, 247, 0.08);
  padding: 8rpx 20rpx;
  border-radius: 10rpx;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 20rpx;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.action-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
}

.btn-edit {
  background: linear-gradient(135deg, #4A6CF7, #6B8AFF);
  color: #fff;
}

.btn-delete {
  background: #FEE2E2;
  color: #EF4444;
}
</style>
