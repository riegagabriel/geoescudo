# -*- coding: utf-8 -*-
"""
Combina `mapa_comando.template.html` con los GeoJSON ya exportados
(etl_geojson.py) para producir un HTML autocontenido: el mapa "sala de
situación" (MapLibre GL JS + Chart.js) con los datos embebidos como JSON
inline (evita problemas de fetch()/CORS al incrustarlo vía iframe en
Streamlit, y lo deja listo también para GitHub Pages).

Salida: OUTPUTS_DASHBOARD/mapa_comando.html
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
GEO_DIR = os.path.join(BASE, "OUTPUTS_DASHBOARD", "geojson")
TEMPLATE = os.path.join(HERE, "mapa_comando.template.html")
OUT = os.path.join(BASE, "OUTPUTS_DASHBOARD", "mapa_comando.html")
# Streamlit solo sirve iframes con <src> real (no srcdoc) de forma confiable:
# los GeoJSON sources de MapLibre dependen de Web Workers, que no completan su
# trabajo dentro de un iframe srcdoc embebido vía st.components.v1.html.
# Se copia también a static/ para servir por /app/static/ con <iframe src=...>.
OUT_STATIC = os.path.join(HERE, "static", "mapa_comando.html")


def load_compact(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def main():
    distritos = load_compact(os.path.join(GEO_DIR, "distritos.geojson"))
    iiee = load_compact(os.path.join(GEO_DIR, "iiee_afectadas.geojson"))
    heatmap = load_compact(os.path.join(GEO_DIR, "heatmap_denuncias.geojson"))

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()

    html = html.replace("/*__DISTRITOS_GEOJSON__*/", distritos)
    html = html.replace("/*__IIEE_GEOJSON__*/", iiee)
    html = html.replace("/*__HEATMAP_GEOJSON__*/", heatmap)

    os.makedirs(os.path.dirname(OUT_STATIC), exist_ok=True)
    for path in (OUT, OUT_STATIC):
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"OK -> {path} ({os.path.getsize(path)/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
