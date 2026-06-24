<template>
  <view class="detail-page" v-if="paper">
    <!-- 试卷概览卡片 -->
    <view class="overview-card">
      <text class="ov-title">{{ paper.title }}</text>
      <text class="ov-subtitle" v-if="paper.subtitle">{{ paper.subtitle }}</text>
      <view class="ov-stats">
        <view class="ov-stat">
          <text class="ov-num">{{ paper.total_score }}</text>
          <text class="ov-label">总分</text>
        </view>
        <view class="ov-divider"></view>
        <view class="ov-stat">
          <text class="ov-num">{{ questions.length }}</text>
          <text class="ov-label">题数</text>
        </view>
        <view class="ov-divider"></view>
        <view class="ov-stat">
          <text class="ov-num">{{ paper.exam_duration }}</text>
          <text class="ov-label">分钟</text>
        </view>
        <view class="ov-divider"></view>
        <view class="ov-stat">
          <text class="ov-num">{{ avgDifficulty }}</text>
          <text class="ov-label">均难度</text>
        </view>
      </view>
    </view>

    <!-- 题型分布 -->
    <view class="section-card">
      <text class="sec-title">📊 题型分布</text>
      <view class="type-bars">
        <view v-for="(info, type) in typeDistribution" :key="type" class="type-bar-row">
          <view class="type-bar-left">
            <view class="type-dot" :style="{ background: info.color }"></view>
            <text class="type-name">{{ info.label }}</text>
            <text class="type-count">{{ info.count }}题</text>
          </view>
          <view class="type-bar-right">
            <view class="type-bar-bg">
              <view class="type-bar-fill" :style="{ width: info.percent + '%', background: info.color }"></view>
            </view>
            <text class="type-percent">{{ info.percent }}%</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 难度分布 -->
    <view class="section-card">
      <text class="sec-title">⭐ 难度分布</text>
      <view class="type-bars">
        <view v-for="i in 5" :key="i" class="type-bar-row">
          <view class="type-bar-left">
            <view class="type-dot" :style="{ background: diffColors[i-1] }"></view>
            <text class="type-name">{{ diffLabels[i-1] }}</text>
            <text class="type-count">{{ getDiffCount(i) }}题</text>
          </view>
          <view class="type-bar-right">
            <view class="type-bar-bg">
              <view class="type-bar-fill" :style="{ width: getDiffPercent(i) + '%', background: diffColors[i-1] }"></view>
            </view>
            <text class="type-percent">{{ getDiffPercent(i) }}%</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 答案显示开关 -->
    <view class="toggle-bar">
      <text class="toggle-label">👁 显示答案</text>
      <switch :checked="showAnswers" @change="showAnswers = !showAnswers" color="#4A6CF7" />
    </view>

    <!-- 按题型分组展示题目 -->
    <view v-for="(group, type) in groupedQuestions" :key="type" class="group-card">
      <view class="group-header" @tap="toggleGroup(type)">
        <view class="group-left">
          <view class="group-icon" :style="{ background: getTypeColor(type) }">
            {{ getTypeIcon(type) }}
          </view>
          <view class="group-info">
            <text class="group-type">{{ getTypeName(type) }}</text>
            <text class="group-meta">{{ group.length }}题 · {{ getGroupScore(group) }}分</text>
          </view>
        </view>
        <text class="group-arrow">{{ expandedGroups[type] ? '▾' : '▸' }}</text>
      </view>

      <view v-if="expandedGroups[type]" class="group-body">
        <view v-for="(q, idx) in group" :key="q.id" class="q-card">
          <view class="q-header">
            <text class="q-index">{{ q._globalIndex }}</text>
            <view class="q-score-badge">{{ q._score }}分</view>
            <view class="q-diff-badge" :style="{ background: diffColors[q.difficulty - 1] }">
              {{ diffLabels[q.difficulty - 1] }}
            </view>
          </view>
          <text class="q-content">{{ q.content }}</text>
          <view v-if="q.options && q.options.length" class="q-options">
            <text v-for="opt in q.options" :key="opt.label" class="q-opt">
              {{ opt.label }}. {{ opt.text }}
            </text>
          </view>
          <view v-if="showAnswers" class="q-answer">
            <text class="q-answer-label">答案：</text>
            <text class="q-answer-text">{{ q.answer }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="action-bar safe-area-bottom">
      <view class="action-btn btn-export" @tap="showExportModal = true">
        <text>📥 导出 Word</text>
      </view>
    </view>

    <!-- 导出弹窗 -->
    <view v-if="showExportModal" class="modal-mask" @tap="showExportModal = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">选择导出格式</text>

        <view :class="['format-option', exportFormat === 'a4' ? 'active' : '']" @tap="exportFormat = 'a4'">
          <view class="format-icon">📄</view>
          <view class="format-info">
            <text class="format-name">A4 标准</text>
            <text class="format-desc">适合常规打印（推荐）</text>
          </view>
          <view v-if="exportFormat === 'a4'" class="format-check">✓</view>
        </view>

        <view :class="['format-option', exportFormat === 'a3' ? 'active' : '']" @tap="exportFormat = 'a3'">
          <view class="format-icon">📄</view>
          <view class="format-info">
            <text class="format-name">A3 对折</text>
            <text class="format-desc">双栏排版，适合考试用纸</text>
          </view>
          <view v-if="exportFormat === 'a3'" class="format-check">✓</view>
        </view>

        <view class="export-options">
          <label class="export-check">
            <switch :checked="includeAnswer" @change="includeAnswer = !includeAnswer" color="#4A6CF7" />
            <text>包含答案卷</text>
          </label>
        </view>

        <view class="modal-actions">
          <view class="modal-btn cancel" @tap="showExportModal = false">取消</view>
          <view class="modal-btn confirm" @tap="doExport">确认导出</view>
        </view>
      </view>
    </view>
  </view>

  <!-- 加载状态 -->
  <view v-else class="loading-page">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>
</template>

<script>
import { papersAPI, exportAPI, buildDownloadUrl } from '../../utils/api.js'
import { buildWordFileName, exportWordToWechat } from '../../utils/export-word.js'
import { QUESTION_TYPES, DIFFICULTY_LEVELS, latexToUnicode } from '../../utils/util.js'

export default {
  data() {
    return {
      paperId: '',
      paper: null,
      questions: [],
      showAnswers: false,
      expandedGroups: {},
      showExportModal: false,
      exportFormat: 'a4',
      includeAnswer: true,
      exporting: false,
      _diffPercents: {},
      diffLabels: ['极易', '较易', '中等', '较难', '极难'],
      diffColors: ['#22C55E', '#84CC16', '#F59E0B', '#F97316', '#EF4444'],
    }
  },
  computed: {
    avgDifficulty() {
      if (!this.questions.length) return '-'
      const avg = this.questions.reduce((s, q) => s + q.difficulty, 0) / this.questions.length
      return avg.toFixed(1)
    },
    typeDistribution() {
      const dist = {}
      for (const q of this.questions) {
        const t = q.question_type
        if (!dist[t]) dist[t] = { count: 0, score: 0, ...QUESTION_TYPES[t] }
        dist[t].count++
        dist[t].score += (q._score || 0)
      }
      // 智能取整保证总和100%
      const types = Object.keys(dist)
      const total = this.questions.length || 1
      const raw = types.map(t => dist[t].count / total * 100)
      const floored = raw.map(v => Math.floor(v))
      const remainders = raw.map((v, i) => ({ i, r: v - floored[i] }))
      remainders.sort((a, b) => b.r - a.r)
      let sum = floored.reduce((a, b) => a + b, 0)
      for (let k = 0; k < 100 - sum; k++) floored[remainders[k].i]++
      types.forEach((t, i) => { dist[t].percent = floored[i] })
      return dist
    },
    groupedQuestions() {
      const groups = {}
      let globalIdx = 0
      for (const q of this.questions) {
        const t = q.question_type
        if (!groups[t]) groups[t] = []
        globalIdx++
        groups[t].push({ ...q, _globalIndex: globalIdx })
      }
      return groups
    },
  },
  onLoad(options) {
    this.paperId = options.id
    this.loadPaper()
  },
  methods: {
    latexToUnicode,
    getTypeName(type) { return QUESTION_TYPES[type]?.label || type },
    getTypeColor(type) { return QUESTION_TYPES[type]?.color || '#6B7280' },
    getTypeIcon(type) {
      const icons = { choice: '📋', fill: '✏️', experiment: '🔬', calculation: '🧮', short_answer: '📝' }
      return icons[type] || '📋'
    },
    getDiffCount(level) {
      return this.questions.filter(q => q.difficulty === level).length
    },
    getDiffPercent(level) {
      return this._diffPercents[level] || 0
    },
    calcDiffPercents() {
      const total = this.questions.length || 1
      const counts = [0, 0, 0, 0, 0]
      this.questions.forEach(q => { counts[q.difficulty - 1]++ })
      const raw = counts.map(c => c / total * 100)
      const floored = raw.map(v => Math.floor(v))
      const remainders = raw.map((v, i) => ({ i, r: v - floored[i] }))
      remainders.sort((a, b) => b.r - a.r)
      let sum = floored.reduce((a, b) => a + b, 0)
      for (let k = 0; k < 100 - sum; k++) floored[remainders[k].i]++
      const result = {}
      for (let i = 0; i < 5; i++) result[i + 1] = floored[i]
      this._diffPercents = result
    },
    getGroupScore(group) {
      return group.reduce((s, q) => s + (q._score || 0), 0)
    },
    toggleGroup(type) {
      this.$set(this.expandedGroups, type, !this.expandedGroups[type])
    },
    async loadPaper() {
      try {
        const res = await papersAPI.detail(this.paperId)
        this.paper = res
        this.questions = (res.questions || []).map((q, idx) => {
          return {
            ...q,
            _score: q.score || 5,
            _sortOrder: q.sort_order || idx,
          }
        })
        // 默认展开第一个题型
        const types = [...new Set(this.questions.map(q => q.question_type))]
        if (types.length) this.$set(this.expandedGroups, types[0], true)
        this.calcDiffPercents()
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    async doExport() {
      if (this.exporting) return
      this.exporting = true
      this.showExportModal = false
      uni.showLoading({ title: '正在生成Word...' })
      let rawUrl = ''
      let exportFailed = false
      try {
        const res = await exportAPI.paperWord(this.paperId, this.includeAnswer)
        rawUrl = res.test_paper_url || ''
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
          fileName: buildWordFileName(this.paper && this.paper.title, '试卷'),
        })
      } catch (err) {
        console.log('Word转发失败:', JSON.stringify(err))
        uni.showToast({ title: 'Word转发失败', icon: 'none' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background: #F5F6FA;
  padding: 24rpx;
  padding-bottom: 160rpx;
}

/* 概览卡片 */
.overview-card {
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
  border-radius: 24rpx;
  padding: 32rpx;
  color: #fff;
  margin-bottom: 20rpx;
}
.ov-title { display: block; font-size: 34rpx; font-weight: 700; margin-bottom: 4rpx; }
.ov-subtitle { display: block; font-size: 24rpx; opacity: 0.85; margin-bottom: 20rpx; }
.ov-stats { display: flex; align-items: center; }
.ov-stat { flex: 1; text-align: center; }
.ov-num { display: block; font-size: 36rpx; font-weight: 700; }
.ov-label { display: block; font-size: 22rpx; opacity: 0.8; }
.ov-divider { width: 1rpx; height: 48rpx; background: rgba(255,255,255,0.3); }

/* 通用区块 */
.section-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.sec-title { display: block; font-size: 28rpx; font-weight: 600; color: #1F2937; margin-bottom: 16rpx; }

/* 题型分布 */
.type-bar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10rpx 0;
}
.type-bar-left { display: flex; align-items: center; gap: 12rpx; min-width: 200rpx; }
.type-dot { width: 16rpx; height: 16rpx; border-radius: 50%; }
.type-name { font-size: 24rpx; color: #374151; }
.type-count { font-size: 22rpx; color: #9CA3AF; }
.type-bar-right { display: flex; align-items: center; gap: 12rpx; flex: 1; margin-left: 16rpx; }
.type-bar-bg { flex: 1; height: 12rpx; background: #F3F4F6; border-radius: 6rpx; overflow: hidden; }
.type-bar-fill { height: 100%; border-radius: 6rpx; transition: width 0.3s; }
.type-percent { font-size: 22rpx; color: #6B7280; min-width: 60rpx; text-align: right; }

/* 难度分布 */
.diff-row { display: flex; align-items: center; gap: 12rpx; padding: 8rpx 0; }
.diff-label { font-size: 22rpx; color: #6B7280; min-width: 64rpx; }
.diff-bar-bg { flex: 1; height: 16rpx; background: #F3F4F6; border-radius: 8rpx; overflow: hidden; }
.diff-bar-fill { height: 100%; border-radius: 8rpx; transition: width 0.3s; }
.diff-count { font-size: 22rpx; color: #6B7280; min-width: 50rpx; text-align: right; }

/* 答案开关 */
.toggle-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.toggle-label { font-size: 28rpx; color: #374151; }

/* 分组 */
.group-card {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  &:active { background: #FAFBFC; }
}
.group-left { display: flex; align-items: center; gap: 16rpx; }
.group-icon {
  width: 56rpx; height: 56rpx;
  border-radius: 14rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 28rpx; color: #fff;
}
.group-type { display: block; font-size: 28rpx; font-weight: 600; color: #1F2937; }
.group-meta { display: block; font-size: 22rpx; color: #9CA3AF; }
.group-arrow { font-size: 28rpx; color: #D1D5DB; }
.group-body { padding: 0 24rpx 16rpx; }

/* 题目卡片 */
.q-card {
  border-top: 1rpx solid #F3F4F6;
  padding: 20rpx 0;
}
.q-header { display: flex; align-items: center; gap: 10rpx; margin-bottom: 10rpx; }
.q-index {
  width: 40rpx; height: 40rpx;
  background: #F59E0B; color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22rpx; font-weight: 700;
  text-align: center; line-height: 40rpx;
}
.q-score-badge {
  font-size: 22rpx; color: #F59E0B; font-weight: 600;
  background: rgba(245,158,11,0.1);
  padding: 4rpx 12rpx; border-radius: 8rpx;
}
.q-diff-badge {
  font-size: 20rpx; color: #fff;
  padding: 4rpx 12rpx; border-radius: 8rpx;
}
.q-content {
  font-size: 26rpx; color: #374151; line-height: 1.7;
  display: block; margin-bottom: 8rpx;
  white-space: pre-wrap;
}
.q-options { display: flex; flex-direction: column; gap: 6rpx; margin-bottom: 8rpx; }
.q-opt { font-size: 24rpx; color: #6B7280; padding-left: 16rpx; }
.q-answer {
  background: #F0FDF4;
  border-left: 4rpx solid #22C55E;
  padding: 12rpx 16rpx;
  border-radius: 0 8rpx 8rpx 0;
  margin-top: 8rpx;
}
.q-answer-label { font-size: 24rpx; color: #22C55E; font-weight: 600; }
.q-answer-text { font-size: 24rpx; color: #166534; }

/* 底部操作栏 */
.action-bar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: #fff;
  padding: 20rpx 32rpx;
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.action-btn {
  text-align: center;
  padding: 26rpx 0;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 600;
}
.btn-export {
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
  color: #fff;
}

/* 导出弹窗 */
.modal-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 200;
  display: flex; align-items: flex-end;
}
.modal-content {
  width: 100%; background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 40rpx 32rpx;
  padding-bottom: calc(40rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}
.modal-title {
  display: block; font-size: 32rpx; font-weight: 700; color: #1F2937;
  text-align: center; margin-bottom: 28rpx;
}
.format-option {
  display: flex; align-items: center; gap: 16rpx;
  padding: 24rpx; border-radius: 16rpx;
  border: 2rpx solid #E5E7EB;
  margin-bottom: 16rpx;
  &.active { border-color: #F59E0B; background: rgba(245,158,11,0.04); }
}
.format-icon { font-size: 36rpx; }
.format-info { flex: 1; }
.format-name { display: block; font-size: 28rpx; font-weight: 600; color: #1F2937; }
.format-desc { display: block; font-size: 22rpx; color: #9CA3AF; }
.format-check { font-size: 28rpx; color: #F59E0B; font-weight: 700; }
.export-options {
  padding: 16rpx 0;
  border-top: 1rpx solid #F3F4F6;
  margin-top: 8rpx;
}
.export-check {
  display: flex; align-items: center; gap: 12rpx;
  font-size: 26rpx; color: #374151;
}
.modal-actions { display: flex; gap: 20rpx; margin-top: 24rpx; }
.modal-btn {
  flex: 1; text-align: center; padding: 24rpx 0;
  border-radius: 16rpx; font-size: 30rpx; font-weight: 600;
}
.modal-btn.cancel { background: #F3F4F6; color: #6B7280; }
.modal-btn.confirm { background: #F59E0B; color: #fff; }

/* 加载 */
.loading-page {
  min-height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid #E5E7EB; border-top-color: #F59E0B;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
.loading-text { margin-top: 16rpx; font-size: 26rpx; color: #9CA3AF; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
