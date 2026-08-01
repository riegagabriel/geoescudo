# -*- coding: utf-8 -*-
"""
Exporta los GeoJSON que consume el mapa "sala de comando" (MapLibre GL JS).

Genera, en OUTPUTS_DASHBOARD/geojson/:
  * distritos.geojson        — 50 distritos Lima+Callao, con denuncias/IBC
                                donde hay muestra suficiente
  * iiee_afectadas.geojson   — locales educativos con >=1 denuncia a <=100 m
  * heatmap_denuncias.geojson— puntos de denuncias con geo precisa (para
                                heatmap de densidad, privacy-by-design: no se
                                muestran como marcadores individuales)

Requiere que ya se hayan corrido etl_proximidad.py, etl_ibc.py y
etl_enapres_distrital.py (lee sus JSON de salida) + los CSV crudos de SIDPOL
y el Padrón MINEDU + DISTRITO.gpkg.
"""
import glob
import json
import os

import geopandas as gpd
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELITOS = sorted(glob.glob(os.path.join(BASE, "MINEDU", "mininter_delitos_total_*.csv")))[-1]
PADRON = os.path.join(BASE, "MINEDU", "padron_iiee_peru_completo_todos_estados.csv")
GPKG = os.path.join(BASE, "MINEDU", "geofiles", "DISTRITO.gpkg")
OUT_DIR = os.path.join(BASE, "OUTPUTS_DASHBOARD")
GEO_DIR = os.path.join(OUT_DIR, "geojson")

PROX_JSON = os.path.join(OUT_DIR, "proximidad_verificada.json")
IBC_JSON = os.path.join(OUT_DIR, "ibc_distrital.json")
DIST_JSON = os.path.join(OUT_DIR, "enapres_distrital.json")


