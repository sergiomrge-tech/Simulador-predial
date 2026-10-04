param(
    [ValidateSet('Lar','Corridor')][string]$Stage = 'Lar',
    [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
    [string]$Root = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
$slice = Join-Path $Root 'ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend'
if (!(Test-Path -LiteralPath $slice)) { throw 'Frozen W3 source missing.' }
if ($Stage -eq 'Corridor') {
    $gate = Join-Path $Root 'Logs/lar-playmode-gate.txt'
    if (!(Test-Path -LiteralPath $gate) -or !(Get-Content -LiteralPath $gate -Raw).StartsWith('PASS')) {
        throw 'Lar Play Mode gate must pass before exporting the corridor.'
    }
}
$sourceHash = (Get-FileHash -LiteralPath $slice -Algorithm SHA256).Hash
$logs = Join-Path $Root 'Logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
function Invoke-Export([string]$Source, [string]$Script, [string[]]$Arguments) {
    $log = Join-Path $logs (([IO.Path]::GetFileNameWithoutExtension($Script)) + '-' + ($Arguments -join '_').Replace('/','_').Replace('\','_').Replace(':','_') + '.log')
    & $Blender -b $Source --python-exit-code 1 --python (Join-Path $Root $Script) -- --root $Root @Arguments *> $log
    if ($LASTEXITCODE -ne 0) { Get-Content -LiteralPath $log -Tail 15; throw "Exporter failed: $Script" }
    Write-Output "PASS: $Script $($Arguments -join ' ')"
}
$corridor = Get-Content -LiteralPath (Join-Path $Root 'Docs/unity-vertical-slice-corridor-v1.json') -Raw | ConvertFrom-Json
$cells = if ($Stage -eq 'Lar') { @('SA_M01_01_S00_02') } else { $corridor.cells }
foreach ($cell in $cells) {
    Invoke-Export $slice 'Tools/Blender/preflight_unity_cell_export.py' @('--cell',$cell)
    Invoke-Export $slice 'Tools/Blender/export_unity_cell_fbx.py' @('--cell',$cell)
}
Invoke-Export $slice 'Tools/Blender/export_unity_w3_materials.py' @()
$heroes = if ($Stage -eq 'Lar') { @('home.starter') } else { @('home.starter','garage','horizonte','grocery') }
foreach ($hero in $heroes) {
    $file = 'W2_' + $hero.Replace('.','_') + '.blend'
    Invoke-Export (Join-Path $Root "ArtSource/Blender/World/OldTown/Heroes/$file") 'Tools/Blender/export_unity_hero_fbx.py' @('--hero',$hero)
    # Include the world anchors and the referenced hero's internal points, preserving their authored names.
    Invoke-Export $slice 'Tools/Blender/export_unity_gameplay_markers.py' @('--name',$hero,'--facility',$hero)
}
if ((Get-FileHash -LiteralPath $slice -Algorithm SHA256).Hash -ne $sourceHash) { throw 'Frozen source changed during export.' }
Write-Output "SOURCE UNMODIFIED: $sourceHash"
