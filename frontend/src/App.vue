<script>
import { authAPI } from './utils/api.js'

export default {
  async onLaunch() {
    // 初始化微信云开发
    // #ifdef MP-WEIXIN
    if (wx && wx.cloud) {
      wx.cloud.init({
        env: 'cloud1-d5gls7mdgf0e5f907',
        traceUser: true,
      })
    }
    // #endif

    // 静默登录：检查本地 token 是否有效
    const token = uni.getStorageSync('access_token')
    if (token) {
      try {
        // 验证 token 是否过期
        const userInfo = await authAPI.getMe()
        // token 有效，更新本地用户信息
        uni.setStorageSync('user_info', JSON.stringify(userInfo))
        return // 已登录，不跳转
      } catch (e) {
        // token 过期，清除本地数据
        uni.removeStorageSync('access_token')
        uni.removeStorageSync('refresh_token')
        uni.removeStorageSync('user_info')
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
