# 🛡️ GeoEscudo

**Plataforma pública de inteligencia territorial contra la extorsión en entornos
escolares de Lima Metropolitana y el Callao.**

Proyecto finalista del Hackathon **RedPública Transforma** (PNUD Perú,
UNDP-PER-00940) — Edición Seguridad Ciudadana, 2026.

## Qué hace

GeoEscudo mide las dos caras de la extorsión escolar:

- **La que se denuncia:** 15,213 denuncias de extorsión (PNP/SIDPOL, corte
  31/05/2026). De las geolocalizables con precisión (27.6%), el 43.7% ocurrió a
  ≤100 m de un colegio activo y el 81.9% a ≤200 m (mediana: 112 m).
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
  ├── enapres_extorsion.json        Cifra negra por dominio (ENAPRES 2025)
  ├── enapres_distrital.json        Termómetro distrital referencial
  ├── agregados_sidpol.json         Línea de tiempo y turnos (SIDPOL)
  ├── proximidad_verificada.json    Distancias denuncia→IIEE verificadas
  └── mapa_geoescudo.html           Mapa interactivo (folium)
etl/                    Pipelines reproducibles (requieren los datos crudos)
  ├── etl_mininter_incremental.py   Descarga incremental del observatorio SIDPOL
  ├── etl_proximidad.py             SIDPOL + Padrón Web → distancias verificadas
  ├── etl_agregados.py              Línea de tiempo y turnos
  ├── etl_enapres.py                ENAPRES Cap.400 → cifra negra por dominio
  ├── etl_enapres_distrital.py      Termómetro distrital Lima y Callao
  └── etl_mapa.py                   Genera el mapa interactivo ligero
```

**Actualización de datos:** `python etl/etl_mininter_incremental.py` descarga solo
los registros nuevos del observatorio MININTER (por OBJECTID); luego se re-ejecutan
los demás ETL, que toman el CSV más reciente automáticamente.

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
