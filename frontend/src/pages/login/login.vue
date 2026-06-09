<template>
  <view class="login-page">
    <!-- 顶部装饰区 -->
    <view class="header-area">
      <view class="header-bg"></view>
      <view class="header-content">
        <view class="brand-mark">
          <view class="brand-circle">
            <text class="brand-emoji">⚗️</text>
          </view>
        </view>
        <text class="app-name">小睿化学</text>
        <text class="app-slogan">化学老师的智能备课助手</text>
      </view>
    </view>

    <!-- 主卡片 -->
    <view class="card-area">
      <!-- Tab 切换 -->
      <view class="tabs">
        <view :class="['tab-item', mode === 'login' ? 'active' : '']" @tap="mode = 'login'">
          <text>登录</text>
          <view v-if="mode === 'login'" class="tab-indicator"></view>
        </view>
        <view :class="['tab-item', mode === 'register' ? 'active' : '']" @tap="mode = 'register'">
          <text>注册</text>
          <view v-if="mode === 'register'" class="tab-indicator"></view>
        </view>
      </view>

      <!-- 登录表单 -->
      <view v-if="mode === 'login'" class="form-area">
        <view class="field">
          <input class="field-input" v-model="loginForm.username" placeholder="请输入用户名" placeholder-class="placeholder" />
        </view>
        <view class="field">
          <input class="field-input" v-model="loginForm.password" type="password" placeholder="请输入密码" placeholder-class="placeholder" />
        </view>
        <view class="btn-primary" @tap="handleLogin">
          <text class="btn-text">登 录</text>
        </view>
      </view>

      <!-- 注册表单 -->
      <view v-if="mode === 'register'" class="form-area">
        <view class="field">
          <input class="field-input" v-model="registerForm.username" placeholder="用户名（2-50个字符）" placeholder-class="placeholder" />
        </view>
        <view class="field">
          <input class="field-input" v-model="registerForm.password" type="password" placeholder="密码（6-64个字符）" placeholder-class="placeholder" />
        </view>
        <view class="field">
          <input class="field-input" v-model="registerForm.phone" type="number" placeholder="手机号码（选填）" placeholder-class="placeholder" />
        </view>
        <view class="field">
          <input class="field-input" v-model="registerForm.school" placeholder="学校名称（选填）" placeholder-class="placeholder" />
        </view>
        <view class="role-row">
          <view :class="['role-chip', registerForm.role === 'teacher' ? 'active' : '']" @tap="registerForm.role = 'teacher'">
            <text>教师</text>
          </view>
          <view :class="['role-chip', registerForm.role === 'student' ? 'active' : '']" @tap="registerForm.role = 'student'">
            <text>学生</text>
          </view>
        </view>
        <view class="btn-primary" @tap="handleRegister">
          <text class="btn-text">注 册</text>
        </view>
      </view>

      <!-- 分割线 -->
      <view class="or-divider">
        <view class="or-line"></view>
        <text class="or-text">或</text>
        <view class="or-line"></view>
      </view>

      <!-- 微信一键登录 -->
      <view class="btn-wechat" @tap="handleWechatLogin">
        <view class="wechat-icon-wrap">
          <text class="wechat-icon-text">微信</text>
        </view>
        <text class="wechat-label">微信一键登录</text>
      </view>
    </view>

    <!-- 底部协议 -->
    <view class="footer-text">
      <text class="footer-tap">登录即表示同意</text>
      <text class="footer-link">《用户协议》</text>
      <text class="footer-tap">和</text>
      <text class="footer-link">《隐私政策》</text>
    </view>

    <!-- 头像昵称授权弹窗 -->
    <view v-if="showProfileModal" class="sheet-mask" @tap="skipProfile">
      <view class="sheet" @tap.stop>
        <view class="sheet-handle"></view>
        <text class="sheet-title">完善个人资料</text>
        <text class="sheet-desc">设置头像和昵称，让同事更容易认识您</text>

        <!-- 头像 -->
        <view class="profile-avatar-wrap">
          <button class="avatar-pick-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
            <image v-if="tempAvatarUrl" class="avatar-preview" :src="tempAvatarUrl" mode="aspectFill" />
            <view v-else class="avatar-empty">
              <text class="avatar-plus">+</text>
            </view>
          </button>
          <text class="avatar-label">点击选择头像</text>
        </view>

        <!-- 昵称 -->
        <view class="field" style="margin-top: 32rpx;">
          <input class="field-input" type="nickname" v-model="tempNickname" placeholder="请输入昵称" placeholder-class="placeholder" @blur="onNicknameBlur" />
        </view>

        <!-- 按钮 -->
        <view class="sheet-btn-primary" @tap="confirmProfile">
          <text class="btn-text">完成</text>
        </view>
        <view class="sheet-btn-text" @tap="skipProfile">
          <text>跳过，稍后设置</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { authAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      mode: 'login',
      loginForm: { username: '', password: '' },
      registerForm: { username: '', password: '', phone: '', school: '', role: 'teacher' },
      showProfileModal: false,
      tempAvatarUrl: '',
      tempNickname: '',
    }
  },
  methods: {
    async handleLogin() {
      if (!this.loginForm.username || !this.loginForm.password) {
        return uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
      }
      uni.showLoading({ title: '登录中...' })
      try {
        const res = await authAPI.login(this.loginForm)
        this.saveLoginData(res)
        uni.hideLoading()
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 500)
      } catch (e) { uni.hideLoading() }
    },
    async handleRegister() {
      if (!this.registerForm.username || !this.registerForm.password) {
        return uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
      }
      uni.showLoading({ title: '注册中...' })
      try {
        await authAPI.register(this.registerForm)
        uni.hideLoading()
        uni.showToast({ title: '注册成功，请登录', icon: 'success' })
        this.mode = 'login'
        this.loginForm.username = this.registerForm.username
        this.loginForm.password = this.registerForm.password
      } catch (e) { uni.hideLoading() }
    },
    async handleWechatLogin() {
      uni.showLoading({ title: '登录中...' })
      try {
        const loginRes = await new Promise((resolve, reject) => {
          uni.login({ provider: 'weixin', success: resolve, fail: reject })
        })
        const res = await authAPI.wechatLogin({ code: loginRes.code, nickname: '' })
        this.saveLoginData(res)
        uni.hideLoading()

        const userInfo = res.user
        const nickname = (userInfo.nickname || '').trim()
        if (!nickname || nickname.startsWith('微信用户')) {
          this.tempNickname = ''
          this.tempAvatarUrl = ''
          this.showProfileModal = true
        } else {
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 500)
        }
      } catch (e) { uni.hideLoading() }
    },
    onChooseAvatar(e) {
      if (e.detail.avatarUrl) this.tempAvatarUrl = e.detail.avatarUrl
    },
    onNicknameBlur(e) { this.tempNickname = e.detail.value || '' },
    async confirmProfile() {
      uni.showLoading({ title: '保存中...' })
      try {
        let avatarUrl = ''
        if (this.tempAvatarUrl) {
          // #ifdef MP-WEIXIN
          if (wx && wx.cloud) {
            const r = await new Promise((res, rej) => {
              wx.cloud.uploadFile({
                cloudPath: `avatars/${Date.now()}_${Math.random().toString(36).slice(2,8)}.jpg`,
                filePath: this.tempAvatarUrl, success: res, fail: rej
              })
            })
            avatarUrl = r.fileID
          }
          // #endif
        }
        const updateData = {}
        if (this.tempNickname) updateData.nickname = this.tempNickname
        if (avatarUrl) updateData.avatar_url = avatarUrl
        if (Object.keys(updateData).length > 0) {
          const updatedUser = await authAPI.updateMe(updateData)
          uni.setStorageSync('user_info', JSON.stringify(updatedUser))
        }
        uni.hideLoading()
        this.showProfileModal = false
        uni.showToast({ title: '设置成功', icon: 'success' })
        setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 500)
      } catch (e) {
        uni.hideLoading()
        this.showProfileModal = false
        uni.switchTab({ url: '/pages/index/index' })
      }
    },
    skipProfile() {
      this.showProfileModal = false
      uni.switchTab({ url: '/pages/index/index' })
    },
    saveLoginData(res) {
      uni.setStorageSync('access_token', res.access_token)
      uni.setStorageSync('refresh_token', res.refresh_token)
      uni.setStorageSync('user_info', JSON.stringify(res.user))
    },
  },
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: #F7F8FC;
}

