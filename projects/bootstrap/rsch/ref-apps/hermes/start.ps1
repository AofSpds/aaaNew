$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:HERMES_HOME = Join-Path $PSScriptRoot 'data'
$env:HERMES_RUNTIME_DIR = Join-Path $PSScriptRoot 'runtime'
$env:UV_CACHE_DIR = Join-Path $PSScriptRoot '.uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PSScriptRoot 'python'
$hermesCommand = Join-Path $PSScriptRoot 'data\bin\hermes.exe'
if (-not (Test-Path -LiteralPath $hermesCommand)) { $hermesCommand = Join-Path $PSScriptRoot 'data\bin\hermes.cmd' }
& $hermesCommand @args