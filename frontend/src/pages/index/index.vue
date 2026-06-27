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

      <!-- 工具箱 -->
      <view class="section-title">工具箱</view>
      <view class="toolbox-list">
        <view class="tool-item" @tap="goTo('/pages/tags/tags')">
          <view class="tool-icon" style="background: linear-gradient(135deg, #3B82F6, #60A5FA)">
            <text class="tool-icon-text">标</text>
          </view>
          <view class="tool-info">
            <text class="tool-name">标签管理</text>
            <text class="tool-desc">管理教材、知识点与题型分类</text>
          </view>
          <text class="tool-arrow">›</text>
        </view>
        <view class="tool-item" :class="{ 'tool-disabled': tagCount >= PRESET_TAGS_TOTAL }" @tap="onInitTagsTap">
          <view class="tool-icon" :style="{ background: tagCount >= PRESET_TAGS_TOTAL ? 'linear-gradient(135deg, #9CA3AF, #D1D5DB)' : tagCount > 0 ? 'linear-gradient(135deg, #3B82F6, #60A5FA)' : 'linear-gradient(135deg, #10B981, #34D399)' }">
            <text class="tool-icon-text">{{ tagCount >= PRESET_TAGS_TOTAL ? '✓' : tagCount > 0 ? '补' : '初' }}</text>
          </view>
          <view class="tool-info">
            <text class="tool-name">{{ tagCount >= PRESET_TAGS_TOTAL ? '标签已就绪' : tagCount > 0 ? '补全标签' : '初始化标签' }}</text>
            <text class="tool-desc">{{ tagCount >= PRESET_TAGS_TOTAL ? '已创建 ' + tagCount + ' 个预设标签' : tagCount > 0 ? '已有 ' + tagCount + ' 个，还差 ' + (PRESET_TAGS_TOTAL - tagCount) + ' 个' : '一键创建高中化学预设标签体系' }}</text>
          </view>
          <text class="tool-arrow" v-if="tagCount < PRESET_TAGS_TOTAL">›</text>
        </view>
        <view class="tool-item" @tap="goTo('/pages/paper-create/paper-create?mode=auto')">
          <view class="tool-icon" style="background: linear-gradient(135deg, #F59E0B, #FBBF24)">
            <text class="tool-icon-text">卷</text>
          </view>
          <view class="tool-info">
            <text class="tool-name">快速组卷</text>
            <text class="tool-desc">按条件自动挑选题目生成试卷</text>
          </view>
          <text class="tool-arrow">›</text>
        </view>
      </view>
    </scroll-view>

    <!-- 底部弹窗：预览 / 结果 -->
    <view class="sheet-mask" v-if="showSheet" @tap="closeSheet"></view>
    <view class="sheet-container" :class="{ 'sheet-show': showSheet }">
      <!-- 预览模式 -->
      <template v-if="sheetMode === 'preview'">
        <view class="sheet-header">
          <text class="sheet-title">预览将创建的标签</text>
          <text class="sheet-close" @tap="closeSheet">×</text>
        </view>
        <scroll-view scroll-y class="sheet-body">
          <view v-for="(tags, catType) in PRESET_TAGS" :key="catType" class="preview-category">
            <text class="preview-cat-name">{{ CATEGORY_NAMES[catType] }} ({{ tags.length }})</text>
            <view class="preview-pills">
              <view v-for="tag in tags" :key="tag.name" class="preview-pill" :class="{ 'pill-exists': existingTagNames.has(tag.name) }">
                <text class="pill-text">{{ tag.name }}</text>
                <text class="pill-check" v-if="existingTagNames.has(tag.name)">✓</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="sheet-footer">
          <view class="sheet-btn-primary" :class="{ 'btn-loading': seeding }" @tap="confirmSeed">
            <text class="btn-text">{{ seeding ? '初始化中...' : '确认初始化 (' + newTagCount + ' 个新标签)' }}</text>
          </view>
          <text class="sheet-cancel" @tap="closeSheet">取消</text>
        </view>
      </template>

      <!-- 结果模式 -->
      <template v-if="sheetMode === 'result'">
        <view class="sheet-header">
          <text class="sheet-title">✓ 标签初始化完成</text>
          <text class="sheet-close" @tap="closeSheet">×</text>
        </view>
        <scroll-view scroll-y class="sheet-body">
          <view class="result-summary">
            <view class="result-stat">
              <text class="result-num result-created">{{ seedResult.created }}</text>
              <text class="result-label">新建</text>
            </view>
            <view class="result-stat">
              <text class="result-num result-skipped">{{ seedResult.skipped }}</text>
              <text class="result-label">已存在</text>
            </view>
            <view class="result-stat">
              <text class="result-num result-total">{{ seedResult.total }}</text>
              <text class="result-label">合计</text>
            </view>
          </view>
          <view v-for="(cat, catType) in seedResult.categories" :key="catType" class="result-row">
            <text class="result-cat-name">{{ CATEGORY_NAMES[catType] }}</text>
            <text class="result-cat-detail">
              <text v-if="cat.created > 0" class="rc-green">新建 {{ cat.created }}</text>
              <text v-if="cat.skipped > 0" class="rc-gray">已存在 {{ cat.skipped }}</text>
            </text>
          </view>
        </scroll-view>
        <view class="sheet-footer">
          <view class="sheet-btn-primary" @tap="goToTags">
            <text class="btn-text">查看标签管理 →</text>
          </view>
          <text class="sheet-cancel" @tap="closeSheet">关闭</text>
        </view>
      </template>
    </view>
  </view>
