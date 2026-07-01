<template>
  <view class="tags-page">
    <view class="page-header">
      <view class="page-header__title">
        <text class="page-header__heading">标签管理</text>
        <text class="page-header__subtext">教材版本、知识点、题型和难度都可以在这里维护</text>
      </view>
      <view class="page-header__summary">
        <text class="page-header__summary-number">{{ currentTabTags.length }}</text>
        <text class="page-header__summary-label">{{ activeTab === 'all' ? '全部标签' : CATEGORY_NAMES[activeTab] }}</text>
      </view>
    </view>

    <view class="tab-bar">
      <scroll-view scroll-x class="tab-scroll" show-scrollbar="false">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ 'tab-item--active': activeTab === tab.key }"
          @tap="activeTab = tab.key"
        >
          <text class="tab-item__text">{{ tab.label }}</text>
          <text class="tab-item__count" v-if="tab.key !== 'all'">{{ getCountByType(tab.key) }}</text>
        </view>
      </scroll-view>
    </view>

    <scroll-view scroll-y class="content-scroll">
      <view class="toolbar-card">
        <view class="toolbar-card__top">
          <view>
            <text class="toolbar-card__title">{{ activeTab === 'all' ? '新增知识点标签' : `新增${CATEGORY_NAMES[activeTab]}` }}</text>
            <text class="toolbar-card__hint">支持新增、重命名、上下调整顺序和安全删除</text>
          </view>
        </view>
        <view class="add-row">
          <view class="add-input-wrap">
            <input
              class="add-input"
              v-model="newTagName"
              :placeholder="`输入${activeTab === 'all' ? '知识点' : CATEGORY_NAMES[activeTab]}名称`"
              confirm-type="done"
              maxlength="50"
              @confirm="handleAdd"
            />
          </view>
          <view
            class="add-button"
            :class="{ 'add-button--disabled': !canAdd }"
            :style="{ background: getTabColor(activeTab) }"
            @tap="handleAdd"
          >
            <text class="add-button__text">新增</text>
          </view>
        </view>
      </view>

      <view v-if="currentTabTags.length === 0" class="empty-state">
        <text class="empty-state__icon">标签</text>
        <text class="empty-state__title">当前分类还没有标签</text>
        <text class="empty-state__hint">先新增一个，后面可以继续改名和调整顺序</text>
      </view>

      <view v-else class="tag-list">
        <view v-for="(tag, index) in currentTabTags" :key="tag.id" class="tag-card">
          <view class="tag-card__main">
            <view class="tag-card__meta">
              <view class="tag-dot" :style="{ background: getTypeColor(tag.tag_type) }"></view>
              <view class="tag-card__text">
                <text class="tag-card__name">{{ tag.name }}</text>
                <view class="tag-card__badges">
                  <text class="tag-card__badge">{{ getCategoryLabel(tag.tag_type) }}</text>
                  <text v-if="tag.tag_type === 'difficulty'" class="tag-card__badge tag-card__badge--accent">难度 {{ index + 1 }}</text>
                  <text v-if="tag.tag_type === 'type'" class="tag-card__badge tag-card__badge--accent">题型 {{ index + 1 }}</text>
                  <text class="tag-card__badge">排序 {{ tag.sort_order || index + 1 }}</text>
                </view>
              </view>
            </view>

            <view class="tag-actions">
              <view class="tag-action" :class="{ 'tag-action--disabled': index === 0 }" @tap="moveTag(tag, -1, index)">
                <text class="tag-action__text">上移</text>
              </view>
              <view class="tag-action" :class="{ 'tag-action--disabled': index === currentTabTags.length - 1 }" @tap="moveTag(tag, 1, index)">
                <text class="tag-action__text">下移</text>
              </view>
              <view class="tag-action tag-action--primary" @tap="openEdit(tag)">
                <text class="tag-action__text tag-action__text--primary">编辑</text>
              </view>
              <view class="tag-action tag-action--danger" @tap="confirmDelete(tag)">
                <text class="tag-action__text tag-action__text--danger">删除</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view v-if="showEditModal" class="modal-mask" @tap="closeEdit">
      <view class="modal-panel" @tap.stop>
        <text class="modal-panel__title">编辑标签</text>
        <text class="modal-panel__subtitle">{{ editingTag ? getCategoryLabel(editingTag.tag_type) : '' }}</text>
        <view class="modal-field">
          <text class="modal-field__label">标签名称</text>
          <view class="modal-field__input-wrap">
            <input
              class="modal-field__input"
              v-model="editForm.name"
              maxlength="50"
              placeholder="输入新的标签名称"
            />
          </view>
        </view>
        <view class="modal-field">
          <text class="modal-field__label">排序位置</text>
          <view class="modal-stepper">
            <view class="modal-stepper__button" @tap="changeEditSort(-1)">
              <text class="modal-stepper__button-text">-</text>
            </view>
            <text class="modal-stepper__value">{{ editForm.sort_order }}</text>
            <view class="modal-stepper__button" @tap="changeEditSort(1)">
              <text class="modal-stepper__button-text">+</text>
            </view>
          </view>
        </view>
        <view class="modal-actions">
          <view class="modal-actions__button modal-actions__button--secondary" @tap="closeEdit">
            <text class="modal-actions__button-text modal-actions__button-text--secondary">取消</text>
          </view>
          <view class="modal-actions__button" @tap="submitEdit">
            <text class="modal-actions__button-text">保存</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { tagsAPI } from '../../utils/api.js'

