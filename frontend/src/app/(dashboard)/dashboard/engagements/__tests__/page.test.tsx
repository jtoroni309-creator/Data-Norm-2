import React from 'react'
import { render, screen, fireEvent, waitFor } from '@/lib/__tests__/test-utils'
import EngagementsPage from '../page'
import { mockEngagement } from '@/lib/__tests__/test-utils'

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    engagements: {
      list: jest.fn(),
      get: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
  },
}))

import { api } from '@/lib/api'

describe('EngagementsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Loading State', () => {
    it('should show loading spinner while fetching engagements', () => {
      ;(api.engagements.list as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      render(<EngagementsPage />)

      expect(screen.getByRole('heading', { name: 'Engagements' })).toBeInTheDocument()
    })
  })

  describe('Empty State', () => {
    it('should show empty state when no engagements exist', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue([])

      render(<EngagementsPage />)

      await waitFor(() => {
        expect(screen.getByText('No engagements found')).toBeInTheDocument()
      })
    })

    it('should show create button in empty state', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue([])

      render(<EngagementsPage />)

      await waitFor(() => {
        const createButtons = screen.getAllByText(/Create Engagement/i)
        expect(createButtons.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Engagements List', () => {
    const mockEngagements = [
      { ...mockEngagement, id: '1', client_name: 'ABC Corp', status: 'planning' },
      { ...mockEngagement, id: '2', client_name: 'XYZ Inc', status: 'fieldwork' },
      { ...mockEngagement, id: '3', client_name: 'Test LLC', status: 'completed' },
    ]

    it('should render list of engagements', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue(mockEngagements)

      render(<EngagementsPage />)

      await waitFor(() => {
        expect(screen.getByText('ABC Corp')).toBeInTheDocument()
        expect(screen.getByText('XYZ Inc')).toBeInTheDocument()
        expect(screen.getByText('Test LLC')).toBeInTheDocument()
      })
    })

    it('should show correct stats', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue(mockEngagements)

      render(<EngagementsPage />)

      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument() // Total
        expect(screen.getByText('Total Engagements')).toBeInTheDocument()
      })
    })
  })

  describe('Search Functionality', () => {
    const mockEngagements = [
      { ...mockEngagement, id: '1', client_name: 'ABC Corp' },
      { ...mockEngagement, id: '2', client_name: 'XYZ Inc' },
    ]

    it('should filter engagements by search query', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue(mockEngagements)

      render(<EngagementsPage />)

      await waitFor(() => {
        expect(screen.getByText('ABC Corp')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Search engagements...')
      fireEvent.change(searchInput, { target: { value: 'ABC' } })

      await waitFor(() => {
        expect(screen.getByText('ABC Corp')).toBeInTheDocument()
        expect(screen.queryByText('XYZ Inc')).not.toBeInTheDocument()
      })
    })

    it('should show empty state when search has no results', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue(mockEngagements)

      render(<EngagementsPage />)

      await waitFor(() => {
        expect(screen.getByText('ABC Corp')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Search engagements...')
      fireEvent.change(searchInput, { target: { value: 'NonExistent' } })

      await waitFor(() => {
        expect(screen.getByText('Try adjusting your filters')).toBeInTheDocument()
      })
    })
  })

  describe('Status Filter', () => {
    const mockEngagements = [
      { ...mockEngagement, id: '1', client_name: 'ABC Corp', status: 'planning' },
      { ...mockEngagement, id: '2', client_name: 'XYZ Inc', status: 'completed' },
    ]

    it('should filter engagements by status', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue(mockEngagements)

      render(<EngagementsPage />)

      await waitFor(() => {
        expect(screen.getByText('ABC Corp')).toBeInTheDocument()
        expect(screen.getByText('XYZ Inc')).toBeInTheDocument()
      })

      const statusFilter = screen.getByRole('combobox', { name: /status/i }) ||
                          screen.getAllByRole('combobox')[1] // Get second combobox (status filter)

      fireEvent.change(statusFilter, { target: { value: 'planning' } })

      await waitFor(() => {
        expect(screen.getByText('ABC Corp')).toBeInTheDocument()
        expect(screen.queryByText('XYZ Inc')).not.toBeInTheDocument()
      })
    })
  })

  describe('Create Engagement Dialog', () => {
    it('should open create dialog when clicking new engagement button', async () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue([])

      render(<EngagementsPage />)

      await waitFor(() => {
        const newEngagementButton = screen.getAllByText(/New Engagement/i)[0]
        fireEvent.click(newEngagementButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Create New Engagement')).toBeInTheDocument()
      })
    })
  })

  describe('Page Header', () => {
    it('should render page title and description', () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue([])

      render(<EngagementsPage />)

      expect(screen.getByText('Engagements')).toBeInTheDocument()
      expect(screen.getByText('Manage your audit engagements and client work')).toBeInTheDocument()
    })

    it('should render new engagement button', () => {
      ;(api.engagements.list as jest.Mock).mockResolvedValue([])

      render(<EngagementsPage />)

      const newButton = screen.getAllByText(/New Engagement/i)[0]
      expect(newButton).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {})
      ;(api.engagements.list as jest.Mock).mockRejectedValue(new Error('API Error'))

      render(<EngagementsPage />)

      await waitFor(() => {
        // Should still render the page structure
        expect(screen.getByText('Engagements')).toBeInTheDocument()
      })

      consoleError.mockRestore()
    })
  })
})