/* ── 顶部区域 ── */
.header-area {
  position: relative;
  padding-top: 120rpx;
  padding-bottom: 80rpx;
}
.header-bg {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 420rpx;
  background: linear-gradient(160deg, #4A6CF7 0%, #6366F1 50%, #8B5CF6 100%);
  border-radius: 0 0 60rpx 60rpx;
}
.header-content {
  position: relative;
  z-index: 1;
  text-align: center;
}
.brand-mark { margin-bottom: 24rpx; }
.brand-circle {
  display: inline-flex;
  width: 120rpx; height: 120rpx;
  border-radius: 32rpx;
  background: rgba(255,255,255,0.2);
  align-items: center; justify-content: center;
}
.brand-emoji { font-size: 56rpx; }
.app-name {
  display: block;
  font-size: 48rpx;
  font-weight: 800;
  color: #fff;
  letter-spacing: 2rpx;
}
.app-slogan {
  display: block;
  font-size: 26rpx;
  color: rgba(255,255,255,0.75);
  margin-top: 8rpx;
}

/* ── 主卡片 ── */
.card-area {
  margin: -40rpx 32rpx 0;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 36rpx;
  position: relative;
  z-index: 2;
  box-shadow: 0 8rpx 40rpx rgba(74,108,247,0.08);
}

/* ── Tab ── */
.tabs {
  display: flex;
  margin-bottom: 40rpx;
}
.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 30rpx;
  color: #94A3B8;
  font-weight: 500;
  position: relative;
  &.active {
    color: #1E293B;
    font-weight: 700;
  }
}
.tab-indicator {
  position: absolute;
  bottom: 0; left: 35%; right: 35%;
  height: 6rpx;
  background: #4A6CF7;
  border-radius: 3rpx;
}

