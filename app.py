# -*- coding: utf-8 -*-
"""
GeoEscudo — Plataforma de inteligencia territorial contra la extorsión
en entornos escolares de Lima Metropolitana y el Callao.

Hackathon RedPública Transforma (PNUD, UNDP-PER-00940) — Etapa final.

Fuentes: MINEDU (Padrón Web / Censo Educativo), PNP SIDPOL-DGIS (observatorio
MININTER), INEI ENAPRES 2025 (Cap. 400 Seguridad Ciudadana).
"""
import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.components.v1 import html as st_html

# ── Configuración ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoEscudo — Extorsión en entornos escolares",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Rutas de datos: en el repo de despliegue los datos van en ./data ;
# en el entorno de desarrollo local, en ../OUTPUTS_DASHBOARD
_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATOS = [
    os.path.join(_HERE, "data"),
    os.path.join(os.path.dirname(_HERE), "OUTPUTS_DASHBOARD"),
]
OUT_DIR = next((p for p in _CANDIDATOS if os.path.isdir(p)), _CANDIDATOS[0])
ENAPRES_JSON = os.path.join(OUT_DIR, "enapres_extorsion.json")
PROX_JSON = os.path.join(OUT_DIR, "proximidad_verificada.json")
DIST_JSON = os.path.join(OUT_DIR, "enapres_distrital.json")
AGR_JSON = os.path.join(OUT_DIR, "agregados_sidpol.json")
MAPA_HTML = os.path.join(OUT_DIR, "mapa_geoescudo.html")

PLOTLY_CFG = {"displayModeBar": False}

