@echo off
echo Starting Unified Cognition Module with Cloudflare Tunnel...

echo Starting Docker containers...
docker-compose up -d

echo Waiting for services to be ready...
timeout /t 30 /nobreak > nul

echo Starting Cloudflare tunnel...
.\cloudflared.exe tunnel --config cloudflared.yml run unified-cognition-tunnel

echo Tunnel started. Your services should be available at:
echo - Dashboard: https://spruked.com
echo - API: https://api.spruked.com
pause