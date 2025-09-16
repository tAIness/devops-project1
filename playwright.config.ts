// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

// ✅ process is a Node global – no import needed
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8081';

export default defineConfig({
  testDir: './e2e',                 // adjust if your tests live elsewhere
  timeout: 30_000,
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
  },
  reporter: [
    ['line'],
    ['allure-playwright'],          // Allure reporter
  ],
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    // add firefox/webkit if you want
  ],
});
