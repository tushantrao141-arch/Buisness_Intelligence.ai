# Run SilentSignal in Docker (PowerShell)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host ">> Building and starting SilentSignal via Docker Compose..." -ForegroundColor Cyan
docker compose up --build -d

Write-Host ">> Waiting for SilentSignal to become healthy..." -ForegroundColor Yellow
$timeout = 30
$elapsed = 0
$url = "http://localhost:8501"

while ($elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "$url/_stcore/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host ">> SilentSignal is live at $url" -ForegroundColor Green
            Start-Process $url
            exit 0
        }
    } catch {
        # continue waiting
    }
    Start-Sleep -Seconds 2
    $elapsed += 2
}

Write-Host ">> Container started! Access the app at: $url" -ForegroundColor Green
