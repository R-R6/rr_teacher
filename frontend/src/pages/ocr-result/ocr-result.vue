<template>
  <view class="result-page">
    <view class="image-section" v-if="imageUrl">
      <image :src="imageUrl" class="result-image" mode="aspectFit" @tap="previewImage" />
      <view class="quality-badge">
        <text class="quality-badge__label">{{ qualityInfo.label }}</text>
        <text class="quality-badge__note">{{ qualityInfo.note }}</text>
      </view>
      <view v-if="engineInfo" class="engine-badge" :class="`engine-badge--${engineInfo.theme}`">
        <text class="engine-badge__primary">{{ engineInfo.primary }}</text>
        <text class="engine-badge__secondary">{{ engineInfo.secondary }}</text>
      </view>
    </view>

    <view v-if="imageUrl" class="preview-action" @tap="previewImage">
      <text>查看原图</text>
    </view>

    <view v-if="reviewTipText" class="review-tip">
      <text class="review-tip__title">{{ showFigureSuggestion ? '建议补拍附图' : '建议人工复核' }}</text>
      <text class="review-tip__body">{{ reviewTipText }}</text>
      <view v-if="showFigureSuggestion" class="review-tip__action" @tap="goEditPage(true)">去补拍附图</view>
    </view>

    <view v-if="images.length" class="figure-section">
      <view class="section-header">
        <text class="section-title">当前题目附图 {{ images.length }} 张</text>
      </view>
      <scroll-view scroll-x class="figure-scroll">
        <view
          v-for="(img, idx) in images"
          :key="img.id || idx"
          class="figure-card"
          @tap="previewFigure(img.image_url)"
        >
          <image :src="img.image_url" class="figure-image" mode="aspectFit" />
          <text v-if="img.image_type" class="figure-type">{{ img.image_type }}</text>
        </view>
      </scroll-view>
    </view>

    <view v-if="error" class="error-bar">提示：{{ error }}</view>

    <view class="result-section">
      <view class="section-header">
        <text class="section-title">题目正文（可快速修改）</text>
        <text class="copy-btn" @tap="copyText(editableContent)">复制</text>
      </view>
      <view class="result-box">
        <textarea
          :key="textareaKey"
          class="result-textarea"
          :value="editableContent"
          auto-height
          maxlength="-1"
          placeholder="识别后的题目正文会显示在这里，可先改几个错字或漏字，再快速保存。"
          @input="handleEditableInput"
        />
      </view>
    </view>

    <view v-if="showFormulaPanel" class="result-section">
      <view class="section-header">
        <text class="section-title">公式识别结果（参考）</text>
        <text class="copy-btn" @tap="copyText(resultLatex)">复制</text>
      </view>
      <view class="result-box">
        <text class="preview-text">{{ resultLatex }}</text>
      </view>
    </view>

    <view class="action-bar safe-area-bottom">
      <view class="action-btn btn-primary" @tap="showQuickSave = true">
        <text>快速保存</text>
      </view>
      <view class="action-btn btn-outline" @tap="goEditPage(false)">
        <text>编辑入库</text>
      </view>
    </view>

    <view v-if="showQuickSave" class="modal-mask" @tap="showQuickSave = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">保存到题库</text>
        <text class="modal-label">题型</text>
        <view class="modal-types">
          <view
            v-for="(item, key) in types"
            :key="key"
            :class="['modal-type', saveForm.question_type === key ? 'active' : '']"
            @tap="saveForm.question_type = key"
          >
            <text>{{ item.icon }} {{ item.label }}</text>
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
            <text>{{ difficultyLabels[i - 1] }}</text>
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
import {
  buildQuestionContent,
  buildOcrEditData,
  getQualitySummary,
  shouldSuggestSupplementalFigure,
} from '../../utils/ocr-result-helpers.js'

const ENGINE_LABELS = {
  tesseract: { primary: '极速识别', secondary: 'Tesseract', theme: 'tesseract' },
  pix2text_online: { primary: '高精度识别（公式）', secondary: 'Pix2Text', theme: 'pix2text' },
  pix2text_local: { primary: '高精度识别（公式）', secondary: 'Pix2Text', theme: 'pix2text' },
  doubao_vision: { primary: '高精度识别（复杂题）', secondary: '豆包视觉', theme: 'doubao' },
}

