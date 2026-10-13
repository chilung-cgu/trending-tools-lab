import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = ['README.md', 'NOTICE.md', 'web/PRODUCT.md', 'web/DESIGN.md', ...fs.readdirSync(path.join(root, 'docs')).filter(f => f.endsWith('.md')).map(f => `docs/${f}`)];
for (const relative of files) {
  const source = path.join(root, relative);
  if (!fs.existsSync(source)) continue;
  const markdown = fs.readFileSync(source, 'utf8');
  const body = marked.parse(markdown).replace(/href="([^"#]+)\.md(#[^"]*)?"/g, 'href="$1.html$2"');
  const home = relative === 'README.md' || relative === 'NOTICE.md' ? './index.html' : '../index.html';
  const document = `<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>工具實驗室操作教學</title>
<style>*{box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#f4f0e6;color:#172c32;line-height:1.8;max-width:880px;margin:auto;padding:32px 24px}pre{background:#172c32;color:#fff;padding:16px;border-radius:8px;overflow:auto}code{overflow-wrap:anywhere}a{color:#145943;text-underline-offset:4px}img,video{max-width:100%}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:10px;border:1px solid #aebeb5}h1,h2,h3{line-height:1.4}a:focus-visible{outline:3px solid #145943}</style>
<nav><a href="${home}">← 回到成品入口</a></nav><main>${body}</main></html>`;
  fs.writeFileSync(source.replace(/\.md$/, '.html'), document);
}
console.log(`Rendered ${files.length} guides (local Markdown sources only).`);
