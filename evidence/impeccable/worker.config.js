import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: '../../tests', testMatch: 'web.spec.js', timeout: 10000, workers: 1, reporter: 'list', outputDir: './test-results', use: { headless: true }, webServer: { command: 'python3 -m http.server 8765 --bind 127.0.0.1', cwd: '../..', url: 'http://127.0.0.1:8765', reuseExistingServer: true } });
