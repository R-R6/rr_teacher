<script>
export default {
  onLaunch() {
    // 初始化微信云开发
    // #ifdef MP-WEIXIN
    if (wx && wx.cloud) {
      wx.cloud.init({
        env: 'cloud1-d5gls7mdgf0e5f907',
        traceUser: true,
      })
      console.log('[云开发] 初始化完成')
    }
    // #endif

    const token = uni.getStorageSync('access_token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/login' })
    }
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
