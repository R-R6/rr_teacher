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
        uni.setStorageSync('access_token', res.access_token)
        uni.setStorageSync('refresh_token', res.refresh_token)
        uni.setStorageSync('user_info', JSON.stringify(res.user))
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
        const loginRes = await new Promise((resolve, reject) => {
          uni.login({
            provider: 'weixin',
            success: resolve,
            fail: reject,
          })
        })
        const res = await authAPI.wechatLogin({
          code: loginRes.code,
          nickname: '微信用户',
        })
        uni.setStorageSync('access_token', res.access_token)
        uni.setStorageSync('refresh_token', res.refresh_token)
        uni.setStorageSync('user_info', JSON.stringify(res.user))
        uni.hideLoading()
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 500)
      } catch (e) {
        uni.hideLoading()
      }
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
</style>