/* ── 表单字段 ── */
.field {
  background: #F1F5F9;
  border-radius: 14rpx;
  padding: 0 28rpx;
  height: 92rpx;
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}
.field-input {
  flex: 1;
  height: 92rpx;
  font-size: 28rpx;
  color: #1E293B;
}
.placeholder { color: #94A3B8; font-size: 28rpx; }

/* ── 角色选择 ── */
.role-row {
  display: flex;
  gap: 20rpx;
  margin-bottom: 24rpx;
}
.role-chip {
  flex: 1;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14rpx;
  border: 2rpx solid #E2E8F0;
  font-size: 28rpx;
  color: #64748B;
  background: #F8FAFC;
  &.active {
    border-color: #4A6CF7;
    background: rgba(74,108,247,0.06);
    color: #4A6CF7;
    font-weight: 600;
  }
}

/* ── 按钮 ── */
.btn-primary {
  background: linear-gradient(135deg, #4A6CF7, #6366F1);
  border-radius: 14rpx;
  height: 92rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 8rpx;
  box-shadow: 0 6rpx 20rpx rgba(74,108,247,0.3);
  &:active { opacity: 0.85; transform: scale(0.98); }
}
.btn-text {
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  letter-spacing: 4rpx;
}

/* ── 分割线 ── */
.or-divider {
  display: flex;
  align-items: center;
  margin: 36rpx 0 28rpx;
}
.or-line {
  flex: 1;
  height: 1rpx;
  background: #E2E8F0;
}
.or-text {
  padding: 0 24rpx;
  font-size: 24rpx;
  color: #94A3B8;
}

/* ── 微信按钮 ── */
.btn-wechat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  height: 88rpx;
  border-radius: 14rpx;
  border: 2rpx solid #E2E8F0;
  background: #F8FAFC;
  &:active { background: #F1F5F9; }
}
.wechat-icon-wrap {
  width: 44rpx; height: 44rpx;
  border-radius: 8rpx;
  background: #07C160;
  display: flex;
  align-items: center; justify-content: center;
}
.wechat-icon-text {
  font-size: 20rpx;
  color: #fff;
  font-weight: 600;
}
.wechat-label {
  font-size: 28rpx;
  color: #334155;
  font-weight: 500;
}

/* ── 底部协议 ── */
.footer-text {
  text-align: center;
  padding: 40rpx 0 60rpx;
}
.footer-tap {
  font-size: 22rpx;
  color: #94A3B8;
}
.footer-link {
  font-size: 22rpx;
  color: #4A6CF7;
}

/* ── 底部弹窗 ── */
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
  background: #E2E8F0;
  border-radius: 4rpx;
  margin: 0 auto 24rpx;
}
.sheet-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #1E293B;
  text-align: center;
}
.sheet-desc {
  display: block;
  font-size: 24rpx;
  color: #94A3B8;
  text-align: center;
  margin-top: 8rpx;
  margin-bottom: 36rpx;
}
.profile-avatar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.avatar-pick-btn {
  width: 144rpx; height: 144rpx;
  border-radius: 50%;
  background: #F1F5F9;
  display: flex; align-items: center; justify-content: center;
  padding: 0; margin: 0; line-height: normal;
  border: 3rpx dashed #CBD5E1;
}
.avatar-pick-btn::after { border: none; }
.avatar-preview {
  width: 144rpx; height: 144rpx;
  border-radius: 50%;
}
.avatar-empty {
  display: flex; align-items: center; justify-content: center;
  width: 144rpx; height: 144rpx;
}
.avatar-plus {
  font-size: 56rpx;
  color: #94A3B8;
  font-weight: 300;
}
.avatar-label {
  font-size: 22rpx;
  color: #94A3B8;
  margin-top: 12rpx;
}
.sheet-btn-primary {
  background: linear-gradient(135deg, #4A6CF7, #6366F1);
  border-radius: 14rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 36rpx;
  box-shadow: 0 6rpx 20rpx rgba(74,108,247,0.25);
  &:active { opacity: 0.85; }
}
.sheet-btn-text {
  text-align: center;
  padding: 20rpx 0;
  font-size: 26rpx;
  color: #94A3B8;
}
</style>
