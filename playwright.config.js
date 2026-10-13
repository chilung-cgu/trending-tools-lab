import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 10_000 },
  workers: 1,
  reporter: [['list'], ['json', { outputFile: 'evidence/playwright.json' }]],
  use: { browserName: 'chromium', headless: true, baseURL: 'http://127.0.0.1:8765' },
  webServer: {
    command: 'python3 -m http.server 8765 --bind 127.0.0.1',
    url: 'http://127.0.0.1:8765',
    reuseExistingServer: false,
  },
});
