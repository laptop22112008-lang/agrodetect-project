import streamlit as st
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AgroDetect AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(180deg, #071018 0%, #0c1722 100%);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

h1, h2, h3, h4, h5 {
    font-family: 'Sora', sans-serif;
    color: #eef6ff;
}

p, li, label, .stMarkdown, .stText, .stCaption {
    color: #d5e3f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08111a 0%, #0c1622 100%);
    border-right: 1px solid #183248;
}
section[data-testid="stSidebar"] * {
    color: #eef6ff;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.55rem 1.2rem !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 18px rgba(14,165,233,0.16);
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(20,184,166,0.28);
}

/* Inputs */
.stTextInput > div > div > input {
    background: #0b1723 !important;
    color: #edf7ee !important;
    border: 1px solid #23405c !important;
    border-radius: 12px !important;
    padding: 0.7rem 0.9rem !important;
}
.stFileUploader {
    background: #0b1723;
    border: 1.5px dashed #23405c;
    border-radius: 14px;
    padding: 0.8rem;
}

/* Cards */
.hero-card, .main-card, .stat-card, .analysis-card, .history-card, .about-card, .tip-card {
    background: linear-gradient(180deg, rgba(10,22,34,0.95), rgba(8,17,26,0.98));
    border: 1px solid #1f3950;
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
    border-left: 5px solid #14b8a6;
}

/* Badges */
.good-badge {
    display: inline-block;
    padding: 0.45rem 0.95rem;
    border-radius: 999px;
    background: rgba(20, 184, 166, 0.15);
    border: 1px solid #14b8a6;
    color: #99f6e4;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    letter-spacing: 0.3px;
}

.bad-badge {
    display: inline-block;
    padding: 0.45rem 0.95rem;
    border-radius: 999px;
    background: rgba(248, 113, 113, 0.12);
    border: 1px solid #fb7185;
    color: #fecdd3;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    letter-spacing: 0.3px;
}

.soft-label {
    color: #8fb1cc;
    font-size: 0.88rem;
}

.soft-value {
    color: #f1f7ff;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
}

.small-note {
    color: #87a5bf;
    font-size: 0.82rem;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #21415b, transparent);
    margin: 1rem 0;
}

/* Better uploader text */
div[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: #cfe8ff !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "last_image" not in st.session_state:
    st.session_state.last_image = None

if "result_data" not in st.session_state:
    st.session_state.result_data = None

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ─────────────────────────────────────────
#  TREATMENT DATABASE
# ─────────────────────────────────────────
TREATMENTS = {
    "Healthy Leaf": {
        "card_class": "",
        "icon": "✅",
        "title": "Plant is healthy — maintain current care",
        "tips": [
            "Continue the regular watering schedule",
            "Apply balanced NPK fertiliser monthly",
            "Monitor for early signs of pests or discoloration",
            "Ensure adequate sunlight and airflow between plants",
        ]
    },
    "Mostly Healthy (Minor Yellowing)": {
        "card_class": "",
        "icon": "🟦",
        "title": "Mostly healthy — minor stress detected",
        "tips": [
            "Inspect the plant again in 3–5 days",
            "Check if the leaf is getting too much direct sun",
            "Avoid overwatering and keep soil moisture stable",
            "Remove only clearly damaged parts if needed",
        ]
    },
    "Disease Detected": {
        "card_class": "danger",
        "icon": "🦠",
        "title": "Disease treatment recommended",
        "tips": [
            "Remove and dispose of heavily infected leaves immediately",
            "Apply a copper-based or neem oil fungicide/bactericide spray",
            "Avoid overhead watering — water at the base only",
            "Increase plant spacing to improve air circulation",
            "Re-inspect after 7 days and repeat treatment if needed",
        ]
    },
    "Nutrient Deficiency": {
        "card_class": "warn",
        "icon": "🌱",
        "title": "Nutrient correction needed",
        "tips": [
            "Test soil pH — ideal range is 6.0–7.0 for most crops",
            "Apply a micronutrient-rich foliar spray (Fe, Mg, Zn)",
            "Add organic compost to improve soil structure and retention",
            "Consider a slow-release fertiliser with balanced N-P-K",
            "Avoid over-watering which leaches nutrients from the soil",
        ]
    },
    "Stress / Early Issue": {
        "card_class": "warn",
        "icon": "⚠️",
        "title": "Mixed stress detected — monitor carefully",
        "tips": [
            "Check watering consistency first",
            "Inspect for pests, fungal spots, and leaf curling",
            "Reduce heat stress with partial shade if needed",
            "Re-scan the leaf under natural light for confirmation",
            "If symptoms spread, isolate the plant from others",
        ]
    }
}

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def safe_pie_values(values):
    arr = np.array(values, dtype=float)
    if np.sum(arr) <= 0:
        return [34.0, 33.0, 33.0]
    arr = np.maximum(arr, 0.5)
    arr = arr / np.sum(arr) * 100.0
    return arr.tolist()


def get_severity(result: str, confidence: float, condition: str):
    if result == "GOOD":
        if confidence >= 86:
            return "🟢 Low Risk", "sev-low"
        return "🟦 Monitor", "sev-medium"

    if condition == "Disease Detected" or confidence >= 82:
        return "🔴 High Risk", "sev-high"
    if confidence >= 68:
        return "🟠 Medium Risk", "sev-medium"
    return "🟡 Low Risk", "sev-low"


# --- keep the brain as-is, just made it stable for the UI ---
def analyze_leaf(image: Image.Image):
    img = np.array(image.convert("RGB"))

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

    if green_ratio > 0.55 and brown_ratio < 0.07 and yellow_ratio < 0.20:
        result = "GOOD"
        condition = "Healthy Leaf"
        confidence = round(75 + green_ratio * 20, 2)

    elif brown_ratio > 0.12:
        result = "BAD"
        condition = "Disease Detected"
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


def treatment_for_condition(condition: str):
    return TREATMENTS.get(condition, TREATMENTS["Stress / Early Issue"])


def make_pie_figure(values, colors, labels):
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.axis('equal')
    return fig


def figure_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def build_report_story(item, styles):
    story = []
    story.append(Paragraph(f"<b>{item['name']}</b>", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Result: {item['result']}", styles["Normal"]))
    story.append(Paragraph(f"Confidence: {item['confidence']}%", styles["Normal"]))
    story.append(Paragraph(f"Condition: {item['condition']}", styles["Normal"]))
    story.append(Spacer(1, 10))

    img_buf = io.BytesIO(item["image"])
    img_buf.seek(0)
    story.append(RLImage(img_buf, width=200, height=200))

    story.append(Spacer(1, 10))

    pie_fig = make_pie_figure(
        [item["green"], item["yellow"], item["brown"]],
        ["#22c55e", "#f59e0b", "#ef4444"],
        ["Green", "Yellow", "Brown"]
    )
    pie_buf = figure_to_bytes(pie_fig)
    story.append(RLImage(pie_buf, width=200, height=200))

    return story


def build_pdf_bytes(item):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    doc.build(build_report_story(item, styles))
    buffer.seek(0)
    return buffer.getvalue()


def build_all_pdf_bytes(history):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    for idx, item in enumerate(history):
        story.extend(build_report_story(item, styles))
        if idx < len(history) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def metric_card(label, value, accent=""):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="soft-label">{label}</div>
            <div class="soft-value" style="color:{accent if accent else '#f1f7ff'}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <div style="font-family:Sora, sans-serif; font-size:2.1rem; font-weight:700; color:#eef6ff;">
        🌿 AgroDetect AI
    </div>
    <div style="font-size:1rem; color:#76d1ff; margin-top:0.35rem;">
        Smart leaf analysis with professional reporting and clean history tracking
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────
st.sidebar.markdown("### 🌿 AgroDetect AI")
st.sidebar.caption("Side navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"
if st.sidebar.button("📁 History"):
    st.session_state.page = "History"
if st.sidebar.button("📊 Analytics"):
    st.session_state.page = "Analytics"
if st.sidebar.button("ℹ️ About"):
    st.session_state.page = "About"

st.sidebar.markdown("---")
st.sidebar.caption("Clean UI refresh · same analysis brain")

# ══════════════════════════════════════════
#  TAB 1 – HOME
# ══════════════════════════════════════════
if st.session_state.page == "Home":
    st.markdown("#### 🔎 Scan a leaf to detect plant health")

    source = st.radio(
        "Input source",
        ["📁 Upload Image", "📷 Use Camera"],
        horizontal=True,
        label_visibility="collapsed"
    )

    image = None
    if source == "📁 Upload Image":
        f = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if f:
            image = Image.open(f)
    else:
        cam = st.camera_input("Point your camera at the leaf and press capture")
        if cam:
            image = Image.open(cam)

    if image:
        result, confidence, condition, green, yellow, brown = analyze_leaf(image)
        severity_label, severity_class = get_severity(result, confidence, condition)
        t = treatment_for_condition(condition)
        pie_values = safe_pie_values([green, yellow, brown])

        col_img, col_result = st.columns([1, 1], gap="large")

        with col_img:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.image(image, use_container_width=True, caption="Scanned Leaf")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_result:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("##### 🔬 Analysis Result")

            badge_class = "good-badge" if result == "GOOD" else "bad-badge"
            icon = "✅" if result == "GOOD" else "⚠️"
            st.markdown(
                f"<span class='{badge_class}'>{icon} {result}</span>"
                f"&nbsp;&nbsp;<span class='{severity_class}'>{severity_label}</span>",
                unsafe_allow_html=True
            )
            st.write("")
            st.markdown(f"**Condition:** {condition}")
            st.progress(min(int(confidence), 100))
            st.caption(f"Confidence: **{confidence}%**")

            st.write("")
            c1, c2, c3 = st.columns(3)
            c1.markdown(
                f"<div class='stat-card'><div class='soft-label'>Healthy</div><div class='soft-value' style='color:#99f6e4'>{pie_values[0]:.0f}%</div></div>",
                unsafe_allow_html=True
            )
            c2.markdown(
                f"<div class='stat-card'><div class='soft-label'>Warning</div><div class='soft-value' style='color:#fde68a'>{pie_values[1]:.0f}%</div></div>",
                unsafe_allow_html=True
            )
            c3.markdown(
                f"<div class='stat-card'><div class='soft-label'>Damage</div><div class='soft-value' style='color:#fecaca'>{pie_values[2]:.0f}%</div></div>",
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")

        tips_html = "".join(f"<li style='margin-bottom:6px'>{tip}</li>" for tip in t["tips"])
        card_class = f"tip-card {t['card_class']}".strip()
        st.markdown(
            f"""
            <div class='{card_class}'>
                <b style='font-family:Sora,sans-serif;color:#eef6ff;font-size:1rem'>
                    {t["icon"]} {t["title"]}
                </b>
                <ul style='color:#d5e3f0;margin-top:10px;padding-left:18px'>
                    {tips_html}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("---")

        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Leaf Colour Composition")

        fig = make_pie_figure(
            pie_values,
            ["#14b8a6", "#f59e0b", "#fb7185"],
            ["Green", "Yellow", "Brown"]
        )
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        leaf_name = st.text_input("Leaf scan name", placeholder="e.g. Field-A Sample 1", key=f"leaf_name_{st.session_state.input_key}")

        if st.button("💾 Save to History"):
            if leaf_name.strip() == "":
                st.warning("Please enter a name before saving.")
            else:
                st.session_state.history.append({
                    "name": leaf_name.strip(),
                    "result": result,
                    "confidence": confidence,
                    "condition": condition,
                    "severity": severity_label,
                    "green": pie_values[0],
                    "yellow": pie_values[1],
                    "brown": pie_values[2],
                    "image": image_to_bytes(image),
                    "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p")
                })
                st.session_state.input_key += 1
                st.success(f"✅ '{leaf_name}' saved to history!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⬆️ Upload an image or use your camera above to scan a leaf.")

# ══════════════════════════════════════════
#  TAB 2 – ANALYTICS
# ══════════════════════════════════════════
elif st.session_state.page == "Analytics":
    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.0rem; font-weight:700; color:#eef6ff;">
            📊 Analytics
        </div>
        <div style="font-size:1rem; color:#76d1ff; margin-top:0.25rem;">
            Overall scan trends and health summary
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        good_count = sum(1 for i in st.session_state.history if i["result"] == "GOOD")
        bad_count = sum(1 for i in st.session_state.history if i["result"] == "BAD")
        high_risk = sum(1 for i in st.session_state.history if "High" in i.get("severity", ""))
        total = len(st.session_state.history)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("Total Scans", total, "#cfe8ff")
        with m2:
            metric_card("Healthy", good_count, "#99f6e4")
        with m3:
            metric_card("Diseased / Deficient", bad_count, "#fecaca")
        with m4:
            metric_card("High Risk", high_risk, "#fda4af")

        st.write("")
        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.markdown("##### Health Distribution")
            fig2 = make_pie_figure(
                [good_count, bad_count],
                ["#14b8a6", "#fb7185"],
                ["GOOD", "BAD"]
            )
            st.pyplot(fig2)

        with col_bar:
            st.markdown("##### Confidence per Scan")
            names = [entry["name"][:12] if entry["name"] else f"Scan {i+1}" for i, entry in enumerate(st.session_state.history)]
            confidences = [entry["confidence"] for entry in st.session_state.history]
            bar_colors = ["#14b8a6" if entry["result"] == "GOOD" else "#fb7185" for entry in st.session_state.history]

            fig3, ax3 = plt.subplots(figsize=(5, 4))
            ax3.set_facecolor("#0c1722")
            ax3.bar(range(len(names)), confidences, color=bar_colors, edgecolor="#0c1722")
            ax3.set_xticks(range(len(names)))
            ax3.set_xticklabels(names, rotation=30, ha="right", color="#d5e3f0", fontsize=9)
            ax3.set_ylabel("Confidence (%)", color="#d5e3f0", fontsize=9)
            ax3.set_ylim(0, 100)
            ax3.tick_params(colors="#d5e3f0")
            for spine in ax3.spines.values():
                spine.set_edgecolor("#23405c")
            ax3.legend(
                handles=[
                    mpatches.Patch(color="#14b8a6", label="GOOD"),
                    mpatches.Patch(color="#fb7185", label="BAD")
                ],
                facecolor="#0c1722",
                labelcolor="white",
                edgecolor="#23405c"
            )
            st.pyplot(fig3)

        st.write("")
        st.markdown("##### 🌡️ Severity Breakdown")

        sev_counts = {
            "Low Risk": sum(1 for i in st.session_state.history if "Low" in i.get("severity", "")),
            "Medium Risk": sum(1 for i in st.session_state.history if "Medium" in i.get("severity", "")),
            "High Risk": sum(1 for i in st.session_state.history if "High" in i.get("severity", "")),
        }

        fig4, ax4 = plt.subplots(figsize=(5, 2.5))
        ax4.set_facecolor("#0c1722")
        bars = ax4.barh(
            list(sev_counts.keys()),
            list(sev_counts.values()),
            color=["#14b8a6", "#f59e0b", "#fb7185"],
            edgecolor="#0c1722",
            height=0.5
        )
        ax4.set_xlabel("Count", color="#d5e3f0", fontsize=9)
        ax4.tick_params(colors="#d5e3f0")
        for spine in ax4.spines.values():
            spine.set_edgecolor("#23405c")
        for bar, val in zip(bars, sev_counts.values()):
            ax4.text(
                bar.get_width() + 0.05,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center",
                color="white",
                fontsize=10
            )
        st.pyplot(fig4)
    else:
        st.info("No scan data yet. Upload and save leaf images from the Dashboard tab.")

# ══════════════════════════════════════════
#  TAB 3 – HISTORY
# ══════════════════════════════════════════
elif st.session_state.page == "History":
    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.0rem; font-weight:700; color:#eef6ff;">
            📁 History
        </div>
        <div style="font-size:1rem; color:#76d1ff; margin-top:0.25rem;">
            Saved analyses with downloadable reports
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("No history yet. Save scans from the Dashboard tab.")
    else:
        if st.button("🗑️ Clear All History"):
            st.session_state.history = []
            st.rerun()

        for idx, item in enumerate(reversed(st.session_state.history), 1):
            badge = "good-badge" if item["result"] == "GOOD" else "bad-badge"
            icon = "✅" if item["result"] == "GOOD" else "⚠️"
            sev = item.get("severity", "")
            ts = item.get("timestamp", "—")
            sev_class = "sev-low" if "Low" in sev else ("sev-medium" if "Medium" in sev else "sev-high")
            t_data = treatment_for_condition(item.get("condition", "Stress / Early Issue"))
            tips_html = "".join(
                f"<li style='margin-bottom:4px;color:#d5e3f0;font-size:0.82rem'>{tip}</li>"
                for tip in t_data["tips"]
            )
            card_class = f"tip-card {t_data['card_class']}".strip()

            st.markdown(f"""
            <div class='history-card'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px'>
                    <b style='font-size:1rem;font-family:Sora,sans-serif;color:#eef6ff'>
                        #{idx} — {item['name']}
                    </b>
                    <span class='small-note'>🕐 {ts}</span>
                </div>
                <br>
                <span class='{badge}'>{icon} {item['result']}</span>
                &nbsp;<span class='{sev_class}'>{sev}</span>
                &nbsp;&nbsp;
                <span style='color:#cfe8ff'>Condition: {item['condition']}</span><br>
                <span style='color:#76d1ff;font-size:0.85rem'>Confidence: {item['confidence']}%</span>
                <br><br>
                <details>
                    <summary style='color:#76d1ff;cursor:pointer;font-size:0.85rem;
                                    font-family:Sora,sans-serif;font-weight:600'>
                        💡 View Treatment Tips
                    </summary>
                    <div class='{card_class}' style='margin-top:10px'>
                        <b style='font-family:Sora,sans-serif;color:#eef6ff;font-size:0.95rem'>
                            {t_data["icon"]} {t_data["title"]}
                        </b>
                        <ul style='padding-left:16px;margin-top:8px'>
                            {tips_html}
                        </ul>
                    </div>
                </details>
            </div>
            """, unsafe_allow_html=True)

            pdf_bytes = build_pdf_bytes(item)
            st.download_button(
                "Download Report",
                pdf_bytes,
                file_name=f"{item['name']}.pdf",
                key=f"download_{idx}"
            )

        st.markdown("---")

        all_pdf = build_all_pdf_bytes(st.session_state.history)
        st.download_button(
            "Download All Reports",
            all_pdf,
            file_name="All_Leaf_Reports.pdf"
        )

# ══════════════════════════════════════════
#  TAB 4 – ABOUT
# ══════════════════════════════════════════
elif st.session_state.page == "About":
    st.markdown("""
    <div class="hero-card">
        <div style="font-family:Sora, sans-serif; font-size:2.0rem; font-weight:700; color:#eef6ff;">
            ℹ️ About AgroDetect AI
        </div>
        <div style="font-size:1rem; color:#76d1ff; margin-top:0.25rem;">
            Smart plant leaf analysis system
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("""
        <div class="about-card">
            <h4 style="margin-top:0;color:#76d1ff">🌿 What It Does</h4>
            AgroDetect AI analyses leaf images using colour-ratio intelligence to detect plant health.
            It provides a clear health result, confidence score, pie chart analysis, and downloadable reports.
        </div>
        <div class="about-card">
            <h4 style="margin-top:0;color:#76d1ff">🚀 Features</h4>
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
            <h4 style="margin-top:0;color:#76d1ff">🔬 How It Works</h4>
            The model checks colour ratios from the uploaded leaf image and uses them to determine
            whether the leaf is healthy, diseased, or stressed.
        </div>
        <div class="about-card">
            <h4 style="margin-top:0;color:#76d1ff">🔮 Future Scope</h4>
            • Deep learning based disease detection<br>
            • Weather and soil integration<br>
            • Mobile app support<br>
            • Crop-specific disease classification
        </div>
        """, unsafe_allow_html=True)


def image_to_bytes(img: Image.Image):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()
