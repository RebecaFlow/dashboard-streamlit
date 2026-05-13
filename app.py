import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Journey Dashboard", layout="wide")

BASE_URL = "https://process-dashboard-file.s3.eu-north-1.amazonaws.com/processed"

URLS = {
    "actual": f"{BASE_URL}/dashboard-data.json",
    "historico": f"{BASE_URL}/historico-tat.json",
    "mensal": f"{BASE_URL}/mensal.json",
    "motivos": f"{BASE_URL}/motivos-fecho.json",
    "reparadores": f"{BASE_URL}/reparadores.json",
    "lojas": f"{BASE_URL}/lojas.json",
    "marcas": f"{BASE_URL}/marcas.json",
    "categorias": f"{BASE_URL}/categorias.json",
}

st.markdown("""
<style>
.stApp { background-color: #f3f6fb; }

.block-container {
    padding-top: 1rem;
    max-width: 1600px;
}

.header {
    background: linear-gradient(90deg,#111827,#1e3a8a);
    padding: 24px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
}

.kpi-card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    height: 118px;
}

.kpi-label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 700;
}

.kpi-value {
    font-size: 32px;
    font-weight: 800;
    color: #111827;
}

.big-blue {
    background: linear-gradient(135deg,#2563eb,#60a5fa);
    color: white;
    padding: 30px;
    border-radius: 18px;
    text-align: center;
}

.big-orange {
    background: linear-gradient(135deg,#ea580c,#fb923c);
    color: white;
    padding: 30px;
    border-radius: 18px;
    text-align: center;
}

.metric-big {
    font-size: 52px;
    font-weight: 800;
}

.section-title {
    font-weight: 800;
    font-size: 20px;
    margin-top: 8px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


actual = load_json(URLS["actual"])
historico = pd.DataFrame(load_json(URLS["historico"]))
mensal = pd.DataFrame(load_json(URLS["mensal"]))
motivos = pd.DataFrame(load_json(URLS["motivos"]))
reparadores = pd.DataFrame(load_json(URLS["reparadores"]))
lojas = pd.DataFrame(load_json(URLS["lojas"]))
marcas = pd.DataFrame(load_json(URLS["marcas"]))
categorias = pd.DataFrame(load_json(URLS["categorias"]))

st.markdown("""
<div class="header">
    <h2 style="color:white;margin-bottom:0;">Journey - Service Operations Dashboard</h2>
    <p style="margin-bottom:0;">Dados actuais + evolução histórica automática</p>
</div>
""", unsafe_allow_html=True)

tab_actual, tab_hist = st.tabs(["📊 Visão Actual", "📈 Histórico"])


with tab_actual:
    col1, col2, col3, col4, col5 = st.columns(5)

    kpis = [
        ("Ordens", actual.get("ordens", "-")),
        ("TAT Cliente", f'{actual.get("tat_cliente", "-")}d'),
        ("TAT Reparador", f'{actual.get("tat_reparador", "-")}d'),
        ("TAT sem Reparador", f'{actual.get("tat_sem_reparador", "-")}d'),
        ("% Rep / Cliente", f'{actual.get("peso_rep_cliente", "-")}%'),
    ]

    for col, (label, value) in zip([col1, col2, col3, col4, col5], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    a, b = st.columns(2)

    with a:
        st.markdown(f"""
        <div class="big-blue">
            <h3 style="color:white;">🔧 TAT Reparador</h3>
            <div class="metric-big">{actual.get("tat_reparador", "-")}d</div>
            <p>Tempo médio em reparador</p>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown(f"""
        <div class="big-orange">
            <h3 style="color:white;">🚚 TAT sem Reparador</h3>
            <div class="metric-big">{actual.get("tat_sem_reparador", "-")}d</div>
            <p>Tempo médio fora do reparador</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">TAT por mês</div>', unsafe_allow_html=True)

        if not mensal.empty:
            mensal = mensal.sort_values("mes")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=mensal["mes"], y=mensal["tat_cliente"], mode="lines+markers", name="TAT Cliente"))
            fig.add_trace(go.Scatter(x=mensal["mes"], y=mensal["tat_reparador"], mode="lines+markers", name="TAT Reparador"))
            fig.add_trace(go.Scatter(x=mensal["mes"], y=mensal["tat_sem"], mode="lines+markers", name="TAT sem Reparador"))

            fig.update_layout(
                height=360,
                template="plotly_white",
                margin=dict(l=10, r=10, t=20, b=10),
                legend=dict(orientation="h")
            )

            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Volume por mês</div>', unsafe_allow_html=True)

        if not mensal.empty:
            fig = px.bar(mensal.sort_values("mes"), x="mes", y="volume")
            fig.update_layout(
                height=360,
                template="plotly_white",
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-title">Motivos de fecho</div>', unsafe_allow_html=True)

        if not motivos.empty:
            fig = px.pie(motivos, names="motivo", values="valor", hole=0.55)
            fig.update_layout(
                height=360,
                template="plotly_white",
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown('<div class="section-title">Top reparadores por TAT</div>', unsafe_allow_html=True)

        if not reparadores.empty:
            fig = px.bar(
                reparadores.sort_values("tat", ascending=True),
                x="tat",
                y="reparador",
                orientation="h",
                hover_data=["volume"]
            )
            fig.update_layout(
                height=360,
                template="plotly_white",
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

    c5, c6, c7 = st.columns(3)

    with c5:
        st.markdown('<div class="section-title">Top marcas</div>', unsafe_allow_html=True)
        if not marcas.empty:
            fig = px.bar(marcas, x="volume", y="marca", orientation="h")
            fig.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with c6:
        st.markdown('<div class="section-title">Top categorias</div>', unsafe_allow_html=True)
        if not categorias.empty:
            fig = px.bar(categorias, x="volume", y="categoria", orientation="h")
            fig.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with c7:
        st.markdown('<div class="section-title">Top lojas</div>', unsafe_allow_html=True)
        if not lojas.empty:
            fig = px.bar(lojas, x="volume", y="loja", orientation="h")
            fig.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)


with tab_hist:
    st.markdown('<div class="section-title">Evolução histórica dos KPIs</div>', unsafe_allow_html=True)

    if not historico.empty:
        historico["data_snapshot"] = pd.to_datetime(historico["data_snapshot"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historico["data_snapshot"], y=historico["tat_cliente"], mode="lines+markers", name="TAT Cliente"))
        fig.add_trace(go.Scatter(x=historico["data_snapshot"], y=historico["tat_reparador"], mode="lines+markers", name="TAT Reparador"))
        fig.add_trace(go.Scatter(x=historico["data_snapshot"], y=historico["tat_sem_reparador"], mode="lines+markers", name="TAT sem Reparador"))

        fig.update_layout(
            height=420,
            template="plotly_white",
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h")
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Volume histórico</div>', unsafe_allow_html=True)

        fig2 = px.bar(historico, x="data_snapshot", y="ordens")
        fig2.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Tabela histórica</div>', unsafe_allow_html=True)
        st.dataframe(historico, use_container_width=True)
