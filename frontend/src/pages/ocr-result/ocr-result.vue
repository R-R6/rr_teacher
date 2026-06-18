<template>
  <view class="result-page">
    <view class="image-section" v-if="image_url">
      <image :src="image_url" class="result-image" mode="aspectFit" @tap="previewImage" />
      <view class="confidence-badge" v-if="confidence">
        置信度 {{ (confidence * 100).toFixed(0) }}%
      </view>
      <view v-if="engine" class="engine-badge" :class="`engine-badge--${engineClass}`">
        {{ engineLabel }}
      </view>
    </view>

    <view v-if="images && images.length" class="figure-section">
      <view class="section-header">
        <text class="section-title">识别出的附图 {{ images.length }} 张</text>
      </view>
      <scroll-view scroll-x class="figure-scroll">
        <view
          v-for="(img, idx) in images"
          :key="idx"
          class="figure-card"
          @tap="previewFigure(img.image_url)"
        >
          <image :src="img.image_url" class="figure-image" mode="aspectFit" />
          <text v-if="img.image_type" class="figure-type">{{ img.image_type }}</text>
        </view>
      </scroll-view>
    </view>

    <view v-if="showFigureSuggestion" class="figure-tip">
      <text class="figure-tip__title">附图建议</text>
      <text class="figure-tip__body">{{ figureSuggestionText }}</text>
    </view>

    <view v-if="error" class="error-bar">提示：{{ error }}</view>

    <view class="result-section">
      <view class="section-header">
        <text class="section-title">{{ editableSectionTitle }}</text>
        <text class="copy-btn" @tap="copyText(editableContent)">复制</text>
      </view>
      <view class="result-box">
        <textarea
          class="result-textarea"
          v-model="editableContent"
          placeholder="识别结果将显示在这里，可直接修改后再入库"
          auto-height
        />
      </view>
    </view>

    <view v-if="showFormulaPanel" class="result-section">
      <view class="section-header">
        <text class="section-title">公式结果（参考）</text>
        <text class="copy-btn" @tap="copyText(result_latex)">复制</text>
      </view>
      <view class="result-box">
        <text class="preview-text">{{ result_latex }}</text>
      </view>
    </view>

    <view v-if="showReviewPanel" class="result-section">
      <view class="section-header">
        <text class="section-title">结构化识别提示</text>
      </view>
      <view class="result-box">
        <view v-if="structured && structured.review_notes && structured.review_notes.length">
          <text
            v-for="(note, idx) in structured.review_notes"
            :key="idx"
            class="review-note"
          >
            {{ idx + 1 }}. {{ note }}
          </text>
        </view>
        <text v-else class="preview-text">当前无额外提示</text>
      </view>
    </view>

    <view class="action-bar safe-area-bottom">
      <view class="action-btn btn-primary" @tap="showQuickSave = true">
        <text>快速保存</text>
      </view>
      <view class="action-btn btn-outline" @tap="goEditPage">
        <text>编辑入库</text>
      </view>
    </view>

    <view v-if="showQuickSave" class="modal-mask" @tap="showQuickSave = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">保存到题库</text>
        <text class="modal-label">题型</text>
        <view class="modal-types">
          <view
            v-for="(t, key) in types"
            :key="key"
            :class="['modal-type', saveForm.question_type === key ? 'active' : '']"
            @tap="saveForm.question_type = key"
          >
            <text>{{ t.icon }} {{ t.label }}</text>
          </view>
        </view>
        <text class="modal-label">难度</text>
        <view class="modal-diff">
          <view
            v-for="i in 5"
            :key="i"
            :class="['diff-dot', saveForm.difficulty >= i ? 'active' : '']"
            @tap="saveForm.difficulty = i"
          >
            <text>{{ ['极易', '较易', '中等', '较难', '极难'][i - 1] }}</text>
          </view>
        </view>
        <text class="modal-label">来源（选填）</text>
        <input class="modal-input" v-model="saveForm.source" placeholder="如：2024高考全国卷" />
        <view class="modal-actions">
          <view class="modal-btn cancel" @tap="showQuickSave = false">取消</view>
          <view class="modal-btn confirm" @tap="quickSave">确认保存</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { questionsAPI } from '../../utils/api.js'
import { QUESTION_TYPES } from '../../utils/util.js'

