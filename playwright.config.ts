// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

const BASE_URL = process.env.BASE_URL ?? 'http://127.0.0.1:8081';

export default defineConfig({
  testDir: 'e2e',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
  ['line'],
  ['junit', { outputFile: 'e2e/junit.xml' }],
  ['allure-playwright', { outputFolder: 'allure-results', detail: true, suiteTitle: true }],
  ],
  outputDir: 'test-results',
  use: {
    baseURL: BASE_URL,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    // { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    // { name: 'webkit',  use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
  command: 'echo CI server is external',
  url: 'http://127.0.0.1:8081',
  reuseExistingServer: true,   // <— crucial to avoid the port-in-use error
}
});

