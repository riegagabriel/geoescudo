# -*- coding: utf-8 -*-
"""
Índice de Brecha de Confianza (IBC) — vista distrital para el mapa 3D de pydeck.

Concepto: para cada distrito con muestra ENAPRES suficiente (n>=80 en el módulo
de percepción), comparamos DOS RANGOS DE PERCENTIL entre distritos:

  * percentil de denuncias registradas (SIDPOL) — "cuánto reporta este distrito
    frente a los demás"
  * percentil de la señal de desconfianza (ENAPRES: inseguridad en institución
    educativa + mala calificación de la comisaría + mala calificación de
    atención pronta PNP) — "cuánta desconfianza expresa este distrito frente
    a los demás"

Ambos percentiles quedan en la MISMA escala 0-100, así que son directamente
comparables como dos barras del mismo tamaño de eje. Cuando la barra de
desconfianza es mucho más alta que la de denuncias, hay más silencio del que
las cifras oficiales muestran (brecha alta). Se usa percentil relativo
—no el valor crudo— precisamente para no comparar peras con manzanas
(un conteo de denuncias contra un porcentaje).

Requiere: enapres_distrital.json (ya generado por etl_enapres_distrital.py),
proximidad_verificada.json (para denuncias y detalle IEEE por distrito),
MINEDU/geofiles/DISTRITO.gpkg (centroides).

Salida: OUTPUTS_DASHBOARD/ibc_distrital.json
"""
import json
import os

import geopandas as gpd
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_JSON = os.path.join(BASE, "OUTPUTS_DASHBOARD", "enapres_distrital.json")
PROX_JSON = os.path.join(BASE, "OUTPUTS_DASHBOARD", "proximidad_verificada.json")
GPKG = os.path.join(BASE, "MINEDU", "geofiles", "DISTRITO.gpkg")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "ibc_distrital.json")

MIN_N = 80