def main():
    os.makedirs(GEO_DIR, exist_ok=True)
    with open(PROX_JSON, encoding="utf-8") as f:
        prox = json.load(f)
    with open(IBC_JSON, encoding="utf-8") as f:
        ibc = json.load(f)
    with open(DIST_JSON, encoding="utf-8") as f:
        dist = json.load(f)

    # ── 1. Distritos: polígonos + métricas ────────────────────────────────────
    print("Distritos...")
    g = gpd.read_file(GPKG)
    g = g[g["nombprov"].isin(["LIMA", "CALLAO"])].copy()
    g["geometry"] = g.geometry.simplify(0.0006, preserve_topology=True)
    g["distrito_norm"] = g["nombdist"].str.upper().str.strip()

    por_dist = {d["distrito"].upper().strip(): d for d in prox["por_distrito"]}
    ibc_by = {d["distrito"].upper().strip(): d for d in ibc["distritos"]}
    dist_by = {d["distrito"].upper().strip(): d for d in dist["distritos"]}

    def props_for(nombre_norm, nombre_orig):
        base = {
            "distrito": nombre_orig.title(),
            "denuncias_total": 0, "denuncias_100m": 0,
            "tiene_ibc": False,
        }
        pd_ = por_dist.get(nombre_norm)
        if pd_:
            base["denuncias_total"] = int(pd_.get("denuncias_total", 0))
            base["denuncias_100m"] = int(pd_.get("denuncias_100m", 0))
        i_ = ibc_by.get(nombre_norm)
        if i_:
            base.update({
                "tiene_ibc": True,
                "victimas_estimadas": i_["victimas_estimadas"],
                "desconfianza_idx": i_["desconfianza_idx"],
                "pct_denuncias": i_["pct_denuncias"],
                "pct_desconfianza": i_["pct_desconfianza"],
                "brecha": i_["brecha"],
                "locales_afectados": i_["locales_afectados"],
                "alumnos_expuestos": i_["alumnos_expuestos"],
                "docentes_expuestos": i_["docentes_expuestos"],
                "inseguridad_col_educativa_pct": i_["inseguridad_col_educativa_pct"],
                "comisaria_mala_pct": i_["comisaria_mala_pct"],
                "pnp_atencion_mala_pct": i_["pnp_atencion_mala_pct"],
                "temor_extorsion_pct": i_["temor_extorsion_pct"],
            })
        else:
            d_ = dist_by.get(nombre_norm)
            base["n_modulo_percepcion"] = d_["n_modulo_percepcion"] if d_ else 0
        return base

    records, geoms = [], []
    for _, row in g.iterrows():
        p = props_for(row["distrito_norm"], row["nombdist"])
        records.append(p)
        geoms.append(row.geometry)
    gout = gpd.GeoDataFrame(records, geometry=geoms, crs=4326)
    gout.to_file(os.path.join(GEO_DIR, "distritos.geojson"), driver="GeoJSON")
    print(f"  {len(gout)} distritos ({sum(r['tiene_ibc'] for r in records)} con IBC)")

    # ── 2. Locales educativos afectados (>=1 denuncia a <=100m) ──────────────
    print("Locales educativos afectados...")
    dt = pd.read_csv(DELITOS, low_memory=False)
    dt["subtipo_hecho"] = dt["subtipo_hecho"].astype(str)
    ext = dt[dt["subtipo_hecho"].str.contains("EXTORS", case=False)
             & dt["departamento_hecho"].isin(["LIMA METROPOLITANA", "CALLAO"])
             ].dropna(subset=["latitud", "longitud"]).copy()

    p = pd.read_csv(PADRON, low_memory=False)
    dpd = p["departamento_provincia_distrito"].astype(str).str.upper()
    act = p[(dpd.str.startswith("LIMA / LIMA") | dpd.str.startswith("CALLAO"))
            & p["estado"].astype(str).str.contains("Activ", case=False)
            ].dropna(subset=["latitud_ie", "longitud_ie"]).copy()
    for c in ("alumnos_censo_2025", "docentes_censo_2025"):
        act[c] = pd.to_numeric(act[c], errors="coerce").fillna(0)
    loc = act.groupby("codigo_local", as_index=False).agg(
        nombre=("nombre", "first"), distrito=("distrito", "first"),
        tipo_gestion=("tipo_gestion", "first"),
        latitud_ie=("latitud_ie", "first"), longitud_ie=("longitud_ie", "first"),
        alumnos=("alumnos_censo_2025", "sum"), docentes=("docentes_censo_2025", "sum"),
    )

    gd = gpd.GeoDataFrame(ext, geometry=gpd.points_from_xy(ext["longitud"], ext["latitud"]),
                          crs=4326).to_crs(32718)
    gi = gpd.GeoDataFrame(loc, geometry=gpd.points_from_xy(loc["longitud_ie"], loc["latitud_ie"]),
                          crs=4326).to_crs(32718)
    buf = gi[["geometry"]].copy()
    buf["geometry"] = buf.geometry.buffer(100)
    hit = gpd.sjoin(buf, gd[["geometry"]], predicate="contains")
    counts = hit.groupby(hit.index).size()
    gi["denuncias_100m"] = counts.reindex(gi.index).fillna(0).astype(int)
    afect = gi[gi["denuncias_100m"] > 0].to_crs(4326)

    iiee_out = gpd.GeoDataFrame({
        "nombre": afect["nombre"], "distrito": afect["distrito"],
        "tipo_gestion": afect["tipo_gestion"],
        "alumnos": afect["alumnos"].astype(int), "docentes": afect["docentes"].astype(int),
        "denuncias_100m": afect["denuncias_100m"],
    }, geometry=afect.geometry, crs=4326)
    iiee_out.to_file(os.path.join(GEO_DIR, "iiee_afectadas.geojson"), driver="GeoJSON")
    print(f"  {len(iiee_out)} locales afectados")

    # ── 3. Puntos de denuncia (geo precisa) para heatmap de densidad ─────────
    print("Heatmap de denuncias (solo geo precisa, privacy-by-design)...")
    ext["pt"] = (ext["latitud"].round(6).astype(str) + "," + ext["longitud"].round(6).astype(str))
    gcnt = ext.groupby("pt").agg(n=("pt", "size"),
                                 ndir=("direccion_hecho", lambda s: s.astype(str).nunique()))
    sospechosos = set(gcnt[(gcnt["n"] >= 10) & (gcnt["ndir"] > gcnt["n"] * 0.5)].index)
    ext_precisa = ext[~ext["pt"].isin(sospechosos)]
    heat = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(ext_precisa["longitud"], ext_precisa["latitud"]), crs=4326)
    heat.to_file(os.path.join(GEO_DIR, "heatmap_denuncias.geojson"), driver="GeoJSON")
    print(f"  {len(heat)} puntos para heatmap")

    for f in ("distritos.geojson", "iiee_afectadas.geojson", "heatmap_denuncias.geojson"):
        size_kb = os.path.getsize(os.path.join(GEO_DIR, f)) / 1024
        print(f"  {f}: {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
