"""Versión Streamlit del dashboard (misma información que web/index.html).

Uso:
    streamlit run app.py
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parent
AZUL, NARANJA, BAJA, SUBE, NS = "#2a78d6", "#eb6834", "#1c5cab", "#b8302f", "#c3c2b7"
NOTA_LIMA = ("Lima Metropolitana: la cifra 2025 no se pudo contrastar con el INEI (error en su archivo); con la misma "
             "metodología, la de 2024 coincide con la publicada.")

st.set_page_config(page_title="¿Bajó la anemia infantil en todo el Perú?", layout="wide")


@st.cache_data
def cargar():
    t = pd.read_csv(RAIZ / "datos" / "procesados" / "anemia_departamento_2025.csv")
    t["cambio_significativo"] = (t.cambio_ls < 0) | (t.cambio_li > 0)
    t["puesto_robusto"] = (t.cambio_puesto_li > 0) | (t.cambio_puesto_ls < 0)
    # Réplica con la ENDES 2024 (scripts/replicar_2024.py)
    r = pd.read_csv(RAIZ / "datos" / "procesados" / "replica_departamento_2024_2025.csv")
    t = t.merge(r[["ambito", "cambio_pp_2024", "cambio_li_2024", "cambio_ls_2024", "significativo_2024",
                   "puesto_363_2024", "puesto_oms_2024", "puesto_robusto_2024"]], on="ambito", how="left")
    t["sin_cambio_ambos"] = ~t.cambio_significativo & ~t.significativo_2024.astype(bool)
    t["puesto_robusto_2024"] = t.puesto_robusto_2024.fillna(False).astype(bool)
    t["puesto_robusto_ambos"] = t.puesto_robusto & t.puesto_robusto_2024
    alt = pd.read_csv(RAIZ / "datos" / "procesados" / "anemia_altitud_2025.csv")
    rep = pd.read_csv(RAIZ / "datos" / "procesados" / "replica_altitud_2024_2025.csv")
    geo = json.loads((RAIZ / "web" / "data" / "ambitos.geojson").read_text(encoding="utf-8"))
    return t, alt, rep, geo


def num(v):
    return f"{v:.1f}".replace(".", ",")


def pp(v):
    return ("+" if v > 0 else "−" if v < 0 else "") + num(abs(v))


def franja(a, b):
    return f"{int(a):,}–{int(b) - 1:,}".replace(",", " ") if pd.notna(b) else f"{int(a):,} o más".replace(",", " ")


def robusto(d):
    if d.puesto_robusto_ambos:
        return "Cambio de puesto robusto en 2025 y 2024"
    if d.puesto_robusto:
        return "Cambio de puesto robusto solo en 2025"
    if d.puesto_robusto_2024:
        return "Cambio de puesto robusto solo en 2024"
    return "Cambio de puesto no concluyente"


t, alt, rep, geo = cargar()
peru = t[t.ambito == "Perú"].iloc[0]
deps = t[t.ambito != "Perú"].copy()

st.title("¿Bajó la anemia infantil en todo el Perú?")
st.markdown(
    "En 2024 el Perú adoptó la guía de la OMS para diagnosticar anemia. Con el criterio nuevo, la anemia en "
    "niñas y niños de 6 a 35 meses pasa de 43,4 % a 34,9 %. Pero el cambio no fue igual en todo el país: "
    "depende de la altitud donde viven."
)
st.caption("ENDES 2025 (INEI), microdatos · Réplica con la ENDES 2024 · Cálculo propio validado contra las cifras publicadas por el INEI · "
           "Intervalos de confianza al 95 %")

h1, h2, h3 = st.columns(3)
h1.markdown("**1. La caída no fue pareja**  \nEn 2025 baja en 20 de 26 ámbitos. En 5 (Amazonas, Arequipa, Cajamarca, "
            "Huánuco y Moquegua) el cambio no se distingue de cero, ni en 2025 ni en 2024.")
h2.markdown("**2. La altitud explica el patrón**  \nEntre 500 y 2499 m la nueva fórmula sube la anemia entre 7 y "
            "11 puntos. Por encima de 3000 m la baja entre 14 y 34 puntos. El patrón se repite con la ENDES 2024.")
h3.markdown("**3. Cambia el orden**  \nCon los datos de 2025 y de 2024, Amazonas, Arequipa y Cajamarca "
            "suben en el orden y Pasco baja. Puno sigue primero con ambos criterios.")

st.divider()
f1, f2, f3 = st.columns(3)
criterio = f1.radio("Mapa", ["RM 363-2022", "OMS 2024", "Cambio"], index=1, horizontal=True)
ambito = f2.selectbox("Ámbito", ["Perú"] + sorted(deps.ambito, key=str.lower))
altitud = f3.selectbox("Altitud mediana del ámbito", ["Todas", "Menos de 500 m", "500 a 2499 m", "2500 m o más"])

m = deps.altitud_mediana_m
filtro = {"Todas": m >= 0, "Menos de 500 m": m < 500, "500 a 2499 m": (m >= 500) & (m < 2500),
          "2500 m o más": m >= 2500}[altitud]
vis = deps[filtro].sort_values("cambio_pp")

# ---------- KPIs ----------
d = t[t.ambito == ambito].iloc[0]
k1, k2, k3, k4 = st.columns(4)
k1.metric(f"Anemia, RM 363-2022 · {ambito}", f"{num(d.anemia_363)} %",
          help=f"IC 95 %: {num(d.anemia_363_li)}–{num(d.anemia_363_ls)}")
k1.caption(f"IC 95 %: {num(d.anemia_363_li)}–{num(d.anemia_363_ls)}")
k2.metric(f"Anemia, OMS 2024 · {ambito}", f"{num(d.anemia_oms)} %")
k2.caption(f"IC 95 %: {num(d.anemia_oms_li)}–{num(d.anemia_oms_ls)}")
k3.metric("Cambio", f"{pp(d.cambio_pp)} pts")
k3.caption(f"IC 95 %: {pp(d.cambio_li)} a {pp(d.cambio_ls)}" + ("" if d.cambio_significativo else " · no significativo"))
if ambito == "Perú":
    k4.metric("Ámbitos sin cambio significativo", f"{deps.sin_cambio_ambos.sum()} de {len(deps)}")
    k4.caption("En 2025 y en 2024: su intervalo de 95 % incluye cero")
else:
    k4.metric("Puesto (1 = más anemia)", f"{int(d.puesto_363)} → {int(d.puesto_oms)}")
    k4.caption(f"{robusto(d)} · 2024: {int(d.puesto_363_2024)} → {int(d.puesto_oms_2024)}")
if ambito == "Lima Metropolitana":
    st.caption(NOTA_LIMA)

# ---------- Mapa y cambio por ámbito ----------
c1, c2 = st.columns(2)
with c1:
    col = {"RM 363-2022": "anemia_363", "OMS 2024": "anemia_oms", "Cambio": "cambio_pp"}[criterio]
    datos_mapa = deps.assign(visible=filtro)
    if criterio == "Cambio":
        st.subheader("Cambio al pasar a OMS 2024")
        escala, rango = [[0, BAJA], [0.5, "#f0efec"], [1, SUBE]], (-20, 20)
    else:
        st.subheader(f"Anemia en niñas y niños de 6 a 35 meses, {criterio}")
        escala, rango = [[0, "#cde2fb"], [1, "#0d366b"]], (20, 80)
    fig = px.choropleth(datos_mapa, geojson=geo, locations="ambito", featureidkey="properties.ambito",
                        color=col, color_continuous_scale=escala, range_color=rango,
                        hover_name="ambito",
                        hover_data={"anemia_363": ":.1f", "anemia_oms": ":.1f", "cambio_pp": ":.1f", "ambito": False})
    fig.update_traces(marker_opacity=[1 if v else 0.25 for v in datos_mapa.visible],
                      marker_line_width=[2.5 if a == ambito else 0.6 for a in datos_mapa.ambito])
    fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
    fig.update_layout(height=560, margin=dict(l=0, r=0, t=0, b=0),
                      coloraxis_colorbar=dict(title="pts" if criterio == "Cambio" else "%"))
    st.plotly_chart(fig, width="stretch")

with c2:
    st.subheader("Cambio al pasar a OMS 2024, por ámbito")
    st.caption("Puntos porcentuales con intervalo de 95 %. En gris, los cambios que no se distinguen de cero.")
    tono = [NS if not s else BAJA if v < 0 else SUBE for s, v in zip(vis.cambio_significativo, vis.cambio_pp)]
    fig = go.Figure(go.Scatter(
        x=vis.cambio_pp, y=vis.ambito, mode="markers",
        marker=dict(color=tono, size=[12 if a == ambito else 9 for a in vis.ambito], line=dict(color="white", width=2)),
        error_x=dict(type="data", symmetric=False, array=vis.cambio_ls - vis.cambio_pp,
                     arrayminus=vis.cambio_pp - vis.cambio_li, color="#898781", thickness=1.5, width=0),
        hovertemplate="<b>%{y}</b><br>Cambio: %{x:.1f} pts<extra></extra>"))
    fig.add_vline(x=0, line_color="#898781", line_width=1)
    fig.update_layout(height=560, margin=dict(l=0, r=10, t=10, b=10), xaxis_title="Puntos porcentuales",
                      xaxis_range=[-30, 15], yaxis_autorange="reversed", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")

# ---------- Por altitud ----------
st.subheader("Anemia según la altitud donde viven las niñas y niños")
st.caption("Perú, franjas de 500 m (las de la Tabla 4 de la guía OMS 2024). Banda: intervalo de 95 %.")
alt["franja"] = [franja(a, b) for a, b in zip(alt.desde, alt.hasta)]
fig = go.Figure()
for k, nombre, c in [("anemia_363", "RM 363-2022-MINSA", AZUL), ("anemia_oms", "OMS 2024 / RM 251-2024-MINSA", NARANJA)]:
    fig.add_trace(go.Scatter(x=list(alt.franja) + list(alt.franja[::-1]), y=list(alt[f"{k}_ls"]) + list(alt[f"{k}_li"][::-1]),
                             fill="toself", fillcolor=c, opacity=0.12, line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=alt.franja, y=alt[k], name=nombre, mode="lines+markers", line=dict(color=c, width=2),
                             marker=dict(size=8), hovertemplate="%{x} m: %{y:.1f} %<extra>" + nombre + "</extra>"))
fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(range=[0, 80], title="%"),
                  xaxis_title="Altitud del conglomerado (m s. n. m.)", legend=dict(orientation="h", y=1.08),
                  plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, width="stretch")

# ---------- Réplica 2024 ----------
st.subheader("¿Se repite en 2024?")
st.caption("Cambio al pasar a OMS 2024 por franja de altitud (puntos porcentuales, intervalo de 95 %), con la ENDES 2025 "
           "y la ENDES 2024. Dos de cada tres conglomerados de 2025 ya estaban en 2024 (con otras viviendas), así que "
           "las dos muestras no son independientes. Por eso se muestra también 2024 solo con los conglomerados que no "
           "están en 2025.")
rep["franja"] = [franja(a, b) for a, b in zip(rep.desde, rep.hasta)]
fig = go.Figure()
for (anio, muestra), nombre, relleno, borde in [((2025, "completa"), "ENDES 2025", "#0b0b0b", "#0b0b0b"),
                                                ((2024, "completa"), "ENDES 2024", "#898781", "#898781"),
                                                ((2024, "sin_panel"), "ENDES 2024, sin conglomerados repetidos",
                                                 "white", "#898781")]:
    s = rep[(rep.anio == anio) & (rep.muestra == muestra)]
    fig.add_trace(go.Scatter(
        x=s.franja, y=s.cambio, name=nombre, mode="markers",
        marker=dict(size=9, color=relleno, line=dict(color=borde, width=2)),
        error_y=dict(type="data", symmetric=False, array=s.cambio_ls - s.cambio, arrayminus=s.cambio - s.cambio_li,
                     color=borde, thickness=2, width=0),
        customdata=s[["cambio_li", "cambio_ls", "n"]],
        hovertemplate="%{x} m: %{y:.1f} pts [%{customdata[0]:.1f} a %{customdata[1]:.1f}] · n = %{customdata[2]}"
                      "<extra>" + nombre + "</extra>"))
fig.add_hline(y=0, line_color="#898781", line_width=1)
fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), scattermode="group",
                  yaxis=dict(range=[-55, 20], title="pts"), xaxis_title="Altitud del conglomerado (m s. n. m.)",
                  legend=dict(orientation="h", y=1.08), plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, width="stretch")

# ---------- Descomposición ----------
st.subheader("¿Qué parte del cambio viene de cada regla?")
st.caption("El criterio OMS 2024 cambió dos cosas a la vez. Cada panel aplica solo uno de los cambios sobre el criterio "
           "anterior (puntos porcentuales).")
e1, e2 = st.columns(2)
for cont, col, titulo in [(e1, "efecto_altitud_pp", "Nueva fórmula de altitud"),
                          (e2, "efecto_corte_pp", "Nuevo punto de corte para 6–23 meses (10,5 g/dL)")]:
    fig = go.Figure(go.Bar(x=vis[col], y=vis.ambito, orientation="h",
                           marker_color=[BAJA if v < 0 else SUBE for v in vis[col]],
                           hovertemplate="<b>%{y}</b>: %{x:.1f} pts<extra></extra>"))
    fig.update_layout(title=titulo, height=560, margin=dict(l=0, r=10, t=40, b=10), xaxis_range=[-20, 20],
                      yaxis_autorange="reversed",
                      plot_bgcolor="rgba(0,0,0,0)")
    cont.plotly_chart(fig, width="stretch")

# ---------- Puestos ----------
st.subheader("Orden de los ámbitos: de mayor a menor anemia")
st.caption("Puesto con cada criterio, ENDES 2025. Resaltados, los cambios de puesto robustos en 2025 y también en 2024: "
           "su intervalo de 95 % (bootstrap de diseño, 2000 réplicas) no incluye cero en ninguno de los dos años. "
           "San Martín y Ucayali son robustos solo en 2025; Huancavelica y Moquegua, solo en 2024. El puesto exacto es "
           "incierto; la dirección de los cambios resaltados, no.")
fig = go.Figure()
for _, r in deps[filtro].sort_values("puesto_robusto_ambos").iterrows():
    c = NS if not r.puesto_robusto_ambos else SUBE if r.puesto_oms < r.puesto_363 else BAJA
    fuerte = r.puesto_robusto_ambos or r.ambito == ambito
    fig.add_trace(go.Scatter(x=["RM 363-2022", "OMS 2024"], y=[r.puesto_363, r.puesto_oms], mode="lines+markers+text",
                             line=dict(color=c, width=3 if fuerte else 1.2), marker=dict(size=8, color=c),
                             text=[f"{r.ambito} {int(r.puesto_363)}", f"{int(r.puesto_oms)} {r.ambito}"],
                             textposition=["middle left", "middle right"], showlegend=False,
                             hovertemplate=f"<b>{r.ambito}</b><br>%{{x}}: puesto %{{y}}<br>{robusto(r)}<extra></extra>"))
fig.update_layout(height=620, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(autorange="reversed", visible=False),
                  xaxis=dict(range=[-0.8, 1.8]),
                  plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, width="stretch")

with st.expander("Tabla de datos"):
    st.dataframe(t[["ambito", "n", "altitud_mediana_m", "anemia_363", "anemia_363_li", "anemia_363_ls", "anemia_oms",
                    "anemia_oms_li", "anemia_oms_ls", "cambio_pp", "cambio_li", "cambio_ls", "cambio_pp_2024", "cambio_li_2024",
                    "cambio_ls_2024", "efecto_altitud_pp", "efecto_corte_pp", "puesto_363", "puesto_oms",
                    "puesto_363_2024", "puesto_oms_2024"]].round(1), hide_index=True)

with st.expander("Metodología, fuentes y limitaciones", expanded=True):
    st.markdown((RAIZ / "web" / "metodologia.md").read_text(encoding="utf-8"))
