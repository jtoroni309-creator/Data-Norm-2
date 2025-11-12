# Microsoft 365 OAuth Setup - Aura Audit AI

This document describes the Microsoft 365 OAuth configuration for the Aura Audit AI platform.

## Azure AD App Registration

**App Name**: Aura Audit AI - OAuth
**Application (client) ID**: `bd4c65f8-e6b1-4980-b47b-47b0ba9f8904`
**Directory (tenant) ID**: `002fa7de-1afd-4945-86e1-79281af841ad`
**Tenant Domain**: `toronico.onmicrosoft.com`

## OAuth Endpoints

### Authorization Endpoint
```
https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/oauth2/v2.0/authorize
```

### Token Endpoint
```
https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/oauth2/v2.0/token
```

### OpenID Connect Discovery
```
https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/v2.0/.well-known/openid-configuration
```

## Redirect URIs (Configured)

### Production
- `https://admin.auraai.toroniandcompany.com/auth/callback`
- `https://portal.auraai.toroniandcompany.com/auth/callback`
- `https://cpa.auraai.toroniandcompany.com/auth/callback`
- `https://admin.auraa.toroniandcompany.com/auth/callback`
- `https://cpa.auraa.toroniandcompany.com/auth/callback`

### Development
- `http://localhost:3001/auth/callback` (Admin Portal)
- `http://localhost:3002/auth/callback` (Client Portal)

## API Permissions (Microsoft Graph)

The following delegated permissions have been granted with admin consent:

| Permission | Type | Description |
|------------|------|-------------|
| `User.Read` | Delegated | Sign in and read user profile |
| `openid` | Delegated | Sign users in |
| `email` | Delegated | View users' email address |
| `profile` | Delegated | View users' basic profile |

## Credentials Storage

All OAuth credentials are securely stored in Azure Key Vault:

| Secret Name | Description |
|-------------|-------------|
| `oauth-client-id` | Application (client) ID |
| `oauth-client-secret` | Client secret (expires in 2 years) |
| `oauth-tenant-id` | Directory (tenant) ID |

**Key Vault**: `aura-audit-ai-prod-kv2`
**Location**: West US 2

## Environment Variables

The following environment variables should be configured for services using OAuth:

```bash
# OAuth/OIDC Configuration
OIDC_ENABLED=true
OIDC_ISSUER=https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/v2.0
OIDC_CLIENT_ID=bd4c65f8-e6b1-4980-b47b-47b0ba9f8904
OIDC_CLIENT_SECRET=<from-keyvault>
OIDC_AUDIENCE=api://bd4c65f8-e6b1-4980-b47b-47b0ba9f8904

# Alternative format for some libraries
AZURE_AD_TENANT_ID=002fa7de-1afd-4945-86e1-79281af841ad
AZURE_AD_CLIENT_ID=bd4c65f8-e6b1-4980-b47b-47b0ba9f8904
AZURE_AD_CLIENT_SECRET=<from-keyvault>
```

## Kubernetes Integration

OAuth credentials are automatically mounted into pods via the Azure Key Vault CSI driver:

1. **SecretProviderClass** (`infra/k8s/base/secretproviderclass.yaml`) defines which secrets to pull from Key Vault
2. Secrets are mounted as Kubernetes Secret: `aura-secrets`
3. Services can reference these secrets as environment variables

Example pod configuration:

```yaml
env:
  - name: OIDC_CLIENT_ID
    valueFrom:
      secretKeyRef:
        name: aura-secrets
        key: oauth-client-id
  - name: OIDC_CLIENT_SECRET
    valueFrom:
      secretKeyRef:
        name: aura-secrets
        key: oauth-client-secret
  - name: OIDC_TENANT_ID
    valueFrom:
      secretKeyRef:
        name: aura-secrets
        key: oauth-tenant-id
```

## Implementation Example (Identity Service)

The identity service supports both OAuth and local JWT authentication:

```python
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
import httpx

app = FastAPI()

# OAuth2 scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize",
    tokenUrl=f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
)

async def verify_microsoft_token(token: str):
    """Verify Microsoft OAuth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/auth/user")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_microsoft_token(token)
    return user
```

