import { Configuration, PopupRequest } from "@azure/msal-browser";

// MSAL configuration - credentials should be set via environment variables
const AZURE_CLIENT_ID = import.meta.env.VITE_AZURE_CLIENT_ID || '';
const AZURE_TENANT_ID = import.meta.env.VITE_AZURE_TENANT_ID || '';

export const msalConfig: Configuration = {
  auth: {
    clientId: AZURE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${AZURE_TENANT_ID}`,
    redirectUri: window.location.origin + "/auth/callback",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

// Add scopes here for ID token to be used at Microsoft identity platform endpoints
export const loginRequest: PopupRequest = {
  scopes: ["User.Read", "openid", "profile", "email"],
};

// Add the endpoints here for Microsoft Graph API services you'd like to use
export const graphConfig = {
  graphMeEndpoint: "https://graph.microsoft.com/v1.0/me",
};
