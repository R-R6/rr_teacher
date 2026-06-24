<template>
  <view class="ocr-page">
    <view class="engine-bar">
      <view
        v-for="engine in engines"
        :key="engine.id"
        :class="['engine-chip', { active: currentEngine === engine.id, disabled: !engine.available }]"
        @tap="engine.available && (currentEngine = engine.id)"
      >
        <text class="engine-chip__primary">{{ engineDisplay(engine.id).primary }}</text>
        <text class="engine-chip__secondary">{{ engineDisplay(engine.id).secondary }}</text>
      </view>
    </view>

    <view class="camera-area">
      <camera
        v-if="!photoPath && !cameraFailed"
        :key="cameraKey"
        class="camera"
        device-position="back"
        :flash="flash"
        @error="onCameraError"
        @initdone="onCameraReady"
      >
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

      <view v-if="!photoPath && cameraFailed" class="camera-fallback">
        <text class="fallback-title">{{ cameraErrorText }}</text>
        <text class="fallback-desc">可使用系统相机拍照，或从相册选择题目图片</text>
        <view class="fallback-actions">
          <view class="fallback-btn primary" @tap="captureWithSystemCamera">系统相机</view>
          <view class="fallback-btn" @tap="retryCamera">重试</view>
        </view>
        <view class="fallback-link" @tap="openCameraSetting">检查权限</view>
      </view>

      <image v-if="photoPath" :src="photoPath" class="preview-image" mode="aspectFit" />

      <view v-if="loading" class="loading-overlay">
        <view class="loading-spinner"></view>
        <text class="loading-text">{{ loadingText }}</text>
      </view>
    </view>

    <view class="bottom-bar safe-area-bottom">
      <template v-if="!photoPath">
        <view class="bar-btn btn-album" @tap="chooseFromAlbum">
          <text class="bar-icon">相册</text>
          <text class="bar-label">选图</text>
        </view>
        <view class="bar-btn btn-capture" @tap="takePhoto">
          <view class="capture-ring">
            <view class="capture-inner"></view>
          </view>
        </view>
        <view class="bar-btn btn-flash" @tap="toggleFlash">
          <text class="bar-icon">{{ flash === 'on' ? '开' : '关' }}</text>
          <text class="bar-label">闪光灯</text>
        </view>
      </template>
      <template v-else>
        <view class="bar-btn btn-retake" @tap="retake">
          <text class="bar-icon">重拍</text>
          <text class="bar-label">返回拍照</text>
        </view>
        <view class="bar-btn btn-confirm" @tap="recognize">
          <text class="bar-text">{{ recognizeButtonText }}</text>
        </view>
      </template>
    </view>
  </view>
</template>

<script>
import { ocrAPI } from '../../utils/api.js'

const ENGINE_MAP = {
  tesseract: {
    primary: '极速识别',
    secondary: 'Tesseract',
    loading: '正在极速识别中...',
    button: '开始极速识别',
  },
  pix2text_online: {
    primary: '高精度识别（公式）',
    secondary: 'Pix2Text',
    loading: '正在高精度识别中（公式题约 5~15 秒）...',
    button: '开始高精度识别',
  },
  pix2text_local: {
    primary: '高精度识别（公式）',
    secondary: 'Pix2Text',
    loading: '正在高精度识别中...',
    button: '开始高精度识别',
  },
  doubao_vision: {
    primary: '高精度识别（复杂题）',
    secondary: '豆包视觉',
    loading: '正在高精度识别中（复杂题约 10~30 秒）...',
    button: '开始高精度识别',
  },
}

