#!/usr/bin/env pwsh
# Build backend Docker image with admin-console static assets included.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host '==> Building admin console static assets...'
node admin-web/scripts/build.mjs

if (-not (Test-Path 'frontend/admin-dist/index.html')) {
    throw 'frontend/admin-dist/index.html not found after admin build'
}

$Tag = if ($args.Count -gt 0) { $args[0] } else { 'chem-teacher/backend:local' }

Write-Host "==> Building Docker image: $Tag"
docker build -f backend/Dockerfile -t $Tag .

Write-Host '==> Done.'
Write-Host "Verify locally: docker run --rm -p 8000:8080 -e DEBUG=true -e DB_TYPE=sqlite $Tag"
