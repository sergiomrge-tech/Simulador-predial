param([string]$UnityEditor = 'C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$unityProject = Join-Path $projectRoot 'FacilityOps'
$logPath = Join-Path $projectRoot 'Logs\unity-build.log'
New-Item -ItemType Directory -Force -Path (Split-Path $logPath) | Out-Null
$unityArguments = @('-batchmode', '-nographics', '-quit', '-projectPath', ('"' + $unityProject + '"'), '-executeMethod', 'FacilityOps.Editor.ProjectBuilder.Build', '-logFile', ('"' + $logPath + '"'))
$buildProcess = Start-Process -FilePath $UnityEditor -ArgumentList $unityArguments -WindowStyle Hidden -Wait -PassThru
if ($buildProcess.ExitCode -ne 0) { throw "Falha na compilação. Consulte $logPath" }
Write-Output (Join-Path $projectRoot 'Builds\Windows\FacilityOps.exe')
