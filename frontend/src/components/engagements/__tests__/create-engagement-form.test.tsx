import React from 'react'
import { render, screen, fireEvent, waitFor } from '@/lib/__tests__/test-utils'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CreateEngagementForm from '../create-engagement-form'

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    engagements: {
      create: jest.fn(),
    },
  },
}))

import { api } from '@/lib/api'

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('CreateEngagementForm', () => {
  const mockOnSuccess = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Form Rendering', () => {
    it('should render all form fields', () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      expect(screen.getByLabelText(/Client Name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Engagement Type/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Fiscal Year End/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Status/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Partner/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Manager/i)).toBeInTheDocument()
    })

    it('should render submit and cancel buttons', () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      expect(screen.getByText('Create Engagement')).toBeInTheDocument()
      expect(screen.getByText('Cancel')).toBeInTheDocument()
    })

    it('should show required indicators', () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const requiredMarkers = screen.getAllByText('*')
      expect(requiredMarkers.length).toBeGreaterThan(0)
    })
  })

  describe('Form Validation', () => {
    it('should show error when client name is empty', async () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Client name is required')).toBeInTheDocument()
      })
    })

    it('should show error when fiscal year end is empty', async () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const clientNameInput = screen.getByLabelText(/Client Name/i)
      fireEvent.change(clientNameInput, { target: { value: 'ABC Corp' } })

      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Fiscal year end is required')).toBeInTheDocument()
      })
    })

    it('should show error when partner is not selected', async () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const clientNameInput = screen.getByLabelText(/Client Name/i)
      fireEvent.change(clientNameInput, { target: { value: 'ABC Corp' } })

      const fyeInput = screen.getByLabelText(/Fiscal Year End/i)
      fireEvent.change(fyeInput, { target: { value: '2024-12-31' } })

      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Partner is required')).toBeInTheDocument()
      })
    })

    it('should clear error when user starts typing', async () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Client name is required')).toBeInTheDocument()
      })

      const clientNameInput = screen.getByLabelText(/Client Name/i)
      fireEvent.change(clientNameInput, { target: { value: 'ABC' } })

      await waitFor(() => {
        expect(screen.queryByText('Client name is required')).not.toBeInTheDocument()
      })
    })
  })

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      ;(api.engagements.create as jest.Mock).mockResolvedValue({
        id: '1',
        client_name: 'ABC Corp',
      })

      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      // Fill in form
      const clientNameInput = screen.getByLabelText(/Client Name/i)
      fireEvent.change(clientNameInput, { target: { value: 'ABC Corp' } })

      const fyeInput = screen.getByLabelText(/Fiscal Year End/i)
      fireEvent.change(fyeInput, { target: { value: '2024-12-31' } })

      const partnerSelect = screen.getByLabelText(/Partner/i)
      fireEvent.change(partnerSelect, { target: { value: '1' } })

      // Submit form
      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(api.engagements.create).toHaveBeenCalledWith(
          expect.objectContaining({
            client_name: 'ABC Corp',
            fiscal_year_end: '2024-12-31',
            partner_id: '1',
          })
        )
      })
    })

    it('should call onSuccess after successful submission', async () => {
      ;(api.engagements.create as jest.Mock).mockResolvedValue({
        id: '1',
        client_name: 'ABC Corp',
      })

      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      // Fill in required fields
      const clientNameInput = screen.getByLabelText(/Client Name/i)
      fireEvent.change(clientNameInput, { target: { value: 'ABC Corp' } })

      const fyeInput = screen.getByLabelText(/Fiscal Year End/i)
      fireEvent.change(fyeInput, { target: { value: '2024-12-31' } })

      const partnerSelect = screen.getByLabelText(/Partner/i)
      fireEvent.change(partnerSelect, { target: { value: '1' } })

      // Submit form
      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalled()
      })
    })

    it('should not submit form with invalid data', async () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(api.engagements.create).not.toHaveBeenCalled()
        expect(mockOnSuccess).not.toHaveBeenCalled()
      })
    })
  })

  describe('Engagement Type Selection', () => {
    it('should allow selecting different engagement types', () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const typeSelect = screen.getByLabelText(/Engagement Type/i)

      fireEvent.change(typeSelect, { target: { value: 'audit' } })
      expect((typeSelect as HTMLSelectElement).value).toBe('audit')

      fireEvent.change(typeSelect, { target: { value: 'review' } })
      expect((typeSelect as HTMLSelectElement).value).toBe('review')

      fireEvent.change(typeSelect, { target: { value: 'compilation' } })
      expect((typeSelect as HTMLSelectElement).value).toBe('compilation')

      fireEvent.change(typeSelect, { target: { value: 'tax' } })
      expect((typeSelect as HTMLSelectElement).value).toBe('tax')
    })
  })

  describe('Cancel Action', () => {
    it('should call onSuccess when cancel button is clicked', () => {
      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      const cancelButton = screen.getByText('Cancel')
      fireEvent.click(cancelButton)

      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    it('should show loading state while submitting', async () => {
      ;(api.engagements.create as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      )

      render(<CreateEngagementForm onSuccess={mockOnSuccess} />, { wrapper: createWrapper() })

      // Fill in required fields
      const clientNameInput = screen.getByLabelText(/Client Name/i)
      fireEvent.change(clientNameInput, { target: { value: 'ABC Corp' } })

      const fyeInput = screen.getByLabelText(/Fiscal Year End/i)
      fireEvent.change(fyeInput, { target: { value: '2024-12-31' } })

      const partnerSelect = screen.getByLabelText(/Partner/i)
      fireEvent.change(partnerSelect, { target: { value: '1' } })

      // Submit form
      const submitButton = screen.getByText('Create Engagement')
      fireEvent.click(submitButton)

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText('Loading...')).toBeInTheDocument()
      })
    })
  })
})
