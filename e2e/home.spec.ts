// e2e/home.spec.ts
import { test, expect } from '@playwright/test';
import { allure } from 'allure-playwright';

test('home: hero + links + gallery reachable', async ({ page }) => {
  // === Allure Metadata ===
  await allure.owner('web-team');
  await allure.epic('Website');
  await allure.feature('Homepage');
  await allure.story('Cards & Links');
  await allure.severity('critical'); // optional: 'minor', 'normal', 'critical', 'blocker'
  await allure.description('Validates homepage layout, internal navigation, gallery API endpoint, and external marketing link.');

  // === Step 1: Open homepage and validate hero ===
  await test.step('Open homepage', async () => {
    await page.goto('/'); // baseURL from config
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toBeVisible();
    await expect(h1).toHaveText(/(super mario|welcome)/i); // flexible copy match
  });

  // === Step 2: Validate internal navigation link ===
  await test.step('Internal card/link is visible', async () => {
    const gameLink = page.locator('a[href="/game/"]');
    await expect(gameLink).toBeVisible();
  });

  // === Step 3: Validate gallery API endpoint ===
  await test.step('Gallery listing is reachable', async () => {
    const resp = await page.request.get('/images/');
    await expect(resp).toBeOK(); // Playwright-native assertion (better than .ok())
  });

  // === Step 4: Validate external marketing link ===
  await test.step('External Nintendo link points to correct URL', async () => {
    const nintendoLink = page.getByRole('link', { name: /nintendo shop/i });
    await expect(nintendoLink).toBeVisible();
    await expect(nintendoLink).toHaveAttribute(
      'href',
      /https:\/\/www\.nintendo\.com\/us\/store\/characters\/mushroom-kingdom\//
    );
  });

  // === Optional: Attach full HTML for deep debugging ===
  await allure.attachment('Raw HTML', await page.content(), 'text/html');

  // === Optional: Attach screenshot even on success (if needed) ===
  // await allure.attachment('Final Screenshot', await page.screenshot(), 'image/png');
});
