import { test, expect } from '@playwright/test';

/**
 * Example E2E Test
 * This is a simple example to verify Playwright is set up correctly
 */

test.describe('Example Tests', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');

    // Basic assertions - check for the actual title
    await expect(page).toHaveTitle(/Aura Audit AI/); // Should have the app title
    expect(page.url()).toContain('localhost'); // Should be on localhost
  });

  test('should have visible content', async ({ page }) => {
    await page.goto('/');

    // Check if body has content
    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText.length).toBeGreaterThan(0);
  });

  test('should take a screenshot', async ({ page }) => {
    await page.goto('/');

    // Take screenshot (saved to test-results folder)
    await page.screenshot({ path: 'test-results/homepage.png', fullPage: true });
  });

  test('should handle API responses', async ({ page }) => {
    // Listen for API calls
    const apiCalls = [];

    page.on('response', response => {
      if (response.url().includes('/api/')) {
        apiCalls.push({
          url: response.url(),
          status: response.status()
        });
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Log API calls for debugging
    console.log('API Calls:', apiCalls);
  });
});
