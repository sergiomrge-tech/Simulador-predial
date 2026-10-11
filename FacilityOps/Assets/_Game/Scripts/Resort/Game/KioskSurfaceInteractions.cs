using UnityEngine;
namespace ResortAurora.Game
{
    /// <summary>Maps a hit on the authored kitchen surface to its existing interaction proxy.</summary>
    public sealed class KioskSurfaceInteractions : MonoBehaviour
    {
        Interactable[] stations;
        public void Init(Transform root) => stations = root.GetComponentsInChildren<Interactable>(true);
        public Interactable Resolve(Vector3 point)
        {
            Interactable result=null;float nearest=.24f*.24f;
            if(stations==null)return null;
            foreach(var station in stations)
            {
                if(station==null||!station.gameObject.activeInHierarchy)continue;
                var collider=station.GetComponent<Collider>();if(collider==null||!collider.enabled)continue;
                float d=(collider.ClosestPoint(point)-point).sqrMagnitude;
                if(d<=nearest){nearest=d;result=station;}
            }
            return result;
        }
    }
    /// <summary>Live information on the staff-facing terminal, using existing service data.</summary>
    public sealed class KioskTerminalDisplay : MonoBehaviour
    {
        public TextMesh display;
        ResortGame game;float nextRefresh;bool fitted;
        void Update()
        {
            if(Time.unscaledTime<nextRefresh)return;nextRefresh=Time.unscaledTime+.5f;
            if(game==null)game=FindAnyObjectByType<ResortGame>();
            if(game==null||game.Service==null||display==null)return;
            if(!fitted)
            {
                var b=display.GetComponent<Renderer>().bounds;
                if(b.size.x>0&&b.size.y>0){display.transform.localScale*=Mathf.Min(.29f/b.size.x,.14f/b.size.y);fitted=true;}
            }
            display.text="LANCHES DO MAR\n"+(game.ShopOpen?"ATENDIMENTO ABERTO":"ATENDIMENTO FECHADO")+"\nPEDIDOS NA FILA: "+game.Service.Queue.Count;
        }
    }
}
