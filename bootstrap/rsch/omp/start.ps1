$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PI_CODING_AGENT_DIR = Join-Path $PSScriptRoot 'data'
& "$PSScriptRoot\omp.exe" @args
