// pages/category/home/home.js
const apis = require('../../../api/apis.js')
const util = require('../../../utils/util.js')
const app = getApp()
Component({
  options: {
    addGlobalClass: true,
  },
  /**
   * 组件的属性列表
   */
  properties: {

  },

  /**
   * 组件的初始数据
   */
  data: {
    StatusBar: app.globalData.StatusBar,
    CustomBar: app.globalData.CustomBar,
    Custom: app.globalData.Custom,
    TabCur: 0,
    MainCur: 0,
    VerticalNavTop: 0,
    rawList: [],
    list: [],
    load: true,
    currentSex: 1,
  },

  /**
   * 组件的方法列表
   */
  methods: {
    show() {
      const list = this.data.rawList.filter(m => m.sex == this.data.currentSex)
      for (let index = 0; index < list.length; index++) {
        list[index].index = index
      }
      this.setData({
        list: list,
        TabCur: 0,
        MainCur: 0,
        VerticalNavTop: 0
      })
    },
    tabSexSelect(e) {
      if (this.data.currentSex != e.currentTarget.dataset.id) {
        this.setData({
          currentSex: e.currentTarget.dataset.id * 1
        })
        this.show()
      }
    },
    tabSelect(e) {
      this.setData({
        TabCur: e.currentTarget.dataset.index,
        MainCur: e.currentTarget.dataset.index,
        VerticalNavTop: (e.currentTarget.dataset.index - 1) * 50
      })
    },
    VerticalMain(e) {
      let that = this;
      let list = this.data.list;
      let tabHeight = 0;
      if (this.data.load) {
        for (let i = 0; i < list.length; i++) {
          let view = that.createSelectorQuery().select("#main-" + list[i].index);
          view.fields({
            size: true
          }, data => {
            list[i].top = tabHeight;
            tabHeight = tabHeight + data.height;
            list[i].bottom = tabHeight;
          }).exec();
        }
        that.setData({
          load: false,
          list: list
        })
      }
      let scrollTop = e.detail.scrollTop + 20;
      for (let i = 0; i < list.length; i++) {
        if (scrollTop > list[i].top && scrollTop < list[i].bottom) {
          that.setData({
            VerticalNavTop: (list[i].index - 1) * 50,
            TabCur: list[i].index
          })
          return false
        }
      }
    }
  },
  lifetimes: {
    created() {

    },
    attached() {
      apis.getCategoryList({
        id: -1
      }).then((res) => {
        let list = [];
        res.Data.forEach((category, index) => {
          list.push({
            id: category.Id,
            name: category.Name,
            parentId: category.ParentId,
            sex: category.Sex,
            url: category.Url
          })
        });
        const rawList = util.listConvertToTreeList(list)
        this.setData({
          rawList: rawList
        })
        this.show()
      })
    },
    ready() {
      // wx.hideLoading()
    }
  }
})