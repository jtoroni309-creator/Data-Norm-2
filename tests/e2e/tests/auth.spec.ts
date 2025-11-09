import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/DataNorm|Tax Preparation/i);
    // Add more specific assertions based on your login page
    await expect(page.locator('input[type="email"], input[name="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"], input[name="password"]')).toBeVisible();
  });

  test('should show error on invalid login', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[type="email"], input[name="email"]', 'invalid@example.com');
    await page.fill('input[type="password"], input[name="password"]', 'wrongpassword');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for error message
    await expect(page.locator('text=/invalid|error|incorrect/i')).toBeVisible({ timeout: 5000 });
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Note: Replace with actual test credentials
    const testEmail = process.env.TEST_USER_EMAIL || 'test@example.com';
    const testPassword = process.env.TEST_USER_PASSWORD || 'testpassword';

    await page.fill('input[type="email"], input[name="email"]', testEmail);
    await page.fill('input[type="password"], input[name="password"]', testPassword);

    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard or authenticated page
    await page.waitForURL(/dashboard|home/i, { timeout: 10000 });

    // Verify user is logged in (adjust selector based on your app)
    await expect(page.locator('text=/dashboard|welcome/i')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    const testEmail = process.env.TEST_USER_EMAIL || 'test@example.com';
    const testPassword = process.env.TEST_USER_PASSWORD || 'testpassword';

    await page.fill('input[type="email"], input[name="email"]', testEmail);
    await page.fill('input[type="password"], input[name="password"]', testPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/dashboard|home/i, { timeout: 10000 });

    // Click logout button (adjust selector based on your app)
    await page.click('button:has-text("Logout"), a:has-text("Logout")');

    // Verify redirected to login page
    await expect(page).toHaveURL(/login|^\/$/, { timeout: 5000 });
  });
});
