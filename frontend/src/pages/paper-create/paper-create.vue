<template>
  <view class="create-page">
    <!-- 模式选择 -->
    <view class="mode-tabs">
      <view :class="['mode-tab', mode === 'manual' ? 'active' : '']" @tap="mode = 'manual'">
        <text class="mode-icon">✋</text>
        <text>手动组卷</text>
      </view>
      <view :class="['mode-tab', mode === 'auto' ? 'active' : '']" @tap="mode = 'auto'">
        <text class="mode-icon">⚡</text>
        <text>智能组卷</text>
      </view>
    </view>

    <!-- 基本信息 -->
    <view class="form-section">
      <text class="section-title">试卷标题 *</text>
      <input class="form-input" v-model="form.title" placeholder="如：高一化学期中考试" />
    </view>
    <view class="form-section">
      <text class="section-title">副标题</text>
      <input class="form-input" v-model="form.subtitle" placeholder="如：必修一第一至三章" />
    </view>

    <!-- 手动组卷 - 选题 -->
    <view v-if="mode === 'manual'" class="form-section">
      <text class="section-title">选择题目（已选 {{ form.question_ids.length }} 题）</text>
      <view v-if="!allQuestions.length" class="empty-hint">暂无可用题目，请先在题库中添加题目</view>
      <view v-for="q in allQuestions" :key="q.id" class="select-item" @tap="toggleQuestion(q.id)">
        <view class="select-check" :class="{ checked: form.question_ids.includes(q.id) }">
          <text v-if="form.question_ids.includes(q.id)">✓</text>
        </view>
        <view class="select-content">
          <view class="select-type" :style="{ background: getTypeColor(q.question_type) }">
            {{ getTypeName(q.question_type) }}
          </view>
          <text class="select-text">{{ truncate(q.content, 40) }}</text>
        </view>
      </view>
    </view>

    <!-- 智能组卷 - 规则 -->
    <view v-if="mode === 'auto'" class="form-section">
      <text class="section-title">组卷规则</text>
      <view v-for="(rule, index) in form.rules" :key="index" class="rule-card">
        <view class="rule-header">
          <text class="rule-num">规则 {{ index + 1 }}</text>
          <text class="rule-del" @tap="removeRule(index)" v-if="form.rules.length > 1">✕</text>
        </view>
        <view class="rule-row">
          <text class="rule-label">题型</text>
          <picker :range="typeOptions" range-key="label" @change="rule.question_type = typeOptions[$event.detail.value].key">
            <text class="rule-value">{{ getTypeName(rule.question_type) }} ▾</text>
          </picker>
        </view>
        <view class="rule-row">
          <text class="rule-label">数量</text>
          <view class="num-control">
            <text class="num-btn" @tap="rule.count > 1 && rule.count--">−</text>
            <text class="num-value">{{ rule.count }}</text>
            <text class="num-btn" @tap="rule.count++">＋</text>
          </view>
        </view>
        <view class="rule-row">
          <text class="rule-label">难度范围</text>
          <text class="rule-value">{{ rule.difficulty_min }} - {{ rule.difficulty_max }}</text>
        </view>
        <view class="rule-row">
          <text class="rule-label">每题分值</text>
          <input class="rule-input" type="digit" v-model.number="rule.score_per_question" placeholder="5" />
        </view>
      </view>
      <view class="add-rule-btn" @tap="addRule">
        <text>+ 添加规则</text>
      </view>
    </view>

    <!-- 其他设置 -->
    <view class="form-section">
      <text class="section-title">总分</text>
      <input class="form-input" type="number" v-model.number="form.total_score" placeholder="100" />
    </view>
    <view class="form-section">
      <text class="section-title">考试时长（分钟）</text>
      <input class="form-input" type="number" v-model.number="form.exam_duration" placeholder="60" />
    </view>

    <!-- 提交 -->
    <view class="submit-area">
      <view class="btn-submit" @tap="handleSubmit">
        <text>{{ mode === 'manual' ? '创建试卷' : '智能组卷' }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { papersAPI, questionsAPI, tagsAPI } from '../../utils/api.js'
import { truncate, QUESTION_TYPES } from '../../utils/util.js'
import { buildTypeConfigs } from '../../utils/type-config.js'

export default {
  data() {
    return {
      mode: 'manual',
      allQuestions: [],
      form: {
        title: '',
        subtitle: '',
        question_ids: [],
        total_score: 100,
        exam_duration: 60,
        rules: [
          { question_type: 'choice', difficulty_min: 1, difficulty_max: 3, count: 5, score_per_question: 4 },
          { question_type: 'fill', difficulty_min: 2, difficulty_max: 4, count: 3, score_per_question: 6 },
        ],
      },
      types: QUESTION_TYPES,
      typeOptions: Object.entries(QUESTION_TYPES).map(([k, v]) => ({ key: k, label: v.label })),
    }
  },
  onLoad(options) {
    if (options.mode === 'auto') this.mode = 'auto'
    this.loadTypeTags()
    this.loadQuestions()
  },
  methods: {
    truncate,
    getTypeName(type) { return this.types[type]?.label || type },
    getTypeColor(type) { return this.types[type]?.color || '#6B7280' },
    async loadTypeTags() {
      try {
        const tags = await tagsAPI.list({})
        const typeTags = (Array.isArray(tags) ? tags : []).filter((tag) => tag.tag_type === 'type')
        this.types = buildTypeConfigs(typeTags, QUESTION_TYPES)
        this.typeOptions = Object.entries(this.types).map(([k, v]) => ({ key: k, label: v.label }))
      } catch (error) {
        console.error('加载题型标签失败', error)
      }
    },
    async loadQuestions() {
      try {
        const res = await questionsAPI.list({ page: 1, page_size: 200 })
        this.allQuestions = res.items || []
      } catch (e) {}
    },
    toggleQuestion(id) {
      const idx = this.form.question_ids.indexOf(id)
      if (idx >= 0) {
        this.form.question_ids.splice(idx, 1)
      } else {
        this.form.question_ids.push(id)
      }
    },
    addRule() {
      this.form.rules.push({ question_type: 'choice', difficulty_min: 1, difficulty_max: 3, count: 3, score_per_question: 5 })
    },
    removeRule(index) {
      this.form.rules.splice(index, 1)
    },
    async handleSubmit() {
      if (!this.form.title.trim()) {
        return uni.showToast({ title: '请输入试卷标题', icon: 'none' })
      }
      uni.showLoading({ title: '创建中...' })
      try {
        if (this.mode === 'manual') {
          if (!this.form.question_ids.length) {
            uni.hideLoading()
            return uni.showToast({ title: '请至少选择一道题目', icon: 'none' })
          }
          await papersAPI.createManual(this.form)
        } else {
          await papersAPI.createAuto(this.form)
        }
        uni.hideLoading()
        uni.showToast({ title: '创建成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 500)
      } catch (e) {
        uni.hideLoading()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.create-page {
  min-height: 100vh;
  background: #F5F6FA;
  padding: 24rpx;
  padding-bottom: 160rpx;
}
.mode-tabs {
  display: flex;
  gap: 16rpx;
  margin-bottom: 28rpx;
}
.mode-tab {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  background: #fff;
  border-radius: 16rpx;
  border: 2rpx solid #E5E7EB;
  font-size: 28rpx;
  color: #6B7280;
  &.active {
    border-color: #F59E0B;
    background: rgba(245,158,11,0.06);
    color: #F59E0B;
    font-weight: 600;
  }
}
.mode-icon { margin-right: 8rpx; }
.form-section { margin-bottom: 28rpx; }
.section-title { display: block; font-size: 28rpx; font-weight: 600; color: #1F2937; margin-bottom: 12rpx; }
.form-input {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.select-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #fff;
  padding: 20rpx 24rpx;
  border-radius: 12rpx;
  margin-bottom: 12rpx;
  &:active { background: #FAFBFC; }
}
.select-check {
  width: 40rpx;
  height: 40rpx;
  border: 3rpx solid #D1D5DB;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  color: #fff;
  flex-shrink: 0;
  &.checked { background: #F59E0B; border-color: #F59E0B; }
}
.select-content { flex: 1; display: flex; align-items: center; gap: 12rpx; }
.select-type { font-size: 20rpx; color: #fff; padding: 4rpx 12rpx; border-radius: 6rpx; white-space: nowrap; }
.select-text { font-size: 26rpx; color: #374151; }
.rule-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.rule-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
}
.rule-num { font-size: 26rpx; font-weight: 600; color: #F59E0B; }
.rule-del { font-size: 28rpx; color: #EF4444; padding: 4rpx 8rpx; }
.rule-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
  &:last-child { border-bottom: none; }
}
.rule-label { font-size: 26rpx; color: #6B7280; }
.rule-value { font-size: 26rpx; color: #1F2937; }
.rule-input {
  width: 120rpx;
  height: 56rpx;
  background: #F5F6FA;
  border-radius: 8rpx;
  text-align: center;
  font-size: 26rpx;
}
.num-control {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.num-btn {
  width: 48rpx;
  height: 48rpx;
  background: #F3F4F6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #6B7280;
}
.num-value { font-size: 28rpx; font-weight: 600; color: #1F2937; min-width: 40rpx; text-align: center; }
.add-rule-btn {
  text-align: center;
  padding: 20rpx;
  color: #F59E0B;
  font-size: 26rpx;
}
.empty-hint { font-size: 26rpx; color: #9CA3AF; text-align: center; padding: 40rpx 0; }
.submit-area {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.btn-submit {
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
  border-radius: 16rpx;
  padding: 26rpx 0;
  text-align: center;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  &:active { opacity: 0.9; }
}
</style>
