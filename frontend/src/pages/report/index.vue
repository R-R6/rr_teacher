<template>
  <view class="report-page">
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <view class="nav-back" @tap="goBack">‹</view>
        <text class="nav-title">📊 学习报告</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 核心数据 -->
      <view class="data-cards">
        <view class="data-card">
          <text class="dc-num">{{ stats.total_questions || 0 }}</text>
          <text class="dc-label">做题总量</text>
        </view>
        <view class="data-card">
          <text class="dc-num" :class="stats.accuracy >= 80 ? 'green' : stats.accuracy >= 60 ? 'blue' : 'red'">
            {{ stats.accuracy || 0 }}%
          </text>
          <text class="dc-label">正确率</text>
        </view>
        <view class="data-card">
          <text class="dc-num">{{ stats.total_minutes || 0 }}min</text>
          <text class="dc-label">学习时长</text>
        </view>
        <view class="data-card">
          <text class="dc-num">{{ stats.streak_days || 0 }}</text>
          <text class="dc-label">连续天数</text>
        </view>
      </view>

      <!-- 正确率趋势 -->
      <view class="section-card">
        <text class="sec-title">📈 近7天正确率趋势</text>
        <view class="trend-chart">
          <view v-for="item in trend" :key="item.date" class="trend-item">
            <view class="trend-bar-wrap">
              <view class="trend-bar" :style="{ height: item.accuracy + '%' }">
                <text class="trend-val">{{ item.accuracy }}%</text>
              </view>
            </view>
            <text class="trend-date">{{ item.date }}</text>
            <text class="trend-count">{{ item.total }}题</text>
          </view>
        </view>
      </view>

      <!-- 错题统计 -->
      <view class="section-card">
        <text class="sec-title">📋 错题概览</text>
        <view class="mistake-stats">
          <view class="ms-item">
            <text class="ms-num">{{ mistakeStats.total || 0 }}</text>
            <text class="ms-label">总错题</text>
          </view>
          <view class="ms-item">
            <text class="ms-num" style="color: #38A169">{{ mistakeStats.mastered || 0 }}</text>
            <text class="ms-label">已掌握</text>
          </view>
          <view class="ms-item">
            <text class="ms-num" style="color: #E53E3E">{{ mistakeStats.unmastered || 0 }}</text>
            <text class="ms-label">待复习</text>
          </view>
        </view>
        <!-- 掌握进度条 -->
        <view class="progress-wrap" v-if="mistakeStats.total > 0">
          <view class="progress-bg">
            <view class="progress-fill" :style="{ width: masteryPercent + '%' }"></view>
          </view>
          <text class="progress-text">掌握率 {{ masteryPercent }}%</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { practiceAPI, mistakesAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      stats: {},
      trend: [],
      mistakeStats: {},
    }
  },
  computed: {
    masteryPercent() {
      const total = this.mistakeStats.total || 0
      const mastered = this.mistakeStats.mastered || 0
      return total > 0 ? Math.round(mastered / total * 100) : 0
    },
  },
  onLoad() {
    try {
      const sysInfo = uni.getSystemInfoSync()
      this.statusBarHeight = sysInfo.statusBarHeight || 20
    } catch (e) { this.statusBarHeight = 20 }
    this.navHeight = this.statusBarHeight + 44
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [stats, trend, mistakeStats] = await Promise.all([
          practiceAPI.getStats(),
          practiceAPI.getTrend(7),
          mistakesAPI.getStats(),
        ])
        this.stats = stats
        this.trend = trend.trend || []
        this.mistakeStats = mistakeStats
      } catch (e) {}
    },
    goBack() { uni.navigateBack() },
  },
}
</script>

<style lang="scss" scoped>
.report-page { min-height: 100vh; background: #F7FAFC; }
.nav-bar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: linear-gradient(135deg, #2B6CB0, #3182CE);
}
.nav-content { height: 88rpx; display: flex; align-items: center; padding: 0 32rpx; }
.nav-back { font-size: 40rpx; color: #fff; padding-right: 16rpx; }
.nav-title { font-size: 34rpx; font-weight: 700; color: #fff; }
.scroll-area { height: 100vh; }

/* 数据卡片 */
.data-cards {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx;
  padding: 20rpx 24rpx;
}
.data-card {
  background: #fff; border-radius: 16rpx; padding: 24rpx; text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.dc-num { display: block; font-size: 40rpx; font-weight: 800; color: #1E293B; }
.dc-num.green { color: #38A169; }
.dc-num.blue { color: #2B6CB0; }
.dc-num.red { color: #E53E3E; }
.dc-label { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }

/* 区块 */
.section-card {
  margin: 0 24rpx 20rpx; background: #fff; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.sec-title { display: block; font-size: 28rpx; font-weight: 600; color: #1E293B; margin-bottom: 20rpx; }

/* 趋势图 */
.trend-chart {
  display: flex; gap: 8rpx; align-items: flex-end; height: 240rpx;
  padding-bottom: 40rpx; position: relative;
}
.trend-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
.trend-bar-wrap {
  width: 100%; height: 180rpx; display: flex; align-items: flex-end;
  justify-content: center;
}
.trend-bar {
  width: 48rpx; min-height: 8rpx; background: linear-gradient(180deg, #2B6CB0, #63B3ED);
  border-radius: 8rpx 8rpx 0 0; position: relative;
  display: flex; align-items: flex-start; justify-content: center;
}
.trend-val {
  font-size: 18rpx; color: #2B6CB0; font-weight: 600;
  position: absolute; top: -28rpx;
}
.trend-date { font-size: 20rpx; color: #64748B; margin-top: 8rpx; }
.trend-count { font-size: 18rpx; color: #94A3B8; }

/* 错题统计 */
.mistake-stats {
  display: flex; gap: 24rpx; margin-bottom: 20rpx;
}
.ms-item { flex: 1; text-align: center; }
.ms-num { display: block; font-size: 36rpx; font-weight: 700; color: #1E293B; }
.ms-label { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }
.progress-wrap { display: flex; align-items: center; gap: 12rpx; }
.progress-bg { flex: 1; height: 12rpx; background: #F1F5F9; border-radius: 6rpx; overflow: hidden; }
.progress-fill { height: 100%; background: #38A169; border-radius: 6rpx; transition: width 0.5s; }
.progress-text { font-size: 22rpx; color: #64748B; white-space: nowrap; }
</style>
