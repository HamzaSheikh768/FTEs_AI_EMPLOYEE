# Build Custom Odoo Image
# Personal AI Employee - Gold Tier

Write-Host "============================================================" -ForegroundColor Blue
Write-Host "  BUILDING CUSTOM ODOO 19 IMAGE" -ForegroundColor Blue
Write-Host "  Personal AI Employee - Gold Tier" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""

# Navigate to odoo directory
$odooPath = Join-Path $PSScriptRoot "."
Write-Host "[INFO] Building from: $odooPath" -ForegroundColor Cyan
Set-Location $odooPath

# Build the Docker image
Write-Host ""
Write-Host "[INFO] Starting Docker build..." -ForegroundColor Cyan
docker build -t personal-ai-employee/odoo:19.0 -f Dockerfile .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Docker image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image Details:" -ForegroundColor Yellow
    docker images personal-ai-employee/odoo:19.0
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Update docker-compose.yml to use the new image" -ForegroundColor White
    Write-Host "  2. Run: docker-compose up -d" -ForegroundColor White
    Write-Host "  3. Access: http://localhost:8069" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "[ERROR] Docker build failed!" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey()
