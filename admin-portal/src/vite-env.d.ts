/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_IDENTITY_API_URL: string;
  readonly VITE_ENGAGEMENT_API_URL: string;
  readonly VITE_REPORTING_API_URL: string;
  readonly VITE_ANALYTICS_API_URL: string;
  readonly VITE_AZURE_CLIENT_ID: string;
  readonly VITE_AZURE_TENANT_ID: string;
  readonly VITE_APP_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