const CATEGORY_NAMES = {
  book: '教材版本',
  knowledge: '知识点',
  type: '题型',
  difficulty: '难度',
}

const TYPE_COLORS = {
  book: '#2563EB',
  knowledge: '#0F766E',
  type: '#EA580C',
  difficulty: '#CA8A04',
}

const TAB_COLORS = {
  all: '#334155',
  book: '#2563EB',
  knowledge: '#0F766E',
  type: '#EA580C',
  difficulty: '#CA8A04',
}

export default {
  data() {
    return {
      tags: [],
      activeTab: 'all',
      newTagName: '',
      showEditModal: false,
      editingTag: null,
      editForm: {
        name: '',
        sort_order: 1,
      },
      CATEGORY_NAMES,
      tabs: [
        { key: 'all', label: '全部' },
        { key: 'book', label: '教材版本' },
        { key: 'knowledge', label: '知识点' },
        { key: 'type', label: '题型' },
        { key: 'difficulty', label: '难度' },
      ],
    }
  },
  computed: {
    canAdd() {
      return !!this.newTagName.trim()
    },
    currentTabTags() {
      const source = this.activeTab === 'all'
        ? this.tags.filter((tag) => tag.tag_type === 'knowledge')
        : this.tags.filter((tag) => tag.tag_type === this.activeTab)

      return source.slice().sort((a, b) => {
        const bySort = (a.sort_order || 0) - (b.sort_order || 0)
        if (bySort !== 0) return bySort
        return String(a.name || '').localeCompare(String(b.name || ''))
      })
    },
  },
  onShow() {
    this.loadTags()
  },
  methods: {
    async loadTags() {
      try {
        const result = await tagsAPI.list({})
        this.tags = Array.isArray(result) ? result : []
      } catch (error) {
        console.error('加载标签失败', error)
      }
    },
    getCountByType(type) {
      return this.tags.filter((tag) => tag.tag_type === type).length
    },
    getCategoryLabel(type) {
      return CATEGORY_NAMES[type] || type
    },
    getTypeColor(type) {
      return TYPE_COLORS[type] || '#94A3B8'
    },
    getTabColor(key) {
      return TAB_COLORS[key] || '#334155'
    },
    currentCreateType() {
      return this.activeTab === 'all' ? 'knowledge' : this.activeTab
    },
    async handleAdd() {
      const name = this.newTagName.trim()
      if (!name) return

      try {
        await tagsAPI.create({
          name,
          tag_type: this.currentCreateType(),
        })
        this.newTagName = ''
        uni.showToast({ title: '新增成功', icon: 'success' })
        await this.loadTags()
      } catch (error) {
        console.error('新增标签失败', error)
      }
    },
    openEdit(tag) {
      const maxOrder = Math.max(1, this.currentTabTags.length)
      this.editingTag = tag
      this.editForm = {
        name: tag.name,
        sort_order: Math.min(Math.max(tag.sort_order || 1, 1), maxOrder),
      }
      this.showEditModal = true
    },
    closeEdit() {
      this.showEditModal = false
      this.editingTag = null
      this.editForm = {
        name: '',
        sort_order: 1,
      }
    },
    changeEditSort(delta) {
      const maxOrder = Math.max(1, this.currentTabTags.length)
      const next = this.editForm.sort_order + delta
      this.editForm.sort_order = Math.min(Math.max(next, 1), maxOrder)
    },
    async submitEdit() {
      if (!this.editingTag) return

      const name = this.editForm.name.trim()
      if (!name) {
        uni.showToast({ title: '请输入标签名称', icon: 'none' })
        return
      }

      try {
        await tagsAPI.update(this.editingTag.id, {
          name,
          sort_order: this.editForm.sort_order,
        })
        uni.showToast({ title: '修改成功', icon: 'success' })
        this.closeEdit()
        await this.loadTags()
      } catch (error) {
        console.error('更新标签失败', error)
      }
    },
    async moveTag(tag, direction, index) {
      if (direction < 0 && index === 0) return
      if (direction > 0 && index === this.currentTabTags.length - 1) return

      const sibling = this.currentTabTags[index + direction]
      if (!sibling) return

      try {
        await tagsAPI.update(tag.id, {
          name: tag.name,
          sort_order: sibling.sort_order || index + direction + 1,
        })
        await tagsAPI.update(sibling.id, {
          name: sibling.name,
          sort_order: tag.sort_order || index + 1,
        })
        await this.loadTags()
      } catch (error) {
        console.error('移动标签失败', error)
      }
    },
    confirmDelete(tag) {
      uni.showModal({
        title: '确认删除',
        content: `删除“${tag.name}”后将无法恢复。如果该标签已被题目使用，系统会阻止删除。`,
        confirmColor: '#DC2626',
        success: async (res) => {
          if (!res.confirm) return
          try {
            await tagsAPI.delete(tag.id)
            uni.showToast({ title: '删除成功', icon: 'success' })
            await this.loadTags()
          } catch (error) {
            console.error('删除标签失败', error)
          }
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.tags-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.08), transparent 32%),
    linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
  padding: 28rpx 24rpx 16rpx;
}

.page-header__title {
  flex: 1;
}

.page-header__heading {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #0F172A;
}

.page-header__subtext {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: #64748B;
}

.page-header__summary {
  min-width: 132rpx;
  padding: 18rpx 20rpx;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 10rpx 30rpx rgba(15, 23, 42, 0.06);
  text-align: center;
}

.page-header__summary-number {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #111827;
}

.page-header__summary-label {
  display: block;
  margin-top: 6rpx;
  font-size: 20rpx;
  color: #64748B;
}

.tab-bar {
  padding: 0 24rpx 16rpx;
}

.tab-scroll {
  white-space: nowrap;
}

.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  padding: 18rpx 22rpx;
  margin-right: 12rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.8);
  color: #64748B;
  box-shadow: inset 0 0 0 2rpx rgba(148, 163, 184, 0.12);
}

.tab-item--active {
  background: #FFFFFF;
  color: #0F172A;
  box-shadow: 0 12rpx 28rpx rgba(15, 23, 42, 0.08);
}

.tab-item__text {
  font-size: 26rpx;
  font-weight: 600;
}

.tab-item__count {
  font-size: 22rpx;
  color: #94A3B8;
}

.content-scroll {
  flex: 1;
  padding: 0 24rpx 28rpx;
}

.toolbar-card,
.tag-card,
.empty-state,
.modal-panel {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10rpx);
  border-radius: 22rpx;
  box-shadow: 0 14rpx 36rpx rgba(15, 23, 42, 0.07);
}

