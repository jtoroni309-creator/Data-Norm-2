import React from 'react'
import { render, screen, fireEvent } from '@/lib/__tests__/test-utils'
import { Input } from '../input'

describe('Input', () => {
  describe('Rendering', () => {
    it('should render input element', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('should render with placeholder', () => {
      render(<Input placeholder="Enter text..." />)
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument()
    })

    it('should render with default value', () => {
      render(<Input defaultValue="Default text" />)
      const input = screen.getByRole('textbox') as HTMLInputElement
      expect(input.value).toBe('Default text')
    })
  })

  describe('Label', () => {
    it('should render label when provided', () => {
      render(<Input label="Username" />)
      expect(screen.getByText('Username')).toBeInTheDocument()
    })

    it('should show required indicator when required', () => {
      render(<Input label="Email" required />)
      expect(screen.getByText('*')).toBeInTheDocument()
      expect(screen.getByText('*')).toHaveClass('text-destructive')
    })

    it('should not show required indicator when not required', () => {
      render(<Input label="Optional Field" />)
      expect(screen.queryByText('*')).not.toBeInTheDocument()
    })
  })

  describe('Error State', () => {
    it('should render error message when error prop is provided', () => {
      render(<Input error="This field is required" />)
      expect(screen.getByText('This field is required')).toBeInTheDocument()
    })

    it('should apply error styles when error exists', () => {
      render(<Input error="Error message" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('border-destructive')
    })

    it('should display error message in destructive color', () => {
      render(<Input error="Invalid input" />)
      const errorMessage = screen.getByText('Invalid input')
      expect(errorMessage).toHaveClass('text-destructive')
    })
  })

  describe('Types', () => {
    it('should render as text input by default', () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'text')
    })

    it('should render as email input', () => {
      render(<Input type="email" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'email')
    })

    it('should render as password input', () => {
      render(<Input type="password" />)
      const input = document.querySelector('input[type="password"]')
      expect(input).toBeInTheDocument()
    })

    it('should render as number input', () => {
      render(<Input type="number" />)
      const input = screen.getByRole('spinbutton')
      expect(input).toHaveAttribute('type', 'number')
    })
  })

  describe('Interactions', () => {
    it('should call onChange when value changes', () => {
      const handleChange = jest.fn()
      render(<Input onChange={handleChange} />)
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      expect(handleChange).toHaveBeenCalledTimes(1)
    })

    it('should update value on change', () => {
      render(<Input />)
      const input = screen.getByRole('textbox') as HTMLInputElement
      fireEvent.change(input, { target: { value: 'new value' } })
      expect(input.value).toBe('new value')
    })

    it('should call onBlur when focus is lost', () => {
      const handleBlur = jest.fn()
      render(<Input onBlur={handleBlur} />)
      const input = screen.getByRole('textbox')
      fireEvent.blur(input)
      expect(handleBlur).toHaveBeenCalledTimes(1)
    })

    it('should call onFocus when focused', () => {
      const handleFocus = jest.fn()
      render(<Input onFocus={handleFocus} />)
      const input = screen.getByRole('textbox')
      fireEvent.focus(input)
      expect(handleFocus).toHaveBeenCalledTimes(1)
    })
  })

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Input disabled />)
      expect(screen.getByRole('textbox')).toBeDisabled()
    })

    it('should not trigger onChange when disabled', () => {
      const handleChange = jest.fn()
      render(<Input disabled onChange={handleChange} />)
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      expect(handleChange).not.toHaveBeenCalled()
    })

    it('should have disabled cursor class', () => {
      render(<Input disabled />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('disabled:cursor-not-allowed')
    })
  })

  describe('Custom className', () => {
    it('should accept and apply custom className', () => {
      render(<Input className="custom-input" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('custom-input')
    })

    it('should merge custom className with default classes', () => {
      render(<Input className="custom-input" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('custom-input', 'rounded-md', 'border')
    })
  })

  describe('Accessibility', () => {
    it('should be keyboard accessible', () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      input.focus()
      expect(input).toHaveFocus()
    })

    it('should support aria-label', () => {
      render(<Input aria-label="Search field" />)
      expect(screen.getByLabelText('Search field')).toBeInTheDocument()
    })

    it('should associate label with input', () => {
      render(<Input label="Email Address" />)
      const label = screen.getByText('Email Address')
      const input = screen.getByRole('textbox')
      expect(label).toBeInTheDocument()
      expect(input).toBeInTheDocument()
    })
  })

  describe('Combined States', () => {
    it('should render with label and error', () => {
      render(<Input label="Password" error="Password is too short" />)
      expect(screen.getByText('Password')).toBeInTheDocument()
      expect(screen.getByText('Password is too short')).toBeInTheDocument()
    })

    it('should render with label, required, and error', () => {
      render(<Input label="Email" required error="Email is invalid" />)
      expect(screen.getByText('Email')).toBeInTheDocument()
      expect(screen.getByText('*')).toBeInTheDocument()
      expect(screen.getByText('Email is invalid')).toBeInTheDocument()
    })
  })
})
