# Arquitetura Técnica — Unity

## 1. Stack proposta

- **Unity 6 LTS**
- **C#**
- Render Pipeline: URP para equilíbrio entre qualidade e desempenho
- Input System novo
- TextMeshPro
- Addressables quando o conteúdo crescer
- ScriptableObjects para dados de conteúdo
- Save local versionado

## 2. Princípios

- arquitetura modular;
- dados separados de lógica;
- evitar lógica crítica diretamente em GameObjects de cenário;
- IDs persistentes para peças, ferramentas, falhas e missões;
- sistemas independentes comunicando por interfaces/eventos;
- testes unitários em regras econômicas e geração de falhas.

## 3. Estrutura de pastas sugerida

```text
Assets/
  _Game/
    Art/
    Audio/
    Data/
      Failures/
      Locations/
      Missions/
      Parts/
      Tools/
      Economy/
    Prefabs/
      Environment/
      Interactables/
      Tools/
      UI/
    Scenes/
      Bootstrap/
      Hub/
      Locations/
      Testbeds/
    Scripts/
      Core/
      Interaction/
      Diagnostics/
      BuildingSystems/
      Missions/
      Economy/
      Company/
      Inventory/
      Save/
      UI/
      AI/
    Tests/
```

## 4. Bootstrap

Criar cena `Bootstrap` responsável por:

- carregar serviços principais;
- save;
- configurações;
- áudio;
- localização;
- banco de dados;
- transição de cenas.

## 5. Serviços principais

- GameStateService
- SaveService
- SceneFlowService
- MissionService
- EconomyService
- InventoryService
- CompanyService
- ReputationService
- LocalizationService
- AudioService

## 6. Interface de interação

Criar interface genérica:

```csharp
public interface IInteractable
{
    bool CanInteract(PlayerContext context);
    InteractionPrompt GetPrompt(PlayerContext context);
    void Interact(PlayerContext context);
}
```

Não acoplar cada ferramenta diretamente a cada objeto.

## 7. Building System Graph

Cada prédio deve possuir uma representação lógica independente da malha visual.

Exemplo:

```text
BuildingSystemGraph
  ElectricalNetwork
  PlumbingNetwork
  HVACNetwork
  SafetyNetwork
```

Cada rede contém nós, conexões, estados e falhas.

O cenário visual apenas reflete esse estado.

## 8. FailureDefinition

ScriptableObject sugerido:

- persistentId;
- systemType;
- possibleSymptoms;
- evidenceRules;
- validLocations;
- requiredTools;
- compatibleParts;
- repairAction;
- verificationRule;
- difficulty;
- rewardModifier.

## 9. MissionDefinition

- persistentId;
- locationId;
- symptomSet;
- allowedFailures;
- timeProfile;
- clientProfile;
- rewardProfile;
- modifiers;
- unlockRules.

## 10. Estado de objeto técnico

Cada objeto técnico deve ter:

- estado visual;
- estado funcional;
- falha atual;
- integridade;
- energia/pressão/conectividade abstrata;
- interações disponíveis;
- registro de inspeção.

## 11. Ferramentas

Usar sistema baseado em tags/capabilities.

Exemplo:

`ToolCapability.MeasureElectrical`
`ToolCapability.DetectMoisture`
`ToolCapability.RemoveFastener`

A falha exige capacidades, não nomes específicos de objetos.

## 12. Save

Salvar apenas estado necessário:

- versão do save;
- dinheiro;
- reputação;
- XP;
- sede;
- ferramentas;
- estoque;
- funcionários;
- contratos;
- histórico de clientes;
- missões ativas;
- flags de tutorial/progressão.

Não serializar GameObjects inteiros.

## 13. Save versionado

Estrutura:

```text
SaveData v1
migrations/
  V1ToV2
  V2ToV3
```

Pensar nisso desde o início por causa de Early Access/updates.

## 14. UI

Recomendação:

- UI Toolkit ou uGUI conforme velocidade da equipe;
- HUD minimalista durante reparos;
- tablet como interface diegética para sistemas complexos;
- evitar cobrir a tela com widgets permanentes.

## 15. Performance

Metas iniciais:

- 1080p / 60 FPS em PC médio;
- limitar física contínua desnecessária;
- pooling para objetos repetidos;
- baked lighting quando possível;
- LODs em mapas maiores;
- Occlusion Culling onde fizer sentido.

## 16. IA

MVP:

- NPCs com rotas simples;
- técnicos contratados simulados fora de cena;
- sem navegação complexa desnecessária.

Depois:

- NavMesh para funcionários e ocupantes;
- reação básica a áreas interditadas.

## 17. Ferramentas internas importantes

Criar cedo:

- Failure Debugger;
- Mission Validator;
- Building Network Viewer;
- Economy Simulator;
- Save Inspector;
- Content ID Validator.

Isso reduz erros quando o conteúdo aumentar.

## 18. Steam

Planejar desde cedo:

- achievements;
- cloud save;
- rich presence opcional;
- controller support posterior;
- build branches para playtest/demo.

Não integrar Steamworks antes do vertical slice estar funcional, exceto se necessário para pipeline.