.toolbar-card {
  padding: 24rpx;
}

.toolbar-card__title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #0F172A;
}

.toolbar-card__hint {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #64748B;
}

.add-row {
  display: flex;
  gap: 16rpx;
  margin-top: 20rpx;
}

.add-input-wrap {
  flex: 1;
  height: 84rpx;
  padding: 0 22rpx;
  border-radius: 18rpx;
  background: #F8FAFC;
  box-shadow: inset 0 0 0 2rpx #E2E8F0;
  display: flex;
  align-items: center;
}

.add-input {
  width: 100%;
  font-size: 28rpx;
  color: #0F172A;
}

.add-button {
  min-width: 140rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 24rpx;
}

.add-button--disabled {
  opacity: 0.38;
}

.add-button__text {
  font-size: 28rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.empty-state {
  margin-top: 18rpx;
  padding: 80rpx 28rpx;
  text-align: center;
}

.empty-state__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 120rpx;
  height: 52rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #E2E8F0;
  color: #475569;
  font-size: 24rpx;
  font-weight: 600;
}

.empty-state__title {
  display: block;
  margin-top: 20rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #0F172A;
}

.empty-state__hint {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #64748B;
  line-height: 1.6;
}

.tag-list {
  margin-top: 18rpx;
}

.tag-card {
  padding: 22rpx 24rpx;
  margin-bottom: 14rpx;
}