</template>

<script>
import { questionsAPI, tagsAPI } from '../../utils/api.js'
import { truncate, QUESTION_TYPES } from '../../utils/util.js'
import { formatRelativeTime as formatTime } from '../../utils/time.js'

const PRESET_TAGS = {
  book: [
    { name: '必修第一册', sort_order: 1 },
    { name: '必修第二册', sort_order: 2 },
    { name: '选择性必修1 化学反应原理', sort_order: 3 },
    { name: '选择性必修2 物质结构与性质', sort_order: 4 },
    { name: '选择性必修3 有机化学基础', sort_order: 5 },
  ],
  type: [
    { name: '选择题', sort_order: 1 },
    { name: '填空题', sort_order: 2 },
    { name: '实验题', sort_order: 3 },
    { name: '计算题', sort_order: 4 },
    { name: '简答题', sort_order: 5 },
  ],
  difficulty: [
    { name: '极易', sort_order: 1 },
    { name: '较易', sort_order: 2 },
    { name: '中等', sort_order: 3 },
    { name: '较难', sort_order: 4 },
    { name: '极难', sort_order: 5 },
  ],
  knowledge: [
    { name: '物质的分类与转化', sort_order: 1 },
    { name: '离子反应', sort_order: 2 },
    { name: '氧化还原反应', sort_order: 3 },
    { name: '钠及其化合物', sort_order: 4 },
    { name: '氯及其化合物', sort_order: 5 },
    { name: '铁及其化合物', sort_order: 6 },
    { name: '物质的量', sort_order: 7 },
    { name: '元素周期表与周期律', sort_order: 8 },
    { name: '化学键与分子结构', sort_order: 9 },
    { name: '化学反应与能量', sort_order: 10 },
    { name: '化学反应速率与平衡', sort_order: 11 },
    { name: '水溶液中的离子平衡', sort_order: 12 },
    { name: '电化学', sort_order: 13 },
    { name: '有机化合物', sort_order: 14 },
    { name: '化学实验基础', sort_order: 15 },
  ],
}

const PRESET_TAGS_TOTAL = Object.values(PRESET_TAGS).reduce((sum, arr) => sum + arr.length, 0)

