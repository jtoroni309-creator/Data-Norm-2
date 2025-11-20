import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { UserRole } from '@/types'

// Create a custom render function that includes providers
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

interface AllProvidersProps {
  children: React.ReactNode
}

export function AllProviders({ children }: AllProvidersProps) {
  const testQueryClient = createTestQueryClient()

  return (
    <QueryClientProvider client={testQueryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Mock data factories
export const mockUser = {
  id: 'user-1',
  email: 'test@example.com',
  full_name: 'Test User',
  role: UserRole.PARTNER,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

export const mockEngagement = {
  id: 'eng-1',
  client_name: 'ABC Corporation',
  engagement_type: 'audit' as const,
  fiscal_year_end: '2024-12-31',
  status: 'planning' as const,
  partner_id: 'user-1',
  manager_id: 'user-2',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

export const mockJETestResult = {
  test_type: 'Round Dollar',
  journal_entry_id: 'je-1',
  entry_number: 'JE-2024-001',
  entry_date: '2024-01-15',
  amount: 10000,
  flagged: true,
  reason: 'Round dollar amount detected',
  score: 0.85,
}

export const mockAnomaly = {
  id: 'anomaly-1',
  engagement_id: 'eng-1',
  transaction_id: 'txn-1',
  anomaly_score: 0.92,
  severity: 'high' as const,
  detection_method: 'zscore',
  description: 'Unusual transaction amount detected',
  amount: 50000,
  detected_at: '2024-01-15T00:00:00Z',
}

export const mockMappingSuggestion = {
  id: 'map-1',
  engagement_id: 'eng-1',
  trial_balance_line_id: 'tb-1',
  source_account_code: '1000',
  source_account_name: 'Cash in Bank',
  suggested_account_code: '1100',
  suggested_account_name: 'Cash and Cash Equivalents',
  confidence_score: 0.95,
  confidence_level: 'very_high' as const,
  status: 'suggested' as const,
  created_at: '2024-01-01T00:00:00Z',
}

export const mockQCResult = {
  id: 'qc-1',
  policy_id: 'policy-1',
  policy_name: 'Trial Balance Validation',
  status: 'passed' as const,
  message: 'Trial balance is in balance',
  timestamp: '2024-01-15T00:00:00Z',
}

// Utility function to wait for async operations
export const waitFor = (callback: () => void, options?: { timeout?: number }) => {
  return new Promise((resolve) => {
    const timeout = options?.timeout || 1000
    setTimeout(() => {
      callback()
      resolve(true)
    }, timeout)
  })
}

// Mock API responses
export const mockApiSuccess = (data: any) => ({
  data,
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
})

export const mockApiError = (message: string, status: number = 400) => ({
  response: {
    data: { message },
    status,
    statusText: 'Error',
    headers: {},
    config: {},
  },
})
