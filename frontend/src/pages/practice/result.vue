<template>
  <view class="result-page">
    <!-- 结果卡片 -->
    <view class="result-card">
      <view class="result-circle" :class="accuracy >= 80 ? 'great' : accuracy >= 60 ? 'good' : 'need-work'">
        <text class="result-percent">{{ accuracy }}%</text>
        <text class="result-label">正确率</text>
      </view>
      <view class="result-stats">
        <view class="rs-item">
          <text class="rs-num correct-num">{{ correct }}</text>
          <text class="rs-label">正确</text>
        </view>
        <view class="rs-divider"></view>
        <view class="rs-item">
          <text class="rs-num wrong-num">{{ total - correct }}</text>
          <text class="rs-label">错误</text>
        </view>
        <view class="rs-divider"></view>
        <view class="rs-item">
          <text class="rs-num time-num">{{ formatTime(time) }}</text>
          <text class="rs-label">用时</text>
        </view>
      </view>

      <!-- 评语 -->
      <view class="result-msg">
        <text v-if="accuracy >= 90">🎉 太棒了！继续保持！</text>
        <text v-else-if="accuracy >= 70">👍 做得不错，继续加油！</text>
        <text v-else-if="accuracy >= 50">💪 还需多练习，加油！</text>
        <text v-else>📖 建议回顾知识点后再练习</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-btns">
      <view class="action-btn retry" @tap="retryAll">
        <text>🔄 全部重做</text>
      </view>
      <view class="action-btn home" @tap="goHome">
        <text>🏠 返回首页</text>
      </view>
    </view>

    <!-- 查看错题 -->
    <view v-if="total - correct > 0" class="mistake-hint" @tap="goMistakes">
      <text class="hint-text">查看 {{ total - correct }} 道错题的解析 →</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      total: 0,
      correct: 0,
      time: 0,
    }
  },
  computed: {
    accuracy() {
      return this.total > 0 ? Math.round(this.correct / this.total * 100) : 0
    },
  },
  onLoad(options) {
    this.total = parseInt(options.total) || 0
    this.correct = parseInt(options.correct) || 0
    this.time = parseInt(options.time) || 0
  },
  methods: {
    retryAll() {
      uni.navigateBack()
    },
    goHome() {
      uni.switchTab({ url: '/pages/index/index' })
    },
    goMistakes() {
      uni.navigateTo({ url: '/pages/mistakes/list' })
    },
    formatTime(s) {
      const m = Math.floor(s / 60)
      const sec = s % 60
      return `${m}:${String(sec).padStart(2, '0')}`
    },
  },
}
</script>

<style lang="scss" scoped>
.result-page {
  min-height: 100vh; background: #F7FAFC;
  display: flex; flex-direction: column; align-items: center;
  padding: 60rpx 32rpx;
}
.result-card {
  width: 100%; background: #fff; border-radius: 24rpx;
  padding: 48rpx 32rpx; text-align: center;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.06);
}
.result-circle {
  width: 200rpx; height: 200rpx; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  margin: 0 auto 32rpx;
  &.great { background: rgba(56,161,105,0.1); border: 6rpx solid #38A169; }
  &.good { background: rgba(43,108,176,0.1); border: 6rpx solid #2B6CB0; }
  &.need-work { background: rgba(229,62,62,0.1); border: 6rpx solid #E53E3E; }
}
.result-percent { font-size: 48rpx; font-weight: 800; color: #1E293B; }
.result-label { font-size: 22rpx; color: #64748B; }
.result-stats {
  display: flex; justify-content: center; gap: 48rpx;
  margin: 32rpx 0;
}
.rs-item { text-align: center; }
.rs-num { display: block; font-size: 36rpx; font-weight: 700; }
.correct-num { color: #38A169; }
.wrong-num { color: #E53E3E; }
.time-num { color: #2B6CB0; }
.rs-label { display: block; font-size: 22rpx; color: #94A3B8; margin-top: 4rpx; }
.result-msg {
  font-size: 28rpx; color: #475569; margin-top: 24rpx;
}
.action-btns {
  display: flex; gap: 20rpx; width: 100%; margin-top: 32rpx;
}
.action-btn {
  flex: 1; text-align: center; padding: 24rpx 0;
  border-radius: 14rpx; font-size: 28rpx; font-weight: 600;
  &.retry { background: #2B6CB0; color: #fff; }
  &.home { background: #F1F5F9; color: #475569; }
  &:active { opacity: 0.85; }
}
.mistake-hint {
  margin-top: 32rpx; padding: 24rpx;
  text-align: center;
}
.hint-text { font-size: 28rpx; color: #2B6CB0; font-weight: 500; }
</style>
