Shader "ResortAurora/WorldSignText"
{
    Properties { _MainTex("Font atlas", 2D) = "white" {} _Color("Color", Color) = (1,1,1,1) }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent" }
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZTest LEqual
            ZWrite Off
            Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            CBUFFER_START(UnityPerMaterial)
            float4 _Color;
            CBUFFER_END
            struct A { float4 vertex:POSITION; float2 uv:TEXCOORD0; float4 color:COLOR; };
            struct V { float4 pos:SV_POSITION; float2 uv:TEXCOORD0; float4 color:COLOR; };
            V Vert(A i) { V o; o.pos=TransformObjectToHClip(i.vertex.xyz); o.uv=i.uv; o.color=i.color*_Color; return o; }
            half4 Frag(V i):SV_Target { return half4(i.color.rgb, i.color.a*SAMPLE_TEXTURE2D(_MainTex,sampler_MainTex,i.uv).a); }
            ENDHLSL
        }
    }
}
