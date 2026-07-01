<template>
  <view class="edit-page">
    <view v-if="figureHint" class="figure-hint">
      <text class="figure-hint__title">题目附图提醒</text>
      <text class="figure-hint__body">{{ figureHint }}</text>
    </view>

    <view class="form-section">
      <text class="section-title">题目内容 *</text>
      <textarea
        class="form-textarea"
        v-model="form.content"
        placeholder="输入题目内容"
        maxlength="-1"
        auto-height
      />
    </view>

    <view class="form-section">
      <text class="section-title">答案 *</text>
      <textarea
        class="form-textarea"
        v-model="form.answer"
        placeholder="输入答案"
        maxlength="-1"
        auto-height
      />
    </view>

    <view class="form-section">
      <text class="section-title">解析</text>
      <textarea
        class="form-textarea"
        v-model="form.analysis"
        placeholder="输入题目解析"
        maxlength="-1"
        auto-height
      />
    </view>

    <view class="form-section">
      <text class="section-title">题目附图</text>
      <view v-if="form.images.length" class="figure-grid">
        <view
          v-for="(img, index) in form.images"
          :key="img.id || img.image_url || index"
          class="figure-item"
        >
          <image :src="img.image_url" class="figure-item__image" mode="aspectFit" @tap="previewImage(img.image_url)" />
          <view class="figure-item__footer">
            <text class="figure-item__type">{{ imageTypeLabel(img) }}</text>
            <text class="figure-item__delete" @tap="removeImage(index)">删除</text>
          </view>
        </view>
      </view>
      <view v-else class="empty-figure">
        <text>当前还没有题目附图</text>
      </view>
      <view class="figure-actions">
        <view class="figure-btn primary" @tap="captureFigure">补拍附图</view>
        <view class="figure-btn" @tap="chooseFigureFromAlbum">从相册添加</view>
      </view>
    </view>

    <view class="form-section">
      <text class="section-title">题型</text>
      <view class="type-grid">
        <view
          v-for="(item, key) in types"
          :key="key"
          :class="['type-item', form.question_type === key ? 'active' : '']"
          :style="form.question_type === key ? { borderColor: item.color, background: item.color + '10' } : {}"
          @tap="form.question_type = key"
        >
          <text class="type-icon">{{ item.icon }}</text>
          <text class="type-label" :style="form.question_type === key ? { color: item.color } : {}">
            {{ item.label }}
          </text>
        </view>
      </view>
    </view>

    <view class="form-section">
      <text class="section-title">难度</text>
      <view class="difficulty-bar">
        <view
          v-for="i in difficultyLabels.length"
          :key="i"
          :class="['diff-item', form.difficulty >= i ? 'active' : '']"
          :style="form.difficulty >= i ? { background: getDiffColor(i) } : {}"
          @tap="form.difficulty = i"
        >
          <text class="diff-text">{{ getDiffLabel(i) }}</text>
        </view>
      </view>
    </view>

    <view class="form-section">
      <text class="section-title">来源</text>
      <input class="form-input" v-model="form.source" placeholder="如：2024高考全国卷" />
    </view>

    <view class="form-section">
      <text class="section-title">教材版本</text>
      <picker :range="bookTagNames" :value="selectedBookIndex" @change="onBookTagChange">
        <view class="picker-trigger">
          <text v-if="selectedBookTag" class="picker-text">{{ selectedBookTag.name }}</text>
          <text v-else class="picker-placeholder">点击选择教材版本</text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
    </view>

    <view class="form-section">
      <view class="section-header-row">
        <text class="section-title">知识点标签</text>
        <text class="section-helper">可多选</text>
      </view>
      <view class="knowledge-grid">
        <view
          v-for="tag in knowledgeTags"
          :key="tag.id"
          :class="['knowledge-chip', selectedKnowledgeIds.includes(tag.id) ? 'knowledge-chip--active' : '']"
          @tap="toggleKnowledgeTag(tag.id)"
        >
          <text :class="['knowledge-chip__text', selectedKnowledgeIds.includes(tag.id) ? 'knowledge-chip__text--active' : '']">{{ tag.name }}</text>
        </view>
      </view>
      <view v-if="selectedKnowledgeTags.length" class="selected-tags">
        <view v-for="tag in selectedKnowledgeTags" :key="tag.id" class="selected-tag" @tap="toggleKnowledgeTag(tag.id)">
          <text>{{ tag.name }}</text>
          <text class="tag-del">×</text>
        </view>
      </view>
    </view>

    <view class="form-section" v-if="form.question_type === 'choice'">
      <text class="section-title">选项</text>
      <view v-for="(opt, index) in form.options" :key="index" class="option-row">
        <picker
          class="option-label-picker"
          :range="optionLabels"
          :value="optionLabelPickerValue(opt.label)"
          @change="changeOptionLabel(index, $event)"
        >
          <text class="option-label">{{ opt.label }}</text>
        </picker>
        <input class="option-input" v-model="opt.text" :placeholder="`选项${opt.label}内容`" />
        <text class="option-del" v-if="form.options.length > 2" @tap="removeOption(index)">×</text>
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
import { questionsAPI, tagsAPI, uploadAPI } from '../../utils/api.js'
import { DIFFICULTY_LEVELS, QUESTION_TYPES } from '../../utils/util.js'
import { buildDifficultyLabels } from '../../utils/difficulty.js'
import { buildTypeConfigs } from '../../utils/type-config.js'
import { buildOcrEditData, getNextOptionLabel, sortOptionsByLabel } from '../../utils/ocr-result-helpers.js'

