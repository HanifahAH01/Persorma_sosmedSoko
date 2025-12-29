# ============================================
# 🧩 LINKEDIN PERFORMANCE DASHBOARD
# (UPDATED & FUTURE-PROOF)
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import base64

# ======================
# PAGE CONFIG (WAJIB PALING ATAS)
# ======================
st.set_page_config(
    page_title="LinkedIn Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==============================
# THEME SWITCHER
# ==============================
theme = st.selectbox(
    "🎨 Pilih Tema Dashboard",
    ["Dark", "Light", "Blue"],
    index=0
)

# ==============================
# THEME COLORS
# ==============================
bg_color = "#0E1117"
card_color = "#161B22"
border_color = "#30363D"
font_color = "#FFFFFF"

if theme == "Light":
    bg_color = "#FFFFFF"
    card_color = "#F5F5F5"
    border_color = "#E0E0E0"
    font_color = "#000000"

#elif theme == "Instagram":
 #   bg_color = "linear-gradient(135deg, #F58529, #DD2A7B, #8134AF)"
  #  card_color = "rgba(255,255,255,0.25)"
   # border_color = "rgba(255,255,255,0.4)"
    #font_color = "#FFFFFF"

elif theme == "Blue":
    bg_color = "#0A2540"
    card_color = "#102A44"
    border_color = "#1E3A5F"
    font_color = "#FFFFFF"

# ==============================
# GLOBAL CSS
# ==============================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg_color};
        color: {font_color};
    }}

    [data-testid="metric-container"] {{
        background-color: {card_color};
        padding: 18px;
        border-radius: 14px;
        border: 1px solid {border_color};
    }}

    div.stButton {{
        display: flex;
        justify-content: center;
    }}

    div.stButton > button {{
        min-width: 160px;
        height: 42px;
        border-radius: 10px;
        font-weight: 500;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# LOGO (TENGAH)
# ==============================
with open("soko.jpg", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <style>
    .app-header {{
        display: flex;
        justify-content: center;
        margin: 12px 0;
    }}
    .app-header img {{
        width: 180px;
    }}
    </style>

    <div class="app-header">
        <img src="data:image/jpg;base64,{logo_base64}">
    </div>
    """,
    unsafe_allow_html=True
)

# ======================
# TITLE
# ======================
st.title("📊 LinkedIn Performance Dashboard")

# ======================
# LOAD DATA
# ======================
try:
    df = pd.read_csv("dataset_linkedin-post-search-scraper.csv")
except FileNotFoundError:
    st.error("❌ File dataset LinkedIn tidak ditemukan.")
    st.stop()

# ======================
# DETEKSI KOLOM REAKSI
# ======================
reaction_col = None
for col in df.columns:
    if "reaction" in col.lower() or "like" in col.lower():
        reaction_col = col
        break

if reaction_col is None:
    df["reaction_count"] = 0
    reaction_col = "reaction_count"

# ======================
# PARSE WAKTU RELATIF
# ======================
def parse_relative_time(x):
    now = datetime.now()
    try:
        x = str(x).lower().strip()
        if "d" in x:
            return now - timedelta(days=int(x.replace("d", "")))
        elif "w" in x:
            return now - timedelta(weeks=int(x.replace("w", "")))
        elif "mo" in x or "m" in x:
            return now - timedelta(days=30 * int(x.replace("mo", "").replace("m", "")))
    except:
        return None
    return None

if "timeSincePosted" in df.columns:
    df["posted_at"] = df["timeSincePosted"].apply(parse_relative_time)
else:
    df["posted_at"] = None

df_clean = df.copy()
df_clean[reaction_col] = pd.to_numeric(
    df_clean[reaction_col], errors="coerce"
).fillna(0)

# ======================
# METRICS
# ======================
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total Post", len(df_clean))
with m2:
    st.metric("Total Reaksi", int(df_clean[reaction_col].sum()))
with m3:
    st.metric("Rata-rata Reaksi", int(df_clean[reaction_col].mean()))

st.divider()

# ======================
# NAVIGASI TOMBOL
# ======================
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "data_awal"

b1, b2, b3, b4 = st.columns(4)
#with b1:
 #   if st.button("📄 Data Awal"):
  #      st.session_state.active_tab = "data_awal"
with b2:
    if st.button("📊 Distribusi Reaksi"):
        st.session_state.active_tab = "distribusi"
with b3:
    if st.button("🏢 Top 10 Perusahaan"):
        st.session_state.active_tab = "top10"
with b4:
    if st.button("📈 Tren Harian"):
        st.session_state.active_tab = "tren"

st.divider()

# ======================
# TAB: DATA AWAL
# ======================
#if st.session_state.active_tab == "data_awal":
 #   st.subheader("📄 Data Awal LinkedIn")
  #  st.dataframe(
   #     df_clean.head(50),
    #    width="stretch",
     #   height=550
    #)

# ======================
# TAB: DISTRIBUSI
# ======================
if st.session_state.active_tab == "distribusi":
    st.subheader("📊 Distribusi Jumlah Reaksi")
   
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.hist(df_clean[reaction_col], bins=20, edgecolor="white")
    ax.set_xlabel("Jumlah Reaksi")
    ax.set_ylabel("Jumlah Postingan")
    ax.grid(alpha=0.3)

    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    ax.tick_params(colors=font_color)
    ax.xaxis.label.set_color(font_color)
    ax.yaxis.label.set_color(font_color)

    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        st.pyplot(fig)

# ======================
# TAB: TOP 10 COMPANY
# ======================
elif st.session_state.active_tab == "top10":
    st.subheader("🏢 Top 10 Perusahaan dengan Total Reaksi")

    if "activityOfCompany/name" in df_clean.columns:
        top_company = (
            df_clean
            .groupby("activityOfCompany/name")[reaction_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        fig, ax = plt.subplots(figsize=(8, 4))
        top_company.plot(kind="bar", ax=ax)
        ax.set_ylabel("Total Reaksi")
        ax.grid(axis="y", alpha=0.3)

        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")
        ax.tick_params(colors=font_color)
        ax.yaxis.label.set_color(font_color)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.pyplot(fig)
    else:
        st.warning("Kolom perusahaan tidak tersedia.")

# ======================
# TAB: TREN HARIAN
# ======================
elif st.session_state.active_tab == "tren":
    st.subheader("📈 Tren Reaksi Harian")

    if df_clean["posted_at"].isna().all():
        st.warning("Data waktu tidak valid.")
    else:
        daily = (
            df_clean
            .groupby(df_clean["posted_at"].dt.date)[reaction_col]
            .sum()
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(daily["posted_at"], daily[reaction_col], marker="o")
        ax.set_xlabel("Tanggal")
        ax.set_ylabel("Jumlah Reaksi")
        ax.grid(alpha=0.3)

        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")
        ax.tick_params(colors=font_color)
        ax.xaxis.label.set_color(font_color)
        ax.yaxis.label.set_color(font_color)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.pyplot(fig)
