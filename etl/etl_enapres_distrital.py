# -*- coding: utf-8 -*-
"""
ETL ENAPRES 2025 — Termómetro distrital de Lima Metropolitana y Callao.

Calcula, por distrito (solo dominio ciudad LIMA/CALLAO), indicadores ponderados de:
  * Percepción de inseguridad en el barrio (P403 in 1,2)
  * Percepción de inseguridad EN UNA INSTITUCIÓN EDUCATIVA (P407_4 in 1,2; excluye 5=No aplica)
  * Temor a ser víctima de extorsión próximos 12 meses (P402_11 == 1)
  * Mala calificación del desempeño PNP — atender prontamente (P413_1 in 1,2)
  * Mala calificación del trabajo de la comisaría del barrio (P414 in 1,2; excluye 5=No sabe)
  * "Poca presencia policial" como razón de inseguridad (P404_1 == 1, entre inseguros)

ADVERTENCIA METODOLÓGICA: ENAPRES es representativa a nivel de ciudad principal /
departamento, NO distrital. Estos valores son REFERENCIALES: se publican solo
distritos con n >= MIN_N respuestas en el módulo y se reporta n por distrito.

También agrega denuncias SIDPOL por distrito y una estimación de víctimas
(denuncias × factor de subregistro del dominio Lima+Callao).

Salida: OUTPUTS_DASHBOARD/enapres_distrital.json
"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(BASE, "ENAPRES_2025", "CAP_400_URBANO_4.csv")
DELITOS = os.path.join(BASE, "MINEDU", "mininter_delitos_total_20260526_135604.csv")
ENAPRES_JSON = os.path.join(BASE, "OUTPUTS_DASHBOARD", "enapres_extorsion.json")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "enapres_distrital.json")

W = "FACTOR_CAP400"
MIN_N = 80  # mínimo de respuestas del módulo de percepción por distrito


def wpct(d, cond_num, cond_den):
    """% ponderado: suma de pesos donde cond_num / suma donde cond_den."""
    den = d.loc[cond_den, W].sum()
    if den <= 0:
        return None
    return round(100 * d.loc[cond_num & cond_den, W].sum() / den, 1)


def main():
    cols = ["NOMBREDI", "CIUDADSEG", W, "P402_11", "P403", "P404_1",
            "P407_4", "P413_1", "P413_3", "P414"]
    df = pd.read_csv(CSV, usecols=cols, low_memory=False)
    lc = df[df["CIUDADSEG"].isin(["LIMA", "CALLAO"])].copy()

    # Denuncias SIDPOL por distrito (extorsión, Lima Met.+Callao)
    dt = pd.read_csv(DELITOS, usecols=["subtipo_hecho", "departamento_hecho", "distrito_hecho"],
                     low_memory=False)
    dt["subtipo_hecho"] = dt["subtipo_hecho"].astype(str)
    ext = dt[dt["subtipo_hecho"].str.contains("EXTORS", case=False)
             & dt["departamento_hecho"].isin(["LIMA METROPOLITANA", "CALLAO"])]
    denu = ext.groupby(ext["distrito_hecho"].astype(str).str.upper().str.strip()).size()

    # Factor de subregistro del dominio Lima+Callao (del ETL de cifra negra)
    with open(ENAPRES_JSON, encoding="utf-8") as f:
        ej = json.load(f)
    lc_dom = next(d for d in ej["dominios"] if d["dominio"] == "Lima + Callao (ciudad)")
    factor = lc_dom["victimas_por_denuncia"]  # ≈ 3.7

    filas = []
    for dist, d in lc.groupby("NOMBREDI"):
        # módulo de percepción: quienes respondieron P403
        n_mod = int(d["P403"].notna().sum())
        n_tot = int(len(d))
        dd = str(dist).upper().strip()
        n_den = int(denu.get(dd, 0))
        fila = {
            "distrito": dist.title(),
            "n_encuestados": n_tot,
            "n_modulo_percepcion": n_mod,
            "denuncias_extorsion_sidpol": n_den,
            "victimas_estimadas": int(round(n_den * factor)) if n_den else 0,
        }
        if n_mod >= MIN_N:
            fila.update({
                "inseguridad_barrio_pct": wpct(d, d["P403"].isin([1, 2]), d["P403"].notna()),
                "inseguridad_col_educativa_pct": wpct(
                    d, d["P407_4"].isin([1, 2]), d["P407_4"].isin([1, 2, 3, 4])),
                "temor_extorsion_pct": wpct(d, d["P402_11"] == 1, d["P402_11"].notna()),
                "pnp_atencion_mala_pct": wpct(
                    d, d["P413_1"].isin([1, 2]), d["P413_1"].isin([1, 2, 3, 4])),
                "pnp_informar_mala_pct": wpct(
                    d, d["P413_3"].isin([1, 2]), d["P413_3"].isin([1, 2, 3, 4])),
                "comisaria_mala_pct": wpct(
                    d, d["P414"].isin([1, 2]), d["P414"].isin([1, 2, 3, 4])),
                "poca_presencia_policial_pct": wpct(
                    d, d["P404_1"] == 1, d["P404_1"].notna()),
            })
        filas.append(fila)

    # Agregado Lima+Callao (para KPIs del acto ④)
    agg = {
        "inseguridad_barrio_pct": wpct(lc, lc["P403"].isin([1, 2]), lc["P403"].notna()),
        "inseguridad_col_educativa_pct": wpct(
            lc, lc["P407_4"].isin([1, 2]), lc["P407_4"].isin([1, 2, 3, 4])),
        "pnp_atencion_mala_pct": wpct(
            lc, lc["P413_1"].isin([1, 2]), lc["P413_1"].isin([1, 2, 3, 4])),
        "pnp_informar_mala_pct": wpct(
            lc, lc["P413_3"].isin([1, 2]), lc["P413_3"].isin([1, 2, 3, 4])),
        "comisaria_mala_pct": wpct(lc, lc["P414"].isin([1, 2]), lc["P414"].isin([1, 2, 3, 4])),
        "poca_presencia_policial_pct": wpct(lc, lc["P404_1"] == 1, lc["P404_1"].notna()),
        "n_modulo_percepcion": int(lc["P403"].notna().sum()),
    }

    out = {
        "fuente": "INEI — ENAPRES 2025 Cap.400 (urbano, 15+) + PNP/SIDPOL corte 26/05/2026",
        "factor_subregistro": factor,
        "min_n_distrital": MIN_N,
        "nota_metodologica": (
            "ENAPRES es representativa por ciudad principal/departamento, NO por distrito. "
            "Los indicadores distritales son REFERENCIALES: solo se publican distritos con "
            f"n>={MIN_N} en el módulo de percepción y siempre acompañados de su n. "
            "Víctimas estimadas = denuncias SIDPOL × factor de subregistro del dominio "
            "Lima+Callao (no es una medición distrital directa). "
            "Inseguridad en institución educativa excluye a quienes no las frecuentan (código 5)."
        ),
        "agregado_lima_callao": agg,
        "distritos": sorted(filas, key=lambda x: -x["denuncias_extorsion_sidpol"]),
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    con_ind = [f for f in filas if "inseguridad_barrio_pct" in f]
    print(f"OK -> {OUT}")
    print(f"Agregado Lima+Callao: {agg}")
    print(f"Distritos totales: {len(filas)} | con indicadores (n>={MIN_N}): {len(con_ind)}")
    top = sorted(con_ind, key=lambda x: -(x.get('inseguridad_col_educativa_pct') or 0))[:8]
    for t in top:
        print(f"  {t['distrito']}: inseg.colegio={t['inseguridad_col_educativa_pct']}% "
              f"comisaria_mala={t['comisaria_mala_pct']}% denuncias={t['denuncias_extorsion_sidpol']} "
              f"(n_mod={t['n_modulo_percepcion']})")


if __name__ == "__main__":
    main()
