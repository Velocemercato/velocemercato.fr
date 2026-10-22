const path = require('path');
module.exports = {
  content: [path.join(__dirname, '../index.html')],
  theme: {
    extend: {
      fontFamily: {
        comic: ['Bangers', 'Impact', 'sans-serif'],
        display: ['Anton', 'Impact', 'sans-serif'],
        body: ['Barlow', 'system-ui', 'sans-serif'],
        cond: ['Barlow Condensed', 'Arial Narrow', 'sans-serif']
      }
    }
  }
};
