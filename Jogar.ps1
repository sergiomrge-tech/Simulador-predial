$ErrorActionPreference = 'Stop'
$gamePath = Join-Path $PSScriptRoot 'Builds\Windows\FacilityOps.exe'
if (-not (Test-Path -LiteralPath $gamePath)) { throw 'Build não encontrado. Execute Tools\Build.ps1 primeiro.' }
Start-Process -FilePath $gamePath -WorkingDirectory (Split-Path $gamePath)
