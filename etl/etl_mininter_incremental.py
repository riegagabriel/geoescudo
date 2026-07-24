# -*- coding: utf-8 -*-
"""
Extractor INCREMENTAL del observatorio SIDPOL (MININTER / ArcGIS FeatureServer).

En lugar de re-descargar la capa completa (~1.4M registros), detecta el último
OBJECTID presente en el CSV local más reciente y descarga solo los registros
nuevos (OBJECTID > max local), en páginas de 2,000 (límite del servidor).
El resultado se guarda como un nuevo CSV con la convención de nombres existente
(`mininter_<capa>_<timestamp>.csv` en MINEDU/), de modo que los ETL descendentes
—que seleccionan el archivo más reciente— lo tomen automáticamente.

Uso:
    python etl_mininter_incremental.py                     # DELITOS_TOTAL, incremental
    python etl_mininter_incremental.py --capa EXTORSION
    python etl_mininter_incremental.py --dry-run           # solo reporta cuántos faltan

Salvaguardas:
  * Si el máximo OBJECTID del servidor es MENOR que el local, el servicio fue
    republicado y los IDs ya no son comparables: se aborta pidiendo descarga
    completa (notebook mininter_descarga_extraccion.ipynb).
  * Se deduplica por OBJECTID al consolidar.
"""
import argparse
import glob
import json
import os
from datetime import datetime

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "MINEDU")
HEADERS = {"User-Agent": "Mozilla/5.0 (GeoEscudo ETL)"}
PAGE = 2000

CAPAS = {
    "EXTORSION": "https://services6.arcgis.com/lMIZrqiJkpM748BR/arcgis/rest/services/EXTORSION_IDSUBTIPO_10508/FeatureServer/1",
    "ROBO": "https://services6.arcgis.com/lMIZrqiJkpM748BR/arcgis/rest/services/ROBO_IDSUBTIPO_10502/FeatureServer/3",
    "HURTO": "https://services6.arcgis.com/lMIZrqiJkpM748BR/arcgis/rest/services/HURTO_IDSUBTIPO_10501/FeatureServer/2",
    "HOMICIDIO": "https://services6.arcgis.com/lMIZrqiJkpM748BR/arcgis/rest/services/HOMICIDIO_IDMODALIDAD_1010102_AL_1010130/FeatureServer/2",
    "VIOLENCIA_CONTRA_MUJER": "https://services6.arcgis.com/lMIZrqiJkpM748BR/arcgis/rest/services/VCM_IDTIPO_504/FeatureServer/0",
    "DELITOS_TOTAL": "https://services6.arcgis.com/lMIZrqiJkpM748BR/arcgis/rest/services/SIDPOL_DELITOS_TOTAL/FeatureServer/1",
}


def get_json(url, params):
    r = requests.get(url, params=params, headers=HEADERS, verify=False, timeout=60)
    r.raise_for_status()
    out = r.json()
    if "error" in out:
        raise RuntimeError(f"Error del servidor ArcGIS: {out['error']}")
    return out


def server_stats(url):
    count = get_json(url + "/query", {"where": "1=1", "returnCountOnly": "true",
                                      "f": "json"})["count"]
    stats = get_json(url + "/query", {
        "where": "1=1", "f": "json",
        "outStatistics": json.dumps([{"statisticType": "max",
                                      "onStatisticField": "OBJECTID",
                                      "outStatisticFieldName": "max_oid"}]),
    })
    max_oid = stats["features"][0]["attributes"]["max_oid"]
    return count, max_oid


def archivo_local_mas_reciente(capa):
    patron = os.path.join(DATA_DIR, f"mininter_{capa.lower()}_*.csv")
    archivos = sorted(glob.glob(patron))
    return archivos[-1] if archivos else None


def descargar_rango(url, oid_desde, oid_hasta):
    """Descarga features con OBJECTID en (oid_desde, oid_hasta]."""
    feats, offset = [], 0
    where = f"OBJECTID > {oid_desde} AND OBJECTID <= {oid_hasta}"
    while True:
        out = get_json(url + "/query", {
            "where": where, "outFields": "*", "outSR": 4326, "f": "json",
            "orderByFields": "OBJECTID", "resultOffset": offset,
            "resultRecordCount": PAGE,
        })
        page = out.get("features", [])
        feats.extend(page)
        if len(page) < PAGE and not out.get("exceededTransferLimit"):
            break
        offset += len(page)
    return feats


def features_a_df(feats):
    rows = []
    for f in feats:
        row = dict(f.get("attributes", {}))
        geom = f.get("geometry") or {}
        row["longitud"] = geom.get("x")
        row["latitud"] = geom.get("y")
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capa", default="DELITOS_TOTAL", choices=sorted(CAPAS))
    ap.add_argument("--dry-run", action="store_true",
                    help="solo reporta cuántos registros faltan, no descarga")
    args = ap.parse_args()
    url = CAPAS[args.capa]

    local = archivo_local_mas_reciente(args.capa)
    if not local:
        raise SystemExit(
            f"No hay CSV local para {args.capa} en {DATA_DIR}. Para la primera "
            "descarga completa usa el notebook mininter_descarga_extraccion.ipynb.")
    print(f"Base local: {os.path.basename(local)}")
    df_local = pd.read_csv(local, low_memory=False)
    max_local = int(df_local["OBJECTID"].max())
    print(f"  {len(df_local):,} registros · max OBJECTID local = {max_local:,}")

    count_srv, max_srv = server_stats(url)
    print(f"Servidor: {count_srv:,} registros · max OBJECTID = {max_srv:,}")

    if max_srv < max_local:
        raise SystemExit(
            "⚠️ El máximo OBJECTID del servidor es MENOR que el local: el servicio "
            "fue republicado y los IDs no son comparables. Se requiere descarga "
            "completa (notebook de extracción).")

    faltan = max_srv - max_local
    if faltan == 0:
        print("✅ Al día: no hay registros nuevos.")
        return
    print(f"→ {faltan:,} registros nuevos por descargar (OBJECTID {max_local + 1:,}"
          f"–{max_srv:,})")
    if args.dry_run:
        return

    nuevos = []
    for desde in range(max_local, max_srv, PAGE):
        hasta = min(desde + PAGE, max_srv)
        feats = descargar_rango(url, desde, hasta)
        nuevos.extend(feats)
        print(f"  OBJECTID {desde + 1:,}–{hasta:,}: +{len(feats):,} "
              f"(acumulado {len(nuevos):,})", flush=True)

    df_nuevos = features_a_df(nuevos)
    # Alinear al esquema local; reportar columnas nuevas del servidor si las hay
    extra = set(df_nuevos.columns) - set(df_local.columns)
    if extra:
        print(f"  Nota: columnas nuevas del servidor ignoradas: {sorted(extra)}")
    df_nuevos = df_nuevos.reindex(columns=df_local.columns)

    df_total = pd.concat([df_local, df_nuevos], ignore_index=True)
    df_total = df_total.drop_duplicates(subset="OBJECTID", keep="last")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = os.path.join(DATA_DIR, f"mininter_{args.capa.lower()}_{ts}.csv")
    df_total.to_csv(out_csv, index=False)
    print(f"✅ {len(df_total):,} registros consolidados -> {os.path.basename(out_csv)}")
    print("Siguiente paso: re-ejecutar etl_proximidad.py, etl_mapa.py y "
          "etl_enapres_distrital.py (toman el CSV más reciente automáticamente).")


if __name__ == "__main__":
    main()
