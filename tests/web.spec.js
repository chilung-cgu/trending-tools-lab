import { test, expect } from '@playwright/test';
import fs from 'node:fs';
const data = JSON.parse(fs.readFileSync(new URL('../data/index.json', import.meta.url)));
const snapshots = [...data.snapshots].sort((a, b) => a.date.localeCompare(b.date));
const latest = snapshots.at(-1);
const url = 'http://127.0.0.1:8765/web/';
const number = value => new Intl.NumberFormat('en-US').format(value);

test('日期與週月榜呈現來源中的 rank、name、count', async ({ page }) => {
  await page.goto(url);
  for (const snapshot of snapshots) {
    await page.getByLabel('快照日期').selectOption(snapshot.date);
    for (const period of ['weekly', 'monthly']) {
      await page.getByLabel('榜單週期').selectOption(period);
      const rows = page.locator('#repo-body > tr');
      await expect(rows).toHaveCount(snapshot[period].length);
      for (let i = 0; i < snapshot[period].length; i++) {
        const item = snapshot[period][i];
        await expect(rows.nth(i).locator('.rank')).toHaveText(String(item.rank).padStart(2, '0'));
        await expect(rows.nth(i)).toContainText(item.full_name);
        await expect(rows.nth(i).locator('.period-stars')).toHaveText(number(item.period_stars));
      }
      await expect(page.getByRole('link', { name: '查看快照原始來源' })).toHaveAttribute('href', snapshot.source_url);
      await expect(page.locator('#provenance')).toContainText(snapshot.generated_at_taipei);
    }
  }
});

test('搜尋名稱與描述、無結果、重設及語言篩選', async ({ page }) => {
  await page.goto(url);
  const first = latest.weekly[0];
  await page.getByLabel('搜尋專案').fill(first.full_name);
  await expect(page.locator('#repo-body > tr')).toHaveCount(1);
  await page.getByLabel('搜尋專案').fill(first.description);
  await expect(page.locator('#repo-body > tr')).toHaveCount(1);
  await page.getByLabel('搜尋專案').fill('definitely-no-such-repository-xyz');
  await expect(page.getByRole('heading', { name: '找不到符合的專案' })).toBeVisible();
  await expect(page.locator('#repo-body > tr')).toHaveCount(0);
  await page.getByRole('button', { name: '清除篩選' }).click();
  await expect(page.locator('#repo-body > tr')).toHaveCount(latest.weekly.length);
  await page.getByLabel('程式語言').selectOption(first.language);
  await expect(page.locator('#repo-body > tr')).toHaveCount(latest.weekly.filter(item => item.language === first.language).length);
  await page.getByLabel('搜尋專案').fill('');
  await expect(page.getByLabel('搜尋專案')).toHaveValue('');
});

test('鍵盤詳情、歷史未觀測與來源連結', async ({ page }) => {
  await page.goto(url);
  const item = latest.weekly[0];
  const button = page.getByRole('button', { name: `查看 ${item.full_name} 詳情`, exact: true });
  await button.focus();
  await page.keyboard.press('Enter');
  const details = page.getByRole('region', { name: '專案詳細資訊' });
  await expect(details).toBeVisible();
  await expect(details.getByRole('heading', { name: item.full_name })).toBeFocused();
  await expect(details.locator('#history-body > tr')).toHaveCount(snapshots.length * 2);
  for (const snapshot of snapshots) {
    for (const period of ['weekly', 'monthly']) {
      const history = details.locator(`[data-date="${snapshot.date}"][data-period="${period}"]`);
      const observed = snapshot[period].find(repo => repo.full_name === item.full_name);
      await expect(history).toContainText(observed ? number(observed.period_stars) : '未觀測');
      await expect(history.getByRole('link', { name: '來源' })).toHaveAttribute('href', snapshot.source_url);
    }
  }
  await expect(details.getByRole('link', { name: '在 GitHub 開啟專案' })).toHaveAttribute('href', item.url);
  await details.getByRole('button', { name: '收起詳情' }).click();
  await expect(details).toBeHidden();
  await expect(button).toBeFocused();
});

for (const [width, height] of [[1920, 1080], [1280, 800], [390, 844]]) {
  test(`版面 ${width}x${height} 無水平溢出與截圖`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto(url);
    await expect(page.locator('#repo-body > tr')).toHaveCount(latest.weekly.length);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.screenshot({ path: `evidence/impeccable/${width}x${height}.png`, fullPage: true });
    await page.getByRole('button', { name: `查看 ${latest.weekly[0].full_name} 詳情`, exact: true }).click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.screenshot({ path: `evidence/impeccable/${width}x${height}-details.png`, fullPage: true });
  });
}

test('不可信文字以文字呈現、拒絕非 GitHub URL', async ({ page }) => {
  const fixture = structuredClone(data);
  const item = fixture.snapshots.find(s => s.date === latest.date).weekly[0];
  item.description = '<img src=x onerror="window.injected=true">';
  item.url = 'https://github.com.evil.example/repo';
  await page.route('**/data/index.json', route => route.fulfill({ json: fixture }));
  await page.goto(url);
  await expect(page.locator('#repo-body')).toContainText(item.description);
  await page.getByRole('button', { name: `查看 ${item.full_name} 詳情`, exact: true }).click();
  await expect(page.getByRole('link', { name: '在 GitHub 開啟專案' })).toHaveCount(0);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
});

test('資料載入失敗有可重試的錯誤狀態', async ({ page }) => {
  await page.route('**/data/index.json', route => route.fulfill({ status: 503, body: 'unavailable' }));
  await page.goto(url);
  await expect(page.getByRole('alert')).toContainText('無法載入快照');
  await page.unroute('**/data/index.json');
  await page.getByRole('button', { name: '重新載入' }).click();
  await expect(page.locator('#repo-body > tr')).toHaveCount(latest.weekly.length);
});
