# PROJECT RESORT — Auditoria de assets gratuitos (2026-10-07)

## Objetivo
Selecionar assets gratuitos que realmente elevem a Fase 02 sem descaracterizar o Resort, sem avançar a Fase 03 e sem substituir capturas reais por concept art.

## Biblioteca local verificada
Local: `D:\ProjectResort_AssetLibrary\UnityFree`

- Human Basic Motions FREE — APROVADO / JÁ INTEGRADO. Arquivos licenciados locais em `FacilityOps/Assets/_Game/ThirdParty/Resources/HBM`; usados em idle, caminhada, corrida e conversa para NPCs próximos/médios.
- Environment Pack: Free Forest Sample — NÃO USAR COMO PACOTE VISUAL DO RESORT. Pinheiros, cogumelos e linguagem de floresta estilizada não combinam com praia tropical. Pedras/grama podem ser avaliadas pontualmente, mas somente após comparação visual.
- Earth Mage — FORA DO ESCOPO do Resort.
- Fantasy Monster 3D Model 03 — FORA DO ESCOPO.
- FreeTrial 30 Monster Stylized Fantasy — FORA DO ESCOPO.
- Magic Effects FREE — FORA DO ESCOPO da Fase 02.

## Assets gratuitos Unity priorizados para aquisição
1. Low Poly Tropical Beach (Aquaset) — prioridade A. Unity 6000 + URP; 18 props de praia, incluindo palmeiras, cadeira, píer, prancha, guarda-sol, salva-vidas, bola e castelo de areia. Candidato direto para substituir blockouts da praia.
2. Coconut Palm Tree Pack (Baldinoboy) — prioridade A. Gratuito; candidato para diversidade de palmeiras, condicionado a teste URP/Unity 6.
3. Furniture Mega Pack - Free (dlgames) — prioridade B. Unity 6000 + URP; 1,7 GB. Usar seletivamente para interiores, evitando importar conteúdo desnecessário.
4. Human Crafting Animations FREE (Kevin Iglesias) — prioridade A para ampliar gestos humanos; avaliar clipes compatíveis com atividades do quiosque.
5. Lowpoly Art Deco Furniture — prioridade C; gratuito e URP, apenas se a linguagem visual combinar com interiores futuros.

## Regra de integração
- Importar em staging primeiro; nunca substituir em massa.
- Comparar escala, materiais, URP, draw calls e coerência visual.
- Só promover assets que superem o blockout atual.
- Manter fallback procedural para clones sem pacotes licenciados.
- Rodar PlayMode completo após qualquer integração de runtime.
- Captura de validação deve ser screenshot real da Unity.
- Fase 03 continua bloqueada por HUMAN_GATE_PENDING.

## Próxima ação
Adquirir/baixar primeiro Low Poly Tropical Beach + Human Crafting Animations FREE + Coconut Palm Tree Pack na conta Unity autorizada. Depois importar em staging e substituir somente os blockouts aprovados visualmente.
