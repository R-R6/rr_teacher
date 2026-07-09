#!/usr/bin/env pwsh
# Build uni-app WeChat mini program into frontend/dist/build/mp-weixin.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

node scripts/build_mp_weixin.mjs
