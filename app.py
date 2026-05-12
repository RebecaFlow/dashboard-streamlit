import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Dashboard automático")
st.write("Dados actualizados automaticamente a partir da AWS.")

DATA_URL = "https://process-dashboard-file.s3.eu-north-1.amazonaws.com/processed/dashboard-data.json"

@st.cache_data(ttl=30)
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data)

df = load_data()

st.subheader("Tabela de dados")
st.dataframe(df, use_container_width=True)

st.subheader("Gráfico")

df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

st.bar_chart(df, x="categoria", y="valor")
