import React from 'react'
import { render, screen } from '@/lib/__tests__/test-utils'
import { Badge } from '../badge'

describe('Badge', () => {
  describe('Rendering', () => {
    it('should render badge with text', () => {
      render(<Badge>New</Badge>)
      expect(screen.getByText('New')).toBeInTheDocument()
    })

    it('should render children content', () => {
      render(<Badge>Badge Content</Badge>)
      expect(screen.getByText('Badge Content')).toBeInTheDocument()
    })
  })

  describe('Variants', () => {
    it('should render default variant', () => {
      const { container } = render(<Badge variant="default">Default</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('bg-primary')
    })

    it('should render secondary variant', () => {
      const { container } = render(<Badge variant="secondary">Secondary</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('bg-secondary')
    })

    it('should render destructive variant', () => {
      const { container } = render(<Badge variant="destructive">Error</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('bg-destructive')
    })

    it('should render outline variant', () => {
      const { container } = render(<Badge variant="outline">Outline</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('border')
    })

    it('should render success variant', () => {
      const { container } = render(<Badge variant="success">Success</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('bg-success')
    })

    it('should render warning variant', () => {
      const { container } = render(<Badge variant="warning">Warning</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('bg-warning')
    })

    it('should render info variant', () => {
      const { container } = render(<Badge variant="info">Info</Badge>)
      const badge = container.firstChild
      expect(badge).toHaveClass('bg-info')
    })
  })

  describe('Custom className', () => {
    it('should accept custom className', () => {
      const { container } = render(<Badge className="custom-badge">Custom</Badge>)
      expect(container.firstChild).toHaveClass('custom-badge')
    })

    it('should merge custom className with variant classes', () => {
      const { container } = render(
        <Badge variant="success" className="custom-badge">Success</Badge>
      )
      const badge = container.firstChild
      expect(badge).toHaveClass('custom-badge', 'bg-success')
    })
  })

  describe('With Icons', () => {
    it('should render badge with icon', () => {
      render(
        <Badge>
          <span data-testid="icon">✓</span>
          Success
        </Badge>
      )
      expect(screen.getByTestId('icon')).toBeInTheDocument()
      expect(screen.getByText('Success')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should support aria attributes', () => {
      render(<Badge aria-label="Status badge">Active</Badge>)
      expect(screen.getByLabelText('Status badge')).toBeInTheDocument()
    })
  })
})
