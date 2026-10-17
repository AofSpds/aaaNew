$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& "$PSScriptRoot\.venv\Scripts\chainlit.exe" run "$PSScriptRoot\app.py" --host 127.0.0.1 --port 30142 --headless

