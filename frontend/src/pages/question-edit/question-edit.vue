<template>
  <view class="edit-page">
    <view class="form-section">
      <text class="section-title">题目内容 *</text>
      <textarea class="form-textarea" v-model="form.content" placeholder="输入题目内容（支持 LaTeX 格式）" :maxlength="-1" />
    </view>

    <view class="form-section">
      <text class="section-title">答案 *</text>
      <textarea class="form-textarea" v-model="form.answer" placeholder="输入答案" :maxlength="-1" />
    </view>

    <view class="form-section">
      <text class="section-title">解析</text>
      <textarea class="form-textarea" v-model="form.analysis" placeholder="输入题目解析" :maxlength="-1" />
    </view>

    <!-- 题型选择 -->
    <view class="form-section">
      <text class="section-title">题型</text>
      <view class="type-grid">
        <view v-for="(t, key) in types" :key="key"
              :class="['type-item', form.question_type === key ? 'active' : '']"
              :style="form.question_type === key ? { borderColor: t.color, background: t.color + '10' } : {}"
              @tap="form.question_type = key">
          <text class="type-icon">{{ t.icon }}</text>
          <text class="type-label" :style="form.question_type === key ? { color: t.color } : {}">{{ t.label }}</text>
        </view>
      </view>
    </view>

    <!-- 难度选择 -->
    <view class="form-section">
      <text class="section-title">难度</text>
      <view class="difficulty-bar">
        <view v-for="i in 5" :key="i"
              :class="['diff-item', form.difficulty >= i ? 'active' : '']"
              :style="form.difficulty >= i ? { background: getDiffColor(i) } : {}"
              @tap="form.difficulty = i">
          <text class="diff-text">{{ getDiffLabel(i) }}</text>
        </view>
      </view>
    </view>

    <!-- 来源 -->
    <view class="form-section">
      <text class="section-title">来源</text>
      <input class="form-input" v-model="form.source" placeholder="如：2024年高考全国卷" />
    </view>

    <!-- 选项（选择题时显示） -->
    <view class="form-section" v-if="form.question_type === 'choice'">
      <text class="section-title">选项</text>
      <view v-for="(opt, index) in form.options" :key="index" class="option-row">
        <text class="option-label">{{ opt.label }}</text>
        <input class="option-input" v-model="opt.text" :placeholder="`选项${opt.label}内容`" />
        <text class="option-del" v-if="form.options.length > 2" @tap="removeOption(index)">✕</text>
      </view>
      <view class="add-option" @tap="addOption">
        <text>+ 添加选项</text>
      </view>
    </view>

    <view class="submit-area">
      <view class="btn-submit" @tap="handleSubmit">
        <text>{{ isEdit ? '保存修改' : '创建题目' }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { questionsAPI } from '../../utils/api.js'
import { QUESTION_TYPES, DIFFICULTY_LEVELS } from '../../utils/util.js'

export default {
  data() {
    return {
      isEdit: false,
      questionId: '',
      form: {
        content: '',
        answer: '',
        analysis: '',
        question_type: 'choice',
        difficulty: 3,
        source: '',
        options: [
          { label: 'A', text: '' },
          { label: 'B', text: '' },
          { label: 'C', text: '' },
          { label: 'D', text: '' },
        ],
        tag_ids: [],
      },
      types: QUESTION_TYPES,
    }
  },
  onLoad(options) {
    if (options.data) {
      try {
        const data = JSON.parse(decodeURIComponent(options.data))
        this.form.content = data.content || ''
        if (data.ocr_record_id) {
          this.form.ocr_record_id = data.ocr_record_id
        }
      } catch (e) {}
    }
    if (options.id) {
      this.isEdit = true
      this.questionId = options.id
      this.loadQuestion()
    }
  },
  methods: {
    getDiffColor(i) {
      return DIFFICULTY_LEVELS[i]?.color || '#F59E0B'
    },
    getDiffLabel(i) {
      return DIFFICULTY_LEVELS[i]?.label || ''
    },
    addOption() {
      const labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      const next = labels[this.form.options.length] || String(this.form.options.length + 1)
      this.form.options.push({ label: next, text: '' })
    },
    removeOption(index) {
      this.form.options.splice(index, 1)
    },
    async loadQuestion() {
      try {
        const res = await questionsAPI.detail(this.questionId)
        this.form.content = res.content || ''
        this.form.answer = res.answer || ''
        this.form.analysis = res.analysis || ''
        this.form.question_type = res.question_type || 'choice'
        this.form.difficulty = res.difficulty || 3
        this.form.source = res.source || ''
        if (res.options && res.options.length) {
          this.form.options = res.options
        }
        if (res.tags) {
          this.form.tag_ids = res.tags.map(t => t.id)
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    async handleSubmit() {
      if (!this.form.content.trim()) {
        return uni.showToast({ title: '请输入题目内容', icon: 'none' })
      }
      uni.showLoading({ title: '保存中...' })
      try {
        if (this.isEdit) {
          await questionsAPI.update(this.questionId, this.form)
        } else {
          await questionsAPI.create(this.form)
        }
        uni.hideLoading()
        uni.showToast({ title: this.isEdit ? '修改成功' : '创建成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 500)
      } catch (e) {
        uni.hideLoading()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.edit-page {
  min-height: 100vh;
  background: #F5F6FA;
  padding: 24rpx;
  padding-bottom: 160rpx;
}
.form-section {
  margin-bottom: 28rpx;
}
.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 12rpx;
}
.form-textarea {
  width: 100%;
  min-height: 180rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
  line-height: 1.7;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.form-input {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.type-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.type-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 24rpx;
  border-radius: 16rpx;
  border: 2rpx solid #E5E7EB;
  background: #fff;
  &.active { border-width: 2rpx; }
}
.type-icon { font-size: 28rpx; }
.type-label { font-size: 24rpx; color: #6B7280; }
.difficulty-bar {
  display: flex;
  gap: 12rpx;
}
.diff-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  border-radius: 12rpx;
  background: #F3F4F6;
  &.active .diff-text { color: #fff; font-weight: 600; }
}
.diff-text { font-size: 24rpx; color: #6B7280; }
.option-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}
.option-label {
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
  text-align: center;
  line-height: 48rpx;
}
.option-input {
  flex: 1;
  height: 72rpx;
  background: #fff;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.04);
}
.option-del {
  font-size: 28rpx;
  color: #EF4444;
  padding: 8rpx;
}
.add-option {
  text-align: center;
  padding: 16rpx;
  color: #4A6CF7;
  font-size: 26rpx;
}
.submit-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.btn-submit {
  background: linear-gradient(135deg, #4A6CF7, #6B8AFF);
  border-radius: 16rpx;
  padding: 26rpx 0;
  text-align: center;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  &:active { opacity: 0.9; }
}
</style>
