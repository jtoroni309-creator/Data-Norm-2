/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_IDENTITY_URL: string
  readonly VITE_RD_STUDY_URL: string
  readonly VITE_PORTAL_NAME: string
  readonly VITE_SUPPORT_EMAIL: string
  readonly VITE_SUPPORT_PHONE: string
  readonly VITE_ENABLE_AI_ASSISTANCE: string
  readonly VITE_ENABLE_TEAM_INVITATIONS: string
  readonly VITE_ENABLE_TAX_RETURN_UPLOAD: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
