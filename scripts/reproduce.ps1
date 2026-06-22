param([string]$RunId)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Test-Path 'data/manifests/demo-cn-etf-synthetic-v1.yml')) {
  uv run python scripts/create_demo_snapshot.py
}
uv run pytest tests/test_core.py
Write-Output "Core reproduction checks passed. Requested run: $RunId"