export default {
  data() {
    return {
      record_id: '',
      image_url: '',
      result_latex: '',
      result_text: '',
      editableContent: '',
      confidence: 0,
      engine: '',
      error: '',
      images: [],
      structured: null,
      showQuickSave: false,
      saveForm: {
        question_type: 'choice',
        difficulty: 3,
        source: '',
      },
      types: QUESTION_TYPES,
    }
  },
  computed: {
    engineClass() {
      if (this.engine === 'tesseract') return 'tesseract'
      if (this.engine && this.engine.startsWith('pix2text')) return 'pix2text'
      if (this.engine === 'doubao_vision') return 'doubao'
      return 'other'
    },
    engineLabel() {
      if (this.engine === 'tesseract') return '极速识别（Tesseract）'
      if (this.engine === 'pix2text_online') return '高精度（Pix2Text 在线）'
      if (this.engine === 'pix2text_local') return '高精度（Pix2Text 本地）'
      if (this.engine === 'doubao_vision') return '高精度（豆包视觉）'
      return this.engine || ''
    },
    editableSectionTitle() {
      return this.engine === 'pix2text_online' ? '识别结果（可编辑）' : '题目正文（可编辑）'
    },
    showFormulaPanel() {
      return this.engine === 'pix2text_online' && !!this.result_latex && this.result_latex !== this.editableContent
    },
    showReviewPanel() {
      return this.engine === 'doubao_vision' && !!this.structured
    },
    showFigureSuggestion() {
      return !!(this.structured && this.structured.figure_analysis)
    },
    figureSuggestionText() {
      const figureAnalysis = this.structured?.figure_analysis
      if (!figureAnalysis) return ''
      if (figureAnalysis.should_keep_original) {
        return figureAnalysis.description || '这道题包含附图，建议保留原图并在入库页继续处理。'
      }
      return figureAnalysis.description || '当前题目未检测到需要单独保留的附图。'
    },
  },
  onLoad(options) {
    if (options.data) {
      try {
        const data = JSON.parse(decodeURIComponent(options.data))
        this.record_id = data.record_id || ''
        this.image_url = data.origin_image_url || ''
        this.result_latex = data.result_latex || ''
        this.result_text = data.result_text || ''
        this.confidence = data.confidence || 0
        this.engine = data.engine || ''
        this.error = data.error || ''
        this.images = data.images || []
        this.structured = data.structured || null
        this.editableContent = this.resolveEditableContent(data)
      } catch (e) {
        console.error('解析识别结果失败', e)
      }
    }
  },
  methods: {
    resolveEditableContent(data) {
      const structuredQuestion = data.structured?.question_text || ''
      if (this.engine === 'doubao_vision' && structuredQuestion) return structuredQuestion
      if (data.result_text) return data.result_text
      if (data.result_latex) return data.result_latex
      return ''
    },
    copyText(text) {
      uni.setClipboardData({
        data: text,
        success: () => uni.showToast({ title: '已复制', icon: 'success' }),
      })
    },
    previewImage() {
      if (this.image_url) {
        uni.previewImage({ urls: [this.image_url], current: this.image_url })
      }
    },
    previewFigure(url) {
      if (url) {
        uni.previewImage({ urls: [url], current: url })
      }
    },
    async quickSave() {
      if (!this.editableContent.trim()) {
        return uni.showToast({ title: '识别内容为空', icon: 'none' })
      }
      uni.showLoading({ title: '保存中...' })
      try {
        await questionsAPI.create({
          content: this.editableContent,
          answer: '',
          analysis: '',
          question_type: this.saveForm.question_type,
          difficulty: this.saveForm.difficulty,
          source: this.saveForm.source,
          options: this.saveForm.question_type === 'choice'
            ? [
              { label: 'A', text: '' },
              { label: 'B', text: '' },
              { label: 'C', text: '' },
              { label: 'D', text: '' },
            ]
            : [],
          tag_ids: [],
          ocr_record_id: this.record_id || undefined,
        })
        uni.hideLoading()
        this.showQuickSave = false
        uni.showModal({
          title: '保存成功',
          content: '题目已保存到题库，是否继续识别？',
          confirmText: '继续识别',
          cancelText: '返回题库',
          success: (res) => {
            if (res.confirm) {
              uni.navigateBack()
            } else {
              uni.switchTab({ url: '/pages/questions/questions' })
            }
          },
        })
      } catch (e) {
        uni.hideLoading()
      }
    },
    goEditPage() {
      const params = encodeURIComponent(
        JSON.stringify({
          content: this.editableContent,
          raw_latex: this.result_latex,
          raw_text: this.result_text,
          structured: this.structured,
          ocr_record_id: this.record_id,
        }),
      )
      uni.navigateTo({
        url: `/pages/question-edit/question-edit?data=${params}`,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.result-page {
  min-height: 100vh;
  background: #F5F6FA;
  padding-bottom: 160rpx;
}

.error-bar,
.figure-tip {
  margin: 0 24rpx 16rpx;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  line-height: 1.6;
}

.error-bar {
  background: #FEF3C7;
  color: #92400E;
}

.figure-tip {
  background: #EEF2FF;
  color: #3730A3;
}

.figure-tip__title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.figure-tip__body {
  display: block;
}

.figure-section {
  margin: 0 24rpx 24rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.figure-scroll {
  white-space: nowrap;
}

.figure-card {
  display: inline-block;
  width: 280rpx;
  height: 280rpx;
  margin-right: 16rpx;
  background: #F3F4F6;
  border-radius: 12rpx;
  position: relative;
  overflow: hidden;
}

.figure-image {
  width: 100%;
  height: 100%;
}

.figure-type {
  position: absolute;
  bottom: 8rpx;
  left: 8rpx;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 20rpx;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
}

.image-section {
  margin: 24rpx;
  border-radius: 20rpx;
  overflow: hidden;
  position: relative;
  background: #000;
}

.result-image {
  width: 100%;
  height: 400rpx;
}

.confidence-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.engine-badge {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;

  &--tesseract { background: rgba(34, 197, 94, 0.85); color: #fff; }
  &--pix2text { background: rgba(139, 92, 246, 0.9); color: #fff; }
  &--doubao { background: rgba(59, 130, 246, 0.9); color: #fff; }
  &--other { background: rgba(107, 114, 128, 0.85); color: #fff; }
}

.result-section {
  margin: 0 24rpx 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
}

.copy-btn {
  font-size: 24rpx;
  color: #4A6CF7;
  padding: 8rpx 16rpx;
}

.result-box {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.result-textarea {
  width: 100%;
  min-height: 200rpx;
  font-size: 28rpx;
  line-height: 1.8;
  color: #1F2937;
}

.preview-text,
.review-note {
  display: block;
  font-size: 30rpx;
  line-height: 1.8;
  color: #374151;
  white-space: pre-wrap;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  display: flex;
  gap: 16rpx;
  padding: 20rpx 24rpx;
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.action-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #4A6CF7, #6B8AFF);
  color: #fff;
  box-shadow: 0 4rpx 16rpx rgba(74, 108, 247, 0.25);
}

.btn-outline {
  background: #fff;
  color: #4A6CF7;
  border: 2rpx solid #4A6CF7;
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  width: 100%;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 40rpx 32rpx;
  padding-bottom: calc(40rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}

.modal-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
  text-align: center;
  margin-bottom: 32rpx;
}

.modal-label {
  display: block;
  font-size: 26rpx;
  color: #6B7280;
  margin-bottom: 12rpx;
  margin-top: 20rpx;
}

.modal-types {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.modal-type {
  padding: 12rpx 20rpx;
  border-radius: 12rpx;
  background: #F3F4F6;
  font-size: 24rpx;
  color: #6B7280;

  &.active {
    background: rgba(74, 108, 247, 0.1);
    color: #4A6CF7;
    font-weight: 600;
  }
}

.modal-diff {
  display: flex;
  gap: 12rpx;
}

.diff-dot {
  flex: 1;
  text-align: center;
  padding: 12rpx 0;
  border-radius: 12rpx;
  background: #F3F4F6;
  font-size: 22rpx;
  color: #6B7280;

  &.active {
    background: #F59E0B;
    color: #fff;
    font-weight: 600;
  }
}

.modal-input {
  width: 100%;
  height: 80rpx;
  background: #F5F6FA;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
}

.modal-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 32rpx;
}

.modal-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.modal-btn.cancel {
  background: #F3F4F6;
  color: #6B7280;
}

.modal-btn.confirm {
  background: #4A6CF7;
  color: #fff;
}
</style>
