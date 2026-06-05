<template>
  <view class="result-page">
    <!-- 原图预览 -->
    <view class="image-section" v-if="image_url">
      <image :src="image_url" class="result-image" mode="aspectFit" @tap="previewImage" />
      <view class="confidence-badge" v-if="confidence">
        置信度 {{ (confidence * 100).toFixed(0) }}%
      </view>
    </view>

    <!-- OCR 识别结果 -->
    <view class="result-section">
      <view class="section-header">
        <text class="section-title">📝 LaTeX 识别结果</text>
        <text class="copy-btn" @tap="copyText(result_latex)">复制</text>
      </view>
      <view class="result-box">
        <textarea class="result-textarea" v-model="result_latex" placeholder="识别结果将显示在这里" auto-height />
      </view>
    </view>

    <view class="result-section">
      <view class="section-header">
        <text class="section-title">📖 文本预览</text>
      </view>
      <view class="result-box">
        <text class="preview-text">{{ latexToUnicode(result_latex) }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-bar safe-area-bottom">
      <view class="action-btn btn-secondary" @tap="correctResult">
        <text>✏️ 纠正</text>
      </view>
      <view class="action-btn btn-primary" @tap="showQuickSave = true">
        <text>💾 一键入库</text>
      </view>
      <view class="action-btn btn-outline" @tap="goEditPage">
        <text>📝 编辑入库</text>
      </view>
    </view>

    <!-- 一键入库弹窗 -->
    <view v-if="showQuickSave" class="modal-mask" @tap="showQuickSave = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">保存到题库</text>

        <text class="modal-label">题型</text>
        <view class="modal-types">
          <view v-for="(t, key) in types" :key="key"
                :class="['modal-type', saveForm.question_type === key ? 'active' : '']"
                @tap="saveForm.question_type = key">
            <text>{{ t.icon }} {{ t.label }}</text>
          </view>
        </view>

        <text class="modal-label">难度</text>
        <view class="modal-diff">
          <view v-for="i in 5" :key="i"
                :class="['diff-dot', saveForm.difficulty >= i ? 'active' : '']"
                @tap="saveForm.difficulty = i">
            <text>{{ ['极易','较易','中等','较难','极难'][i-1] }}</text>
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
import { ocrAPI, questionsAPI } from '../../utils/api.js'
import { latexToUnicode, QUESTION_TYPES } from '../../utils/util.js'

export default {
  data() {
    return {
      record_id: '',
      image_url: '',
      result_latex: '',
      result_text: '',
      confidence: 0,
      showQuickSave: false,
      saveForm: {
        question_type: 'choice',
        difficulty: 3,
        source: '',
      },
      types: QUESTION_TYPES,
    }
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
      } catch (e) {
        console.error('解析数据失败', e)
      }
    }
  },
  methods: {
    latexToUnicode,
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
    correctResult() {
      uni.showModal({
        title: '纠正识别结果',
        editable: true,
        placeholderText: '输入正确的内容',
        content: this.result_latex,
        success: async (res) => {
          if (res.confirm && res.content) {
            this.result_latex = res.content
            try {
              await ocrAPI.correct({
                record_id: this.record_id,
                corrected_latex: res.content,
              })
              uni.showToast({ title: '已纠正', icon: 'success' })
            } catch (e) {}
          }
        },
      })
    },
    async quickSave() {
      if (!this.result_latex.trim()) {
        return uni.showToast({ title: '识别内容为空', icon: 'none' })
      }
      uni.showLoading({ title: '保存中...' })
      try {
        await questionsAPI.create({
          content: this.result_latex,
          answer: '',
          analysis: '',
          question_type: this.saveForm.question_type,
          difficulty: this.saveForm.difficulty,
          source: this.saveForm.source,
          options: this.saveForm.question_type === 'choice' ? [
            { label: 'A', text: '' }, { label: 'B', text: '' },
            { label: 'C', text: '' }, { label: 'D', text: '' },
          ] : [],
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
      const params = encodeURIComponent(JSON.stringify({
        content: this.result_latex,
        ocr_record_id: this.record_id,
      }))
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
.image-section {
  margin: 24rpx;
  border-radius: 20rpx;
  overflow: hidden;
  position: relative;
  background: #000;
}
.result-image { width: 100%; height: 400rpx; }
.confidence-badge {
  position: absolute; top: 16rpx; right: 16rpx;
  background: rgba(0,0,0,0.6); color: #fff;
  font-size: 22rpx; padding: 6rpx 16rpx; border-radius: 20rpx;
}
.result-section { margin: 0 24rpx 24rpx; }
.section-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx;
}
.section-title { font-size: 28rpx; font-weight: 600; color: #1F2937; }
.copy-btn { font-size: 24rpx; color: #4A6CF7; padding: 8rpx 16rpx; }
.result-box {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.result-textarea { width: 100%; min-height: 120rpx; font-size: 28rpx; line-height: 1.8; color: #1F2937; }
.preview-text { font-size: 30rpx; line-height: 1.8; color: #374151; white-space: pre-wrap; }

.action-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff; display: flex; gap: 12rpx;
  padding: 20rpx 24rpx;
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.action-btn {
  flex: 1; text-align: center; padding: 22rpx 0;
  border-radius: 16rpx; font-size: 26rpx; font-weight: 600;
}
.btn-primary { background: linear-gradient(135deg, #4A6CF7, #6B8AFF); color: #fff; }
.btn-secondary { background: #F3F4F6; color: #374151; }
.btn-outline { background: #fff; color: #4A6CF7; border: 2rpx solid #4A6CF7; }

/* 弹窗 */
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
  text-align: center; margin-bottom: 32rpx;
}
.modal-label {
  display: block; font-size: 26rpx; color: #6B7280;
  margin-bottom: 12rpx; margin-top: 20rpx;
}
.modal-types {
  display: flex; flex-wrap: wrap; gap: 12rpx;
}
.modal-type {
  padding: 12rpx 20rpx; border-radius: 12rpx;
  background: #F3F4F6; font-size: 24rpx; color: #6B7280;
  &.active { background: rgba(74,108,247,0.1); color: #4A6CF7; font-weight: 600; }
}
.modal-diff { display: flex; gap: 12rpx; }
.diff-dot {
  flex: 1; text-align: center; padding: 12rpx 0;
  border-radius: 12rpx; background: #F3F4F6;
  font-size: 22rpx; color: #6B7280;
  &.active { background: #F59E0B; color: #fff; font-weight: 600; }
}
.modal-input {
  width: 100%; height: 80rpx; background: #F5F6FA;
  border-radius: 12rpx; padding: 0 20rpx; font-size: 26rpx;
}
.modal-actions {
  display: flex; gap: 20rpx; margin-top: 32rpx;
}
.modal-btn {
  flex: 1; text-align: center; padding: 24rpx 0;
  border-radius: 16rpx; font-size: 30rpx; font-weight: 600;
}
.modal-btn.cancel { background: #F3F4F6; color: #6B7280; }
.modal-btn.confirm { background: #4A6CF7; color: #fff; }
</style>
