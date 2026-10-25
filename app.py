import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Konfigurasi Halaman (Harus di baris paling atas)
st.set_page_config(
    page_title="Dashboard Analisis Fiskal & Makroekonomi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Fungsi Load Data dengan Caching
@st.cache_data
def load_data():
    df = pd.read_csv("dataset_fiskal_97_hipoFull.csv")
    return df

df = load_data()

# 3. Pengaturan Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3004/3004122.png", width=100)
st.sidebar.title("Panel Navigasi")
st.sidebar.markdown("Filter data berdasarkan kota dan rentang waktu.")

# Filter Kota
kota_list = df['Kota'].unique().tolist()
kota_pilihan = st.sidebar.selectbox("Pilih Kota/Kabupaten:", kota_list)

# Filter Tahun
min_tahun = int(df['Tahun'].min())
max_tahun = int(df['Tahun'].max())
tahun_pilihan = st.sidebar.slider("Pilih Rentang Tahun:", min_tahun, max_tahun, (min_tahun, max_tahun))

# Proses Filter Data
df_filtered = df[(df['Kota'] == kota_pilihan) & 
                 (df['Tahun'] >= tahun_pilihan[0]) & 
                 (df['Tahun'] <= tahun_pilihan[1])]

# 4. Judul Dashboard
st.title(f"📊 Dashboard Kinerja Fiskal & Makroekonomi: {kota_pilihan}")
st.markdown("Analisis komprehensif mengenai pendapatan, pengeluaran, dan indikator kesejahteraan.")
st.divider()

# 5. Baris Metrik Utama (KPI)
# Mengambil data tahun terakhir dari filter untuk menampilkan metrik saat ini
tahun_terakhir = df_filtered['Tahun'].max()
df_latest = df_filtered[df_filtered['Tahun'] == tahun_terakhir]

if not df_latest.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"PAD ({tahun_terakhir})", value=f"{df_latest['PAD'].values[0]:.2f}")
    with col2:
        st.metric(label=f"Indeks Pembangunan Manusia", value=f"{df_latest['IPM'].values[0]:.2f}")
    with col3:
        st.metric(label=f"Tingkat Kemiskinan (%)", value=f"{df_latest['KEMISKINAN'].values[0]:.2f}")
    with col4:
        st.metric(label=f"Pertumbuhan Ekonomi (%)", value=f"{df_latest['PE'].values[0]:.2f}")

st.divider()

# 6. Pembuatan Tab untuk Kerapian Tata Letak
tab1, tab2, tab3 = st.tabs(["💰 Keuangan Daerah", "🏗️ Alokasi Belanja Modal", "📈 Indikator Makroekonomi"])

with tab1:
    st.subheader("Tren Pendapatan Daerah & Dana Transfer")
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Line Chart PAD vs DAU
        fig_pendapatan = go.Figure()
        fig_pendapatan.add_trace(go.Scatter(x=df_filtered['Tahun'], y=df_filtered['PAD'], mode='lines+markers', name='PAD', line=dict(color='green')))
        fig_pendapatan.add_trace(go.Scatter(x=df_filtered['Tahun'], y=df_filtered['DAU_Grant'], mode='lines+markers', name='DAU Grant', line=dict(color='blue')))
        fig_pendapatan.update_layout(title="Komparasi PAD dan DAU Grant", xaxis_title="Tahun", yaxis_title="Nilai", legend=dict(orientation="h", ybottom=-0.2))
        st.plotly_chart(fig_pendapatan, use_container_width=True)
        
    with col_b:
        # Bar Chart Dana Bagi Hasil (DBH)
        fig_dbh = px.bar(df_filtered, x='Tahun', y=['DBH_PAJAK', 'DBH_SDA', 'DBH_Lainnya'],
                         title="Komposisi Dana Bagi Hasil (DBH)",
                         labels={'value': 'Total DBH', 'variable': 'Kategori'},
                         barmode='stack')
        st.plotly_chart(fig_dbh, use_container_width=True)

with tab2:
    st.subheader("Distribusi Belanja Modal Sektoral")
    
    # Menghitung rata-rata belanja modal selama periode yang dipilih
    belanja_cols = ['bm_pendidikan', 'bm_kesehatan', 'bm_perumahan', 'bm_lingkungan', 'bm_ekonomi', 'bm_infrastruktur', 'bm_pariwisata', 'bm_perlindungan_sosial']
    df_belanja = df_filtered[belanja_cols].mean().reset_index()
    df_belanja.columns = ['Sektor', 'Rata-rata Alokasi']
    df_belanja['Sektor'] = df_belanja['Sektor'].str.replace('bm_', '').str.title()
    
    col_c, col_d = st.columns([1, 1])
    with col_c:
        # Pie Chart Proporsi Belanja
        fig_pie = px.pie(df_belanja, values='Rata-rata Alokasi', names='Sektor', 
                         title=f"Proporsi Belanja Modal ({tahun_pilihan[0]}-{tahun_pilihan[1]})",
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_d:
        # Tabel Belanja
        st.dataframe(df_filtered[['Tahun'] + belanja_cols].set_index('Tahun').style.highlight_max(axis=0), use_container_width=True)

with tab3:
    st.subheader("Analisis Kesejahteraan Sosial & Ekonomi")
    
    col_e, col_f = st.columns(2)
    with col_e:
        # Dual-axis chart untuk Kemiskinan & Pengangguran
        fig_sosial = px.line(df_filtered, x='Tahun', y=['KEMISKINAN', 'PENGANGGURAN'], 
                             title="Tren Kemiskinan dan Pengangguran (%)",
                             markers=True)
        st.plotly_chart(fig_sosial, use_container_width=True)
        
    with col_f:
        # Scatter plot Hubungan PAD dan IPM
        fig_scatter = px.scatter(df_filtered, x='PAD', y='IPM', size='PE', color='Tahun',
                                 hover_name='Tahun', title="Korelasi PAD, IPM, dan Pertumbuhan Ekonomi (Size)",
                                 size_max=20)
        st.plotly_chart(fig_scatter, use_container_width=True)

# 7. Footer
st.markdown("---")
st.caption("Sumber Data: Dataset Fiskal HipoFull | Dibuat menggunakan Streamlit & Plotly")