## Frontend Integration (React)

Example using MSAL (Microsoft Authentication Library):

```typescript
import { PublicClientApplication } from "@azure/msal-browser";

const msalConfig = {
  auth: {
    clientId: "bd4c65f8-e6b1-4980-b47b-47b0ba9f8904",
    authority: "https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad",
    redirectUri: window.location.origin + "/auth/callback",
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

// Login
const loginRequest = {
  scopes: ["User.Read", "openid", "profile", "email"],
};

await msalInstance.loginPopup(loginRequest);

// Get token
const tokenRequest = {
  scopes: ["User.Read"],
  account: msalInstance.getAllAccounts()[0],
};

const response = await msalInstance.acquireTokenSilent(tokenRequest);
const accessToken = response.accessToken;
```

## Testing OAuth Flow

### 1. Test Authorization Flow
Navigate to:
```
https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/oauth2/v2.0/authorize?
  client_id=bd4c65f8-e6b1-4980-b47b-47b0ba9f8904
  &response_type=code
  &redirect_uri=https://portal.auraai.toroniandcompany.com/auth/callback
  &scope=openid%20profile%20email%20User.Read
  &state=12345
```

### 2. Exchange Code for Token
```bash
curl -X POST https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/oauth2/v2.0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=bd4c65f8-e6b1-4980-b47b-47b0ba9f8904" \
  -d "client_secret=<secret>" \
  -d "code=<authorization_code>" \
  -d "redirect_uri=https://portal.auraai.toroniandcompany.com/auth/callback" \
  -d "grant_type=authorization_code"
```

### 3. Verify Token with Microsoft Graph
```bash
curl -X GET https://graph.microsoft.com/v1.0/me \
  -H "Authorization: Bearer <access_token>"
```

## Security Considerations

1. **Client Secret Rotation**: The client secret expires in 2 years (2027). Set a calendar reminder to rotate it before expiration.

2. **PKCE Flow**: For SPAs (Single Page Applications), use PKCE (Proof Key for Code Exchange) flow instead of client secret:
   ```typescript
   const loginRequest = {
     scopes: ["User.Read"],
     prompt: "select_account",
   };
   ```

3. **Token Validation**: Always validate tokens server-side using Microsoft's public keys from:
   ```
   https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad/discovery/v2.0/keys
   ```

4. **Scope Limitation**: Only request the minimum scopes needed. Current scopes are:
   - `openid` - Basic authentication
   - `profile` - User's name and picture
   - `email` - User's email address
   - `User.Read` - Read user profile

5. **Network Security**: Key Vault has public network access disabled and only allows access from the AKS subnet.

## Troubleshooting

### Issue: "AADSTS50011: The reply URL specified in the request does not match"
**Solution**: Ensure the redirect URI in your app exactly matches one of the configured URIs (including protocol and path).

### Issue: "AADSTS65001: The user or administrator has not consented"
**Solution**: Admin consent has already been granted. Clear browser cache or try incognito mode.

### Issue: "Invalid client secret"
**Solution**: Verify the client secret in Key Vault hasn't expired. Generate a new one if needed:
```bash
az ad app credential reset --id bd4c65f8-e6b1-4980-b47b-47b0ba9f8904 --append
```

### Issue: Token validation fails
**Solution**: Check that:
1. Token is not expired
2. Audience (`aud`) claim matches your application ID
3. Issuer (`iss`) claim matches your tenant
4. Token signature is valid using Microsoft's public keys

## Monitoring

Monitor OAuth authentication in Azure Portal:
1. Go to **Azure Active Directory** > **Enterprise applications**
2. Find "Aura Audit AI - OAuth"
3. View **Sign-in logs** for authentication attempts
4. Check **Audit logs** for configuration changes

## Additional Resources

- [Microsoft identity platform documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [MSAL.js documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [Microsoft Graph API reference](https://docs.microsoft.com/en-us/graph/api/overview)
- [OAuth 2.0 and OpenID Connect protocols](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-protocols)