export default {
  data() {
    return {
      recordId: '',
      imageUrl: '',
      resultLatex: '',
      resultText: '',
      editableContent: '',
      confidence: 0,
      engine: '',
      error: '',
      images: [],
      structured: null,
      textareaKey: 0,
      showQuickSave: false,
      saveForm: {
        question_type: 'choice',
        difficulty: 3,
        source: '',
      },
      types: QUESTION_TYPES,
      difficultyLabels: ['极易', '较易', '中等', '较难', '极难'],
    }
  },
  computed: {
    engineInfo() {
      return ENGINE_LABELS[this.engine] || null
    },
    qualityInfo() {
      return getQualitySummary({
        confidence: this.confidence,
        structured: this.structured,
      })
    },
    showFormulaPanel() {
      return this.engine && this.engine.startsWith('pix2text') && this.resultLatex && this.resultLatex !== this.editableContent
    },
    showFigureSuggestion() {
      return shouldSuggestSupplementalFigure({
        content: this.editableContent,
        images: this.images,
        structured: this.structured,
        result_text: this.resultText,
        result_latex: this.resultLatex,
      })
    },
    reviewTipText() {
      if (this.showFigureSuggestion) {
        return '检测到这道题可能包含流程图、装置图或结构图，建议在编辑入库页补拍或维护题目附图。'
      }
      if (this.qualityInfo.needsReview) {
        return '这次识别结果建议再复核一遍。小问题可以直接修改后快速保存，复杂问题再进入编辑入库。'
      }
      return ''
    },
  },
  onLoad(options) {
    if (!options.data) return
    try {
      const data = JSON.parse(decodeURIComponent(options.data))
      this.recordId = data.record_id || ''
      this.imageUrl = data.origin_image_url || ''
      this.resultLatex = data.result_latex || ''
      this.resultText = data.result_text || ''
      this.confidence = data.confidence || 0
      this.engine = data.engine || ''
      this.error = data.error || ''
      this.images = data.images || []
      this.structured = data.structured || null
      this.editableContent = buildQuestionContent(data)
      this.textareaKey += 1
    } catch (error) {
      console.error('解析识别结果失败', error)
    }
  },
  methods: {
    handleEditableInput(event) {
      this.editableContent = event.detail.value
    },
    copyText(text) {
      uni.setClipboardData({
        data: text,
        success: () => uni.showToast({ title: '已复制', icon: 'success' }),
      })
    },
    previewImage() {
      if (!this.imageUrl) return
      uni.previewImage({ urls: [this.imageUrl], current: this.imageUrl })
    },
    previewFigure(url) {
      if (!url) return
      uni.previewImage({ urls: [url], current: url })
    },
    async quickSave() {
      if (!this.editableContent.trim()) {
        uni.showToast({ title: '识别内容为空', icon: 'none' })
        return
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
          source_image_url: this.imageUrl || undefined,
          ocr_record_id: this.recordId || undefined,
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
          }
        })
      } catch (error) {
        uni.hideLoading()
      }
    },
    goEditPage(focusFigureSection) {
      const editData = buildOcrEditData({
        rawContent: this.editableContent || '',
        recordId: this.recordId || '',
        imageUrl: this.imageUrl || '',
        engine: this.engine || '',
        structured: this.structured || null,
        focusFigure: !!focusFigureSection,
      })

      try {
        uni.setStorageSync('ocrEditData', editData)
        uni.removeStorageSync('ocrMinimalData')
      } catch (e) {
        console.error('[OCR] 存储失败:', e)
        uni.showToast({ title: '准备编辑数据失败', icon: 'none' })
        return
      }

      uni.navigateTo({
        url: `/pages/question-edit/question-edit`,
        fail: (err) => {
          console.error('[OCR] 跳转失败:', err)
          uni.showToast({ title: '跳转失败', icon: 'none' })
        }
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

.quality-badge,
.engine-badge {
  position: absolute;
  top: 16rpx;
  border-radius: 20rpx;
  padding: 8rpx 16rpx;
  display: flex;
  flex-direction: column;
}

.quality-badge {
  right: 16rpx;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  align-items: flex-end;
}

.quality-badge__label {
  font-size: 22rpx;
}

.quality-badge__note {
  font-size: 18rpx;
  opacity: 0.8;
}

.engine-badge {
  left: 16rpx;
  color: #fff;

  &--tesseract { background: rgba(34, 197, 94, 0.88); }
  &--pix2text { background: rgba(139, 92, 246, 0.92); }
  &--doubao { background: rgba(59, 130, 246, 0.92); }
  &--other { background: rgba(107, 114, 128, 0.88); }
}

.engine-badge__primary {
  font-size: 24rpx;
  font-weight: 600;
}

.engine-badge__secondary {
  font-size: 18rpx;
  opacity: 0.9;
}

.preview-action,
.review-tip,
.error-bar {
  margin: 0 24rpx 16rpx;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  line-height: 1.6;
}

.preview-action {
  background: #fff;
  color: #4A6CF7;
  text-align: center;
  font-weight: 600;
}

.review-tip {
  background: #EEF2FF;
  color: #3730A3;
}

.review-tip__title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.review-tip__body {
  display: block;
}

.review-tip__action {
  margin-top: 14rpx;
  color: #4A6CF7;
  font-size: 24rpx;
  font-weight: 600;
}

.error-bar {
  background: #FEF3C7;
  color: #92400E;
}

.figure-section,
.result-box {
  background: #fff;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.figure-section,
.result-section {
  margin: 0 24rpx 24rpx;
}

.figure-section {
  padding: 20rpx 24rpx;
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
  padding: 24rpx;
}

.result-textarea {
  width: 100%;
  min-height: 360rpx;
  font-size: 28rpx;
  line-height: 1.8;
  color: #1F2937;
}

.preview-text {
  display: block;
  font-size: 28rpx;
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
  inset: 0;
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
