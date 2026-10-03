using System;
using UnityEngine;

namespace FacilityOps
{
    [Serializable] public sealed class CampaignCatalog
    {
        public int schemaVersion;
        public string city;
        public DistrictData[] districts;
        public ChapterData[] chapters;
        public LocationData[] locations;
    }
    [Serializable] public sealed class DistrictData { public string id, name, description; public float x,z; }
    [Serializable] public sealed class ChapterData { public string id,name,beat; public int index; public string[] locationIds; }
    [Serializable] public sealed class LocationData
    {
        public string id,name,districtId,npc,lore;
        public int unlockChapter;
        public float x,z;
        public string[] systems;
        public FloorData[] floors;
    }
    [Serializable] public sealed class FloorData { public string id,name; public int index; public RoomData[] rooms; public RoomConnection[] connections; }
    [Serializable] public sealed class RoomData { public string id,name,hotspot; public float x,z,width,depth; public string[] systemIds; }
    [Serializable] public sealed class RoomConnection { public string from,to,type; }
    public sealed class LoreHotspot : MonoBehaviour, IInteractable
    {
        public string caption, note;
        public string GetPrompt(ToolMode tool) => "[E] Ler registro / " + caption;
        public void Interact(GameRuntime context) { context.Notify(note); }
    }
}
