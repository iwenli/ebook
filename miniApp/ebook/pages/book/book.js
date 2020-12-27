// pages/book/book.js
const apis = require('../../api/apis.js')
const util = require('../../utils/util.js')
const app = getApp()
let context;
Page({

  /**
   * 页面的初始数据
   */
  data: {
    config: {
      fontSize: 30,
      lineHeight: 30 * 1.7
    },
    showConfigUI: false,
    configMenus: [{
      name: 'cata',
      icon: 'cata',
      text: '目录'
    }, {
      name: 'options',
      icon: 'Aa',
      text: '选项'
    }, {
      name: 'light',
      icon: 'light',
      text: '亮度'
    }, {
      name: 'read',
      icon: 'headset',
      text: '阅读模式'
    }, {
      name: 'more',
      icon: 'more',
      text: '更多'
    }],
    showChapterUI: false,
    bookId: 0,
    book: null,
    chapters: [],
    currentSerialNums: 1, // 当前正在阅读的章节
    currentChapter: null,
    maxSerialNums: 0, // 最大章节id
    chapterContent: '',
    scrollTop: 0,
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    context = this
    const {
      id,
    } = options;
    context.setData({
      bookId: id
    })
    context.fetch()
  },
  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {},

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {},

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {},

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function (e) {
    if (e.from === 'button') {
      // 来自页面内转发按钮
      console.log(e.target)
    }
    return {
      title: this.data.book.name,
      desc: this.data.book.desc,
      imageUrl: util.cdnImageFormatHandler.withWidth(this.data.book.cover, 350),
      path: '/pages/book/book?id=' + this.data.book.id
    }
  },
  onShareTimeline(res) {
    // webview 页面返回 webviewUrl
    return {
      title: this.data.book.name,
      desc: this.data.book.desc,
      imageUrl: util.cdnImageFormatHandler.square(this.data.book.cover, 300),
      path: '/pages/book/book?id=' + this.data.book.id
    }
  },
  onAddToFavorites(res) {
    // webview 页面返回 webviewUrl
    return {
      title: this.data.book.name,
      imageUrl: util.cdnImageFormatHandler.square(this.data.book.cover, 300),
      path: '/pages/book/book?id=' + this.data.book.id
    }
  },
  fetch: function () {
    apis.getBookDetail({
      id: context.data.bookId
    }).then((res) => {
      console.log(res)
      context.setData({
        book: {
          id: res.Data.Book.Id,
          name: res.Data.Book.Name,
          desc: res.Data.Book.Desc,
          author: res.Data.Book.Author,
          cover: res.Data.Book.Cover,
          wordNums: res.Data.Book.WordNums,
        },
        maxSerialNums: Math.max(...res.Data.Chapters.map(m => m.SerialNums))
      })
      const chapters = res.Data.Chapters.map(chapter => {
        return {
          id: chapter.Id,
          serialNums: chapter.SerialNums,
          name: chapter.Name,
          wordNums: chapter.WordNums,
        }
      })
      context.fetchChapterContent(false, chapters)
    })
  },
  fetchChapterContent: function (append = false, chapters = []) {
    const indentChar = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    const newLineChar = '\n'
    const detail = context.getCurrentChapterDetail(chapters)
    let newContent = append ? context.data.chapterContent : ""
    newContent += newLineChar + indentChar + detail.name + newLineChar
    newContent += indentChar + '------------' + newLineChar
    apis.getChapter({
      bookId: context.data.bookId,
      serialNums: context.data.currentSerialNums,
    }).then((res) => {
      let data = {
        chapterContent: newContent + indentChar + res.Data.join(newLineChar + indentChar) + newLineChar,
        currentChapter: detail
      }
      if (!append) {
        data = {
          ...data,
          scrollTop: 0
        }
      }
      context.setData(data)

      if (chapters.length > 0) {
        // 延时渲染了目录   解决首屏加载慢的bug
        setTimeout(() => {
          context.setData({
            chapters: chapters
          })
        }, 500);
      }
    })
  },
  toggleConfigUI: function (e) {
    const {
      clientY
    } = e.changedTouches[0]
    console.log(e)
    console.log(app.globalData.sysInfo.screenHeight - clientY)
    if (clientY > 100 && (app.globalData.sysInfo.screenHeight - clientY) > 150) {
      // 点击中部地区
      context.setData({
        showConfigUI: !context.data.showConfigUI
      })
    }
  },
  toggleChapterUI: e => {
    context.setData({
      showChapterUI: !context.data.showChapterUI
    })
  },
  configMenuTap: (e) => {
    const {
      action
    } = e.currentTarget.dataset
    switch (action) {
      case "cata":
        context.setData({
          showChapterUI: true,
          showConfigUI: false,
        })
        break;
      default:
        break;
    }
  },
  getCurrentChapterDetail: (chapters = []) => {
    if (chapters.length === 0) {
      chapters = context.data.chapters
    }
    const detail = chapters.filter(m => m.serialNums === context.data.currentSerialNums)
    if (detail.length == 1) {
      return detail[0]
    }
    return {
      serialNums: context.data.currentSerialNums,
      name: '未知'
    }
  },
  nextChapterTap: (e) => {
    const {
      append
    } = e.currentTarget.dataset
    context.nextChapter(append)
  },
  preChapterTap: (e) => {
    context.preChapter()
  },
  changeChapterTap: (e) => {
    const {
      serialnums
    } = e.currentTarget.dataset
    console.log(serialnums)
    if (serialnums > 1 && serialnums !== context.data.currentSerialNums) {
      context._changeChapter(serialnums)
    }
  },
  nextChapter: (append = false) => {
    let cur = context.data.currentSerialNums
    if (cur < context.data.maxSerialNums) {
      cur += 1
      context._changeChapter(cur, append)
    }
  },
  preChapter: (append = false) => {
    let cur = context.data.currentSerialNums
    if (cur > 1) {
      cur -= 1
      context._changeChapter(cur, append)
    }
  },
  _changeChapter: (serialNums, append = false) => {
    context.setData({
      currentSerialNums: serialNums
    })
    context.fetchChapterContent(append)
  }
})