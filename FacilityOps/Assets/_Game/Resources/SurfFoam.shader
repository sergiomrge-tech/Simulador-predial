Shader "ResortAurora/SurfFoam"
{
    Properties { _Color("Foam tint",Color)=(1,1,1,0.6) }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent" }
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            CBUFFER_START(UnityPerMaterial)
            float4 _Color;
            CBUFFER_END
            struct A { float4 vertex:POSITION; float2 uv:TEXCOORD0; };
            struct V { float4 pos:SV_POSITION; float3 world:TEXCOORD0; float2 uv:TEXCOORD1; float fog:TEXCOORD2; };
            V Vert(A i) { V o; o.world=TransformObjectToWorld(i.vertex.xyz); o.pos=TransformWorldToHClip(o.world); o.uv=i.uv; o.fog=ComputeFogFactor(o.pos.z); return o; }
            float Hash(float2 p) { return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453); }
            float Noise(float2 p)
            {
                float2 q=floor(p), f=frac(p); f=f*f*(3-2*f);
                return lerp(lerp(Hash(q),Hash(q+float2(1,0)),f.x),lerp(Hash(q+float2(0,1)),Hash(q+1),f.x),f.y);
            }
            half4 Frag(V i):SV_Target
            {
                // Feather both ribbon edges and break crests into irregular
                // foam cells. Existing wave motion remains authoritative.
                float2 p=i.world.xz*1.8+float2(_Time.y*0.08,0);
                float n=Noise(p)*0.55+Noise(p*2.8)*0.3+Noise(p*7.1)*0.15;
                float edge=pow(saturate(sin(i.uv.y*3.14159265)),0.85);
                float breakup=smoothstep(0.30,0.68,n);
                float holes=smoothstep(0.18,0.42,Noise(p*13));
                float a=_Color.a*edge*breakup*holes*0.85;
                float3 col=MixFog(_Color.rgb,i.fog);
                return half4(col,a);
            }
            ENDHLSL
        }
    }
}
