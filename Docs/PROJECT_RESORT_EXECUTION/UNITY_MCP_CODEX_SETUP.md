# PROJECT RESORT — Codex ↔ Unity MCP: working setup

Verified on 2026-10-07, approximately 09:43 America/Sao_Paulo (12:43 UTC). Priority Zero completed. This run stops at MCP verification; Fase 02 was not resumed.

## Confirmed environment

| Component | Working value |
| --- | --- |
| Unity project | `D:\sergi\Documents\Simulador-predial\FacilityOps` |
| Unity Editor | `6000.6.2f1` |
| Editor executable | `C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe` |
| MCP plugin/server | MCPForUnity `10.2.0` |
| Original plugin repository | `D:\ProjectResort_Autonomy\unity-mcp-v10.2.0` |
| Imported local plugin | `FacilityOps\Assets\MCPForUnity` |
| MCP endpoint for Codex | `http://127.0.0.1:8080/mcp` |
| HTTP base URL in Unity | `http://127.0.0.1:8080` |
| Unity transport selection | `HTTP Local` |
| Verified instance | `FacilityOps@80d9f59950304178` |
| Manual UPM server IPC | `Unity-Upm-33107` |
| Editor IPC argument | `-upmIpcPath Upm-33107` |

## Cause and fix

The plugin's own `package.json` declares `com.unity.nuget.newtonsoft-json@3.0.2`. Copying it into `Assets` does not make that JSON a UPM package manifest, so its dependencies were not installed automatically. `MCPForUnity.Runtime` uses Newtonsoft types in `Serialization/UnityTypeConverters.cs`, but its assembly had no explicit Newtonsoft reference. The Editor assembly's reference does not propagate to Runtime. The DLL inside the Unity installation is not a substitute for installing the project dependency.

Changes made:

1. In `FacilityOps/Assets/MCPForUnity/Runtime/MCPForUnity.Runtime.asmdef`, set `overrideReferences` to `true` and `precompiledReferences` to `["Newtonsoft.Json.dll"]`. The rest of this assembly definition is preserved.
2. Installed the official registry package through Unity's Package Manager: **Window → Package Management → Package Manager → + → Install package by technical name**, name `com.unity.nuget.newtonsoft-json`, version `3.0.2`.
3. Unity updated `Packages/manifest.json` and `Packages/packages-lock.json`. Their Git diffs contain only the new Newtonsoft dependency; existing package versions remain unchanged.

No DLL was copied from the Editor installation or another project. The compiler response file confirms the actual reference:

```text
-r:"Library/PackageCache/com.unity.nuget.newtonsoft-json@eebc3d041427/Runtime/Newtonsoft.Json.dll"
```

The initial Editor was paused at **Enter Safe Mode?**. Entering Safe Mode allowed recovery. During dependency resolution, UPM reported access denied writing `Packages/packages-lock.json`, although normal read/write access and the visible ACL were valid. The original lock file was moved to `D:\ProjectResort_Autonomy\logs\packages-lock.before-mcp-recovery.json`, then recreated at the original path with identical bytes. Both copies had SHA256 `F1FD6C735AEB101CB30FEE75D4139ED0DB08DA704C87F6CE37CFD22B95C80356` before UPM updated it. A retry then resolved and registered the package successfully. The underlying reason for that access-denied result was not conclusively identified; no broad ACL change or project cleanup was used.

## Start or recover the services

Do not launch duplicates if the existing server and Editor are already running.

The existing MCP server was kept running throughout the fix. Its command is:

```powershell
uvx --from 'git+https://github.com/CoplayDev/unity-mcp@v10.2.0#subdirectory=Server' mcp-for-unity --transport http --http-host 127.0.0.1 --http-port 8080 --project-scoped-tools
```

Automatic UPM spawning remains an environment issue. Use the existing manual launcher, which was inspected and used successfully:

```powershell
Start-Process -FilePath 'C:\Windows\System32\cmd.exe' -ArgumentList '/c "D:\ProjectResort_Autonomy\start_upm_mcp.cmd"' -WindowStyle Hidden
```

It starts:

```text
"C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Data\Resources\PackageManager\Server\UnityPackageManager.exe" server --ipc-path Unity-Upm-33107 -l 2 --log-file "D:\ProjectResort_Autonomy\logs\upm_mcp.log"
```

