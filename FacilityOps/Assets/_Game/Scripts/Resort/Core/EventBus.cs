using System;
using System.Collections.Generic;

namespace ResortAurora.Core
{
    /// <summary>Marker for all simulation events. Events are plain structs so publishing never allocates.</summary>
    public interface IGameEvent { }

    /// <summary>
    /// Minimal typed publish/subscribe bus. The simulation publishes; UI, audio and analytics subscribe, so none of them
    /// reference each other. Instance-based (not static) so it can be injected and replaced in tests.
    /// </summary>
    public interface IEventBus
    {
        void Subscribe<T>(Action<T> handler) where T : struct, IGameEvent;
        void Unsubscribe<T>(Action<T> handler) where T : struct, IGameEvent;
        void Publish<T>(in T evt) where T : struct, IGameEvent;
    }

    public sealed class EventBus : IEventBus
    {
        readonly Dictionary<Type, Delegate> handlers = new Dictionary<Type, Delegate>();

        public void Subscribe<T>(Action<T> handler) where T : struct, IGameEvent
        {
            var key = typeof(T);
            handlers[key] = handlers.TryGetValue(key, out var existing) ? Delegate.Combine(existing, handler) : handler;
        }

        public void Unsubscribe<T>(Action<T> handler) where T : struct, IGameEvent
        {
            var key = typeof(T);
            if (!handlers.TryGetValue(key, out var existing)) return;
            var next = Delegate.Remove(existing, handler);
            if (next == null) handlers.Remove(key); else handlers[key] = next;
        }

        public void Publish<T>(in T evt) where T : struct, IGameEvent
        {
            if (handlers.TryGetValue(typeof(T), out var d)) ((Action<T>)d)(evt);
        }
    }
}
