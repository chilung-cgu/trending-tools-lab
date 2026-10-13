import fs from 'node:fs';
import { test, expect } from '@playwright/test';

test('Archify 主題、節點搜尋與 SVG 匯出可操作', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/artifacts/archify/crawler.html');
  await page.getByRole('button', { name: 'Toggle color theme', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.getByRole('button', { name: 'Find a node', exact: true }).click();
  const search = page.getByRole('searchbox', { name: 'Search diagram nodes' });
  await expect(search).toBeVisible();
  await search.fill('retry');
  await page.getByRole('button', { name: 'Focus Attempt Retry Loop, 4 related connections', exact: true }).click();
  await expect(search).toBeHidden();
  await page.getByRole('button', { name: 'Export diagram', exact: true }).click();
  const downloaded = page.waitForEvent('download');
  await page.getByRole('menuitem', { name: /SVG · Light/ }).click();
  const download = await downloaded;
  await download.saveAs('evidence/archify/browser-export.svg');
  const svg = fs.readFileSync('evidence/archify/browser-export.svg', 'utf8');
  expect(svg).toContain('<svg');
  expect(svg).toContain('Attempt Retry Loop');
  await page.getByRole('button', { name: 'Trace a directed route', exact: true }).last().click();
  await page.locator('#node-runner_start').click();
  await page.locator('#node-git_push').click();
  await expect(page.getByText('Actions Trigger to Git Commit & Push', { exact: true }).last()).toBeVisible();
  expect(errors).toEqual([]);
});
