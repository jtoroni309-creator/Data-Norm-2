import { test, expect } from '@playwright/test';

// Helper to login before tests
async function login(page) {
  const testEmail = process.env.TEST_USER_EMAIL || 'test@example.com';
  const testPassword = process.env.TEST_USER_PASSWORD || 'testpassword';

  await page.goto('/');
  await page.fill('input[type="email"], input[name="email"]', testEmail);
  await page.fill('input[type="password"], input[name="password"]', testPassword);
  await page.click('button[type="submit"]');
  await page.waitForURL(/dashboard|home/i, { timeout: 10000 });
}

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should display dashboard elements', async ({ page }) => {
    // Check for common dashboard elements
    await expect(page.locator('text=/dashboard/i')).toBeVisible();

    // Add more specific assertions based on your dashboard
    // Examples:
    // await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
    // await expect(page.locator('[data-testid="navigation"]')).toBeVisible();
  });

  test('should navigate to engagements', async ({ page }) => {
    // Click on engagements link/button
    await page.click('a:has-text("Engagement"), button:has-text("Engagement")');

    // Verify navigation
    await expect(page).toHaveURL(/engagement/i);
  });

  test('should display user information', async ({ page }) => {
    // Verify user profile or account information is visible
    // Adjust selectors based on your app structure
    await expect(page.locator('[data-testid="user-menu"], [aria-label="User menu"]')).toBeVisible();
  });

  test('should handle navigation between pages', async ({ page }) => {
    // Test navigation flow
    const navItems = [
      'Dashboard',
      'Clients',
      'Documents',
      'Reports'
    ];

    for (const item of navItems) {
      const navLink = page.locator(`a:has-text("${item}"), button:has-text("${item}")`);

      if (await navLink.isVisible()) {
        await navLink.click();
        // Wait for page to load
        await page.waitForLoadState('networkidle');

        // Verify URL or page content changed
        await expect(page).toHaveURL(new RegExp(item.toLowerCase(), 'i'));
      }
    }
  });
});
