$ErrorActionPreference = "Continue"

$Repo = "D:\sergi\Documents\Simulador-predial"
$Runtime = "D:\ProjectResort_Autonomy"
$LogDir = Join-Path $Runtime "logs"
$StateDir = Join-Path $Runtime "state"
$StopFile = Join-Path $Runtime "STOP"
$StatusFile = Join-Path $StateDir "supervisor_status.txt"
$Claude = "C:\Users\sergi\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"

New-Item -ItemType Directory -Force -Path $Runtime,$LogDir,$StateDir,(Join-Path $Runtime "temp") | Out-Null

$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, "ProjectResortClaudeSupervisor", [ref]$createdNew)
if (-not $createdNew) {
    Set-Content $StatusFile "Another supervisor instance is already active."
    exit 0
}

function Write-Status([string]$Text) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Set-Content $StatusFile "$stamp | $Text"
}

try {
    Remove-Item $StopFile -Force -ErrorAction SilentlyContinue
    Write-Status "Supervisor started."

    while ($true) {
        if (Test-Path $StopFile) {
            Write-Status "STOP requested. Supervisor exiting."
            break
        }

        if (-not (Test-Path $Repo)) {
            Write-Status "Repository not found. Retrying in 5 minutes."
            Start-Sleep -Seconds 300
            continue
        }

        Set-Location $Repo

        $currentTask = Join-Path $Repo "Docs\PROJECT_RESORT_EXECUTION\CLAUDE_CURRENT_TASK.md"
        if (Test-Path $currentTask) {
            $taskText = Get-Content $currentTask -Raw
            if ($taskText -match "PROJECT_STATUS:\s*COMPLETE") {
                Write-Status "Project marked COMPLETE. Supervisor exiting."
                break
            }
        }

        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $log = Join-Path $LogDir "claude_$stamp.log"

        $prompt = @"
You are the autonomous primary implementation agent for PROJECT RESORT.

Work directly in D:\sergi\Documents\Simulador-predial on branch claude/w1-masterplan.

Before changing anything, read:
- CLAUDE.md
- Docs/PROJECT_RESORT_EXECUTION/CLAUDE_AUTONOMOUS_MASTER.md
- Docs/PROJECT_RESORT_EXECUTION/00_EXECUTION_INDEX.md
- Docs/PROJECT_RESORT_EXECUTION/CLAUDE_CURRENT_TASK.md
- the current phase document
- the master GDD
- the official visual references
- the latest report for the current phase.

Continue from the real repository state. Do not wait for new instructions for normal implementation decisions. Do concrete work until the maximum safe amount of the current phase is complete.

Rules:
- preserve all existing local work;
- never use git reset --hard, git clean, force push, or destructive cleanup;
- never merge to main;
- never delete player saves;
- never skip phases;
- never invent a human playtest;
- never label concept art as a real gameplay screenshot;
- run real Unity validation before declaring technical PASS;
- use Tools/Autonomy/Run-UnityResortTests.ps1 for automated Unity validation;
- make small descriptive commits and push to origin/claude/w1-masterplan as validated blocks are completed;
- update Docs/PROJECT_RESORT_EXECUTION/CLAUDE_CURRENT_TASK.md and the current phase report before ending each work round;
- if a human gate is pending, mark HUMAN_GATE_PENDING and continue only with safe refinements inside the same phase;
- if blocked, try safe alternatives, document evidence and leave the next concrete action;
- if usage limits are near, prioritize checkpointing, commit/push, and a precise resume state.

Do not wait for approval for routine development work. Stop only for a genuine human-only blocker, usage limit, or a safely completed work round.
"@

        Write-Status "Claude starting work round. Log: $log"

        $output = @()
        try {
            $output = (& $Claude -p --permission-mode auto --permission-prompts none --effort high --autocompact auto --add-dir $Runtime --name "ProjectResort-Autonomous" $prompt 2>&1 | Tee-Object -FilePath $log)
            $code = $LASTEXITCODE
        }
        catch {
            $output += $_.Exception.ToString()
            $output | Add-Content -Path $log -Encoding UTF8
            $code = 99
        }

        $joined = ($output | Out-String)

        if (Test-Path $StopFile) {
            Write-Status "STOP requested after round."
            break
        }

        if ($joined -match "(?i)(usage limit|rate limit|quota|too many requests|reset.*usage)") {
            Write-Status "Usage limit detected. Retrying in 30 minutes."
            Start-Sleep -Seconds 1800
            continue
        }

        if ($code -ne 0) {
            Write-Status "Claude exited with code $code. Retrying in 5 minutes."
            Start-Sleep -Seconds 300
            continue
        }

        Write-Status "Work round complete. Starting another in 90 seconds."
        Start-Sleep -Seconds 90
    }
}
finally {
    try { $mutex.ReleaseMutex() } catch {}
    $mutex.Dispose()
}
