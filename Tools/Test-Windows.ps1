$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$executable = Join-Path $projectRoot 'Builds\Windows\FacilityOps.exe'
$logPath = Join-Path $projectRoot 'Logs\windows-smoke.log'
$qaPath = Join-Path $projectRoot 'Builds\Windows\QA'
$passPath = Join-Path $qaPath 'PASSED.txt'
if (Test-Path -LiteralPath $passPath) { Remove-Item -LiteralPath $passPath }
$smokeArguments = @('-facilitySmoke', '-screen-width', '1280', '-screen-height', '720', '-screen-fullscreen', '0', '-logFile', ('"' + $logPath + '"'))
$smokeProcess = Start-Process -FilePath $executable -ArgumentList $smokeArguments -WindowStyle Hidden -PassThru
if (-not $smokeProcess.WaitForExit(90000)) { Stop-Process -Id $smokeProcess.Id; throw "Teste excedeu 90s. Consulte $logPath" }
if ($smokeProcess.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $passPath)) { throw "Teste falhou. Consulte $logPath" }
Get-Content -LiteralPath $passPath
