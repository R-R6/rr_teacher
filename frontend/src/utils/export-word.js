export function buildWordFileName(title, suffix) {
  const rawTitle = String(title || '试卷')
  const safeTitle = rawTitle
    .replace(/[\\/:*?"<>|\r\n\t]+/g, '_')
    .replace(/\s+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 50) || '试卷'
  return `${safeTitle}_${suffix || '试卷'}.docx`
}

function getDownloadHeader() {
  const token = uni.getStorageSync('access_token') || ''
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function openWordDocument(filePath) {
  return new Promise((resolve, reject) => {
    uni.openDocument({
      filePath,
      fileType: 'docx',
      showMenu: true,
      success: () => resolve({ mode: 'openDocument' }),
      fail: reject,
    })
  })
}

function prepareShareableWordPath(tempFilePath, fileName) {
  return new Promise((resolve) => {
    const wxApi = typeof wx !== 'undefined' ? wx : null
    if (!wxApi || !wxApi.env || !wxApi.env.USER_DATA_PATH || typeof wxApi.getFileSystemManager !== 'function') {
      resolve(tempFilePath)
      return
    }

    const targetPath = `${wxApi.env.USER_DATA_PATH}/${fileName}`
    const fs = wxApi.getFileSystemManager()
    const copyToTarget = () => {
      fs.copyFile({
        srcPath: tempFilePath,
        destPath: targetPath,
        success: () => resolve(targetPath),
        fail: () => resolve(tempFilePath),
      })
    }
    fs.unlink({
      filePath: targetPath,
      complete: copyToTarget,
    })
  })
}

function shareTempWordFile(filePath, fileName) {
  return new Promise((resolve, reject) => {
    const wxApi = typeof wx !== 'undefined' ? wx : null
    if (wxApi && typeof wxApi.shareFileMessage === 'function') {
      wxApi.shareFileMessage({
        filePath,
        fileName,
        success: () => resolve({ mode: 'shareFileMessage' }),
        fail: (err) => {
          openWordDocument(filePath).then(resolve).catch(() => reject(err))
        },
      })
      return
    }

    openWordDocument(filePath).then(resolve).catch(reject)
  })
}

function downloadTempWordFile(url) {
  return new Promise((resolve, reject) => {
    uni.downloadFile({
      url,
      header: getDownloadHeader(),
      success: (res) => {
        console.log('Word下载完成:', res.tempFilePath, res.statusCode)
        if (res.statusCode !== 200) {
          reject(new Error(`Word download failed with status ${res.statusCode}`))
          return
        }
        resolve(res.tempFilePath)
      },
      fail: reject,
    })
  })
}

export async function exportWordToWechat(options) {
  const url = options && options.url
  const fileName = (options && options.fileName) || buildWordFileName('', '试卷')
  if (!url) {
    throw new Error('Word download url is empty')
  }

  let loadingVisible = true
  uni.showLoading({ title: '正在准备转发...' })
  try {
    const tempFilePath = await downloadTempWordFile(url)
    const shareFilePath = await prepareShareableWordPath(tempFilePath, fileName)
    loadingVisible = false
    uni.hideLoading()
    return await shareTempWordFile(shareFilePath, fileName)
  } catch (err) {
    if (loadingVisible) {
      uni.hideLoading()
    }
    throw err
  }
}
