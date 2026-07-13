# BGDDR — Windows Production Setup (PowerShell)
# Run this script as Administrator to set up the full production environment.
# It installs dependencies, configures PostgreSQL, migrates data, and sets environment variables.

param(
    [string]$DbPassword = "",
    [string]$SecretKey = "",
    [switch]$SkipPgInstall = $false,
    [switch]$SkipDataMigration = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BGDDR Production Setup (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# --- 1. Python & pip check ---
Write-Host "`n[1/6] Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "Python not found. Install Python 3.11+ from https://python.org and retry."
}
Write-Host "  Python found: $($python.Source)" -ForegroundColor Green

# --- 2. Install Python dependencies ---
Write-Host "`n[2/6] Installing Python dependencies..." -ForegroundColor Yellow
& $python.Source -m pip install -r "$ProjectRoot\requirements.txt" 2>$null
& $python.Source -m pip install psycopg gunicorn 2>$null
Write-Host "  Dependencies installed." -ForegroundColor Green

# --- 3. PostgreSQL check ---
Write-Host "`n[3/6] Checking PostgreSQL..." -ForegroundColor Yellow
$pgCtl = Get-Command pg_ctl -ErrorAction SilentlyContinue
if (-not $pgCtl -and -not $SkipPgInstall) {
    Write-Host "  PostgreSQL not found. Install it from https://www.postgresql.org/download/windows/" -ForegroundColor Red
    Write-Host "  Then re-run this script with -SkipPgInstall after installation." -ForegroundColor Red
    Write-Host "  Or use -SkipPgInstall if PostgreSQL is already installed but not in PATH." -ForegroundColor Yellow
    exit 1
}
if ($pgCtl) {
    Write-Host "  PostgreSQL found: $($pgCtl.Source)" -ForegroundColor Green
} else {
    Write-Host "  Skipping PostgreSQL check (user says it's installed)." -ForegroundColor Yellow
}

# --- 4. Database setup ---
Write-Host "`n[4/6] Setting up PostgreSQL database..." -ForegroundColor Yellow
if ($DbPassword -eq "") {
    $DbPassword = Read-Host "Enter PostgreSQL password for user 'bgddr' (or press Enter for empty)" -AsSecureString | ConvertFrom-SecureString -AsPlainText
}

# Create user and database (if psql is available)
$psql = Get-Command psql -ErrorAction SilentlyContinue
if ($psql) {
    $env:PGPASSWORD = $DbPassword
    # Try creating user and db (may fail if they exist -- that's OK)
    & $psql.Source -U postgres -c "CREATE USER bgddr WITH PASSWORD '$DbPassword';" 2>$null
    & $psql.Source -U postgres -c "CREATE DATABASE bgddr OWNER bgddr;" 2>$null
    & $psql.Source -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bgddr TO bgddr;" 2>$null
    Write-Host "  Database 'bgddr' and user 'bgddr' ensured." -ForegroundColor Green
} else {
    Write-Host "  psql not in PATH. Create database and user manually:" -ForegroundColor Yellow
    Write-Host "    CREATE USER bgddr WITH PASSWORD 'your_password';" -ForegroundColor Gray
    Write-Host "    CREATE DATABASE bgddr OWNER bgddr;" -ForegroundColor Gray
    Write-Host "    GRANT ALL PRIVILEGES ON DATABASE bgddr TO bgddr;" -ForegroundColor Gray
}

# --- 5. Environment variables ---
Write-Host "`n[5/6] Setting environment variables..." -ForegroundColor Yellow
if ($SecretKey -eq "") {
    $SecretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object { [char]$_ })
    Write-Host "  Generated random SECRET_KEY." -ForegroundColor Green
}

$envVars = @{
    "DJANGO_SETTINGS_MODULE" = "bgddr.settings_prod"
    "DJANGO_SECRET_KEY" = $SecretKey
    "DJANGO_ALLOWED_HOSTS" = "localhost,127.0.0.1"
    "POSTGRES_DB" = "bgddr"
    "POSTGRES_USER" = "bgddr"
    "POSTGRES_PASSWORD" = $DbPassword
    "POSTGRES_HOST" = "localhost"
    "POSTGRES_PORT" = "5432"
}

# Save to a .env file for easy loading
$envFile = "$ProjectRoot\.env"
$envContent = @"
# BGDDR Production Environment Variables
# Source this file in PowerShell: Get-Content .env | ForEach-Object { if (`$_ -match '^(.*?)=(.*)$') { Set-Item "env:`$(`$matches[1])" `$matches[2] } }
"@
foreach ($key in $envVars.Keys) {
    $envContent += "`n$key=$($envVars[$key])"
    [Environment]::SetEnvironmentVariable($key, $envVars[$key], "Process")
}
$envContent | Out-File -FilePath $envFile -Encoding UTF8
Write-Host "  Environment variables set and saved to .env" -ForegroundColor Green

# --- 6. Django migrations & data ---
Write-Host "`n[6/6] Django setup..." -ForegroundColor Yellow

# Run migrations
& $python.Source "$ProjectRoot\manage.py" migrate --settings=bgddr.settings_prod

# Seed static data
& $python.Source "$ProjectRoot\manage.py" seed_drugs --settings=bgddr.settings_prod
& $python.Source "$ProjectRoot\manage.py" seed_labs --settings=bgddr.settings_prod
& $python.Source "$ProjectRoot\manage.py" seed_roles --settings=bgddr.settings_prod

# Collect static
& $python.Source "$ProjectRoot\manage.py" collectstatic --no-input --settings=bgddr.settings_prod

# Data migration (SQLite -> PostgreSQL)
if (-not $SkipDataMigration) {
    Write-Host "  Migrating data from SQLite to PostgreSQL..." -ForegroundColor Yellow
    # Update the migration script with the actual password
    $migrateScript = Get-Content "$ProjectRoot\migrate_to_postgres.py" -Raw
    $migrateScript = $migrateScript -replace 'PG_PASSWORD = "your_password_here"', "PG_PASSWORD = `"$DbPassword`""
    $migrateScript | Out-File -FilePath "$ProjectRoot\migrate_to_postgres.py" -Encoding UTF8
    & $python.Source "$ProjectRoot\migrate_to_postgres.py"
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Create a superuser: python manage.py createsuperuser --settings=bgddr.settings_prod" -ForegroundColor Gray
Write-Host "  2. Run the server: python manage.py runserver --settings=bgddr.settings_prod" -ForegroundColor Gray
Write-Host "  3. Or use gunicorn: gunicorn bgddr.wsgi:application --bind 0.0.0.0:8000" -ForegroundColor Gray
Write-Host "`nEnvironment variables saved to .env file." -ForegroundColor White
Write-Host "Load them in a new session with: Get-Content .env | ForEach-Object { if (`$_ -match '^(.*?)=(.*)$') { Set-Item env:`$(`$matches[1]) `$matches[2] } }" -ForegroundColor Gray
