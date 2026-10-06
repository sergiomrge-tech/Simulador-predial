using System.Collections.Generic;
using ResortAurora.Core;
using ResortAurora.Site;
using ResortAurora.Sim;
using UnityEngine;

namespace ResortAurora.Game
{
    /// <summary>
    /// Composition root and play-loop driver for the stall stage: builds the simulation objects, ticks them, spawns customer agents from the
    /// demand model, runs the end-of-day flow and saves. Scene objects only mirror the pure Sim state.
    /// </summary>
    public sealed class ResortGame : MonoBehaviour
    {
        [SerializeField] ResortSite site;
        [SerializeField] PlayerController player;
        [SerializeField] Light sun;
        [SerializeField, Tooltip("Local X of the stall along the promenade.")] float stallX = 160f;
        [SerializeField] int startingMoney = 150;

        public IEventBus Bus { get; private set; }
        public GameClock Clock { get; private set; }
        public Ledger Ledger { get; private set; }
        public StallModel Stall { get; private set; }
        public StaffRoster Roster { get; private set; }
        public StallService Service { get; private set; }
        public StallLayout Layout { get; private set; }
        public Weather Weather { get; private set; }
        public Panel OpenedPanel { get; private set; }
        public ResortSite Site => site;
        public int Seed { get; private set; }
        public int TotalServed { get; private set; }
        public DaySummary LastSummary { get; private set; }
        public string Toast { get; private set; }
        float toastUntil;

        readonly List<CustomerAgent> agents = new List<CustomerAgent>();
        readonly System.Random rng = new System.Random();
        float spawnAccumulator, ambientAccumulator;
        bool dayClosing;

        public sealed class DaySummary
        {
            public int day, revenue, expenses, served, lost, payroll, melted, balance;
            public float reputation; public Weather weather;
            public Dictionary<string, int> byCategory;
        }

        void Start()
        {
            Bus = new EventBus();
            Clock = new GameClock(Bus);
            Ledger = new Ledger(Bus, startingMoney);
            Stall = new StallModel();
            Roster = new StaffRoster(Bus);
            Service = new StallService(Bus, Stall, Ledger, Roster, () => Clock.Day);
            Seed = Random.Range(1, 99999);

            if (!site.Ready) site.Build();
            Layout = StallBuilder.Build(this, site, stallX);
            player.Bind(this);
            player.transform.position = Layout.PlayerSpawn;
            player.transform.rotation = Layout.Root.rotation;

            if (SaveStore.Exists()) Load(SaveStore.Read());
            Weather = DemandModel.WeatherFor(Seed, Clock.Day);
            Bus.Subscribe<CustomerServed>(e => TotalServed++);
            Bus.Subscribe<StaffChanged>(e => Layout.RefreshStaff(this));
            Layout.RefreshStaff(this);
            Say(SaveStore.Exists() ? "Jogo carregado. Bom dia!" : "Primeiro dia! Compre estoque na caixa e abra o dia.");
            SetCursor(false);
        }

        void Load(ResortSave s)
        {
            if (s == null) return;
            Seed = s.seed;
            Ledger.Restore(s.balance, s.transactions);
            Stall.Reputation = s.reputation;
            Stall.ImportStock(s.stock);
            foreach (var u in s.upgrades) Stall.Grant(u);
            Roster.Restore(s.staff);
            Clock.Restore(s.day, GameClock.DayStart);
            TotalServed = s.totalServed;
        }

        public void SaveNow()
        {
            var s = new ResortSave { seed = Seed, day = Clock.Day, balance = Ledger.Balance, reputation = Stall.Reputation, totalServed = TotalServed };
            s.stock = Stall.ExportStock();
            s.upgrades.AddRange(Stall.OwnedUpgrades);
            s.staff.AddRange(Roster.Hired);
            s.transactions.AddRange(Ledger.History);
            SaveStore.Write(s);
        }

        void Update()
        {
            float dt = Time.deltaTime;
            bool paused = OpenedPanel != Panel.None;
            if (!paused)
            {
                Clock.Tick(dt);
                Service.Tick(dt);
                SpawnCustomers(dt);
            }
            UpdateSun();
            if (Clock.DayOver && !dayClosing && Service.Queue.Count == 0 && Service.Tickets.Count == 0 && Service.Ready.Count == 0) CloseDay();
            if (OpenedPanel != Panel.None && UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.escapeKey.wasPressedThisFrame && OpenedPanel != Panel.Summary) ClosePanel();
            if (UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.f1Key.wasPressedThisFrame) OpenPanel(OpenedPanel == Panel.Help ? Panel.None : Panel.Help);
        }

