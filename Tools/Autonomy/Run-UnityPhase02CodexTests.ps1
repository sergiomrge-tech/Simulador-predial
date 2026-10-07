# Phase 02 only. Captures are redirected so ArtSource/Blender/World/Reviews is never overwritten.
param(
    [string]$TestFilter = "ResortAurora.Tests.LoopTests;ResortAurora.Tests.LivingWorldTests;ResortAurora.Tests.AmbientLifeTests;ResortAurora.Tests.HumanVisualTests",
    [ValidateSet("PlayMode","EditMode")]
    [string]$TestPlatform = "PlayMode",
    [switch]$Graphics,
    [string]$EvidenceRoot = "D:\sergi\Documents\Simulador-predial\Docs\PROJECT_RESORT_EXECUTION\Evidence\CODEX_2026-10-07"
)

$ErrorActionPreference = "Stop"

$Repo = "D:\sergi\Documents\Simulador-predial"
$Project = Join-Path $Repo "FacilityOps"
$Runtime = $EvidenceRoot
$LogDir = Join-Path $Runtime "logs"
$TempDir = Join-Path $Runtime "temp"
$Unity = "C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe"
$Upm = "C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Data\Resources\PackageManager\Server\UnityPackageManager.exe"

# Concurrent continuations share one Unity project. Serialize this existing
# runner and also respect older launches that predate the mutex.
$projectMutex = New-Object System.Threading.Mutex($false, "ProjectResortUnityPhase02Tests")
Write-Host "Waiting for exclusive Unity project access..."
try { $null = $projectMutex.WaitOne() } catch [System.Threading.AbandonedMutexException] { }
while (Get-CimInstance Win32_Process -Filter "name = 'Unity.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine.Contains($Project) -and $_.CommandLine -notmatch 'AssetImport|adb2'
}) {
    Write-Host "Unity is already running this project; preserving the active execution."
    Start-Sleep -Seconds 5
}

New-Item -ItemType Directory -Force -Path $LogDir,$TempDir | Out-Null
$env:RESORT_TEST_CAPTURE_ROOT = Join-Path $Runtime "captures"
$env:RESORT_STAGE = "1"

# UPM 6000.6 requires HOME even on Windows; use the actual user profile.
$env:HOME = $env:USERPROFILE
$env:ALLUSERSPROFILE = "C:\ProgramData"
$env:PROGRAMDATA = "C:\ProgramData"
$env:TEMP = $TempDir
$env:TMP = $TempDir

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ipcId = "PR$PID"
$upmIpc = "Unity-Upm-$ipcId"
$unityIpc = "Upm-$ipcId"
$log = Join-Path $LogDir "unity_${TestPlatform}_${stamp}.log"
$results = Join-Path $LogDir "unity_${TestPlatform}_${stamp}.xml"

Write-Host "PROJECT=$Project"
Write-Host "FILTER=$TestFilter"
Write-Host "PLATFORM=$TestPlatform"
Write-Host "LOG=$log"
Write-Host "RESULTS=$results"

$upmArgs = @("server","-s",$PID,"--ipc-path",$upmIpc,"-l","2")
$upmProc = Start-Process -FilePath $Upm -ArgumentList $upmArgs -PassThru -WindowStyle Hidden
Start-Sleep -Milliseconds 900

try {
    if ($upmProc.HasExited) {
        throw "Unity Package Manager encerrou antes do Unity iniciar."
    }

    $args = @(
        "-batchmode",
        "-upmIpcPath",$unityIpc,
        "-projectPath",$Project,
        "-runTests",
        "-testPlatform",$TestPlatform,
        "-testFilter",$TestFilter,
        "-testResults",$results,
        "-logFile",$log
    )
    if (-not $Graphics) {
        $args = @("-nographics") + $args
    }

    $unityProc = Start-Process -FilePath $Unity -ArgumentList $args -PassThru -WindowStyle Hidden
    $deadline = (Get-Date).AddMinutes(45)

    while (-not $unityProc.HasExited) {
        if ((Get-Date) -gt $deadline) {
            Stop-Process -Id $unityProc.Id -Force -ErrorAction SilentlyContinue
            throw "Unity excedeu 45 minutos."
        }
        Start-Sleep -Seconds 2
        $unityProc.Refresh()
    }

    $exit = $unityProc.ExitCode
    Write-Host "UNITY_EXIT=$exit"

    if (Test-Path $results) {
        [xml]$xml = Get-Content $results
        $run = $xml.'test-run'
        Write-Host ("TESTS total={0} passed={1} failed={2} skipped={3}" -f $run.total,$run.passed,$run.failed,$run.skipped)
        if ([int]$run.failed -gt 0) {
            Write-Host "FAILED_TESTS:"
            Select-Xml -Xml $xml -XPath "//test-case[@result='Failed']" | ForEach-Object {
                Write-Host (" - " + $_.Node.fullname)
            }
            exit 2
        }
        if ($exit -ne 0) { exit $exit }
        exit 0
    }

    Write-Host "RESULT_XML_MISSING"
    if (Test-Path $log) {
        Get-Content $log -Tail 160
    }
    if ($exit -eq 0) { exit 3 } else { exit $exit }
}
finally {
    if ($upmProc -and -not $upmProc.HasExited) {
        Stop-Process -Id $upmProc.Id -Force -ErrorAction SilentlyContinue
    }
    $projectMutex.ReleaseMutex()
    $projectMutex.Dispose()
}
