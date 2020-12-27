const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}

// Promise化
const promisify = name => option =>
  new Promise((resolve, reject) =>
    wx[name]({
      ...option,
      success: resolve,
      fail: reject,
    })
  )
// Proxy 代理
const wxPro = new Proxy(wx, {
  get(target, prop) {
    return promisify(prop)
  }
})

/**
 * 将普通列表转换为树结构的列表
 * @param {列表 id,parendId 是必须项} list 
 */
const listConvertToTreeList = list => {
  if (!list || !list.length) {
    return [];
  }
  const treeListMap = {};
  list.forEach(item => {
    treeListMap[item.id] = item;
  });
  for (let i = 0; i < list.length; i++) {
    if (list[i].parentId && treeListMap[list[i].parentId]) {
      if (!treeListMap[list[i].parentId].children) {
        treeListMap[list[i].parentId].children = [];
      }
      treeListMap[list[i].parentId].children.push(list[i]);
      list.splice(i, 1);
      i--;
    }
  }
  return list;
}
/**
 * CDN图片格式化
 * 通过路径参数处理
 */
const cdnImageFormatHandler = {
  withWidth: (url, width) => `${url},1,${width},0,1`,
  withHeight: (url, height) => `${url},1,0,${height},1`,
  custom: (url, width, height) => `${url},1,${width},${height},3`,
  square: (url, val) => `${url},1,${val},${val},3`,
}

/**
 * 缓存
 * 使用小程序 Storage
 */
const cacheHandler = {
  claer: () => wx.clearStorageSync(),
  set: (key, data) => wx.setStorageSync(key, data),
  get: (key) => wx.getStorageSync(key),
  info: () => wx.getStorageInfoSync()
}

module.exports = {
  formatTime: formatTime,
  promisify: promisify,
  wxPro: wxPro,
  listConvertToTreeList,
  cdnImageFormatHandler,
  cacheHandler
}


/**
 *  !用法示例
    const util = require('../../../utils/util.js')
    util.wxPro.showToast({
      title: 'okya',
    }).then(() => {
      console.log('showToast')
    })
 */