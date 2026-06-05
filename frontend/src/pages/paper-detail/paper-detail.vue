<template>
  <view class="detail-page" v-if="paper">
    <view class="paper-header-card">
      <text class="paper-title">{{ paper.title }}</text>
      <text class="paper-subtitle" v-if="paper.subtitle">{{ paper.subtitle }}</text>
      <view class="paper-meta">
        <view class="meta-item">
          <text class="meta-label">总分</text>
          <text class="meta-value">{{ paper.total_score }}</text>
        </view>
        <view class="meta-item">
          <text class="meta-label">时长</text>
          <text class="meta-value">{{ paper.exam_duration }}分钟</text>
        </view>
        <view class="meta-item">
          <text class="meta-label">题数</text>
          <text class="meta-value">{{ paper.sections?.length || 0 }}</text>
        </view>
      </view>
    </view>

    <!-- 题目列表 -->
    <view v-for="(item, index) in (paper.sections || [])" :key="index" class="question-card">
      <view class="q-index">{{ index + 1 }}</view>
      <view class="q-body">
        <view class="q-top">
          <view class="q-type" :style="{ background: getTypeColor(item.question?.question_type) }">
            {{ getTypeName(item.question?.question_type) }}
          </view>
          <text class="q-score">{{ item.score }}分</text>
        </view>
        <text class="q-content">{{ truncate(item.question?.content, 100) }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-area">
      <view class="btn-action btn-download" @tap="downloadWord">
        <text>📥 导出 Word 试卷</text>
      </view>
      <view class="btn-action btn-answer" @tap="downloadAnswer">
        <text>📋 导出答案</text>
      </view>
    </view>
  </view>
</template>

<script>
import { papersAPI, exportAPI } from '../../utils/api.js'
import { truncate, QUESTION_TYPES } from '../../utils/util.js'

export default {
  data() {
    return {
      paperId: '',
      paper: null,
      exporting: false,
    }
  },
  onLoad(options) {
    this.paperId = options.id
    this.loadPaper()
  },
  methods: {
    truncate,
    getTypeName(type) { return QUESTION_TYPES[type]?.label || type || '' },
    getTypeColor(type) { return QUESTION_TYPES[type]?.color || '#6B7280' },
    async loadPaper() {
      try {
        this.paper = await papersAPI.detail(this.paperId)
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    async downloadWord() {
      if (this.exporting) return
      this.exporting = true
      uni.showLoading({ title: '正在生成Word...' })
      try {
        const res = await exportAPI.paperWord(this.paperId)
        uni.hideLoading()
        if (res.test_paper_url) {
          this.paper.word_url = res.test_paper_url
          this.doDownload(res.test_paper_url)
        }
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: '导出失败', icon: 'none' })
      }
      this.exporting = false
    },
    async downloadAnswer() {
      if (this.exporting) return
      this.exporting = true
      uni.showLoading({ title: '正在生成答案...' })
      try {
        const res = await exportAPI.paperWord(this.paperId)
        uni.hideLoading()
        if (res.answer_sheet_url) {
          this.paper.answer_word_url = res.answer_sheet_url
          this.doDownload(res.answer_sheet_url)
        }
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: '导出失败', icon: 'none' })
      }
      this.exporting = false
    },
    doDownload(url) {
      uni.downloadFile({
        url,
        success: (res) => {
          if (res.statusCode === 200) {
            uni.openDocument({ filePath: res.tempFilePath, fileType: 'docx', showMenu: true })
          }
        },
        fail: () => {
          uni.showToast({ title: '下载失败', icon: 'none' })
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
  padding-bottom: 200rpx;
}
.paper-header-card {
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
  border-radius: 24rpx;
  padding: 36rpx;
  color: #fff;
  margin-bottom: 24rpx;
}
.paper-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  margin-bottom: 8rpx;
}
.paper-subtitle {
  display: block;
  font-size: 26rpx;
  opacity: 0.85;
  margin-bottom: 20rpx;
}
.paper-meta {
  display: flex;
  gap: 40rpx;
}
.meta-item { display: flex; flex-direction: column; align-items: center; }
.meta-label { font-size: 22rpx; opacity: 0.8; }
.meta-value { font-size: 32rpx; font-weight: 700; }
.question-card {
  display: flex;
  gap: 16rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.q-index {
  width: 48rpx;
  height: 48rpx;
  background: #F59E0B;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 700;
  text-align: center;
  line-height: 48rpx;
  flex-shrink: 0;
}
.q-body { flex: 1; }
.q-top {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}
.q-type {
  font-size: 22rpx;
  color: #fff;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
}
.q-score {
  font-size: 22rpx;
  color: #F59E0B;
  font-weight: 600;
  margin-left: auto;
}
.q-content {
  font-size: 26rpx;
  color: #374151;
  line-height: 1.6;
}
.action-area {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  display: flex;
  gap: 16rpx;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.btn-action {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
}
.btn-download { background: linear-gradient(135deg, #F59E0B, #FBBF24); color: #fff; }
.btn-answer { background: #F3F4F6; color: #374151; }
</style>
