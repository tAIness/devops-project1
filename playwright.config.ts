import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['list'],                                     // console
    ['allure-playwright', {
      outputFolder: 'allure-results',             // default name; we’ll upload this
      detail: true,
      suiteTitle: false
   }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:8080',
  }
});
