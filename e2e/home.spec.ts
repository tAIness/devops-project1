// e2e/home.spec.ts
import { test, expect } from '@playwright/test';
import { allure } from 'allure-playwright';

test('home: hero + links + gallery reachable', async ({ page }) => {
  await allure.owner('web-team');
  await allure.epic('Website');
  await allure.feature('Homepage');
  await allure.story('Cards & Links');

  await test.step('Open homepage', async () => {
    await page.goto('/'); // baseURL comes from playwright.config.ts
    // Accept either wording if copy changes:
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toBeVisible();
    await expect(h1).toHaveText(/(super mario|welcome)/i);
  });

  await test.step('Internal card/link is visible', async () => {
    await expect(page.locator('a[href="/game/"]')).toBeVisible();
  });

  await test.step('Gallery listing is reachable', async () => {
    const resp = await page.request.get('/images/');
    expect(resp.ok()).toBeTruthy();
  });

  await test.step('External Nintendo link points to correct URL', async () => {
    const nintendo = page.getByRole('link', { name: /nintendo shop/i });
    await expect(nintendo).toHaveAttribute(
      'href',
      /https:\/\/www\.nintendo\.com\/us\/store\/characters\/mushroom-kingdom\//
    );
  });

  // Attach the HTML for Allure
  await allure.attachment('Raw HTML', await page.content(), 'text/html');
});
