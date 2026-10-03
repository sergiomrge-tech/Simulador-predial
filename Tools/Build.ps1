param([string]$UnityEditor = 'C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$unityProject = Join-Path $projectRoot 'FacilityOps'
$logPath = Join-Path $projectRoot 'Logs\unity-build.log'
New-Item -ItemType Directory -Force -Path (Split-Path $logPath) | Out-Null
$unityArguments = @('-batchmode', '-nographics', '-quit', '-projectPath', ('"' + $unityProject + '"'), '-executeMethod', 'FacilityOps.Editor.ProjectBuilder.Build', '-logFile', ('"' + $logPath + '"'))
$buildProcess = Start-Process -FilePath $UnityEditor -ArgumentList $unityArguments -WindowStyle Hidden -Wait -PassThru
if ($buildProcess.ExitCode -ne 0) { throw "Falha na compilação. Consulte $logPath" }
# The Editor regenerates a default value for an unused console platform on load.
# Clear that field after the Editor exits so Windows sources remain portable.
$settingsPath = Join-Path $unityProject 'ProjectSettings\ProjectSettings.asset'
$settingsText = [IO.File]::ReadAllText($settingsPath)
$settingsText = [regex]::Replace($settingsText, '(?m)^(  ps4Passcode:).*$', '$1 ')
[IO.File]::WriteAllText($settingsPath, $settingsText, [Text.UTF8Encoding]::new($false))
Write-Output (Join-Path $projectRoot 'Builds\Windows\FacilityOps.exe')