export default {
  data() {
    return {
      photoPath: '',
      loading: false,
      loadingText: '正在识别中...',
      flash: 'auto',
      engines: [],
      currentEngine: 'tesseract',
      cameraFailed: true,
      cameraErrorText: '正在检查摄像头',
      cameraKey: 0,
      cameraReady: false,
      cameraInitTimer: null,
    }
  },
  computed: {
    recognizeButtonText() {
      return this.engineDisplay(this.currentEngine).button
    },
  },
  onLoad() {
    this.loadEngines()
    if (this.isDevtools()) {
      this.cameraFailed = true
      this.cameraErrorText = '开发者工具未检测到摄像头'
      return
    }
    this.cameraFailed = false
    this.cameraErrorText = '未找到摄像头'
    this.prepareCamera()
    this.setCameraInitTimeout()
  },
  onUnload() {
    this.clearCameraInitTimer()
  },
  methods: {
    engineDisplay(id) {
      return ENGINE_MAP[id] || { primary: id, secondary: '', loading: '正在识别中...', button: '开始识别' }
    },
    isDevtools() {
      let systemInfo = null
      try {
        if (uni.getSystemInfoSync) {
          systemInfo = uni.getSystemInfoSync()
        }
      } catch (error) {
        systemInfo = null
      }
      if (!systemInfo && typeof wx !== 'undefined' && wx.getSystemInfoSync) {
        try {
          systemInfo = wx.getSystemInfoSync()
        } catch (error) {
          systemInfo = null
        }
      }
      return !!(systemInfo && (systemInfo.platform === 'devtools' || systemInfo.brand === 'devtools'))
    },
    takePhoto() {
      if (this.cameraFailed) {
        this.captureWithSystemCamera()
        return
      }
      const ctx = uni.createCameraContext()
      ctx.takePhoto({
        quality: 'high',
        success: (res) => {
          this.photoPath = res.tempImagePath
        },
        fail: () => {
          this.cameraFailed = true
          this.cameraErrorText = '摄像头暂不可用'
          this.captureWithSystemCamera()
        },
      })
    },
    captureWithSystemCamera() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['camera'],
        success: (res) => {
          this.photoPath = res.tempFilePaths[0]
          this.cameraFailed = false
        },
        fail: () => {
          uni.showToast({ title: '无法打开系统相机，请从相册选图', icon: 'none' })
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
      this.retryCamera()
    },
    toggleFlash() {
      this.flash = this.flash === 'on' ? 'off' : 'on'
    },
    prepareCamera() {
      if (!uni.getSetting || !uni.authorize) return
      uni.getSetting({
        success: (res) => {
          const cameraAuth = res.authSetting && res.authSetting['scope.camera']
          if (cameraAuth === false) {
            this.cameraFailed = true
            this.cameraErrorText = '摄像头权限未开启'
            return
          }
          if (cameraAuth === true) return
          uni.authorize({
            scope: 'scope.camera',
            fail: () => {
              this.cameraFailed = true
              this.cameraErrorText = '摄像头权限未开启'
            },
          })
        },
      })
    },
    setCameraInitTimeout() {
      this.clearCameraInitTimer()
      this.cameraReady = false
      this.cameraInitTimer = setTimeout(() => {
        if (!this.photoPath && !this.cameraReady) {
          this.cameraFailed = true
          this.cameraErrorText = '未找到摄像头'
        }
      }, 2500)
    },
    clearCameraInitTimer() {
      if (this.cameraInitTimer) {
        clearTimeout(this.cameraInitTimer)
        this.cameraInitTimer = null
      }
    },
    onCameraReady() {
      this.cameraReady = true
      this.clearCameraInitTimer()
      this.cameraFailed = false
      this.cameraErrorText = '未找到摄像头'
    },
    onCameraError(event) {
      this.clearCameraInitTimer()
      const message = event && event.detail && event.detail.errMsg ? event.detail.errMsg : ''
      this.cameraFailed = true
      this.cameraErrorText = /auth|permission|deny|authorize/i.test(message)
        ? '摄像头权限未开启'
        : '未找到摄像头'
      uni.showToast({ title: this.cameraErrorText, icon: 'none' })
    },
    retryCamera() {
      this.clearCameraInitTimer()
      if (this.isDevtools()) {
        this.cameraFailed = true
        this.cameraReady = false
        this.cameraErrorText = '开发者工具未检测到摄像头'
        return
      }
      this.cameraFailed = false
      this.cameraErrorText = '未找到摄像头'
      this.cameraKey += 1
      this.prepareCamera()
      this.setCameraInitTimeout()
    },
    openCameraSetting() {
      if (!uni.openSetting) return
      uni.openSetting({
        success: () => {
          this.retryCamera()
        },
      })
    },
    async loadEngines() {
      try {
        const res = await ocrAPI.listEngines()
        this.engines = res.engines || []
        this.currentEngine = res.default || 'tesseract'
      } catch (error) {
        this.engines = [
          { id: 'tesseract', available: true },
          { id: 'pix2text_online', available: false },
          { id: 'doubao_vision', available: false },
        ]
      }
    },
    async recognize() {
      if (!this.photoPath) return
      const engine = this.engines.find(item => item.id === this.currentEngine)
      if (!engine || !engine.available) {
        uni.showToast({
          title: '当前引擎未配置，请先检查服务端环境变量',
          icon: 'none',
          duration: 2500,
        })
        return
      }
      this.loading = true
      this.loadingText = this.engineDisplay(this.currentEngine).loading
      try {
        const res = await ocrAPI.recognize(this.photoPath, this.currentEngine)
        this.loading = false
        const data = encodeURIComponent(JSON.stringify(res))
        uni.navigateTo({
          url: `/pages/ocr-result/ocr-result?data=${data}`,
        })
      } catch (error) {
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

.engine-bar {
  display: flex;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  background: #1a1a2e;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.06);
}

.engine-chip {
  flex: 1;
  padding: 16rpx 12rpx;
  background: rgba(255, 255, 255, 0.08);
  border: 2rpx solid transparent;
  border-radius: 16rpx;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;

  &.active {
    background: rgba(74, 108, 247, 0.2);
    border-color: #4A6CF7;
    color: #fff;
  }

  &.disabled {
    opacity: 0.45;
  }
}

.engine-chip__primary {
  font-size: 24rpx;
  font-weight: 600;
}

.engine-chip__secondary {
  margin-top: 4rpx;
  font-size: 20rpx;
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
  inset: 0;
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
  margin-top: 32rpx;
  color: rgba(255, 255, 255, 0.8);
  font-size: 26rpx;
}

.camera-fallback {
  height: 100%;
  padding: 0 64rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: #202124;
  color: #fff;
}

.fallback-title {
  font-size: 34rpx;
  font-weight: 700;
  margin-bottom: 16rpx;
}

.fallback-desc {
  font-size: 26rpx;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 36rpx;
}

.fallback-actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.fallback-btn {
  min-width: 160rpx;
  padding: 18rpx 28rpx;
  border-radius: 32rpx;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 26rpx;

  &.primary {
    background: #4A6CF7;
  }
}

.fallback-link {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: underline;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-spinner {
  width: 80rpx;
  height: 80rpx;
  border: 6rpx solid rgba(255, 255, 255, 0.3);
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
  background: rgba(0, 0, 0, 0.9);
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

.bar-icon {
  font-size: 34rpx;
  color: #fff;
}

.bar-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
}

.btn-capture {
  padding: 0 40rpx;
}

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