const CATEGORY_NAMES = {
  book: '教材版本',
  knowledge: '知识点',
  type: '题型',
  difficulty: '难度',
}

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      nickname: '老师',
      recentQuestions: [],
      // 标签状态
      tagCount: 0,
      existingTagNames: new Set(),
      PRESET_TAGS_TOTAL,
      PRESET_TAGS,
      CATEGORY_NAMES,
      // 底部弹窗
      showSheet: false,
      sheetMode: 'preview', // 'preview' | 'result'
      seeding: false,
      seedResult: { created: 0, skipped: 0, total: 0, categories: {} },
    }
  },
  computed: {
    newTagCount() {
      let count = 0
      for (const tags of Object.values(PRESET_TAGS)) {
        for (const tag of tags) {
          if (!this.existingTagNames.has(tag.name)) count++
        }
      }
      return count
    },
  },
  onShow() {
    const info = uni.getStorageSync('user_info')
    if (info) {
      const user = typeof info === 'string' ? JSON.parse(info) : info
      this.nickname = user.nickname || user.username || '老师'
    }
    this.loadRecentQuestions()
    this.loadTagStatus()
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
    async loadTagStatus() {
      const token = uni.getStorageSync('access_token')
      if (!token) return
      try {
        const tags = await tagsAPI.list({})
        this.tagCount = Array.isArray(tags) ? tags.length : 0
        this.existingTagNames = new Set((tags || []).map((t) => t.name))
      } catch (e) {
        // 静默失败，不影响首页
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
    onInitTagsTap() {
      if (this.tagCount >= PRESET_TAGS_TOTAL) return
      this.sheetMode = 'preview'
      this.showSheet = true
    },
    closeSheet() {
      this.showSheet = false
    },
    async confirmSeed() {
      if (this.seeding) return
      this.seeding = true
      try {
        const res = await tagsAPI.seed()
        this.seedResult = res || { created: 0, skipped: 0, total: 0, categories: {} }
        this.sheetMode = 'result'
        // 刷新本地标签状态
        this.tagCount = (this.seedResult.created || 0) + (this.seedResult.skipped || 0)
        const allNames = new Set(this.existingTagNames)
        for (const tags of Object.values(PRESET_TAGS)) {
          for (const tag of tags) allNames.add(tag.name)
        }
        this.existingTagNames = allNames
      } catch (e) {
        this.showSheet = false
        // 错误已由 request 层 toast 处理
      } finally {
        this.seeding = false
      }
    },
    goToTags() {
      this.showSheet = false
      uni.navigateTo({ url: '/pages/tags/tags' })
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

.toolbox-list {
  padding: 0 24rpx 40rpx;
}
.tool-item {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  transition: transform 150ms ease-out, opacity 150ms ease-out;
  &:active {
    transform: scale(0.98);
    opacity: 0.85;
  }
}
.tool-disabled {
  opacity: 0.6;
  &:active { transform: none; opacity: 0.6; }
}
.tool-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.tool-icon-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #fff;
}
.tool-info {
  flex: 1;
  margin-left: 24rpx;
}
.tool-name {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 4rpx;
}
.tool-desc {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
  line-height: 1.4;
}
.tool-arrow {
  font-size: 36rpx;
  color: #D1D5DB;
  flex-shrink: 0;
  margin-left: 16rpx;
}

/* ===== 底部弹窗 ===== */
.sheet-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.45);
  z-index: 200;
}
.sheet-container {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  z-index: 201;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  transform: translateY(100%);
  transition: transform 250ms ease-out;
  padding-bottom: env(safe-area-inset-bottom);
}
.sheet-show {
  transform: translateY(0);
}
.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 32rpx 16rpx;
  flex-shrink: 0;
}
.sheet-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
}
.sheet-close {
  font-size: 40rpx;
  color: #9CA3AF;
  padding: 8rpx;
}
.sheet-body {
  flex: 1;
  overflow-y: auto;
  padding: 0 32rpx;
  max-height: 55vh;
}
.sheet-footer {
  flex-shrink: 0;
  padding: 20rpx 32rpx 24rpx;
  text-align: center;
}
.sheet-btn-primary {
  background: linear-gradient(135deg, #10B981, #34D399);
  border-radius: 16rpx;
  padding: 24rpx 0;
  margin-bottom: 16rpx;
  transition: opacity 150ms;
  &:active { opacity: 0.85; }
}
.btn-loading {
  opacity: 0.6;
  &:active { opacity: 0.6; }
}
.btn-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #fff;
}
.sheet-cancel {
  font-size: 28rpx;
  color: #9CA3AF;
  padding: 12rpx 0;
  display: inline-block;
}

/* 预览标签 */
.preview-category {
  margin-bottom: 24rpx;
}
.preview-cat-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12rpx;
  display: block;
}
.preview-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}
.preview-pill {
  display: flex;
  align-items: center;
  background: #EEF2FF;
  border-radius: 8rpx;
  padding: 8rpx 16rpx;
}
.pill-exists {
  background: #F3F4F6;
}
.pill-text {
  font-size: 24rpx;
  color: #374151;
}
.pill-exists .pill-text {
  color: #9CA3AF;
}
.pill-check {
  font-size: 20rpx;
  color: #10B981;
  margin-left: 6rpx;
}

/* 结果摘要 */
.result-summary {
  display: flex;
  justify-content: space-around;
  padding: 24rpx 0;
  margin-bottom: 16rpx;
  border-bottom: 1rpx solid #F3F4F6;
}
.result-stat {
  text-align: center;
}
.result-num {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
}
.result-created { color: #10B981; }
.result-skipped { color: #9CA3AF; }
.result-total { color: #3B82F6; }
.result-label {
  display: block;
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}
.result-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #F9FAFB;
}
.result-cat-name {
  font-size: 28rpx;
  color: #374151;
}
.result-cat-detail {
  font-size: 24rpx;
}
.rc-green { color: #10B981; margin-right: 16rpx; }
.rc-gray { color: #9CA3AF; }
</style>