def main():
    with open(DIST_JSON, encoding="utf-8") as f:
        dist = json.load(f)
    with open(PROX_JSON, encoding="utf-8") as f:
        prox = json.load(f)

    d = pd.DataFrame(dist["distritos"])
    d = d[d["n_modulo_percepcion"] >= MIN_N].copy()
    d = d[d["inseguridad_col_educativa_pct"].notna()].copy()

    d["desconfianza_idx"] = d[
        ["inseguridad_col_educativa_pct", "comisaria_mala_pct", "pnp_atencion_mala_pct"]
    ].mean(axis=1)

    # Percentiles relativos SOLO dentro de este conjunto comparable (n>=80)
    d["pct_denuncias"] = d["denuncias_extorsion_sidpol"].rank(pct=True) * 100
    d["pct_desconfianza"] = d["desconfianza_idx"].rank(pct=True) * 100
    d["brecha"] = d["pct_desconfianza"] - d["pct_denuncias"]

    # Detalle IEEE por distrito: denuncias ≤100m (geo precisa) y top IIEE
    pdist = pd.DataFrame(prox["por_distrito"])
    pdist["distrito"] = pdist["distrito"].str.title()
    d = d.merge(
        pdist[["distrito", "denuncias_100m", "denuncias_geo_precisa"]],
        on="distrito", how="left",
    )
    top_iiee = pd.DataFrame(prox["top_iiee"])
    expuestos = pd.DataFrame(prox["expuestos_por_distrito"])  # ya en distrito NORM (upper/strip)

    # Centroides distritales (proyección UTM para centroide correcto, luego a 4326)
    g = gpd.read_file(GPKG)
    g = g[g["nombprov"].isin(["LIMA", "CALLAO"])].copy()
    g["distrito_match"] = g["nombdist"].str.upper().str.strip()
    g_utm = g.to_crs(32718)
    cent = g_utm.geometry.centroid.to_crs(4326)
    g["lon"] = cent.x.values
    g["lat"] = cent.y.values

    d["distrito_match"] = d["distrito"].str.upper().str.strip()
    d = d.merge(g[["distrito_match", "lon", "lat"]], on="distrito_match", how="left")
    sin_geom = d[d["lon"].isna()]["distrito"].tolist()
    if sin_geom:
        print(f"⚠️ Sin centroide (revisar nombre): {sin_geom}")
    d = d.dropna(subset=["lon", "lat"])

    registros = []
    for _, r in d.iterrows():
        top3 = (top_iiee[top_iiee["distrito"].str.upper().str.strip() == r["distrito_match"]]
                .nlargest(3, "denuncias_100m"))
        exp = expuestos[expuestos["distrito"] == r["distrito_match"]]
        registros.append({
            "distrito": r["distrito"],
            "lon": round(float(r["lon"]), 5),
            "lat": round(float(r["lat"]), 5),
            "denuncias_total": int(r["denuncias_extorsion_sidpol"]),
            "denuncias_100m": int(r["denuncias_100m"]) if pd.notna(r["denuncias_100m"]) else 0,
            "victimas_estimadas": int(r["victimas_estimadas"]),
            "locales_afectados": int(exp["locales_afectados"].iloc[0]) if len(exp) else 0,
            "alumnos_expuestos": int(exp["alumnos_expuestos"].iloc[0]) if len(exp) else 0,
            "docentes_expuestos": int(exp["docentes_expuestos"].iloc[0]) if len(exp) else 0,
            "desconfianza_idx": round(float(r["desconfianza_idx"]), 1),
            "inseguridad_col_educativa_pct": r["inseguridad_col_educativa_pct"],
            "comisaria_mala_pct": r["comisaria_mala_pct"],
            "pnp_atencion_mala_pct": r["pnp_atencion_mala_pct"],
            "temor_extorsion_pct": r["temor_extorsion_pct"],
            "pct_denuncias": round(float(r["pct_denuncias"]), 1),
            "pct_desconfianza": round(float(r["pct_desconfianza"]), 1),
            "brecha": round(float(r["brecha"]), 1),
            "n_modulo_percepcion": int(r["n_modulo_percepcion"]),
            "top_iiee": [
                {"nombre": t["nombre"], "denuncias_100m": int(t["denuncias_100m"])}
                for _, t in top3.iterrows()
            ],
        })

    registros.sort(key=lambda x: -x["brecha"])
    out = {
        "fuente": "ENAPRES 2025 (percepción) + PNP/SIDPOL-DGIS + MINEDU (geofiles distritales)",
        "min_n_distrital": MIN_N,
        "nota_metodologica": (
            "El IBC compara, SOLO entre los distritos con muestra ENAPRES suficiente "
            f"(n≥{MIN_N} en el módulo de percepción), el percentil relativo de denuncias "
            "registradas contra el percentil relativo de una señal de desconfianza "
            "(inseguridad en institución educativa + mala calificación de la comisaría + "
            "mala calificación de la atención pronta de la PNP). Un percentil, no un valor "
            "absoluto, para poder comparar dos escalas distintas (conteos vs. porcentajes) "
            "de forma honesta. Brecha = percentil de desconfianza − percentil de denuncias: "
            "positiva y alta significa que el distrito desconfía proporcionalmente más de lo "
            "que denuncia; negativa significa que denuncia proporcionalmente más de lo que "
            "su desconfianza declarada sugeriría."
        ),
        "distritos": registros,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"OK -> {OUT} ({len(registros)} distritos)")
    print("Top 5 brecha (mayor desconfianza relativa a su denuncia):")
    for r in registros[:5]:
        print(f"  {r['distrito']}: brecha={r['brecha']:+.1f} "
              f"(denuncias pct={r['pct_denuncias']:.0f}, desconfianza pct={r['pct_desconfianza']:.0f})")
    print("Bottom 5 (denuncian proporcionalmente más que su desconfianza):")
    for r in registros[-5:]:
        print(f"  {r['distrito']}: brecha={r['brecha']:+.1f} "
              f"(denuncias pct={r['pct_denuncias']:.0f}, desconfianza pct={r['pct_desconfianza']:.0f})")


if __name__ == "__main__":
    main()
