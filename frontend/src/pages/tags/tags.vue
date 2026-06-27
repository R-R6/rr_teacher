<template>
  <view class="tags-page">
    <!-- 分类 Tab -->
    <view class="tab-bar">
      <scroll-view scroll-x class="tab-scroll">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ 'tab-active': activeTab === tab.key }"
          @tap="activeTab = tab.key"
        >
          <text class="tab-text" :style="activeTab === tab.key ? { color: getTabColor(tab.key), fontWeight: '700' } : {}">{{ tab.label }}</text>
          <text class="tab-count" v-if="tab.key !== 'all'">{{ getCountByType(tab.key) }}</text>
          <view v-if="activeTab === tab.key" class="tab-indicator" :style="{ background: getTabColor(tab.key) }"></view>
        </view>
      </scroll-view>
    </view>

    <!-- 标签列表 -->
    <scroll-view scroll-y class="tag-scroll">
      <view v-if="filteredTags.length === 0" class="empty-state">
        <text class="empty-icon">🏷️</text>
        <text class="empty-text">暂无{{ activeTab === 'all' ? '' : CATEGORY_NAMES[activeTab] }}标签</text>
        <text class="empty-hint">点击下方输入框添加</text>
      </view>

      <view v-else class="tag-list">
        <view
          v-for="tag in filteredTags"
          :key="tag.id"
          class="tag-item"
          @longpress="onTagLongpress(tag)"
        >
          <view class="tag-left">
            <view class="tag-dot" :style="{ background: getTypeColor(tag.tag_type) }"></view>
            <text class="tag-name">{{ tag.name }}</text>
          </view>
          <text class="tag-type-badge">{{ getCategoryLabel(tag.tag_type) }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- 底部添加栏 -->
    <view class="add-bar">
      <view class="add-input-wrap">
        <input
          class="add-input"
          v-model="newTagName"
          :placeholder="'添加' + (activeTab === 'all' ? '' : CATEGORY_NAMES[activeTab]) + '标签'"
          confirm-type="done"
          @confirm="handleAdd"
        />
      </view>
      <view class="add-btn" :style="{ background: getTabColor(activeTab) }" :class="{ 'add-btn-disabled': !newTagName.trim() }" @tap="handleAdd">
        <text class="add-btn-text">添加</text>
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
  book: '#3B82F6',
  knowledge: '#8B5CF6',
  type: '#F59E0B',
  difficulty: '#EF4444',
}

const TAB_COLORS = {
  all: '#4A6CF7',
  book: '#3B82F6',
  knowledge: '#8B5CF6',
  type: '#F59E0B',
  difficulty: '#EF4444',
}

export default {
  data() {
    return {
      tags: [],
      activeTab: 'all',
      newTagName: '',
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
    filteredTags() {
      if (this.activeTab === 'all') return this.tags
      return this.tags.filter((t) => t.tag_type === this.activeTab)
    },
  },
  onShow() {
    this.loadTags()
  },
  methods: {
    async loadTags() {
      try {
        this.tags = await tagsAPI.list({})
      } catch (e) {}
    },
    getCountByType(type) {
      return this.tags.filter((t) => t.tag_type === type).length
    },
    getCategoryLabel(type) {
      return CATEGORY_NAMES[type] || type
    },
    getTypeColor(type) {
      return TYPE_COLORS[type] || '#9CA3AF'
    },
    getTabColor(key) {
      return TAB_COLORS[key] || '#4A6CF7'
    },
    async handleAdd() {
      const name = this.newTagName.trim()
      if (!name) return

      const tagType = this.activeTab === 'all' ? 'knowledge' : this.activeTab
      try {
        await tagsAPI.create({ name, tag_type: tagType })
        this.newTagName = ''
        uni.showToast({ title: '添加成功', icon: 'success' })
        this.loadTags()
      } catch (e) {}
    },
    onTagLongpress(tag) {
      uni.showActionSheet({
        itemList: ['删除标签'],
        success: (res) => {
          if (res.tapIndex === 0) {
            this.confirmDelete(tag)
          }
        },
      })
    },
    confirmDelete(tag) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除标签「${tag.name}」吗？`,
        confirmColor: '#EF4444',
        success: async (res) => {
          if (res.confirm) {
            try {
              await tagsAPI.delete(tag.id)
              uni.showToast({ title: '已删除', icon: 'success' })
              this.loadTags()
            } catch (e) {}
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
  background: #F5F6FA;
  display: flex;
  flex-direction: column;
}

/* Tab 栏 */
.tab-bar {
  background: #fff;
  border-bottom: 1rpx solid #F3F4F6;
  flex-shrink: 0;
}
.tab-scroll {
  white-space: nowrap;
  padding: 0 16rpx;
}
.tab-item {
  display: inline-flex;
  align-items: center;
  padding: 24rpx 20rpx;
  margin: 0 4rpx;
  position: relative;
}
.tab-text {
  font-size: 28rpx;
  color: #6B7280;
  font-weight: 500;
}
.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 20rpx;
  right: 20rpx;
  height: 4rpx;
  border-radius: 2rpx;
}
.tab-count {
  font-size: 20rpx;
  color: #9CA3AF;
  margin-left: 6rpx;
}

/* 标签列表 */
.tag-scroll {
  flex: 1;
  padding: 16rpx 24rpx;
}
.tag-list {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.tag-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #F9FAFB;
  transition: background 150ms;
  &:last-child { border-bottom: none; }
  &:active { background: #F9FAFB; }
}
.tag-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.tag-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  flex-shrink: 0;
}
.tag-name {
  font-size: 28rpx;
  color: #1F2937;
}
.tag-type-badge {
  font-size: 22rpx;
  color: #9CA3AF;
  background: #F3F4F6;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 120rpx 0;
}
.empty-icon { font-size: 64rpx; display: block; margin-bottom: 16rpx; }
.empty-text { display: block; font-size: 28rpx; color: #9CA3AF; }
.empty-hint { display: block; font-size: 24rpx; color: #D1D5DB; margin-top: 8rpx; }

/* 底部添加栏 */
.add-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F3F4F6;
  flex-shrink: 0;
}
.add-input-wrap {
  flex: 1;
  background: #F5F6FA;
  border-radius: 16rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  padding: 0 20rpx;
}
.add-input {
  flex: 1;
  font-size: 28rpx;
  color: #1F2937;
}
.add-btn {
  border-radius: 16rpx;
  height: 80rpx;
  padding: 0 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity 150ms;
  &:active { opacity: 0.85; }
}
.add-btn-disabled {
  opacity: 0.4;
  &:active { opacity: 0.4; }
}
.add-btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #fff;
}
</style>
