/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_AUTH_DOMAIN: string
  readonly VITE_AUTH_CLIENT_ID: string
  readonly VITE_ENABLE_REG_AB_AUDIT: string
  readonly VITE_ENABLE_AI_ASSISTANT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
