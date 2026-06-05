<template>
  <view class="ocr-page">
    <view class="camera-area">
      <camera v-if="!photoPath" class="camera" device-position="back" flash="auto" @error="onCameraError">
        <view class="camera-overlay">
          <view class="focus-frame">
            <view class="corner tl"></view>
            <view class="corner tr"></view>
            <view class="corner bl"></view>
            <view class="corner br"></view>
          </view>
          <text class="camera-hint">将化学题目放入框内拍摄</text>
        </view>
      </camera>

      <!-- 拍照后预览 -->
      <image v-if="photoPath" :src="photoPath" class="preview-image" mode="aspectFit" />

      <!-- 加载遮罩 -->
      <view v-if="loading" class="loading-overlay">
        <view class="loading-spinner"></view>
        <text class="loading-text">{{ loadingText }}</text>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar safe-area-bottom">
      <template v-if="!photoPath">
        <view class="bar-btn btn-album" @tap="chooseFromAlbum">
          <text class="bar-icon">🖼️</text>
          <text class="bar-label">相册</text>
        </view>
        <view class="bar-btn btn-capture" @tap="takePhoto">
          <view class="capture-ring">
            <view class="capture-inner"></view>
          </view>
        </view>
        <view class="bar-btn btn-flash" @tap="toggleFlash">
          <text class="bar-icon">{{ flash === 'on' ? '🔦' : '💡' }}</text>
          <text class="bar-label">闪光灯</text>
        </view>
      </template>
      <template v-else>
        <view class="bar-btn btn-retake" @tap="retake">
          <text class="bar-icon">🔄</text>
          <text class="bar-label">重拍</text>
        </view>
        <view class="bar-btn btn-confirm" @tap="recognize">
          <text class="bar-text">🔍 开始识别</text>
        </view>
      </template>
    </view>
  </view>
</template>

<script>
import { ocrAPI } from '../../utils/api.js'

export default {
  data() {
    return {
      photoPath: '',
      loading: false,
      loadingText: '正在识别中...',
      flash: 'auto',
    }
  },
  methods: {
    takePhoto() {
      const ctx = uni.createCameraContext()
      ctx.takePhoto({
        quality: 'high',
        success: (res) => {
          this.photoPath = res.tempImagePath
        },
      })
    },
    chooseFromAlbum() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album'],
        success: (res) => {
          this.photoPath = res.tempFilePaths[0]
        },
      })
    },
    retake() {
      this.photoPath = ''
    },
    toggleFlash() {
      this.flash = this.flash === 'on' ? 'off' : 'on'
    },
    onCameraError(e) {
      uni.showToast({ title: '摄像头初始化失败', icon: 'none' })
    },
    async recognize() {
      if (!this.photoPath) return
      this.loading = true
      this.loadingText = '正在上传图片...'
      try {
        this.loadingText = '正在识别化学题目...'
        const res = await ocrAPI.recognize(this.photoPath)
        this.loading = false
        // 跳转到结果页
        const data = encodeURIComponent(JSON.stringify(res))
        uni.navigateTo({
          url: `/pages/ocr-result/ocr-result?data=${data}`,
        })
      } catch (e) {
        this.loading = false
        uni.showToast({ title: '识别失败，请重试', icon: 'none' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.ocr-page {
  height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
}
.camera-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.camera {
  width: 100%;
  height: 100%;
}
.camera-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.focus-frame {
  width: 580rpx;
  height: 420rpx;
  position: relative;
}
.corner {
  position: absolute;
  width: 40rpx;
  height: 40rpx;
  border-color: #4A6CF7;
  border-style: solid;
  border-width: 0;
}
.corner.tl { top: 0; left: 0; border-top-width: 4rpx; border-left-width: 4rpx; border-radius: 8rpx 0 0 0; }
.corner.tr { top: 0; right: 0; border-top-width: 4rpx; border-right-width: 4rpx; border-radius: 0 8rpx 0 0; }
.corner.bl { bottom: 0; left: 0; border-bottom-width: 4rpx; border-left-width: 4rpx; border-radius: 0 0 0 8rpx; }
.corner.br { bottom: 0; right: 0; border-bottom-width: 4rpx; border-right-width: 4rpx; border-radius: 0 0 8rpx 0; }
.camera-hint {
  color: rgba(255,255,255,0.8);
  font-size: 26rpx;
  margin-top: 32rpx;
}
.preview-image {
  width: 100%;
  height: 100%;
}
.loading-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.loading-spinner {
  width: 80rpx;
  height: 80rpx;
  border: 6rpx solid rgba(255,255,255,0.3);
  border-top-color: #4A6CF7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20rpx;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text {
  color: #fff;
  font-size: 28rpx;
}
.bottom-bar {
  height: 200rpx;
  background: rgba(0,0,0,0.9);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 40rpx;
}
.bar-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}
.bar-icon { font-size: 40rpx; }
.bar-label { font-size: 22rpx; color: rgba(255,255,255,0.7); }
.btn-capture { padding: 0 40rpx; }
.capture-ring {
  width: 120rpx;
  height: 120rpx;
  border: 6rpx solid #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.capture-inner {
  width: 96rpx;
  height: 96rpx;
  background: #fff;
  border-radius: 50%;
  &:active { background: #ccc; }
}
.btn-confirm {
  background: #4A6CF7;
  border-radius: 40rpx;
  padding: 20rpx 48rpx;
}
.bar-text {
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
}
</style>
