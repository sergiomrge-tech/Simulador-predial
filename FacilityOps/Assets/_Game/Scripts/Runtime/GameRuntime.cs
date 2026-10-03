using System;
using System.IO;
using UnityEngine;

namespace FacilityOps
{
    public sealed class GameRuntime : MonoBehaviour
    {
        public static readonly string[] ToolNames = { "Inspeção visual", "Scanner de energia", "Sonda de sinal", "Kit de reparo", "Teste / confirmação", "Isolar circuito", "Restaurar circuito" };
        public static readonly string[] CauseNames = { "Módulo de alimentação", "Relé de comando", "Driver de iluminação" };
        public static readonly string[] HydraulicToolNames = { "Inspeção visual", "Medidor de pressão", "Sonda de vazão", "Kit hidráulico", "Teste / confirmação", "Fechar registro", "Abrir registro" };
        public ServiceSession Session { get; private set; }
        public FirstPersonController Player { get; private set; }
        public WorldBuilder World { get; private set; }
        public ToolMode Tool;
        public bool TabletOpen { get; private set; } = true;
        public bool AtOffice { get; private set; } = true;
        public bool IsSmokeTest { get; private set; }
        public string Notice { get; private set; } = "Bem-vindo à Oficina Aurora. Prepare peças e aceite seu primeiro chamado.";
        public string SavePath { get; private set; }
        public string SaveError { get; private set; }
        public string LastReport { get; private set; }
        public CampaignCatalog Campaign { get; private set; }
        public ServiceDefinition DisplayJob => Session.ActiveJob ?? (Session.Active==null && Session.Career.prologueCompleted
            ? Session.NextJob ?? (Session.FirstContractAvailable ? ChapterOne.FirstContract : null)
            : null);
        public string MissionTitle => DisplayJob?.title ?? (Session.IsPrologue || (Session.Active == null && !Session.Career.prologueCompleted) ? "PRÓLOGO / O primeiro chamado" : "Corredor às escuras / chamado livre");
        public string CauseName(int cause) => Session.ActiveJob?.causes[cause] ?? (Session.IsPrologue && cause == 2 ? "Isolamento da luminária" : CauseNames[cause]);
        public string ToolName => (Session.ActiveJob?.hydraulic==true ? HydraulicToolNames : ToolNames)[(int)Tool];
        public string ServiceLocationName => Session.ActiveJob==null ? "Edifício Horizonte" : Array.Find(Campaign.locations,place=>place.id==Session.ActiveJob.locationId).name;
        public string DisplayLocationName => DisplayJob==null ? "Edifício Horizonte" : Array.Find(Campaign.locations,place=>place.id==DisplayJob.locationId).name;
        public LocationData PreviewLocation { get; private set; }
        public int PreviewFloor { get; private set; }
        private AudioSource audioSource;
        private AudioClip click;
        private AudioClip success;
        private float noticeUntil;
        private float autosave;
        private bool canSave = true;

