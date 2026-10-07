Shader "ResortAurora/Sea"
{
    // Phase 02 sea: depth colour (vertex R = shallowness, G = opacity), analytic rolling ripples, Fresnel sky reflection, sun/moon glitter.
    // Everything it needs (ambient sky, fog, main light) is already driven by DayNightCycle, so the water follows the clock with no per-frame C#.
    Properties
    {
        _Deep("Deep water", Color) = (0.015, 0.16, 0.27, 1)
        _Shallow("Shallow water", Color) = (0.12, 0.60, 0.58, 1)
        _Ripple("Ripple strength", Range(0, 2)) = 1
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent-10" "RenderType"="Transparent" }
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite On
            Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
            float4 _Deep;
            float4 _Shallow;
            float _Ripple;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; float4 color : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 positionWS : TEXCOORD0; float4 color : COLOR; float fog : TEXCOORD1; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.color = input.color;
                o.fog = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            // slope contribution of one travelling ripple: direction, spatial frequency (rad/m), speed (rad/s), slope amplitude
            float2 Ripple(float2 p, float t, float2 dir, float freq, float speed, float slope)
            {
                float phase = dot(dir, p) * freq + speed * t;
                return dir * (slope * cos(phase));
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float3 P = i.positionWS;
                float3 toCam = _WorldSpaceCameraPos - P;
                float dist = length(toCam);
                float3 V = toCam / max(dist, 0.001);
                float t = _Time.y;

                // swell (long, calm) + chop (short, busier close to the camera)
                float2 g = Ripple(P.xz, t, float2(0.00, -1.00), 0.21, 0.95, 0.050)
                         + Ripple(P.xz, t, float2(0.55, -0.84), 0.37, 1.30, 0.045)
                         + Ripple(P.xz, t, float2(-0.62, -0.78), 0.63, 1.70, 0.040);
                float chop = saturate(1.0 - dist / 180.0);
                g += (Ripple(P.xz, t, float2(0.93, -0.36), 1.9, 2.6, 0.050)
                    + Ripple(P.xz, t, float2(-0.80, -0.60), 2.7, 3.1, 0.045)
                    + Ripple(P.xz, t, float2(0.20, -0.98), 4.3, 3.8, 0.030)) * chop;
                g *= _Ripple * lerp(1.0, 0.35, saturate(dist / 420.0));
                float3 N = normalize(float3(-g.x, 1.0, -g.y));

                float3 L = _MainLightPosition.xyz;
                float shallow = saturate(i.color.r);
                float3 lightCol = _MainLightColor.rgb;

                // body colour: deeper offshore, turquoise in the shallows, tinted by the ambient sky so it dims with the evening
                float3 amb = unity_AmbientSky.rgb;
                float3 body = lerp(_Deep.rgb, _Shallow.rgb, shallow);
                float3 lit = amb * 0.75 + lightCol * saturate(dot(N, L)) * 0.45;
                body *= lit;

                // sky reflection: Fresnel, brighter towards the horizon
                float nv = saturate(dot(N, V));
                float fres = 0.02 + 0.98 * pow(1.0 - nv, 5.0);
                float3 horizon = unity_FogColor.rgb;
                float3 refl = lerp(amb * 1.15, horizon, saturate(1.0 - V.y * 4.0));
                float3 col = lerp(body, refl, saturate(fres * lerp(1.0, 0.45, shallow)));

                // sun / moon glitter on the ripples
                float3 H = normalize(L + V);
                float nh = saturate(dot(N, H));
                float glint = pow(nh, 900.0) * 6.0 + pow(nh, 80.0) * 0.22;
                col += lightCol * glint * saturate(L.y * 6.0);

                col = MixFog(col, i.fog);
                return half4(col, i.color.g);
            }
            ENDHLSL
        }
    }
}
