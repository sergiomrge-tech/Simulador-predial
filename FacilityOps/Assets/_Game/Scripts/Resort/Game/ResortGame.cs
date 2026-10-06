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
        public LodgingModel Lodging { get; private set; }
        public ResortStages Stages { get; private set; }
        public StallLayout Layout { get; private set; }
        public Weather Weather { get; private set; }
        public DayNightCycle DayNight { get; private set; }
        public BeachLife Life { get; private set; }
        public AmbientLife Ambient { get; private set; }
        public Panel OpenedPanel { get; private set; }
        public ResortSite Site => site;
        public int Seed { get; private set; }
        public int TotalServed { get; private set; }
        public DaySummary LastSummary { get; private set; }
        public string Toast { get; private set; }
        float toastUntil;

        readonly List<CustomerAgent> agents = new List<CustomerAgent>();
        readonly System.Random rng = new System.Random();
        float spawnAccumulator;
        bool dayClosing, closingRequested;

        /// <summary>The stall only gets customers while it is open (sign on the counter). Opening and closing are the player's decisions.</summary>
        public bool ShopOpen { get; private set; }
        /// <summary>The day is over and the player has to walk home and sleep (bed in the Apto 12) to start the next one.</summary>
        public bool AwaitingSleep { get; private set; }

        public sealed class DaySummary
        {
            public int day, revenue, expenses, served, lost, payroll, melted, balance;
            public NightReport lodging;
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
            Lodging = new LodgingModel(Bus);
            Service = new StallService(Bus, Stall, Ledger, Roster, () => Clock.Day);
            Seed = Random.Range(1, 99999);

            if (!site.Ready) site.Build();
            DayNight = new GameObject("DayNight").AddComponent<DayNightCycle>();
            DayNight.Init(this, sun);
            Layout = StallBuilder.Build(this, site, site.StallX);
            DayNight.BuildPromenadeLamps(site, site.StallX);
            player.Bind(this);

            Parcels = new ParcelBook(Bus);
            foreach (var p in site.Data.parcels)
                Parcels.Add(new ParcelInfo { Id = p.id, Name = p.name, Note = p.note, Price = p.price, LockTag = p.locked }, p.owned);
            new GameObject("ParcelMarkers").AddComponent<ParcelMarkers>().Init(this);

            Stages = new GameObject("ResortStages").AddComponent<ResortStages>();
            Stages.Init(site);
            Bus.Subscribe<ParcelBought>(e => { if (e.Id == "P2") UnlockLodging(true); RefreshStage(); });

            BuildHomeStations();
            bool hasSave = SaveStore.Exists();
            if (hasSave) Load(SaveStore.Read());
            // New game: wake up at the Santa Clara door and walk to work (the commute is part of the story). Otherwise start at the stall.
            PlaceAtHome();                                  // every day starts at the door of the Apto 12
            if (Parcels.Owns("P2")) UnlockLodging(false);
            RefreshStage();
            Weather = DemandModel.WeatherFor(Seed, Clock.Day);
            Bus.Subscribe<CustomerServed>(e => TotalServed++);
            Bus.Subscribe<StaffChanged>(e => Layout.RefreshStaff(this));
            Layout.RefreshStaff(this);
            Life = new GameObject("BeachLife").AddComponent<BeachLife>();
            Life.Init(this);
            Ambient = new GameObject("AmbientLife").AddComponent<AmbientLife>();
            Ambient.Init(this);
            Say(hasSave ? "Jogo carregado. Bom dia!" : "Primeiro dia! Siga para a barraca no calçadão, ao sul.", 7f);
            SetCursor(false);
        }

        /// <summary>The pousada exists once the sobrado parcel (P2) is owned: six simple rooms, room for two more helpers, a reception desk.</summary>
        void UnlockLodging(bool announce)
        {
            Lodging.Unlock();
            Roster.Capacity = Mathf.Max(Roster.Capacity, 4);
            EnsureLodgingDesk();
            if (announce) Say("A pousada abriu! Use a recepção (placa na frente do sobrado) para preços, quartos e avaliações.", 7f);
        }

        GameObject lodgingDesk;
        void EnsureLodgingDesk()
        {
            if (lodgingDesk != null) return;
            var p2 = System.Array.Find(site.Data.parcels, p => p.id == "P2");
            if (p2 == null) return;
            float x = p2.x + 19f, z = p2.z + 1.2f, y = site.HeightAt(x, z);
            lodgingDesk = new GameObject("LodgingDesk");
            lodgingDesk.transform.position = new Vector3(x, y, z);
            var board = StallBuilder.Box("Board", lodgingDesk.transform, new Vector3(0f, 1.2f, 0f), new Vector3(1.8f, 1.2f, 0.12f), new Color(0.2f, 0.35f, 0.5f));
            StallBuilder.Box("Post", lodgingDesk.transform, new Vector3(0f, 0.5f, 0f), new Vector3(0.14f, 1.0f, 0.14f), new Color(0.4f, 0.28f, 0.18f), collider: false);
            var st = board.AddComponent<PanelStation>(); st.panel = Panel.Lodging; st.label = "Recepção da Pousada";
            StallBuilder.Label(lodgingDesk.transform, new Vector3(0f, 2.3f, 0f), "POUSADA\nRecepção", 44, 0.09f);
        }

        /// <summary>Shows the physical stage that matches the land owned (RESORT_STAGE overrides it for captures and tests).</summary>
        public void RefreshStage()
        {
            var forced = System.Environment.GetEnvironmentVariable("RESORT_STAGE");
            int stage = int.TryParse(forced, out var f) ? Mathf.Clamp(f, 1, 7) : ResortStages.StageFor(Parcels);
            Stages.SetStage(stage);
            Layout.SetKioskLook(stage >= 2);
            Layout.RefreshUpgrades(this);
        }

        /// <summary>The bed of the Apto 12 (sleep to start the next day) and the building sign. The kitnet model itself is an exported stage piece.</summary>
        void BuildHomeStations()
        {
            var h = site.Data.home;
            float ox = h.x - h.width / 2f, oz = h.z - h.depth / 2f;           // frame origin of the kitnet (u east, d north)
            float y = site.HeightAt(ox + 9f, oz + 6f);
            var bed = new GameObject("HomeBed");
            bed.transform.position = new Vector3(ox + 9.2f, y + 0.5f, oz + 6.6f);
            bed.AddComponent<BoxCollider>().size = new Vector3(1.9f, 0.9f, 2.3f);
            var st = bed.AddComponent<ActionStation>();
            st.prompt = g => g.AwaitingSleep ? $"[E] Dormir e começar o dia {g.Clock.Day + 1}" : "Cama (só depois de encerrar o dia)";
            st.canUse = g => g.AwaitingSleep;
            st.action = g => g.SleepNow();
            var door = new Vector3(h.x, site.HeightAt(h.x, oz), oz);
            // porch lamp by the door and a warm light inside the kitnet (the home glows when the sun goes down)
            var porch = new GameObject("HomePorchLamp"); porch.transform.position = door + new Vector3(1.3f, 2.7f, -0.55f);
            DayNight.LampHead(porch.transform, Vector3.zero, 0.26f);
            DayNight.AddLamp(porch.transform.position + new Vector3(0f, -0.1f, -0.4f), 11f, 2.4f);
            DayNight.AddLamp(new Vector3(ox + 6.5f, y + 2.3f, oz + 4f), 10f, 1.7f, new Color(1f, 0.82f, 0.55f));
            StallBuilder.Label(new GameObject("HomeSign").transform, Vector3.zero, h.name + "\n" + h.unit, 44, 0.08f).transform.parent.position = door + new Vector3(0f, 3.9f, -0.6f);
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
            Clock.Restore(s.dayClosed ? s.day + 1 : s.day, GameClock.DayStart);
            TotalServed = s.totalServed;
            if (s.rooms != null && s.rooms.Count > 0) Lodging.Restore(s.rooms, s.reviews, s.totalGuests);
        }

        public void SaveNow(bool dayClosed = false)
        {
            var s = new ResortSave { seed = Seed, day = Clock.Day, dayClosed = dayClosed, balance = Ledger.Balance, reputation = Stall.Reputation, totalServed = TotalServed };
            s.stock = Stall.ExportStock();
            s.upgrades.AddRange(Stall.OwnedUpgrades);
            s.parcels.AddRange(Parcels.Owned);
            s.rooms.AddRange(Lodging.Rooms);
            s.reviews.AddRange(Lodging.Reviews);
            s.totalGuests = Lodging.TotalGuests;
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
                if (ShopOpen) SpawnCustomers(dt);
            }
            if ((Clock.DayOver || closingRequested) && !dayClosing && Service.Queue.Count == 0 && Service.Tickets.Count == 0 && Service.Ready.Count == 0) CloseDay();
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
        }

        void SpawnAgent(Customer data)
        {
            bool fromWest = rng.NextDouble() < 0.5;
            var go = new GameObject("Customer" + data.Id);
            var agent = go.AddComponent<CustomerAgent>();
            agent.Init(this, data, fromWest, (float)rng.NextDouble());
            agents.Add(agent);
        }

        public void ForgetAgent(CustomerAgent a) => agents.Remove(a);

        public void OpenShop()
        {
            if (ShopOpen || dayClosing || Clock.DayOver) return;
            ShopOpen = true;
            int stocked = 0; foreach (var p in Catalog.Products) stocked += Stall.Stock(p.Id);
            Say(stocked > 0 ? "Quiosque aberto!" : "Quiosque aberto, mas sem estoque! Compre na caixa do fornecedor.", 5f);
        }

        /// <summary>Stops new customers; the day closes (cash, payroll, save) as soon as the queue is served.</summary>
        public void RequestClose()
        {
            if (!ShopOpen) return;
            ShopOpen = false; closingRequested = true;
            Say("Fechando o caixa...");
        }

        public void SleepNow()
        {
            if (!AwaitingSleep) return;
            AwaitingSleep = false;
            StartNextDay();
        }

        public void GoHome()
        {
            ClosePanel(force: true);
            AwaitingSleep = true;
            Say("Dia encerrado e salvo. Volte para casa (Apto 12) e durma para começar o próximo dia.", 8f);
        }

        void CloseDay()
        {
            ShopOpen = false; closingRequested = false;
            dayClosing = true;
            int day = Clock.Day;
            int payroll = Roster.DailyPayroll();
            Ledger.Add(day, "salarios", -payroll);
            int melted = Stall.MeltStock();
            var night = Lodging.RunNight(day, Stall, Roster, Ledger, Weather, rng);
            var byCat = Ledger.DayByCategory(day);
            LastSummary = new DaySummary
            {
                day = day, revenue = Ledger.DayTotal(day, true), expenses = Ledger.DayTotal(day, false), served = Service.Served, lost = Service.Lost,
                payroll = payroll, melted = melted, lodging = night, balance = Ledger.Balance, reputation = Stall.Reputation, weather = Weather, byCategory = byCat,
            };
            SaveNow(dayClosed: true);
            OpenPanel(Panel.Summary);
        }

        public void StartNextDay()
        {
            dayClosing = false; closingRequested = false; ShopOpen = false; AwaitingSleep = false;
            Clock.StartNextDay();
            Service.ResetDay();
            Weather = DemandModel.WeatherFor(Seed, Clock.Day);
            spawnAccumulator = 0f;
            ClosePanel(force: true);
            PlaceAtHome();                                  // the next morning starts at the door of the Apto 12
            SaveNow();
            Say($"Dia {Clock.Day}: {WeatherInfo.Label(Weather)}. Boa sorte!");
        }

        public void OpenPanel(Panel p) { OpenedPanel = p; player.Frozen = p != Panel.None; SetCursor(p != Panel.None); }
        public void ClosePanel(bool force = false) { if (OpenedPanel == Panel.Summary && !force) return; OpenPanel(Panel.None); }
        static void SetCursor(bool free) { Cursor.lockState = free ? CursorLockMode.None : CursorLockMode.Locked; Cursor.visible = free; }

        public void Say(string text, float seconds = 4f) { Toast = text; toastUntil = Time.time + seconds; }
        public bool ToastActive => Time.time < toastUntil;

    }
}
