# DataNorm E2E Tests

End-to-end testing suite for the DataNorm Tax Preparation Platform using Playwright.

## Prerequisites

Before running E2E tests, ensure you have:

1. **Node.js** installed (v18 or higher)
2. **Local services running**:
   - Frontend: `http://localhost:5173`
   - API Gateway: `http://localhost:8000`
   - Database (PostgreSQL)
   - Redis
   - All backend services

## Installation

```bash
cd tests/e2e
npm install
npx playwright install
```

The `playwright install` command downloads the necessary browser binaries (Chromium, Firefox, WebKit).

## Configuration

### Environment Variables

Create a `.env` file in the `tests/e2e` directory:

```env
# Application URLs
BASE_URL=http://localhost:5173
API_URL=http://localhost:8000

# Test credentials
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123

# Test settings
CI=false
```

### Playwright Configuration

The Playwright configuration is in [playwright.config.ts](playwright.config.ts). Key settings:

- **Base URL**: `http://localhost:5173` (configurable via `BASE_URL` env var)
- **Browsers**: Chromium, Firefox, WebKit
- **Retries**: 2 retries on CI, 0 locally
- **Reporters**: HTML, List, JSON
- **Artifacts**: Screenshots and videos on failure

## Running Tests

### Run all tests

```bash
npm test
```

### Run tests in headed mode (see browser)

```bash
npm run test:headed
```

### Run tests in UI mode (interactive)

```bash
npm run test:ui
```

### Run tests in debug mode

```bash
npm run test:debug
```

### Run tests for specific browser

```bash
npm run test:chromium
npm run test:firefox
npm run test:webkit
```

### Run a specific test file

```bash
npx playwright test tests/auth.spec.ts
```

### Run tests matching a pattern

```bash
npx playwright test --grep "login"
```

## Test Files

- [tests/example.spec.ts](tests/example.spec.ts) - Basic example tests
- [tests/auth.spec.ts](tests/auth.spec.ts) - Authentication flows
- [tests/dashboard.spec.ts](tests/dashboard.spec.ts) - Dashboard functionality
- [tests/engagement.spec.ts](tests/engagement.spec.ts) - Engagement management

## Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Test implementation
    await page.click('button');
    await expect(page.locator('h1')).toHaveText('Expected Text');
  });
});
```

## Viewing Test Results

### HTML Report

After running tests, view the HTML report:

```bash
npm run test:report
```

This opens an interactive report showing:
- Test results
- Screenshots
- Videos
- Traces

### Test Artifacts

Test artifacts are saved to:
- `test-results/` - Test output and artifacts
- `playwright-report/` - HTML report
- `test-results.json` - JSON report

## Code Generation

Playwright can generate tests by recording your actions:

```bash
npm run codegen
```

Or generate tests for a specific URL:

```bash
npx playwright codegen http://localhost:5173
```

## Best Practices

### 1. Use Data Test IDs

Add `data-testid` attributes to your components:

```html
<button data-testid="submit-button">Submit</button>
```

```typescript
await page.click('[data-testid="submit-button"]');
```

### 2. Wait for Elements

Use Playwright's auto-waiting:

```typescript
await expect(page.locator('[data-testid="result"]')).toBeVisible();
```

### 3. Use Page Object Model

Create reusable page objects:

```typescript
class LoginPage {
  constructor(private page: Page) {}

  async login(email: string, password: string) {
    await this.page.fill('[name="email"]', email);
    await this.page.fill('[name="password"]', password);
    await this.page.click('button[type="submit"]');
  }
}
```

### 4. Isolate Tests

Each test should be independent:

```typescript
test.beforeEach(async ({ page }) => {
  // Reset state before each test
  await page.goto('/');
});
```

### 5. Use Fixtures

Create reusable test fixtures:

```typescript
const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await login(page);
    await use(page);
  },
});
```

## Debugging

### Debug Mode

```bash
npm run test:debug
```

This opens the Playwright Inspector for step-by-step debugging.

### VS Code Debugging

Install the Playwright Test extension for VS Code:
- Set breakpoints in test files
- Run tests in debug mode from the test explorer

### Screenshots and Videos

Screenshots and videos are automatically captured on test failure.

To always capture:

```typescript
test('example', async ({ page }) => {
  await page.screenshot({ path: 'screenshot.png' });
});
```

### Trace Viewer

View traces for failed tests:

```bash
npx playwright show-trace test-results/path-to-trace.zip
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Install dependencies
  run: |
    cd tests/e2e
    npm install
    npx playwright install --with-deps

- name: Run E2E tests
  run: |
    cd tests/e2e
    npm test

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: tests/e2e/playwright-report/
```

## Troubleshooting

### Tests failing to connect

Ensure all services are running:

```bash
# Check frontend
curl http://localhost:5173

# Check API
curl http://localhost:8000/health
```

### Browser not found

Install browsers:

```bash
npx playwright install
```

### Timeout errors

Increase timeouts in [playwright.config.ts](playwright.config.ts):

```typescript
use: {
  actionTimeout: 10000,
  navigationTimeout: 30000,
}
```

### Flaky tests

- Add explicit waits
- Use `waitForLoadState('networkidle')`
- Increase retries for specific tests

```typescript
test.describe.configure({ retries: 3 });
```

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Add comments for complex test logic
4. Ensure tests are independent and can run in any order
5. Update this README if adding new test patterns
