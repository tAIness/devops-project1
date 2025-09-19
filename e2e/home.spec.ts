// e2e/home.spec.ts
import { test, expect } from '@playwright/test';
import { allure } from 'allure-playwright';

test.describe('Website / Homepage / Smoke', () => {
  test('home: validate structure, content, navigation, and external links', async ({ page }) => {
    await allure.owner('web-team');
    await allure.epic('Website');
    await allure.feature('Homepage');
    await allure.story('Full Homepage Validation');
    await allure.severity('critical');
    await allure.description('Validates all visible content, cards, links, images, and footer on homepage. Ensures external link matches Nintendo official page.');

    await page.goto('/');
    await expect(page).toHaveTitle(/Super Mario/i); // more robust gate than the strict header selector
  // === Navigate and wait for critical element ===
  await test.step('Navigate to homepage and wait for content', async () => {
    await page.goto('/');
    // Wait for hero header — ensures page is rendered before assertions
    await page.waitForSelector('header.site-header h1', { timeout: 10000 });
  });

  // === Step 1: Validate page metadata ===
  await test.step('Page has correct title and viewport', async () => {
    await expect(page).toHaveTitle('Super Mario — Static Site');
    const viewportMeta = page.locator('meta[name="viewport"]');
    await expect(viewportMeta).toBeAttached(); // ✅ Correct for <meta>
    const viewport = await viewportMeta.getAttribute('content');
    expect(viewport).toBe('width=device-width, initial-scale=1');
  });

  // === Step 2: Validate CSS is loaded ===
  await test.step('CSS stylesheet is loaded', async () => {
    const cssLink = page.locator('link[rel="stylesheet"][href="/css/site.css"]');
    await expect(cssLink).toBeAttached(); // ✅ Correct for <link> — NOT toBeVisible()
  });

  // === Step 3: Validate hero header content ===
  await test.step('Hero section displays correct heading and description', async () => {
    const header = page.locator('.site-header h1');
    const subtext = page.locator('.site-header p');
    await expect(header).toHaveText('Super Mario');
    await expect(subtext).toHaveText('Click a card to play the game, view the leaderboard, or browse images.');
  });

  // === Step 4: Validate "Play Super Mario" card ===
  await test.step('Play Game card is visible and links correctly', async () => {
    const card = page.locator('a.card:has-text("Play Super Mario")').first();
    await expect(card).toBeVisible();
    await expect(card).toHaveAttribute('href', '/game/');
    await expect(card).toHaveAttribute('title', 'Play the game!');
    await expect(card.locator('img')).toHaveAttribute('alt', 'Super Mario standing');
  });

  // === Step 5: Validate "Gallery" card ===
  await test.step('Gallery card is visible and links correctly', async () => {
    const card = page.locator('a.card:has-text("Gallery")').first();
    await expect(card).toBeVisible();
    await expect(card).toHaveAttribute('href', '/images/');
    await expect(card).toHaveAttribute('title', 'Open the Mario gallery');
    await expect(card.locator('img')).toHaveAttribute('alt', 'Gallery');
  });

  // === Step 6: Validate "Leaderboard" card ===
  await test.step('Leaderboard card is visible and links correctly', async () => {
    const card = page.locator('a.card:has-text("Leaderboard")').first();
    await expect(card).toBeVisible();
    await expect(card).toHaveAttribute('href', '/leaderboard/');
    await expect(card).toHaveAttribute('title', 'View leaderboard');
    await expect(card.locator('img')).toHaveAttribute('alt', 'Leaderboard');
  });

  // === Step 7: Validate "Nintendo Shop" external card ===
  await test.step('Nintendo Shop card opens externally with correct URL', async () => {
    const card = page.locator('a.card:has-text("Nintendo Shop →")').first();
    await expect(card).toBeVisible();
    // Validate exact URL (trim any accidental spaces from HTML)
    const href = await card.getAttribute('href');
    expect(href?.trim()).toBe('https://www.nintendo.com/us/store/characters/mushroom-kingdom/');
    await expect(card).toHaveAttribute('target', '_blank');
    await expect(card).toHaveAttribute('rel', 'noopener noreferrer');
    await expect(card).toHaveAttribute('title', 'Nintendo Shop — Mushroom Kingdom');
    await expect(card.locator('img')).toHaveAttribute('alt', 'Nintendo Shop — Mushroom Kingdom');
  });

  // === Step 8: Validate footer disclaimer ===
  await test.step('Footer displays correct disclaimer', async () => {
    const footer = page.locator('.site-footer small');
    await expect(footer).toHaveText('Images are placeholders—use your own licensed artwork.');
  });

  // === Step 9: Validate accessibility - all images have alt text ===
  await test.step('All images have non-empty alt attributes', async () => {
    const images = page.locator('img');
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      expect(alt).toBeTruthy();
      expect(alt).not.toBe('');
    }
  });

  // === Step 10: Validate all card links have title attributes ===
  await test.step('All card links have descriptive title attributes', async () => {
    const cards = page.locator('a.card');
    const count = await cards.count();
    for (let i = 0; i < count; i++) {
      const title = await cards.nth(i).getAttribute('title');
      expect(title).toBeTruthy();
      expect(title).not.toBe('');
    }
  });

  // === Attach full HTML for deep debugging ===
  await allure.attachment('Homepage Raw HTML', await page.content(), 'text/html');
});
