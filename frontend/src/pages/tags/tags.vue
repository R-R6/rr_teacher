<template>
  <view class="tags-page">
    <view v-for="(group, type) in groupedTags" :key="type" class="tag-group">
      <view class="group-header">
        <text class="group-icon">{{ getGroupIcon(type) }}</text>
        <text class="group-title">{{ getGroupName(type) }}</text>
        <text class="group-count">{{ group.length }}个标签</text>
      </view>
      <view class="tag-list">
        <view v-for="tag in group" :key="tag.id" class="tag-item">
          <view class="tag-name">
            <text>{{ tag.name }}</text>
            <text class="tag-count" v-if="tag.children && tag.children.length">({{ tag.children.length }}子项)</text>
          </view>
          <text class="tag-del" @tap="handleDelete(tag.id, tag.name)">删除</text>
        </view>
      </view>
    </view>

    <!-- 添加标签 -->
    <view class="add-section">
      <text class="section-title">添加标签</text>
      <view class="add-form">
        <input class="add-input" v-model="newTagName" placeholder="标签名称" />
        <picker :range="typeOptions" range-key="label" @change="newTagType = typeOptions[$event.detail.value].key">
          <view class="add-picker">{{ getGroupName(newTagType) }} ▾</view>
        </picker>
        <view class="add-btn" @tap="handleAdd">添加</view>
      </view>
    </view>
  </view>
</template>

<script>
import { tagsAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      tags: [],
      newTagName: '',
      newTagType: 'knowledge',
      typeOptions: [
        { key: 'book', label: '教材版本' },
        { key: 'knowledge', label: '知识点' },
        { key: 'type', label: '题型' },
        { key: 'difficulty', label: '难度' },
      ],
    }
  },
  computed: {
    groupedTags() {
      const groups = {}
      for (const tag of this.tags) {
        const type = tag.tag_type || 'other'
        if (!groups[type]) groups[type] = []
        groups[type].push(tag)
      }
      return groups
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
    getGroupName(type) {
      const map = { book: '教材版本', knowledge: '知识点', type: '题型', difficulty: '难度', other: '其他' }
      return map[type] || type
    },
    getGroupIcon(type) {
      const map = { book: '📚', knowledge: '💡', type: '📋', difficulty: '⚡', other: '🏷️' }
      return map[type] || '🏷️'
    },
    async handleAdd() {
      if (!this.newTagName.trim()) {
        return uni.showToast({ title: '请输入标签名', icon: 'none' })
      }
      try {
        await tagsAPI.create({ name: this.newTagName, tag_type: this.newTagType })
        this.newTagName = ''
        uni.showToast({ title: '添加成功', icon: 'success' })
        this.loadTags()
      } catch (e) {}
    },
    handleDelete(id, name) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除标签「${name}」吗？`,
        confirmColor: '#EF4444',
        success: async (res) => {
          if (res.confirm) {
            try {
              await tagsAPI.delete(id)
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
  padding: 24rpx;
}
.tag-group {
  margin-bottom: 28rpx;
}
.group-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}
.group-icon { font-size: 28rpx; }
.group-title { font-size: 28rpx; font-weight: 600; color: #1F2937; }
.group-count { font-size: 22rpx; color: #9CA3AF; margin-left: auto; }
.tag-list {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.tag-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
  &:last-child { border-bottom: none; }
}
.tag-name {
  font-size: 28rpx;
  color: #374151;
}
.tag-count { font-size: 22rpx; color: #9CA3AF; margin-left: 8rpx; }
.tag-del { font-size: 24rpx; color: #EF4444; padding: 8rpx 16rpx; }
.add-section {
  margin-top: 20rpx;
}
.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 12rpx;
}
.add-form {
  display: flex;
  gap: 12rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.add-input {
  flex: 1;
  height: 72rpx;
  background: #F5F6FA;
  border-radius: 12rpx;
  padding: 0 16rpx;
  font-size: 26rpx;
}
.add-picker {
  height: 72rpx;
  line-height: 72rpx;
  background: #F5F6FA;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  color: #374151;
}
.add-btn {
  height: 72rpx;
  line-height: 72rpx;
  background: #4A6CF7;
  color: #fff;
  border-radius: 12rpx;
  padding: 0 28rpx;
  font-size: 26rpx;
  font-weight: 500;
}
</style>
