# 🛡️ GeoEscudo

**Plataforma pública de inteligencia territorial contra la extorsión en entornos
escolares de Lima Metropolitana y el Callao.**

Proyecto finalista del Hackathon **RedPública Transforma** (PNUD Perú,
UNDP-PER-00940) — Edición Seguridad Ciudadana, 2026.

## Qué hace

GeoEscudo mide las dos caras de la extorsión escolar:

- **La que se denuncia:** 14,319 denuncias de extorsión (PNP/SIDPOL, 2025–26).
  El 49.5% ocurrió a ≤100 m de un colegio activo; el 79% a ≤200 m (mediana: 105 m).
- **La que se calla:** según ENAPRES 2025 (INEI), el **73.3% de las víctimas de
  extorsión en Lima y Callao no denuncia**. El 58% de la no-denuncia a nivel
  nacional se explica por miedo a represalias o desconfianza en la Policía.

Sobre esa evidencia, la plataforma prioriza instituciones educativas mediante el
**Índice de Exposición Escolar a la Extorsión (IEEE)** y articula **encuentros
escuela–policía** (enfoque *community policing* / justicia procedimental) para
convertir cercanía en confianza, y confianza en denuncia.

## Estructura

```
app.py                  Dashboard Streamlit (4 actos narrativos)
data/                   Datos procesados que consume la app
  ├── dashboard_bienestar_docente.xlsx   KPIs y agregados SIDPOL × MINEDU
  ├── enapres_extorsion.json             Cifra negra por dominio (ENAPRES 2025)
  ├── proximidad_verificada.json         Distancias denuncia→IIEE verificadas
  └── mapa_geoescudo.html                Mapa interactivo (folium, ~3.4 MB)
etl/                    Pipelines reproducibles (requieren los datos crudos)
  ├── etl_enapres.py       ENAPRES 2025 Cap.400 → indicadores de cifra negra
  ├── etl_proximidad.py    SIDPOL + Padrón Web → distancias verificadas
  └── etl_mapa.py          Genera el mapa interactivo ligero
```

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Los ETL requieren además `geopandas` y `folium`, y los datos crudos (no
versionados por tamaño): microdatos ENAPRES 2025 (INEI), capa de extorsión del
observatorio SIDPOL (MININTER/ArcGIS) y Padrón Web de IIEE (MINEDU). Las fuentes
y cortes están documentados en la pestaña **Metodología** de la app.

## Principios

- **Bien público:** código y metodología abiertos, replicables a otras regiones
  (La Libertad: victimización 3× la nacional y cifra negra de 89.8%).
- **Privacidad desde el diseño:** la vista pública muestra agregados y niveles de
  exposición, no denuncias individuales atribuibles.
- **Honestidad metodológica:** ENAPRES es representativa por dominio (ciudad /
  departamento), no distrital; el ajuste por subregistro se aplica en ese nivel.

## Equipo

Xiomara Salas · Gabriel Riega · Carlos Crespín · André Rodríguez · Jaime Olivas
