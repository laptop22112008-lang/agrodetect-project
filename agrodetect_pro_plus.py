import streamlit as st
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- CUSTOM UI ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(180deg, #0b120c 0%, #0f1a10 100%);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}

h1, h2, h3, h4, h5 {
    font-family: 'Sora', sans-serif;
    color: #e8f5e9;
}

p, li, label, .stMarkdown, .stText, .stCaption {
    color: #dbe8dc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102112 0%, #0c150d 100%);
    border-right: 1px solid #1f3622;
}
section[data-testid="stSidebar"] * {
    color: #e8f5e9;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.55rem 1.2rem !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 18px rgba(76,175,80,0.16);
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(76,175,80,0.28);
}

/* Inputs */
.stTextInput > div > div > input {
    background: #132215 !important;
    color: #edf7ee !important;
    border: 1px solid #2b4a2e !important;
    border-radius: 12px !important;
    padding: 0.7rem 0.9rem !important;
}
.stFileUploader {
    background: #132215;
    border: 1px dashed #315535;
    border-radius: 14px;
    padding: 0.8rem;
}

/* Result cards */
.hero-card, .main-card, .stat-card, .analysis-card, .history-card, .about-card, .tip-card {
    background: linear-gradient(180deg, rgba(27,44,28,0.95), rgba(17,27,18,0.98));
    border: 1px solid #26402a;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22);
}

.hero-card {
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}

.main-card {
    padding: 1.2rem 1.3rem;
    margin-bottom: 1rem;
}

.stat-card {
    padding: 1rem;
    text-align: center;
}

.analysis-card {
    padding: 1rem 1.1rem;
    margin-top: 0.85rem;
}

.history-card {
    padding: 1rem 1.1rem;
    margin-bottom: 0.9rem;
}

.about-card {
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}

.tip-card {
    padding: 1rem 1.2rem;
    border-left: 5px solid #43a047;
}

/* Badges */
.good-badge {
    display: inline-block;
    padding: 0.45rem 0.95rem;
    border-radius: 999px;
    background: rgba(67, 160, 71, 0.15);
    border: 1px solid #43a047;
    color: #a5d6a7;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    letter-spacing: 0.3px;
}

.bad-badge {
    display: inline-block;
    padding: 0.45rem 0.95rem;
    border-radius: 999px;
    background: rgba(229, 57, 53, 0.12);
    border: 1px solid #e53935;
    color: #ef9a9a;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    letter-spacing: 0.3px;
}

.soft-label {
    color: #89b88b;
    font-size: 0.88rem;
}

.soft-value {
    color: #edf7ee;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
}

.small-note {
    color: #7fa081;
    font-size: 0.82rem;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a4b2d, transparent);
    margin: 1rem 0;
}

