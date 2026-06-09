<template>
  <view class="login-page">
    <view class="login-bg"></view>
    <view class="login-content">
      <!-- Logo区域 -->
      <view class="logo-area">
        <view class="logo-icon">🧪</view>
        <text class="logo-title">小睿化学</text>
        <text class="logo-subtitle">化学老师的智能助手</text>
      </view>

      <!-- 登录表单 -->
      <view class="form-card">
        <view class="tab-bar">
          <view :class="['tab', mode === 'login' ? 'active' : '']" @tap="mode = 'login'">登录</view>
          <view :class="['tab', mode === 'register' ? 'active' : '']" @tap="mode = 'register'">注册</view>
        </view>

        <!-- 登录 -->
        <view v-if="mode === 'login'" class="form-body">
          <view class="input-group">
            <view class="input-icon">👤</view>
            <input class="input-field" v-model="loginForm.username" placeholder="请输入用户名" />
          </view>
          <view class="input-group">
            <view class="input-icon">🔒</view>
            <input class="input-field" v-model="loginForm.password" type="password" placeholder="请输入密码" />
          </view>
          <view class="btn-primary" @tap="handleLogin">
            <text>登 录</text>
          </view>
        </view>

        <!-- 注册 -->
        <view v-if="mode === 'register'" class="form-body">
          <view class="input-group">
            <view class="input-icon">👤</view>
            <input class="input-field" v-model="registerForm.username" placeholder="用户名（2-50个字符）" />
          </view>
          <view class="input-group">
            <view class="input-icon">🔒</view>
            <input class="input-field" v-model="registerForm.password" type="password" placeholder="密码（6-64个字符）" />
          </view>
          <view class="input-group">
            <view class="input-icon">📱</view>
            <input class="input-field" v-model="registerForm.phone" type="number" placeholder="手机号码（选填）" />
          </view>
          <view class="input-group">
            <view class="input-icon">🏫</view>
            <input class="input-field" v-model="registerForm.school" placeholder="学校名称（选填）" />
          </view>
          <view class="role-select">
            <view :class="['role-btn', registerForm.role === 'teacher' ? 'active' : '']" @tap="registerForm.role = 'teacher'">
              👨‍🏫 老师
            </view>
            <view :class="['role-btn', registerForm.role === 'student' ? 'active' : '']" @tap="registerForm.role = 'student'">
              🎓 学生
            </view>
          </view>
          <view class="btn-primary" @tap="handleRegister">
            <text>注 册</text>
          </view>
        </view>

        <!-- 微信登录 -->
        <view class="divider">
          <view class="line"></view>
          <text class="divider-text">其他登录方式</text>
          <view class="line"></view>
        </view>
        <view class="btn-wechat" @tap="handleWechatLogin">
          <text class="wechat-icon">💬</text>
          <text>微信一键登录</text>
        </view>
      </view>

      <!-- 头像昵称授权弹窗 -->
      <view v-if="showProfileModal" class="modal-mask" @tap="skipProfile">
        <view class="modal-content" @tap.stop>
          <text class="modal-title">完善个人信息</text>
          <text class="modal-desc">授权后可获得您的微信头像和昵称</text>

          <!-- 头像选择（新版API） -->
          <view class="profile-section">
            <text class="profile-label">头像</text>
            <button class="avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
              <image v-if="tempAvatarUrl" class="avatar-img" :src="tempAvatarUrl" mode="aspectFill" />
              <view v-else class="avatar-placeholder">
                <text class="avatar-plus">+</text>
              </view>
            </button>
          </view>

          <!-- 昵称输入（新版API） -->
          <view class="profile-section">
            <text class="profile-label">昵称</text>
            <input class="nickname-input" type="nickname" v-model="tempNickname" placeholder="请输入昵称" @blur="onNicknameBlur" />
          </view>

          <view class="modal-actions">
            <view class="modal-btn skip" @tap="skipProfile">跳过</view>
            <view class="modal-btn confirm" @tap="confirmProfile">确认</view>
          </view>
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
      loginForm: {
        username: '',
        password: '',
      },
      registerForm: {
        username: '',
        password: '',
        phone: '',
        school: '',
        role: 'teacher',
      },
      // 头像昵称授权
      showProfileModal: false,
      tempAvatarUrl: '',
      tempAvatarFileID: '',
      tempNickname: '',
      pendingWechatCode: '',  // 暂存微信 code
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
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 500)
      } catch (e) {
        uni.hideLoading()
      }
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
      } catch (e) {
        uni.hideLoading()
      }
    },
    async handleWechatLogin() {
      uni.showLoading({ title: '微信登录中...' })
      try {
        // 第一步：wx.login 获取 code
        const loginRes = await new Promise((resolve, reject) => {
          uni.login({
            provider: 'weixin',
            success: resolve,
            fail: reject,
          })
        })

        // 第二步：code 换取 token（后端调用微信 jscode2session）
        const res = await authAPI.wechatLogin({
          code: loginRes.code,
          nickname: '',
        })

        this.saveLoginData(res)
        uni.hideLoading()

        // 第三步：检查是否需要完善信息（新用户）
        const userInfo = res.user
        if (!userInfo.nickname || userInfo.nickname.startsWith('微信用户')) {
          // 新用户，弹出头像昵称授权
          this.pendingWechatCode = loginRes.code
          this.tempNickname = ''
          this.tempAvatarUrl = ''
          this.showProfileModal = true
        } else {
          // 老用户，直接进入
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            uni.switchTab({ url: '/pages/index/index' })
          }, 500)
        }
      } catch (e) {
        uni.hideLoading()
      }
    },

    // --- 头像昵称授权 ---
    onChooseAvatar(e) {
      const tempFilePath = e.detail.avatarUrl
      if (tempFilePath) {
        this.tempAvatarUrl = tempFilePath
      }
    },
    onNicknameBlur(e) {
      this.tempNickname = e.detail.value || ''
    },
    async confirmProfile() {
      uni.showLoading({ title: '保存中...' })
      try {
        // 上传头像到云存储（如果有）
        let avatarUrl = ''
        if (this.tempAvatarUrl) {
          // #ifdef MP-WEIXIN
          if (wx && wx.cloud) {
            const uploadRes = await new Promise((resolve, reject) => {
              wx.cloud.uploadFile({
                cloudPath: `avatars/${Date.now()}_${Math.random().toString(36).slice(2, 8)}.jpg`,
                filePath: this.tempAvatarUrl,
                success: resolve,
                fail: reject,
              })
            })
            avatarUrl = uploadRes.fileID
          }
          // #endif
        }

        // 更新用户信息（通过重新登录获取最新 token + 用户信息）
        // 这里简化处理：直接更新本地存储的用户信息
        const userInfo = JSON.parse(uni.getStorageSync('user_info') || '{}')
        if (this.tempNickname) userInfo.nickname = this.tempNickname
        if (avatarUrl) userInfo.avatar_url = avatarUrl
        uni.setStorageSync('user_info', JSON.stringify(userInfo))

        uni.hideLoading()
        this.showProfileModal = false
        uni.showToast({ title: '设置成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 500)
      } catch (e) {
        uni.hideLoading()
        // 上传失败不影响登录
        this.showProfileModal = false
        uni.switchTab({ url: '/pages/index/index' })
      }
    },
    skipProfile() {
      this.showProfileModal = false
      uni.switchTab({ url: '/pages/index/index' })
    },

    // --- 通用 ---
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}
.login-bg {
  position: absolute;
  top: -200rpx;
  right: -100rpx;
  width: 500rpx;
  height: 500rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
}
.login-content {
  position: relative;
  z-index: 1;
  padding: 0 48rpx;
  padding-top: 160rpx;
}
.logo-area {
  text-align: center;
  margin-bottom: 60rpx;
}
.logo-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}
.logo-title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8rpx;
}
.logo-subtitle {
  display: block;
  font-size: 26rpx;
  color: rgba(255,255,255,0.8);
}
.form-card {
  background: #fff;
  border-radius: 32rpx;
  padding: 40rpx;
  box-shadow: 0 20rpx 60rpx rgba(0,0,0,0.15);
}
.tab-bar {
  display: flex;
  margin-bottom: 40rpx;
  border-bottom: 2rpx solid #f0f0f0;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 30rpx;
  color: #999;
  position: relative;
  &.active {
    color: #4A6CF7;
    font-weight: 600;
    &::after {
      content: '';
      position: absolute;
      bottom: -2rpx;
      left: 30%;
      width: 40%;
      height: 4rpx;
      background: #4A6CF7;
      border-radius: 2rpx;
    }
  }
}
.input-group {
  display: flex;
  align-items: center;
  background: #F5F6FA;
  border-radius: 16rpx;
  padding: 0 24rpx;
  margin-bottom: 24rpx;
  height: 96rpx;
}
.input-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}
.input-field {
  flex: 1;
  height: 96rpx;
  font-size: 28rpx;
}
.role-select {
  display: flex;
  gap: 20rpx;
  margin-bottom: 24rpx;
}
.role-btn {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  border-radius: 16rpx;
  border: 2rpx solid #E5E7EB;
  font-size: 28rpx;
  color: #6B7280;
  &.active {
    border-color: #4A6CF7;
    background: rgba(74, 108, 247, 0.08);
    color: #4A6CF7;
    font-weight: 600;
  }
}
.btn-primary {
  background: linear-gradient(135deg, #4A6CF7 0%, #6B8AFF 100%);
  border-radius: 16rpx;
  padding: 24rpx 0;
  text-align: center;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  margin-top: 8rpx;
  &:active { opacity: 0.9; }
}
.divider {
  display: flex;
  align-items: center;
  margin: 32rpx 0;
}
.line {
  flex: 1;
  height: 1rpx;
  background: #E5E7EB;
}
.divider-text {
  padding: 0 20rpx;
  font-size: 24rpx;
  color: #9CA3AF;
}
.btn-wechat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  background: #07C160;
  border-radius: 16rpx;
  padding: 22rpx 0;
  color: #fff;
  font-size: 28rpx;
  font-weight: 500;
  &:active { opacity: 0.9; }
}
.wechat-icon {
  font-size: 32rpx;
}

