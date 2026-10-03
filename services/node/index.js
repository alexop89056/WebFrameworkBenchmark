const http = require('http');

const server = http.createServer((req, res) => {
  if (req.url !== '/') {
    res.writeHead(404);
    return res.end();
  }

  const body = JSON.stringify({ message: 'hello', framework: 'node-native' });
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(body);
});

server.listen(8000, '0.0.0.0');
