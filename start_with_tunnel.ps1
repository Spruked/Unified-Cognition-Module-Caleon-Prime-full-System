Write-Host "Starting Unified Cognition Module with Cloudflare Tunnel..." -ForegroundColor Green

Write-Host "Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Starting Cloudflare tunnel..." -ForegroundColor Yellow
.\cloudflared.exe tunnel --config cloudflared.yml run unified-cognition-tunnel

Write-Host "Tunnel started. Your services should be available at:" -ForegroundColor Green
Write-Host "- Dashboard: https://spruked.com" -ForegroundColor Cyan
Write-Host "- API: https://api.spruked.com" -ForegroundColor Cyan
Read-Host "Press Enter to exit"