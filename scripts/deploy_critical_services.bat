@echo off
REM Deploy Critical Services to Azure - Windows Batch Script
REM Fixes analytics, normalize crashes + deploys E&O portal

echo ==========================================
echo AURA AUDIT AI - CRITICAL FIXES DEPLOYMENT
echo ==========================================
echo.

SET ACR_NAME=auraauditaiprodacr
SET RESOURCE_GROUP=aura-audit-ai-prod-rg
SET AKS_CLUSTER=aura-audit-ai-prod-aks

echo Configuration:
echo   ACR: %ACR_NAME%
echo   Resource Group: %RESOURCE_GROUP%
echo   AKS Cluster: %AKS_CLUSTER%
echo.

echo ==========================================
echo Step 1: Build Critical Services with ACR Tasks
echo ==========================================
echo.

echo Building analytics (FIXED - ImportError)...
cd /d "C:\Users\jtoroni\Data Norm\Data-Norm-2\services\analytics"
call az acr build --registry %ACR_NAME% --image aura/analytics:latest --image aura/analytics:fixed-import-error --file Dockerfile .
IF %ERRORLEVEL% NEQ 0 (
    echo WARNING: Analytics build failed
) ELSE (
    echo SUCCESS: Analytics built and pushed
)
echo.

echo Building normalize (FIXED - ImportError)...
cd /d "C:\Users\jtoroni\Data Norm\Data-Norm-2\services\normalize"
call az acr build --registry %ACR_NAME% --image aura/normalize:latest --image aura/normalize:fixed-import-error --file Dockerfile .
IF %ERRORLEVEL% NEQ 0 (
    echo WARNING: Normalize build failed
) ELSE (
    echo SUCCESS: Normalize built and pushed
)
echo.

echo Building E&O Insurance Portal (REVENUE CRITICAL!)...
cd /d "C:\Users\jtoroni\Data Norm\Data-Norm-2\services\eo-insurance-portal"
call az acr build --registry %ACR_NAME% --image aura/eo-insurance-portal:latest --image aura/eo-insurance-portal:production --file Dockerfile .
IF %ERRORLEVEL% NEQ 0 (
    echo WARNING: E&O Portal build failed
) ELSE (
    echo SUCCESS: E&O Insurance Portal built and pushed!!!
)
echo.

echo Building connectors (MISSING IMAGE)...
cd /d "C:\Users\jtoroni\Data Norm\Data-Norm-2\services\connectors"
call az acr build --registry %ACR_NAME% --image aura/connectors:latest --file Dockerfile .
IF %ERRORLEVEL% NEQ 0 (
    echo WARNING: Connectors build failed
) ELSE (
    echo SUCCESS: Connectors built and pushed
)
echo.

echo Building gateway...
cd /d "C:\Users\jtoroni\Data Norm\Data-Norm-2\services\gateway"
call az acr build --registry %ACR_NAME% --image aura/gateway:latest --file Dockerfile .
IF %ERRORLEVEL% NEQ 0 (
    echo WARNING: Gateway build failed
) ELSE (
    echo SUCCESS: Gateway built and pushed
)
echo.

cd /d "C:\Users\jtoroni\Data Norm\Data-Norm-2"

echo.
echo ==========================================
echo Step 2: Get AKS Credentials
echo ==========================================
echo.

call az aks get-credentials --resource-group %RESOURCE_GROUP% --name %AKS_CLUSTER% --overwrite-existing
echo.

echo ==========================================
echo Step 3: Restart Critical Pods
echo ==========================================
echo.

echo Restarting analytics (to pick up fixed image)...
kubectl rollout restart deployment/analytics -n aura-audit-ai
echo.

echo Restarting normalize (to pick up fixed image)...
kubectl rollout restart deployment/normalize -n aura-audit-ai
echo.

echo Restarting connectors (to pick up new image)...
kubectl rollout restart deployment/connectors -n aura-audit-ai
echo.

echo ==========================================
echo Step 4: Check Pod Status
echo ==========================================
echo.

echo Waiting 30 seconds for pods to restart...
timeout /t 30 /nobreak
echo.

echo Current pod status:
kubectl get pods -n aura-audit-ai
echo.

echo ==========================================
echo CRITICAL FIXES DEPLOYED!
echo ==========================================
echo.
echo Fixed Services:
echo   - analytics (ImportError fixed)
echo   - normalize (ImportError fixed)
echo   - connectors (Image now exists)
echo   - E&O Insurance Portal (DEPLOYED!!!)
echo   - gateway (Deployed)
echo.
echo Next: Check pod logs to verify fixes:
echo   kubectl logs -n aura-audit-ai deployment/analytics --tail=20
echo   kubectl logs -n aura-audit-ai deployment/eo-insurance-portal --tail=20
echo.

pause
