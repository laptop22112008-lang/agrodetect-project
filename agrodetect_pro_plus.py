import streamlit as st
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
import io

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------- STABLE CSS ----------
st.markdown("""
    <style>
    /* Reset & Background */
    [data-testid="stAppViewContainer"] {
        background-color: #F0F2F6;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
    }

    /* Modern Card Container */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-left: 5px solid #4ADE80;
    }

    /* Result Box Logic */
    .result-box {
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        background: #F8FAFC;
    }
    
    .status-text {
        font-size: 24px;
        font-weight: 800;
        margin: 0;
    }
    
    /* Remove default Streamlit padding for a tighter look */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<h2 style='color:#4ADE80'>🌿 agri-cultur</h2>", unsafe_allow_html=True)
    st.write("---")
    if st.button("📊 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
    if st.button("📁 History", use_container_width=True): st.session_state.page = "History"
    st.write("---")
    st.caption("v2.1 Stable Build")

# ---------- ANALYSIS LOGIC ----------
def analyze_leaf(image):
    img = np.array(image)
    r, g, b = img[:,:,0].astype(float), img[:,:,1].astype(float), img[:,:,2].astype(float)
    total = r + g + b + 1e-6
    g_ratio = np.sum((g/total > 0.36))/ (img.shape[0]*img.shape[1])
    # Simplified for UI testing
    res = "GOOD" if g_ratio > 0.4 else "BAD"
    return res, round(g_ratio*100, 1), "Healthy" if res=="GOOD" else "Check Stress", 70, 20, 10

# ---------- DASHBOARD ----------
if st.session_state.page == "Dashboard":
    st.title("Field Intelligence")
    
    # Grid Layout
    top_col1, top_col2 = st.columns([1, 1.5])
    
    with top_col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("📸 Leaf Scan")
        uploaded_file = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with top_col2:
        if uploaded_file:
            image = Image.open(uploaded_file)
            res, conf, cond, g, y, b = analyze_leaf(image)
            
            # Key Stats Row
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="result-box"><caption>STATUS</caption><p class="status-text" style="color:{"#10B981" if res=="GOOD" else "#EF4444"}">{res}</p></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="result-box"><caption>CONFIDENCE</caption><p class="status-text">{conf}%</p></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="result-box"><caption>CONDITION</caption><p style="font-weight:bold; margin-top:10px;">{cond}</p></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Chart Card
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.subheader("Color Analysis")
            fig, ax = plt.subplots(figsize=(8, 1.5))
            ax.barh(["Composition"], [g], color="#4ADE80", label="Green")
            ax.barh(["Composition"], [y], left=[g], color="#FACC15", label="Yellow")
            ax.barh(["Composition"], [b], left=[g+y], color="#78350F", label="Brown")
            ax.set_xlim(0, 100)
            ax.axis('off')
            st.pyplot(fig)
            
            name = st.text_input("Log Batch ID", placeholder="e.g. Corn-01")
            if st.button("Save Record", use_container_width=True):
                st.toast("Saved!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Please upload an image to view analysis results.")
