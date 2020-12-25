// components/image-preload/image-preload.js
Component({
  options: {
    addGlobalClass: true,
  },
  /**
   * 组件的属性列表
   */
  properties: {
    //默认图片
    defaultImage: {
      type: String,
      value: "http://img.txooo.com/2020/12/25/02fecf5824ec6e0271a646f122f94a7a.gif"
    },
    //原始图片
    originalImage: String,
    width: {
      type: Number,
      value: 0
    },
    height: {
      type: Number,
      value: 0
    },
    //图片剪裁mode，同Image组件的mode
    mode: String,
    loadmode: String,
    text: String,
    is_bg: Boolean
  },

  /**
   * 组件的初始数据
   */
  data: {
    finishLoadFlag: false
  },

  /**
   * 组件的方法列表
   */
  methods: {
    finishLoad: function (e) {
      this.setData({
        finishLoadFlag: true
      })
    }
  }
})