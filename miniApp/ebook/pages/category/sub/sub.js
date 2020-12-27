// pages/category/sub/sub.js
const apis = require('../../../api/apis.js');
const util = require('../../../utils/util.js');
const app = getApp()
Page({
  /**
   * 页面的初始数据
   */
  data: {
    isCard: false,
    title: '',
    list: [],
    fetchFinsh: false,
    hasData: true,

    query: {
      pageIndex: 1,
      pageRows: 10,
      categoryId: 0,
      subCategoryId: 0,
      keyword: '',
    }
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    const {
      id,
      name
    } = options;
    this.setData({
      'title': name || '玄幻',
      'query.subCategoryId': id
    })
    this.fetch()
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

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
  onReachBottom: function () {
    if (this.data.hasData && !this.data.fetchFinsh) {
      this.setData({
        'query.pageIndex': this.data.query.pageIndex + 1
      })
      this.fetch()
    }
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },
  /**
   * 加载书籍
   */
  fetch: function () {
    const that = this
    let list = that.data.list;
    const query = {
      pageIndex: that.data.query.pageIndex,
      pageRows: that.data.query.pageRows,
      'search.categoryId': that.data.query.categoryId,
      'search.subCategoryId': that.data.query.subCategoryId,
      'search.keyword': that.data.query.keyword,
    }
    console.log(query)
    apis.getBookList(query).then((res) => {
      const preListCount = list.length
      res.Data.forEach((book, index) => {
        list.push({
          index: index + preListCount + 1,
          id: book.Id,
          name: book.Name,
          author: book.Author,
          cover: book.Cover,
          thumCover: util.cdnImageFormatHandler.withWidth(book.Cover, 150),
          desc: book.Desc,
          status: book.Status,
          rate: book.Rate || 10
        })
      });
      console.log(list)
      that.setData({
        list: list,
      })
      if (res.Total === 0) {
        that.setData({
          hasData: false
        })
      } else if (res.Total <= list.length) {
        that.setData({
          fetchFinsh: true
        })
      }
    })
  },
})