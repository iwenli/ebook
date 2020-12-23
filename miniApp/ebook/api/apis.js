const request = require('request.js')

module.exports = {
  getCategoryList: (data) => request.get('/GetCategoryList', data),
  getBookList: (data) => request.get('/GetBookList', data),
}