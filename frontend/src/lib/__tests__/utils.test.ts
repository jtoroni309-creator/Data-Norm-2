import {
  cn,
  formatCurrency,
  formatDate,
  formatNumber,
  formatPercentage,
  truncate,
  getInitials,
  generateId,
  deepClone,
  groupBy,
  sortBy,
  unique,
  chunk,
  debounce,
  sleep,
} from '../utils'

describe('Utility Functions', () => {
  describe('cn (classname merger)', () => {
    it('should merge class names', () => {
      const result = cn('class1', 'class2')
      expect(result).toContain('class1')
      expect(result).toContain('class2')
    })

    it('should handle conditional classes', () => {
      const result = cn('base', true && 'active', false && 'inactive')
      expect(result).toContain('base')
      expect(result).toContain('active')
      expect(result).not.toContain('inactive')
    })

    it('should handle undefined and null', () => {
      const result = cn('class1', undefined, null, 'class2')
      expect(result).toContain('class1')
      expect(result).toContain('class2')
    })
  })

  describe('formatCurrency', () => {
    it('should format number as USD currency', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56')
    })

    it('should handle zero', () => {
      expect(formatCurrency(0)).toBe('$0.00')
    })

    it('should handle negative numbers', () => {
      expect(formatCurrency(-1234.56)).toBe('-$1,234.56')
    })

    it('should support different currencies', () => {
      const result = formatCurrency(1000, 'EUR')
      expect(result).toContain('1,000')
    })

    it('should handle large numbers', () => {
      expect(formatCurrency(1000000)).toBe('$1,000,000.00')
    })
  })

  describe('formatNumber', () => {
    it('should format number with default decimals', () => {
      expect(formatNumber(1234.5678)).toBe('1,234.57')
    })

    it('should format with specified decimals', () => {
      expect(formatNumber(1234.5678, 3)).toBe('1,234.568')
    })

    it('should format with no decimals', () => {
      expect(formatNumber(1234.5678, 0)).toBe('1,235')
    })

    it('should handle zero', () => {
      expect(formatNumber(0)).toBe('0.00')
    })
  })

  describe('formatPercentage', () => {
    it('should format decimal as percentage', () => {
      expect(formatPercentage(0.1234)).toBe('12.34%')
    })

    it('should format with specified decimals', () => {
      expect(formatPercentage(0.1234, 1)).toBe('12.3%')
    })

    it('should handle zero', () => {
      expect(formatPercentage(0)).toBe('0.00%')
    })

    it('should handle values over 1', () => {
      expect(formatPercentage(1.5)).toBe('150.00%')
    })
  })

  describe('formatDate', () => {
    const testDate = new Date('2024-01-15T12:00:00Z')

    it('should format date in short format', () => {
      const result = formatDate(testDate, 'short')
      expect(result).toContain('2024')
    })

    it('should format date in long format', () => {
      const result = formatDate(testDate, 'long')
      expect(result).toContain('2024')
    })

    it('should handle string dates', () => {
      const result = formatDate('2024-01-15', 'short')
      expect(result).toContain('2024')
    })
  })

  describe('truncate', () => {
    it('should truncate long strings', () => {
      expect(truncate('This is a long string', 10)).toBe('This is a...')
    })

    it('should not truncate short strings', () => {
      expect(truncate('Short', 10)).toBe('Short')
    })

    it('should handle empty strings', () => {
      expect(truncate('', 10)).toBe('')
    })
  })

  describe('getInitials', () => {
    it('should get initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD')
    })

    it('should handle single name', () => {
      expect(getInitials('John')).toBe('J')
    })

    it('should handle three names', () => {
      expect(getInitials('John Michael Doe')).toBe('JD')
    })

    it('should handle empty string', () => {
      expect(getInitials('')).toBe('')
    })

    it('should convert to uppercase', () => {
      expect(getInitials('john doe')).toBe('JD')
    })
  })

  describe('generateId', () => {
    it('should generate a string', () => {
      const id = generateId()
      expect(typeof id).toBe('string')
    })

    it('should generate unique IDs', () => {
      const id1 = generateId()
      const id2 = generateId()
      expect(id1).not.toBe(id2)
    })

    it('should generate non-empty string', () => {
      const id = generateId()
      expect(id.length).toBeGreaterThan(0)
    })
  })

  describe('deepClone', () => {
    it('should clone simple objects', () => {
      const obj = { a: 1, b: 2 }
      const cloned = deepClone(obj)
      expect(cloned).toEqual(obj)
      expect(cloned).not.toBe(obj)
    })

    it('should clone nested objects', () => {
      const obj = { a: { b: { c: 1 } } }
      const cloned = deepClone(obj)
      expect(cloned).toEqual(obj)
      expect(cloned.a).not.toBe(obj.a)
    })

    it('should clone arrays', () => {
      const arr = [1, 2, 3]
      const cloned = deepClone(arr)
      expect(cloned).toEqual(arr)
      expect(cloned).not.toBe(arr)
    })
  })

  describe('groupBy', () => {
    it('should group array by key', () => {
      const items = [
        { type: 'a', value: 1 },
        { type: 'b', value: 2 },
        { type: 'a', value: 3 },
      ]
      const grouped = groupBy(items, 'type')
      expect(grouped.a).toHaveLength(2)
      expect(grouped.b).toHaveLength(1)
    })

    it('should handle empty arrays', () => {
      const grouped = groupBy([], 'type')
      expect(grouped).toEqual({})
    })
  })

  describe('sortBy', () => {
    it('should sort array by key ascending', () => {
      const items = [{ value: 3 }, { value: 1 }, { value: 2 }]
      const sorted = sortBy(items, 'value')
      expect(sorted[0].value).toBe(1)
      expect(sorted[2].value).toBe(3)
    })

    it('should sort array by multiple keys', () => {
      const items = [{ a: 1, b: 3 }, { a: 2, b: 1 }, { a: 1, b: 2 }]
      const sorted = sortBy(items, 'a', 'b')
      expect(sorted[0]).toEqual({ a: 1, b: 2 })
      expect(sorted[1]).toEqual({ a: 1, b: 3 })
      expect(sorted[2]).toEqual({ a: 2, b: 1 })
    })
  })

  describe('unique', () => {
    it('should remove duplicates from array', () => {
      const result = unique([1, 2, 2, 3, 3, 3, 4])
      expect(result).toEqual([1, 2, 3, 4])
    })

    it('should handle empty arrays', () => {
      expect(unique([])).toEqual([])
    })

    it('should work with strings', () => {
      const result = unique(['a', 'b', 'a', 'c', 'b'])
      expect(result).toEqual(['a', 'b', 'c'])
    })
  })

  describe('chunk', () => {
    it('should split array into chunks', () => {
      const result = chunk([1, 2, 3, 4, 5], 2)
      expect(result).toEqual([[1, 2], [3, 4], [5]])
    })

    it('should handle exact divisions', () => {
      const result = chunk([1, 2, 3, 4], 2)
      expect(result).toEqual([[1, 2], [3, 4]])
    })

    it('should handle empty arrays', () => {
      expect(chunk([], 2)).toEqual([])
    })
  })

  describe('debounce', () => {
    jest.useFakeTimers()

    it('should debounce function calls', () => {
      const fn = jest.fn()
      const debounced = debounce(fn, 100)

      debounced()
      debounced()
      debounced()

      expect(fn).not.toHaveBeenCalled()

      jest.advanceTimersByTime(100)

      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should pass arguments to debounced function', () => {
      const fn = jest.fn()
      const debounced = debounce(fn, 100)

      debounced('arg1', 'arg2')

      jest.advanceTimersByTime(100)

      expect(fn).toHaveBeenCalledWith('arg1', 'arg2')
    })

    jest.useRealTimers()
  })

  describe('sleep', () => {
    it('should resolve after specified time', async () => {
      const start = Date.now()
      await sleep(100)
      const elapsed = Date.now() - start
      expect(elapsed).toBeGreaterThanOrEqual(90) // Allow some margin
    })
  })
})