# Paleta (una sola familia + acento cálido; emphasis por luminosidad, CVD-safe)
AZUL = "#2563EB"        # serie principal / denuncia registrada
AZUL_OSCURO = "#1E3A8A" # énfasis
AZUL_CLARO = "#93C5FD"  # contexto / de-énfasis
AMBAR = "#D97706"       # segunda serie fija / cifra negra
INK = "#374151"
INK_MUTED = "#6B7280"
GRID = "rgba(107,114,128,0.18)"

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.55rem; font-weight: 700; }
[data-testid="stMetricLabel"] { font-size: 0.8rem; color: #666; }
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1E3A8A;
    border-left: 4px solid #1E3A8A; padding-left: 10px; margin: 14px 0 8px 0;
}
.fuente { font-size: 0.72rem; color: #888; margin-top: 2px; }
.hero-claim {
    background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
    color: white; padding: 14px 20px; border-radius: 10px;
    font-size: 1.02rem; margin: 6px 0 14px 0;
}
.hero-claim b { color: #FDE68A; }
.pilar {
    border: 1px solid #E5E7EB; border-radius: 10px; padding: 14px 16px;
    height: 100%; background: #FAFAFA;
}
.pilar h4 { margin: 0 0 6px 0; color: #1E3A8A; font-size: 0.95rem; }
.pilar p { margin: 0; font-size: 0.85rem; color: #374151; }
</style>
""", unsafe_allow_html=True)


# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_json(path, mtime):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_json(path):
    return _load_json(path, os.path.getmtime(path)) if os.path.exists(path) else None


enapres = load_json(ENAPRES_JSON)
prox = load_json(PROX_JSON)
dist = load_json(DIST_JSON)
agr = load_json(AGR_JSON)

if not (enapres and prox and agr):
    st.error("Faltan datos procesados. Ejecuta los ETL de `GEOESCUDO_APP/` "
             "(etl_proximidad, etl_enapres, etl_enapres_distrital, etl_agregados).")
    st.stop()

CORTE = prox.get("corte", "s/f")


def dom(nombre):
    """Indicadores ENAPRES de un dominio."""
    if not enapres:
        return None
    for d in enapres["dominios"]:
        if d["dominio"] == nombre:
            return d
    return None


def fig_base(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        bargap=0.35,
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🛡️ GeoEscudo")
st.markdown("**Inteligencia territorial contra la extorsión en entornos escolares** · "
            "Lima Metropolitana y Callao · Hackathon RedPública Transforma (PNUD)")

lc = dom("Lima + Callao (ciudad)")
cifra_negra_lc = lc["cifra_negra_pct"] if lc else None
vxd = lc["victimas_por_denuncia"] if lc else None

st.markdown(
    f"""<div class="hero-claim">
    La extorsión escolar tiene dos caras: <b>la que se denuncia</b> — 4 de cada 10 denuncias
    geolocalizables en Lima y Callao ocurren a <b>≤100 metros de un colegio</b> — y <b>la que se calla</b>:
    el <b>{cifra_negra_lc if cifra_negra_lc else '—'}%</b> de las víctimas de extorsión no
    denuncia (ENAPRES 2025). GeoEscudo mide ambas — y actúa sobre la causa del silencio:
    <b>la desconfianza</b>.
    </div>""",
    unsafe_allow_html=True,
)

# KPIs hero
p100 = prox["umbrales"]["100"]
med = prox["mediana_distancia_m"]
af = prox["afectados_100m"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Denuncias de extorsión 2025–26", f"{prox['n_denuncias']:,}",
          help=f"PNP / SIDPOL-DGIS, Lima Metropolitana y Callao, corte {CORTE}")
c2.metric("A ≤100 m de un colegio", f"{p100['pct']}%",
          delta=f"mediana: {med:.0f} m", delta_color="off",
          help="Sobre las denuncias con geolocalización precisa "
               f"({prox['cobertura_geo_pct']}% del total): distancia al local educativo "
               "activo más cercano (UTM-18S). El resto se georreferencia al centroide "
               "distrital y se excluye del análisis de proximidad.")
c3.metric("Locales educativos afectados", f"{af['n_locales']:,}",
          delta=f"{af['pct_locales']}% del total", delta_color="inverse",
          help="Locales con ≥1 denuncia (geo precisa) a ≤100 m")
c4.metric("Alumnos y docentes expuestos",
          f"{af['alumnos_expuestos'] + af['docentes_expuestos']:,}",
          help="Población (Censo 2025) de los locales educativos afectados")
c5.metric("Cifra negra (Lima+Callao)",
          f"{cifra_negra_lc}%" if cifra_negra_lc else "—",
          delta="víctimas que no denuncian", delta_color="inverse",
          help="ENAPRES 2025: % de víctimas de extorsión que no denunció")

# ── Tabs narrativos ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "① El riesgo",
    "② La cifra negra",
    "③ Dónde actuar",
    "④ La respuesta",
    "Metodología",
])

# ══════════════════════════════════════════════════════════════════════════════
# ① EL RIESGO VISIBLE — lo que registra el Estado
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Mapa: denuncias de extorsión e instituciones educativas</div>',
                unsafe_allow_html=True)
    st.markdown("Heatmap y clusters de denuncias (SIDPOL) + IIEE con ≥1 denuncia a ≤100 m (MINEDU). "
                "Usa el panel de capas para activar o desactivar cada capa.")

    if os.path.exists(MAPA_HTML):
        with open(MAPA_HTML, encoding="utf-8") as fh:
            st_html(fh.read(), height=650, scrolling=False)
        st.markdown('<div class="fuente">Vista pública agregada (privacy by design): los círculos '
                    'muestran nivel de exposición, no denuncias individuales atribuibles. '
                    'Generado con GEOESCUDO_APP/etl_mapa.py</div>', unsafe_allow_html=True)
    else:
        st.info("Ejecuta `GEOESCUDO_APP/etl_mapa.py` para generar el mapa.")

    if prox:
        st.markdown('<div class="section-title">¿Qué tan cerca de los colegios ocurre la extorsión?</div>',
                    unsafe_allow_html=True)
        u = prox["umbrales"]
        radios = list(u.keys())
        pcts = [u[r]["pct"] for r in radios]
        emph = ["100", "200"]
        fig = go.Figure(go.Bar(
            x=[f"≤ {r} m" for r in radios], y=pcts,
            marker_color=[AZUL_OSCURO if r in emph else AZUL_CLARO for r in radios],
            text=[f"{v}%" for v in pcts], textposition="outside",
        ))
        fig.update_yaxes(ticksuffix="%", range=[0, 108])
        st.plotly_chart(fig_base(fig, 300), use_container_width=True, config=PLOTLY_CFG)
        st.info(f"**Lectura:** de las {prox['n_geo_precisa']:,} denuncias con geolocalización "
                f"precisa, **4 de cada 10 ocurrieron a ≤100 m** de un colegio activo y **8 de "
                f"cada 10 a ≤200 m** (menos de dos cuadras). La mediana es "
                f"{prox['mediana_distancia_m']:.0f} m: la denuncia típica de extorsión en Lima "
                "y Callao sucede a una cuadra de una institución educativa.")
        st.warning(f"**La otra brecha de datos:** el {100 - prox['cobertura_geo_pct']:.0f}% de "
                   "las denuncias de extorsión no puede ubicarse con precisión — SIDPOL las "
                   "georreferencia al centroide del distrito. GeoEscudo trabaja solo con las "
                   "geolocalizables y visibiliza esta brecha de calidad de información, que "
                   "también limita la capacidad de focalización de la propia PNP.")
        st.markdown(f'<div class="fuente">Distancia de cada denuncia (geo precisa) al local '
                    f'educativo activo más cercano · SIDPOL corte {CORTE} + Padrón Web MINEDU · '
                    'UTM-18S</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Evolución mensual de las denuncias</div>',
                unsafe_allow_html=True)
    df_t = pd.DataFrame(agr["linea_tiempo"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_t["periodo"], y=df_t["extorsion"], name="Extorsión",
                             mode="lines", line=dict(color=AZUL, width=2)))
    fig.add_trace(go.Scatter(x=df_t["periodo"], y=df_t["extorsion_agravada"],
                             name="Extorsión agravada",
                             mode="lines", line=dict(color=AMBAR, width=2)))
    st.plotly_chart(fig_base(fig, 300), use_container_width=True, config=PLOTLY_CFG)
    st.markdown(f'<div class="fuente">Fuente: PNP / SIDPOL-DGIS · corte {CORTE}</div>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-title">Top 15 distritos por denuncias</div>',
                    unsafe_allow_html=True)
        df_da = (pd.DataFrame(prox["por_distrito"])
                 .nlargest(15, "denuncias_total").sort_values("denuncias_total"))
        fig = go.Figure(go.Bar(
            x=df_da["denuncias_total"], y=df_da["distrito"].str.title(), orientation="h",
            marker_color=AZUL, text=df_da["denuncias_total"], textposition="outside",
        ))
        st.plotly_chart(fig_base(fig, 420), use_container_width=True, config=PLOTLY_CFG)
    with col_b:
        st.markdown('<div class="section-title">Denuncias según turno del hecho</div>',
                    unsafe_allow_html=True)
        df_tu = pd.DataFrame(agr["turnos"])
        fig = go.Figure(go.Bar(
            x=df_tu["turno"], y=df_tu["total"], marker_color=AZUL,
            text=df_tu["total"], textposition="outside",
        ))
        st.plotly_chart(fig_base(fig, 420), use_container_width=True, config=PLOTLY_CFG)
        st.info("**Lectura:** los picos en turno mañana y tarde coinciden con el horario "
                "escolar: el riesgo ocurre cuando los colegios están llenos.")

# ══════════════════════════════════════════════════════════════════════════════
# ② LA CIFRA QUE NO SE VE — ENAPRES 2025
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">La cifra negra en Lima y Callao: lo que ocurre vs. lo que se denuncia</div>',
                unsafe_allow_html=True)
    st.markdown(
        "Las denuncias del acto ① son solo la **punta del iceberg**. La ENAPRES 2025 (INEI) "
        "pregunta directamente a la población de Lima y Callao si fue víctima de extorsión y "
        "si denunció. La brecha entre ambas es la **cifra negra** — y su causa principal no es "
        "apatía: es **miedo y desconfianza**."
    )

    if enapres and lc:
        d = lc  # dominio Lima + Callao (ciudad)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Victimización por extorsión", f"{d['tasa_victimizacion_extorsion_pct']}%",
                  help="Población urbana 15+ de Lima y Callao víctima de extorsión en los "
                       "últimos 12 meses (ponderado, FACTOR_CAP400)")
        m2.metric("Con intento de extorsión", f"{d['tasa_victimizacion_ext_o_intento_pct']}%",
                  help="Víctimas de extorsión consumada o intento")
        m3.metric("Víctimas que denunciaron", f"{d['tasa_denuncia_pct']}%")
        m4.metric("Cifra negra", f"{d['cifra_negra_pct']}%",
                  delta="no denuncia", delta_color="inverse")

        st.markdown(
            f"""<div class="hero-claim">Por cada víctima que denuncia, hay
            <b>≈ {d['victimas_por_denuncia']:.0f} víctimas</b> de extorsión en Lima y Callao.
            Las {prox['n_denuncias']:,}
            denuncias registradas son el <b>piso</b>: la dimensión real del fenómeno se acercaría
            a <b>{int(round(prox['n_denuncias'] * d['victimas_por_denuncia'] / 1000)):,} mil víctimas</b>.</div>""",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-title">¿Denunció? — Lima, Callao y referencia nacional</div>',
                        unsafe_allow_html=True)
            foco = ["Lima (ciudad)", "Callao (ciudad)", "Nacional urbano"]
            dd = [x for x in enapres["dominios"] if x["dominio"] in foco]
            dd = sorted(dd, key=lambda x: foco.index(x["dominio"]))
            names = [x["dominio"] for x in dd]
            den = [x["tasa_denuncia_pct"] for x in dd]
            cn = [x["cifra_negra_pct"] for x in dd]
            fig = go.Figure()
            fig.add_trace(go.Bar(y=names, x=den, orientation="h", name="Denunció",
                                 marker_color=AZUL, text=[f"{v}%" for v in den],
                                 textposition="inside", insidetextanchor="start"))
            fig.add_trace(go.Bar(y=names, x=cn, orientation="h", name="No denunció (cifra negra)",
                                 marker_color=AMBAR, text=[f"{v}%" for v in cn],
                                 textposition="inside"))
            fig.update_layout(barmode="stack")
            fig.update_xaxes(ticksuffix="%", range=[0, 100])
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_base(fig, 300), use_container_width=True, config=PLOTLY_CFG)
            st.markdown('<div class="fuente">ENAPRES 2025, ponderado · víctimas de extorsión '
                        'consumada · en el Callao la cifra negra llega a 83.7%</div>',
                        unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-title">¿Por qué no denuncian en Lima y Callao?</div>',
                        unsafe_allow_html=True)
            mot = d.get("motivos_no_denuncia_pct")
            if mot:
                mm = pd.Series(mot).sort_values()
                confianza = {"Miedo a represalias del agresor", "Desconfía de la Policía",
                             "Es una pérdida de tiempo"}
                colors = [AZUL_OSCURO if k in confianza else AZUL_CLARO for k in mm.index]
                fig = go.Figure(go.Bar(
                    x=mm.values, y=mm.index, orientation="h", marker_color=colors,
                    text=[f"{v}%" for v in mm.values], textposition="outside",
                ))
                fig.update_xaxes(ticksuffix="%")
                st.plotly_chart(fig_base(fig, 300), use_container_width=True, config=PLOTLY_CFG)
                pct_conf = sum(v for k, v in mot.items() if k in confianza)
                st.info(f"**Lectura clave:** el **{pct_conf:.0f}%** de la no-denuncia refleja "
                        "falta de confianza en el sistema (barras oscuras): miedo a represalias, "
                        "desconfianza en la Policía o la expectativa de que denunciar 'es una "
                        "pérdida de tiempo'. La cifra negra no es apatía: es una respuesta "
                        "racional a la falta de canales seguros y confiables. "
                        "**Ahí interviene GeoEscudo (acto ④).**")

    # ── Termómetro distrital ──────────────────────────────────────────────────
    if dist:
        st.markdown('<div class="section-title">Termómetro distrital: dónde duele más el silencio</div>',
                    unsafe_allow_html=True)
        ddf = pd.DataFrame(dist["distritos"])

        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("**Víctimas estimadas vs. denuncias registradas** (top 12 distritos)")
            top = ddf.nlargest(12, "denuncias_extorsion_sidpol").sort_values(
                "denuncias_extorsion_sidpol")
            adicionales = top["victimas_estimadas"] - top["denuncias_extorsion_sidpol"]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top["distrito"], x=top["denuncias_extorsion_sidpol"], orientation="h",
                name="Denuncias registradas (SIDPOL)", marker_color=AZUL,
                text=top["denuncias_extorsion_sidpol"], textposition="inside",
                insidetextanchor="start"))
            fig.add_trace(go.Bar(
                y=top["distrito"], x=adicionales, orientation="h",
                name="Víctimas adicionales estimadas (cifra negra)", marker_color=AMBAR,
                text=top["victimas_estimadas"], textposition="outside"))
            fig.update_layout(barmode="stack")
            st.plotly_chart(fig_base(fig, 430), use_container_width=True, config=PLOTLY_CFG)
            st.markdown('<div class="fuente">Estimación = denuncias × factor de subregistro '
                        f'({dist["factor_subregistro"]}) del dominio Lima+Callao. Referencial, '
                        'no medición distrital directa.</div>', unsafe_allow_html=True)

        with col_d:
            st.markdown("**Se siente inseguro/a en una institución educativa** (% referencial)")
            ref = ddf[ddf["inseguridad_col_educativa_pct"].notna()].sort_values(
                "inseguridad_col_educativa_pct").tail(15)
            fig = go.Figure(go.Bar(
                x=ref["inseguridad_col_educativa_pct"], y=ref["distrito"], orientation="h",
                marker_color=AZUL_OSCURO,
                text=[f"{v}%" for v in ref["inseguridad_col_educativa_pct"]],
                textposition="outside",
                customdata=ref["n_modulo_percepcion"],
                hovertemplate="%{y}: %{x}% (n=%{customdata})<extra></extra>"))
            fig.update_xaxes(ticksuffix="%")
            st.plotly_chart(fig_base(fig, 430), use_container_width=True, config=PLOTLY_CFG)
            st.markdown('<div class="fuente">ENAPRES P407_4, excluye a quienes no frecuentan '
                        'IIEE · solo distritos con n≥80 en el módulo de percepción · '
                        'Lima+Callao agregado: '
                        f'{dist["agregado_lima_callao"]["inseguridad_col_educativa_pct"]}%</div>',
                        unsafe_allow_html=True)

        with st.expander("📋 Tabla distrital completa (indicadores referenciales + n)"):
            cols_show = {
                "distrito": "Distrito",
                "denuncias_extorsion_sidpol": "Denuncias SIDPOL",
                "victimas_estimadas": "Víctimas estimadas",
                "inseguridad_col_educativa_pct": "% inseg. en IIEE",
                "inseguridad_barrio_pct": "% inseg. barrio",
                "temor_extorsion_pct": "% temor extorsión",
                "comisaria_mala_pct": "% comisaría mal calificada",
                "n_modulo_percepcion": "n módulo",
            }
            st.dataframe(ddf[list(cols_show)].rename(columns=cols_show),
                         use_container_width=True, hide_index=True)

        with st.expander("⚠️ Nota metodológica (leer antes de citar)"):
            st.markdown(
                f"- {dist['nota_metodologica']}\n"
                f"- {enapres['nota_metodologica'] if enapres else ''}\n"
                "- Los dominios con pocas víctimas en muestra tienen mayor error muestral: "
                "usar como referencia, no como estimación puntual precisa."
            )

        with st.expander("🚀 ¿Y fuera de Lima? — la escalabilidad de GeoEscudo"):
            if enapres:
                otros = pd.DataFrame([
                    {"Dominio": x["dominio"],
                     "Victimización (%)": x["tasa_victimizacion_extorsion_pct"],
                     "Denunció (%)": x["tasa_denuncia_pct"],
                     "Cifra negra (%)": x["cifra_negra_pct"]}
                    for x in enapres["dominios"]
                    if x["dominio"] in ("La Libertad (depto.)", "Trujillo (ciudad)",
                                        "Nacional urbano")])
                st.dataframe(otros, use_container_width=True, hide_index=True)
                st.markdown(
                    "**La Libertad** — la otra región del concurso — tiene una victimización "
                    "por extorsión **3× la nacional** y una cifra negra de **89.8%**: la "
                    "arquitectura de GeoEscudo (datos SIDPOL + Padrón MINEDU + ENAPRES) es "
                    "directamente replicable allí."
                )
    elif not enapres:
        st.warning("Ejecuta `GEOESCUDO_APP/etl_enapres.py` y `etl_enapres_distrital.py` "
                   "para generar los indicadores ENAPRES.")

# ══════════════════════════════════════════════════════════════════════════════
# ③ DÓNDE ACTUAR — exposición escolar / IEEE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Índice de Exposición Escolar a la Extorsión (IEEE)</div>',
                unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    p1.markdown('<div class="pilar"><h4>Capa 1 · Denuncias</h4><p>Densidad y proximidad de '
                'denuncias de extorsión (SIDPOL), ponderadas por tipo (simple/agravada) y '
                'recencia.</p></div>', unsafe_allow_html=True)
    p2.markdown('<div class="pilar"><h4>Capa 2 · Población expuesta</h4><p>Alumnos y docentes '
                'por colegio según Censo Educativo: a igual riesgo, prioridad donde hay más '
                'personas.</p></div>', unsafe_allow_html=True)
    p3.markdown('<div class="pilar"><h4>Capa 3 · Ajuste por cifra negra</h4><p>Factor de '
                'subregistro por dominio (ENAPRES, acto ②): donde la brecha es mayor, la '
                'intervención es más urgente.</p></div>', unsafe_allow_html=True)

    st.markdown("")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-title">Distritos con más denuncias ≤100 m de un colegio</div>',
                    unsafe_allow_html=True)
        if prox and prox.get("por_distrito"):
            df_dn = pd.DataFrame(prox["por_distrito"]).head(15).sort_values("denuncias_100m")
            fig = go.Figure(go.Bar(
                x=df_dn["denuncias_100m"], y=df_dn["distrito"].str.title(), orientation="h",
                marker_color=AZUL, text=df_dn["denuncias_100m"], textposition="outside",
                customdata=df_dn["denuncias_geo_precisa"],
                hovertemplate="%{y}: %{x} de %{customdata} geolocalizables<extra></extra>",
            ))
            st.plotly_chart(fig_base(fig, 430), use_container_width=True, config=PLOTLY_CFG)
            st.markdown('<div class="fuente">Denuncias con geo precisa a ≤100 m del local '
                        'educativo más cercano, por distrito del hecho</div>',
                        unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="section-title">Locales educativos más expuestos (entorno ≤100 m)</div>',
                    unsafe_allow_html=True)
        if prox and prox.get("top_iiee"):
            df_ti = pd.DataFrame(prox["top_iiee"])
            top = df_ti.head(12).sort_values("denuncias_100m")
            top["etiqueta"] = top["nombre"].str.slice(0, 34) + " · " + top["distrito"].str.title()
            fig = go.Figure(go.Bar(
                x=top["denuncias_100m"], y=top["etiqueta"], orientation="h",
                marker_color=AZUL, text=top["denuncias_100m"], textposition="outside",
            ))
            st.plotly_chart(fig_base(fig, 430), use_container_width=True, config=PLOTLY_CFG)
            st.info("**Lectura:** cada barra son las denuncias (geo precisa) registradas a "
                    "≤100 m de ese local educativo. Una denuncia puede contar para varios "
                    "locales cercanos: mide exposición geográfica, no atribución. En el "
                    "piloto, las 3–5 IIEE priorizadas por el IEEE reciben la intervención "
                    "del acto ④.")

# ══════════════════════════════════════════════════════════════════════════════
# ④ CÓMO ACTUAR — comunidad + policía (community policing)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">La cadena de GeoEscudo</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="hero-claim" style="text-align:center; font-size:1.1rem;">
        Cercanía → Confianza → Denuncia → Mejores datos → Mejor prevención → Más confianza
        </div>""", unsafe_allow_html=True)
    st.markdown(
        "El acto ② mostró que la mayoría no denuncia por **miedo o desconfianza**. "
        "La evidencia internacional del *community policing* (policía comunitaria) muestra el camino: "
        "**el contacto positivo y no coercitivo entre policía y comunidad aumenta la confianza y la "
        "disposición a denunciar** (Peyton et al., 2019, experimento aleatorizado en *PNAS*; "
        "Gill et al., 2014, revisión sistemática)."
    )

    if dist:
        agg = dist["agregado_lima_callao"]
        st.markdown('<div class="section-title">La línea de base: así está hoy la relación '
                    'comunidad–policía en Lima y Callao</div>', unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Califica mal el trabajo de su comisaría",
                  f"{agg['comisaria_mala_pct']:.0f}%",
                  help="ENAPRES P414: 'malo' o 'muy malo', excluye 'no sabe'")
        b2.metric("Califica mal a la PNP en atender prontamente",
                  f"{agg['pnp_atencion_mala_pct']:.0f}%",
                  help="ENAPRES P413_1")
        b3.metric("Califica mal a la PNP en informar a la comunidad",
                  f"{agg['pnp_informar_mala_pct']:.0f}%",
                  help="ENAPRES P413_3 — la dimensión que los encuentros escuela-policía "
                       "atacan directamente")
        b4.metric("Se siente inseguro/a en una institución educativa",
                  f"{agg['inseguridad_col_educativa_pct']:.0f}%",
                  help="ENAPRES P407_4, excluye a quienes no frecuentan IIEE")
        st.info(
            f"**Lectura:** esto no es hostilidad hacia la policía — es **demanda insatisfecha "
            f"de presencia y comunicación**: entre quienes se sienten inseguros en su barrio, el "
            f"{agg['poca_presencia_policial_pct']:.0f}% cita la *poca presencia policial* como "
            "razón. Los encuentros escuela–policía convierten esa demanda en contacto positivo, "
            "y el contacto en confianza (Peyton et al., 2019)."
        )

    st.markdown('<div class="section-title">Encuentros escuela–policía en las IIEE priorizadas</div>',
                unsafe_allow_html=True)
    e1, e2, e3, e4 = st.columns(4)
    e1.markdown('<div class="pilar"><h4>🗣️ Voz</h4><p>Estudiantes, docentes y vecinos mapean '
                'sus zonas y horarios de miedo (cartografía social). Su conocimiento territorial '
                'enriquece el IEEE.</p></div>', unsafe_allow_html=True)
    e2.markdown('<div class="pilar"><h4>⚖️ Neutralidad</h4><p>La comisaría explica cómo opera '
                'un caso de extorsión: cómo denunciar, protección de identidad, qué pasa después. '
                'Canales: Línea 1818, comisaría virtual, "Tu Denuncia, Nuestra Fuerza".</p></div>',
                unsafe_allow_html=True)
    e3.markdown('<div class="pilar"><h4>🤝 Respeto</h4><p>Encuentros en la escuela, terreno '
                'propio de la comunidad, vía estructuras que ya existen: BAPE, OPC de comisarías, '
                'CODISEC. Sin crear institucionalidad paralela.</p></div>', unsafe_allow_html=True)
    e4.markdown('<div class="pilar"><h4>✅ Confiabilidad</h4><p>Los compromisos de cada '
                'institución quedan registrados en la plataforma con su estado de cumplimiento. '
                'La confianza no se pide: se demuestra.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Módulos del piloto (60 días)</div>',
                unsafe_allow_html=True)
    mod = pd.DataFrame({
        "Módulo": ["① Exposición", "② Cifra negra", "③ Actividades y compromisos", "④ Confianza"],
        "Qué muestra": [
            "Mapa IEEE, ranking de distritos e IIEE (operativo — actos ① y ③)",
            "Brecha victimización–denuncia ENAPRES y motivos de no denuncia (operativo — acto ②)",
            "Registro de encuentros escuela–policía: fechas, participantes, compromisos "
            "institucionales y % de cumplimiento (se activa con el piloto)",
            "Encuestas pre/post en talleres: confianza en la policía, disposición a denunciar, "
            "conocimiento de rutas (se activa con el piloto)",
        ],
        "Estado": ["✅ Operativo", "✅ Operativo", "🔜 Piloto", "🔜 Piloto"],
    })
    st.dataframe(mod, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Cómo mediremos el éxito</div>', unsafe_allow_html=True)
    st.markdown(
        "- **Indicadores primarios (60 días):** ↑ confianza y legitimidad percibida, "
        "↑ conocimiento de rutas de denuncia y disposición a denunciar, participación efectiva "
        "(≥60 estudiantes, ≥20 docentes/directivos, comisarías y vecinos).\n"
        "- **Indicador intermedio (6–12 meses):** ↑ denuncias en zonas intervenidas — "
        "**aquí subir denuncias es éxito: es la cifra negra saliendo a la luz.**\n"
        "- **Largo plazo:** ↓ exposición escolar (IEEE).\n\n"
        "*Levantamiento de información: encuestas pre/post con ítems de legitimidad (Tyler), "
        "entrevistas a directores y comisarios, cartografía social. El piloto genera la primera "
        "línea de base de este tipo en el Perú.*"
    )

# ══════════════════════════════════════════════════════════════════════════════
# METODOLOGÍA Y FUENTES
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Fuentes de datos</div>', unsafe_allow_html=True)
    st.markdown(
        "| Fuente | Contenido | Corte |\n"
        "|---|---|---|\n"
        f"| MINEDU — Padrón Web / Censo Educativo | {prox['n_locales_educativos']:,} locales "
        "educativos activos georreferenciados (Lima Met. y Callao), docentes y alumnos "
        "censados | 29/04/2026 |\n"
        f"| PNP / SIDPOL-DGIS (observatorio MININTER) | {prox['n_denuncias']:,} denuncias de "
        f"extorsión, Lima Met. y Callao 2025–26 | {CORTE} |\n"
        "| INEI — ENAPRES 2025, Cap. 400 | Victimización, denuncia y motivos de no denuncia "
        "por extorsión (urbano, 15+) | 2025 |\n"
        "| IGN Perú | Límites político-administrativos | — |"
    )
    st.markdown('<div class="section-title">Metodología</div>', unsafe_allow_html=True)
    st.markdown(
        "- **Calidad de geolocalización (filtro clave):** SIDPOL georreferencia al centroide "
        "distrital las denuncias cuya dirección no puede geocodificar "
        f"({prox['n_puntos_relleno_excluidos']} puntos de relleno con direcciones "
        "heterogéneas). El análisis de proximidad usa solo las "
        f"{prox['n_geo_precisa']:,} denuncias con geolocalización precisa "
        f"({prox['cobertura_geo_pct']}%) y declara esta cobertura; los conteos distritales "
        "usan el campo `distrito_hecho` (no afectado).\n"
        "- **Proximidad espacial:** distancia de cada denuncia (geo precisa) al local "
        "educativo activo más cercano (`geopandas.sjoin_nearest`, UTM-18S), numerador y "
        f"denominador en denuncias. Cifras verificadas al corte {CORTE}: "
        f"{prox['umbrales']['100']['pct']}% ≤100 m, {prox['umbrales']['200']['pct']}% "
        f"≤200 m, mediana {prox['mediana_distancia_m']:.0f} m. Locales afectados y "
        "población expuesta: buffer de 100 m por local (agregando servicios del mismo "
        "código de local).\n"
        "- **Cifra negra:** tasas ponderadas con FACTOR_CAP400 (ENAPRES). Extorsión = delito 19; "
        "intento = delito 20. Representatividad por ciudad principal/departamento, no distrital.\n"
        "- **Pipeline reproducible:** descarga automatizada del observatorio ArcGIS del MININTER "
        "(capas EXTORSION, DELITOS_TOTAL, COMISARIAS, jurisdicciones policiales) + ETL ENAPRES "
        "documentado. Código en repositorio abierto al cierre del piloto (R6).\n"
        "- **Privacidad desde el diseño:** la vista pública agrega por distrito y rangos; el "
        "detalle por IIEE se entrega solo por canal institucional (UGEL, municipio, comisaría), "
        "siguiendo el modelo europeo CITYCoP.\n"
        "- **Efecto desplazamiento:** el monitoreo incluye buffers adyacentes a las zonas "
        "priorizadas (Blattman et al., 2021)."
    )
    st.markdown('<div class="section-title">Evidencia académica que sustenta el diseño</div>',
                unsafe_allow_html=True)
    st.markdown(
        "- Peyton, Sierra-Arévalo & Rand (2019), *PNAS* — el contacto positivo policía-vecino "
        "aumenta la legitimidad percibida (experimento aleatorizado).\n"
        "- Gill et al. (2014), *J. Experimental Criminology* — el community policing mejora "
        "confianza y legitimidad de forma consistente.\n"
        "- Tyler (2023); Sunshine & Tyler (2003) — justicia procedimental: voz, neutralidad, "
        "respeto, confiabilidad.\n"
        "- Huaytalla (2019); Oviedo Maravi (2021, PUCP) — el vacío peruano de datos y evaluación "
        "en participación ciudadana que GeoEscudo cierra.\n\n"
        "*Revisión de literatura completa (17 fuentes) disponible en el repositorio del proyecto.*"
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "**GeoEscudo** · Equipo: Xiomara Salas · Gabriel Riega · Carlos Crespín · André Rodríguez · "
    "Jaime Olivas — Hackathon RedPública Transforma (PNUD, UNDP-PER-00940) · 2026. "
    "Los datos de denuncias no representan la totalidad de los hechos delictivos; "
    "la brecha se analiza explícitamente en el acto ②."
)
