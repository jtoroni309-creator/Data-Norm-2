import { Page, expect } from '@playwright/test';

export interface TestCredentials {
  cpaPortal: {
    email: string;
    password: string;
    firmId: string;
  };
  clientPortal: {
    email: string;
    password: string;
  };
}

export const TEST_CREDENTIALS: TestCredentials = {
  cpaPortal: {
    email: process.env.CPA_TEST_EMAIL || 'test.auditor@auraai.test',
    password: process.env.CPA_TEST_PASSWORD || 'TestPassword123!',
    firmId: process.env.CPA_FIRM_ID || 'test-firm-001',
  },
  clientPortal: {
    email: process.env.CLIENT_TEST_EMAIL || 'test.client@enterprise.test',
    password: process.env.CLIENT_TEST_PASSWORD || 'ClientPassword123!',
  },
};

export const PORTAL_URLS = {
  cpaPortal: process.env.CPA_PORTAL_URL || 'https://app.auraai.toroniandcompany.com',
  clientPortal: process.env.CLIENT_PORTAL_URL || 'https://portal.auraai.toroniandcompany.com',
  apiBase: process.env.API_BASE_URL || 'https://api.auraai.toroniandcompany.com',
};

export class AuthHelper {
  constructor(private page: Page) {}

  /**
   * Login to CPA Portal
   */
  async loginToCPAPortal(credentials = TEST_CREDENTIALS.cpaPortal): Promise<void> {
    await this.page.goto(PORTAL_URLS.cpaPortal);

    // Wait for login form
    await this.page.waitForSelector('[data-testid="login-form"], form[action*="login"], #login-form', {
      timeout: 15000,
    });

    // Try different selectors for email input
    const emailInput = await this.page.locator(
      'input[type="email"], input[name="email"], input[placeholder*="email"], #email'
    ).first();
    await emailInput.fill(credentials.email);

    // Try different selectors for password input
    const passwordInput = await this.page.locator(
      'input[type="password"], input[name="password"], #password'
    ).first();
    await passwordInput.fill(credentials.password);

    // Submit form
    const submitButton = await this.page.locator(
      'button[type="submit"], button:has-text("Sign in"), button:has-text("Login"), button:has-text("Log in")'
    ).first();
    await submitButton.click();

    // Wait for successful login (dashboard or main content)
    await expect(this.page).toHaveURL(/.*dashboard|.*home|.*engagements/, { timeout: 30000 });
  }

  /**
   * Login to Client Portal
   */
  async loginToClientPortal(credentials = TEST_CREDENTIALS.clientPortal): Promise<void> {
    await this.page.goto(PORTAL_URLS.clientPortal);

    await this.page.waitForSelector('[data-testid="login-form"], form, .login-container', {
      timeout: 15000,
    });

    const emailInput = await this.page.locator(
      'input[type="email"], input[name="email"], input[placeholder*="email"], #email'
    ).first();
    await emailInput.fill(credentials.email);

    const passwordInput = await this.page.locator(
      'input[type="password"], input[name="password"], #password'
    ).first();
    await passwordInput.fill(credentials.password);

    const submitButton = await this.page.locator(
      'button[type="submit"], button:has-text("Sign in"), button:has-text("Login")'
    ).first();
    await submitButton.click();

    await expect(this.page).toHaveURL(/.*portal|.*dashboard|.*documents/, { timeout: 30000 });
  }

  /**
   * Accept client portal invitation
   */
  async acceptInvitation(inviteToken: string): Promise<void> {
    await this.page.goto(`${PORTAL_URLS.clientPortal}/invite/${inviteToken}`);

    // Wait for invitation acceptance page
    await this.page.waitForLoadState('networkidle');

    // Check if we need to create an account or just accept
    const createAccountButton = await this.page.locator(
      'button:has-text("Create Account"), button:has-text("Accept Invitation"), button:has-text("Accept")'
    ).first();

    if (await createAccountButton.isVisible()) {
      // Fill registration form if needed
      const nameInput = await this.page.locator('input[name="name"], input[placeholder*="name"]').first();
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test Client User');
      }

      const passwordInputs = await this.page.locator('input[type="password"]').all();
      if (passwordInputs.length >= 1) {
        await passwordInputs[0].fill(TEST_CREDENTIALS.clientPortal.password);
      }
      if (passwordInputs.length >= 2) {
        await passwordInputs[1].fill(TEST_CREDENTIALS.clientPortal.password);
      }

      await createAccountButton.click();
    }

    // Wait for acceptance confirmation
    await this.page.waitForURL(/.*dashboard|.*engagements|.*welcome/, { timeout: 30000 });
  }

  /**
   * Logout from current portal
   */
  async logout(): Promise<void> {
    const logoutButton = await this.page.locator(
      '[data-testid="logout"], button:has-text("Logout"), button:has-text("Sign out"), a:has-text("Logout")'
    ).first();

    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await this.page.waitForURL(/.*login|.*signin/, { timeout: 15000 });
    }
  }

  /**
   * Get authentication token from storage
   */
  async getAuthToken(): Promise<string | null> {
    const localStorage = await this.page.evaluate(() => {
      return window.localStorage.getItem('authToken') ||
             window.localStorage.getItem('token') ||
             window.localStorage.getItem('access_token');
    });
    return localStorage;
  }

  /**
   * Check if currently logged in
   */
  async isLoggedIn(): Promise<boolean> {
    const token = await this.getAuthToken();
    return token !== null;
  }
}
