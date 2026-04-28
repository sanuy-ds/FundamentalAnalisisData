import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import streamlit as st

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Air Quality Dashboard: Aotizhongxin",
    page_icon="☁️",
    layout="wide"
)

# 2. CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 80px;
        padding-bottom: 50px;
    }
    [data-testid="stSidebar"] {
        overflow: visible !important;
    }
    .instruction-box {
    background-color: #1a3a52 !important;
    color: #e8f4fd !important;
    padding: 12px 16px;
    border-radius: 5px;
    border-left: 5px solid #ff4b4b;
    font-size: 14px;
    margin-bottom: 10px;
    line-height: 1.7;
}
.instruction-box b {
    color: #7ecef5 !important;
}
    .insight-box {
    background-color: #1a3a52 !important;
    color: #e8f4fd !important;
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 5px solid #4da6e8;
    font-size: 14px;
    margin-top: 10px;
    line-height: 1.7;
}
.insight-box b {
    color: #7ecef5 !important;
}
.insight-box code {
    background-color: #0f2233;
    color: #f0c040 !important;
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 13px;
}
.insight-box i {
    color: #a8d8f0 !important;
}
    </style>
    """, unsafe_allow_html=True)

# 3. LOAD DATA
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dashboard/all_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("all_data.csv")
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    if 'day_type' not in df.columns:
        df['day_type'] = df['datetime'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    if 'pres_group' not in df.columns:
        df['pres_group'] = pd.cut(df['PRES'], bins=3, labels=['Rendah', 'Normal', 'Tinggi'])
        
    return df

all_df = load_data()

# 4. SIDEBAR
with st.sidebar:
    st.image("https://tse2.mm.bing.net/th/id/OIP.fHET4vM8XHqXmSPKFbsvoAHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3")
    st.title("Pusat Kendali Data")
    st.markdown("---")
    
    st.markdown('<div class="instruction-box"><b>💡 Cara Memilih Periode:</b><br>1. Klik tanggal untuk <b>Periode Awal</b><br>2. Klik tanggal untuk <b>Periode Akhir</b></div>', unsafe_allow_html=True)

    min_date_ds = all_df["datetime"].min().date()
    max_date_ds = all_df["datetime"].max().date()

    st.subheader("📅 Filter Periode")
    
    date_range = st.date_input(
        label='Tentukan Rentang Waktu Analisis',
        min_value=min_date_ds,
        max_value=max_date_ds,
        value=[min_date_ds, max_date_ds],
        help="Pilih dua tanggal untuk menentukan awal dan akhir periode analisis."
    )
    
    if isinstance(date_range, (list, tuple)):
        if len(date_range) == 2:
            start_date, end_date = date_range
            st.success(f"✅ Rentang dipilih: \n{start_date} s/d {end_date}")
        else:
            start_date = date_range[0]
            end_date = max_date_ds
            st.warning("⚠️ Silakan pilih tanggal kedua (akhir).")
    else:
        start_date, end_date = min_date_ds, max_date_ds

    main_df = all_df[(all_df["datetime"].dt.date >= start_date) & 
                     (all_df["datetime"].dt.date <= end_date)]

    st.markdown("---")
    st.write(f"📊 **Data Terpilih:** {len(main_df):,} baris")

#HELPER: STATUS PM2.5
def get_pm25_status(val):
    if val <= 15:
        return "🟢 Baik", "normal"
    elif val <= 35:
        return "🟡 Sedang", "off"
    elif val <= 75:
        return "🟠 Tidak Sehat", "inverse"
    else:
        return "🔴 Berbahaya", "inverse"

# 5. MAIN PAGE
st.title("☁️ Air Quality Dashboard: Stasiun Aotizhongxin")
st.markdown(f"Menampilkan data dari: **{start_date}** hingga **{end_date}**")

# METRICS
col1, col2, col3 = st.columns(3)
with col1:
    avg_pm25 = main_df['PM2.5'].mean()
    status_label, status_delta_color = get_pm25_status(avg_pm25)
    st.metric(
        label="Rata-rata PM2.5",
        value=f"{avg_pm25:.2f} µg/m³",
        delta=status_label,
        delta_color=status_delta_color,
        help="Standar WHO: ≤15 µg/m³ (Baik), ≤35 µg/m³ (Sedang), ≤75 µg/m³ (Tidak Sehat)"
    )
with col2:
    avg_pm10 = main_df['PM10'].mean()
    pm10_status = "🟢 Baik (< 45 µg/m³)" if avg_pm10 < 45 else ("🟡 Sedang" if avg_pm10 < 100 else "🔴 Tinggi")
    st.metric(
        label="Rata-rata PM10",
        value=f"{avg_pm10:.2f} µg/m³",
        delta=pm10_status,
        delta_color="normal" if avg_pm10 < 45 else "inverse",
        help="Standar WHO: ≤45 µg/m³ (Baik), ≤100 µg/m³ (Sedang)"
    )
with col3:
    max_temp = main_df['TEMP'].max()
    avg_temp = main_df['TEMP'].mean()
    st.metric(
        label="Suhu Maksimum",
        value=f"{max_temp:.1f} °C",
        delta=f"Rata-rata: {avg_temp:.1f} °C",
        delta_color="off",
        help="Suhu tinggi dapat meningkatkan pembentukan ozon dan polutan sekunder"
    )

st.divider()

# TAB ANALISIS
tab1, tab2, tab3 = st.tabs(["📊 Korelasi Polutan", "📅 Pola Hari Kerja vs Akhir Pekan", "🌡️ Tekanan Udara vs PM10"])

# TAB 1: KORELASI
with tab1:
    st.subheader("Pertanyaan 1: Polutan gas mana yang paling erat hubungannya dengan PM2.5?")
    st.markdown("**Tujuan:** Memahami polutan mana yang paling erat hubungannya dengan PM2.5 — sehingga bisa menjadi indikator awal pencemaran udara.")

    corr_cols = ['PM2.5', 'SO2', 'NO2', 'CO', 'O3']
    corr = main_df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 5))
    mask = np.zeros_like(corr, dtype=bool)
    mask[np.triu_indices_from(mask, k=1)] = True  # Sembunyikan segitiga atas (redundan)
    
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap='RdYlGn',
        ax=ax,
        linewidths=0.5,
        linecolor='white',
        vmin=-1, vmax=1,
        annot_kws={"size": 11, "weight": "bold"},
        cbar_kws={"label": "Koefisien Korelasi Pearson"}
    )
    ax.set_title("Matriks Korelasi Antar Polutan", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis='x', labelrotation=0, labelsize=11)
    ax.tick_params(axis='y', labelrotation=0, labelsize=11)
    plt.tight_layout()
    st.pyplot(fig)

    # Insight otomatis dari korelasi PM2.5
    pm25_corr = corr['PM2.5'].drop('PM2.5').sort_values(ascending=False)
    top_pollutant = pm25_corr.index[0]
    top_val = pm25_corr.iloc[0]
    low_pollutant = pm25_corr.index[-1]
    low_val = pm25_corr.iloc[-1]

    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Insight Utama:</b><br>
    • <b>{top_pollutant}</b> memiliki korelasi <b>tertinggi</b> dengan PM2.5 (<code>{top_val:.2f}</code>) → kemungkinan berasal dari sumber emisi yang sama (mis. kendaraan/industri).<br>
    • <b>{low_pollutant}</b> memiliki korelasi <b>terendah/negatif</b> (<code>{low_val:.2f}</code>) → pola terbalik, karena O3 cenderung terbentuk saat PM2.5 rendah (sinar matahari kuat).<br>
    • Nilai mendekati <b>+1</b> = polutan naik bersama PM2.5. Nilai mendekati <b>-1</b> = berlawanan arah.
    </div>
    """, unsafe_allow_html=True)

