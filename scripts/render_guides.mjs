import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO_BLOB = 'https://github.com/chilung-cgu/trending-tools-lab/blob/main/';
const RAW_SOURCE = /\.(py|sh|ya?ml|json|js|mjs|toml|log|txt)$/i;
const files = ['README.md', 'NOTICE.md', 'web/PRODUCT.md', 'web/DESIGN.md', ...fs.readdirSync(path.join(root, 'docs')).filter(f => f.endsWith('.md')).map(f => 'docs/' + f),
  ...['specs', 'plans'].flatMap(d => fs.readdirSync(path.join(root, 'docs/superpowers', d))
    .filter(f => f.endsWith('.md')).map(f => 'docs/superpowers/' + d + '/' + f))];

// 本機路徑 -> 發布後仍能使用的連結。
// .md 改連渲染後的網頁；程式、設定與資料檔改連 GitHub 原始碼檢視頁，因為 Pages 會讓瀏覽器下載或顯示成文字。
export function rewriteHref(target, hash, relative) {
  if (/^(https?:|mailto:|data:|\/\/)/.test(target)) return null;
  if (target.endsWith('.md')) return target.slice(0, -3) + '.html' + hash;
  if (RAW_SOURCE.test(target)) {
    const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(relative), target));
    return REPO_BLOB + resolved + hash;
  }
  return null;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  for (const relative of files) {
    const source = path.join(root, relative);
    if (!fs.existsSync(source)) continue;
    const markdown = fs.readFileSync(source, 'utf8');
    const body = marked.parse(markdown).replace(/href="([^"#]+)(#[^"]*)?"/g, (whole, target, hash = '') => {
      const next = rewriteHref(target, hash, relative);
      return next === null ? whole : 'href="' + next + '"';
    });
    const depth = relative.split('/').length - 1;
    const home = (depth === 0 ? './' : '../'.repeat(depth)) + 'index.html';
    const document = '<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>工具實驗室操作教學</title>\n' +
'<style>*{box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#f4f0e6;color:#172c32;line-height:1.8;max-width:880px;margin:auto;padding:32px 24px}pre{background:#172c32;color:#fff;padding:16px;border-radius:8px;overflow:auto}code{overflow-wrap:anywhere}a{color:#145943;text-underline-offset:4px}img,video{max-width:100%}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:10px;border:1px solid #aebeb5}h1,h2,h3{line-height:1.4}a:focus-visible{outline:3px solid #145943}</style>\n' +
'<nav><a href="' + home + '">← 回到成品入口</a></nav><main>' + body + '</main></html>';
    fs.writeFileSync(source.replace(/\.md$/, '.html'), document);
  }
  console.log('Rendered ' + files.length + ' guides (local Markdown sources only).');
}
