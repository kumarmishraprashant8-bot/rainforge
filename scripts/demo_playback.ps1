# RainForge Demo Playback Script (PowerShell)
# Runs through complete demo flow using Invoke-RestMethod

$API_BASE = "http://localhost:8000/api/v1"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       RainForge Demo Playback Script         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Health check
Write-Host "1. Health Check..." -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "$API_BASE/health" -Method Get
    $health | ConvertTo-Json
} catch {
    Write-Host "Error: Backend not responding. Make sure docker-compose is running!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create Assessment
Write-Host "2. Creating Assessment..." -ForegroundColor Green
$assessBody = @{
    site_id = "DEMO-PLAY-001"
    address = "Municipal School Sector 5, Rohini, Delhi"
    lat = 28.7041
    lng = 77.1025
    roof_area_sqm = 250
    roof_material = "concrete"
    demand_l_per_day = 400
    floors = 2
    people = 150
    state = "Delhi"
    city = "New Delhi"
} | ConvertTo-Json

try {
    $assess = Invoke-RestMethod -Uri "$API_BASE/assess" -Method Post -Body $assessBody -ContentType "application/json"
    $assess | ConvertTo-Json -Depth 3
    $assessmentId = $assess.assessment_id
    Write-Host "Assessment ID: $assessmentId" -ForegroundColor Yellow
} catch {
    Write-Host "Assessment Error: $_" -ForegroundColor Red
}
Write-Host ""

# List Installers
Write-Host "3. Listing Available Installers..." -ForegroundColor Green
try {
    $installers = Invoke-RestMethod -Uri "$API_BASE/installers?min_rpi=70" -Method Get
    $installers.installers | Select-Object -First 3 | ConvertTo-Json
} catch {
    Write-Host "Installers Error: $_" -ForegroundColor Red
}
Write-Host ""

# Run Allocation
Write-Host "4. Running Gov-Optimized Allocation..." -ForegroundColor Green
$allocBody = @{
    job_ids = @("JOB-DEMO-001")
    mode = "gov_optimized"
} | ConvertTo-Json

try {
    $alloc = Invoke-RestMethod -Uri "$API_BASE/allocate" -Method Post -Body $allocBody -ContentType "application/json"
    $alloc | ConvertTo-Json -Depth 2
} catch {
    Write-Host "Allocation Error: $_" -ForegroundColor Red
}
Write-Host ""

# Submit Telemetry
Write-Host "5. Submitting Tank Telemetry..." -ForegroundColor Green
$telemetryBody = @{
    device_id = "TANK-DEMO-001"
    project_id = 1
    tank_level_liters = 5700
    battery_pct = 87.5
    signal_rssi = -67
} | ConvertTo-Json

try {
    $telemetry = Invoke-RestMethod -Uri "$API_BASE/telemetry" -Method Post -Body $telemetryBody -ContentType "application/json"
    $telemetry | ConvertTo-Json
} catch {
    Write-Host "Telemetry Error: $_" -ForegroundColor Red
}
Write-Host ""

# Get Monitoring Data
Write-Host "6. Fetching Monitoring Data..." -ForegroundColor Green
try {
    $monitor = Invoke-RestMethod -Uri "$API_BASE/monitoring/1?hours=24" -Method Get
    @{
        current_level = $monitor.current_level
        days_until_empty = $monitor.days_until_empty
        alerts = $monitor.alerts
    } | ConvertTo-Json -Depth 2
} catch {
    Write-Host "Monitoring Error: $_" -ForegroundColor Red
}
Write-Host ""

# Public Dashboard
Write-Host "7. Public Transparency Dashboard..." -ForegroundColor Green
try {
    $dashboard = Invoke-RestMethod -Uri "$API_BASE/public/dashboard" -Method Get
    $dashboard.summary | ConvertTo-Json
} catch {
    Write-Host "Dashboard Error: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Demo Playback Complete!             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open http://localhost:5173 in your browser to see the frontend!" -ForegroundColor Yellow
