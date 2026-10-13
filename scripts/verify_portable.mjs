import fs from 'node:fs';
import { chromium } from '@playwright/test';

const base = new URL(process.argv[2] || 'http://127.0.0.1:8767/');
if (base.protocol !== 'http:' || base.hostname !== '127.0.0.1') {
  throw new Error('請提供解壓成品的 loopback HTTP URL。');
}
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [], broken = [];
let checked = 0;
page.on('pageerror', error => errors.push(error.message));
try {
  for (const path of ['', 'README.html', 'docs/impeccable.html', 'docs/archify.html',
    'docs/hyperframes.html', 'docs/text-to-cad.html', 'docs/context-mode.html',
    'docs/worktrunk.html', 'docs/re-review.html', 'docs/review-resolution.html',
    'docs/progress.html', 'docs/next-ideas.html', 'docs/openrig.html', 'NOTICE.html', 'artifacts/openrig/', 'web/PRODUCT.html', 'web/DESIGN.html']) {
    const response = await page.goto(new URL(path, base).href);
    if (response.status() !== 200) broken.push({ url: page.url(), status: response.status() });
    for (const url of await page.locator('a[href],script[src],link[href],source[src]')
      .evaluateAll(elements => elements.map(e => e.href || e.src).filter(Boolean))) {
      if (new URL(url).origin !== base.origin) continue;
      const response = await page.request.get(url);
      checked++;
      if (response.status() !== 200) broken.push({ url, status: response.status() });
    }
  }
  await page.goto(base.href);
  await page.locator('video').evaluate(video => video.load());
  await page.waitForFunction(() => document.querySelector('video').duration === 30);
  await page.goto(new URL('web/', base).href);
  await page.locator('button[aria-controls="details"]').first().waitFor();
  await page.goto(new URL('artifacts/cad/', base).href);
  await page.getByRole('status').filter({ hasText: '3D 模型已載入' }).waitFor();
  await page.goto(new URL('artifacts/archify/crawler.html', base).href);
  await page.getByRole('button', { name: 'Toggle color theme', exact: true }).click();
  if (await page.locator('html').getAttribute('data-theme') !== 'dark') {
    throw new Error('Archify 主題切換未生效。');
  }
  const result = {
    verified_at_utc: new Date().toISOString(), base: base.href, viewport: [1440, 1000],
    checked_local_links: checked, broken_links: broken, page_errors: errors,
    video_duration: 30, cad_model_loaded: true, archify_theme_toggle: true,
    explorer_loaded: true,
  };
  fs.writeFileSync('evidence/portable-verification.json', JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result));
  if (broken.length || errors.length) process.exitCode = 1;
} finally {
  await browser.close();
}
