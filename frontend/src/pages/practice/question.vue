<template>
  <view class="question-page">
    <!-- 进度条 -->
    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: ((currentIndex + 1) / questions.length * 100) + '%' }"></view>
    </view>
    <view class="progress-text">
      <text>{{ currentIndex + 1 }} / {{ questions.length }}</text>
      <view v-if="timerRunning" class="timer">
        <text>{{ formatTime(elapsedSeconds) }}</text>
      </view>
    </view>

    <!-- 答题卡 -->
    <view class="answer-sheet">
      <view v-for="(q, idx) in questions" :key="q.id"
            :class="['dot', idx === currentIndex ? 'current' : '', idx < currentIndex ? 'done' : '', answers[q.id] !== undefined ? (answers[q.id].is_correct ? 'correct' : 'wrong') : '']"
            @tap="goToQuestion(idx)">
      </view>
    </view>

    <!-- 题目内容 -->
    <scroll-view scroll-y class="question-scroll" v-if="currentQuestion">
      <view class="q-card">
        <view class="q-header">
          <view class="q-type" :style="{ background: getTypeColor(currentQuestion.question_type) }">
            {{ getTypeName(currentQuestion.question_type) }}
          </view>
          <view class="q-diff">
            <text v-for="i in 5" :key="i" :class="i <= currentQuestion.difficulty ? 'star-on' : 'star-off'">★</text>
          </view>
        </view>
        <text class="q-content">{{ latexToUnicode(currentQuestion.content) }}</text>

        <!-- 选项（选择题） -->
        <view v-if="currentQuestion.question_type === 'choice' && currentQuestion.options" class="options-area">
          <view v-for="opt in currentQuestion.options" :key="opt.label"
                :class="['option-item', getOptionClass(opt.label)]"
                @tap="selectOption(opt.label)">
            <view class="opt-label">{{ opt.label }}</view>
            <text class="opt-text">{{ latexToUnicode(opt.text) }}</text>
          </view>
        </view>

        <!-- 填空题输入 -->
        <view v-if="currentQuestion.question_type === 'fill'" class="fill-area">
          <input class="fill-input" v-model="fillAnswer" placeholder="输入答案" />
        </view>

        <!-- 已提交的答案反馈 -->
        <view v-if="showFeedback" class="feedback-area">
          <view :class="['feedback-box', currentAnswer.is_correct ? 'correct' : 'wrong']">
            <text class="feedback-icon">{{ currentAnswer.is_correct ? '✓' : '✗' }}</text>
            <text class="feedback-text">{{ currentAnswer.is_correct ? '回答正确！' : '回答错误' }}</text>
          </view>

          <!-- 正确答案 -->
          <view v-if="!currentAnswer.is_correct" class="correct-answer">
            <text class="answer-label">正确答案：</text>
            <text class="answer-text">{{ currentQuestion.answer }}</text>
          </view>

          <!-- 解析 -->
          <view v-if="currentQuestion.analysis" class="analysis-box" @tap="showAnalysis = !showAnalysis">
            <text class="analysis-title">💡 解析 {{ showAnalysis ? '▾' : '▸' }}</text>
            <view v-if="showAnalysis" class="analysis-body">
              <text>{{ latexToUnicode(currentQuestion.analysis) }}</text>
            </view>
          </view>

          <view class="btn-next" @tap="nextQuestion">
            <text>{{ currentIndex < questions.length - 1 ? '下一题' : '查看结果' }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部提交按钮 -->
    <view v-if="!showFeedback" class="bottom-bar">
      <view class="btn-submit" @tap="submitAnswer">
        <text>提交答案</text>
      </view>
    </view>
  </view>
</template>

<script>
import { practiceAPI, tagsAPI } from '../../utils/api.js'
import { QUESTION_TYPES, latexToUnicode } from '../../utils/util.js'
import { buildTypeConfigs } from '../../utils/type-config.js'

export default {
  data() {
    return {
      questions: [],
      currentIndex: 0,
      answers: {},
      selectedOption: '',
      fillAnswer: '',
      showFeedback: false,
      showAnalysis: false,
      currentAnswer: {},
      elapsedSeconds: 0,
      timerRunning: false,
      questionStartTime: 0,
      types: QUESTION_TYPES,
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex] || null
    },
  },
  onLoad(options) {
    const mode = options.mode || 'sequential'
    const tagId = options.tag_id || ''
    const tag_name = options.tag_name || ''
    this.loadTypeTags()
    this.loadQuestions(mode, tagId)
  },
  methods: {
    latexToUnicode,
    getTypeName(type) { return this.types[type]?.label || type },
    getTypeColor(type) { return this.types[type]?.color || '#6B7280' },
    async loadTypeTags() {
      try {
        const tags = await tagsAPI.list({})
        const typeTags = (Array.isArray(tags) ? tags : []).filter((tag) => tag.tag_type === 'type')
        this.types = buildTypeConfigs(typeTags, QUESTION_TYPES)
      } catch (error) {
        console.error('加载题型标签失败', error)
      }
    },

    async loadQuestions(mode, tagId) {
      uni.showLoading({ title: '加载中...' })
      try {
        const params = { mode, count: 20 }
        if (tagId) params.tag_id = tagId
        const res = await practiceAPI.getQuestions(params)
        this.questions = res.questions || []
        if (this.questions.length === 0) {
          uni.showToast({ title: '暂无题目', icon: 'none' })
          setTimeout(() => uni.navigateBack(), 1000)
          return
        }
        this.currentIndex = 0
        this.questionStartTime = Date.now()
        this.startTimer()
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
      uni.hideLoading()
    },

    startTimer() {
      this.timerRunning = true
      this.timerInterval = setInterval(() => {
        this.elapsedSeconds++
      }, 1000)
    },

    selectOption(label) {
      if (this.showFeedback) return
      this.selectedOption = label
    },

    getOptionClass(label) {
      if (!this.showFeedback) {
        return label === this.selectedOption ? 'selected' : ''
      }
      // 已提交，显示正确/错误
      if (label === this.currentQuestion.answer) return 'correct-answer'
      if (label === this.selectedOption && !this.currentAnswer.is_correct) return 'wrong-answer'
      return ''
    },

    async submitAnswer() {
      if (this.showFeedback) return

      const q = this.currentQuestion
      let answer = ''
      let isCorrect = false

      if (q.question_type === 'choice') {
        if (!this.selectedOption) {
          return uni.showToast({ title: '请先选择答案', icon: 'none' })
        }
        answer = this.selectedOption
        isCorrect = answer === q.answer
      } else {
        answer = this.fillAnswer.trim()
        if (!answer) {
          return uni.showToast({ title: '请输入答案', icon: 'none' })
        }
        isCorrect = answer.toLowerCase() === (q.answer || '').toLowerCase()
      }

      const duration = Math.floor((Date.now() - this.questionStartTime) / 1000)

      // 保存答案
      this.$set(this.answers, q.id, { answer, is_correct: isCorrect })
      this.currentAnswer = { answer, is_correct: isCorrect }

      // 提交到后端
      try {
        await practiceAPI.submitAnswer({
          question_id: q.id,
          student_answer: answer,
          is_correct: isCorrect,
          duration_seconds: duration,
        })
      } catch (e) {}

      this.showFeedback = true
      this.showAnalysis = false
      this.timerRunning = false
      clearInterval(this.timerInterval)
    },

    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.selectedOption = ''
        this.fillAnswer = ''
        this.showFeedback = false
        this.showAnalysis = false
        this.currentAnswer = {}
        this.questionStartTime = Date.now()
        this.timerRunning = true
        this.timerInterval = setInterval(() => {
          this.elapsedSeconds++
        }, 1000)
      } else {
        // 全部完成
        clearInterval(this.timerInterval)
        this.goToResult()
      }
    },

    goToQuestion(idx) {
      if (idx < this.currentIndex) {
        // 只能回看已做的题
        this.currentIndex = idx
        this.showFeedback = true
        this.showAnalysis = false
        const q = this.questions[idx]
        this.currentAnswer = this.answers[q.id] || {}
        this.selectedOption = this.currentAnswer.answer || ''
      }
    },

    goToResult() {
      const total = this.questions.length
      const correct = Object.values(this.answers).filter(a => a.is_correct).length
      uni.redirectTo({
        url: `/pages/practice/result?total=${total}&correct=${correct}&time=${this.elapsedSeconds}`
      })
    },

    formatTime(s) {
      const m = Math.floor(s / 60)
      const sec = s % 60
      return `${m}:${String(sec).padStart(2, '0')}`
    },
  },

  beforeDestroy() {
    if (this.timerInterval) clearInterval(this.timerInterval)
  },
}
</script>

