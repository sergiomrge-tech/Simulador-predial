# W1 masterplan pipeline: static validation -> Blender generation -> reopen audit + review renders.
# Usage: powershell -ExecutionPolicy Bypass -File Tools/Blender/Run-W1Masterplan.ps1 [-Blender PATH] [-NoRender]
param(
    [string]$Blender = "",
    [switch]$NoRender
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if (-not $Blender) {
    $cmd = Get-Command blender -ErrorAction SilentlyContinue
    if ($cmd) { $Blender = $cmd.Source }
    else {
        $Blender = Get-ChildItem "C:\Program Files\Blender Foundation\*\blender.exe" -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
    }
}
if (-not $Blender -or -not (Test-Path $Blender)) { throw "Blender not found; pass -Blender PATH" }

python (Join-Path $root "Tools\Map\validate_masterplan.py") $root | Out-Null
if ($LASTEXITCODE -ne 0) { throw "static masterplan validation failed; see Docs/masterplan-validation-v1.json" }

& $Blender --background --factory-startup --python (Join-Path $root "Tools\Blender\create_santa_aurora_masterplan.py") -- --root $root
if ($LASTEXITCODE -ne 0) { throw "Blender generation failed" }

$blend = Join-Path $root "ArtSource\Blender\World\SantaAurora_Masterplan_v1.blend"
$verifyArgs = @("--background", "--factory-startup", $blend, "--python", (Join-Path $root "Tools\Blender\verify_masterplan_v1.py"), "--", "--root", $root)
if ($NoRender) { $verifyArgs += "--no-render" }
& $Blender @verifyArgs
if ($LASTEXITCODE -ne 0) { throw "Blender reopen verification failed" }

$report = Get-Content (Join-Path $root "ArtSource\Blender\World\Reviews\W1\w1_reopen_report.json") -Raw | ConvertFrom-Json
if (-not $report.passed) { throw ("reopen audit failed: " + ($report.errors -join "; ")) }
Write-Host "W1 masterplan pipeline OK: $($report.objectCount) objects, Blender $($report.blenderVersion)"
