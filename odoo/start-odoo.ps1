# Start Odoo - PowerShell Script
# Gold Tier - Personal AI Employee

Write-Host "============================================================" -ForegroundColor Blue
Write-Host "  STARTING ODOO COMMUNITY 19+" -ForegroundColor Blue
Write-Host "  Gold Tier - Personal AI Employee" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""

# Navigate to odoo directory
$odooPath = Join-Path $PSScriptRoot "odoo"
Write-Host "[INFO] Navigating to: $odooPath" -ForegroundColor Cyan
Set-Location $odooPath

# Check if docker-compose.yml exists
if (Test-Path "docker-compose.yml") {
    Write-Host "[OK] docker-compose.yml found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] docker-compose.yml not found!" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey()
    exit 1
}

# Start Odoo
Write-Host ""
Write-Host "[INFO] Starting Odoo containers..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Containers started" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to start containers" -ForegroundColor Red
    Write-Host "Check Docker Desktop is running"
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey()
    exit 1
}

# Wait for containers to start
Write-Host ""
Write-Host "[INFO] Waiting for containers to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check container status
Write-Host ""
Write-Host "[INFO] Container Status:" -ForegroundColor Cyan
docker-compose ps

# Show logs (last 20 lines)
Write-Host ""
Write-Host "[INFO] Recent Odoo logs (last 20 lines):" -ForegroundColor Cyan
docker-compose logs --tail=20 odoo

Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "  NEXT STEPS" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "1. Wait 2-3 minutes for Odoo to fully start" -ForegroundColor White
Write-Host "2. Check status: docker-compose ps" -ForegroundColor White
Write-Host "3. View logs: docker-compose logs -f odoo" -ForegroundColor White
Write-Host "4. Open browser: http://localhost:8069" -ForegroundColor White
Write-Host "5. Generate API key: python generate_api_key.py" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  URL: http://localhost:8069" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: OdooDb_S3cur3P@ss_9x7K2mN5pQ8w" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey()
