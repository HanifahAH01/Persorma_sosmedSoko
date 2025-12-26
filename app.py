# ============================================
# 🧩 STREAMLIT DASHBOARD DENGAN BUTTON SEJAJAR
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Load Data ----
file_path = "dataset_instagram-scraper.csv"
df = pd.read_csv(file_path)

cols = ['caption', 'commentsCount', 'likesCount', 'timestamp', 'type', 'videoViewCount']
available_cols = [c for c in cols if c in df.columns]
df = df[available_cols].copy()

# ---- Preprocessing WAKTU (WAJIB) ----
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])

df['date'] = df['timestamp'].dt.date
df['year'] = df['timestamp'].dt.year
df['month'] = df['timestamp'].dt.month
df['month_name'] = df['timestamp'].dt.strftime('%B')

# ---- Numeric cleaning ----
for col in ['likesCount', 'commentsCount', 'videoViewCount']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ---- Streamlit UI ----
st.set_page_config(page_title="Instagram Performance Dashboard", layout="wide")
st.title("📊 Instagram Performance Dashboard")

# ---- Filter tanggal (GLOBAL) ----
min_date, max_date = df['date'].min(), df['date'].max()
start_date, end_date = st.date_input(
    "📆 Pilih rentang tanggal:",
    [min_date, max_date]
)

mask = (df['date'] >= start_date) & (df['date'] <= end_date)
filtered_df = df[mask]

# ---- Metrik ----
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Post", len(filtered_df))
with col2:
    st.metric("Total Likes", int(filtered_df['likesCount'].sum()))
with col3:
    st.metric("Total Comments", int(filtered_df['commentsCount'].sum()))

st.divider()

# ==============================
# NAVIGASI BUTTON SEJAJAR
# ==============================
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "post_per_hari"

colA, colB, colC = st.columns(3)
with colA:
    if st.button("📅 Jumlah Postingan per Hari"):
        st.session_state.active_tab = "post_per_hari"
with colB:
    if st.button("📊 Rata-rata Engagement"):
        st.session_state.active_tab = "engagement"
with colC:
    if st.button("🍰 Distribusi Jenis Konten"):
        st.session_state.active_tab = "distribusi"

st.divider()

# ==============================
# TAB: POST PER HARI + FILTER BULAN & TAHUN
# ==============================
if st.session_state.active_tab == "post_per_hari":
    st.subheader("📅 Jumlah Postingan per Hari")

    colY, colM = st.columns(2)

    # ---- Filter Tahun ----
    available_years = sorted(filtered_df['year'].unique())
    selected_year = colY.selectbox("📆 Pilih Tahun", available_years)

    year_df = filtered_df[filtered_df['year'] == selected_year]

    # ---- Filter Bulan ----
    available_months = (
        year_df[['month', 'month_name']]
        .drop_duplicates()
        .sort_values('month')
    )

    selected_month_name = colM.selectbox(
        "🗓️ Pilih Bulan",
        available_months['month_name']
    )

    selected_month = available_months.loc[
        available_months['month_name'] == selected_month_name,
        'month'
    ].iloc[0]

    final_df = year_df[year_df['month'] == selected_month]

    posts_per_day = (
        final_df.groupby('date')
        .size()
        .reset_index(name='count')
    )

    if posts_per_day.empty:
        st.warning("Tidak ada data postingan pada bulan & tahun ini.")
    else:
        fig1 = px.line(
            posts_per_day,
            x='date',
            y='count',
            markers=True
        )
        fig1.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Postingan"
        )
        st.plotly_chart(fig1, use_container_width=True)

# ==============================
# TAB: ENGAGEMENT
# ==============================
elif st.session_state.active_tab == "engagement":
    st.subheader("📊 Rata-rata Engagement per Jenis Konten")

    engagement = (
        filtered_df
        .groupby('type')[['likesCount', 'commentsCount', 'videoViewCount']]
        .mean()
        .reset_index()
    )

    if engagement.empty:
        st.warning("Data engagement tidak tersedia.")
    else:
        fig2 = px.bar(
            engagement,
            x='type',
            y=['likesCount', 'commentsCount', 'videoViewCount'],
            barmode='group'
        )
        fig2.update_layout(
            xaxis_title="Jenis Konten",
            yaxis_title="Rata-rata Nilai"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ==============================
# TAB: DISTRIBUSI KONTEN
# ==============================
elif st.session_state.active_tab == "distribusi":
    st.subheader("🍰 Distribusi Jenis Konten")

    if filtered_df.empty or 'type' not in filtered_df.columns:
        st.warning("Data jenis konten tidak tersedia.")
    else:
        fig3 = px.pie(filtered_df, names='type')
        st.plotly_chart(fig3, use_container_width=True)

st.divider()
# st.markdown("Dibuat dengan ❤️ menggunakan Streamlit & Plotly")
