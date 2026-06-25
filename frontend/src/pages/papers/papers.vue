<template>
  <view class="papers-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">📄 试卷管理</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <view v-if="loading" class="loading-state">
        <view class="loading-spinner"></view>
      </view>
      <view v-else-if="papers.length === 0" class="empty-state">
        <text class="empty-icon">📄</text>
        <text class="empty-text">暂无试卷</text>
        <text class="empty-hint">点击下方按钮创建试卷</text>
      </view>
      <view v-else class="paper-list">
        <view v-for="p in papers" :key="p.id" class="paper-card" @tap="goDetail(p.id)">
          <view class="paper-header">
            <text class="paper-title">{{ p.title }}</text>
            <text class="paper-date">{{ formatTime(p.created_at) }}</text>
          </view>
          <text class="paper-subtitle" v-if="p.subtitle">{{ p.subtitle }}</text>
          <view class="paper-stats">
            <view class="stat">
              <text class="stat-value">{{ p.total_score }}</text>
              <text class="stat-label">总分</text>
            </view>
            <view class="stat">
              <text class="stat-value">{{ p.exam_duration }}</text>
              <text class="stat-label">分钟</text>
            </view>
            <view class="stat">
              <text class="stat-value">{{ p.question_count || '—' }}</text>
              <text class="stat-label">题目数</text>
            </view>
          </view>
          <view class="paper-actions">
            <view class="paper-action" @tap="exportAndShare(p)">
              <text>📤 导出Word</text>
            </view>
            <view class="paper-action danger" @tap="handleDelete(p.id)">
              <text>🗑️ 删除</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 分页 -->
      <view class="pagination" v-if="total > pageSize">
        <view class="page-btn" :class="{ disabled: page <= 1 }" @tap="page > 1 && loadPapers(page - 1)">上一页</view>
        <text class="page-info">{{ page }} / {{ Math.ceil(total / pageSize) }}</text>
        <view class="page-btn" :class="{ disabled: page >= Math.ceil(total / pageSize) }"
              @tap="page < Math.ceil(total / pageSize) && loadPapers(page + 1)">下一页</view>
      </view>
    </scroll-view>

    <!-- 创建按钮 -->
    <view class="fab-btn" @tap="goCreate">
      <text class="fab-icon">＋</text>
    </view>
  </view>
</template>

<script>
import { papersAPI, exportAPI, buildDownloadUrl } from '../../utils/api.js'
import { buildWordFileName, exportWordToWechat } from '../../utils/export-word.js'
import { formatRelativeTime as formatTime } from '../../utils/time.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      papers: [],
      page: 1,
      pageSize: 10,
      total: 0,
      loading: false,
      exporting: false,
    }
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
    this.loadPapers(1)
  },
  methods: {
    formatTime,
    async loadPapers(p) {
      const token = uni.getStorageSync('access_token')
      if (!token) return
      this.page = p || 1
      this.loading = true
      try {
        const res = await papersAPI.list({ page: this.page, page_size: this.pageSize })
        this.papers = res.items || []
        this.total = res.total || 0
      } catch (e) {}
      this.loading = false
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/paper-detail/paper-detail?id=${id}` })
    },
    goCreate() {
      uni.navigateTo({ url: '/pages/paper-create/paper-create' })
    },
    async exportAndShare(paper) {
      if (this.exporting) return
      this.exporting = true
      uni.showLoading({ title: '正在生成Word...' })
      let rawUrl = ''
      let exportFailed = false
      try {
        const res = await exportAPI.paperWord(paper.id)
        rawUrl = res.test_paper_url || res.answer_sheet_url
      } catch (e) {
        exportFailed = true
      } finally {
        uni.hideLoading()
        this.exporting = false
      }

      const url = buildDownloadUrl(rawUrl)
      if (exportFailed || !url) {
        uni.showToast({ title: '导出失败', icon: 'none' })
        return
      }

      try {
        await exportWordToWechat({
          url,
          fileName: buildWordFileName(paper && paper.title, '试卷'),
        })
      } catch (err) {
        console.log('Word转发失败:', JSON.stringify(err))
        uni.showToast({ title: 'Word转发失败', icon: 'none' })
      }
    },
    handleDelete(id) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这份试卷吗？',
        confirmColor: '#EF4444',
        success: async (res) => {
          if (res.confirm) {
            try {
              await papersAPI.delete(id)
              uni.showToast({ title: '已删除', icon: 'success' })
              this.loadPapers(this.page)
            } catch (e) {}
          }
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.papers-page {
  min-height: 100vh;
  background: #F5F6FA;
}
.nav-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
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
.paper-list {
  padding: 24rpx;
}
.paper-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8rpx;
}
.paper-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2937;
  flex: 1;
}
.paper-date {
  font-size: 22rpx;
  color: #D1D5DB;
  margin-left: 16rpx;
}
.paper-subtitle {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
  margin-bottom: 16rpx;
}
.paper-stats {
  display: flex;
  gap: 32rpx;
  padding: 20rpx 0;
  border-top: 1rpx solid #F3F4F6;
  border-bottom: 1rpx solid #F3F4F6;
  margin-bottom: 16rpx;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stat-value {
  font-size: 32rpx;
  font-weight: 700;
  color: #F59E0B;
}
.stat-label {
  font-size: 22rpx;
  color: #9CA3AF;
}
.paper-actions {
  display: flex;
  gap: 16rpx;
}
.paper-action {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  border-radius: 12rpx;
  font-size: 24rpx;
  background: #F3F4F6;
  color: #4A6CF7;
  &.danger {
    color: #EF4444;
    background: #FEE2E2;
  }
}
.loading-state { text-align: center; padding: 80rpx 0; }
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid #E5E7EB; border-top-color: #F59E0B;
  border-radius: 50%; animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state { text-align: center; padding: 100rpx 0; }
.empty-icon { font-size: 56rpx; display: block; margin-bottom: 16rpx; }
.empty-text { display: block; font-size: 30rpx; color: #9CA3AF; }
.empty-hint { display: block; font-size: 24rpx; color: #D1D5DB; margin-top: 8rpx; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 24rpx; padding: 24rpx 0 40rpx; }
.page-btn { padding: 12rpx 28rpx; background: #fff; border-radius: 12rpx; font-size: 26rpx; color: #F59E0B; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); &.disabled { color: #D1D5DB; } }
.page-info { font-size: 26rpx; color: #6B7280; }
.fab-btn {
  position: fixed; right: 32rpx; bottom: 200rpx;
  width: 100rpx; height: 100rpx;
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(245,158,11,0.4);
  z-index: 50;
  &:active { transform: scale(0.95); }
}
.fab-icon { font-size: 44rpx; color: #fff; font-weight: 300; }
</style>
