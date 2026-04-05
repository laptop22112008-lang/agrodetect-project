import streamlit as st
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import io

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AgroDetect AI | Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------- CUSTOM CSS (THE MAGIC) ----------
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        color: white;
    }
    
    /* Custom Card Styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-content {
        animation: fadeIn 0.6s ease-out;
    }

    /* Titles */
    h1, h2, h3 {
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Success/Warning custom colors */
    .status-good { color: #10b981; font-weight: bold; }
    .status-bad { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- SIDEBAR NAVIGATION ----------
with st.sidebar:
    st.markdown("<h1 style='color: #4ade80; font-size: 24px;'>🌿 agri-cultur</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Modern Menu using buttons
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"
    if st.button("📁 History", use_container_width=True):
        st.session_state.page = "History"
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.page = "Analytics"
    if st.button("ℹ️ About", use_container_width=True):
        st.session_state.page = "About"
    
    st.sidebar.markdown("---")
    st.sidebar.caption("System Status: Online")

# ---------- ANALYSIS LOGIC (UNTOUCHED) ----------
def analyze_leaf(image):
    img = np.array(image)
    r, g, b = img[:,:,0].astype(float), img[:,:,1].astype(float), img[:,:,2].astype(float)
    total = r + g + b + 1e-6
    r_norm, g_norm, b_norm = r/total, g/total, b/total
    
    green_mask = (g_norm > 0.36) & (g_norm > r_norm) & (g_norm > b_norm)
    yellow_mask = (r_norm > 0.34) & (g_norm > 0.34) & (b_norm < 0.32)
    brown_mask = (r_norm > 0.45) & (g_norm < 0.38) & (b_norm < 0.32)
    
    total_pixels = img.shape[0] * img.shape[1]
    green_ratio, yellow_ratio, brown_ratio = np.sum(green_mask)/total_pixels, np.sum(yellow_mask)/total_pixels, np.sum(brown_mask)/total_pixels
    
    g_p, y_p, b_p = int(green_ratio*100), int(yellow_ratio*100), int(brown_ratio*100)
    
    if green_ratio > 0.55 and brown_ratio < 0.07:
        return "GOOD", round(75 + green_ratio*20, 2), "Healthy Leaf", g_p, y_p, b_p
    elif brown_ratio > 0.12:
        return "BAD", round(65 + brown_ratio*30, 2), "Disease (Brown Damage)", g_p, y_p, b_p
    else:
        return "BAD", 60.0, "Stress Detected", g_p, y_p, b_p

# ---------- DASHBOARD PAGE ----------
if st.session_state.page == "Dashboard":
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Plant Health Dashboard")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📤 Upload Field Data")
        uploaded_file = st.file_uploader("Drop leaf image here", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if uploaded_file:
            image = Image.open(uploaded_file)
            with st.spinner("AI analyzing pixels..."):
                time.sleep(0.8)
                res, conf, cond, g, y, b = analyze_leaf(image)
            
            # Summary Row
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>Status</h4><h2 class="{"status-good" if res=="GOOD" else "status-bad"}">{res}</h2></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><h4>Confidence</h4><h2>{conf}%</h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4>Issue</h4><p>{cond}</p></div>', unsafe_allow_html=True)
            
            # Chart Row
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("Color Distribution")
            fig, ax = plt.subplots(figsize=(10, 3))
            ax.barh(["Health Markers"], [g], color="#4ade80", label="Green")
            ax.barh(["Health Markers"], [y], left=[g], color="#facc15", label="Yellow")
            ax.barh(["Health Markers"], [b], left=[g+y], color="#78350f", label="Brown")
            ax.set_xlim(0, 100)
            ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), ncol=3)
            st.pyplot(fig)
            
            name = st.text_input("Assign to Field/Batch (e.g. Corn-Section-A)")
            if st.button("💾 Log Data to History"):
                st.session_state.history.append({"name": name, "result": res, "confidence": conf, "condition": cond, "image": uploaded_file.getvalue(), "green": g, "yellow": y, "brown": b})
                st.toast("Record saved successfully!", icon="✅")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Waiting for image upload to generate predictive analysis...")

# ---------- OTHER PAGES (MINIMAL WRAPPERS) ----------
elif st.session_state.page == "History":
    st.title("📁 Field Logs")
    if not st.session_state.history:
        st.info("No logs found. Start by scanning a leaf in the dashboard.")
    else:
        for item in st.session_state.history:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                cols = st.columns([1, 4])
                cols[0].image(item["image"], width=100)
                cols[1].markdown(f"**Batch:** {item['name']} | **Result:** {item['result']} | **Confidence:** {item['confidence']}%")
                st.markdown('</div>', unsafe_allow_html=True)

# Footer/Closing tags
st.markdown('</div>', unsafe_allow_html=True)
