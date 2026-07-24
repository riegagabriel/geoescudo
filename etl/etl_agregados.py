# -*- coding: utf-8 -*-
"""
Agregados SIDPOL para el dashboard (reemplaza al xlsx legado del notebook):
  * Línea de tiempo mensual: extorsión simple vs. agravada
  * Denuncias por turno del hecho
  * Totales por subtipo

Ámbito: Lima Metropolitana + Callao. Usa TODAS las denuncias (los agregados
temporales y de turno no dependen de la calidad de geocodificación).
Toma automáticamente el CSV mininter_delitos_total_* más reciente.

Salida: OUTPUTS_DASHBOARD/agregados_sidpol.json
"""
import glob
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELITOS = sorted(glob.glob(os.path.join(BASE, "MINEDU", "mininter_delitos_total_*.csv")))[-1]
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "agregados_sidpol.json")


def main():
    print(f"Cargando {os.path.basename(DELITOS)} ...")
    cols = ["subtipo_hecho", "modalidad_hecho", "departamento_hecho", "turno_hecho",
            "año_hecho", "mes_hecho", "fecha_hora_registro_hecho"]
    dt = pd.read_csv(DELITOS, usecols=cols, low_memory=False)
    dt["subtipo_hecho"] = dt["subtipo_hecho"].astype(str).str.upper().str.strip()
    ext = dt[dt["subtipo_hecho"].str.contains("EXTORS")
             & dt["departamento_hecho"].isin(["LIMA METROPOLITANA", "CALLAO"])].copy()
    print(f"  {len(ext):,} denuncias de extorsión Lima Met.+Callao")
    # En la capa DELITOS_TOTAL la distinción simple/agravada está en modalidad_hecho
    print("  Modalidades:", ext["modalidad_hecho"].astype(str).value_counts().head(5).to_dict())
    ext["agravada"] = ext["modalidad_hecho"].astype(str).str.upper().str.contains("AGRAVADA")
    corte = pd.to_datetime(ext["fecha_hora_registro_hecho"], unit="ms",
                           errors="coerce").max()
    corte_str = corte.strftime("%d/%m/%Y") if pd.notna(corte) else "s/f"

    ext["periodo"] = (ext["año_hecho"].astype(int).astype(str) + "-"
                      + ext["mes_hecho"].astype(int).astype(str).str.zfill(2))
    lt = (ext.groupby(["periodo", "agravada"]).size().unstack(fill_value=0)
          .rename(columns={False: "extorsion", True: "extorsion_agravada"})
          .reset_index().sort_values("periodo"))
    lt["total"] = lt["extorsion"] + lt["extorsion_agravada"]

    tu = (ext.groupby(ext["turno_hecho"].astype(str).str.strip().str.lower())
          .size().rename("total").reset_index()
          .rename(columns={"turno_hecho": "turno"})
          .sort_values("total", ascending=False))

    out = {
        "fuente": f"PNP/SIDPOL-DGIS · corte {corte_str}",
        "corte": corte_str,
        "archivo_origen": os.path.basename(DELITOS),
        "ambito": "Lima Metropolitana + Callao",
        "total_denuncias": int(len(ext)),
        "total_extorsion": int((~ext["agravada"]).sum()),
        "total_extorsion_agravada": int(ext["agravada"].sum()),
        "linea_tiempo": lt.to_dict(orient="records"),
        "turnos": tu.to_dict(orient="records"),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK -> {OUT}")
    print(f"  Corte: {corte_str} · total {out['total_denuncias']:,} "
          f"(simple {out['total_extorsion']:,} / agravada "
          f"{out['total_extorsion_agravada']:,})")
    print(f"  Periodos: {lt['periodo'].iloc[0]} a {lt['periodo'].iloc[-1]}")


if __name__ == "__main__":
    main()
