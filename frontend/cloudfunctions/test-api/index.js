/**
 * 云函数：test-api
 * 用于验证云开发环境是否正常工作
 */
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext()

  return {
    code: 0,
    message: '云开发环境正常工作',
    data: {
      openid: wxContext.OPENID,
      appid: wxContext.APPID,
      unionid: wxContext.UNIONID || null,
      env: cloud.DYNAMIC_CURRENT_ENV,
      timestamp: Date.now(),
    }
  }
}
