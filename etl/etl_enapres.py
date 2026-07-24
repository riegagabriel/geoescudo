# -*- coding: utf-8 -*-
"""
ETL ENAPRES 2025 — Capítulo 400 (Seguridad Ciudadana, urbano)
Calcula los indicadores de victimización, denuncia y cifra negra de EXTORSIÓN
que consume el dashboard GeoEscudo.

Fuente: INEI — ENAPRES 2025, CAP_400_URBANO_4.csv (personas de 15+ años, área urbana)
Delito 19 = Extorsión | Delito 20 = Intento de extorsión
Ponderación: FACTOR_CAP400 (factor de expansión del capítulo 400)

Representatividad: nacional urbano, departamentos y ciudades principales (CIUDADSEG).
NO es representativa a nivel distrital — el factor de subregistro se aplica por dominio.

Salida: OUTPUTS_DASHBOARD/enapres_extorsion.json
"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(BASE, "ENAPRES_2025", "CAP_400_URBANO_4.csv")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "enapres_extorsion.json")

W = "FACTOR_CAP400"

MOTIVOS_NO_DENUNCIA = {
    1: "Miedo a represalias del agresor",
    2: "Es una pérdida de tiempo",
    3: "Desconfía de la Policía",
    4: "No se consumó el hecho",
    5: "Delito de poca importancia",
    6: "Desconoce al delincuente",
    7: "Otro",
}

COLS = [
    "NOMBREDD", "CIUDADSEG", W,
    "P402_11",              # cree que será víctima de extorsión (próx. 12 meses)
    "P424_19", "P428_19", "P433_19",  # extorsión: víctima / denunció / motivo no denuncia
    "P424_20", "P428_20", "P433_20",  # intento de extorsión
]


def indicadores(d: pd.DataFrame, label: str) -> dict:
    resp = d[d["P424_19"].notna()]
    vic = resp[resp["P424_19"] == 1]
    den = vic[vic["P428_19"] == 1]
    vic_any = resp[(resp["P424_19"] == 1) | (resp["P424_20"] == 1)]

    w_resp, w_vic, w_den = resp[W].sum(), vic[W].sum(), den[W].sum()
    tasa_vic = 100 * w_vic / w_resp if w_resp else None
    tasa_vic_any = 100 * vic_any[W].sum() / w_resp if w_resp else None
    tasa_den = 100 * w_den / w_vic if w_vic else None

    temor_resp = d[d["P402_11"].notna()]
    temor = (100 * temor_resp[temor_resp["P402_11"] == 1][W].sum() / temor_resp[W].sum()
             if len(temor_resp) else None)

    # Motivos de no denuncia (extorsión consumada + intento, ponderado)
    nd = d[((d["P424_19"] == 1) & (d["P428_19"] == 2) & d["P433_19"].notna())]
    nd_int = d[((d["P424_20"] == 1) & (d["P428_20"] == 2) & d["P433_20"].notna())]
    mot = pd.concat([
        nd.groupby("P433_19")[W].sum(),
        nd_int.groupby("P433_20")[W].sum(),
    ]).groupby(level=0).sum()
    motivos = {}
    if mot.sum() > 0:
        motivos = {MOTIVOS_NO_DENUNCIA[int(k)]: round(100 * v / mot.sum(), 1)
                   for k, v in mot.items() if int(k) in MOTIVOS_NO_DENUNCIA}

    return {
        "dominio": label,
        "n_respondentes": int(len(resp)),
        "n_victimas_extorsion": int(len(vic)),
        "n_victimas_intento": int(len(resp[resp["P424_20"] == 1])),
        "tasa_victimizacion_extorsion_pct": round(tasa_vic, 2) if tasa_vic is not None else None,
        "tasa_victimizacion_ext_o_intento_pct": round(tasa_vic_any, 2) if tasa_vic_any is not None else None,
        "tasa_denuncia_pct": round(tasa_den, 1) if tasa_den is not None else None,
        "cifra_negra_pct": round(100 - tasa_den, 1) if tasa_den is not None else None,
        "victimas_por_denuncia": round(100 / tasa_den, 1) if tasa_den else None,
        "temor_extorsion_pct": round(temor, 1) if temor is not None else None,
        "motivos_no_denuncia_pct": motivos,
    }


def main():
    print(f"Leyendo {CSV} ...")
    df = pd.read_csv(CSV, usecols=COLS, low_memory=False)
    print(f"{len(df):,} registros")

    dominios = {
        "Nacional urbano": df,
        "Lima + Callao (ciudad)": df[df["CIUDADSEG"].isin(["LIMA", "CALLAO"])],
        "Lima (ciudad)": df[df["CIUDADSEG"] == "LIMA"],
        "Callao (ciudad)": df[df["CIUDADSEG"] == "CALLAO"],
        "La Libertad (depto.)": df[df["NOMBREDD"] == "LA LIBERTAD"],
        "Trujillo (ciudad)": df[df["CIUDADSEG"] == "TRUJILLO"],
    }

    out = {
        "fuente": "INEI — ENAPRES 2025, Cap. 400 Seguridad Ciudadana (urbano, 15+ años)",
        "ponderacion": "FACTOR_CAP400",
        "nota_metodologica": (
            "Extorsión = delito 19; intento de extorsión = delito 20. "
            "Representatividad: nacional urbano, departamentos y ciudades principales; "
            "NO representativa a nivel distrital. Tasas ponderadas con factor de expansión. "
            "La tasa de denuncia se calcula sobre víctimas de extorsión consumada; "
            "los motivos de no denuncia agregan extorsión consumada e intento."
        ),
        "dominios": [indicadores(d, k) for k, d in dominios.items()],
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK -> {OUT}")
    for d in out["dominios"]:
        print(f"  {d['dominio']}: vict={d['tasa_victimizacion_extorsion_pct']}% "
              f"denuncia={d['tasa_denuncia_pct']}% cifra_negra={d['cifra_negra_pct']}% "
              f"(n_vic={d['n_victimas_extorsion']})")


if __name__ == "__main__":
    main()
