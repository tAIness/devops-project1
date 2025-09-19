// e2e/home.spec.ts
import { test, expect } from '@playwright/test';
import { allure } from 'allure-playwright';

test.describe('Website / Homepage / Smoke', () => {
  test('home: validate structure, content, navigation, and external links', async ({ page }) => {
    // Allure metadata + suite labels
    await allure.parentSuite('Website');
    await allure.suite('Homepage');
    await allure.subSuite('Smoke');
    await allure.owner('web-team');
    await allure.epic('Website');
    await allure.feature('Homepage');
    await allure.story('Full Homepage Validation');
    await allure.severity('critical');
    await allure.description(
      'Validates visible content, cards, links, images, and footer on the homepage.'
    );

    // Navigate and basic gate
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await expect(page).toHaveTitle(/Super Mario/i);

    // Page metadata
    const viewportMeta = page.locator('meta[name="viewport"]');
    await expect(viewportMeta).toBeAttached();
    const viewport = await viewportMeta.getAttribute('content');
    expect(viewport).toBe('width=device-width, initial-scale=1');

    // CSS present
    const cssLink = page.locator('link[rel="stylesheet"][href="/css/site.css"]');
    await expect(cssLink).toBeAttached();

    // Hero content
    const header = page.locator('.site-header h1');
    const subtext = page.locator('.site-header p');
    await expect(header).toHaveText(/Super Mario/);
    await expect(subtext).toContainText(/Click a card/);

    // Cards
    const game = page.locator('a.card:has-text("Play Super Mario")').first();
    await expect(game).toBeVisible();
    await expect(game).toHaveAttribute('href', '/game/');
    await expect(game).toHaveAttribute('title', /Play the game/);
    await expect(game.locator('img')).toHaveAttribute('alt', /Super Mario/);

    const gallery = page.locator('a.card:has-text("Gallery")').first();
    await expect(gallery).toBeVisible();
    await expect(gallery).toHaveAttribute('href', '/images/');
    await expect(gallery).toHaveAttribute('title', /gallery/i);

    const leaderboard = page.locator('a.card:has-text("Leaderboard")').first();
    await expect(leaderboard).toBeVisible();
    await expect(leaderboard).toHaveAttribute('href', '/leaderboard/');

    const shop = page.locator('a.card:has-text("Nintendo Shop")').first();
    await expect(shop).toBeVisible();
    const href = (await shop.getAttribute('href'))?.trim();
    expect(href).toBe('https://www.nintendo.com/us/store/characters/mushroom-kingdom/');
    await expect(shop).toHaveAttribute('target', '_blank');
    await expect(shop).toHaveAttribute('rel', /noopener/);

    // Footer
    const footer = page.locator('.site-footer small');
    await expect(footer).toContainText(/Images are placeholders/i);

    // Accessibility sweeps
    const images = page.locator('img');
    for (let i = 0, n = await images.count(); i < n; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      expect(alt && alt.trim().length).toBeTruthy();
    }
    const cards = page.locator('a.card');
    for (let i = 0, n = await cards.count(); i < n; i++) {
      const title = await cards.nth(i).getAttribute('title');
      expect(title && title.trim().length).toBeTruthy();
    }

    await allure.attachment('Homepage Raw HTML', await page.content(), 'text/html');
  });
});