/* 头像昵称授权弹窗 */
.modal-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 200;
  display: flex; align-items: center; justify-content: center;
}
.modal-content {
  width: 600rpx; background: #fff;
  border-radius: 24rpx; padding: 40rpx;
}
.modal-title {
  display: block; font-size: 34rpx; font-weight: 700; color: #1F2937;
  text-align: center; margin-bottom: 8rpx;
}
.modal-desc {
  display: block; font-size: 24rpx; color: #9CA3AF;
  text-align: center; margin-bottom: 32rpx;
}
.profile-section {
  margin-bottom: 24rpx;
}
.profile-label {
  display: block; font-size: 26rpx; color: #374151; margin-bottom: 12rpx;
}
.avatar-btn {
  width: 120rpx; height: 120rpx; border-radius: 50%;
  overflow: hidden; background: #F5F6FA; border: 2rpx dashed #D1D5DB;
  display: flex; align-items: center; justify-content: center;
  padding: 0; margin: 0; line-height: normal;
}
.avatar-btn::after { border: none; }
.avatar-img {
  width: 120rpx; height: 120rpx; border-radius: 50%;
}
.avatar-placeholder {
  width: 120rpx; height: 120rpx; display: flex;
  align-items: center; justify-content: center;
}
.avatar-plus { font-size: 48rpx; color: #D1D5DB; }
.nickname-input {
  width: 100%; height: 80rpx; background: #F5F6FA;
  border-radius: 12rpx; padding: 0 24rpx; font-size: 28rpx;
}
.modal-actions {
  display: flex; gap: 20rpx; margin-top: 32rpx;
}
.modal-btn {
  flex: 1; text-align: center; padding: 20rpx 0;
  border-radius: 12rpx; font-size: 28rpx; font-weight: 600;
}
.modal-btn.skip { background: #F3F4F6; color: #6B7280; }
.modal-btn.confirm { background: #4A6CF7; color: #fff; }
</style>
