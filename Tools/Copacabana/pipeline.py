#!/usr/bin/env python3
"""Real OSM -> geographic GeoJSON + locally clipped 3D OBJ for Copacabana.

Requires: pyproj, shapely. No fake OSM fallback.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
import math
from pathlib import Path
import re
import shutil
import sys
import time
from urllib import parse, request
from xml.etree import ElementTree as ET

from pyproj import Transformer
from shapely.geometry import (
    LineString, Point, Polygon, box, mapping
)
from shapely.ops import transform, triangulate

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
REGION = ROOT / "region.json"
ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
)


class Frame:
    """Meters in EPSG:32723, local X along coast and Y toward inland."""

    def __init__(self, config=None):
        config = config or json.loads(REGION.read_text(encoding="utf-8"))
        self.config = config
        self.fwd = Transformer.from_crs("EPSG:4326", config["crs"], always_xy=True)
        self.back = Transformer.from_crs(config["crs"], "EPSG:4326", always_xy=True)
        ref_lon, ref_lat = config["avenue_reference_lonlat"]
        ax, ay = self.fwd.transform(ref_lon, ref_lat)
        angle = math.radians(config["axis_angle_degrees_counterclockwise_from_east"])
        self.c, self.s = math.cos(angle), math.sin(angle)
        shift = config["center_shift_inland_m"]
        self.cx = ax - self.s * shift
        self.cy = ay + self.c * shift
        self.length = config["along_coast_length_m"]
        self.width = config["inland_width_m"]
        self.roi = box(-self.length / 2, -self.width / 2,
                       self.length / 2, self.width / 2)

    def to_local(self, lon, lat):
        e, n = self.fwd.transform(lon, lat)
        dx, dy = e - self.cx, n - self.cy
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

    def to_lonlat(self, x, y):
        east = self.cx + x * self.c - y * self.s
        north = self.cy + x * self.s + y * self.c
        return self.back.transform(east, north)

    def bbox(self, padding_degrees=0.0004):
        corners = [self.to_lonlat(x, y) for x, y in self.roi.exterior.coords]
        west, east = min(c[0] for c in corners), max(c[0] for c in corners)
        south, north = min(c[1] for c in corners), max(c[1] for c in corners)
        return (south - padding_degrees, west - padding_degrees,
                north + padding_degrees, east + padding_degrees)

    def geodetic(self, geometry):
        return transform(self.to_lonlat, geometry)


def ql_query(bounds):
    b = ",".join(f"{v:.7f}" for v in bounds)
    # Only ways and mapped trees: avoids huge multipolygon relation recursions
    # that can crash public Overpass servers (or pull whole distant features).
    return ("[out:xml][timeout:90];\n("
            f'way["building"]({b});\n'
            f'way["highway"]({b});\n'
            f'way["natural"]({b});\n'
            f'way["landuse"]({b});\n'
            f'way["leisure"]({b});\n'
            f'way["waterway"]({b});\n'
            f'way["tourism"]({b});\n'
            f'way["man_made"]({b});\n'
            f'node["natural"="tree"]({b});\n'
            ");\n(._; >;);\nout body;\n")


def download(frame: Frame, output: Path):
    query = ql_query(frame.bbox())
    errors = []
    for endpoint in ENDPOINTS:
        try:
            # GET works on more public Overpass reverse proxies than POST.
            url = endpoint + "?" + parse.urlencode({"data": query})
            req = request.Request(url, headers={
                "User-Agent": "CopacabanaGISPrototype/1.0 (OSM research)",
                "Accept": "application/xml",
            })
            with request.urlopen(req, timeout=240) as resp:
                content = resp.read(65_000_000)
            if len(content) >= 65_000_000:
                raise RuntimeError("Resposta OSM muito grande; subdividir consulta")
            root = ET.fromstring(content)
            if root.tag != "osm" or len(root.findall("way")) < 20:
                raise ValueError("Resposta OSM vazia/incompleta, sem vias suficientes")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            print(f"REAL OSM downloaded from {endpoint}: {len(content):,} bytes")
            return endpoint
        except Exception as exc:
            detail = ""
            if hasattr(exc, "read"):
                try:
                    detail = " | server: " + exc.read(700).decode("utf-8", "replace")
                except Exception:
                    pass
            errors.append(f"{endpoint}: {type(exc).__name__}: {exc}{detail}")
            time.sleep(2)
    raise RuntimeError("Falha em TODOS os endpoints. Sem substituicao ficticia.\n" +
                       "\n".join(errors))


def tags(element):
    return {t.get("k"): t.get("v") for t in element.findall("tag")}


def nonempty_geometries(shape, kind):
    if shape.is_empty:
        return
    if shape.geom_type == kind:
        yield shape
    elif hasattr(shape, "geoms"):
        for sub in shape.geoms:
            yield from nonempty_geometries(sub, kind)


def parse_osm(input_file: Path, frame: Frame):
    root = ET.parse(input_file).getroot()
    if root.tag != "osm":
        raise ValueError("XML nao e documento OSM")
    nodes = {}
    for el in root.findall("node"):
        if el.get("lat") and el.get("lon"):
            nodes[el.get("id")] = frame.to_local(
                float(el.get("lon")), float(el.get("lat")))
    features = []
    dropped = Counter()
    for way in root.findall("way"):
        tg = tags(way)
        ids = [n.get("ref") for n in way.findall("nd")]
        if len(ids) < 2 or any(n not in nodes for n in ids):
            dropped["missing_nodes"] += 1
            continue
        xy = [nodes[n] for n in ids]
        ident = "way/" + (way.get("id") or "unknown")
        is_closed = len(xy) >= 4 and xy[0] == xy[-1]
        kind = None
        geom = None
        if tg.get("building") not in (None, "no") and is_closed:
            kind = "building"
        elif tg.get("highway"):
            kind = "road"
        elif tg.get("natural") == "coastline":
            kind = "coastline"
        elif tg.get("waterway"):
            kind = "waterway"
        elif is_closed and (
            tg.get("natural") in ("beach", "water", "wood", "scrub", "sand")
            or tg.get("landuse") or tg.get("leisure") or tg.get("tourism")
        ):
            kind = "land"
        if kind is None:
            continue
        try:
            geom = Polygon(xy) if kind in ("building", "land") else LineString(xy)
            if not geom.is_valid:
                geom = geom.buffer(0) if kind in ("building", "land") else geom
            if geom.is_empty:
                dropped["invalid_geometry"] += 1
                continue
            geom = geom.intersection(frame.roi)
            for part in nonempty_geometries(
                    geom, "Polygon" if kind in ("building", "land") else "LineString"):
                if kind in ("building", "land") and part.area < 1:
                    continue
                if kind in ("road", "coastline", "waterway") and part.length < 0.5:
                    continue
                features.append({
                    "kind": kind, "source_id": ident, "tags": tg,
                    "geometry": part
                })
        except Exception:
            dropped["geometry_error"] += 1
    # Trees mapped as points, never injected randomly.
    for node in root.findall("node"):
        tg = tags(node)
        if tg.get("natural") != "tree":
            continue
        pos = nodes.get(node.get("id"))
        if pos and frame.roi.covers(Point(pos)):
            features.append({"kind": "tree", "source_id": "node/" + node.get("id"),
                             "tags": tg, "geometry": Point(pos)})
    return features, dropped


def collection(features, frame, kind):
    return {
        "type": "FeatureCollection",
        "name": f"Copacabana OSM actual {kind}",
        "features": [
            {
                "type": "Feature",
                "properties": {"osm_id": f["source_id"], **f["tags"]},
                "geometry": mapping(frame.geodetic(f["geometry"])),
            }
            for f in features if f["kind"] == kind
        ],
    }


def height_info(tg):
    raw = tg.get("height") or tg.get("building:height")
    if raw:
        raw = raw.strip().replace(",", ".")
        m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*(?:m)?", raw)
        if m and 1.5 <= float(m.group(1)) <= 300:
            return float(m.group(1)), "OSM_height"
    levels = tg.get("building:levels")
    if levels:
        try:
            count = float(levels)
            if 1 <= count <= 100:
                return 3 * count, "OSM_levels_estimated_3m_each"
        except ValueError:
            pass
    return 18.0, "visualization_estimate_NOT_actual"


class ObjWriter:
    def __init__(self, output):
        self.path = output
        self.lines = ["# COPACABANA. OSM footprints, assumed volumes, meters, Z up",
                      "mtllib copacabana_base.mtl"]
        self.index = 1
        self.counts = Counter()

    def vertex(self, x, y, z):
        self.lines.append(f"v {x:.3f} {y:.3f} {z:.3f}")
        i = self.index
        self.index += 1
        return i

    def tri(self, a, b, c):
        self.lines.append(f"f {a} {b} {c}")

    def top(self, poly, height, category):
        self.lines.append(f"usemtl {category}")
        for tri in triangulate(poly):
            if not poly.covers(tri.representative_point()):
                continue
            coords = list(tri.exterior.coords)[:3]
            points = [self.vertex(p[0], p[1], height) for p in coords]
            self.tri(*points)
            self.counts[category] += 1

    def building(self, poly, height):
        self.top(poly, height, "Building")
        self.lines.append("usemtl Building")
        for ring in [poly.exterior, *poly.interiors]:
            pts = list(ring.coords)
            for a, b in zip(pts, pts[1:]):
                b0 = self.vertex(*a, 0)
                b1 = self.vertex(*b, 0)
                t1 = self.vertex(*b, height)
                t0 = self.vertex(*a, height)
                self.tri(b0, b1, t1)
                self.tri(b0, t1, t0)
                self.counts["wall_triangles"] += 2

    def save(self):
        self.path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        self.path.with_suffix(".mtl").write_text(
            "newmtl Building\nKd 0.72 0.72 0.69\n"
            "newmtl Road\nKd 0.17 0.17 0.18\n"
            "newmtl Land\nKd 0.36 0.50 0.30\n",
            encoding="utf-8")


def build(data=DATA, require_real_density=True):
    frame = Frame()
    osm_file = data / "copacabana.osm"
    if not osm_file.exists():
        gz = data / "copacabana.osm.gz"
        if gz.exists():
            with gzip.open(gz, "rb") as source, osm_file.open("wb") as dest:
                shutil.copyfileobj(source, dest)
        else:
            raise FileNotFoundError("Sem dados OSM reais; usar --download")
    features, dropped = parse_osm(osm_file, frame)
    counts = Counter(f["kind"] for f in features)
    if require_real_density and (counts["building"] < 20 or counts["road"] < 10):
        raise RuntimeError("Area insuficientemente mapeada: nao declarar cidade real pronta. " +
                           str(dict(counts)))
    data.mkdir(parents=True, exist_ok=True)
    for group, kinds in [
        ("buildings", ("building",)),
        ("roads", ("road",)),
        ("coast_and_land", ("coastline", "waterway", "land", "tree")),
    ]:
        content = {"type": "FeatureCollection", "features": []}
        for kind in kinds:
            content["features"].extend(collection(features, frame, kind)["features"])
        (data / f"{group}.geojson").write_text(
            json.dumps(content, ensure_ascii=False), encoding="utf-8")
    (data / "roi.geojson").write_text(
        json.dumps({"type": "Feature", "properties": {"area_m2": frame.roi.area,
                   "coordinates_crs": "EPSG:4326", "local_crs": frame.config["crs"]},
                    "geometry": mapping(frame.geodetic(frame.roi))}),
        encoding="utf-8")
    writer = ObjWriter(data / "copacabana_base.obj")
    heights = Counter()
    for feature in features:
        kind, geo = feature["kind"], feature["geometry"]
        if kind == "building":
            height, source = height_info(feature["tags"])
            heights[source] += 1
            writer.building(geo, height)
        elif kind == "road":
            category = feature["tags"].get("highway")
            width = 8.0 if category in ("primary", "secondary", "tertiary") else (
                2.5 if category in ("footway", "path", "pedestrian", "steps") else 5.0)
            road_shape = geo.buffer(width / 2, cap_style=2, join_style=2).intersection(frame.roi)
            for polygon in nonempty_geometries(road_shape, "Polygon"):
                writer.top(polygon, 0.06, "Road")
        elif kind == "land" and feature["tags"].get("natural") == "beach":
            writer.top(geo, 0.01, "Land")
    writer.save()
    with gzip.open(data / "copacabana.osm.gz", "wb", compresslevel=8) as dest:
        dest.write(osm_file.read_bytes())
    streets = sorted({f["tags"].get("name") for f in features if
                      f["kind"] == "road" and f["tags"].get("name")})
    report = {
        "source": "OpenStreetMap contributors; ODbL 1.0",
        "attribution_url": "https://www.openstreetmap.org/copyright",
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        "georeferencing": "EPSG:32723 (internal frame) -> local meters; exports EPSG:4326",
        "bbox_requested_south_west_north_east": frame.bbox(),
        "game_area_m2": frame.roi.area,
        "real_osm_entities_within_roi": dict(counts),
        "height_sources": dict(heights),
        "discarded": dict(dropped),
        "named_streets": streets,
        "gaps": ["No DEM/true mountain geometry", "No validated PBR facades",
                 "Relation multipolygon areas not assembled",
                 "OSM buildings with missing height use 18 m visualization estimate",
                 "Road ribbon widths approximate, not surveyed lanes",
                 "Coastline/beach depends on OSM tag coverage"],
        "warning": "Visual base, NOT a Unity-ready premium city.",
    }
    (data / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(json.dumps({"counts": dict(counts), "height_sources": dict(heights),
                      "street_count": len(streets), "area_m2": frame.roi.area},
                     indent=2))
    return report


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--download", action="store_true", help="Fetch live real OSM")
    args = cli.parse_args()
    DATA.mkdir(exist_ok=True)
    if args.download:
        download(Frame(), DATA / "copacabana.osm")
    build()
