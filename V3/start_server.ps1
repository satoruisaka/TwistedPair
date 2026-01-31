# TwistedPair V2 Startup Script
# Run this from the TwistedPair root directory

Write-Host "🎸 Starting TwistedPair V2 Server..." -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is running
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama is not running. Please start Ollama first." -ForegroundColor Red
    Write-Host "   Run: ollama serve" -ForegroundColor Yellow
    exit 1
}

# Check Python dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$deps = @("fastapi", "uvicorn", "requests", "pyyaml")
foreach ($dep in $deps) {
    $check = python -c "import $dep; print('OK')" 2>$null
    if ($check -eq "OK") {
        Write-Host "  ✅ $dep" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dep not found" -ForegroundColor Red
        Write-Host "     Install: pip install $dep" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Starting FastAPI server on http://localhost:8000..." -ForegroundColor Cyan
Write-Host "Open UI at: http://localhost:8000/V2/index.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start server from V2 directory
Set-Location V2
uvicorn server:app --reload --port 8000
