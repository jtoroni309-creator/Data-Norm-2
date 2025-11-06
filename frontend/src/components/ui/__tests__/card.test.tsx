import React from 'react'
import { render, screen } from '@/lib/__tests__/test-utils'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../card'

describe('Card Components', () => {
  describe('Card', () => {
    it('should render card component', () => {
      const { container } = render(<Card>Card content</Card>)
      expect(container.firstChild).toBeInTheDocument()
      expect(container.firstChild).toHaveClass('rounded-lg', 'border')
    })

    it('should render children', () => {
      render(<Card>Test content</Card>)
      expect(screen.getByText('Test content')).toBeInTheDocument()
    })

    it('should accept custom className', () => {
      const { container } = render(<Card className="custom-card">Content</Card>)
      expect(container.firstChild).toHaveClass('custom-card')
    })
  })

  describe('CardHeader', () => {
    it('should render card header', () => {
      const { container } = render(<CardHeader>Header</CardHeader>)
      expect(container.firstChild).toBeInTheDocument()
      expect(container.firstChild).toHaveClass('flex', 'flex-col', 'space-y-1.5')
    })

    it('should render children', () => {
      render(<CardHeader>Header content</CardHeader>)
      expect(screen.getByText('Header content')).toBeInTheDocument()
    })
  })

  describe('CardTitle', () => {
    it('should render card title', () => {
      render(<CardTitle>Card Title</CardTitle>)
      expect(screen.getByText('Card Title')).toBeInTheDocument()
    })

    it('should have proper heading styles', () => {
      const { container } = render(<CardTitle>Title</CardTitle>)
      expect(container.firstChild).toHaveClass('text-2xl', 'font-semibold')
    })
  })

  describe('CardDescription', () => {
    it('should render card description', () => {
      render(<CardDescription>This is a description</CardDescription>)
      expect(screen.getByText('This is a description')).toBeInTheDocument()
    })

    it('should have muted text color', () => {
      const { container } = render(<CardDescription>Description</CardDescription>)
      expect(container.firstChild).toHaveClass('text-muted-foreground')
    })
  })

  describe('CardContent', () => {
    it('should render card content', () => {
      render(<CardContent>Main content</CardContent>)
      expect(screen.getByText('Main content')).toBeInTheDocument()
    })

    it('should have proper padding', () => {
      const { container } = render(<CardContent>Content</CardContent>)
      expect(container.firstChild).toHaveClass('p-6')
    })
  })

  describe('CardFooter', () => {
    it('should render card footer', () => {
      render(<CardFooter>Footer content</CardFooter>)
      expect(screen.getByText('Footer content')).toBeInTheDocument()
    })

    it('should have flex layout', () => {
      const { container } = render(<CardFooter>Footer</CardFooter>)
      expect(container.firstChild).toHaveClass('flex', 'items-center')
    })
  })

  describe('Full Card Composition', () => {
    it('should render complete card with all components', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Card</CardTitle>
            <CardDescription>Test description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Card content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Action</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByText('Test Card')).toBeInTheDocument()
      expect(screen.getByText('Test description')).toBeInTheDocument()
      expect(screen.getByText('Card content goes here')).toBeInTheDocument()
      expect(screen.getByText('Action')).toBeInTheDocument()
    })

    it('should maintain proper structure', () => {
      const { container } = render(
        <Card data-testid="card">
          <CardHeader data-testid="header">
            <CardTitle>Title</CardTitle>
          </CardHeader>
          <CardContent data-testid="content">Content</CardContent>
        </Card>
      )

      const card = container.querySelector('[data-testid="card"]')
      const header = container.querySelector('[data-testid="header"]')
      const content = container.querySelector('[data-testid="content"]')

      expect(card).toContainElement(header)
      expect(card).toContainElement(content)
    })
  })
})
