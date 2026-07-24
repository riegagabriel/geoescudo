# -*- coding: utf-8 -*-
"""
Genera el mapa interactivo ligero de GeoEscudo (reemplaza el HTML de 56 MB).

Capas:
  1. Heatmap de denuncias de extorsión (SIDPOL, Lima Met. + Callao)
  2. Clusters de denuncias (FastMarkerCluster — datos compactos)
  3. IIEE afectadas (≥1 denuncia a ≤100 m) como círculos escalados por denuncias

Salida: OUTPUTS_DASHBOARD/mapa_geoescudo.html  (objetivo: < 8 MB)
"""
import os

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import FastMarkerCluster, HeatMap

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELITOS = os.path.join(BASE, "MINEDU", "mininter_delitos_total_20260526_135604.csv")
PADRON = os.path.join(BASE, "MINEDU", "padron_iiee_peru_completo_todos_estados.csv")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "mapa_geoescudo.html")

RADIO_M = 100


def main():
    print("Cargando denuncias...")
    dt = pd.read_csv(DELITOS, low_memory=False)
    dt["subtipo_hecho"] = dt["subtipo_hecho"].astype(str)
    ext = dt[
        dt["subtipo_hecho"].str.contains("EXTORS", case=False)
        & dt["departamento_hecho"].isin(["LIMA METROPOLITANA", "CALLAO"])
    ].dropna(subset=["latitud", "longitud"]).copy()
    print(f"  {len(ext):,} denuncias")

    print("Cargando IIEE activas...")
    p = pd.read_csv(PADRON, low_memory=False)
    dpd = p["departamento_provincia_distrito"].astype(str).str.upper()
    act = p[
        (dpd.str.startswith("LIMA / LIMA") | dpd.str.startswith("CALLAO"))
        & p["estado"].astype(str).str.contains("Activ", case=False)
    ].dropna(subset=["latitud_ie", "longitud_ie"]).copy()

    # Deduplicar por local (varios servicios comparten local/coordenada)
    if "codigo_local" in act.columns:
        agg = {"latitud_ie": "first", "longitud_ie": "first"}
        for c in ("nombre", "nivel_modalidad"):
            if c in act.columns:
                agg[c] = "first"
        for c in ("alumnos", "docentes"):
            hits = [x for x in act.columns if c in x.lower()]
            if hits:
                agg[hits[0]] = "sum"
        loc = act.groupby("codigo_local", as_index=False).agg(agg)
    else:
        loc = act
    print(f"  {len(loc):,} locales educativos")

    print("Identificando IIEE afectadas (≥1 denuncia a ≤100 m)...")
    gd = gpd.GeoDataFrame(
        ext, geometry=gpd.points_from_xy(ext["longitud"], ext["latitud"]), crs=4326
    ).to_crs(32718)
    gi = gpd.GeoDataFrame(
        loc, geometry=gpd.points_from_xy(loc["longitud_ie"], loc["latitud_ie"]), crs=4326
    ).to_crs(32718)
    buf = gi[["geometry"]].copy()
    buf["geometry"] = buf.geometry.buffer(RADIO_M)
    hit = gpd.sjoin(buf, gd[["geometry"]], predicate="contains")
    counts = hit.groupby(hit.index).size()
    gi["denuncias_100m"] = counts.reindex(gi.index).fillna(0).astype(int)
    afectadas = gi[gi["denuncias_100m"] > 0]
    print(f"  {len(afectadas):,} locales afectados")

    print("Construyendo mapa...")
    m = folium.Map(location=[-12.05, -77.05], zoom_start=11, tiles="cartodbpositron",
                   prefer_canvas=True)

    HeatMap(
        ext[["latitud", "longitud"]].values.tolist(),
        name="🔥 Densidad de denuncias (heatmap)",
        radius=13, blur=18, min_opacity=0.25, show=True,
    ).add_to(m)

    FastMarkerCluster(
        ext[["latitud", "longitud"]].round(5).values.tolist(),
        name="📍 Denuncias de extorsión (clusters)", show=False,
    ).add_to(m)

    fg = folium.FeatureGroup(name=f"🏫 IIEE afectadas (≤{RADIO_M} m)", show=True)
    nom_col = "nombre" if "nombre" in afectadas.columns else None
    for _, r in afectadas.iterrows():
        n = int(r["denuncias_100m"])
        nombre = str(r[nom_col])[:60] if nom_col else "IIEE"
        folium.CircleMarker(
            location=[r["latitud_ie"], r["longitud_ie"]],
            radius=min(3 + n * 0.8, 12),
            color="#B45309", weight=1, fill=True, fill_color="#D97706",
            fill_opacity=0.75,
            tooltip=f"{nombre} — {n} denuncia(s) ≤{RADIO_M} m",
        ).add_to(fg)
    fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    title = ("<div style='position:fixed;top:10px;left:60px;z-index:9999;"
             "background:#1E3A8A;color:white;padding:8px 16px;border-radius:8px;"
             "font-family:sans-serif;font-size:14px;'>"
             "<b>GeoEscudo</b> · Extorsión en entornos escolares · Lima y Callao 2025–26"
             "</div>")
    m.get_root().html.add_child(folium.Element(title))

    m.save(OUT)
    size_mb = os.path.getsize(OUT) / 1e6
    print(f"OK -> {OUT} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
