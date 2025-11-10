# GitHub Secrets Configuration for Azure Deployment

This guide helps you set up GitHub Secrets for automated CI/CD deployment to Azure.

## 🎯 Overview

GitHub Actions uses secrets to securely store sensitive information like API keys, passwords, and credentials. This prevents them from being exposed in your repository code.

**Your Azure Application Registration:**
- Application (Client) ID: `6d1fdc5d-580b-499d-bae8-c129af50e96e`
- Directory (Tenant) ID: `002fa7de-1afd-4945-86e1-79281af841ad`

---

## 📋 Required Secrets

### How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the name and value
5. Click **Add secret**

---

## 🔐 Secrets to Add

### 1. AZURE_CREDENTIALS

This is the service principal credentials in JSON format for GitHub Actions to authenticate with Azure.

**Format:**
```json
{
  "clientId": "6d1fdc5d-580b-499d-bae8-c129af50e96e",
  "clientSecret": "YOUR_CLIENT_SECRET_HERE",
  "subscriptionId": "YOUR_AZURE_SUBSCRIPTION_ID",
  "tenantId": "002fa7de-1afd-4945-86e1-79281af841ad"
}
```

**How to get these values:**

- `clientId`: ✅ Already provided above
- `clientSecret`: ⚠️ You need to generate this in Azure Portal:
  1. Go to Azure Portal → Azure Active Directory
  2. Go to App registrations
  3. Find your app (ID: 6d1fdc5d-580b-499d-bae8-c129af50e96e)
  4. Click "Certificates & secrets"
  5. Click "New client secret"
  6. Copy the value immediately (you can't view it again!)
- `subscriptionId`: Run `az account show --query id -o tsv`
- `tenantId`: ✅ Already provided above

**Add to GitHub:**
- Secret Name: `AZURE_CREDENTIALS`
- Secret Value: The entire JSON object (with your actual values)

---

### 2. AZURE_CLIENT_ID

The Application (Client) ID for your Azure service principal.

**Value:**
```
6d1fdc5d-580b-499d-bae8-c129af50e96e
```

**Add to GitHub:**
- Secret Name: `AZURE_CLIENT_ID`
- Secret Value: `6d1fdc5d-580b-499d-bae8-c129af50e96e`

---

### 3. AZURE_CLIENT_SECRET

The secret/password for your Azure service principal.

**How to get:**
1. Azure Portal → Azure Active Directory → App registrations
2. Select your app (6d1fdc5d-580b-499d-bae8-c129af50e96e)
3. Certificates & secrets → New client secret
4. Copy the value

**Add to GitHub:**
- Secret Name: `AZURE_CLIENT_SECRET`
- Secret Value: Your client secret value

⚠️ **Important:** Save this immediately - you cannot view it again after creation!

---

### 4. AZURE_TENANT_ID

Your Azure Active Directory tenant ID.

**Value:**
```
002fa7de-1afd-4945-86e1-79281af841ad
```

**Add to GitHub:**
- Secret Name: `AZURE_TENANT_ID`
- Secret Value: `002fa7de-1afd-4945-86e1-79281af841ad`

---

### 5. AZURE_SUBSCRIPTION_ID

Your Azure subscription ID.

**How to get:**
```bash
az login
az account show --query id -o tsv
```

**Add to GitHub:**
- Secret Name: `AZURE_SUBSCRIPTION_ID`
- Secret Value: Your subscription ID

---

### 6. TF_BACKEND_STORAGE_ACCOUNT

The name of the Azure Storage Account used for Terraform state.

**How to get:**
- After running `azure-deployment-config.sh`, this will be in `terraform-backend-config.txt`
- Format: `auratfstate1234567890`

**Add to GitHub:**
- Secret Name: `TF_BACKEND_STORAGE_ACCOUNT`
- Secret Value: Your storage account name

---

### 7. TF_BACKEND_ACCESS_KEY

The access key for the Terraform backend storage account.

**How to get:**
- After running `azure-deployment-config.sh`, this will be in `terraform-backend-config.txt`
- Or run:
  ```bash
  az storage account keys list \
    --resource-group aura-tfstate-rg \
    --account-name YOUR_STORAGE_ACCOUNT \
    --query '[0].value' -o tsv
  ```

**Add to GitHub:**
- Secret Name: `TF_BACKEND_ACCESS_KEY`
- Secret Value: Your storage account access key

---

### 8. OPENAI_API_KEY

Your OpenAI API key for AI/ML features.

**How to get:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

**Add to GitHub:**
- Secret Name: `OPENAI_API_KEY`
- Secret Value: Your OpenAI API key (sk-...)

---

### 9. JWT_SECRET

Secret key for JWT token generation.

**How to get:**
- After running `azure-deployment-config.sh`, this will be in `azure-secrets.env`
- Or generate:
  ```bash
  openssl rand -hex 32
  ```

**Add to GitHub:**
- Secret Name: `JWT_SECRET`
- Secret Value: Your generated JWT secret

---

### 10. ENCRYPTION_KEY

Encryption key for sensitive data.

**How to get:**
- After running `azure-deployment-config.sh`, this will be in `azure-secrets.env`
- Or generate:
  ```bash
  openssl rand -hex 32
  ```

**Add to GitHub:**
- Secret Name: `ENCRYPTION_KEY`
- Secret Value: Your generated encryption key

---

### 11. MASTER_KEY

Master encryption key.

**How to get:**
- After running `azure-deployment-config.sh`, this will be in `azure-secrets.env`
- Or generate:
  ```bash
  openssl rand -hex 32
  ```

**Add to GitHub:**
- Secret Name: `MASTER_KEY`
- Secret Value: Your generated master key

---

### 12. POSTGRES_PASSWORD

PostgreSQL database password.

**How to get:**
- After running `azure-deployment-config.sh`, this will be in `azure-secrets.env`
- Or generate:
  ```bash
  openssl rand -base64 24 | tr -d "=+/" | cut -c1-20
  ```

**Add to GitHub:**
- Secret Name: `POSTGRES_PASSWORD`
- Secret Value: Your generated PostgreSQL password

---

## 📝 Quick Copy Template

After running `azure-deployment-config.sh`, you'll have most values in `azure-secrets.env`. Here's a checklist:

```
☐ AZURE_CREDENTIALS (JSON format - see above)
☐ AZURE_CLIENT_ID: 6d1fdc5d-580b-499d-bae8-c129af50e96e
☐ AZURE_CLIENT_SECRET: [Get from Azure Portal]
☐ AZURE_TENANT_ID: 002fa7de-1afd-4945-86e1-79281af841ad
☐ AZURE_SUBSCRIPTION_ID: [Run: az account show --query id -o tsv]
☐ TF_BACKEND_STORAGE_ACCOUNT: [From terraform-backend-config.txt]
☐ TF_BACKEND_ACCESS_KEY: [From terraform-backend-config.txt]
☐ OPENAI_API_KEY: [Get from https://platform.openai.com/api-keys]
☐ JWT_SECRET: [From azure-secrets.env]
☐ ENCRYPTION_KEY: [From azure-secrets.env]
☐ MASTER_KEY: [From azure-secrets.env]
☐ POSTGRES_PASSWORD: [From azure-secrets.env]
```

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets to Git

Add these to `.gitignore`:
```
azure-secrets.env
terraform-backend-config.txt
azure-credentials.json
.env.production
*.tfvars
```

### 2. Rotate Secrets Regularly

- **Client Secrets**: Every 90 days
- **Database Passwords**: Every 180 days
- **API Keys**: When compromised or annually

### 3. Use Separate Environments

Create different secrets for:
- Development
- Staging
- Production

Use GitHub Environments to manage them separately.

### 4. Limit Access

- Only give repository admin access to those who need it
- Use GitHub's environment protection rules
- Enable required reviewers for production deployments

---

## 🧪 Testing Secrets Setup

After adding all secrets, test the GitHub Actions workflow:

### Method 1: Manual Trigger

1. Go to **Actions** tab in your repository
2. Select **Deploy to Azure** workflow
3. Click **Run workflow**
4. Select the environment (dev/staging/prod)
5. Click **Run workflow**

### Method 2: Push to Main Branch

```bash
git add .
git commit -m "Configure Azure deployment"
git push origin main
```

The workflow will automatically trigger and you can watch the progress in the Actions tab.

---

## ❌ Troubleshooting

### Error: "Secret not found"

**Solution:** Verify the secret name matches exactly (case-sensitive):
- ✅ Correct: `AZURE_CLIENT_ID`
- ❌ Wrong: `azure_client_id`

### Error: "Invalid credentials"

**Solution:**
1. Verify the service principal has Contributor role:
   ```bash
   az role assignment list --assignee 6d1fdc5d-580b-499d-bae8-c129af50e96e
   ```
2. If not, add it:
   ```bash
   az role assignment create \
     --assignee 6d1fdc5d-580b-499d-bae8-c129af50e96e \
     --role Contributor \
     --scope /subscriptions/YOUR_SUBSCRIPTION_ID
   ```

### Error: "Terraform backend authentication failed"

**Solution:**
1. Verify storage account name and key are correct
2. Check if the storage account exists:
   ```bash
   az storage account show \
     --name YOUR_STORAGE_ACCOUNT \
     --resource-group aura-tfstate-rg
   ```

### Error: "OpenAI API quota exceeded"

**Solution:**
1. Check your OpenAI usage: https://platform.openai.com/usage
2. Verify your billing is set up
3. Consider upgrading your plan

---

## 🔄 Updating Secrets

To update a secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Find the secret you want to update
3. Click **Update**
4. Enter the new value
5. Click **Update secret**

---

## 📊 Monitoring Secret Usage

### View Secret Usage in Logs

GitHub Actions logs will show when secrets are used, but the values are masked:

```
Using secret: AZURE_CLIENT_ID: ***
Using secret: POSTGRES_PASSWORD: ***
```

### Audit Secret Access

1. Go to **Settings** → **Audit log**
2. Filter by "secrets"
3. Review who accessed or modified secrets

---

## ✅ Verification Checklist

After adding all secrets, verify:

- [ ] All 12 required secrets are added
- [ ] Secret names match exactly (case-sensitive)
- [ ] No typos in secret values
- [ ] Client secret is current and valid
- [ ] OpenAI API key has sufficient quota
- [ ] Subscription ID is correct
- [ ] GitHub Actions workflow file exists (`.github/workflows/deploy-azure.yml`)
- [ ] Service principal has Contributor role on subscription

---

## 🚀 Next Steps

After configuring all secrets:

1. **Test the deployment workflow**
   ```bash
   git push origin main
   ```

2. **Monitor the deployment**
   - Go to **Actions** tab
   - Watch the workflow progress
   - Check for any errors

3. **Verify deployment**
   - Check Azure Portal for created resources
   - Test application endpoints
   - Verify monitoring is working

---

## 📚 Additional Resources

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure Service Principal Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals)
- [Terraform Azure Backend](https://www.terraform.io/docs/language/settings/backends/azurerm.html)

---

**Need Help?**

If you encounter issues:
1. Check the GitHub Actions logs for specific error messages
2. Verify all secrets are correctly configured
3. Review the Azure Portal for resource deployment status
4. Check the troubleshooting section above

**Security Concerns?**

If you believe a secret has been compromised:
1. Immediately rotate the secret in Azure Portal
2. Update the GitHub Secret with the new value
3. Review audit logs to identify how it was exposed
4. Consider enabling additional security measures (MFA, IP restrictions, etc.)
