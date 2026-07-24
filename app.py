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
import tempfile
import zipfile

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
XLSX_FILE = os.path.join(OUT_DIR, "dashboard_bienestar_docente.xlsx")
ENAPRES_JSON = os.path.join(OUT_DIR, "enapres_extorsion.json")
PROX_JSON = os.path.join(OUT_DIR, "proximidad_verificada.json")
MAPA_HTML = os.path.join(OUT_DIR, "mapa_geoescudo.html")
ZIP_FILE = os.path.join(OUT_DIR, "mapa_iiee_extorsion.zip")

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
@st.cache_data(show_spinner="Cargando datos…")
def load_xlsx(path):
    return pd.read_excel(path, sheet_name=None, engine="openpyxl")


@st.cache_data(show_spinner=False)
def load_enapres(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner="Cargando mapa interactivo…")
def load_map_html(path):
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(tmp)
        for root, _, files in os.walk(tmp):
            for f in files:
                if f.endswith(".html"):
                    with open(os.path.join(root, f), encoding="utf-8") as fh:
                        return fh.read()
    return None


sheets = load_xlsx(XLSX_FILE) if os.path.exists(XLSX_FILE) else {}
enapres = load_enapres(ENAPRES_JSON) if os.path.exists(ENAPRES_JSON) else None
prox = load_enapres(PROX_JSON) if os.path.exists(PROX_JSON) else None


def get(sheet):
    return sheets.get(sheet, pd.DataFrame())


kpi = get("Resumen_KPI")


