Shader "ResortAurora/CoastalSand"
{
 Properties
 {
  _DryColor("Dry scanned albedo",2D)="white"{} _DryNormal("Dry normal",2D)="bump"{}
  _DryRough("Dry roughness",2D)="white"{} _DryAO("Dry AO",2D)="white"{}
  _WetColor("Wet scanned albedo",2D)="white"{} _WetNormal("Wet normal",2D)="bump"{}
  _WetRough("Wet roughness",2D)="white"{} _WetAO("Wet AO",2D)="white"{}
  _DryMetres("Dry scan metres",Float)=2 _WetMetres("Wet scan metres",Float)=2
  _BaseMap("Depth pass base",2D)="white"{} _BaseColor("Depth color",Color)=(1,1,1,1) _Cutoff("Cutoff",Float)=0
 }
 SubShader
 {
  Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry+5" }
  Pass
  {
   Tags { "LightMode"="UniversalForward" }
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma target 3.5
   #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
   #pragma multi_compile_fragment _ _SHADOWS_SOFT
   #pragma multi_compile_fog
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   TEXTURE2D(_DryColor); SAMPLER(sampler_DryColor); TEXTURE2D(_DryNormal); SAMPLER(sampler_DryNormal);
   TEXTURE2D(_DryRough); SAMPLER(sampler_DryRough); TEXTURE2D(_DryAO); SAMPLER(sampler_DryAO);
   TEXTURE2D(_WetColor); SAMPLER(sampler_WetColor); TEXTURE2D(_WetNormal); SAMPLER(sampler_WetNormal);
   TEXTURE2D(_WetRough); SAMPLER(sampler_WetRough); TEXTURE2D(_WetAO); SAMPLER(sampler_WetAO);
   CBUFFER_START(UnityPerMaterial)
    float _DryMetres,_WetMetres; float4 _BaseColor; float4 _BaseMap_ST; float _Cutoff;
   CBUFFER_END
   struct A { float4 p:POSITION; float3 n:NORMAL; float4 t:TANGENT; float2 uv:TEXCOORD0; float2 mask:TEXCOORD1; };
   struct V { float4 p:SV_POSITION; float3 ws:TEXCOORD0; float3 n:TEXCOORD1; float4 t:TEXCOORD2; float2 uv:TEXCOORD3; float2 mask:TEXCOORD4; float fog:TEXCOORD5; };
   V vert(A a) { V o; VertexPositionInputs p=GetVertexPositionInputs(a.p.xyz); o.p=p.positionCS; o.ws=p.positionWS;
    o.n=TransformObjectToWorldNormal(a.n); o.t=float4(TransformObjectToWorldDir(a.t.xyz),a.t.w*GetOddNegativeScale());
    o.uv=a.uv; o.mask=a.mask; o.fog=ComputeFogFactor(o.p.z); return o; }
   float2 hash(float2 p) { return frac(sin(float2(dot(p,float2(127.1,311.7)),dot(p,float2(269.5,183.3))))*43758.5453); }
   // Three translated scan samples with triangular barycentric weights break obvious
   // repeated landmarks without rotating the tangent-space normal incorrectly.
   float4 scan(TEXTURE2D_PARAM(tex,samp),float2 uv)
   {
    float2 q=uv*.57735; float2 id=floor(q), f=frac(q); bool upper=f.x+f.y>1;
    float2 a=id+(upper?float2(1,1):float2(0,0)); float2 b=id+float2(1,0),c=id+float2(0,1);
    float3 w=upper?float3(f.x+f.y-1,1-f.y,1-f.x):float3(1-f.x-f.y,f.x,f.y);
    w=pow(max(w,0),3); w/=max(dot(w,1),.0001);
    float2 ddxUV=ddx(uv),ddyUV=ddy(uv);
    return SAMPLE_TEXTURE2D_GRAD(tex,samp,uv+hash(a)*11,ddxUV,ddyUV)*w.x+
     SAMPLE_TEXTURE2D_GRAD(tex,samp,uv+hash(b)*11,ddxUV,ddyUV)*w.y+
     SAMPLE_TEXTURE2D_GRAD(tex,samp,uv+hash(c)*11,ddxUV,ddyUV)*w.z;
   }
   half4 frag(V i):SV_Target
   {
    float wet=1-smoothstep(2.5,11,i.mask.x+.55*sin(i.uv.x*.19));
    float2 dryUV=i.uv/max(.1,_DryMetres),wetUV=i.uv/max(.1,_WetMetres);
    half3 dry=scan(TEXTURE2D_ARGS(_DryColor,sampler_DryColor),dryUV).rgb;
    half3 damp=scan(TEXTURE2D_ARGS(_WetColor,sampler_WetColor),wetUV).rgb;
    half3 nd=UnpackNormalScale(scan(TEXTURE2D_ARGS(_DryNormal,sampler_DryNormal),dryUV),.55);
    half3 nw=UnpackNormalScale(scan(TEXTURE2D_ARGS(_WetNormal,sampler_WetNormal),wetUV),.23);
    half rough=lerp(scan(TEXTURE2D_ARGS(_DryRough,sampler_DryRough),dryUV).r,
     scan(TEXTURE2D_ARGS(_WetRough,sampler_WetRough),wetUV).r,wet);
    half ao=lerp(scan(TEXTURE2D_ARGS(_DryAO,sampler_DryAO),dryUV).r,scan(TEXTURE2D_ARGS(_WetAO,sampler_WetAO),wetUV).r,wet);
    SurfaceData s=(SurfaceData)0;
    // Keep scanned grain but lift the beige dry sand into a daylight beach palette.
    // Old damp*.79 plus unavailable ambient SH turned the beach near-black.
    half3 dryBeige=saturate(dry*1.24+half3(.23,.16,.075));
    half3 wetBeige=saturate(damp*1.08+half3(.17,.10,.042));
    s.albedo=lerp(dryBeige,wetBeige,wet); s.metallic=0; s.specular=.04;
    s.smoothness=lerp(1-clamp(rough,.75,.98),.32*(1-rough)+.16,wet);
    s.normalTS=normalize(lerp(nd,nw,wet)); s.occlusion=lerp(1,ao,.4); s.alpha=1;
    InputData d=(InputData)0; d.positionWS=i.ws;
    half3 n=normalize(i.n),t=normalize(i.t.xyz),b=cross(n,t)*i.t.w;
    d.normalWS=normalize(mul(s.normalTS,half3x3(t,b,n))); d.viewDirectionWS=GetWorldSpaceNormalizeViewDir(i.ws);
    d.shadowCoord=TransformWorldToShadowCoord(i.ws); d.bakedGI=SampleSH(d.normalWS);
    d.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(i.p); d.shadowMask=1;
    half4 color=UniversalFragmentPBR(d,s);
    // Dynamic sky/solar fill safeguards against missing light-probe ambient
    // in batch and standalone. Falls dark naturally when the sun sets.
    Light sun=GetMainLight(d.shadowCoord);
    half diffuseSun=saturate(sun.direction.y);
    half fill=(.08h+.68h*diffuseSun);
    color.rgb=max(color.rgb,s.albedo*fill);
    color.rgb=MixFog(color.rgb,i.fog); return color;
   }
   ENDHLSL
  }
  UsePass "Universal Render Pipeline/Lit/ShadowCaster"
  UsePass "Universal Render Pipeline/Lit/DepthOnly"
  UsePass "Universal Render Pipeline/Lit/DepthNormals"
 }
}
