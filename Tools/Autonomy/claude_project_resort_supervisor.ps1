$ErrorActionPreference = "Continue"

$Repo = "D:\sergi\Documents\Simulador-predial"
$Runtime = "D:\ProjectResort_Autonomy"
$LogDir = Join-Path $Runtime "logs"
$StateDir = Join-Path $Runtime "state"
$StopFile = Join-Path $Runtime "STOP"
$StatusFile = Join-Path $StateDir "supervisor_status.txt"
$Claude = "C:\Users\sergi\AppData\Roaming\npm\claude.cmd"

New-Item -ItemType Directory -Force -Path $Runtime,$LogDir,$StateDir,(Join-Path $Runtime "temp") | Out-Null

$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, "ProjectResortClaudeSupervisor", [ref]$createdNew)
if (-not $createdNew) {
    Set-Content $StatusFile "Outra instância do supervisor já está ativa."
    exit 0
}

function Write-Status([string]$Text) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Set-Content $StatusFile "$stamp | $Text"
}

try {
    Remove-Item $StopFile -Force -ErrorAction SilentlyContinue
    Write-Status "Supervisor iniciado."

    while ($true) {
        if (Test-Path $StopFile) {
            Write-Status "STOP solicitado. Supervisor encerrando."
            break
        }

        if (-not (Test-Path $Repo)) {
            Write-Status "Repositório não encontrado. Nova tentativa em 5 minutos."
            Start-Sleep -Seconds 300
            continue
        }

        Set-Location $Repo

        $currentTask = Join-Path $Repo "Docs\PROJECT_RESORT_EXECUTION\CLAUDE_CURRENT_TASK.md"
        if (Test-Path $currentTask) {
            $taskText = Get-Content $currentTask -Raw
            if ($taskText -match "PROJECT_STATUS:\s*COMPLETE") {
                Write-Status "Projeto marcado como COMPLETE. Supervisor encerrado."
                break
            }
        }

        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $log = Join-Path $LogDir "claude_$stamp.log"

        $prompt = @"
Você é o executor principal autônomo do PROJECT RESORT.

Trabalhe diretamente no repositório D:\sergi\Documents\Simulador-predial, branch claude/w1-masterplan.

Antes de agir, leia:
- CLAUDE.md
- Docs/PROJECT_RESORT_EXECUTION/CLAUDE_AUTONOMOUS_MASTER.md
- Docs/PROJECT_RESORT_EXECUTION/00_EXECUTION_INDEX.md
- Docs/PROJECT_RESORT_EXECUTION/CLAUDE_CURRENT_TASK.md
- o documento da fase atual
- o GDD mestre
- as referências visuais oficiais
- o relatório mais recente da fase atual.

Continue do estado real existente. Não espere novas instruções para microdecisões. Faça trabalho concreto até concluir o máximo seguro da fase atual.

Regras:
- preserve todo trabalho local;
- não use git reset --hard, git clean, force-push ou ações destrutivas;
- não faça merge em main;
- não apague saves;
- não pule fases;
- não invente teste humano;
- não trate concept art como captura real;
- rode Unity/testes reais antes de declarar PASS técnico;
- use Tools/Autonomy/Run-UnityResortTests.ps1 para a validação automatizada;
- faça commits pequenos e push para origin/claude/w1-masterplan conforme blocos validados;
- atualize Docs/PROJECT_RESORT_EXECUTION/CLAUDE_CURRENT_TASK.md e o relatório da fase antes de encerrar a rodada;
- se houver gate humano pendente, marque HUMAN_GATE_PENDING e continue apenas com refinamentos seguros da mesma fase;
- se houver bloqueio, tente alternativas seguras, documente causa/evidência e deixe o próximo passo concreto;
- se o limite de uso estiver próximo, priorize checkpoint, commit/push e estado de retomada.

Não fique aguardando confirmação para ações normais de desenvolvimento. Pare somente por bloqueio que realmente exija uma pessoa, limite de uso, ou conclusão segura da rodada.
"@

        Write-Status "Claude iniciando nova rodada. Log: $log"

        $output = @()
        try {
            $output = & $Claude -p --permission-mode auto --permission-prompts none --effort high --autocompact auto --add-dir $Runtime --name "ProjectResort-Autonomous" $prompt 2>&1
            $code = $LASTEXITCODE
        }
        catch {
            $output += $_.Exception.ToString()
            $code = 99
        }

        $output | Set-Content -Path $log -Encoding UTF8
        $joined = ($output | Out-String)

        if (Test-Path $StopFile) {
            Write-Status "STOP solicitado após rodada."
            break
        }

        if ($joined -match "(?i)(usage limit|rate limit|quota|limite de uso|reset.*usage|too many requests)") {
            Write-Status "Limite/franquia detectado. Retentativa em 30 minutos."
            Start-Sleep -Seconds 1800
            continue
        }

        if ($code -ne 0) {
            Write-Status "Claude encerrou com código $code. Retentativa em 5 minutos."
            Start-Sleep -Seconds 300
            continue
        }

        Write-Status "Rodada concluída. Nova rodada em 90 segundos."
        Start-Sleep -Seconds 90
    }
}
finally {
    try { $mutex.ReleaseMutex() } catch {}
    $mutex.Dispose()
}
