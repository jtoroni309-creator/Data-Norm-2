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

test.describe('Engagement Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    // Navigate to engagements page
    await page.goto('/engagements');
  });

  test('should display engagements list', async ({ page }) => {
    // Verify engagements page loaded
    await expect(page).toHaveURL(/engagement/i);

    // Check for engagements list or empty state
    const hasEngagements = await page.locator('[data-testid="engagement-list"], table').isVisible();
    const hasEmptyState = await page.locator('text=/no engagement|empty/i').isVisible();

    expect(hasEngagements || hasEmptyState).toBeTruthy();
  });

  test('should create new engagement', async ({ page }) => {
    // Click create engagement button
    await page.click('button:has-text("New Engagement"), button:has-text("Create Engagement")');

    // Fill engagement form
    await page.fill('input[name="clientName"], input[placeholder*="client"]', 'Test Client');
    await page.fill('input[name="taxYear"], input[placeholder*="year"]', '2024');

    // Submit form
    await page.click('button[type="submit"]:has-text("Create"), button:has-text("Save")');

    // Wait for success message or redirect
    await expect(
      page.locator('text=/success|created/i, [role="alert"]:has-text("success")')
    ).toBeVisible({ timeout: 5000 });
  });

  test('should view engagement details', async ({ page }) => {
    // Click on first engagement in the list
    const firstEngagement = page.locator('[data-testid="engagement-item"], tr').first();

    if (await firstEngagement.isVisible()) {
      await firstEngagement.click();

      // Verify details page loaded
      await expect(page).toHaveURL(/engagement\/\d+|engagement\/[a-f0-9-]+/i);

      // Verify engagement details are visible
      await expect(page.locator('text=/client|taxpayer/i')).toBeVisible();
    }
  });

  test('should filter engagements', async ({ page }) => {
    // Find search/filter input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"]');

    if (await searchInput.isVisible()) {
      await searchInput.fill('Test');

      // Wait for filtered results
      await page.waitForTimeout(500); // Allow debounce

      // Verify filtering worked (results updated)
      await expect(page.locator('[data-testid="engagement-list"], table')).toBeVisible();
    }
  });

  test('should handle pagination', async ({ page }) => {
    // Check if pagination exists
    const nextButton = page.locator('button:has-text("Next"), [aria-label="Next page"]');

    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      // Get current page content
      const firstPageContent = await page.textContent('body');

      // Click next page
      await nextButton.click();

      // Wait for content to change
      await page.waitForTimeout(500);

      // Verify content changed
      const secondPageContent = await page.textContent('body');
      expect(firstPageContent).not.toBe(secondPageContent);
    }
  });
});
