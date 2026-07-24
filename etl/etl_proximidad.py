# -*- coding: utf-8 -*-
"""
ETL de proximidad verificada — denuncias de extorsión vs. IIEE (Lima Met. + Callao).

Reconciliación de cifras (jul 2026):
  * El análisis original (mapa_iiee_extorsion.ipynb) usó RADIO de 200 m -> "72.5%".
  * El xlsx del dashboard usó 100 m pero con numerador en ubicaciones únicas y
    denominador en denuncias (16.2%) — mezcla de unidades.
  * Este script calcula la distancia de CADA DENUNCIA a la IIEE activa más cercana
    (sjoin_nearest, UTM-18S) y reporta % por umbral, sin mezclar unidades.

Insumos:
  MINEDU/mininter_delitos_total_20260526_135604.csv  (SIDPOL, corte 26/05/2026)
  MINEDU/padron_iiee_peru_completo_todos_estados.csv (Padrón Web MINEDU)

Salida: OUTPUTS_DASHBOARD/proximidad_verificada.json
"""
import json
import os

import geopandas as gpd
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELITOS = os.path.join(BASE, "MINEDU", "mininter_delitos_total_20260526_135604.csv")
PADRON = os.path.join(BASE, "MINEDU", "padron_iiee_peru_completo_todos_estados.csv")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "proximidad_verificada.json")

UMBRALES = [50, 100, 150, 200, 300, 500]


def main():
    print("Cargando denuncias SIDPOL (corte 26/05/2026)...")
    dt = pd.read_csv(DELITOS, low_memory=False)
    dt["subtipo_hecho"] = dt["subtipo_hecho"].astype(str)
    ext = dt[
        dt["subtipo_hecho"].str.contains("EXTORS", case=False)
        & dt["departamento_hecho"].isin(["LIMA METROPOLITANA", "CALLAO"])
    ].dropna(subset=["latitud", "longitud"]).copy()
    print(f"  Denuncias de extorsión Lima Met.+Callao: {len(ext):,}")

    print("Cargando Padrón Web MINEDU...")
    p = pd.read_csv(PADRON, low_memory=False)
    dpd = p["departamento_provincia_distrito"].astype(str).str.upper()
    act = p[
        (dpd.str.startswith("LIMA / LIMA") | dpd.str.startswith("CALLAO"))
        & p["estado"].astype(str).str.contains("Activ", case=False)
    ].dropna(subset=["latitud_ie", "longitud_ie"])
    n_locales = act["codigo_local"].nunique() if "codigo_local" in act else None
    print(f"  Servicios educativos activos: {len(act):,} (locales únicos: {n_locales})")

    gd = gpd.GeoDataFrame(
        ext, geometry=gpd.points_from_xy(ext["longitud"], ext["latitud"]), crs=4326
    ).to_crs(32718)
    gi = gpd.GeoDataFrame(
        act, geometry=gpd.points_from_xy(act["longitud_ie"], act["latitud_ie"]), crs=4326
    ).to_crs(32718)

    print("Calculando distancia de cada denuncia a la IIEE activa más cercana...")
    j = gpd.sjoin_nearest(gd, gi[["geometry"]], distance_col="dist_m")
    j = j[~j.index.duplicated()]

    total = int(len(j))
    out = {
        "fuente": "PNP/SIDPOL-DGIS corte 26/05/2026 + MINEDU Padrón Web (IIEE activas)",
        "ambito": "Lima Metropolitana + Callao",
        "metodo": ("Distancia de cada denuncia de extorsión a la IIEE activa más cercana; "
                   "sjoin_nearest en UTM-18S. Denominador y numerador en DENUNCIAS "
                   "(sin deduplicar ubicaciones), unidades consistentes."),
        "n_denuncias": total,
        "n_servicios_educativos_activos": int(len(act)),
        "n_locales_educativos": int(n_locales) if n_locales else None,
        "mediana_distancia_m": round(float(np.median(j["dist_m"])), 1),
        "umbrales": {
            str(r): {
                "n_denuncias": int((j["dist_m"] <= r).sum()),
                "pct": round(100 * float((j["dist_m"] <= r).mean()), 1),
            }
            for r in UMBRALES
        },
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK -> {OUT}")
    print(f"  Mediana: {out['mediana_distancia_m']} m")
    for r in UMBRALES:
        u = out["umbrales"][str(r)]
        print(f"  <= {r} m: {u['n_denuncias']:,} ({u['pct']}%)")


if __name__ == "__main__":
    main()
