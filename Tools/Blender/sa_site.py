"""Shared site loader for the Bairro das Palmeiras scenes (requires bpy): reads the exported ResortSite.json + heightfield and builds the
terrain (vertex-coloured, noise-broken), the sea and the vila massing. Used by the evolution-stage scenes.
"""
import json
import math
import struct
from pathlib import Path

import bpy

import sa_bl


class Site:
    def __init__(self, root):
        d = Path(root) / "FacilityOps" / "Assets" / "_Game" / "Resources" / "Resort"
        self.dir = d
        self.json = json.loads((d / "ResortSite.json").read_text(encoding="utf-8"))
        self.nx, self.nz, self.step = self.json["columns"], self.json["rows"], self.json["step"]
        self._cache = {}

    def heights(self, natural=False):
        key = "natural" if natural else "built"
        if key not in self._cache:
            name = "ResortSiteHeights_natural.bytes" if natural else "ResortSiteHeights.bytes"
            raw = (self.dir / name).read_bytes()
            self._cache[key] = struct.unpack("<%df" % (self.nx * self.nz), raw)
        return self._cache[key]

    def height_at(self, x, y, natural=False):
        H, nx, nz, st = self.heights(natural), self.nx, self.nz, self.step
        fx, fy = max(0.0, min(x / st, nx - 1.001)), max(0.0, min(y / st, nz - 1.001))
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        a, b, c, d = H[j * nx + i], H[j * nx + i + 1], H[(j + 1) * nx + i], H[(j + 1) * nx + i + 1]
        return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty

    def prom_z(self, x):
        p = self.json["promenade"]
        if x <= p[0]["x"]:
            return p[0]["z"]
        for k in range(1, len(p)):
            if x <= p[k]["x"]:
                t = (x - p[k - 1]["x"]) / max(1e-6, p[k]["x"] - p[k - 1]["x"])
                return p[k - 1]["z"] + t * (p[k]["z"] - p[k - 1]["z"])
        return p[-1]["z"]

    def parcel(self, pid):
        return next(p for p in self.json["parcels"] if p["id"] == pid)

    def terrain_object(self, name, natural, coll):
        s, H, nx, nz, step = self.json, self.heights(natural), self.nx, self.nz, self.step
        verts, cols = [], []
        for j in range(nz):
            for i in range(nx):
                x, y, z = i * step, j * step, H[j * nx + i]
                verts.append((x, y, z))
                if abs(y - self.prom_z(x)) < 6:
                    c = (.62, .60, .55)
                elif abs(y - s["avenue"]["z"]) < s["avenue"]["width"] / 2 or any(abs(y - e["z"]) < e["width"] / 2 for e in s["streetsEW"]) \
                        or any(e["from"] <= y <= e["to"] and abs(x - e["x"]) < e["width"] / 2 for e in s["streetsNS"]):
                    c = (.09, .09, .10)
                elif z < 0.5:
                    t = max(0.0, min(1.0, (z + 1.0) / 1.5))
                    c = (.38 + .26 * t, .31 + .22 * t, .21 + .16 * t)
                elif z < 3.2:
                    c = (.64, .54, .38)
                else:
                    t = max(0.0, min(1.0, (z - 3.2) / 2.5))
                    n = (math.sin(x * .13) * math.cos(y * .11)) * .03
                    c = (.62 - .40 * t + n, .54 - .22 * t + n, .38 - .27 * t + n)
                cols.append(c)
        faces = [(j * nx + i, j * nx + i + 1, j * nx + i + nx + 1, j * nx + i + nx) for j in range(nz - 1) for i in range(nx - 1)]
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.update()
        me.shade_smooth()
        ca = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
        for k, c in enumerate(cols):
            ca.data[k].color = (c[0], c[1], c[2], 1.0)
        mat = bpy.data.materials.get("terreno_cores")
        if mat is None:
            mat = bpy.data.materials.new("terreno_cores")
            nt = mat.node_tree
            bsdf = nt.nodes["Principled BSDF"]
            attr = nt.nodes.new("ShaderNodeVertexColor")
            attr.layer_name = "Col"
            noise = nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 0.35
            noise.inputs["Detail"].default_value = 6.0
            rng = nt.nodes.new("ShaderNodeMapRange")
            rng.inputs["To Min"].default_value = 0.78
            rng.inputs["To Max"].default_value = 1.18
            nt.links.new(noise.outputs["Fac"], rng.inputs["Value"])
            grey = nt.nodes.new("ShaderNodeCombineColor")
            for ch in ("Red", "Green", "Blue"):
                nt.links.new(rng.outputs["Result"], grey.inputs[ch])
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            nt.links.new(attr.outputs["Color"], mix.inputs["A"])
            nt.links.new(grey.outputs["Color"], mix.inputs["B"])
            nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
            bsdf.inputs["Roughness"].default_value = 0.92
        me.materials.append(mat)
        o = bpy.data.objects.new(name, me)
        coll.objects.link(o)
        return o

    def sea(self, lib, coll):
        sea = bpy.data.objects.new("Mar", bpy.data.meshes.new("Mar"))
        sea.data.from_pydata([(-1500, -900, 0), (2500, -900, 0), (2500, 80, 0), (-1500, 80, 0)], [], [(0, 1, 2, 3)])
        sea.data.materials.append(lib["agua_mar"])
        coll.objects.link(sea)

    def vila(self, lib, coll):
        mbv = sa_bl.MeshBuilder()
        for l in self.json["lots"]:
            z0 = min(self.height_at(l["x"] - l["w"] / 2, l["z"], True), self.height_at(l["x"] + l["w"] / 2, l["z"], True)) - 0.8
            mbv.box(l["x"], l["z"], z0, l["w"], l["d"], l["h"] + 0.8, [0, 1, 2, 3][l["c"] % 4], math.radians(l["rot"]))
            mbv.box(l["x"], l["z"], z0 + l["h"] + 0.8, l["w"] + .5, l["d"] + .5, .35, 4, math.radians(l["rot"]))
        vm = [lib["reboco_pintado"], lib["concreto_pintado"], lib["reboco_antigo"], lib["reboco_pastilha"], lib["ceramica_telha"]]
        return mbv.to_object("Vila", vm, coll)