        private void Start()
        {
            string[] args = Environment.GetCommandLineArgs();
            IsSmokeTest = Array.IndexOf(args, "-facilitySmoke") >= 0;
            SavePath = IsSmokeTest ? Path.Combine(Application.dataPath, "..", "QA", "smoke-career.json") : SaveService.DefaultPath;
            CareerData data;
            try { data = IsSmokeTest ? new CareerData() : SaveService.Load(SavePath); }
            catch (Exception e) { data = new CareerData(); canSave = false; SaveError = e.Message; }
            Session = new ServiceSession(data);
            var catalog = Resources.Load<TextAsset>("World/campaign");
            if (catalog != null) Campaign = JsonUtility.FromJson<CampaignCatalog>(catalog.text);
            World = new WorldBuilder();
            var player = new GameObject("Técnico primeira pessoa"); Player = player.AddComponent<FirstPersonController>(); Player.Initialize(this);
            audioSource = gameObject.AddComponent<AudioSource>();
            click = Tone("Scanner", 740, .09f); success = Tone("Serviço concluído", 1040, .22f);
            LoadLocation(data.active == null);
            gameObject.AddComponent<TabletUI>().game = this;
            Application.targetFrameRate = 60;
            SetTablet(true);
            if (IsSmokeTest) gameObject.AddComponent<RuntimeSmoke>().game = this;
        }
        private AudioClip Tone(string title, float frequency, float duration)
        {
            const int rate = 22050;
            float[] samples = new float[(int)(rate * duration)];
            for (int i = 0; i < samples.Length; i++) samples[i] = Mathf.Sin(i * 2 * Mathf.PI * frequency / rate) * .12f * (1f - i / (float)samples.Length);
            var clip = AudioClip.Create(title, samples.Length, 1, rate, false); clip.SetData(samples, 0); return clip;
        }
        private void Update()
        {
            if (Session == null) return;
            if (!TabletOpen && !AtOffice && PreviewLocation == null && Session.Active != null)
            {
                Session.Active.elapsed += Time.deltaTime;
                string eventMessage = Session.Tick(Time.deltaTime);
                if (eventMessage != null) { World.ReflectService(Session); Notify(eventMessage); Save(); }
            }
            autosave += Time.unscaledDeltaTime;
            if (autosave > 30) { Save(); autosave = 0; }
        }
        public void SetTablet(bool open)
        {
            TabletOpen = open;
            Cursor.lockState = open || IsSmokeTest ? CursorLockMode.None : CursorLockMode.Locked;
            Cursor.visible = open || IsSmokeTest;
        }
        public void LoadLocation(bool office)
        {
            PreviewLocation = null;
            AtOffice = office;
            if (!office && Session.ActiveJob!=null)
            {
                var location=Array.Find(Campaign.locations,place=>place.id==Session.ActiveJob.locationId);
                World.CreateService(Session.ActiveJob,location,Session.Career);
                var entry=location.floors[0].rooms[0];
                Player.Teleport(new Vector3(entry.x,.1f,entry.z));
            }
            else { World.Create(office); Player.Teleport(new Vector3(0, .1f, office ? 4 : 2)); }
            if (!office) World.ReflectService(Session);
        }
        public void VisitPreview(LocationData location, int floor = 0)
        {
            PreviewLocation = location;
            PreviewFloor = Mathf.Clamp(floor, 0, location.floors.Length - 1);
            AtOffice = false;
            World.CreatePreview(location, PreviewFloor);
            if (PreviewFloor==0) World.ShowBuildingHistory(location,Session.Career);
            var entry = location.floors[PreviewFloor].rooms[0];
            Player.Teleport(new Vector3(entry.x, .1f, entry.z));
            SetTablet(false);
            Notify("PRÉVIA DE MAPA / " + location.name + " / " + location.floors[PreviewFloor].name + ". [TAB] Cidade para mudar pavimento ou voltar à sede.");
        }
        public void Accept()
        {
            bool accepted = !Session.Career.prologueCompleted
                ? Session.AcceptPrologue()
                : Session.NextJob!=null
                    ? Session.AcceptChapterOne(Session.NextJob.id)
                    : Session.FirstContractAvailable
                        ? Session.AcceptFirstContract()
                        : Session.Accept((FailureCause)((Session.Career.completed + DateTime.Now.Second) % 3));
            if (!accepted) return;
            LoadLocation(false); SetTablet(false); Save();
            Notify(Session.IsPrologue
                ? "Guto: disjuntor não desarma por vontade própria. Inspecione QD-01 e a luminária LM-01. Mensagens no tablet."
                : Session.IsFirstContract
                    ? "Primeira preventiva aceita. Compare entrada, bomba e reservatório antes de intervir."
                    : Session.ActiveJob!=null
                        ? Session.ActiveJob.symptom + " Consulte CHAMADO e DIAGNÓSTICO no tablet."
                        : "Chamado livre aceito. Inspecione QD-01, CT-01 e LM-01. [TAB] abre suas hipóteses.");
        }
        public void AcceptFree()
        {
            if (!Session.Career.prologueCompleted || !Session.Accept((FailureCause)((Session.Career.completed+DateTime.Now.Second)%3))) return;
            LoadLocation(false); SetTablet(false); Save(); Notify("Chamado livre aceito no Horizonte. A progressão autoral fica preservada.");
        }
        public void Resume() { LoadLocation(false); SetTablet(false); }
        public void ReturnToOffice() { LoadLocation(true); SetTablet(true); Save(); }
        public void UseStation(StationId node)
        {
            string message;
            if (Tool == ToolMode.Inspect) message = Session.Inspect(node);
            else if (Tool == ToolMode.Repair) message = Session.Repair(node);
            else if (Tool == ToolMode.Verify) message = Session.Verify(node);
            else if (Tool == ToolMode.Isolate) message = Session.Isolate(node);
            else if (Tool == ToolMode.Restore) message = Session.Restore(node);
            else message = Session.Measure(node, Tool);
            World.ReflectService(Session);
            Notify(message); Save();
        }
        public void Diagnose(FailureCause cause) { Notify(Session.Diagnose(cause)); Save(); }
        public void Buy(FailureCause cause)
        {
            if (!AtOffice) return;
            int debtBefore = Session.Career.supplierDebt;
            bool bought = Session.Buy(cause, AtOffice);
            Notify(bought ? (Session.Career.supplierDebt > debtBefore ? "Peça recebida a crédito. O fornecedor descontará a dívida no próximo pagamento." : "Peça adicionada ao estoque. R$ 60 debitados.") : "Compra disponível na sede."); Save();
        }
        public void BuySealKit()
        {
            if (!AtOffice)return;
            int debt=Session.Career.supplierDebt;
            bool bought=Session.BuySealKit(true);
            Notify(bought ? (Session.Career.supplierDebt>debt ? "Kit hidráulico recebido a crédito." : "Kit hidráulico adicionado. R$ 50 debitados.") : "Compra disponível na sede."); Save();
        }
        public void BuyPumpKit()
        {
            if (!AtOffice)return;
            int debt=Session.Career.supplierDebt;
            bool bought=Session.BuyPumpKit(true);
            Notify(bought ? (Session.Career.supplierDebt>debt ? "Kit preventivo de bomba recebido a crédito." : "Kit preventivo de bomba adicionado. R$ 120 debitados.") : "Compra disponível na sede."); Save();
        }
        public void Deliver()
        {
            bool prologue = Session.IsPrologue;
            bool firstContract = Session.IsFirstContract;
            string reportTitle = MissionTitle;
            bool contractBefore=Session.Career.recurringContractUnlocked;
            int mistakes = Session.Active?.mistakes ?? 0;
            float elapsed = Session.Active?.elapsed ?? 0;
            if (!Session.Settle(out int payment)) { Notify("Conclua o reparo e o teste integrado antes de entregar."); return; }
            LastReport = "SERVIÇO ENTREGUE\n\n" + reportTitle + "\nSistema restaurado e validado.\nPagamento: R$ " + payment + "\nPeças desperdiçadas: " + mistakes + "\nTempo em campo: " + TimeSpan.FromSeconds(elapsed).ToString(@"mm\:ss") + "\nExperiência: +100  •  Reputação: +" + (mistakes == 0 ? "5" : "1");
            LoadLocation(true); SetTablet(true); Save(); audioSource.PlayOneShot(success);
            Notify(firstContract
                ? "Primeira preventiva concluída. O condomínio entrou no histórico e o Capítulo II foi aberto."
                : !contractBefore && Session.Career.recurringContractUnlocked
                    ? "Helena indicou sua empresa ao primeiro contrato recorrente. Confira MENSAGENS."
                    : prologue
                        ? "Prólogo concluído. Primeiro serviço do Capítulo I disponível. Leia Guto e Helena em MENSAGENS."
                        : "Serviço entregue. Pagamento e histórico salvos. Você voltou à sede.");
        }
        public void Notify(string message) { Notice = message; noticeUntil = Time.unscaledTime + 10; if (audioSource) audioSource.PlayOneShot(click); }
        public bool ShowNotice => TabletOpen || Time.unscaledTime < noticeUntil;
        public void Save()
        {
            if (!canSave || Session == null) return;
            try { SaveService.Save(Session.Career, SavePath); SaveError = null; }
            catch (Exception e) { SaveError = "Falha ao salvar: " + e.Message; Debug.LogError(SaveError); }
        }
        private void OnApplicationQuit() { Save(); }
        private void OnApplicationFocus(bool focus) { if (!focus && Session != null) { SetTablet(true); Save(); } }
    }
}
