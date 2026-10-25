import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Dashboard Analisis Fiskal Daerah")

@st.cache_data
def load_data():
    return pd.read_csv("dataset_fiskal_97_hipoFull.csv")

df = load_data()

# Sidebar Filter
kota_pilihan = st.sidebar.selectbox("Pilih Kota:", df['Kota'].unique())
df_kota = df[df['Kota'] == kota_pilihan]

# Visualisasi Interaktif
st.subheader(f"Tren Pendapatan Asli Daerah (PAD) - {kota_pilihan}")
fig_pad = px.line(df_kota, x='Tahun', y='PAD', markers=True)
st.plotly_chart(fig_pad)

# Tabel Metrik Makroekonomi
st.subheader("Data Indikator Fiskal & Sosial")
st.dataframe(df_kota[['Tahun', 'PAD', 'IPM', 'PE', 'KEMISKINAN', 'PENGANGGURAN']])
