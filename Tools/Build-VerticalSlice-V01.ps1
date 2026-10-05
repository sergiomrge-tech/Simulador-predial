#requires -Version 7.0
[CmdletBinding()]
param([switch]$ValidateOnly, [int]$PlayerTimeoutSeconds = 1800)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repository = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$project = Join-Path $repository 'FacilityOps'
$evidence = Join-Path $repository 'Docs/ValidationEvidence/VerticalSliceQA'
$logs = Join-Path $repository 'Logs/VerticalSliceQA'
New-Item -ItemType Directory -Force -Path $evidence, $logs | Out-Null
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
if (-not (Get-Command unity -ErrorAction SilentlyContinue)) { throw 'Unity CLI ausente. Instale a CLI oficial antes de executar.' }
function Invoke-UnityQa([string]$Method, [string]$LogName) {
    & unity run $project --timeout 600 --non-interactive --no-banner -- -executeMethod $Method -logFile (Join-Path $logs $LogName)
    if ($LASTEXITCODE -ne 0) { throw "Unity QA falhou em $Method. Consulte $logs." }
}
$oldContinuous = $env:VERTICAL_SLICE_CONTINUOUS_QA
$oldStage = $env:FACILITY_QA_BUILD_STAGE
try {
    Invoke-UnityQa 'FacilityOps.Editor.VerticalSliceQaRunner.ValidateStaticBatch' 'static.log'
    $env:VERTICAL_SLICE_CONTINUOUS_QA = '1'
    & unity test $project --mode EditMode --timeout 1500 --output (Join-Path $evidence 'EditMode.xml') --non-interactive --no-banner -- -worldSlice -worldSliceQa -logFile (Join-Path $logs 'tests.log')
    if ($LASTEXITCODE -ne 0) { throw 'Compilação/testes/rota física falharam. Nenhum build foi gerado.' }
    Invoke-UnityQa 'FacilityOps.Editor.VerticalSliceBuildPipeline.RecordTests' 'test-receipt.log'
    if ($ValidateOnly) {
        Invoke-UnityQa 'FacilityOps.Editor.VerticalSliceQaRunner.Run' 'summary.log'
        Write-Output "Validação do Editor concluída. READY_FOR_USER_TEST depende da rodada Player. Evidências: $evidence"
        return
    }
    $buildRoot = [IO.Path]::GetFullPath((Join-Path $repository 'Builds/Windows'))
    $stage = Join-Path $buildRoot ('QA-stage-' + [guid]::NewGuid().ToString('N'))
    $distribution = Join-Path $buildRoot 'FacilityOps_CidadeAntiga_VerticalSlice_v0.1'
    if (Test-Path -LiteralPath $distribution) { throw "Distribuição existente preservada: $distribution. Mova-a antes de gerar outra." }
    $env:FACILITY_QA_BUILD_STAGE = $stage
    Invoke-UnityQa 'FacilityOps.Editor.VerticalSliceBuildPipeline.BuildCandidate' 'build.log'
    $qa = Get-Content -LiteralPath (Join-Path $evidence 'qa.json') -Raw | ConvertFrom-Json
    $executable = Join-Path $stage 'FacilityOps_CidadeAntiga_VerticalSlice_v0_1.exe'
    $playerLog = Join-Path $logs 'player.log'
    foreach ($file in @('player-qa.json', 'process-receipt.json', 'performance.json', 'performance.md')) {
        $previousReceipt = Join-Path $evidence $file
        if (Test-Path -LiteralPath $previousReceipt) { Remove-Item -LiteralPath $previousReceipt }
    }
    $arguments = @('-worldSlice', '-worldSliceQa', '-verticalSliceQa', '-verticalSliceQaRoot', ('"' + $repository + '"'), '-verticalSliceQaRoute', ('"' + (Join-Path $evidence 'route.json') + '"'), '-verticalSliceQaFingerprint', $qa.fingerprint, '-logFile', ('"' + $playerLog + '"'))
    $process = Start-Process -FilePath $executable -ArgumentList $arguments -WindowStyle Hidden -PassThru
    if (-not $process.WaitForExit($PlayerTimeoutSeconds * 1000)) { $process.Kill(); throw 'Player QA excedeu timeout. Não empacotado.' }
    if ($process.ExitCode -ne 0) { throw "Player falhou com código $($process.ExitCode). Consulte $playerLog." }
    if (-not (Test-Path -LiteralPath $playerLog)) { throw 'Log de Player ausente.' }
    $critical = Select-String -LiteralPath $playerLog -Pattern '^NullReferenceException|^MissingReferenceException|^InvalidOperationException|^ArgumentException|^Exception:|^Assertion failed|^Crash!!!|^Fatal error|^Shader error|^error CS|^DllNotFoundException|^TypeLoadException'
    if ($critical) { throw 'Erro crítico no log do Player. Entrega bloqueada.' }
    [ordered]@{ status = 'PASS'; fingerprint = $qa.fingerprint; exitCode = $process.ExitCode; criticalLogErrors = 0 } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $evidence 'process-receipt.json') -Encoding utf8
    Invoke-UnityQa 'FacilityOps.Editor.VerticalSliceQaRunner.AssertReadyBatch' 'delivery.log'
    $resolvedStage = [IO.Path]::GetFullPath($stage)
    $resolvedDistribution = [IO.Path]::GetFullPath($distribution)
    $allowedPrefix = $buildRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $resolvedStage.StartsWith($allowedPrefix, [StringComparison]::OrdinalIgnoreCase) -or -not $resolvedDistribution.StartsWith($allowedPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Destino fora de Builds/Windows.' }
    # One shell, literal paths; fresh destination, no recursive deletion/overwrite of other builds.
    Move-Item -LiteralPath $resolvedStage -Destination $resolvedDistribution
    Copy-Item -LiteralPath $evidence -Destination (Join-Path $distribution 'ValidationEvidence') -Recurse
    $playerReceipt = Get-Content -LiteralPath (Join-Path $evidence 'player-qa.json') -Raw | ConvertFrom-Json
    Copy-Item -LiteralPath $playerReceipt.captureFolder -Destination (Join-Path $distribution 'Previews') -Recurse
    $manifest = @(Get-ChildItem -LiteralPath $distribution -Recurse -File | ForEach-Object {
        [ordered]@{ path = [IO.Path]::GetRelativePath($distribution, $_.FullName).Replace('\', '/'); bytes = $_.Length; sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    })
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $distribution 'FILES_MANIFEST.json') -Encoding utf8
    Get-FileHash -LiteralPath (Join-Path $distribution 'FILES_MANIFEST.json') -Algorithm SHA256 | ForEach-Object { "$($_.Hash)  FILES_MANIFEST.json" } | Set-Content -LiteralPath (Join-Path $distribution 'SHA256SUMS.txt') -Encoding utf8
    Write-Output "READY_FOR_USER_TEST = TRUE / $distribution"
} finally {
    $env:VERTICAL_SLICE_CONTINUOUS_QA = $oldContinuous
    $env:FACILITY_QA_BUILD_STAGE = $oldStage
}