/* Make download buttons and report buttons a bit cleaner */
button[kind="secondary"] {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- NAVIGATION ----------
st.sidebar.title("🌿 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"

if st.sidebar.button("📁 History"):
    st.session_state.page = "History"

if st.sidebar.button("📊 Analytics"):
    st.session_state.page = "Analytics"

if st.sidebar.button("ℹ️ About"):
    st.session_state.page = "About"

# ---------- MODEL ----------
def analyze_leaf(image):
    img = np.array(image)

    r = img[:, :, 0].astype(float)
    g = img[:, :, 1].astype(float)
    b = img[:, :, 2].astype(float)

    total = r + g + b + 1e-6

    r_norm = r / total
    g_norm = g / total
    b_norm = b / total

    green_mask = (g_norm > 0.36) & (g_norm > r_norm) & (g_norm > b_norm)
    yellow_mask = (r_norm > 0.34) & (g_norm > 0.34) & (b_norm < 0.32)
    brown_mask = (r_norm > 0.45) & (g_norm < 0.38) & (b_norm < 0.32)

    total_pixels = img.shape[0] * img.shape[1]

    green_ratio = np.sum(green_mask) / total_pixels
    yellow_ratio = np.sum(yellow_mask) / total_pixels
    brown_ratio = np.sum(brown_mask) / total_pixels

    green = int(green_ratio * 100)
    yellow = int(yellow_ratio * 100)
    brown = int(brown_ratio * 100)

    total_color = green + yellow + brown

    if total_color == 0:
        green, yellow, brown = 34, 33, 33
    else:
        green = int((green / total_color) * 100)
        yellow = int((yellow / total_color) * 100)
        brown = 100 - green - yellow

    # BALANCED DECISION
    if green_ratio > 0.55 and brown_ratio < 0.07 and yellow_ratio < 0.20:
        result = "GOOD"
        condition = "Healthy Leaf"
        confidence = round(75 + green_ratio * 20, 2)

    elif brown_ratio > 0.12:
        result = "BAD"
        condition = "Disease (Brown Damage)"
        confidence = round(65 + brown_ratio * 30, 2)

    elif yellow_ratio > 0.25:
        result = "BAD"
        condition = "Nutrient Deficiency"
        confidence = round(60 + yellow_ratio * 25, 2)

    elif green_ratio > 0.45:
        result = "GOOD"
        condition = "Mostly Healthy (Minor Yellowing)"
        confidence = round(65 + green_ratio * 20, 2)

    else:
        result = "BAD"
        condition = "Stress / Early Issue"
        confidence = round(55 + (yellow_ratio + brown_ratio) * 30, 2)

    return result, confidence, condition, green, yellow, brown

# ---------- HOME ----------
if st.session_state.page == "Home":

    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.2rem; font-weight:700; color:#e8f5e9;">
            🌿 AgroDetect AI
        </div>
        <div style="font-size:1rem; color:#8ecf8f; margin-top:0.35rem;">
            Smart plant leaf analysis with clean reporting and history tracking
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)

        file_bytes = uploaded_file.getvalue()

        if "last_image" not in st.session_state or st.session_state.last_image != file_bytes:
            st.session_state.last_image = file_bytes

            with st.spinner("Analyzing..."):
                time.sleep(1)

            result, confidence, condition, g, y, b = analyze_leaf(image)

            st.session_state.result_data = {
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "green": g,
                "yellow": y,
                "brown": b
            }

        data = st.session_state.result_data

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown("#### 🔎 Analysis Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            if data["result"] == "GOOD":
                st.markdown(f'<div class="stat-card"><div class="soft-label">Result</div><div class="soft-value"><span class="good-badge">GOOD</span></div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="stat-card"><div class="soft-label">Result</div><div class="soft-value"><span class="bad-badge">BAD</span></div></div>', unsafe_allow_html=True)

        with col2:
            st.markdown(
                f'<div class="stat-card"><div class="soft-label">Confidence</div>'
                f'<div class="soft-value">{data["confidence"]}%</div></div>',
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f'<div class="stat-card"><div class="soft-label">Condition</div>'
                f'<div class="soft-value">{data["condition"]}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.subheader("📊 Leaf Analysis")

        values = [data["green"], data["yellow"], data["brown"]]
        if sum(values) == 0:
            values = [34, 33, 33]

        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        ax.pie(
            values,
            labels=["Green", "Yellow", "Brown"],
            autopct='%1.1f%%',
            colors=["green", "yellow", "brown"],
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1}
        )
        ax.axis('equal')
        st.pyplot(fig)
        plt.close(fig)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        leaf_name = st.text_input("Enter Leaf Name")
        if st.button("Save to History"):
            st.session_state.history.append({
                "name": leaf_name,
                "result": data["result"],
                "confidence": data["confidence"],
                "condition": data["condition"],
                "green": data["green"],
                "yellow": data["yellow"],
                "brown": data["brown"],
                "image": uploaded_file.getvalue()
            })
            st.success("Saved successfully!")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- HISTORY ----------
elif st.session_state.page == "History":

    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.0rem; font-weight:700; color:#e8f5e9;">
            📁 History
        </div>
        <div style="font-size:1rem; color:#8ecf8f; margin-top:0.25rem;">
            Saved analyses with downloadable reports
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("No data yet")
    else:
        for i, item in enumerate(st.session_state.history):

            st.markdown('<div class="history-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])

            with col1:
                st.image(item["image"], width=120)

            with col2:
                st.markdown(f"#### {item['name']}")
                st.write(f"**Result:** {item['result']}")
                st.write(f"**Confidence:** {item['confidence']}%")
                st.write(f"**Condition:** {item['condition']}")

                img_path = f"leaf_{i}.png"
                with open(img_path, "wb") as f:
                    f.write(item["image"])

                fig, ax = plt.subplots()
                ax.pie(
                    [item["green"], item["yellow"], item["brown"]],
                    labels=["Green", "Yellow", "Brown"],
                    autopct='%1.1f%%',
                    colors=["green", "yellow", "brown"]
                )
                ax.axis('equal')
                pie_path = f"pie_{i}.png"
                fig.savefig(pie_path, bbox_inches="tight")
                plt.close(fig)

                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()

                content = []
                content.append(Paragraph(f"<b>{item['name']}</b>", styles["Title"]))
                content.append(Spacer(1, 10))
                content.append(Paragraph(f"Result: {item['result']}", styles["Normal"]))
                content.append(Paragraph(f"Confidence: {item['confidence']}%", styles["Normal"]))
                content.append(Paragraph(f"Condition: {item['condition']}", styles["Normal"]))
                content.append(Spacer(1, 10))
                content.append(RLImage(img_path, width=200, height=200))
                content.append(Spacer(1, 10))
                content.append(RLImage(pie_path, width=200, height=200))

                doc.build(content)

                st.download_button(
                    "Download Report",
                    buffer.getvalue(),
                    file_name=f"{item['name']}.pdf",
                    key=f"download_{i}"
                )
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        merged = io.BytesIO()
        doc = SimpleDocTemplate(merged)
        styles = getSampleStyleSheet()
        final_content = []

        for i, item in enumerate(st.session_state.history):
            img_path = f"leaf_{i}.png"
            pie_path = f"pie_{i}.png"

            final_content.append(Paragraph(f"<b>{item['name']}</b>", styles["Title"]))
            final_content.append(Spacer(1, 10))
            final_content.append(Paragraph(f"Result: {item['result']}", styles["Normal"]))
            final_content.append(Paragraph(f"Confidence: {item['confidence']}%", styles["Normal"]))
            final_content.append(Paragraph(f"Condition: {item['condition']}", styles["Normal"]))
            final_content.append(Spacer(1, 10))
            final_content.append(RLImage(img_path, width=200, height=200))
            final_content.append(Spacer(1, 10))
            final_content.append(RLImage(pie_path, width=200, height=200))
            final_content.append(Spacer(1, 20))

        doc.build(final_content)

        st.download_button(
            "Download All Reports",
            merged.getvalue(),
            file_name="All_Leaf_Reports.pdf"
        )

# ---------- ANALYTICS ----------
elif st.session_state.page == "Analytics":

    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.0rem; font-weight:700; color:#e8f5e9;">
            📊 Analytics
        </div>
        <div style="font-size:1rem; color:#8ecf8f; margin-top:0.25rem;">
            Overall scan trends and health summary
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        good = sum(1 for i in st.session_state.history if i["result"] == "GOOD")
        bad = len(st.session_state.history) - good

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                f'<div class="stat-card"><div class="soft-label">Total Images</div><div class="soft-value">{len(st.session_state.history)}</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="stat-card" style="margin-top:0.8rem;"><div class="soft-label">Good</div><div class="soft-value" style="color:#a5d6a7">{good}</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="stat-card" style="margin-top:0.8rem;"><div class="soft-label">Bad</div><div class="soft-value" style="color:#ef9a9a">{bad}</div></div>',
                unsafe_allow_html=True
            )

        with col_b:
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie([good, bad], labels=["Good", "Bad"], autopct='%1.1f%%', colors=["green", "red"])
            ax.axis('equal')
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info("No data yet")

# ---------- ABOUT ----------
elif st.session_state.page == "About":

    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.0rem; font-weight:700; color:#e8f5e9;">
            ℹ️ About AgroDetect AI
        </div>
        <div style="font-size:1rem; color:#8ecf8f; margin-top:0.25rem;">
            Smart plant leaf analysis system
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("""
        <div class="about-card">
            <h4 style="margin-top:0;color:#a5d6a7">🌿 What It Does</h4>
            AgroDetect AI analyses leaf images using colour-based intelligence to detect plant health.
            It provides a clear health result, confidence score, pie chart analysis, and downloadable reports.
        </div>
        <div class="about-card">
            <h4 style="margin-top:0;color:#a5d6a7">🚀 Features</h4>
            • Leaf health detection<br>
            • Confidence-based prediction<br>
            • Visual pie chart analysis<br>
            • History tracking<br>
            • PDF report downloads
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="about-card">
            <h4 style="margin-top:0;color:#a5d6a7">🔬 How It Works</h4>
            The model checks colour ratios from the uploaded leaf image and uses them to determine
            whether the leaf is healthy, diseased, or stressed.
        </div>
        <div class="about-card">
            <h4 style="margin-top:0;color:#a5d6a7">🔮 Future Scope</h4>
            • Deep learning based disease detection<br>
            • Weather and soil integration<br>
            • Mobile app support<br>
            • Crop-specific disease classification
        </div>
        """, unsafe_allow_html=True)
