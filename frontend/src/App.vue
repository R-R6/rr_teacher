<script>
import { authAPI } from './utils/api.js'

export default {
  async onLaunch() {
    // 初始化微信云开发
    // #ifdef MP-WEIXIN
    try {
      if (wx && wx.cloud) {
        wx.cloud.init({
          env: 'cloud1-d5gls7mdgf0e5f907',
          traceUser: true,
        })
      }
    } catch (e) {
      console.warn('[云开发] 初始化跳过:', e.message)
    }
    // #endif

    // 静默登录：检查本地 token 是否有效
    const token = uni.getStorageSync('access_token')
    if (token) {
      try {
        // 验证 token 是否过期（超时10秒，云托管冷启动可能较慢）
        const userInfo = await authAPI.getMe()
        // token 有效，更新本地用户信息
        uni.setStorageSync('user_info', JSON.stringify(userInfo))
        return // 已登录，不跳转
      } catch (e) {
        // 只有 401（token 真正过期）才清除
        // 网络超时、服务器500等不清理，保留本地缓存
        if (e.code === 401) {
          uni.removeStorageSync('access_token')
          uni.removeStorageSync('refresh_token')
          uni.removeStorageSync('user_info')
        }
        // 其他错误（超时等）：保留 token，使用本地缓存的用户信息
      }
    }
    // 未登录，跳转到登录页
    uni.reLaunch({ url: '/pages/login/login' })
  },
  onShow() {},
  onHide() {}
}
</script>

<style lang="scss">
/* 全局样式 */
page {
  background-color: #F5F6FA;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #1F2937;
  line-height: 1.6;
}

/* 全局滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

/* 安全区域适配 */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
