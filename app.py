import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Journey - Service Operations Dashboard", layout="wide")

BASE_URL = "https://process-dashboard-file.s3.eu-north-1.amazonaws.com/processed"
DATA_ATUAL_URL = f"{BASE_URL}/dashboard-data.json"
HISTORICO_URL = f"{BASE_URL}/historico-tat.json"

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    background-color: #f5f7fb;
}

.header {
    background-color: #111827;
    padding: 22px;
    border-radius: 0 0 14px 14px;
    color: white;
    margin-bottom: 20px;
}

.kpi-card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.kpi-label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: #111827;
}

.section-card {
    background-color: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


actual = load_json(DATA_ATUAL_URL)
historico = load_json(HISTORICO_URL)

df_hist = pd.DataFrame(historico)

if not df_hist.empty:
    df_hist["data_snapshot"] = pd.to_datetime(df_hist["data_snapshot"])


st.markdown("""
<div class="header">
    <h2>Journey - Service Operations Dashboard</h2>
    <p>Jan–Mai 2026</p>
</div>
""", unsafe_allow_html=True)


# KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)

kpis = [
    ("Ordens", actual.get("total_linhas", 0)),
    ("TAT Cliente", actual.get("tat_cliente_medio", "-")),
    ("TAT Reparador", actual.get("tat_reparador_medio", "-")),
    ("TAT sem Reparador", actual.get("tat_sem_reparador_medio", "-")),
    ("% Rep / Cliente", "-"),
    ("Taxa Sucesso", "-"),
]

for col, (label, value) in zip([col1, col2, col3, col4, col5, col6], kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# Filtros
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📊 Journey do Processo de Reparação")

f1, f2, f3 = st.columns(3)

with f1:
    filtro_rep = st.selectbox("Reparador", ["Todos"])

with f2:
    filtro_marca = st.selectbox("Marca", ["Todas"])

with f3:
    filtro_categoria = st.selectbox("Categoria", ["Todas"])

st.markdown("</div>", unsafe_allow_html=True)


# Blocos grandes TAT
col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"""
    <div style="background:#2563eb;color:white;padding:35px;border-radius:16px;text-align:center;">
        <h4>🔧 TAT Reparador</h4>
        <h1>{actual.get("tat_reparador_medio", "-")}d</h1>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div style="background:#f97316;color:white;padding:35px;border-radius:16px;text-align:center;">
        <h4>🚚 TAT sem Reparador</h4>
        <h1>{actual.get("tat_sem_reparador_medio", "-")}d</h1>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# Gráficos principais
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("TAT total e reparador por mês")

    if not df_hist.empty:
        chart_df = df_hist.copy()
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=chart_df["data_snapshot"],
            y=chart_df["tat_cliente_medio"],
            mode="lines+markers",
            name="TAT Cliente"
        ))

        fig.add_trace(go.Scatter(
            x=chart_df["data_snapshot"],
            y=chart_df["tat_reparador_medio"],
            mode="lines+markers",
            name="Reparador"
        ))

        fig.add_trace(go.Scatter(
            x=chart_df["data_snapshot"],
            y=chart_df["tat_sem_reparador_medio"],
            mode="lines+markers",
            name="Sem Reparador",
            line=dict(dash="dot")
        ))

        fig.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Indicadores Operacionais")

    if not df_hist.empty:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_hist["data_snapshot"],
            y=df_hist["total_linhas"],
            name="Ordens"
        ))

        fig.add_trace(go.Scatter(
            x=df_hist["data_snapshot"],
            y=df_hist["processos_concluidos"],
            mode="lines+markers",
            name="Processos concluídos",
            yaxis="y2"
        ))

        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(title="Ordens"),
            yaxis2=dict(title="Concluídos", overlaying="y", side="right")
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# Segunda linha
col3, col4, col5 = st.columns([1, 1, 1])

with col3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Decomposição TAT")

    tat_rep = actual.get("tat_reparador_medio") or 0
    tat_sem = actual.get("tat_sem_reparador_medio") or 0

    decomp = pd.DataFrame({
        "Tipo": ["TAT Reparador", "TAT sem Reparador"],
        "Valor": [tat_rep, tat_sem]
    })

    fig = px.bar(decomp, x="Valor", y="Tipo", orientation="h")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


with col4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Reparador vs sem Reparador")

    if not df_hist.empty:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_hist["data_snapshot"],
            y=df_hist["tat_reparador_medio"],
            name="Reparador"
        ))

        fig.add_trace(go.Bar(
            x=df_hist["data_snapshot"],
            y=df_hist["tat_sem_reparador_medio"],
            name="Sem Reparador"
        ))

        fig.update_layout(
            barmode="stack",
            height=280,
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


with col5:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Motivo de Fecho")

    motivos = pd.DataFrame({
        "Motivo": ["Reparação ok", "Sem avaria", "Troca", "Não reparado"],
        "Peso": [65, 15, 12, 8]
    })

    fig = px.pie(motivos, names="Motivo", values="Peso", hole=0.55)
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# Histórico
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Histórico")
st.dataframe(df_hist, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
