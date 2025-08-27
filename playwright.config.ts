import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e',
  testMatch: /.*\.spec\.(ts|js|tsx|jsx)/,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8080',
    headless: true,
  },
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['line']
  ],
});
