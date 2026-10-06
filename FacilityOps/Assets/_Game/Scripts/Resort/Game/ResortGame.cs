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
        [SerializeField] int startingMoney = 150;

        public IEventBus Bus { get; private set; }
        public GameClock Clock { get; private set; }
        public Ledger Ledger { get; private set; }
        public StallModel Stall { get; private set; }
        public StaffRoster Roster { get; private set; }
        public StallService Service { get; private set; }
        public ParcelBook Parcels { get; private set; }
        public ResortStages Stages { get; private set; }
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
            Layout = StallBuilder.Build(this, site, site.StallX);
            player.Bind(this);

            Parcels = new ParcelBook(Bus);
            foreach (var p in site.Data.parcels)
                Parcels.Add(new ParcelInfo { Id = p.id, Name = p.name, Note = p.note, Price = p.price, LockTag = p.locked }, p.owned);
            new GameObject("ParcelMarkers").AddComponent<ParcelMarkers>().Init(this);

            Stages = new GameObject("ResortStages").AddComponent<ResortStages>();
            Stages.Init(site);
            Bus.Subscribe<ParcelBought>(e => RefreshStage());

            bool hasSave = SaveStore.Exists();
            if (hasSave) Load(SaveStore.Read());
            // New game: wake up at the Santa Clara door and walk to work (the commute is part of the story). Otherwise start at the stall.
            if (hasSave) PlaceAtStall(); else PlaceAtHome();
            RefreshStage();
            Weather = DemandModel.WeatherFor(Seed, Clock.Day);
            Bus.Subscribe<CustomerServed>(e => TotalServed++);
            Bus.Subscribe<StaffChanged>(e => Layout.RefreshStaff(this));
            Layout.RefreshStaff(this);
            Say(hasSave ? "Jogo carregado. Bom dia!" : "Primeiro dia! Siga para a barraca no calçadão, ao sul.", 7f);
            SetCursor(false);
        }

        /// <summary>Shows the physical stage that matches the land owned (RESORT_STAGE overrides it for captures and tests).</summary>
        public void RefreshStage()
        {
            var forced = System.Environment.GetEnvironmentVariable("RESORT_STAGE");
            int stage = int.TryParse(forced, out var f) ? Mathf.Clamp(f, 1, 7) : ResortStages.StageFor(Parcels);
            Stages.SetStage(stage);
            Layout.SetKioskLook(stage >= 2);
        }

        void PlaceAtStall() => player.Teleport(Layout.PlayerSpawn, Layout.Root.rotation);
        void PlaceAtHome() => player.Teleport(site.HomeDoor + Vector3.up * 0.2f, Quaternion.Euler(0f, 180f, 0f));

        void Load(ResortSave s)
        {
            if (s == null) return;
            Parcels.Restore(s.parcels);
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
            s.parcels.AddRange(Parcels.Owned);
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
            PlaceAtStall();
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
            // tri-light ambient: sky / horizon / ground bounce, so shaded facades keep form and colour instead of flat grey-blue
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = Color.Lerp(new Color(0.60f, 0.72f, 0.90f), new Color(0.38f, 0.34f, 0.46f), low);
            RenderSettings.ambientEquatorColor = Color.Lerp(new Color(0.62f, 0.60f, 0.56f), new Color(0.34f, 0.28f, 0.28f), low);
            RenderSettings.ambientGroundColor = Color.Lerp(new Color(0.40f, 0.34f, 0.26f), new Color(0.18f, 0.14f, 0.12f), low);
        }
    }
}
