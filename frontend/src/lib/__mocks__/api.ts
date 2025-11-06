// Mock API client for testing
export const api = {
  auth: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    me: jest.fn(),
  },
  engagements: {
    list: jest.fn(),
    get: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
  analytics: {
    jeTests: jest.fn(),
    anomalies: {
      detect: jest.fn(),
      list: jest.fn(),
      get: jest.fn(),
    },
    ratios: jest.fn(),
  },
  normalize: {
    mappings: {
      list: jest.fn(),
      generate: jest.fn(),
      update: jest.fn(),
      batch: jest.fn(),
    },
  },
  qc: {
    policies: {
      list: jest.fn(),
      get: jest.fn(),
    },
    results: {
      list: jest.fn(),
      get: jest.fn(),
    },
    execute: jest.fn(),
  },
}

export default api
