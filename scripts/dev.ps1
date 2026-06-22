$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$api = Start-Process -FilePath 'uv' -ArgumentList @('run','uvicorn','app.main:app','--reload','--host','127.0.0.1','--port','8000') -WorkingDirectory "$root\apps\api" -WindowStyle Hidden -PassThru
try {
  Set-Location $root
  npm.cmd run dev
} finally {
  Stop-Process -Id $api.Id -ErrorAction SilentlyContinue
}

