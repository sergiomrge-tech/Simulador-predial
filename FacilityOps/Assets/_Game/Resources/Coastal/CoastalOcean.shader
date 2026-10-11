Shader "ResortAurora/CoastalOcean"
{
 Properties
 {
  _NormalA("Wind ripple spectrum 12m",2D)="bump"{} _NormalB("Cross ripple spectrum 7m",2D)="bump"{}
  _Absorption("Absorption per metre RGB",Vector)=(.29,.105,.065,0)
  _WaterColor("Scattering",Color)=(.025,.16,.205,1)
 }
 SubShader
 {
  Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent" }
  Pass
  {
   Tags { "LightMode"="UniversalForward" }
   // Scene colour provides physical shallow transmission; composite once, avoiding double blending.
   Blend One Zero ZWrite Off Cull Off
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma target 3.5
   #pragma multi_compile_fog
   #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
   #pragma multi_compile_fragment _ _SHADOWS_SOFT
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareOpaqueTexture.hlsl"
   TEXTURE2D(_NormalA); SAMPLER(sampler_NormalA); TEXTURE2D(_NormalB); SAMPLER(sampler_NormalB);
   CBUFFER_START(UnityPerMaterial)
    float4 _Absorption,_WaterColor;
   CBUFFER_END
   struct A { float4 p:POSITION; float2 uv:TEXCOORD0; float2 shore:TEXCOORD1; };
   struct V { float4 p:SV_POSITION; float3 ws:TEXCOORD0; float2 uv:TEXCOORD1; float2 shore:TEXCOORD2; float3 n:TEXCOORD3; float fog:TEXCOORD4; };
   V vert(A a)
   {
    V o; float t=_Time.y; float d=a.shore.x;
    float fade=smoothstep(-4,8,d); float offshore=smoothstep(18,80,d);
    // Gravity wave dispersion omega=sqrt(g*k), amplitudes sum <= 0.25 metres.
    float k1=.24,k2=.41; float phase1=dot(a.uv,float2(.18,.984))*k1-t*sqrt(9.81*k1);
    float phase2=dot(a.uv,float2(-.36,.933))*k2-t*sqrt(9.81*k2)+1.9;
    float amp1=lerp(.055,.16,offshore)*fade,amp2=lerp(.025,.065,offshore)*fade;
    a.p.y+=amp1*sin(phase1)+amp2*sin(phase2);
    float2 slope=amp1*k1*cos(phase1)*float2(.18,.984)+amp2*k2*cos(phase2)*float2(-.36,.933);
    o.n=TransformObjectToWorldNormal(normalize(float3(-slope.x,1,-slope.y)));
    VertexPositionInputs p=GetVertexPositionInputs(a.p.xyz); o.p=p.positionCS; o.ws=p.positionWS;
    o.uv=a.uv; o.shore=a.shore; o.fog=ComputeFogFactor(o.p.z); return o;
   }
   half4 frag(V i):SV_Target
   {
    float2 screen=GetNormalizedScreenSpaceUV(i.p);
    float raw=SampleSceneDepth(screen);
    float eye=LinearEyeDepth(raw,_ZBufferParams),waterEye=-TransformWorldToView(i.ws).z;
    float depth=max(0,eye-waterEye); float d=i.shore.x;
    half3 na=UnpackNormal(SAMPLE_TEXTURE2D(_NormalA,sampler_NormalA,i.uv/12+_Time.y*float2(.011,-.019)));
    half3 nb=UnpackNormal(SAMPLE_TEXTURE2D(_NormalB,sampler_NormalB,i.uv/7+_Time.y*float2(-.017,-.009)));
    half strength=lerp(.14,.43,smoothstep(0,28,d));
    half3 n=normalize(i.n+half3((na.x+nb.x)*strength,0,(na.y+nb.y)*strength));
    half3 view=GetWorldSpaceNormalizeViewDir(i.ws);
    float fresnel=.0204+.9796*pow(1-saturate(dot(n,view)),5);
    float2 refrUV=screen+n.xz*.007*saturate(depth*.5);
    // Reject offsets that sample foreground geometry (promenade, people, kiosk).
    float refrDepth=LinearEyeDepth(SampleSceneDepth(refrUV),_ZBufferParams);
    if(refrDepth<waterEye) refrUV=screen;
    half3 transmission=exp(-_Absorption.rgb*min(depth,80));
    Light light=GetMainLight(TransformWorldToShadowCoord(i.ws));
    half illumination=.45+.55*saturate(light.direction.y)*light.distanceAttenuation;
    half3 scatter=_WaterColor.rgb*illumination;
    half3 background=SampleSceneColor(refrUV);
    half3 body=background*transmission+scatter*(1-transmission);
    half3 reflected=GlossyEnvironmentReflection(reflect(-view,n),i.ws,.23,1,screen);
    half3 color=lerp(body,reflected,fresnel);
    // Moderate broad sun lobe; no plastic mirror highlight.
    half3 h=normalize(view+light.direction);
    float spec=pow(saturate(dot(n,h)),110)*.24;
    color+=spec*light.color*light.shadowAttenuation;
    // Breakers travel landward (decreasing seaward distance), not parallel to shoreline.
    float phase=d*.72+_Time.y*1.18+.18*sin(i.uv.x*.081);
    float pulse=pow(saturate(.5+.5*sin(phase)),10);
    float breakup=.55+.45*sin(i.uv.x*2.73+d*3.7+_Time.y*.63)*sin(i.uv.x*.67-d*4.1);
    float breaker=pulse*(1-smoothstep(2,19,d))*smoothstep(-1,2,d)*breakup;
    float contact=(1-smoothstep(.03,.38,depth))*(.55+.45*pulse);
    float foam=saturate(max(breaker*.7,contact*.5));
    color=lerp(color,half3(.76,.79,.77)*(.45+.55*illumination),foam);
    // Soft swash termination conforms to actual depth and the WaterlineZ strip.
    clip(d+5); float coverage=smoothstep(0,.10,depth)*smoothstep(-5,-1,d);
    color=lerp(background,color,coverage); color=MixFog(color,i.fog);
    return half4(color,1);
   }
   ENDHLSL
  }
 }
}