export default {
  data() {
    return {
      isEdit: false,
      questionId: '',
      figureHint: '',
      form: {
        content: '',
        answer: '',
        analysis: '',
        question_type: 'choice',
        difficulty: 3,
        source: '',
        source_image_url: '',
        options: [
          { label: 'A', text: '' },
          { label: 'B', text: '' },
          { label: 'C', text: '' },
          { label: 'D', text: '' },
        ],
        tag_ids: [],
        images: [],
      },
      allTags: [],
      difficultyTags: [],
      typeTags: [],
      pendingOcrEditData: null,
      optionLabels: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    }
  },
  computed: {
    difficultyLabels() {
      return buildDifficultyLabels(this.difficultyTags, DIFFICULTY_LEVELS)
    },
    types() {
      return buildTypeConfigs(this.typeTags, QUESTION_TYPES)
    },
    bookTags() {
      return this.allTags
        .filter(tag => tag.tag_type === 'book')
        .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
    },
    bookTagNames() {
      return this.bookTags.map(tag => tag.name)
    },
    selectedBookTag() {
      return this.bookTags.find(tag => this.form.tag_ids.includes(tag.id)) || null
    },
    selectedBookIndex() {
      if (!this.selectedBookTag) return 0
      const index = this.bookTags.findIndex(tag => tag.id === this.selectedBookTag.id)
      return index >= 0 ? index : 0
    },
    knowledgeTags() {
      return this.allTags
        .filter(tag => tag.tag_type === 'knowledge')
        .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
    },
    selectedKnowledgeIds() {
      return this.form.tag_ids.filter(id => this.knowledgeTags.some(tag => tag.id === id))
    },
    selectedKnowledgeTags() {
      return this.knowledgeTags.filter(tag => this.selectedKnowledgeIds.includes(tag.id))
    },
  },
  onLoad(options) {
    console.log('[EditPage] onLoad 启动', options)

    if (options.id) {
      console.log('[EditPage] 编辑已有题目:', options.id)
      this.isEdit = true
      this.questionId = options.id
      this.loadTags()
      this.loadQuestion()
      return
    }

    this.pendingOcrEditData = this.readStoredOcrData()
  },
  onReady() {
    if (this.isEdit) return
    this.processOcrData()
    this.loadTags()
  },
  onUnload() {
    // 页面卸载时无需再手动移除事件监听
  },
  methods: {
    readStoredOcrData() {
      const editData = uni.getStorageSync('ocrEditData')
      const minimalData = editData ? null : uni.getStorageSync('ocrMinimalData')
      uni.removeStorageSync('ocrEditData')
      uni.removeStorageSync('ocrMinimalData')
      return editData || minimalData
    },
    processOcrData() {
      console.log('[EditPage] processOcrData 开始')
      try {
        const data = this.pendingOcrEditData || this.readStoredOcrData()
        this.pendingOcrEditData = null
        if (!data) {
          console.log('[EditPage] 没有OCR数据')
          return
        }

        const editData = data.content || data.options || data.source_image_url
          ? data
          : buildOcrEditData(data)
        const nextForm = { ...this.form }

        nextForm.content = editData.content || ''
        nextForm.source_image_url = editData.source_image_url || ''
        if (editData.ocr_record_id) {
          nextForm.ocr_record_id = editData.ocr_record_id
        }
        if (editData.question_type) {
          nextForm.question_type = editData.question_type
        }

        if (Array.isArray(editData.options) && editData.options.length) {
          nextForm.options = sortOptionsByLabel(editData.options.map(opt => ({
            label: String(opt.label || '').toUpperCase(),
            text: opt.text || '',
          })).filter(opt => opt.label))
        }

        this.form = nextForm
        this.figureHint = editData.focusFigure
          ? '这道题可能带有流程图、装置图或结构图，建议先补拍或维护题目附图。'
          : ''

      } catch (e) {
        console.error('[EditPage] 处理OCR数据失败:', e)
      }
    },

    handleOcrData(data) {
      // 保留旧方法兼容性
      console.log('[EditPage] handleOcrData (compat)', data)
    },
    getDiffColor(level) {
      const config = DIFFICULTY_LEVELS[level] || {}
      return config.color || '#F59E0B'
    },
    getDiffLabel(level) {
      return this.difficultyLabels[level - 1] || ''
    },
    imageTypeLabel(image) {
      if (image.image_type === 'manual_figure') return '手动附图'
      if (image.image_type === 'figure') return '附图'
      return image.image_type || '附图'
    },
    onBookTagChange(event) {
      const nextTag = this.bookTags[event.detail.value]
      const nextIds = this.form.tag_ids.filter(id => !this.bookTags.some(tag => tag.id === id))
      if (nextTag) {
        nextIds.push(nextTag.id)
      }
      this.form.tag_ids = nextIds
    },
    toggleKnowledgeTag(tagId) {
      const nextIds = this.form.tag_ids.filter(id => !this.knowledgeTags.some(tag => tag.id === id))
      const selected = this.selectedKnowledgeIds.includes(tagId)
      const knowledgeIds = selected
        ? this.selectedKnowledgeIds.filter(id => id !== tagId)
        : [...this.selectedKnowledgeIds, tagId]
      this.form.tag_ids = [...nextIds, ...knowledgeIds]
    },
    optionLabelPickerValue(label) {
      const index = this.optionLabels.indexOf(String(label || '').toUpperCase())
      return index >= 0 ? index : 0
    },
    changeOptionLabel(index, event) {
      const nextLabel = this.optionLabels[event.detail.value]
      if (!nextLabel) return

      const options = this.form.options.map(opt => ({ ...opt }))
      const currentLabel = String((options[index] && options[index].label) || '').toUpperCase()
      const targetIndex = options.findIndex((opt, optIndex) =>
        optIndex !== index && String(opt.label || '').toUpperCase() === nextLabel
      )

      options[index].label = nextLabel
      if (targetIndex >= 0 && currentLabel) {
        options[targetIndex].label = currentLabel
      }
      this.form.options = sortOptionsByLabel(options)
    },
    addOption() {
      const next = getNextOptionLabel(this.form.options)
      this.form.options = sortOptionsByLabel([
        ...this.form.options,
        { label: next, text: '' },
      ])
    },
    removeOption(index) {
      this.form.options.splice(index, 1)
    },
    removeImage(index) {
      this.form.images.splice(index, 1)
    },
    previewImage(url) {
      uni.previewImage({ urls: [url], current: url })
    },
    async uploadFigure(filePath) {
      uni.showLoading({ title: '上传附图中...' })
      try {
        const result = await uploadAPI.image(filePath, 'question_figure')
        this.form.images.push({
          image_url: result.url,
          image_type: 'manual_figure',
          fromOcr: false,
        })
      } finally {
        uni.hideLoading()
      }
    },
    captureFigure() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['camera'],
        success: async (res) => {
          await this.uploadFigure(res.tempFilePaths[0])
        },
      })
    },
    chooseFigureFromAlbum() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album'],
        success: async (res) => {
          await this.uploadFigure(res.tempFilePaths[0])
        },
      })
    },
    async loadTags() {
      try {
        const result = await tagsAPI.list()
        const flat = []
        const flatten = (nodes) => {
          for (const node of nodes) {
            flat.push(node)
            if (node.children && node.children.length) flatten(node.children)
          }
        }
        flatten(result || [])
        this.allTags = flat
        // 提取难度标签，按 sort_order 排序
        this.difficultyTags = flat
          .filter(tag => tag.tag_type === 'difficulty')
          .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
        this.typeTags = flat
          .filter(tag => tag.tag_type === 'type')
          .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      } catch (error) {
        console.error(error)
      }
    },
    async loadQuestion() {
      try {
        const result = await questionsAPI.detail(this.questionId)
        this.form.content = result.content || ''
        this.form.answer = result.answer || ''
        this.form.analysis = result.analysis || ''
        this.form.question_type = result.question_type || 'choice'
        this.form.difficulty = result.difficulty || 3
        this.form.source = result.source || ''
        this.form.source_image_url = result.source_image_url || ''
        this.form.options = result.options && result.options.length ? result.options : this.form.options
        this.form.tag_ids = result.tags ? result.tags.map(tag => tag.id) : []
        this.form.images = Array.isArray(result.images) ? result.images.map(image => ({ ...image, fromOcr: false })) : []
      } catch (error) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    serializeImagesForSubmit() {
      return (this.form.images || []).map(image => ({
        ...(image.id ? { id: image.id } : {}),
        image_url: image.image_url,
        image_type: image.image_type || 'figure',
      }))
    },
    async handleSubmit() {
      if (!this.form.content.trim()) {
        uni.showToast({ title: '请输入题目内容', icon: 'none' })
        return
      }

      uni.showLoading({ title: '保存中...' })
      const payload = {
        ...this.form,
        images: this.serializeImagesForSubmit(),
      }
      try {
        if (this.isEdit) {
          await questionsAPI.update(this.questionId, payload)
        } else {
          await questionsAPI.create(payload)
        }
        uni.hideLoading()
        uni.showToast({ title: this.isEdit ? '修改成功' : '创建成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 500)
      } catch (error) {
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
  padding-bottom: 200rpx;
}

.figure-hint {
  margin-bottom: 24rpx;
  padding: 20rpx;
  background: #EEF2FF;
  border-radius: 16rpx;
  color: #3730A3;
  font-size: 24rpx;
  line-height: 1.6;
}

.figure-hint__title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.figure-hint__body {
  display: block;
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

.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.section-helper {
  font-size: 22rpx;
  color: #94A3B8;
}

.form-textarea {
  width: 100%;
  min-height: 180rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
  line-height: 1.7;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.figure-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.figure-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.figure-item__image {
  width: 100%;
  height: 240rpx;
  border-radius: 12rpx;
  background: #F3F4F6;
}

.figure-item__footer {
  margin-top: 10rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.figure-item__type {
  font-size: 22rpx;
  color: #6B7280;
}

.figure-item__delete {
  font-size: 22rpx;
  color: #EF4444;
}

.empty-figure {
  padding: 24rpx;
  border-radius: 16rpx;
  background: #fff;
  color: #9CA3AF;
  font-size: 26rpx;
}

.figure-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 16rpx;
}

.figure-btn {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  border-radius: 14rpx;
  background: #fff;
  color: #4A6CF7;
  border: 2rpx solid #DDE5FF;
  font-size: 26rpx;
  font-weight: 600;
}

.figure-btn.primary {
  background: rgba(74, 108, 247, 0.1);
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
}

.type-icon {
  font-size: 28rpx;
}

.type-label {
  font-size: 24rpx;
  color: #6B7280;
}

.difficulty-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.diff-item {
  flex: 0 0 calc((100% - 48rpx) / 5);
  box-sizing: border-box;
  text-align: center;
  padding: 16rpx 0;
  border-radius: 12rpx;
  background: #F3F4F6;
}

.diff-item.active .diff-text {
  color: #fff;
  font-weight: 600;
}

.diff-text {
  font-size: 24rpx;
  color: #6B7280;
}

.picker-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.picker-text {
  font-size: 28rpx;
  color: #4A6CF7;
  font-weight: 600;
}

.picker-placeholder {
  font-size: 28rpx;
  color: #9CA3AF;
}

.picker-arrow {
  font-size: 28rpx;
  color: #D1D5DB;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.knowledge-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.knowledge-chip {
  min-height: 64rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #FFFFFF;
  box-shadow: inset 0 0 0 2rpx #E5E7EB;
  display: flex;
  align-items: center;
}

.knowledge-chip--active {
  background: rgba(74, 108, 247, 0.12);
  box-shadow: inset 0 0 0 2rpx rgba(74, 108, 247, 0.24);
}

.knowledge-chip__text {
  font-size: 24rpx;
  color: #64748B;
}

.knowledge-chip__text--active {
  color: #3155D4;
  font-weight: 600;
}

.selected-tag {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #4A6CF7;
  background: rgba(74, 108, 247, 0.1);
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
}

.tag-del {
  font-size: 20rpx;
  color: #9CA3AF;
  margin-left: 8rpx;
}

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
  line-height: 48rpx;
}

.option-label-picker {
  width: 48rpx;
  height: 48rpx;
  flex: 0 0 48rpx;
}

.option-input {
  flex: 1;
  height: 72rpx;
  background: #fff;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
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
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.btn-submit {
  background: linear-gradient(135deg, #4A6CF7, #6B8AFF);
  border-radius: 16rpx;
  padding: 26rpx 0;
  text-align: center;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}
</style>