<style lang="scss" scoped>
.question-page { min-height: 100vh; background: #F7FAFC; }

/* 进度条 */
.progress-bar {
  height: 6rpx; background: #E2E8F0; margin: 0 24rpx; border-radius: 3rpx;
}
.progress-fill {
  height: 100%; background: linear-gradient(90deg, #2B6CB0, #38A169);
  border-radius: 3rpx; transition: width 0.3s;
}
.progress-text {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12rpx 24rpx; font-size: 24rpx; color: #64748B;
}
.timer { color: #E53E3E; font-weight: 600; }

/* 答题卡 */
.answer-sheet {
  display: flex; gap: 8rpx; padding: 0 24rpx; flex-wrap: wrap;
  margin-bottom: 16rpx;
}
.dot {
  width: 20rpx; height: 20rpx; border-radius: 50%;
  background: #E2E8F0; transition: background 0.2s;
  &.current { background: #2B6CB0; transform: scale(1.3); }
  &.done { background: #CBD5E1; }
  &.correct { background: #38A169; }
  &.wrong { background: #E53E3E; }
}

/* 题目 */
.question-scroll { height: calc(100vh - 260rpx); }
.q-card {
  margin: 0 24rpx; background: #fff; border-radius: 20rpx;
  padding: 28rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.q-header { display: flex; align-items: center; gap: 12rpx; margin-bottom: 16rpx; }
.q-type {
  font-size: 22rpx; color: #fff; padding: 4rpx 16rpx; border-radius: 8rpx;
  font-weight: 500;
}
.q-diff { font-size: 20rpx; }
.star-on { color: #F59E0B; }
.star-off { color: #E2E8F0; }
.q-content {
  font-size: 30rpx; color: #1E293B; line-height: 1.8;
  display: block; margin-bottom: 24rpx; white-space: pre-wrap;
}

/* 选项 */
.options-area { display: flex; flex-direction: column; gap: 16rpx; }
.option-item {
  display: flex; align-items: flex-start; gap: 16rpx;
  padding: 24rpx; border-radius: 14rpx;
  border: 2rpx solid #E2E8F0; background: #F8FAFC;
  transition: all 0.2s;
  &:active { background: #F1F5F9; }
  &.selected {
    border-color: #2B6CB0; background: rgba(43,108,176,0.06);
  }
  &.correct-answer {
    border-color: #38A169; background: rgba(56,161,105,0.08);
  }
  &.wrong-answer {
    border-color: #E53E3E; background: rgba(229,62,62,0.08);
  }
}
.opt-label {
  width: 44rpx; height: 44rpx; border-radius: 50%;
  background: #E2E8F0; color: #475569;
  display: flex; align-items: center; justify-content: center;
  font-size: 24rpx; font-weight: 600; flex-shrink: 0;
}
.opt-text { font-size: 28rpx; color: #1E293B; line-height: 1.6; flex: 1; }

/* 填空 */
.fill-area { margin-top: 8rpx; }
.fill-input {
  width: 100%; height: 88rpx; background: #F8FAFC;
  border: 2rpx solid #E2E8F0; border-radius: 14rpx;
  padding: 0 24rpx; font-size: 30rpx;
}

/* 反馈 */
.feedback-area { margin-top: 24rpx; }
.feedback-box {
  display: flex; align-items: center; gap: 12rpx;
  padding: 20rpx; border-radius: 14rpx;
  &.correct { background: rgba(56,161,105,0.08); }
  &.wrong { background: rgba(229,62,62,0.08); }
}
.feedback-icon { font-size: 36rpx; font-weight: 700; }
.feedback-box.correct .feedback-icon { color: #38A169; }
.feedback-box.wrong .feedback-icon { color: #E53E3E; }
.feedback-box.correct .feedback-text { color: #276749; font-weight: 600; }
.feedback-box.wrong .feedback-text { color: #9B2C2C; font-weight: 600; }

.correct-answer {
  margin-top: 12rpx; padding: 16rpx 20rpx;
  background: #F0FDF4; border-radius: 12rpx;
  border-left: 4rpx solid #38A169;
}
.answer-label { font-size: 24rpx; color: #38A169; font-weight: 600; }
.answer-text { font-size: 24rpx; color: #276749; }

.analysis-box {
  margin-top: 16rpx; padding: 16rpx 20rpx;
  background: #FFFBEB; border-radius: 12rpx;
  border-left: 4rpx solid #F59E0B;
}
.analysis-title { font-size: 24rpx; color: #92400E; font-weight: 600; }
.analysis-body { margin-top: 8rpx; font-size: 24rpx; color: #78350F; line-height: 1.6; }

.btn-next {
  margin-top: 24rpx; background: linear-gradient(135deg, #2B6CB0, #3182CE);
  border-radius: 14rpx; padding: 24rpx 0; text-align: center;
  color: #fff; font-size: 30rpx; font-weight: 600;
  &:active { opacity: 0.85; }
}

/* 底部按钮 */
.bottom-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 20rpx 24rpx;
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.btn-submit {
  background: linear-gradient(135deg, #2B6CB0, #3182CE);
  border-radius: 14rpx; padding: 26rpx 0; text-align: center;
  color: #fff; font-size: 30rpx; font-weight: 600;
  &:active { opacity: 0.85; }
}
</style>
