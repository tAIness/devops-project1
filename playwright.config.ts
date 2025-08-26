import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: 'e2e',
  timeout: 30000,
  reporter: [['html', { outputFolder: 'playwright-report', open: 'never' }], ['list']],
  use: { baseURL: process.env.BASE_URL || 'http://localhost:8080', headless: true, trace: 'on-first-retry' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]
});
