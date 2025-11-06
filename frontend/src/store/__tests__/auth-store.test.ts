import { renderHook, act } from '@testing-library/react'
import { useAuthStore } from '../auth-store'
import { mockUser } from '@/lib/__tests__/test-utils'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('Auth Store', () => {
  beforeEach(() => {
    localStorage.clear()
    // Reset store state
    const { result } = renderHook(() => useAuthStore())
    act(() => {
      result.current.logout()
    })
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore())

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('setUser', () => {
    it('should set user and update isAuthenticated', () => {
      const { result } = renderHook(() => useAuthStore())

      act(() => {
        result.current.setUser(mockUser)
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('should clear user when set to null', () => {
      const { result } = renderHook(() => useAuthStore())

      act(() => {
        result.current.setUser(mockUser)
      })

      expect(result.current.isAuthenticated).toBe(true)

      act(() => {
        result.current.setUser(null)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('setToken', () => {
    it('should set token and store in localStorage', () => {
      const { result } = renderHook(() => useAuthStore())
      const testToken = 'test-token-123'

      act(() => {
        result.current.setToken(testToken)
      })

      expect(result.current.token).toBe(testToken)
      expect(localStorage.getItem('auth_token')).toBe(testToken)
    })

    it('should remove token from localStorage when set to null', () => {
      const { result } = renderHook(() => useAuthStore())

      act(() => {
        result.current.setToken('test-token')
      })

      expect(localStorage.getItem('auth_token')).toBe('test-token')

      act(() => {
        result.current.setToken(null)
      })

      expect(result.current.token).toBeNull()
      expect(localStorage.getItem('auth_token')).toBeNull()
    })
  })

  describe('login', () => {
    it('should set user, token, and authentication state', () => {
      const { result } = renderHook(() => useAuthStore())
      const testToken = 'test-token-123'

      act(() => {
        result.current.login(mockUser, testToken)
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.token).toBe(testToken)
      expect(result.current.isAuthenticated).toBe(true)
      expect(localStorage.getItem('auth_token')).toBe(testToken)
    })
  })

  describe('logout', () => {
    it('should clear user, token, and authentication state', () => {
      const { result } = renderHook(() => useAuthStore())

      // First login
      act(() => {
        result.current.login(mockUser, 'test-token')
      })

      expect(result.current.isAuthenticated).toBe(true)

      // Then logout
      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorage.getItem('auth_token')).toBeNull()
    })
  })

  describe('setLoading', () => {
    it('should set loading state', () => {
      const { result } = renderHook(() => useAuthStore())

      expect(result.current.isLoading).toBe(false)

      act(() => {
        result.current.setLoading(true)
      })

      expect(result.current.isLoading).toBe(true)

      act(() => {
        result.current.setLoading(false)
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Persistence', () => {
    it('should persist state to localStorage', () => {
      const { result } = renderHook(() => useAuthStore())

      act(() => {
        result.current.login(mockUser, 'test-token')
      })

      // Check that state was persisted
      const persistedState = localStorage.getItem('auth-storage')
      expect(persistedState).toBeTruthy()

      if (persistedState) {
        const parsed = JSON.parse(persistedState)
        expect(parsed.state.user).toEqual(mockUser)
        expect(parsed.state.token).toBe('test-token')
        expect(parsed.state.isAuthenticated).toBe(true)
      }
    })

    it('should restore state from localStorage', () => {
      // Set up persisted state
      const persistedState = {
        state: {
          user: mockUser,
          token: 'persisted-token',
          isAuthenticated: true,
        },
        version: 0,
      }
      localStorage.setItem('auth-storage', JSON.stringify(persistedState))

      // Create new hook instance
      const { result } = renderHook(() => useAuthStore())

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.token).toBe('persisted-token')
      expect(result.current.isAuthenticated).toBe(true)
    })
  })

  describe('Multiple Store Instances', () => {
    it('should share state across multiple hook instances', () => {
      const { result: result1 } = renderHook(() => useAuthStore())
      const { result: result2 } = renderHook(() => useAuthStore())

      act(() => {
        result1.current.login(mockUser, 'test-token')
      })

      // Both instances should have the same state
      expect(result1.current.isAuthenticated).toBe(true)
      expect(result2.current.isAuthenticated).toBe(true)
      expect(result2.current.user).toEqual(mockUser)
      expect(result2.current.token).toBe('test-token')
    })
  })
})
