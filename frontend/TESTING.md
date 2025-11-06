# Frontend Testing Documentation

## Overview

This document describes the comprehensive testing strategy for the Aura Audit AI frontend application. Our testing approach follows industry best practices to ensure code quality, maintainability, and reliability.

## Testing Stack

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **TanStack Query**: API mocking and testing utilities
- **TypeScript**: Type-safe test code

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── __tests__/
│   │   │   │   ├── button.test.tsx
│   │   │   │   ├── input.test.tsx
│   │   │   │   ├── card.test.tsx
│   │   │   │   └── badge.test.tsx
│   │   └── engagements/
│   │       └── __tests__/
│   │           └── create-engagement-form.test.tsx
│   ├── lib/
│   │   ├── __tests__/
│   │   │   ├── test-utils.tsx
│   │   │   └── utils.test.ts
│   │   └── __mocks__/
│   │       └── api.ts
│   ├── store/
│   │   └── __tests__/
│   │       └── auth-store.test.ts
│   └── app/
│       └── (dashboard)/
│           └── dashboard/
│               └── engagements/
│                   └── __tests__/
│                       └── page.test.tsx
├── jest.config.js
├── jest.setup.js
└── TESTING.md
```

## Test Categories

### 1. Unit Tests

Unit tests verify individual functions, components, and utilities in isolation.

**Examples:**
- `utils.test.ts`: Tests for utility functions (formatCurrency, formatDate, etc.)
- `button.test.tsx`: Tests for Button component variants, states, and interactions
- `auth-store.test.ts`: Tests for authentication state management

**Coverage:**
- All utility functions
- All UI components
- State management stores
- Custom hooks

### 2. Integration Tests

Integration tests verify that multiple components work together correctly.

**Examples:**
- `page.test.tsx`: Tests for complete page functionality with data fetching
- `create-engagement-form.test.tsx`: Tests for form validation and submission

**Coverage:**
- Form submissions with validation
- API interactions with React Query
- User workflows (create, edit, delete)

### 3. Component Tests

Component tests verify rendering, user interactions, and accessibility.

**What we test:**
- Rendering with different props
- User interactions (clicks, typing, etc.)
- Conditional rendering
- State changes
- Accessibility attributes

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run tests with coverage
```bash
npm run test:coverage
```

### Run tests in CI mode
```bash
npm run test:ci
```

## Test Utilities

### Custom Render Function

Located in `src/lib/__tests__/test-utils.tsx`, this provides a wrapper with all necessary providers:

```typescript
import { render, screen } from '@/lib/__tests__/test-utils'

test('example', () => {
  render(<Component />)
  expect(screen.getByText('Hello')).toBeInTheDocument()
})
```

### Mock Data Factories

Pre-defined mock data for testing:

```typescript
import { mockUser, mockEngagement, mockJETestResult } from '@/lib/__tests__/test-utils'
```

Available mocks:
- `mockUser`: User object
- `mockEngagement`: Engagement object
- `mockJETestResult`: JE test result
- `mockAnomaly`: Anomaly detection result
- `mockMappingSuggestion`: Account mapping suggestion
- `mockQCResult`: QC policy result

## Writing Tests

### Basic Component Test

```typescript
import { render, screen } from '@/lib/__tests__/test-utils'
import { Button } from '../button'

describe('Button', () => {
  it('should render button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('should call onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### Testing with React Query

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

test('with query', async () => {
  render(<Component />, { wrapper: createWrapper() })

  await waitFor(() => {
    expect(screen.getByText('Loaded')).toBeInTheDocument()
  })
})
```

### Mocking API Calls

```typescript
jest.mock('@/lib/api', () => ({
  api: {
    engagements: {
      list: jest.fn(),
    },
  },
}))

import { api } from '@/lib/api'

test('fetches data', async () => {
  (api.engagements.list as jest.Mock).mockResolvedValue([mockEngagement])

  render(<Component />)

  await waitFor(() => {
    expect(screen.getByText('ABC Corp')).toBeInTheDocument()
  })
})
```

## Coverage Goals

We aim for the following coverage thresholds:

- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

Current coverage can be viewed by running:
```bash
npm run test:coverage
```

## Best Practices

### 1. Test Behavior, Not Implementation

❌ Bad:
```typescript
expect(component.state.count).toBe(5)
```

✅ Good:
```typescript
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

### 2. Use Accessible Queries

Priority order:
1. `getByRole`
2. `getByLabelText`
3. `getByPlaceholderText`
4. `getByText`
5. `getByTestId` (last resort)

### 3. Test User Interactions

```typescript
import { fireEvent, waitFor } from '@testing-library/react'

test('user can submit form', async () => {
  render(<Form />)

  fireEvent.change(screen.getByLabelText('Name'), {
    target: { value: 'John' }
  })

  fireEvent.click(screen.getByText('Submit'))

  await waitFor(() => {
    expect(screen.getByText('Success')).toBeInTheDocument()
  })
})
```

### 4. Clean Up After Tests

```typescript
beforeEach(() => {
  jest.clearAllMocks()
  localStorage.clear()
})
```

### 5. Use Descriptive Test Names

```typescript
describe('Button', () => {
  describe('Variants', () => {
    it('should render destructive variant with correct styles', () => {
      // test
    })
  })
})
```

## Accessibility Testing

All components should be tested for basic accessibility:

```typescript
test('is accessible', () => {
  render(<Button aria-label="Close">×</Button>)
  expect(screen.getByLabelText('Close')).toBeInTheDocument()
})

test('is keyboard accessible', () => {
  const handleClick = jest.fn()
  render(<Button onClick={handleClick}>Click</Button>)

  const button = screen.getByRole('button')
  button.focus()
  expect(button).toHaveFocus()
})
```

## Debugging Tests

### View rendered HTML
```typescript
const { debug } = render(<Component />)
debug()
```

### Check what queries are available
```typescript
screen.logTestingPlaygroundURL()
```

### Run single test file
```bash
npm test -- button.test.tsx
```

### Run tests matching pattern
```bash
npm test -- --testNamePattern="should render"
```

## Continuous Integration

Tests run automatically in CI on:
- Pull requests
- Pushes to main branch
- Manual workflow dispatch

CI configuration includes:
- Parallel test execution
- Coverage reporting
- Failure notifications

## Troubleshooting

### Common Issues

**Issue**: Tests timeout
```typescript
// Increase timeout for slow tests
jest.setTimeout(10000)
```

**Issue**: Async updates not reflected
```typescript
// Use waitFor
await waitFor(() => {
  expect(screen.getByText('Updated')).toBeInTheDocument()
})
```

**Issue**: Mock not working
```typescript
// Ensure mock is before import
jest.mock('@/lib/api')
import { api } from '@/lib/api'
```

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Contributing

When adding new features:
1. Write tests for new components
2. Update existing tests if behavior changes
3. Ensure coverage thresholds are met
4. Run tests before committing: `npm test`

## Summary

Our testing approach ensures:
- ✅ High code quality
- ✅ Confidence in refactoring
- ✅ Documentation through tests
- ✅ Faster debugging
- ✅ Better accessibility
- ✅ Reduced bugs in production