def kv(nombre, default="—"):
    if kpi.empty:
        return default
    row = kpi[kpi["Indicador"].str.strip() == nombre]
    return row["Valor"].iloc[0] if not row.empty else default


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
    La extorsión escolar tiene dos caras: <b>la que se denuncia</b> — la mitad de las denuncias
    en Lima y Callao ocurre a <b>≈100 metros de un colegio</b> — y <b>la que se calla</b>:
    el <b>{cifra_negra_lc if cifra_negra_lc else '—'}%</b> de las víctimas de extorsión no
    denuncia (ENAPRES 2025). GeoEscudo mide ambas — y actúa sobre la causa del silencio:
    <b>la desconfianza</b>.
    </div>""",
    unsafe_allow_html=True,
)

# KPIs hero
p100 = prox["umbrales"]["100"] if prox else None
med = prox["mediana_distancia_m"] if prox else None
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Denuncias de extorsión 2025–26",
          f"{prox['n_denuncias']:,}" if prox else f"{int(kv('Denuncias de extorsión (total)')):,}",
          help="PNP / SIDPOL-DGIS, Lima Metropolitana y Callao, corte 26/05/2026")
c2.metric("A ≤100 m de un colegio", f"{p100['pct']}%" if p100 else "—",
          delta=f"mediana: {med:.0f} m" if med else None, delta_color="off",
          help="Distancia de cada denuncia a la IIEE activa más cercana (sjoin_nearest, "
               "UTM-18S). La mediana indica que la denuncia típica ocurre a ~1 cuadra "
               "de un colegio.")
c3.metric("IIEE con extorsión en su entorno", f"{int(kv('IIEE con ≥ 1 denuncia en entorno')):,}",
          delta=f"{float(kv('% IIEE afectadas'))}% del total", delta_color="inverse")
c4.metric("Alumnos y docentes expuestos",
          f"{int(kv('Alumnos en IIEE afectadas')) + int(kv('Docentes en IIEE afectadas')):,}")
c5.metric("Cifra negra (Lima+Callao)",
          f"{cifra_negra_lc}%" if cifra_negra_lc else "—",
          delta="víctimas que no denuncian", delta_color="inverse",
          help="ENAPRES 2025: % de víctimas de extorsión que no denunció")

# ── Tabs narrativos ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "① El riesgo visible",
    "② La cifra que no se ve",
    "③ Dónde actuar: exposición escolar",
    "④ Cómo actuar: comunidad + policía",
    "Metodología y fuentes",
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
    elif os.path.exists(ZIP_FILE):
        if st.toggle("Mostrar mapa interactivo (versión pesada)", value=True):
            html_src = load_map_html(ZIP_FILE)
            if html_src:
                st_html(html_src, height=650, scrolling=False)
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
        st.plotly_chart(fig_base(fig, 300), use_container_width=True)
        st.info(f"**Lectura:** de las {prox['n_denuncias']:,} denuncias de extorsión, "
                f"**1 de cada 2 ocurrió a ≤100 m** de un colegio activo y **8 de cada 10 a "
                f"≤200 m** (menos de dos cuadras). La mediana es {prox['mediana_distancia_m']:.0f} m: "
                "la denuncia típica de extorsión en Lima y Callao sucede a una cuadra de una "
                "institución educativa.")
        st.markdown('<div class="fuente">Distancia de cada denuncia a la IIEE activa más '
                    'cercana · SIDPOL 26/05/2026 + Padrón Web MINEDU · UTM-18S</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="section-title">Evolución mensual de las denuncias</div>',
                unsafe_allow_html=True)
    df_t = get("Linea_Tiempo")
    if not df_t.empty:
        per = df_t.columns[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_t[per], y=df_t["EXTORSION"], name="Extorsión",
                                 mode="lines", line=dict(color=AZUL, width=2)))
        fig.add_trace(go.Scatter(x=df_t[per], y=df_t["EXTORSION AGRAVADA"], name="Extorsión agravada",
                                 mode="lines", line=dict(color=AMBAR, width=2)))
        st.plotly_chart(fig_base(fig, 300), use_container_width=True)
        st.markdown('<div class="fuente">Fuente: PNP / SIDPOL-DGIS · 2025–2026</div>',
                    unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-title">Top 15 distritos por denuncias</div>',
                    unsafe_allow_html=True)
        df_da = get("Top_Distritos").head(15)
        if not df_da.empty:
            df_da = df_da.sort_values("Total denuncias")
            fig = go.Figure(go.Bar(
                x=df_da["Total denuncias"], y=df_da["Distrito"], orientation="h",
                marker_color=AZUL, text=df_da["Total denuncias"], textposition="outside",
            ))
            st.plotly_chart(fig_base(fig, 420), use_container_width=True)
    with col_b:
        st.markdown('<div class="section-title">Denuncias según turno del hecho</div>',
                    unsafe_allow_html=True)
        df_tu = get("Por_Turno")
        if not df_tu.empty:
            fig = go.Figure(go.Bar(
                x=df_tu["Turno del hecho"], y=df_tu["Total"], marker_color=AZUL,
                text=df_tu["Total"], textposition="outside",
            ))
            st.plotly_chart(fig_base(fig, 420), use_container_width=True)
            st.info("**Lectura:** los picos en turno mañana y tarde coinciden con el horario "
                    "escolar: el riesgo ocurre cuando los colegios están llenos.")

# ══════════════════════════════════════════════════════════════════════════════
# ② LA CIFRA QUE NO SE VE — ENAPRES 2025
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">La cifra negra: lo que ocurre vs. lo que se denuncia</div>',
                unsafe_allow_html=True)
    st.markdown(
        "Las denuncias del acto ① son solo la **punta del iceberg**. La ENAPRES 2025 (INEI) "
        "pregunta directamente a la población si fue víctima de extorsión y si denunció. "
        "La brecha entre ambas es la **cifra negra** — y su causa principal no es apatía: "
        "es **miedo y desconfianza**."
    )

    if enapres:
        doms = [d["dominio"] for d in enapres["dominios"]]
        sel = st.selectbox("Dominio de análisis (representatividad ENAPRES)", doms,
                           index=doms.index("Lima + Callao (ciudad)"))
        d = dom(sel)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Victimización por extorsión", f"{d['tasa_victimizacion_extorsion_pct']}%",
                  help="Población urbana 15+ víctima de extorsión en los últimos 12 meses (ponderado)")
        m2.metric("Con intento de extorsión", f"{d['tasa_victimizacion_ext_o_intento_pct']}%",
                  help="Víctimas de extorsión consumada o intento de extorsión")
        m3.metric("Víctimas que denunciaron", f"{d['tasa_denuncia_pct']}%")
        m4.metric("Cifra negra", f"{d['cifra_negra_pct']}%",
                  delta="no denuncia", delta_color="inverse")

        if d.get("victimas_por_denuncia"):
            st.markdown(
                f"""<div class="hero-claim">Por cada víctima que denuncia, hay
                <b>≈ {d['victimas_por_denuncia']:.0f} víctimas</b> de extorsión en {sel}.
                Las {prox['n_denuncias'] if prox else int(kv('Denuncias de extorsión (total)')):,}
                denuncias registradas son el <b>piso</b>, no la dimensión real del fenómeno.</div>""",
                unsafe_allow_html=True,
            )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-title">¿Denunció? — comparación entre dominios</div>',
                        unsafe_allow_html=True)
            dd = [x for x in enapres["dominios"] if x["tasa_denuncia_pct"] is not None]
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
            st.plotly_chart(fig_base(fig, 320), use_container_width=True)
            st.markdown('<div class="fuente">ENAPRES 2025, ponderado (FACTOR_CAP400) · '
                        'víctimas de extorsión consumada</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-title">¿Por qué no denuncian? (motivo principal)</div>',
                        unsafe_allow_html=True)
            mot = d.get("motivos_no_denuncia_pct") or dom("Nacional urbano")["motivos_no_denuncia_pct"]
            if mot:
                mm = pd.Series(mot).sort_values()
                confianza = {"Miedo a represalias del agresor", "Desconfía de la Policía"}
                colors = [AZUL_OSCURO if k in confianza else AZUL_CLARO for k in mm.index]
                fig = go.Figure(go.Bar(
                    x=mm.values, y=mm.index, orientation="h", marker_color=colors,
                    text=[f"{v}%" for v in mm.values], textposition="outside",
                ))
                fig.update_xaxes(ticksuffix="%")
                st.plotly_chart(fig_base(fig, 320), use_container_width=True)
                pct_conf = sum(v for k, v in mot.items() if k in confianza)
                st.info(f"**Lectura clave:** el **{pct_conf:.0f}%** de la no-denuncia se explica por "
                        "**miedo a represalias o desconfianza en la Policía** (barras oscuras). "
                        "La cifra negra no es apatía: es una respuesta racional a la falta de "
                        "canales seguros y confiables. **Ahí interviene GeoEscudo (acto ④).**")

        t1, t2 = st.columns(2)
        with t1:
            st.metric("Cree que será víctima de extorsión (próx. 12 meses)",
                      f"{d['temor_extorsion_pct']}%",
                      help="ENAPRES 2025 P402_11 — percepción de inseguridad futura")
        with t2:
            st.metric("Muestra del dominio",
                      f"{d['n_respondentes']:,} personas",
                      delta=f"{d['n_victimas_extorsion']} víctimas de extorsión en muestra",
                      delta_color="off")

        with st.expander("⚠️ Nota metodológica (leer antes de citar)"):
            st.markdown(
                f"- {enapres['nota_metodologica']}\n"
                "- Los dominios con pocas víctimas en muestra (n < 50) tienen mayor error "
                "muestral: usar como referencia, no como estimación puntual precisa.\n"
                "- El **factor de subregistro** del índice IEEE se aplica por dominio "
                "(ciudad/departamento), nunca distrito a distrito."
            )
    else:
        st.warning("Ejecuta `GEOESCUDO_APP/etl_enapres.py` para generar los indicadores ENAPRES.")

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
        st.markdown('<div class="section-title">Distritos con más denuncias ≤100 m de IIEE</div>',
                    unsafe_allow_html=True)
        df_dn = get("Distritos_IIEE").head(15)
        if not df_dn.empty:
            df_dn = df_dn.sort_values("Denuncias ≤100m IIEE")
            fig = go.Figure(go.Bar(
                x=df_dn["Denuncias ≤100m IIEE"], y=df_dn["Distrito"], orientation="h",
                marker_color=AZUL, text=df_dn["Denuncias ≤100m IIEE"], textposition="outside",
            ))
            st.plotly_chart(fig_base(fig, 430), use_container_width=True)
            st.dataframe(get("Distritos_IIEE").head(15), use_container_width=True, hide_index=True)
    with col_b:
        st.markdown('<div class="section-title">IIEE más expuestas (entorno ≤100 m)</div>',
                    unsafe_allow_html=True)
        df_ti = get("Top_IIEE")
        if not df_ti.empty:
            top = df_ti.head(12).sort_values("Denuncias cercanas")
            fig = go.Figure(go.Bar(
                x=top["Denuncias cercanas"], y=top["IIEE"].str.slice(0, 38), orientation="h",
                marker_color=AZUL, text=top["Denuncias cercanas"], textposition="outside",
            ))
            st.plotly_chart(fig_base(fig, 430), use_container_width=True)
            st.info("**Lectura:** cada barra son las denuncias registradas a ≤100 m de esa IIEE. "
                    "Una denuncia puede contar para varias IIEE cercanas: mide exposición "
                    "geográfica, no atribución. En el piloto, las 3–5 IIEE priorizadas por el "
                    "IEEE reciben la intervención del acto ④.")

    st.markdown('<div class="section-title">Exposición por tipo de gestión</div>',
                unsafe_allow_html=True)
    df_g = get("Por_Gestion")
    if not df_g.empty:
        st.dataframe(df_g, use_container_width=True, hide_index=True)
        st.markdown('<div class="fuente">La exposición se concentra en la gestión pública: '
                    'un problema de bien público que exige respuesta pública.</div>',
                    unsafe_allow_html=True)

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
        "| MINEDU — Padrón Web / Censo Educativo | 13,737 IIEE activas georreferenciadas, "
        "docentes y alumnos censados | 29/04/2026 |\n"
        "| PNP / SIDPOL-DGIS (observatorio MININTER) | 14,665 denuncias de extorsión "
        "georreferenciadas, Lima y Callao 2025–26 | 26/05/2026 |\n"
        "| INEI — ENAPRES 2025, Cap. 400 | Victimización, denuncia y motivos de no denuncia "
        "por extorsión (urbano, 15+) | 2025 |\n"
        "| IGN Perú | Límites político-administrativos | — |"
    )
    st.markdown('<div class="section-title">Metodología</div>', unsafe_allow_html=True)
    st.markdown(
        "- **Proximidad espacial:** distancia de cada denuncia a la IIEE activa más cercana "
        "(`geopandas.sjoin_nearest`, proyección UTM-18S), numerador y denominador en denuncias "
        "(unidades consistentes). Cifras verificadas: 49.5% ≤100 m, 79.0% ≤200 m, mediana 105 m "
        "(corte 26/05/2026). Los conteos de IIEE afectadas y población expuesta usan asignación "
        "a la IIEE más cercana dentro de 100 m (estimación conservadora, sin doble conteo).\n"
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