# TAB 2: POLA HARI
with tab2:
    st.subheader("Pertanyaan 2: Apakah aktivitas hari kerja berdampak lebih besar terhadap PM2.5 dibanding akhir pekan?")
    st.markdown("**Tujuan:** Mengetahui apakah aktivitas manusia (kerja & transportasi) pada hari kerja berdampak signifikan terhadap kadar PM2.5.")

    weekday_avg = main_df[main_df['day_type'] == 'Weekday']['PM2.5'].mean()
    weekend_avg = main_df[main_df['day_type'] == 'Weekend']['PM2.5'].mean()
    diff_pct = ((weekday_avg - weekend_avg) / weekend_avg) * 100

    palette_colors = ['#E74C3C' if weekday_avg > weekend_avg else '#3498DB',
                      '#3498DB' if weekday_avg > weekend_avg else '#E74C3C']

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = sns.barplot(
        x='day_type', y='PM2.5',
        data=main_df,
        palette=palette_colors,
        ax=ax,
        order=['Weekday', 'Weekend'],
        width=0.5,
        capsize=0.1,
        err_kws={'linewidth': 1.5}
    )

    # Garis referensi WHO
    WHO_LIMIT = 15
    ax.axhline(y=WHO_LIMIT, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(1.45, WHO_LIMIT + 0.5, f'Batas WHO: {WHO_LIMIT} µg/m³', color='red', fontsize=9, va='bottom')

    # Anotasi nilai di atas bar
    for i, p in enumerate(ax.patches):
        val = [weekday_avg, weekend_avg][i]
        ax.annotate(
            f'{val:.1f} µg/m³',
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            xytext=(0, 6), textcoords='offset points'
        )

    ax.set_title("Rata-rata PM2.5: Hari Kerja vs Akhir Pekan", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Tipe Hari", fontsize=11)
    ax.set_ylabel("Konsentrasi PM2.5 (µg/m³)", fontsize=11)
    ax.set_xticklabels(['Hari Kerja (Sen–Jum)', 'Akhir Pekan (Sab–Min)'], fontsize=11)
    
    # Legend warna
    ax.legend().set_visible(False)
    ax.set_ylim(0, max(weekday_avg, weekend_avg) * 1.3)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

    higher_day = "Hari Kerja" if weekday_avg > weekend_avg else "Akhir Pekan"
    lower_day = "Akhir Pekan" if weekday_avg > weekend_avg else "Hari Kerja"
    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Insight Utama:</b><br>
    • <b>{higher_day}</b> memiliki PM2.5 lebih tinggi ({abs(diff_pct):.1f}%) dibanding {lower_day}.<br>
    • {"Pola ini konsisten dengan tingginya aktivitas kendaraan & industri di hari kerja." if weekday_avg > weekend_avg else "Ini bisa mengindikasikan aktivitas rekreasi atau pembakaran sampah lebih banyak saat akhir pekan."}<br>
    • Kedua tipe hari <b>melampaui batas WHO</b> ({WHO_LIMIT} µg/m³) → kualitas udara secara umum <b>perlu perhatian</b>.
    </div>
    """, unsafe_allow_html=True)

# TAB 3: TEKANAN UDARA
with tab3:
    st.subheader("Analisis lanjutan: Bagaimana tekanan udara memengaruhi konsentrasi PM10?")
    st.markdown("**Tujuan:** Memahami bagaimana kondisi tekanan atmosfer memengaruhi konsentrasi partikel kasar (PM10) di udara.")

    pres_summary = main_df.groupby('pres_group', observed=False)['PM10'].agg(['mean', 'std', 'count']).reset_index()
    pres_summary.columns = ['pres_group', 'mean_pm10', 'std_pm10', 'count']

    color_map = {'Rendah': '#5DADE2', 'Normal': '#58D68D', 'Tinggi': '#EC7063'}
    bar_colors = [color_map.get(str(g), '#95A5A6') for g in pres_summary['pres_group']]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        pres_summary['pres_group'].astype(str),
        pres_summary['mean_pm10'],
        color=bar_colors,
        width=0.45,
        edgecolor='white',
        linewidth=1.2,
        yerr=pres_summary['std_pm10'],
        capsize=5,
        error_kw={'elinewidth': 1.5, 'ecolor': 'gray', 'alpha': 0.6}
    )

    # Anotasi nilai + jumlah data
    for i, (bar, row) in enumerate(zip(bars, pres_summary.itertuples())):
        ax.annotate(
            f'{row.mean_pm10:.1f} µg/m³',
            (bar.get_x() + bar.get_width() / 2., bar.get_height()),
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            xytext=(0, 6), textcoords='offset points'
        )
        ax.annotate(
            f'n = {row.count:,}',
            (bar.get_x() + bar.get_width() / 2., bar.get_height() / 2),
            ha='center', va='center', fontsize=9, color='white', fontweight='bold'
        )

    ax.set_title("Rata-rata PM10 per Kelompok Tekanan Udara\n(± Standar Deviasi)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Kelompok Tekanan Udara (PRES)", fontsize=11)
    ax.set_ylabel("Konsentrasi PM10 (µg/m³)", fontsize=11)
    ax.set_xticklabels(
        ['Rendah\n(tekanan kecil,\nudara lebih bergejolak)',
         'Normal\n(kondisi atmosfer\nstabil)',
         'Tinggi\n(tekanan besar,\npartikel terperangkap)'],
        fontsize=9
    )

    # Legend warna
    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
    ax.legend(handles=legend_patches, fontsize=9, title="Kelompok Tekanan", title_fontsize=9)
    ax.set_ylim(0, pres_summary['mean_pm10'].max() * 1.35)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

    max_group = pres_summary.loc[pres_summary['mean_pm10'].idxmax(), 'pres_group']
    min_group = pres_summary.loc[pres_summary['mean_pm10'].idxmin(), 'pres_group']
    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Insight Utama:</b><br>
    • Tekanan udara <b>{max_group}</b> menghasilkan PM10 tertinggi → tekanan tinggi menghambat dispersi vertikal udara, sehingga partikel terakumulasi di permukaan.<br>
    • Tekanan <b>{min_group}</b> memiliki PM10 terendah → udara lebih aktif bersirkulasi, membantu menyebarkan polutan.<br>
    • <i>Error bar</i> (garis abu-abu) menunjukkan variasi data — semakin panjang, semakin beragam kondisi di kelompok tersebut.
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("Copyright © 2026 | Submission Fundamental Analisis Data - Yunas Wildan")