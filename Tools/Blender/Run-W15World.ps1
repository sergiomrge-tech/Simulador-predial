# W1.5 pipeline: static validation + routes -> masterplan, Old Town base and kit generation -> reopen audits + review captures.
# Usage: powershell -ExecutionPolicy Bypass -File Tools/Blender/Run-W15World.ps1 [-Blender PATH] [-NoRender]
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
if ($LASTEXITCODE -ne 0) { throw "static validation failed; see Docs/masterplan-validation-v1.json" }
python (Join-Path $root "Tools\Map\masterplan_routes.py") $root | Out-Null
if ($LASTEXITCODE -ne 0) { throw "routes failed" }

$gens = @(
    @{ script = "create_santa_aurora_masterplan.py"; blend = "ArtSource\Blender\World\SantaAurora_Masterplan_v1_5.blend"; mode = "masterplan" },
    @{ script = "create_oldtown_base.py"; blend = "ArtSource\Blender\World\OldTown\SantaAurora_CidadeAntiga_Base_v1.blend"; mode = "oldtown" },
    @{ script = "create_oldtown_kit.py"; blend = "ArtSource\Blender\Kits\SantaAurora_CidadeAntiga_Kit_v1.blend"; mode = "kit" }
)
foreach ($g in $gens) {
    & $Blender --background --factory-startup --python (Join-Path $root "Tools\Blender\$($g.script)") -- --root $root
    if ($LASTEXITCODE -ne 0) { throw "generation failed: $($g.script)" }
}
foreach ($g in $gens) {
    $args = @("--background", "--factory-startup", (Join-Path $root $g.blend), "--python", (Join-Path $root "Tools\Blender\verify_world_v1_5.py"), "--", "--root", $root, "--mode", $g.mode)
    if ($NoRender) { $args += "--no-render" }
    & $Blender @args
    if ($LASTEXITCODE -ne 0) { throw "reopen failed: $($g.mode)" }
    $rep = Get-Content (Join-Path $root "ArtSource\Blender\World\Reviews\W1_5\reopen_$($g.mode).json") -Raw | ConvertFrom-Json
    if (-not $rep.passed) { throw ("reopen audit failed ($($g.mode)): " + ($rep.errors -join "; ")) }
    Write-Host "OK $($g.mode): $($rep.objectCount) objects"
}
Write-Host "W1.5 pipeline OK"
