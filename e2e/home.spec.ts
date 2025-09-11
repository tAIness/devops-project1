import { test, expect } from '@playwright/test';

test('homepage shows cards and links work', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');

  // Headline
  await expect(page.getByRole('heading', { level: 1, name: /super mario/i })).toBeVisible();

  // Game link: check by href rather than text copy
  const gameLink = page.locator('a[href="/game/"]');
  await expect(gameLink).toBeVisible();

  // Gallery listing reachable (nginx autoindex)
  const gallery = await page.request.get('/images/');
  expect(gallery.ok()).toBeTruthy();

  // Nintendo external link (keep your assertion)
  const nintendoLink = page.getByRole('link', { name: /nintendo shop/i });
  await expect(nintendoLink).toHaveAttribute(
    'href',
    /https:\/\/www\.nintendo\.com\/us\/store\/characters\/mushroom-kingdom\//
  );
});
