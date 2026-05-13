import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dashboard TAT", layout="wide")

BASE_URL = "https://process-dashboard-file.s3.eu-north-1.amazonaws.com/processed"

DATA_ATUAL_URL = f"{BASE_URL}/dashboard-data.json"
HISTORICO_URL = f"{BASE_URL}/historico-tat.json"

st.title("Dashboard Operacional TAT")
st.write("Dados actualizados automaticamente a partir da AWS.")

@st.cache_data(ttl=30)
def load_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

actual = load_json(DATA_ATUAL_URL)
historico = load_json(HISTORICO_URL)

df_hist = pd.DataFrame(historico)
df_hist["data_snapshot"] = pd.to_datetime(df_hist["data_snapshot"])

st.subheader("KPIs actuais")

col1, col2, col3, col4 = st.columns(4)

col1.metric("TAT Cliente médio", actual.get("tat_cliente_medio"))
col2.metric("TAT Reparador médio", actual.get("tat_reparador_medio"))
col3.metric("TAT sem Reparador médio", actual.get("tat_sem_reparador_medio"))
col4.metric("Processos concluídos", actual.get("processos_concluidos"))

st.subheader("Evolução diária do TAT")

chart_df = df_hist.set_index("data_snapshot")[
    [
        "tat_cliente_medio",
        "tat_reparador_medio",
        "tat_sem_reparador_medio"
    ]
]

st.line_chart(chart_df)

st.subheader("Histórico")

st.dataframe(df_hist, use_container_width=True)
