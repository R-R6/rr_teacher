/**
 * 云存储工具
 * 封装微信云开发的文件上传/下载能力
 * 与现有 cos_uploader.py 后端配合使用
 */

// 检查云开发是否已初始化
function isCloudReady() {
  // #ifdef MP-WEIXIN
  return !!(wx && wx.cloud)
  // #endif
  // #ifndef MP-WEIXIN
  return false
  // #endif
}

/**
 * 上传文件到云存储
 * @param {string} filePath - 本地临时文件路径
 * @param {string} cloudPath - 云存储路径，如 'uploads/2024/01/image.jpg'
 * @returns {Promise<{fileID: string, url: string}>}
 */
export function uploadToCloud(filePath, cloudPath) {
  return new Promise((resolve, reject) => {
    if (!isCloudReady()) {
      reject(new Error('云开发未初始化'))
      return
    }

    wx.cloud.uploadFile({
      cloudPath,
      filePath,
      success: (res) => {
        // fileID 格式: cloud://env-id.xxxx/path/file
        resolve({
          fileID: res.fileID,
          url: res.fileID, // 云存储 fileID 可直接用于 <image> 组件
        })
      },
      fail: (err) => {
        console.error('[云存储] 上传失败:', err)
        reject(err)
      }
    })
  })
}

/**
 * 获取云存储文件的临时链接
 * @param {string} fileID - 云存储 fileID
 * @returns {Promise<string>} 临时访问 URL
 */
export function getTempFileURL(fileID) {
  return new Promise((resolve, reject) => {
    if (!isCloudReady()) {
      reject(new Error('云开发未初始化'))
      return
    }

    wx.cloud.getTempFileURL({
      fileList: [fileID],
      success: (res) => {
        if (res.fileList && res.fileList[0] && res.fileList[0].tempFileURL) {
          resolve(res.fileList[0].tempFileURL)
        } else {
          reject(new Error('获取临时链接失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

/**
 * 删除云存储文件
 * @param {string} fileID - 云存储 fileID
 */
export function deleteCloudFile(fileID) {
  return new Promise((resolve, reject) => {
    if (!isCloudReady()) {
      reject(new Error('云开发未初始化'))
      return
    }

    wx.cloud.deleteFile({
      fileList: [fileID],
      success: () => resolve(),
      fail: (err) => reject(err)
    })
  })
}

/**
 * 上传图片（拍照/相册）到云存储
 * 自动按日期生成路径: uploads/YYYY/MM/uuid.ext
 * @param {string} tempFilePath - wx.chooseImage 的临时路径
 * @param {string} prefix - 前缀，如 'ocr', 'avatar', 'question'
 * @returns {Promise<{fileID: string, url: string}>}
 */
export function uploadImage(tempFilePath, prefix = 'uploads') {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const ext = tempFilePath.split('.').pop() || 'jpg'
  const uuid = Date.now() + '_' + Math.random().toString(36).slice(2, 8)
  const cloudPath = `${prefix}/${year}/${month}/${uuid}.${ext}`

  return uploadToCloud(tempFilePath, cloudPath)
}

/**
 * 调用云函数
 * @param {string} name - 云函数名
 * @param {object} data - 参数
 * @returns {Promise<object>} 云函数返回结果
 */
export function callCloudFunction(name, data = {}) {
  return new Promise((resolve, reject) => {
    if (!isCloudReady()) {
      reject(new Error('云开发未初始化'))
      return
    }

    wx.cloud.callFunction({
      name,
      data,
      success: (res) => {
        resolve(res.result)
      },
      fail: (err) => {
        console.error(`[云函数] ${name} 调用失败:`, err)
        reject(err)
      }
    })
  })
}

export default {
  isCloudReady,
  uploadToCloud,
  getTempFileURL,
  deleteCloudFile,
  uploadImage,
  callCloudFunction,
}
