import { test, expect } from '@playwright/test';

test('OpenRig 成果頁呈現真實團隊紀錄、限制且不連外', async ({ page }) => {
  const external = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.hostname !== '127.0.0.1') external.push(request.url());
  });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/artifacts/openrig/');
  await expect(page.getByRole('heading', { name: 'OpenRig 多代理團隊實驗場' })).toBeVisible();
  await expect(page.getByText('0.6.10', { exact: false }).first()).toBeVisible();
  await expect(page.locator('[data-seat]')).toHaveCount(3);
  await expect(page.locator('[data-queue-hop]')).toHaveCount(3);
  await expect(page.locator('#limits')).toContainText('stub 席位不呼叫模型');
  await expect(page.getByRole('heading', { name: '先釐清：需要多個帳號嗎？' })).toBeVisible();
  await expect(page.getByText('不需要第二個帳號。', { exact: false }).first()).toBeVisible();
  await expect(page.locator('#restore-plain')).toContainText('awaiting-decision');
  await expect(page.locator('#restore-fresh')).toContainText('fresh-primed');
  await expect(page.locator('#checks li')).toHaveCount(10);
  await expect(page.locator('#checks li', { hasText: '未通過' })).toHaveCount(0);
  await expect(page.locator('img[alt]').first()).toBeVisible();
  for (const link of await page.locator('a').evaluateAll(a => a.map(x => x.getAttribute('href')))) {
    if (link.startsWith('http')) continue;
    const response = await page.request.get(new URL(link, page.url()).href);
    expect(response.status(), link).toBe(200);
  }
  expect(external).toEqual([]);
  expect(errors).toEqual([]);
});
