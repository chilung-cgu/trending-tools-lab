// 模擬 GitHub Pages 的專案站點：把 _site 放在 /trending-tools-lab/ 子路徑下提供，
// 並對根路徑回 404（就像網域根不屬於這個專案）。只綁 loopback。
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const [dir, port = '8769', prefix = '/trending-tools-lab/'] = process.argv.slice(2);
if (!dir) throw new Error('用法：node scripts/serve_subpath.mjs <站點目錄> [port] [前綴]');
const root = path.resolve(dir);
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.mp4': 'video/mp4',
  '.glb': 'model/gltf-binary', '.pdf': 'application/pdf', '.txt': 'text/plain; charset=utf-8', '.md': 'text/markdown; charset=utf-8',
  '.log': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml' };

http.createServer((request, response) => {
  const url = new URL(request.url, 'http://127.0.0.1');
  if (!url.pathname.startsWith(prefix)) { response.writeHead(404); response.end('not found'); return; }
  let relative = decodeURIComponent(url.pathname.slice(prefix.length));
  let file = path.resolve(root, relative);
  if (file !== root && !file.startsWith(root + path.sep)) { response.writeHead(403); response.end('forbidden'); return; }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) {
    if (!url.pathname.endsWith('/')) { response.writeHead(301, { Location: url.pathname + '/' }); response.end(); return; }
    file = path.join(file, 'index.html');
  }
  if (!fs.existsSync(file)) { response.writeHead(404); response.end('not found'); return; }
  const range = request.headers.range;
  const size = fs.statSync(file).size;
  const type = types[path.extname(file)] || 'application/octet-stream';
  if (range) {
    const [startText, endText] = range.replace('bytes=', '').split('-');
    const start = Number(startText), end = endText ? Number(endText) : size - 1;
    response.writeHead(206, { 'Content-Type': type, 'Content-Range': 'bytes ' + start + '-' + end + '/' + size, 'Accept-Ranges': 'bytes', 'Content-Length': end - start + 1 });
    fs.createReadStream(file, { start, end }).pipe(response);
    return;
  }
  response.writeHead(200, { 'Content-Type': type, 'Content-Length': size, 'Accept-Ranges': 'bytes' });
  fs.createReadStream(file).pipe(response);
}).listen(Number(port), '127.0.0.1', () => console.log('serving ' + root + ' at http://127.0.0.1:' + port + prefix));
