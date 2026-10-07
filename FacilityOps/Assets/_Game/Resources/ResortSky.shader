Shader "ResortAurora/Sky"
{
    // Phase 02 sky: a clock-driven gradient (zenith -> horizon) with a warm band on the sun's side, a sun disc and its glow.
    // DayNightCycle sets the colours every frame, so the horizon matches the fog and the sea at every hour (no yellow/olive dusk of the stock procedural sky).
    Properties
    {
        _Zenith("Zenith", Color) = (0.16, 0.38, 0.78, 1)
        _Horizon("Horizon", Color) = (0.70, 0.82, 0.93, 1)
        _Ground("Below horizon", Color) = (0.37, 0.35, 0.33, 1)
        _SunDir("Sun direction", Vector) = (0, 1, 0, 0)
        _SunColor("Sun colour", Color) = (1, 0.95, 0.85, 1)
        _Glow("Sun-side horizon glow", Color) = (0, 0, 0, 1)
        _SunDisc("Sun disc strength", Range(0, 1)) = 1
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" }
        Pass
        {
            ZWrite Off
            Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
            float4 _Zenith;
            float4 _Horizon;
            float4 _Ground;
            float4 _SunDir;
            float4 _SunColor;
            float4 _Glow;
            float _SunDisc;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dir : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.dir = input.positionOS.xyz;
                return o;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float3 d = normalize(i.dir);
                float3 S = normalize(_SunDir.xyz);
                float h = d.y;

                // gradient: the horizon colour hugs the horizon, the zenith takes over quickly overhead
                float up = saturate(h);
                float3 col = lerp(_Horizon.rgb, _Zenith.rgb, pow(up, 0.42));
                col = lerp(col, _Ground.rgb, saturate(-h * 6.0));

                // the glow: widest on the horizon on the sun's side, a tighter halo around the sun itself
                float2 hd = normalize(d.xz + 1e-5), hs = normalize(S.xz + 1e-5);
                float side = saturate(dot(hd, hs) * 0.5 + 0.5);
                float band = exp(-abs(h) * 5.5) * pow(side, 3.0);
                float cosS = saturate(dot(d, S));
                float halo = pow(cosS, 14.0) * 0.55 + pow(cosS, 220.0) * 1.2;
                col += _Glow.rgb * (band * 0.9 + halo);

                // sun disc (its colour is zero when the sun is under the horizon)
                float disc = smoothstep(0.99955, 0.99985, cosS) * step(0.0, S.y + 0.02) * step(-0.02, h);
                col += _SunColor.rgb * disc * 6.0 * _SunDisc;

                // 1/255 interleaved gradient noise against banding in the slow night gradient
                float n = frac(52.9829189 * frac(dot(i.positionCS.xy, float2(0.06711056, 0.00583715))));
                col += (n - 0.5) / 255.0;
                return half4(max(col, 0.0), 1.0);
            }
            ENDHLSL
        }
    }
    Fallback Off
}
