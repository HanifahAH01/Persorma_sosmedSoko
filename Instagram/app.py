# ============================================
# 📊 STREAMLIT INSTAGRAM PERFORMANCE DASHBOARD
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ==============================
# PAGE CONFIG (HARUS PALING ATAS)
# ==============================
st.set_page_config(
    page_title="Instagram Performance Dashboard",
    layout="wide"
)

# ==============================
# LOAD DATA
# ==============================
file_path = "dataset_instagram-scraper.csv"
df = pd.read_csv(file_path)

cols = ['caption', 'commentsCount', 'likesCount', 'timestamp', 'type', 'videoViewCount']
available_cols = [c for c in cols if c in df.columns]
df = df[available_cols].copy()

# ==============================
# PREPROCESSING WAKTU
# ==============================
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])

df['date'] = df['timestamp'].dt.date
df['year'] = df['timestamp'].dt.year
df['month'] = df['timestamp'].dt.month
df['month_name'] = df['timestamp'].dt.strftime('%B')

# ==============================
# CLEAN NUMERIC
# ==============================
for col in ['likesCount', 'commentsCount', 'videoViewCount']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ==============================
# THEME SWITCHER
# ==============================
theme = st.selectbox(
    "🎨 Pilih Tema Dashboard",
    ["Dark", "Light", "Instagram", "Blue"],
    index=0
)

# ==============================
# DEFAULT WARNA (WAJIB ADA)
# ==============================
bg_color = "#0E1117"
card_color = "#161B22"
border_color = "#30363D"

chart_bg = "#0E1117"
plot_bg = "#0E1117"
grid_color = "#30363D"
font_color = "#FFFFFF"

# ==============================
# OVERRIDE WARNA PER TEMA
# ==============================
if theme == "Light":
    bg_color = "#FFFFFF"
    card_color = "#F5F5F5"
    border_color = "#E0E0E0"

    chart_bg = "#FFFFFF"
    plot_bg = "#FFFFFF"
    grid_color = "#E0E0E0"
    font_color = "#000000"

elif theme == "Instagram":
    bg_color = "linear-gradient(135deg, #F58529, #DD2A7B, #8134AF)"
    card_color = "rgba(255,255,255,0.2)"
    border_color = "rgba(255,255,255,0.4)"

    chart_bg = "rgba(0,0,0,0)"
    plot_bg = "rgba(0,0,0,0)"
    grid_color = "rgba(255,255,255,0.4)"
    font_color = "#FFFFFF"

elif theme == "Blue":
    bg_color = "#0A2540"
    card_color = "#102A44"
    border_color = "#1E3A5F"

    chart_bg = "#0A2540"
    plot_bg = "#0A2540"
    grid_color = "#1E3A5F"
    font_color = "#FFFFFF"

# ==============================
# APPLY GLOBAL CSS
# ==============================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg_color};
    }}

    [data-testid="metric-container"] {{
        background-color: {card_color};
        padding: 20px;
        border-radius: 14px;
        border: 1px solid {border_color};
    }}

    .stButton > button {{
        background-color: #1F6FEB;
        color: white;
        border-radius: 10px;
        height: 45px;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# LOGO TENGAH
# ==============================
with open("soko.jpg", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <style>
    .app-header {{
        display: flex;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }}
    .app-header img {{
        width: 200px;
    }}
    </style>

    <div class="app-header">
        <img src="data:image/jpg;base64,{logo_base64}">
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================
# TITLE
# ==============================
st.title("📊 Instagram Performance Dashboard")

# ==============================
# DATE FILTER
# ==============================
min_date, max_date = df['date'].min(), df['date'].max()
start_date, end_date = st.date_input(
    "📆 Pilih Rentang Tanggal",
    [min_date, max_date]
)

filtered_df = df[
    (df['date'] >= start_date) &
    (df['date'] <= end_date)
]

# ==============================
# METRICS
# ==============================
col1, col2, col3 = st.columns(3)
col1.metric("Total Post", len(filtered_df))
col2.metric("Total Likes", int(filtered_df['likesCount'].sum()))
col3.metric("Total Comments", int(filtered_df['commentsCount'].sum()))

st.divider()

# ==============================
# NAVIGASI BUTTON
# ==============================
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "post"

c1, c2, c3 = st.columns(3)
if c1.button("📅 Post per Hari"):
    st.session_state.active_tab = "post"
if c2.button("📊 Engagement"):
    st.session_state.active_tab = "engagement"
if c3.button("🍰 Distribusi Konten"):
    st.session_state.active_tab = "distribusi"

st.divider()

# ==============================
# TAB: POST PER HARI
# ==============================
if st.session_state.active_tab == "post":
    st.subheader("📅 Jumlah Postingan per Hari")

    colY, colM = st.columns(2)
    years = sorted(filtered_df['year'].unique())
    selected_year = colY.selectbox("Pilih Tahun", years)

    year_df = filtered_df[filtered_df['year'] == selected_year]

    months = (
        year_df[['month', 'month_name']]
        .drop_duplicates()
        .sort_values('month')
    )

    selected_month_name = colM.selectbox(
        "Pilih Bulan",
        months['month_name']
    )

    selected_month = months.loc[
        months['month_name'] == selected_month_name, 'month'
    ].iloc[0]

    final_df = year_df[year_df['month'] == selected_month]

    posts_per_day = final_df.groupby('date').size().reset_index(name='count')

    if not posts_per_day.empty:
        fig1 = px.line(posts_per_day, x='date', y='count', markers=True)

        fig1.update_layout(
            paper_bgcolor=chart_bg,
            plot_bgcolor=plot_bg,
            font=dict(color=font_color),
            xaxis=dict(gridcolor=grid_color),
            yaxis=dict(gridcolor=grid_color)
        )

        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("Tidak ada data pada periode ini.")

# ==============================
# TAB: ENGAGEMENT
# ==============================
elif st.session_state.active_tab == "engagement":
    st.subheader("📊 Rata-rata Engagement")

    engagement = (
        filtered_df
        .groupby('type')[['likesCount', 'commentsCount', 'videoViewCount']]
        .mean()
        .reset_index()
    )

    if not engagement.empty:
        fig2 = px.bar(
            engagement,
            x='type',
            y=['likesCount', 'commentsCount', 'videoViewCount'],
            barmode='group'
        )

        fig2.update_layout(
            paper_bgcolor=chart_bg,
            plot_bgcolor=plot_bg,
            font=dict(color=font_color),
            xaxis=dict(gridcolor=grid_color),
            yaxis=dict(gridcolor=grid_color)
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Data engagement tidak tersedia.")

# ==============================
# TAB: DISTRIBUSI
# ==============================
elif st.session_state.active_tab == "distribusi":
    st.subheader("🍰 Distribusi Jenis Konten")

    if not filtered_df.empty:
        fig3 = px.pie(filtered_df, names='type')

        fig3.update_layout(
            paper_bgcolor=chart_bg,
            font=dict(color=font_color)
        )

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Data tidak tersedia.")
