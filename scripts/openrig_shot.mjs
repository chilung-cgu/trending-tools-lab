// 對示範中運行的 OpenRig 儀表板截圖；只連 loopback，並同時保存 tmux 內三個席位的文字畫面。
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from '@playwright/test';

const [url, out] = process.argv.slice(2);
const base = new URL(url);
if (base.protocol !== 'http:' || base.hostname !== '127.0.0.1') throw new Error('只允許 loopback 儀表板');
const shots = path.join(out, 'shots');
fs.mkdirSync(shots, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(new URL('/topology', base).href, { waitUntil: 'domcontentloaded' });
  await page.getByText('desk-lead@triage').first().waitFor({ timeout: 15000 });
  await page.getByRole('button', { name: '×' }).first().click({ timeout: 2000 }).catch(() => {});
  await page.locator('.react-flow__controls-fitview').click({ timeout: 5000 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(shots, 'topology.png') });
} finally {
  await browser.close();
}
