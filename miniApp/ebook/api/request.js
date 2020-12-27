// app.js中获取不到getApp()
let globalData = {
  http: 'domain'
} // 接口domain

const {
  GET,
  POST
} = {
  GET: "GET",
  POST: "POST"
}
// 成功http状态码
const successCodes = [200, 201, 202, 204, 304]

// http状态码对应的默认文本提醒
const codeMessage = {
  200: '操作成功',
  201: '新建或修改数据成功',
  202: '一个请求已经进入后台排队（异步任务）',
  204: '删除数据成功。',
  400: '参数错误',
  401: '需要用户验证',
  403: '用户无权限',
  404: '资源不存在',
  405: '不支持的操作方法',
  406: '请求的格式不可得。',
  410: '请求的资源被永久删除，且不会再得到的',
  422: '当创建一个对象时，发生一个验证错误',
  500: '服务器内部错误',
  502: '应用程序错误',
  503: '维护中',
  504: '网关超时',
}

// 请求的默认参数
const defaultOptions = {
  method: GET,
  success: function () {},
  fail: function (err) {
    console.log(err)
  },
  complete: function () {},
}

// 默认的额外参数
const defaultOtherOptions = {
  useSuccessCode: true, // 是否检测预定义的http请求的成功状态
  isShowError: true, // 是否显示错误提醒
  globalData: '',
  timeout: 1000 * 30, //超时时间，单位为毫秒
}

// toast提醒函数
function _showToast(title = '网络请求失败', duration = 3000) {
  wx.showToast({
    title: title,
    icon: 'none',
    duration: duration
  })
}

const request = (fetchOptions = {
  header: {}
}, otherOptions) => {
  // 合并otherOptions
  otherOptions = typeof otherOptions !== 'undefined' ? {
    ...defaultOtherOptions,
    ...otherOptions
  } : defaultOtherOptions

  // app.js中获取不到getApp(), globalData需要传进来
  if (otherOptions.globalData) { // app.js传globalData
    globalData = otherOptions.globalData
  } else { // 非app.js不传
    const app = getApp()
    globalData = JSON.parse(JSON.stringify(app.globalData))
  }

  // 设置header统一的Api-Ext属性
  defaultOptions.header = {
    'Api-Ext': globalData.apiExt
  }

  // 合并newFetchOptions
  const newHeader = {
    ...defaultOptions.header,
    ...fetchOptions.header
  }
  const newFetchOptions = {
    ...defaultOptions,
    ...fetchOptions
  }
  newFetchOptions.header = newHeader
  newFetchOptions.url = `${globalData.http}${newFetchOptions.url}`
  newFetchOptions.timeout = otherOptions.timeout

  return new Promise((resolve, reject) => {
    try {
      wx.showLoading({
        title: '加载中',
      })
      wx.request({
        ...newFetchOptions,
        success: function (res) {
          const {
            errMsg
          } = res
          // 真机wx.toast和showLoading只能同时允许一个出现，故请求完成全部关闭，以便后续能toast提醒
          wx.hideLoading()
          // 请求网络成功
          if (errMsg.includes('ok')) {
            // 使用预设的成功状态
            if (otherOptions.useSuccessCode) {
              const {
                statusCode,
                data
              } = res
              if (successCodes.findIndex((item) => item === statusCode) > -1) {
                !data.Success && _showToast(data.Msg) // 业务异常拦截
                newFetchOptions.success(data, res)
                resolve(data, res)
              } else {
                console.log('非请求成功状态', res)
                let msg = codeMessage[statusCode] || '未知错误'
                if (typeof data !== 'undefined' && typeof data.message !== 'undefined') {
                  msg = data.message
                }
                otherOptions.isShowError && _showToast(msg)
                resolve(res)
              }
            } else { // 不使用预设的成功状态, 返回整个requestResult
              console.log('不使用预设的成功状态', res)
              newFetchOptions.success(res)
              resolve(res)
            }
          } else { // 请求网络失败
            otherOptions.isShowError && _showToast()
            newFetchOptions.fail(res)
          }
        },
        fail: function (res) {
          otherOptions.isShowError && _showToast(res.errMsg)
          newFetchOptions.fail(res)
          reject(res)
        },
        complete: function () {
          newFetchOptions.complete()
        },
      })
    } catch (e) {
      otherOptions.isShowError && _showToast(e)
      newFetchOptions.fail(e)
      reject(e)
    }
  })
}

const get = (url, data = {}, header = {}, otherOptions = {}) => {
  return request({
    url: url,
    data: data,
    header: header,
    method: GET
  }, otherOptions)
}

const post = (url, data = {}, headers = {}, otherOptions = {}) => {
  return request({
    url: url,
    data: data,
    header: header,
    method: POST
  }, otherOptions)
}

module.exports = {
  get,
  post,
}