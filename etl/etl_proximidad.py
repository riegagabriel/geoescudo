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

import glob

import geopandas as gpd
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELITOS = sorted(glob.glob(os.path.join(BASE, "MINEDU", "mininter_delitos_total_*.csv")))[-1]
PADRON = os.path.join(BASE, "MINEDU", "padron_iiee_peru_completo_todos_estados.csv")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "proximidad_verificada.json")

UMBRALES = [50, 100, 150, 200, 300, 500]


def main():
    print(f"Cargando denuncias SIDPOL ({os.path.basename(DELITOS)})...")
    dt = pd.read_csv(DELITOS, low_memory=False)
    dt["subtipo_hecho"] = dt["subtipo_hecho"].astype(str)
    ext = dt[
        dt["subtipo_hecho"].str.contains("EXTORS", case=False)
        & dt["departamento_hecho"].isin(["LIMA METROPOLITANA", "CALLAO"])
    ].dropna(subset=["latitud", "longitud"]).copy()
    n_total = len(ext)
    print(f"  Denuncias de extorsión Lima Met.+Callao: {n_total:,}")

    # ── Filtro de geocodificación imprecisa ──────────────────────────────────
    # SIDPOL georreferencia al centroide distrital cuando no puede geocodificar
    # la dirección: puntos con decenas/cientos de denuncias de direcciones
    # distintas. Criterio: ≥10 denuncias en el mismo punto Y más de la mitad
    # con direcciones diferentes -> punto de relleno, se excluye del análisis
    # de proximidad (NO de los conteos distritales, que usan distrito_hecho).
    ext["pt"] = (ext["latitud"].round(6).astype(str) + ","
                 + ext["longitud"].round(6).astype(str))
    g = ext.groupby("pt").agg(
        n=("pt", "size"),
        ndir=("direccion_hecho", lambda s: s.astype(str).nunique()),
    )
    sospechosos = set(g[(g["n"] >= 10) & (g["ndir"] > g["n"] * 0.5)].index)
    ext["geo_precisa"] = ~ext["pt"].isin(sospechosos)
    n_precisa = int(ext["geo_precisa"].sum())
    print(f"  Con geolocalización precisa: {n_precisa:,} "
          f"({100*n_precisa/n_total:.1f}%) — excluidos {len(sospechosos)} puntos de relleno")
    ext_todas = ext.copy()
    ext = ext[ext["geo_precisa"]].copy()

    print("Cargando Padrón Web MINEDU...")
    p = pd.read_csv(PADRON, low_memory=False)
    dpd = p["departamento_provincia_distrito"].astype(str).str.upper()
    act = p[
        (dpd.str.startswith("LIMA / LIMA") | dpd.str.startswith("CALLAO"))
        & p["estado"].astype(str).str.contains("Activ", case=False)
    ].dropna(subset=["latitud_ie", "longitud_ie"]).copy()
    for c in ("alumnos_censo_2025", "docentes_censo_2025"):
        act[c] = pd.to_numeric(act[c], errors="coerce").fillna(0)
    n_locales = act["codigo_local"].nunique()
    print(f"  Servicios educativos activos: {len(act):,} (locales únicos: {n_locales})")

    # Nivel LOCAL educativo: varios servicios comparten local y coordenada
    loc = act.groupby("codigo_local", as_index=False).agg(
        nombre=("nombre", "first"),
        distrito=("distrito", "first"),
        tipo_gestion=("tipo_gestion", "first"),
        latitud_ie=("latitud_ie", "first"),
        longitud_ie=("longitud_ie", "first"),
        alumnos=("alumnos_censo_2025", "sum"),
        docentes=("docentes_censo_2025", "sum"),
    )

    gd = gpd.GeoDataFrame(
        ext, geometry=gpd.points_from_xy(ext["longitud"], ext["latitud"]), crs=4326
    ).to_crs(32718)
    gi = gpd.GeoDataFrame(
        loc, geometry=gpd.points_from_xy(loc["longitud_ie"], loc["latitud_ie"]), crs=4326
    ).to_crs(32718)

    print("Calculando distancia de cada denuncia al local educativo más cercano...")
    j = gpd.sjoin_nearest(gd, gi[["geometry"]], distance_col="dist_m")
    j = j[~j.index.duplicated()]

    print("Calculando locales afectados (buffer 100 m) y población expuesta...")
    buf = gi[["geometry"]].copy()
    buf["geometry"] = buf.geometry.buffer(100)
    hit = gpd.sjoin(buf, gd[["geometry"]], predicate="contains")
    counts = hit.groupby(hit.index).size()
    gi["denuncias_100m"] = counts.reindex(gi.index).fillna(0).astype(int)
    afect = gi[gi["denuncias_100m"] > 0]

    # Denuncias ≤100 m por distrito. Numerador y denominador SOLO sobre el
    # subconjunto con geo precisa; el total distrital (todas) va aparte.
    j["distrito_hecho"] = j["distrito_hecho"].astype(str).str.upper().str.strip()
    por_dist = (
        j.assign(cerca=j["dist_m"] <= 100)
        .groupby("distrito_hecho")
        .agg(denuncias_geo_precisa=("cerca", "size"), denuncias_100m=("cerca", "sum"))
        .reset_index()
    )
    tot_dist = (ext_todas.groupby(ext_todas["distrito_hecho"].astype(str).str.upper().str.strip())
                .size().rename("denuncias_total").reset_index())
    por_dist = por_dist.merge(tot_dist, on="distrito_hecho", how="outer").fillna(0)
    for c in ("denuncias_geo_precisa", "denuncias_100m", "denuncias_total"):
        por_dist[c] = por_dist[c].astype(int)
    por_dist = por_dist.sort_values("denuncias_100m", ascending=False)

    top_iiee = afect.nlargest(30, "denuncias_100m")[
        ["nombre", "distrito", "tipo_gestion", "alumnos", "docentes", "denuncias_100m"]]

    # Población expuesta y locales afectados, agregados por distrito (para el
    # panel del IBC): SOLO locales con >=1 denuncia en su buffer de 100 m.
    afect_dist = (
        afect.assign(distrito_norm=afect["distrito"].astype(str).str.upper().str.strip())
        .groupby("distrito_norm")
        .agg(locales_afectados=("denuncias_100m", "size"),
             alumnos_expuestos=("alumnos", "sum"),
             docentes_expuestos=("docentes", "sum"))
        .reset_index()
        .rename(columns={"distrito_norm": "distrito"})
    )
    for c in ("locales_afectados", "alumnos_expuestos", "docentes_expuestos"):
        afect_dist[c] = afect_dist[c].astype(int)

    # Fecha de corte: máxima fecha de registro presente en la extracción
    corte = pd.to_datetime(dt["fecha_hora_registro_hecho"], unit="ms", errors="coerce").max()
    corte_str = corte.strftime("%d/%m/%Y") if pd.notna(corte) else "s/f"

    out = {
        "fuente": f"PNP/SIDPOL-DGIS corte {corte_str} + MINEDU Padrón Web (IIEE activas)",
        "corte": corte_str,
        "archivo_origen": os.path.basename(DELITOS),
        "ambito": "Lima Metropolitana + Callao",
        "metodo": ("Distancia de cada denuncia de extorsión al local educativo activo más "
                   "cercano; sjoin_nearest en UTM-18S. Numerador y denominador en denuncias. "
                   "El análisis de proximidad usa SOLO denuncias con geolocalización precisa: "
                   "se excluyen los puntos de relleno (centroides distritales) donde SIDPOL "
                   "agrupa denuncias no geocodificables (criterio: ≥10 denuncias en un mismo "
                   "punto con >50% de direcciones distintas)."),
        "n_denuncias": n_total,
        "n_geo_precisa": n_precisa,
        "cobertura_geo_pct": round(100 * n_precisa / n_total, 1),
        "n_puntos_relleno_excluidos": len(sospechosos),
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
        "afectados_100m": {
            "n_locales": int(len(afect)),
            "pct_locales": round(100 * len(afect) / len(gi), 1),
            "alumnos_expuestos": int(afect["alumnos"].sum()),
            "docentes_expuestos": int(afect["docentes"].sum()),
            "metodo": ("Local educativo afectado = ≥1 denuncia dentro de su buffer de 100 m. "
                       "Población expuesta = suma de alumnos y docentes (Censo 2025) de los "
                       "servicios de esos locales."),
        },
        "por_distrito": por_dist.rename(columns={"distrito_hecho": "distrito"})
                                .to_dict(orient="records"),
        "top_iiee": top_iiee.to_dict(orient="records"),
        "expuestos_por_distrito": afect_dist.to_dict(orient="records"),
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
