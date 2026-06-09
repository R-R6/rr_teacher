<template>
  <view class="profile-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">👤 我的</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area" :style="{ paddingTop: navHeight + 'px' }">
      <!-- 用户信息卡片（点击编辑） -->
      <view class="user-card" @tap="showEditModal = true">
        <view class="avatar">
          <image v-if="user?.avatar_url" class="avatar-img" :src="user.avatar_url" mode="aspectFill" />
          <text v-else class="avatar-text">{{ (user?.nickname || user?.username || '?')[0] }}</text>
        </view>
        <view class="user-info">
          <text class="user-name">{{ user?.nickname || user?.username || '未登录' }}</text>
          <view class="user-role" :class="user?.role">
            {{ user?.role === 'teacher' ? '教师' : '学生' }}
          </view>
          <text class="user-school" v-if="user?.school">{{ user.school }}</text>
        </view>
        <text class="edit-arrow">编辑 ›</text>
      </view>

      <!-- 统计 -->
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-num">{{ stats.questions }}</text>
          <text class="stat-label">题目</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ stats.papers }}</text>
          <text class="stat-label">试卷</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ stats.ocr }}</text>
          <text class="stat-label">OCR识别</text>
        </view>
      </view>

      <!-- 功能列表 -->
      <view class="menu-card">
        <view class="menu-item" @tap="goTo('/pages/tags/tags')">
          <text class="menu-icon">🏷️</text>
          <text class="menu-text">标签管理</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @tap="initTags">
          <text class="menu-icon">🌱</text>
          <text class="menu-text">初始化预设标签</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-card">
        <view class="menu-item" @tap="viewAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于系统</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 退出登录 -->
      <view class="logout-btn" @tap="handleLogout">
        <text>退出登录</text>
      </view>
    </scroll-view>

    <!-- 编辑个人资料弹窗 -->
    <view v-if="showEditModal" class="sheet-mask" @tap="showEditModal = false">
      <view class="sheet" @tap.stop>
        <view class="sheet-handle"></view>
        <text class="sheet-title">编辑个人资料</text>

        <view class="profile-avatar-wrap">
          <button class="avatar-pick-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
            <image v-if="editAvatarUrl" class="avatar-preview" :src="editAvatarUrl" mode="aspectFill" />
            <image v-else-if="user?.avatar_url" class="avatar-preview" :src="user.avatar_url" mode="aspectFill" />
            <view v-else class="avatar-empty">
              <text class="avatar-plus">+</text>
            </view>
          </button>
          <text class="avatar-label">点击更换头像</text>
        </view>

        <view class="field" style="margin-top: 28rpx;">
          <input class="field-input" type="nickname" v-model="editNickname" :placeholder="user?.nickname || '请输入昵称'" placeholder-class="placeholder" />
        </view>

        <view class="sheet-btn-primary" @tap="saveProfile">
          <text class="btn-text">保存</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { tagsAPI, questionsAPI, papersAPI, ocrAPI, authAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      navHeight: 0,
      user: null,
      stats: { questions: 0, papers: 0, ocr: 0 },
      showEditModal: false,
      editNickname: '',
      editAvatarUrl: '',
    }
  },
  onLoad() {
    try {
      const sysInfo = uni.getSystemInfoSync()
      this.statusBarHeight = sysInfo.statusBarHeight || 20
    } catch (e) {
      this.statusBarHeight = 20
    }
    this.navHeight = this.statusBarHeight + 44
  },
  onShow() {
    this.loadUserInfo()
    this.loadStats()
  },
  methods: {
    loadUserInfo() {
      // 先从本地缓存加载
      const info = uni.getStorageSync('user_info')
      this.user = info ? (typeof info === 'string' ? JSON.parse(info) : info) : null
      // 再从后端刷新（获取最新头像昵称）
      authAPI.getMe().then(res => {
        this.user = res
        uni.setStorageSync('user_info', JSON.stringify(res))
      }).catch(() => {})
    },
    async loadStats() {
      try {
        const [q, p, o] = await Promise.all([
          questionsAPI.list({ page: 1, page_size: 1 }),
          papersAPI.list({ page: 1, page_size: 1 }),
          ocrAPI.history({ page: 1, page_size: 1 }),
        ])
        this.stats.questions = q.total || 0
        this.stats.papers = p.total || 0
        this.stats.ocr = o.total || 0
      } catch (e) {}
    },
    goTo(url) {
      uni.navigateTo({ url })
    },
    viewAbout() {
      uni.showModal({
        title: '高中化学教学辅助系统',
        content: '版本 1.0.0\n\n功能：拍照OCR识别化学题目、管理题库、智能组卷、导出Word试卷\n\n技术栈：uni-app + FastAPI + Pix2Text',
        showCancel: false,
      })
    },
    async initTags() {
      uni.showModal({
        title: '初始化标签',
        content: '将创建预设的高中化学标签，已有标签不会重复。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await tagsAPI.seed()
              uni.showToast({ title: '初始化成功', icon: 'success' })
            } catch (e) {}
          }
        },
      })
    },
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('access_token')
            uni.removeStorageSync('refresh_token')
            uni.removeStorageSync('user_info')
            uni.reLaunch({ url: '/pages/login/login' })
          }
        },
      })
    },
    onChooseAvatar(e) {
      if (e.detail.avatarUrl) this.editAvatarUrl = e.detail.avatarUrl
    },
    async saveProfile() {
      uni.showLoading({ title: '保存中...' })
      try {
        let avatarUrl = ''
        if (this.editAvatarUrl) {
          // #ifdef MP-WEIXIN
          if (wx && wx.cloud) {
            const r = await new Promise((res, rej) => {
              wx.cloud.uploadFile({
                cloudPath: `avatars/${Date.now()}_${Math.random().toString(36).slice(2,8)}.jpg`,
                filePath: this.editAvatarUrl, success: res, fail: rej
              })
            })
            avatarUrl = r.fileID
          }
          // #endif
        }
        const updateData = {}
        if (this.editNickname) updateData.nickname = this.editNickname
        if (avatarUrl) updateData.avatar_url = avatarUrl
        if (Object.keys(updateData).length > 0) {
          const updatedUser = await authAPI.updateMe(updateData)
          uni.setStorageSync('user_info', JSON.stringify(updatedUser))
          this.user = updatedUser
        }
        uni.hideLoading()
        this.showEditModal = false
        uni.showToast({ title: '保存成功', icon: 'success' })
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: '保存失败', icon: 'none' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: #F5F6FA;
}
.nav-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
}
.nav-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
}
.nav-title { font-size: 34rpx; font-weight: 700; color: #fff; }
.scroll-area { height: 100vh; }
.user-card {
  margin: 24rpx;
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  align-items: center;
  gap: 28rpx;
  color: #fff;
}
.avatar {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}
.avatar-img {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
}
.avatar-text {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
}
.user-name { display: block; font-size: 32rpx; font-weight: 700; margin-bottom: 4rpx; }
.user-role {
  display: inline-block;
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: rgba(255,255,255,0.2);
  margin-bottom: 4rpx;
}
.user-school { display: block; font-size: 22rpx; opacity: 0.8; }
.edit-arrow {
  font-size: 24rpx;
  color: rgba(255,255,255,0.7);
  flex-shrink: 0;
}
.stats-card {
  display: flex;
  background: #fff;
  border-radius: 20rpx;
  margin: 0 24rpx 24rpx;
  padding: 32rpx 0;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.stat-item { flex: 1; text-align: center; }
.stat-num { display: block; font-size: 36rpx; font-weight: 700; color: #8B5CF6; }
.stat-label { display: block; font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }
.stat-divider { width: 1rpx; background: #F3F4F6; }
.menu-card {
  background: #fff;
  border-radius: 20rpx;
  margin: 0 24rpx 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
  &:last-child { border-bottom: none; }
  &:active { background: #FAFBFC; }
}
.menu-icon { font-size: 32rpx; margin-right: 16rpx; }
.menu-text { flex: 1; font-size: 28rpx; color: #374151; }
.menu-arrow { font-size: 32rpx; color: #D1D5DB; }
.logout-btn {
  margin: 40rpx 24rpx;
  padding: 28rpx 0;
  text-align: center;
  background: #fff;
  border-radius: 16rpx;
  color: #EF4444;
  font-size: 30rpx;
  font-weight: 500;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #FEF2F2; }
}

/* 编辑弹窗 */
.sheet-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 200;
}
.sheet {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 20rpx 40rpx;
  padding-bottom: calc(60rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(60rpx + env(safe-area-inset-bottom));
  z-index: 201;
}
.sheet-handle {
  width: 60rpx; height: 8rpx;
  background: #E2E8F0; border-radius: 4rpx;
  margin: 0 auto 24rpx;
}
.sheet-title {
  display: block; font-size: 34rpx; font-weight: 700;
  color: #1E293B; text-align: center; margin-bottom: 28rpx;
}
.profile-avatar-wrap {
  display: flex; flex-direction: column; align-items: center;
}
.avatar-pick-btn {
  width: 144rpx; height: 144rpx; border-radius: 50%;
  background: #F1F5F9; display: flex; align-items: center; justify-content: center;
  padding: 0; margin: 0; line-height: normal;
  border: 3rpx dashed #CBD5E1;
}
.avatar-pick-btn::after { border: none; }
.avatar-preview { width: 144rpx; height: 144rpx; border-radius: 50%; }
.avatar-empty { display: flex; align-items: center; justify-content: center; width: 144rpx; height: 144rpx; }
.avatar-plus { font-size: 56rpx; color: #94A3B8; font-weight: 300; }
.avatar-label { font-size: 22rpx; color: #94A3B8; margin-top: 12rpx; }
.field {
  background: #F1F5F9; border-radius: 14rpx;
  padding: 0 28rpx; height: 92rpx;
  display: flex; align-items: center; margin-bottom: 20rpx;
}
.field-input { flex: 1; height: 92rpx; font-size: 28rpx; color: #1E293B; }
.placeholder { color: #94A3B8; font-size: 28rpx; }
.sheet-btn-primary {
  background: linear-gradient(135deg, #4A6CF7, #6366F1);
  border-radius: 14rpx; height: 88rpx;
  display: flex; align-items: center; justify-content: center;
  margin-top: 12rpx;
  &:active { opacity: 0.85; }
}
.btn-text { color: #fff; font-size: 30rpx; font-weight: 600; }
</style>
