$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:XDG_CONFIG_HOME = Join-Path $PSScriptRoot '.runtime\config'
$env:XDG_DATA_HOME = Join-Path $PSScriptRoot '.runtime\data'
$env:XDG_CACHE_HOME = Join-Path $PSScriptRoot '.runtime\cache'
$env:XDG_STATE_HOME = Join-Path $PSScriptRoot '.runtime\state'
& "$PSScriptRoot\node_modules\opencode-ai\bin\opencode.exe" web --hostname 127.0.0.1 --port 4096