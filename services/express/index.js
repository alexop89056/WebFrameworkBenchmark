const express = require('express');

const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'hello', framework: 'express' });
});

app.listen(8000, '0.0.0.0');
