<template>
  <view class="practice-page">
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">📝 刷题练习</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 今日数据 -->
      <view class="stats-banner">
        <view class="stats-row">
          <view class="stat-item">
            <text class="stat-num">{{ stats.today_count || 0 }}</text>
            <text class="stat-label">今日已练</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-num">{{ stats.total_questions || 0 }}</text>
            <text class="stat-label">累计做题</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-num">{{ stats.accuracy || 0 }}%</text>
            <text class="stat-label">正确率</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-num">{{ stats.streak_days || 0 }}</text>
            <text class="stat-label">连续天数</text>
          </view>
        </view>
      </view>

      <!-- 刷题模式 -->
      <view class="section-title">选择刷题模式</view>

      <view class="mode-grid">
        <view class="mode-card" @tap="startPractice('sequential')">
          <view class="mode-icon-wrap" style="background: linear-gradient(135deg, #4A6CF7, #6366F1)">
            <text class="mode-icon">📚</text>
          </view>
          <text class="mode-name">顺序刷题</text>
          <text class="mode-desc">按顺序逐题练习</text>
        </view>

        <view class="mode-card" @tap="startPractice('random')">
          <view class="mode-icon-wrap" style="background: linear-gradient(135deg, #38A169, #48BB78)">
            <text class="mode-icon">🎲</text>
          </view>
          <text class="mode-name">随机刷题</text>
          <text class="mode-desc">随机出题防背答案</text>
        </view>

        <view class="mode-card" @tap="startPractice('mistakes')">
          <view class="mode-icon-wrap" style="background: linear-gradient(135deg, #E53E3E, #FC8181)">
            <text class="mode-icon">❌</text>
          </view>
          <text class="mode-name">错题重练</text>
          <text class="mode-desc">重做错过的题目</text>
        </view>

        <view class="mode-card" @tap="goToMistakes">
          <view class="mode-icon-wrap" style="background: linear-gradient(135deg, #ED8936, #F6AD55)">
            <text class="mode-icon">📋</text>
          </view>
          <text class="mode-name">错题本</text>
          <text class="mode-desc">查看所有错题记录</text>
        </view>
      </view>

      <!-- 知识点专项 -->
      <view class="section-title">知识点专项</view>
      <view class="knowledge-list">
        <view v-for="tag in knowledgeTags" :key="tag.id" class="knowledge-item" @tap="startKnowledgePractice(tag)">
          <view class="knowledge-left">
            <text class="knowledge-name">{{ tag.name }}</text>
            <text class="knowledge-count">{{ tag.question_count || 0 }}题</text>
          </view>
          <text class="knowledge-arrow">›</text>
        </view>
        <view v-if="knowledgeTags.length === 0" class="empty-tip">
          <text>暂无知识点标签，请联系老师添加</text>
        </view>
      </view>

      <!-- 学习报告入口 -->
      <view class="report-entry" @tap="goToReport">
        <view class="report-left">
          <text class="report-title">📊 学习报告</text>
          <text class="report-desc">查看详细的学习数据分析</text>
        </view>
        <text class="report-arrow">›</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { practiceAPI, tagsAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      stats: {},
      knowledgeTags: [],
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
    this.loadStats()
    this.loadKnowledgeTags()
  },
  methods: {
    async loadStats() {
      try {
        this.stats = await practiceAPI.getStats()
      } catch (e) {}
    },
    async loadKnowledgeTags() {
      try {
        const res = await tagsAPI.list()
        const allTags = []
        const flatten = (nodes) => {
          for (const n of (nodes || [])) {
            if (n.tag_type === 'knowledge') allTags.push(n)
            if (n.children && n.children.length) flatten(n.children)
          }
        }
        flatten(res || [])
        this.knowledgeTags = allTags.slice(0, 10)
      } catch (e) {}
    },
    startPractice(mode) {
      if (mode === 'mistakes') {
        this.goToMistakes()
        return
      }
      uni.navigateTo({
        url: `/pages/practice/question?mode=${mode}`
      })
    },
    startKnowledgePractice(tag) {
      uni.navigateTo({
        url: `/pages/practice/question?mode=knowledge&tag_id=${tag.id}&tag_name=${tag.name}`
      })
    },
    goToMistakes() {
      uni.navigateTo({ url: '/pages/mistakes/list' })
    },
    goToReport() {
      uni.navigateTo({ url: '/pages/report/index' })
    },
  },
}
</script>

<style lang="scss" scoped>
.practice-page {
  min-height: 100vh;
  background: #F7FAFC;
}
.nav-bar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: linear-gradient(135deg, #2B6CB0, #3182CE);
}
.nav-content { height: 88rpx; display: flex; align-items: center; padding: 0 32rpx; }
.nav-title { font-size: 34rpx; font-weight: 700; color: #fff; }
.scroll-area { height: 100vh; }

/* 今日数据 */
.stats-banner {
  margin: 20rpx 24rpx; background: #fff; border-radius: 20rpx;
  padding: 28rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.stats-row { display: flex; align-items: center; }
.stat-item { flex: 1; text-align: center; }
.stat-num { display: block; font-size: 36rpx; font-weight: 700; color: #2B6CB0; }
.stat-label { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }
.stat-divider { width: 1rpx; height: 48rpx; background: #E2E8F0; }

.section-title {
  font-size: 30rpx; font-weight: 700; color: #1E293B;
  padding: 20rpx 24rpx 12rpx;
}

/* 模式卡片 */
.mode-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx;
  padding: 0 24rpx;
}
.mode-card {
  background: #fff; border-radius: 20rpx; padding: 28rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { transform: scale(0.97); }
}
.mode-icon-wrap {
  width: 72rpx; height: 72rpx; border-radius: 18rpx;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16rpx;
}
.mode-icon { font-size: 36rpx; }
.mode-name { display: block; font-size: 28rpx; font-weight: 600; color: #1E293B; }
.mode-desc { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }

/* 知识点 */
.knowledge-list {
  margin: 0 24rpx; background: #fff; border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.knowledge-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #F1F5F9;
  &:last-child { border-bottom: none; }
  &:active { background: #F8FAFC; }
}
.knowledge-left { flex: 1; }
.knowledge-name { display: block; font-size: 28rpx; color: #1E293B; font-weight: 500; }
.knowledge-count { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }
.knowledge-arrow { font-size: 32rpx; color: #CBD5E1; }
.empty-tip { text-align: center; padding: 40rpx; font-size: 26rpx; color: #94A3B8; }

/* 学习报告入口 */
.report-entry {
  display: flex; align-items: center; justify-content: space-between;
  margin: 20rpx 24rpx 40rpx; background: #fff; border-radius: 20rpx;
  padding: 32rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #F8FAFC; }
}
.report-title { display: block; font-size: 30rpx; font-weight: 600; color: #1E293B; }
.report-desc { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }
.report-arrow { font-size: 32rpx; color: #CBD5E1; }
</style>
