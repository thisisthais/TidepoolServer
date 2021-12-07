var express = require('express');
const path = require('path');
var app = express();

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.listen(3000, () => {
  console.log('Server running on port 3000')
})