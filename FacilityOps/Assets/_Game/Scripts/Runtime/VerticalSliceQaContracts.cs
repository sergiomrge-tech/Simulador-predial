using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;

namespace FacilityOps
{
    [Serializable] public sealed class VerticalSliceQaItem
    {
        public string id, status, detail; public Vector3 position;
        public VerticalSliceQaItem(string id, string status, string detail, Vector3 position = default)
        { this.id = id; this.status = status; this.detail = detail; this.position = position; }
    }
    [Serializable] public sealed class VerticalSliceMetric
    {
        public string status, value, unit;
        public static VerticalSliceMetric Unavailable(string unit) => new VerticalSliceMetric { status = "INDISPONÍVEL", value = null, unit = unit };
        public static VerticalSliceMetric Measured(double value, string unit) => new VerticalSliceMetric { status = "MEDIDO", value = value.ToString("F3", CultureInfo.InvariantCulture), unit = unit };
    }
    // Pure accumulator: no synthetic zero samples for an absent profiler counter.
    public sealed class VerticalSliceCounter
    {
        private double sum; private long count;
        public void Observe(bool valid, long value, bool requirePositive = false)
        {
            if (!valid || value < 0 || (requirePositive && value == 0)) return;
            sum += value; count++;
        }
        public VerticalSliceMetric Mean(string unit) => count == 0 ? VerticalSliceMetric.Unavailable(unit) : VerticalSliceMetric.Measured(sum / count, unit);
    }
    public static class VerticalSliceDeliveryGate
    {
        public static readonly string[] Required = { "compilation", "references", "cells", "spawn", "route", "streaming", "save_load", "player", "log" };
        public static bool Ready(IEnumerable<VerticalSliceQaItem> items)
        {
            var all = items.ToArray();
            if (all.Any(i => i.status == "FAIL")) return false;
            return Required.All(id => all.Count(i => i.id == id && i.status == "PASS") == 1);
        }
    }
    public static class VerticalSliceQaFlags
    {
        public static bool Has(string flag) => Array.IndexOf(Environment.GetCommandLineArgs(), flag) >= 0;
        public static string Value(string flag, string fallback = null)
        {
            string[] args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, flag);
            return i >= 0 && i + 1 < args.Length && !args[i + 1].StartsWith("-") ? args[i + 1] : fallback;
        }
        public static bool Overlay => (Application.isEditor || Debug.isDebugBuild) &&
            (Has("-verticalSliceQa") || Has("-verticalSliceQaOverlay") || Has("-worldSliceQa") || Has("-worldSliceQaWalk") || Has("-worldSliceQaTour"));
    }
}
