import { test, expect } from '@playwright/test';

test('入口提供實際影片與全部相對連結', async ({ page, request }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Trending 工具實驗室' })).toBeVisible();
  for (const href of await page.locator('a').evaluateAll(links => links.map(a => a.getAttribute('href')))) {
    const response = await request.get(new URL(href, 'http://127.0.0.1:8765/').href);
    expect(response.status(), href).toBe(200);
  }
  const video = page.locator('video');
  await video.evaluate(v => v.load());
  await expect.poll(() => video.evaluate(v => v.duration)).toBe(30);
  await video.evaluate(v => { v.currentTime = 13; });
  await expect.poll(() => video.evaluate(v => v.currentTime)).toBe(13);
});

test('CAD 本機模型載入、旋轉縮放與重設', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/artifacts/cad/');
  await expect(page.getByRole('status')).toContainText('3D 模型已載入');
  await expect(page.locator('canvas')).toBeVisible();
  await expect(page.getByText('100 × 30 × 15 mm', { exact: true })).toBeVisible();
  const canvas = page.locator('canvas');
  const box = await canvas.boundingBox();
  const initial = await page.evaluate(() => window.labViewer.camera.position.toArray());
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width / 2 + 100, box.y + box.height / 2 + 30, { steps: 8 });
  await page.mouse.up();
  expect(await page.evaluate(() => window.labViewer.camera.position.toArray())).not.toEqual(initial);
  await page.getByRole('button', { name: '重設視角' }).click();
  const reset = await page.evaluate(() => window.labViewer.camera.position.toArray());
  reset.forEach((value, i) => expect(value).toBeCloseTo(initial[i], 10));
  await page.getByLabel('顯示網格線').check();
  await expect(page.getByLabel('顯示網格線')).toBeChecked();
  expect(errors).toEqual([]);
});
