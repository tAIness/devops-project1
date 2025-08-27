import { test, expect } from '@playwright/test';

test('homepage shows cards and links work', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1, name: /super mario/i })).toBeVisible();
  await expect(page.getByText(/play super mario/i)).toBeVisible();
  await expect(page.getByText(/gallery/i)).toBeVisible();

  const nintendoLink = page.getByRole('link', { name: /nintendo shop/i });
  await expect(nintendoLink).toHaveAttribute(
    'href',
    /https:\/\/www\.nintendo\.com\/us\/store\/characters\/mushroom-kingdom\//
  );

  // gallery listing should be reachable (nginx autoindex on /images/)
  const res = await page.request.get('/images/');
  expect(res.ok()).toBeTruthy();
});
