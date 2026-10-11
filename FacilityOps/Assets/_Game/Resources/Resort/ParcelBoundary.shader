Shader "ResortAurora/ParcelBoundary"
{
    Properties { _Color ("Boundary color", Color) = (0.85,0.85,0.65,0.80) }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Transparent" "Queue"="Transparent" }
        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            CBUFFER_START(UnityPerMaterial)
                float4 _Color;
            CBUFFER_END
            struct Attributes { float4 vertex:POSITION; };
            struct Varyings { float4 positionCS:SV_POSITION; };
            Varyings vert(Attributes v)
            {
                Varyings o;
                o.positionCS=TransformObjectToHClip(v.vertex.xyz);
                return o;
            }
            half4 frag(Varyings input):SV_Target { return _Color; }
            ENDHLSL
        }
    }
}
