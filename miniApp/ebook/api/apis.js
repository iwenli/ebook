const request = require('request.js')

module.exports = {
  getCategoryList: (data) => request.get('/GetCategoryList', data),
  getBookList: (data) => request.get('/GetBookList', data),
  getBookDetail: (data) => request.get('/GetBookDetail', data),
  getChapter: (data) => request.get('/GetChapter', data),
}