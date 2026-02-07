# Deploy Helper Script
# Usage: ./deploy_helper.ps1

Write-Host "🌧️ Rain Forge Deployment Verification" -ForegroundColor Cyan
Write-Host "------------------------------------"

# Check Frontend Build
Write-Host "`n📦 Checking Frontend Build..." -ForegroundColor Yellow
cd frontend
if (Test-Path "package.json") {
    Write-Host "Installing dependencies..."
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Building frontend..."
        npm run build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Frontend Build Successful!" -ForegroundColor Green
        } else {
            Write-Host "❌ Frontend Build Failed!" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ npm install failed" -ForegroundColor Red
    }
} else {
    Write-Host "❌ package.json not found in frontend directory" -ForegroundColor Red
}
cd ..

# Check Backend Docker Build
Write-Host "`n🐳 Checking Backend Docker Build..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker build -t rainforge-backend-check ./backend
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend Docker Build Successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend Docker Build Failed!" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️ Docker is not installed or not in PATH. Skipping Docker check." -ForegroundColor Yellow
}

Write-Host "`n------------------------------------"
Write-Host "Ready to push! Follow instructions in DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