        void SpawnCustomers(float dt)
        {
            float hourMinutes = dt / Clock.SecondsPerMinute;      // game minutes elapsed this frame
            float passers = DemandModel.Passersby(Clock.Hour, Weather);
            spawnAccumulator += passers * DemandModel.StopChance(Stall) * hourMinutes / 60f;
            while (spawnAccumulator >= 1f)
            {
                spawnAccumulator -= 1f;
                var product = DemandModel.Pick(Stall, Weather, rng);
                var data = Service.Arrive(product);
                SpawnAgent(data);
            }
            // Cosmetic passers-by that do not stop keep the promenade alive.
            ambientAccumulator += passers * 0.7f * hourMinutes / 60f;
            while (ambientAccumulator >= 1f && agents.Count < 40) { ambientAccumulator -= 1f; SpawnAgent(null); }
            ambientAccumulator = Mathf.Min(ambientAccumulator, 3f);
        }

        void SpawnAgent(Customer data)
        {
            bool fromWest = rng.NextDouble() < 0.5;
            var go = new GameObject(data != null ? "Customer" + data.Id : "Walker");
            var agent = go.AddComponent<CustomerAgent>();
            agent.Init(this, data, fromWest, (float)rng.NextDouble());
            agents.Add(agent);
        }

        public void ForgetAgent(CustomerAgent a) => agents.Remove(a);

        void CloseDay()
        {
            dayClosing = true;
            int day = Clock.Day;
            int payroll = Roster.DailyPayroll();
            Ledger.Add(day, "salarios", -payroll);
            int melted = Stall.MeltStock();
            var byCat = Ledger.DayByCategory(day);
            LastSummary = new DaySummary
            {
                day = day, revenue = Ledger.DayTotal(day, true), expenses = Ledger.DayTotal(day, false), served = Service.Served, lost = Service.Lost,
                payroll = payroll, melted = melted, balance = Ledger.Balance, reputation = Stall.Reputation, weather = Weather, byCategory = byCat,
            };
            SaveNow();
            OpenPanel(Panel.Summary);
        }

        public void StartNextDay()
        {
            dayClosing = false;
            Clock.StartNextDay();
            Service.ResetDay();
            Weather = DemandModel.WeatherFor(Seed, Clock.Day);
            spawnAccumulator = ambientAccumulator = 0f;
            ClosePanel(force: true);
            SaveNow();
            Say($"Dia {Clock.Day}: {WeatherInfo.Label(Weather)}. Boa sorte!");
        }

        public void OpenPanel(Panel p) { OpenedPanel = p; player.Frozen = p != Panel.None; SetCursor(p != Panel.None); }
        public void ClosePanel(bool force = false) { if (OpenedPanel == Panel.Summary && !force) return; OpenPanel(Panel.None); }
        static void SetCursor(bool free) { Cursor.lockState = free ? CursorLockMode.None : CursorLockMode.Locked; Cursor.visible = free; }

        public void Say(string text, float seconds = 4f) { Toast = text; toastUntil = Time.time + seconds; }
        public bool ToastActive => Time.time < toastUntil;

        void UpdateSun()
        {
            if (sun == null) return;
            float t = Mathf.InverseLerp(6f, 20f, Clock.Hours);               // 0 sunrise .. 1 sunset
            float elevation = Mathf.Sin(Mathf.Clamp01(t) * Mathf.PI) * 70f + 4f;
            sun.transform.rotation = Quaternion.Euler(elevation, 70f + t * 40f, 0f);
            float low = 1f - Mathf.Sin(Mathf.Clamp01(t) * Mathf.PI);
            sun.color = Color.Lerp(new Color(1f, 0.96f, 0.88f), new Color(1f, 0.62f, 0.38f), low);
            sun.intensity = Mathf.Lerp(1.15f, 0.45f, low * low);
            RenderSettings.ambientLight = Color.Lerp(new Color(0.55f, 0.62f, 0.72f), new Color(0.35f, 0.3f, 0.4f), low);
        }
    }
}
