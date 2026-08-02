# MEMORIA DEL PROYECTO — GeoEscudo

> Documento de referencia único para retomar el trabajo en cualquier momento, en cualquier sesión nueva. Reúne el contexto del concurso, el objetivo de la propuesta, el estado del producto, la arquitectura técnica completa, la organización de carpetas y archivos, los repositorios y enlaces, y los pendientes.
>
> **Nota sobre fechas:** este documento describe *qué* existe y *en qué estado*, no *cuándo* se hizo. No contiene fechas ni cuentas regresivas — para el cronograma oficial del concurso, ver `bases-hackathon-redpublica.md`.

---

## 1. Índice

1. [Índice](#1-índice)
2. [El concurso: RedPública Transforma (PNUD)](#2-el-concurso-redpública-transforma-pnud)
3. [La propuesta: GeoEscudo](#3-la-propuesta-geoescudo)
4. [Estado actual del producto](#4-estado-actual-del-producto)
5. [Arquitectura técnica](#5-arquitectura-técnica)
6. [Mapa de carpetas y archivos](#6-mapa-de-carpetas-y-archivos)
7. [Repositorios, despliegues y enlaces](#7-repositorios-despliegues-y-enlaces)
8. [Documentos clave del proyecto](#8-documentos-clave-del-proyecto)
9. [Decisiones técnicas y aprendizajes importantes](#9-decisiones-técnicas-y-aprendizajes-importantes)
10. [Identidad visual y logos](#10-identidad-visual-y-logos)
11. [Pendientes y próximos pasos](#11-pendientes-y-próximos-pasos)
12. [Cómo continuar en una sesión nueva](#12-cómo-continuar-en-una-sesión-nueva)

---

## 2. El concurso: RedPública Transforma (PNUD)

- **Convocatoria:** Hackathon RedPública Transforma, edición Seguridad Ciudadana.
- **Organiza:** Programa de las Naciones Unidas para el Desarrollo (PNUD), en alianza con Equipu (Red de Innovación y Emprendimiento) y SENAJU (Secretaría Nacional de la Juventud).
- **Número de Innovation Challenge en la plataforma QUANTUM:** `UNDP-PER-00940`.
- **Documento fuente completo:** [`bases-hackathon-redpublica.md`](bases-hackathon-redpublica.md) (transcripción en Markdown) y [`undp-per-00940_bases-hackaton.pdf`](undp-per-00940_bases-hackaton.pdf) (PDF oficial).

### Desafío al que responde la convocatoria

> ¿Cómo pueden las juventudes generar soluciones e intervenciones innovadoras para prevenir la violencia y fortalecer la seguridad ciudadana en sus comunidades?

### Perfil de postulantes

Organizaciones, colectivos y equipos juveniles de **Lima y La Libertad**, equipos multidisciplinarios de mínimo 4 jóvenes entre 18 y 29 años.

### Ejes temáticos de la convocatoria

- Prevención comunitaria de la violencia juvenil
- Recuperación de espacios públicos seguros
- Tecnología y datos para la seguridad ciudadana
- Redes comunitarias de prevención
- Participación juvenil en seguridad y convivencia

### Etapas del proceso

1. Convocatoria y postulación (descripción del problema, solución, resultados esperados, perfil del equipo, video de motivación).
2. Preselección de 5 equipos finalistas.
3. Hackathon presencial con mentoría técnica y pitch final ante jurado.
4. Fondo de Innovación Juvenil: 2 propuestas ganadoras acceden a hasta **S/ 10,000** para pilotear la solución en 60 días.

**GeoEscudo quedó entre los 5 equipos finalistas** y se encuentra en la etapa de mentoría/preparación del pitch presencial.

### Criterios de evaluación (100 puntos)

| Categoría | Subcriterio | Puntaje |
|---|---|---|
| Innovación de la propuesta | Impacto potencial en juventudes y comunidad | 20 |
| | Relevancia frente al problema de seguridad ciudadana | 20 |
| | Pertinencia territorial y enfoque de equidad | 20 |
| Viabilidad de la propuesta | Viabilidad técnica y financiera | 20 |
| | Escalabilidad y sostenibilidad | 10 |
| | Capacidad del equipo | 10 |

### Compromisos del equipo ganador

Implementar el piloto en un plazo de 60 días, participar en mentorías, presentar reportes de avance e informe final, documentar aprendizajes, y participar en actividades de visibilidad del PNUD/RedPública.

### Propiedad de las soluciones

Las propuestas se tratan como **bienes públicos**: el PNUD puede utilizar, reproducir, adaptar, implementar y escalar las soluciones, y las licencias otorgadas son no exclusivas, permanentes y transferibles. El equipo conserva el reconocimiento de autoría pero no exclusividad.

### Contacto oficial de la convocatoria

📧 `redpublica.pe@undp.org` · Plataforma de postulación: `supplier.quantum.partneragencies.org`

---

## 3. La propuesta: GeoEscudo

### 3.1 El problema (versión reorientada — vigente)

El problema central **no es únicamente la exposición al riesgo de extorsión en el entorno escolar**, sino **la desconfianza que produce el silencio**: la brecha entre la extorsión que efectivamente ocurre (victimización) y la que llega a denunciarse. La extorsión escolar es el escenario donde ese silencio es más grave, porque protege menos a quien más debería estar protegido.

**Frase eje del pitch:** *"Medimos el silencio para romperlo."*

Alcance: extorsión, entorno de instituciones educativas, Lima Metropolitana y Callao (con La Libertad como caso de escalabilidad, dado que también es región elegible de la convocatoria).

### 3.2 El modelo: sistema integrado 50/50

La propuesta dejó de estar organizada como "plataforma (componente 1) + talleres comunitarios (componente 2)" y pasó a un **ciclo de dos mitades iguales**:

```
   DATO                VIABILIDAD              TERRITORIO              DATO (retorno)
Los índices      →   Se filtra el ranking  →  Ciclo de encuentros  →  Los resultados de
IEEE / IBC           por qué sitios tienen     comunidad-escuela-       confianza y la
priorizan            comisaría/UGEL/           policía: se escucha,    cartografía social
distritos e IIEE     municipio dispuestos      se mide, se genera      retroalimentan la
                     a participar              contacto positivo       plataforma
```

- **Mitad "plataforma"**: dos índices geoespaciales complementarios.
  - **IEEE — Índice de Exposición Escolar a la Extorsión**: densidad y proximidad de denuncias SIDPOL respecto a instituciones educativas, ponderada por población escolar expuesta.
  - **IBC — Índice de Brecha de Confianza** (nuevo, protagonista del modelo reorientado): por distrito, compara el **percentil relativo** de denuncias registradas contra el percentil relativo de una señal de desconfianza construida con ENAPRES (inseguridad dentro de instituciones educativas + mala calificación de la comisaría + mala calificación de la atención pronta de la PNP). Se usan percentiles —no valores crudos— para poder comparar honestamente un conteo (denuncias) contra porcentajes (percepción), y solo se calcula entre distritos con muestra ENAPRES suficiente (n≥80 en el módulo de percepción). Una brecha alta significa que el distrito desconfía proporcionalmente más de lo que denuncia.

- **Mitad "programa comunitario"**: ciclo completo de 4 sesiones en 2–3 IIEE priorizadas por IBC/IEEE + viabilidad institucional real (existencia de comisaría/UGEL/municipio dispuestos a participar):
  1. **Línea base** — encuesta corta a estudiantes (confianza, conocimiento de rutas de denuncia, disposición a denunciar; ítems adaptados del marco de justicia procedimental de Tom Tyler) + entrevista semiestructurada a docentes/directivos.
  2. **Encuentro con la comisaría** — la Oficina de Participación Ciudadana (OPC) o el comisario explican cómo opera un caso de extorsión (ruta de denuncia, protección de identidad, seguimiento); entrevista semiestructurada al responsable de la OPC.
  3. **Cartografía social** — estudiantes y vecinos marcan zonas y horarios de riesgo que el IEEE no captura; esta capa retroalimenta la plataforma.
  4. **Cierre** — segunda aplicación de la encuesta a estudiantes (mismo instrumento de la sesión 1) + devolución de resultados y registro de compromisos institucionales.

  Diseño de medición: **antes/después en los mismos sitios**, sin grupo de comparación (limitación reconocida explícitamente: no aísla el efecto del programa de otros factores externos, pero es la opción viable dado el plazo y presupuesto del piloto de 60 días).

### 3.3 Marco teórico: community policing

Fundamentado en una revisión de literatura de 17 fuentes académicas (ver [`Revision_Literatura_Community_Policing_Peru.docx`](Revision_Literatura_Community_Policing_Peru.docx)). Ideas centrales:

- **Justicia procedimental (Tom Tyler)**: la legitimidad institucional se construye sobre cuatro dimensiones — voz, neutralidad, respeto, confiabilidad. Marco usado para diseñar los encuentros comunidad-escuela-policía y los ítems de la encuesta.
- **Gill et al. (2014), revisión sistemática**: el *community policing* mejora de forma consistente la confianza y la legitimidad policial, con efectos más débiles sobre la reducción directa del delito. Esto calibra los indicadores de éxito del piloto: **el indicador primario es el aumento de confianza y de denuncia, no la caída del delito** (un aumento de denuncias en las zonas intervenidas se interpreta como éxito: la cifra negra saliendo a la luz).
- **Peyton, Sierra-Arévalo y Rand (2019), experimento aleatorizado en PNAS**: un solo contacto breve y no coercitivo entre policía y vecino aumenta significativamente la legitimidad percibida — cita central que sustenta el diseño de los "encuentros con la comisaría".
- **Vacío de investigación en Perú**: Huaytalla (2019), Ramos Arias (2018) y Oviedo Maravi/PLAMOVE (2021) documentan que no existen evaluaciones rigurosas de programas de participación ciudadana en seguridad en el país — el piloto de GeoEscudo se posiciona como la primera línea de base de este tipo.
- **Riesgos reconocidos**: vigilantismo y privacidad de datos (modelo de referencia: proyecto europeo CITYCoP, "privacy by design"), y desplazamiento espacial del delito hacia zonas no intervenidas (Blattman et al. 2021, Bogotá) — el diseño de la plataforma contempla monitorear zonas adyacentes a las priorizadas.

### 3.4 Diferenciación frente a otras iniciativas

- **Frente a SíseVe (MINEDU)**: SíseVe registra violencia intraescolar (entre estudiantes, o de personal a estudiantes); GeoEscudo mide la amenaza criminal **externa** al entorno escolar.
- **Alineación institucional**: la propuesta se conecta con la campaña MININTER-DGCO "Tu Denuncia, Nuestra Fuerza" y con las estructuras ya existentes (BAPE — Brigadas de Autoprotección Escolar, OPC de comisarías, CODISEC) en lugar de crear institucionalidad paralela.

### 3.5 Equipo

Cinco integrantes: **Xiomara Salas Vega** (representante legal), **Gabriel Riega Nuñez**, **Carlos Crespín Juarez**, **André Rodríguez**, **Jaime Olivas Vera**. Perfil: científicos sociales con formación en ciencia de datos y experiencia en estudios de crimen y seguridad ciudadana en el Perú (incluye trabajo previo con el Instituto de Análisis Estratégico de la PUCP y con el Ministerio del Interior).

**Roles de campo propuestos** para el piloto (mapeo a personas pendiente de confirmar):
- Coordinación institucional → conduce la entrevista al comisario/OPC.
- Ciencia de datos → diseña la encuesta a estudiantes, procesa resultados pre/post, calcula el IBC.
- Plataforma web → mantiene y evoluciona el dashboard.
- Campo y facilitación → conduce las 4 sesiones del ciclo y las entrevistas a docentes/directivos.
- Comunicación y sistematización → transcribe entrevistas (con Plaud AI, ya presupuestado) y redacta el informe final.

### 3.6 Presupuesto (S/ 10,000, piloto de 60 días)

| Rubro | Monto vigente | Nota |
|---|---|---|
| 1. Servicios técnicos especializados (datos, geoespacial, desarrollo, sistematización, coordinación) | S/ 4,000 | Sin cambios |
| 2. Herramientas de IA y productividad (Claude Pro ×5, Plaud AI Pro) | S/ 1,780 | Sin cambios |
| 3. Plataforma web e infraestructura tecnológica | **S/ 400** (antes S/ 1,120) | Ajuste propuesto: al desplegar en hosting gratuito (Vercel/Netlify/Streamlit Cloud) sobra presupuesto de infraestructura |
| 4. Trabajo de campo y validación comunitaria | **S/ 2,070** (antes S/ 1,350) | Ajuste propuesto: cubre el ciclo completo de 4 sesiones en 2–3 IIEE en vez de un evento puntual en 3–5 IIEE |
| 5. Productos de conocimiento y transferencia (Policy Brief, guía IEEE, kit de herramientas) | S/ 1,000 | Sin cambios |
| 6. Comunicación y difusión comunitaria | S/ 750 | Sin cambios |
| **Total** | **S/ 10,000** | El ajuste de los rubros 3 y 4 está propuesto, no confirmado formalmente en el formulario oficial todavía |

### 3.7 Resultados esperados (R1–R6, versión reescrita para el modelo 50/50)

| # | Resultado | Mitad del sistema |
|---|---|---|
| R1 | Dashboard público operativo con dos capas filtrables por distrito: IEEE (exposición) e IBC (brecha de confianza) | Plataforma |
| R2 | Índice de Brecha de Confianza construido y documentado (ENAPRES × SIDPOL), con nota metodológica pública sobre representatividad y límites | Plataforma |
| R3 | Ciclo completo de encuentros comunidad-escuela-policía realizado en 2–3 IIEE priorizadas por IBC + viabilidad institucional | Programa |
| R4 | Primera línea de base de confianza policía-comunidad en entorno escolar documentada en el Perú (encuesta pre/post + entrevistas) | Programa |
| R5 | Entregas institucionales formales del dashboard y hallazgos a comisarías, UGEL y/o municipios, con registro de compromisos asumidos | Ambas |
| R6 | Metodología, código e instrumentos sistematizados en repositorio abierto, replicables a otros distritos y a La Libertad | Ambas |

---

## 4. Estado actual del producto

### 4.1 Cifras vigentes (las que debe citar el pitch)

> Estas son las cifras **verificadas y defendibles**, recalculadas tras corregir un artefacto de geocodificación de SIDPOL (ver sección 9). Cualquier cifra que aparezca en documentos más antiguos de la carpeta `POSTULACION/` (p. ej. "72.5% a ≤100m") **ya no es la vigente** — quedó reemplazada por lo siguiente:

- **15,213** denuncias de extorsión en Lima Metropolitana y Callao (fuente: PNP/SIDPOL-DGIS, observatorio MININTER).
- De las denuncias con **geolocalización precisa** (una fracción del total: SIDPOL georreferencia al centroide del distrito las direcciones que no puede geocodificar — ver sección 9):
  - **43.7%** ocurre a ≤100 metros de un colegio activo.
  - **81.9%** ocurre a ≤200 metros.
  - Mediana: **112 metros**.
- **5,424** locales educativos con al menos una denuncia en su entorno inmediato (≤100 m) — **29.7%** del total de locales activos en Lima y Callao.
- **508,958** alumnos y docentes expuestos (según Censo Educativo, en los locales afectados).
- **Cifra negra (Lima+Callao, ENAPRES 2025): 73.3%** de las víctimas de extorsión no denuncia. Es decir, por cada denuncia registrada hay aproximadamente **4 víctimas reales**.
- Motivos de no denuncia con mayor peso: miedo a represalias, desconfianza en la Policía y percepción de que "es una pérdida de tiempo" — en conjunto explican la mayoría del silencio.
- **La Libertad** (la otra región elegible de la convocatoria) muestra una victimización por extorsión ~3× la nacional y una cifra negra de ~90% — argumento directo de escalabilidad de la metodología.
- Distritos con mayor **Índice de Brecha de Confianza** (desconfianza desproporcionadamente alta frente a su volumen de denuncias): **Villa María del Triunfo** y **Villa El Salvador**. Nota importante para el discurso: Villa El Salvador no tiene pocas denuncias en términos absolutos — tiene denuncias insuficientes para su nivel de desconfianza. San Juan de Lurigancho, el distrito con más denuncias de toda Lima, muestra en cambio la relación más proporcional entre desconfianza y denuncia.

### 4.2 Qué funciona hoy en el dashboard

La aplicación (`GEOESCUDO_APP/app.py`, Streamlit) tiene 5 pestañas:

1. **① El riesgo** — el mapa "sala de comando" (ver sección 5.3): heatmap de densidad de denuncias, círculos de locales educativos afectados, coropleta de distritos por IBC, panel lateral completo al hacer clic en un distrito. Debajo: gráfico de proximidad por umbrales de distancia, evolución mensual de denuncias, top distritos, denuncias por turno.
2. **② La cifra negra** — análisis ENAPRES de victimización vs. denuncia, motivos de no denuncia, comparación de dominios (Lima, Callao, nacional, La Libertad). *(Pendiente: aún no se actualizó el lenguaje de esta pestaña para hablar explícitamente en términos del IBC — ver sección 11.)*
3. **③ Dónde actuar** — detalle del IEEE: top distritos e IIEE por exposición, exposición por tipo de gestión educativa.
4. **④ La respuesta** — el marco de community policing: la cadena "cercanía → confianza → denuncia", la línea de base de confianza comunidad-policía (ENAPRES: % que califica mal a su comisaría, a la PNP, etc.), los módulos del piloto y cómo se medirá el éxito.
5. **Metodología** — fuentes de datos, métodos, honestidad metodológica (representatividad de ENAPRES, filtro de geocodificación, efecto desplazamiento), referencias académicas.

### 4.3 Qué se decidió NO hacer (para que quede registrado y no se repita la discusión)

- **No se migra a una SPA en React/MapLibre-deck.gl.** Se evaluó y se aprobó esa arquitectura en un momento del proyecto, pero se revirtió la decisión: construir todo dentro de la app Streamlit ya desplegada (embebiendo piezas HTML/JS a medida cuando hace falta más control visual) es la vía de menor riesgo. GitHub Pages queda como opción secundaria si en algún momento se decide independizar el mapa de Streamlit.
- **No se usan barras 3D (pydeck/deck.gl) para representar el IBC.** Se probaron y no convencieron visualmente; se reemplazaron por el mapa "sala de comando" (heatmap + círculos + coropleta + panel).
- **No se agrega el diagrama de "flujo institucional"** (escuela → municipalidad → UGEL → comisaría → emergencia) al panel del mapa. Se diseñó una maqueta de cómo quedaría, pero se decidió mantener el panel actual tal como está.

---

## 5. Arquitectura técnica

### 5.1 Principio general

Separación estricta entre **datos crudos** (pesados, no se versionan en el repo de despliegue), **pipelines ETL** (scripts Python que procesan los crudos y producen JSON/HTML livianos) y **presentación** (la app Streamlit, que solo lee los archivos ya procesados). La app nunca hace cómputo pesado en vivo ni toca los datos crudos directamente.

```
Datos crudos (MINEDU/, ENAPRES_2025/)
        │
        ▼  scripts ETL (GEOESCUDO_APP/etl_*.py)
        │
Datos procesados (OUTPUTS_DASHBOARD/*.json, */geojson/*.geojson, mapa_comando.html)
        │
        ▼  se copian a mano a geoescudo-repo/data/ y /static/
        │
App Streamlit (GEOESCUDO_APP/app.py  ≡  geoescudo-repo/app.py)
        │
        ▼  git push
        │
GitHub → Streamlit Community Cloud (despliegue público)
```

### 5.2 Los scripts ETL, en orden de ejecución

Todos viven en `GEOESCUDO_APP/` y se ejecutan con el intérprete del entorno conda `basilisco` (`D:\Anaconda\envs\basilisco\python.exe`), desde el directorio raíz del proyecto.

| Orden | Script | Qué hace | Entrada | Salida |
|---|---|---|---|---|
| 0 (opcional, solo si hay datos nuevos de MININTER) | `etl_mininter_incremental.py` | Descarga del observatorio ArcGIS del MININTER **solo los registros nuevos** (por OBJECTID), evitando re-descargar el histórico completo | Servicio ArcGIS remoto + CSV local más reciente | Nuevo `MINEDU/mininter_delitos_total_<timestamp>.csv` consolidado |
| 1 | `etl_proximidad.py` | Filtra denuncias con geolocalización precisa (excluye puntos de relleno/centroides distritales), calcula distancia de cada denuncia al local educativo activo más cercano, identifica locales afectados y población expuesta, agrega por distrito | CSV de denuncias (el más reciente por *glob*) + Padrón Web MINEDU | `proximidad_verificada.json` |
| 2 | `etl_agregados.py` | Línea de tiempo mensual y denuncias por turno (reemplaza al antiguo xlsx) | CSV de denuncias | `agregados_sidpol.json` |
| 3 | `etl_enapres.py` | Indicadores de cifra negra por dominio (Lima, Callao, nacional, La Libertad, etc.) a partir de ENAPRES | `ENAPRES_2025/CAP_400_URBANO_4.csv` | `enapres_extorsion.json` |
| 4 | `etl_enapres_distrital.py` | Indicadores de percepción por distrito (inseguridad en IIEE, calificación de comisaría/PNP) — solo distritos con n≥80 | ENAPRES + denuncias | `enapres_distrital.json` |
| 5 | `etl_ibc.py` | Calcula el Índice de Brecha de Confianza: percentiles de denuncias vs. percentiles de desconfianza, solo entre distritos con muestra suficiente | `enapres_distrital.json` + `proximidad_verificada.json` + `MINEDU/geofiles/DISTRITO.gpkg` (centroides) | `ibc_distrital.json` |
| 6 | `etl_geojson.py` | Exporta GeoJSON para el mapa: los 50 distritos de Lima+Callao con todas las propiedades IBC/IEEE embebidas, los locales educativos afectados, y los puntos de denuncia (geo precisa) para el heatmap | Todo lo anterior + CSV crudos + geofiles | `OUTPUTS_DASHBOARD/geojson/distritos.geojson`, `iiee_afectadas.geojson`, `heatmap_denuncias.geojson` |
| 7 | `build_mapa_comando.py` | Combina la plantilla HTML (`mapa_comando.template.html`) con los tres GeoJSON, embebiendo los datos directamente en el HTML final (autocontenido, sin *fetch* externo) | Plantilla + GeoJSON | `OUTPUTS_DASHBOARD/mapa_comando.html` **y** `GEOESCUDO_APP/static/mapa_comando.html` (esta segunda copia es la que sirve la app) |
| — | `etl_mapa.py` | Genera un mapa Folium alternativo (heatmap + clusters), más liviano que el original de 56 MB. **Ya no se usa en la app actual**, pero se conserva como opción secundaria | CSV de denuncias + Padrón | `OUTPUTS_DASHBOARD/mapa_geoescudo.html` (archivado, ver sección 6) |

**Regenerar todo desde cero**, en este orden, tras cualquier actualización de datos:
```bash
cd D:\HACKATON_RED_PUBLICA_PNUD
python GEOESCUDO_APP/etl_mininter_incremental.py   # solo si hay datos nuevos que descargar
python GEOESCUDO_APP/etl_proximidad.py
python GEOESCUDO_APP/etl_agregados.py
python GEOESCUDO_APP/etl_enapres.py
python GEOESCUDO_APP/etl_enapres_distrital.py
python GEOESCUDO_APP/etl_ibc.py
python GEOESCUDO_APP/etl_geojson.py
python GEOESCUDO_APP/build_mapa_comando.py
```
Luego copiar manualmente lo generado a `geoescudo-repo/data/` y `geoescudo-repo/static/`, y hacer commit + push (ver sección 7).

### 5.3 El mapa "sala de comando" (la pieza central de la interfaz)

- **Tecnología:** HTML/CSS/JS a medida, con **MapLibre GL JS** (mapas vectoriales/raster, motor open-source compatible con la API de Mapbox) y **Chart.js** para el mini-gráfico del panel. Basemap: teselas raster de CARTO ("dark_all", estética oscura tipo sala de operaciones).
- **Capas:** heatmap de densidad de denuncias (mono-ámbar), círculos de locales educativos afectados (tamaño = denuncias cercanas), coropleta de distritos por Índice de Brecha de Confianza (paleta divergente azul → gris neutro → ámbar → rojo). Chips para activar/desactivar cada capa.
- **Interacción:** clic en un distrito abre un panel lateral con: nombre y etiqueta de severidad de la brecha, métricas (denuncias, víctimas estimadas, índice de brecha, % de comisaría mal calificada), un mini-gráfico de barras comparando percentil de denuncias vs. percentil de desconfianza, y el detalle de exposición escolar (locales afectados, alumnos+docentes expuestos, top IIEE).
- **Cómo se integra a Streamlit** (detalle importante, ver sección 9): el HTML **no** se embebe como contenido inline (`st.components.v1.html`), porque los *Web Workers* internos de MapLibre no completan su trabajo dentro de un iframe `srcdoc`. En su lugar, el archivo se sirve como archivo real vía **Streamlit static file serving** (`enableStaticServing = true` en `.streamlit/config.toml`, carpeta `static/` junto a `app.py`) y se inserta un `<iframe src="/app/static/mapa_comando.html">` con `st.markdown(unsafe_allow_html=True)`.

### 5.4 Entorno de ejecución

- **Intérprete:** entorno conda `basilisco` (`D:\Anaconda\envs\basilisco\python.exe`) — tiene pandas, geopandas, folium, plotly, streamlit, pydeck (ya no se usa pero sigue instalado) y las demás dependencias del proyecto.
- **Lanzar la app localmente:** configurado en `.claude/launch.json` (perfil `geoescudo`, puerto 8510):
  ```bash
  D:/Anaconda/envs/basilisco/python.exe -m streamlit run GEOESCUDO_APP/app.py --server.port 8510 --server.headless true --browser.gatherUsageStats false
  ```
- **Config de Streamlit local:** `.streamlit/config.toml` en la raíz del proyecto, con `enableStaticServing = true` (imprescindible para que el mapa cargue).

---

## 6. Mapa de carpetas y archivos

> Leyenda: ✅ vigente y en uso activo · 🗄️ archivado (movido a una subcarpeta `_ARCHIVO_LEGADO/`, ya superado pero conservado por si acaso) · ⏳ dato reservado para expansión futura, no usado todavía.

```
HACKATON_RED_PUBLICA_PNUD/
│
├── MEMORIA.md                                    ✅ ESTE DOCUMENTO
├── bases-hackathon-redpublica.md                 ✅ Bases del concurso (transcripción Markdown)
├── undp-per-00940_bases-hackaton.pdf              ✅ Bases del concurso (PDF oficial)
├── Revision_Literatura_Community_Policing_Peru.docx ✅ Revisión de literatura académica (17 fuentes)
├── q.zip                                          🗄️ Prototipos HTML de referencia (ideas ya evaluadas
│                                                      e incorporadas parcialmente; ver sección 9)
│
├── GEOESCUDO_APP/                                ✅ CÓDIGO FUENTE — el motor del proyecto
│   ├── app.py                                        La app Streamlit (5 pestañas, ver sección 4.2)
│   ├── etl_mininter_incremental.py                   Descarga incremental del observatorio MININTER
│   ├── etl_proximidad.py                             Proximidad denuncia↔colegio, filtro de geocodificación
│   ├── etl_agregados.py                              Línea de tiempo y turnos
│   ├── etl_enapres.py                                Cifra negra por dominio (ENAPRES)
│   ├── etl_enapres_distrital.py                      Percepción por distrito (ENAPRES)
│   ├── etl_ibc.py                                     Índice de Brecha de Confianza
│   ├── etl_geojson.py                                 Exporta GeoJSON para el mapa
│   ├── etl_mapa.py                                    Mapa Folium alternativo (no usado en la app actual)
│   ├── build_mapa_comando.py                          Ensambla el mapa final autocontenido
│   ├── mapa_comando.template.html                     Plantilla HTML/JS/CSS del mapa (con placeholders)
│   ├── static/mapa_comando.html                       Mapa ya ensamblado — el que sirve la app en vivo
│   └── __pycache__/                                   (bytecode de Python, se regenera solo)
│
├── OUTPUTS_DASHBOARD/                             ✅ SALIDAS DE LOS ETL — se regeneran, no editar a mano
│   ├── proximidad_verificada.json                    ← etl_proximidad.py
│   ├── agregados_sidpol.json                         ← etl_agregados.py
│   ├── enapres_extorsion.json                        ← etl_enapres.py
│   ├── enapres_distrital.json                         ← etl_enapres_distrital.py
│   ├── ibc_distrital.json                             ← etl_ibc.py
│   ├── geojson/
│   │   ├── distritos.geojson                          ← etl_geojson.py
│   │   ├── iiee_afectadas.geojson                      ← etl_geojson.py
│   │   └── heatmap_denuncias.geojson                   ← etl_geojson.py
│   ├── mapa_comando.html                              ← build_mapa_comando.py (copia gemela de static/)
│   └── _ARCHIVO_LEGADO/                           🗄️ dashboard_bienestar_docente.xlsx (el xlsx legado que
│                                                      alimentaba la primera versión de la app),
│                                                      mapa_bienestar_cluster.html, mapa_geoescudo.html
│                                                      (versiones anteriores del mapa, ya superadas),
│                                                      mapa_iiee_extorsion.zip
│
├── geoescudo-repo/                                ✅ REPOSITORIO GIT DEL DESPLIEGUE (ver sección 7)
│   ├── app.py                                         Copia exacta de GEOESCUDO_APP/app.py
│   ├── requirements.txt                               streamlit, pandas, plotly (versiones fijadas)
│   ├── README.md
│   ├── .streamlit/config.toml                         Tema visual + enableStaticServing=true
│   ├── .gitignore                                     Excluye CSV crudos y datos pesados
│   ├── data/                                           Copia de los JSON de OUTPUTS_DASHBOARD/
│   ├── static/mapa_comando.html                        Copia del mapa ensamblado
│   └── etl/                                            Copia de todos los scripts ETL (documentación/histórico;
│                                                        no se ejecutan desde aquí, se ejecutan desde
│                                                        GEOESCUDO_APP/ en el proyecto de trabajo)
│
├── MINEDU/                                        ✅ DATOS CRUDOS — fuente SIDPOL/MININTER y MINEDU
│   ├── mininter_delitos_total_<timestamp>.csv         El CSV vigente (el de fecha más reciente; los scripts
│   │                                                    lo detectan automáticamente por *glob*)
│   ├── mininter_descarga_extraccion.ipynb             Notebook para la descarga COMPLETA inicial desde cero
│   │                                                    (distinto del script incremental — usar este solo si
│   │                                                    no existe ningún CSV local todavía)
│   ├── padron_iiee_peru_completo_todos_estados.csv    Padrón Web MINEDU (instituciones educativas)
│   ├── geofiles/                                       DISTRITO.gpkg, PROVINCIA.gpkg, DEPARTAMENTO.gpkg
│   │                                                    (límites político-administrativos, usados para
│   │                                                    centroides de distrito)
│   ├── Especificacion de la tabla de datos padron web.xlsx     Diccionario de variables del Padrón
│   ├── Especificacion de la tabla de datos locales adicionales.xlsx
│   ├── RESUMEN_REU_BIENESTAR_DOCENTE.txt              Transcripción de una reunión sobre bienestar docente
│   │                                                    (proyecto relacionado pero distinto de GeoEscudo;
│   │                                                    contexto de la alianza PUCP/MINEDU)
│   ├── PROGRAMA CULTURA DE LA DENUNCIA_13-05.docx     Documento de referencia de la campaña MININTER
│   ├── mininter_homicidio_20260520_*.csv/.geojson     ⏳ Otros delitos descargados, sin usar todavía —
│   ├── mininter_robo_20260520_*.csv/.geojson          ⏳ reservados para una futura expansión de alcance
│   ├── mininter_violencia_contra_mujer_*.csv/.geojson ⏳ (la propuesta ya menciona esta posibilidad)
│   └── _ARCHIVO_LEGADO/                           🗄️ Todo lo superado por GEOESCUDO_APP/, organizado en:
│       ├── mapas_html_viejos/                          Los mapas Folium de versiones anteriores del proyecto
│       │                                                (v1_buffer, v2_heatmap, v3_clusters, cluster,
│       │                                                markers, docente, y sus zips)
│       ├── notebooks_viejos/                           Los notebooks originales (mapa_bienestar_docente.ipynb,
│       │                                                mapa_iiee_extorsion.ipynb,
│       │                                                GEO_MERGING_MINEDU_DENUNCIAS_POLICIALES.ipynb) y el
│       │                                                streamlit_app.py original (superado por
│       │                                                GEOESCUDO_APP/app.py), y el xlsx legado
│       └── datos_crudos_superados/                     Formatos DBF/XLS/ZIP antiguos del Padrón (superados
│                                                        por el CSV consolidado), snapshots viejos del CSV
│                                                        de denuncias, y los CSV/GeoJSON de "extorsion_completo"
│                                                        (una extracción previa, ya reemplazada por
│                                                        mininter_delitos_total_*)
│
├── ENAPRES_2025/                                  ✅ Microdatos INEI (Encuesta Nacional de Programas
│   ├── CAP_400_URBANO_4.csv                            Presupuestales), capítulo 400 - Seguridad Ciudadana
│   ├── CUESTIONARIO_CAP_400_URBANO.pdf                 El cuestionario aplicado
│   ├── DICCIONARIO DE VARIABLES 2025 - CAP400.pdf      Diccionario de variables (imprescindible para
│   │                                                    entender los códigos de columnas)
│   ├── 1030-Ficha.pdf                                  Ficha técnica de la encuesta
│   └── 8370672-encuesta-nacional-de-programas-presupuestales-2025.pdf  Documento metodológico general
│
├── PLATAFORMA/                                    ✅ Documentos de la ETAPA FINAL del concurso
│   ├── ARGUMENTARIO_GEOESCUDO_COMMUNITY_POLICING.md   Argumentario extenso con el marco teórico completo,
│   │                                                    KPIs calibrados y respuestas preparadas al jurado
│   ├── Formulario de presentación de GeoEscudo .docx  El formulario de la etapa final
│   ├── INTEGRANTES_EQUIPO_GEOESCUDO.xlsx              Datos del equipo (nombres, DNI, correos)
│   ├── Presupuesto - 60 dias.xlsx                     El presupuesto detallado (versión previa al ajuste
│   │                                                    de rubros 3/4 propuesto en la sección 3.6)
│   └── BASES PNUD.pdf                                 Copia adicional de las bases oficiales
│
├── POSTULACION/                                   ✅ Documentos de la ETAPA 1 (postulación inicial)
│   ├── Formulario de presentación de iniciativas - GeoEscudo (LLENADO).docx   El formulario original enviado
│   ├── Formularios de presentación de iniciativas.docx    Plantilla en blanco
│   ├── Modelo de acuerdo - Desafío de Innovación.docx
│   ├── PROGRAMA CULTURA DE LA DENUNCIA_13-05.docx
│   ├── UNDP-PER-00940 BASES-HACKATON.pdf              (duplicado del PDF de bases)
│   └── Guía Registro Proveedores / cómo editar oferta / cómo presentar oferta / activar cuenta Quantum (PDFs)
│       — guías operativas de la plataforma QUANTUM
│
├── LOGOS/                                         ✅ Identidad visual oficial (ver sección 10)
│   ├── logo_pnud.png
│   └── logo_hackaton_zrzx56vlegn9g2gizeaxeotycg5z.png
│
├── _ARCHIVO_LEGADO/                                🗄️ Untitled-1.ipynb (notebook de exploración temprana,
│                                                       lectura de archivos DBF; sin contenido relevante hoy)
│
├── .claude/                                        Configuración del entorno de trabajo
│   ├── launch.json                                     Perfil de lanzamiento de la app (puerto 8510)
│   └── settings.local.json
│
└── .streamlit/config.toml                          enableStaticServing=true (necesario para el mapa)
```

### Nota sobre el volumen de datos

`MINEDU/` es la carpeta más pesada del proyecto por lejos (varios gigabytes), casi enteramente por los archivos ya archivados en `_ARCHIVO_LEGADO/` (snapshots históricos de denuncias, exportaciones GeoJSON completas de más de un gigabyte cada una, y los mapas Folium de versiones anteriores). Los datos realmente activos que usan los scripts ETL —el CSV de denuncias vigente, el Padrón MINEDU y los geofiles— son una fracción pequeña de eso. Si se necesita liberar espacio en disco, `_ARCHIVO_LEGADO/` es seguro de eliminar por completo (nada del pipeline actual lo referencia), pero se dejó movido en vez de borrado por si hiciera falta revisar el histórico.

---

## 7. Repositorios, despliegues y enlaces

| Recurso | URL / ubicación | Estado |
|---|---|---|
| Repositorio GitHub (código del despliegue) | `https://github.com/riegagabriel/geoescudo` | ✅ Activo, con historial completo de commits documentando cada cambio |
| Despliegue en Streamlit Community Cloud | `geoescudo-pnud.streamlit.app` | ⚠️ Se detectó en un momento que estaba configurado como **privado** (un visitante externo sin sesión ve "no tienes acceso"). Se solicitó cambiarlo a público desde *Settings → Sharing* en share.streamlit.io. **Falta confirmar que quedó público.** |
| Plataforma de postulación QUANTUM | `supplier.quantum.partneragencies.org` | Plataforma oficial del concurso, no un recurso propio del equipo |
| Informe de auditoría técnica y UI/UX (Artifact) | `https://claude.ai/code/artifact/7d4c6a95-f38e-4255-a7e0-4293cd842062` | Documento de referencia — diagnóstico inicial de la app, comparativa de tecnologías (se decidió NO seguir la recomendación de migrar a SPA, ver sección 4.3) |
| Propuestas estéticas (Artifact) | `https://claude.ai/code/artifact/02b9dbea-4a79-44dd-80fd-f1fdab205f55` | Tres direcciones visuales exploradas; la dirección "sala de comando/operativa" es la que terminó implementándose en el mapa |
| Síntesis del modelo reorientado 50/50 (Artifact) | `https://claude.ai/code/artifact/d137df81-3768-426f-9ef0-ffb7090fe531` | El documento donde se definió el IBC, el ciclo de 4 sesiones, los roles de campo y el presupuesto ajustado — ya confirmado e incorporado |
| Maqueta del panel con flujo institucional (Artifact) | `https://claude.ai/code/artifact/2c8fe44a-3c7d-4877-a4a0-37d02150c51b` | Comparación visual antes/después; **se decidió no implementar** — el panel se queda como está |

---

## 8. Documentos clave del proyecto

| Documento | Ubicación | Contenido |
|---|---|---|
| Bases del concurso | `bases-hackathon-redpublica.md`, `undp-per-00940_bases-hackaton.pdf` | Ver sección 2 |
| Revisión de literatura académica | `Revision_Literatura_Community_Policing_Peru.docx` | 17 fuentes sobre *community policing*, justicia procedimental, confianza institucional y evidencia de programas similares en Perú y América Latina |
| Argumentario de la etapa final | `PLATAFORMA/ARGUMENTARIO_GEOESCUDO_COMMUNITY_POLICING.md` | El desarrollo narrativo completo de los 5 pilares del pitch, con citas académicas, tabla de KPIs calibrados y respuestas preparadas a preguntas difíciles del jurado |
| Formulario de postulación (etapa 1) | `POSTULACION/Formulario de presentación de iniciativas - GeoEscudo (LLENADO).docx` | El formulario enviado originalmente — **contiene cifras ya superadas** (ver sección 9), útil como referencia histórica de la narrativa original |
| Formulario de la etapa final | `PLATAFORMA/Formulario de presentación de GeoEscudo .docx` | Versión más reciente del formulario |
| Presupuesto | `PLATAFORMA/Presupuesto - 60 dias.xlsx` | Versión previa al ajuste de rubros propuesto en la sección 3.6 |
| Datos del equipo | `PLATAFORMA/INTEGRANTES_EQUIPO_GEOESCUDO.xlsx` | Nombres, DNI y correos de los 5 integrantes |

---

## 9. Decisiones técnicas y aprendizajes importantes

Esta sección documenta *por qué* las cosas son como son, para no repetir investigación ya hecha.

### 9.1 La reconciliación de cifras de proximidad

El formulario original citaba "72.5% de denuncias a ≤100m de una IIEE". Esa cifra **no es reproducible**: el análisis que la generó usó un radio de 200 metros, no 100. Además, una versión intermedia del dashboard (16.2%) mezclaba unidades (comparaba ubicaciones únicas contra el total de denuncias). Las cifras vigentes (sección 4.1) fueron recalculadas desde cero con unidades consistentes.

### 9.2 El artefacto de geocodificación de SIDPOL

Al recalcular la proximidad se descubrió que una gran parte de las denuncias de SIDPOL está georreferenciada a un puñado de **puntos de relleno** (centroides distritales), no a la ubicación real del hecho: son denuncias cuya dirección no pudo geocodificarse automáticamente, y el sistema les asigna una coordenada genérica del distrito. Se detectan estadísticamente así: un punto con muchas denuncias (≥10) que además tiene muchas direcciones de texto distintas entre sí (>50% del total) es, casi con certeza, un centroide de relleno, no un lugar real.

**Todo el análisis de proximidad y el mapa usan solo el subconjunto de denuncias con geolocalización precisa**, excluyendo esos puntos de relleno. Este filtro está implementado en `etl_proximidad.py`, `etl_mapa.py` y `etl_geojson.py`, y se declara explícitamente como cobertura de datos en la interfaz (pestaña de Metodología) — se convirtió, de hecho, en un argumento más del pitch: la mala calidad de geocodificación de SIDPOL es otra "brecha de datos" que limita la capacidad de focalización de la propia Policía, exactamente el tipo de problema que GeoEscudo visibiliza.

### 9.3 El bug de los Web Workers en el iframe de Streamlit

Al integrar el mapa MapLibre GL JS dentro de Streamlit usando `st.components.v1.html()` (que embebe el contenido vía el atributo `srcdoc` de un iframe), el mapa cargaba el fondo (basemap raster) pero **ninguna de las capas de datos propias se dibujaba** — quedaban completamente invisibles, sin ningún error visible en consola.

**Diagnóstico:** MapLibre GL JS procesa las fuentes GeoJSON en *Web Workers* internos. Esos workers nunca terminan su trabajo dentro de un iframe `srcdoc`, incluso con los flags de sandbox más permisivos (`allow-scripts allow-same-origin`). El basemap raster sí funcionaba porque las imágenes raster no requieren workers (se decodifican de forma nativa). Confirmarlo requirió inyectar un `<script>` directamente dentro del `contentDocument` del iframe para poder leer variables declaradas con `const`/`let` en el script original — un dato técnico aparte a recordar: **acceder `iframe.contentWindow.miVariable` desde fuera del iframe NO funciona para variables `const`/`let` de nivel superior de un script clásico**; solo funciona para variables asignadas explícitamente a `window.algo`.

**Solución implementada:** el mapa se sirve como archivo real a través de la función de *static file serving* de Streamlit (`enableStaticServing = true` en `.streamlit/config.toml`, archivo colocado en una carpeta `static/` junto a `app.py`, servido automáticamente en la ruta `/app/static/<archivo>`), y se inserta un `<iframe src="/app/static/mapa_comando.html">` con `st.markdown(..., unsafe_allow_html=True)` — nunca con `components.v1.html`, para evitar anidar un segundo iframe con sandbox.

### 9.4 Metodología del Índice de Brecha de Confianza (IBC)

El primer intento de construir un "índice de brecha" comparó valores crudos (denuncias, un conteo, contra un porcentaje de desconfianza) — esto es estadísticamente inválido porque las dos variables no están en la misma escala. La solución fue calcular el **percentil relativo** de cada distrito en ambas variables, dentro del conjunto de distritos con muestra ENAPRES suficiente (n≥80), y definir la brecha como la diferencia entre esos dos percentiles. Esto sí es una comparación honesta y es lo que está implementado en `etl_ibc.py`.

### 9.5 Ideas evaluadas y no adoptadas (o adoptadas parcialmente)

- **Barras 3D por distrito (pydeck/deck.gl)** para representar el IBC: se implementó, se probó, y se descartó por decisión explícita — no convenció visualmente. Reemplazada por el mapa "sala de comando" (heatmap + círculos + coropleta).
- **Migración completa a una SPA en React + MapLibre/deck.gl**: se diseñó una arquitectura completa y se aprobó en un momento del proyecto, pero se revirtió por una reevaluación de plazos reales — se prefirió invertir el esfuerzo en mejorar la app Streamlit existente en lugar de reconstruir todo en un stack nuevo.
- **Diagrama de "flujo institucional"** (escuela → municipalidad → UGEL → comisaría → emergencia) en el panel del mapa, inspirado en dos prototipos HTML de referencia (`q.zip`): se construyó una maqueta comparativa completa, pero se decidió no implementarlo y dejar el panel actual como está.
- **Del contenido de `q.zip`** (dos prototipos HTML con datos parcialmente reales), lo que sí quedó como referencia de diseño para el futuro si se retoma: tarjetas de KPI con contador animado, tarjetas modales de "cómo leer el indicador / fuentes / acciones sugeridas" para reemplazar el bloque de texto largo de la pestaña de Metodología, y una "tarjeta de método" destacada explicando la metodología en la vista principal. Ninguna de estas se implementó todavía.

---

## 10. Identidad visual y logos

Carpeta `LOGOS/`, dos archivos:

| Archivo | Dimensiones | Formato | Uso |
|---|---|---|---|
| `logo_pnud.png` | 362 × 552 px | PNG, paleta indexada | Logo oficial del PNUD (Programa de las Naciones Unidas para el Desarrollo) — usar en materiales que requieran atribución institucional al organismo convocante |
| `logo_hackaton_zrzx56vlegn9g2gizeaxeotycg5z.png` | 1614 × 546 px | PNG, RGB | Logo oficial de la convocatoria RedPública Transforma / Hackathon — formato apaisado, apto para encabezados de documentos y presentaciones |

**Pendiente:** GeoEscudo todavía no tiene un logo o isotipo propio — solo se ha usado el emoji 🛡️ como marca provisional en el dashboard y los documentos. Si se decide crear una identidad visual propia para el proyecto, esta carpeta es el lugar natural donde debería vivir (junto a los dos logos institucionales ya existentes, que sí deben mantenerse y usarse en cualquier material oficial de cara al PNUD).

El sistema de color del dashboard (mapa "sala de comando" y resto de la app) usa una paleta azul/ámbar consistente en todos los materiales: azul (`#2563EB` / `#1E3A8A`) para lo "registrado/oficial", ámbar (`#D97706` / `#F0A24B`) reservado exclusivamente para representar la cifra negra / desconfianza. Esta paleta no está formalizada como marca (no hay un archivo de tokens de diseño separado), vive implícitamente en el CSS de `GEOESCUDO_APP/app.py` y `mapa_comando.template.html`.

---

## 11. Pendientes y próximos pasos

En orden aproximado de importancia, no de urgencia temporal:

1. **Confirmar que el despliegue en Streamlit Cloud está configurado como público.** Es el pendiente más simple y más importante: sin esto, nadie externo puede ver la app.
2. **Actualizar el lenguaje de la pestaña "② La cifra negra"** para hablar explícitamente en términos del IBC (hoy la pestaña muestra el análisis de cifra negra de ENAPRES, pero no usa todavía el nombre ni el marco del Índice de Brecha de Confianza que sí aparece en el mapa de la pestaña ①).
3. **Actualizar el formulario oficial de la etapa final y el guion del video de pitch** con: las cifras vigentes de la sección 4.1, la frase eje *"Medimos el silencio para romperlo"*, el modelo 50/50 y los resultados R1–R6 reescritos de la sección 3.7.
4. **Confirmar formalmente el ajuste de presupuesto** propuesto en la sección 3.6 (rubros 3 y 4) en el documento oficial `PLATAFORMA/Presupuesto - 60 dias.xlsx`.
5. **Confirmar el mapeo de roles de campo a personas específicas** del equipo (sección 3.5) — hoy son roles propuestos, no asignados a nombres.
6. **Completar el nodo de "comisaría" con datos reales** si en algún momento se retoma la idea del flujo institucional: requiere descargar la capa `COMISARIAS` del observatorio ArcGIS del MININTER (ya identificada en `etl_mininter_incremental.py`, nunca descargada) y cruzarla espacialmente contra cada distrito. El dato de UGEL por distrito ya está disponible (viene del Padrón Web MINEDU).
7. **Preparar el guion y los materiales del pitch presencial**, apoyándose en el argumentario ya escrito (`PLATAFORMA/ARGUMENTARIO_GEOESCUDO_COMMUNITY_POLICING.md`) y en las cifras y el modelo de este documento.
8. Ideas de pulido visual de baja prioridad, tomadas de `q.zip` y no implementadas todavía (ver sección 9.5): KPIs con contador animado, tarjetas modales para la pestaña de Metodología, tarjeta de método destacada en la vista principal.

---

## 12. Cómo continuar en una sesión nueva

**Para entender el proyecto:** leer este documento completo primero. Después, si hace falta el detalle narrativo del pitch, leer `PLATAFORMA/ARGUMENTARIO_GEOESCUDO_COMMUNITY_POLICING.md`.

**Para correr la app localmente:**
```bash
cd D:\HACKATON_RED_PUBLICA_PNUD
D:/Anaconda/envs/basilisco/python.exe -m streamlit run GEOESCUDO_APP/app.py --server.port 8510
```
(o usar el perfil `geoescudo` ya configurado en `.claude/launch.json` con las herramientas de preview del entorno de trabajo). Abrir `http://localhost:8510`.

**Para actualizar los datos:** ver la secuencia de comandos de la sección 5.2.

**Para desplegar un cambio:**
```bash
cd D:\HACKATON_RED_PUBLICA_PNUD
cp GEOESCUDO_APP/app.py geoescudo-repo/app.py
cp GEOESCUDO_APP/etl_*.py GEOESCUDO_APP/*.template.html geoescudo-repo/etl/
cp OUTPUTS_DASHBOARD/*.json geoescudo-repo/data/
cp GEOESCUDO_APP/static/mapa_comando.html geoescudo-repo/static/mapa_comando.html
cd geoescudo-repo
git add -A
git commit -m "mensaje descriptivo del cambio"
git push
```
El despliegue en Streamlit Community Cloud se actualiza solo tras el push (unos minutos de espera).

**Para saber qué está vigente y qué está archivado:** la sección 6 de este documento (mapa de carpetas) es la referencia; todo lo marcado 🗄️ está en una subcarpeta `_ARCHIVO_LEGADO/` y puede ignorarse con seguridad para el trabajo activo.

**Regla general de trabajo de esta sesión** (mantenerla): cualquier cifra nueva que se calcule debe salir de un script ETL versionado en `GEOESCUDO_APP/`, nunca de un cálculo manual suelto — así toda cifra que aparezca en el dashboard, el formulario o el pitch queda rastreable a su fuente.