.tag-card__meta {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
}

.tag-card__text {
  flex: 1;
  min-width: 0;
}

.tag-dot {
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  margin-top: 12rpx;
  flex-shrink: 0;
}

.tag-card__name {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.4;
  color: #0F172A;
  word-break: break-all;
}

.tag-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 12rpx;
}

.tag-card__badge {
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
  background: #F8FAFC;
  color: #64748B;
  font-size: 20rpx;
}

.tag-card__badge--accent {
  background: #E0F2FE;
  color: #0F766E;
}

.tag-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 20rpx;
}

.tag-action {
  min-width: 96rpx;
  height: 60rpx;
  padding: 0 18rpx;
  border-radius: 16rpx;
  background: #F8FAFC;
  box-shadow: inset 0 0 0 2rpx #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-action--disabled {
  opacity: 0.38;
}

.tag-action--primary {
  background: #E0F2FE;
  box-shadow: none;
}

.tag-action--danger {
  background: #FEF2F2;
  box-shadow: none;
}

.tag-action__text {
  font-size: 24rpx;
  font-weight: 600;
  color: #475569;
}

.tag-action__text--primary {
  color: #0369A1;
}

.tag-action__text--danger {
  color: #DC2626;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  display: flex;
  align-items: flex-end;
  z-index: 200;
}

.modal-panel {
  width: 100%;
  border-radius: 32rpx 32rpx 0 0;
  padding: 34rpx 28rpx 32rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
}

.modal-panel__title {
  display: block;
  text-align: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #0F172A;
}

.modal-panel__subtitle {
  display: block;
  text-align: center;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #64748B;
}

.modal-field {
  margin-top: 26rpx;
}

.modal-field__label {
  display: block;
  margin-bottom: 12rpx;
  font-size: 24rpx;
  color: #475569;
}

.modal-field__input-wrap {
  height: 86rpx;
  padding: 0 22rpx;
  border-radius: 18rpx;
  background: #F8FAFC;
  box-shadow: inset 0 0 0 2rpx #E2E8F0;
  display: flex;
  align-items: center;
}

.modal-field__input {
  width: 100%;
  font-size: 28rpx;
  color: #0F172A;
}

.modal-stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18rpx;
}

.modal-stepper__button {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  background: #F8FAFC;
  box-shadow: inset 0 0 0 2rpx #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-stepper__button-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #334155;
}

.modal-stepper__value {
  min-width: 96rpx;
  text-align: center;
  font-size: 30rpx;
  font-weight: 700;
  color: #0F172A;
}

.modal-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 32rpx;
}

.modal-actions__button {
  flex: 1;
  height: 88rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #2563EB, #1D4ED8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-actions__button--secondary {
  background: #F8FAFC;
  box-shadow: inset 0 0 0 2rpx #E2E8F0;
}

.modal-actions__button-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.modal-actions__button-text--secondary {
  color: #475569;
}
</style>