The launcher supplies the Windows environment expected by UPM. A direct launch from this terminal failed because `PROGRAMDATA` and `ALLUSERSPROFILE` were absent, with `getLocalConfigFolder` / `ERR_INVALID_ARG_TYPE`. The existing launcher succeeded. Wait for `IPC server started (IPC path=Unity-Upm-33107)` in the UPM log before launching the Editor:

```powershell
Start-Process -FilePath 'C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe' -ArgumentList '-projectPath "D:\sergi\Documents\Simulador-predial\FacilityOps" -upmIpcPath Upm-33107' -WindowStyle Hidden
```

In Unity, open **MCP for Unity** with `Ctrl+Shift+M`. Select `HTTP Local`, confirm base URL `http://127.0.0.1:8080`, and click **Connect**. The running server is already available; configuring all clients is unnecessary for this connection.

Codex's existing configuration was left unchanged, including its other MCP entries:

```toml
[mcp_servers.unityMCP]
url = "http://127.0.0.1:8080/mcp"
```

`unity status` from the separate Unity CLI checks the Pipeline package, which this project does not have. Its empty result is not a test of MCPForUnity. Do not install Pipeline solely to test this MCP connection.

## Verification results

`FacilityOps/Logs/Editor.log` reported `*** Tundra build success (24.25 seconds), 430 items updated, 1030 evaluated`. Both `Library/ScriptAssemblies/MCPForUnity.Runtime.dll` and `MCPForUnity.Editor.dll` were generated. The final Editor log contains no `error CS` entries.

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/instances | ConvertTo-Json -Depth 8
```

Returned:

```json
{
  "success": true,
  "instances": [{
    "session_id": "cc0eb895-f7df-4c25-bb56-be061f92776b",
    "project": "FacilityOps",
    "hash": "80d9f59950304178",
    "unity_version": "6000.6.2f1",
    "connected_at": "2026-10-07T12:43:11.167654+00:00"
  }]
}
```

The following calls were executed through the actual Codex `unityMCP` connector, not just a separate HTTP test:

| Call | Verified response |
| --- | --- |
| Resource `mcpforunity://custom-tools` | Success, 35 project tools registered |
| Resource `mcpforunity://instances` | One instance, `FacilityOps@80d9f59950304178` |
| `set_active_instance(instance="FacilityOps@80d9f59950304178")` | Success |
| Resource `mcpforunity://project/info` | Correct FacilityOps path and Unity version |
| `manage_scene(action="get_hierarchy", page_size=10, max_depth=1)` | Success, two root objects: `Main Camera`, `Directional Light` |
| `read_console(action="get", types=["error"], count=30, format="json")` | Success, `Retrieved 0 log entries`, `data: []` |
| `read_console` for logs/warnings | Success, returned compiler compatibility warnings |

The Editor opened its existing unsaved default scene for this check. No gameplay scene was created, loaded, edited, or saved by this run. No Play Mode or gameplay work was performed. Console read was the harmless additional MCP tool; an MCP screenshot was not needed.

The `editor/state` resource returned `is_compiling=false` and no pending domain reload, but its cached snapshot also reported `stale_status` / `ready_for_tools=false`. Do not present that cached readiness flag as a fresh health proof. The live hierarchy, project-info and console calls succeeded. MCPForUnity still emits Unity 6.6 analyzer warnings (`UAC0005`, `UAC0020`, `UAC0007`); zero compile errors does not mean zero warnings.

Machine-readable connector responses are preserved in [UNITY_MCP_CODEX_PROOF_2026-10-07.json](UNITY_MCP_CODEX_PROOF_2026-10-07.json). Project logs are under `FacilityOps/Logs`; UPM logs and the original lock backup are under `D:\ProjectResort_Autonomy\logs`.

## Scope boundary

Priority Zero is proven. The local plugin, dependency metadata and this documentation are the only intentional project changes made for this task. Existing unrelated modifications were preserved; no reset, clean, revert, asset authoring or Fase 02 implementation was performed. Leave the connected Editor, manual UPM and MCP server running for subsequent authorized work.


## Live re-verification during urban continuation

MCPForUnity v10.2.0 is already installed and connected to FacilityOps. Live execution and the full 30/30 PlayMode suite succeeded on 2026-10-07 at approximately 18:50 local. No MCP configuration was changed; the complete config hash before and after is identical. Other configured servers remain intact. [Fresh proof](UNITY_MCP_CODEX_REVERIFICATION_2026-10-07.json). Gameplay execution here belongs to the later authorized visual continuation, not the historical setup scope above.
