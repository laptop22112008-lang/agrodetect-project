# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import rgb_to_hsv
from datetime import datetime
import io
import hashlib

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AgroDetect AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding-top: 3rem; }

div[data-baseweb="tab-list"] {
    gap: 8px; background: transparent;
    border-bottom: none !important; flex-wrap: wrap;
}
div[data-baseweb="tab"] {
    background: #1e2d1f; border: 1.5px solid #2e4d30;
    border-radius: 10px !important; padding: 10px 22px !important;
    font-family: 'Sora', sans-serif; font-size: 0.88rem;
    font-weight: 600; color: #a5c9a7 !important;
    transition: all 0.2s ease; white-space: nowrap;
}
div[data-baseweb="tab"]:hover {
    background: #2a4a2c; border-color: #4caf50; color: #fff !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    border-color: #66bb6a !important; color: #fff !important;
    box-shadow: 0 4px 14px rgba(76,175,80,0.35);
}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none !important; }

.agro-card {
    background: #1a2b1c; border: 1px solid #2d4a2f;
    border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
}

.hero-wrap {
    width: 100%;
    text-align: center;
    margin-bottom: 1rem;
    padding: 1.2rem 0.5rem 0 0.5rem;
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(1.55rem, 4.5vw, 2.45rem);
    font-weight: 700;
    color: #e8f5e9;
    letter-spacing: -0.5px;
    margin: 0 auto;
    line-height: 1.08;
    word-break: break-word;
    overflow-wrap: anywhere;
    max-width: 100%;
}
.hero-sub {
    font-size: 1rem; color: #81c784;
    margin-top: 6px; margin-bottom: 0;
}

.badge-good {
    display: inline-block; background: #1b5e20; border: 1.5px solid #43a047;
    color: #a5d6a7; border-radius: 8px; padding: 6px 18px;
    font-weight: 700; font-family: 'Sora', sans-serif; font-size: 1.1rem;
}
.badge-bad {
    display: inline-block; background: #5e1b1b; border: 1.5px solid #e53935;
    color: #ef9a9a; border-radius: 8px; padding: 6px 18px;
    font-weight: 700; font-family: 'Sora', sans-serif; font-size: 1.1rem;
}

.sev-low {
    display: inline-block; background: #1b3a1f; border: 1.5px solid #43a047;
    color: #a5d6a7; border-radius: 20px; padding: 4px 16px;
    font-weight: 600; font-family: 'Sora', sans-serif; font-size: 0.85rem;
}
.sev-medium {
    display: inline-block; background: #3e2a00; border: 1.5px solid #ffa726;
    color: #ffcc80; border-radius: 20px; padding: 4px 16px;
    font-weight: 600; font-family: 'Sora', sans-serif; font-size: 0.85rem;
}
.sev-high {
    display: inline-block; background: #5e1b1b; border: 1.5px solid #ef5350;
    color: #ef9a9a; border-radius: 20px; padding: 4px 16px;
    font-weight: 600; font-family: 'Sora', sans-serif; font-size: 0.85rem;
}

.treatment-card {
    background: #0f2211; border: 1px solid #2d6a35;
    border-left: 4px solid #43a047;
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.6rem;
}
.treatment-card.warn {
    background: #1e1400; border: 1px solid #6d4c00;
    border-left: 4px solid #ffa726;
}
.treatment-card.danger {
    background: #1e0a0a; border: 1px solid #6d1212;
    border-left: 4px solid #ef5350;
}

.metric-box {
    background: #1a2b1c; border: 1px solid #2d4a2f;
    border-radius: 12px; padding: 1rem; text-align: center;
}
.metric-num { font-family: 'Sora', sans-serif; font-size: 2rem; font-weight: 700; color: #a5d6a7; }
.metric-label { font-size: 0.8rem; color: #81c784; margin-top: 2px; }

.ts-tag { font-size: 0.75rem; color: #558b57; font-style: italic; }

body { background-color: #0f1a10; color: #e0e0e0; }
h1, h2, h3 { font-family: 'Sora', sans-serif; color: #e8f5e9; }
.stButton>button {
    background: linear-gradient(135deg, #2e7d32, #43a047);
    color: white; border: none; border-radius: 8px;
    padding: 0.5rem 1.4rem; font-family: 'Sora', sans-serif;
    font-weight: 600; transition: 0.2s;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #388e3c, #66bb6a);
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(76,175,80,0.4);
}
.stTextInput>div>div>input {
    background: #1a2b1c; border: 1px solid #2d4a2f;
    color: #e0e0e0; border-radius: 8px;
}
.stFileUploader { background: #1a2b1c; border: 1.5px dashed #2d4a2f; border-radius: 12px; }
div[data-testid="stAlert"] { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "saved_hashes" not in st.session_state:
    st.session_state.saved_hashes = []

if "save_nonce" not in st.session_state:
    st.session_state.save_nonce = 0

# ─────────────────────────────────────────
# TREATMENT DATABASE
# ─────────────────────────────────────────
TREATMENTS = {
    "Healthy Leaf": {
        "card_class": "",
        "icon": "✅",
        "title": "Plant is healthy — maintain current care",
        "tips": [
            "Continue the regular watering schedule",
            "Apply balanced NPK fertiliser monthly",
            "Monitor for early signs of pests or discolouration",
            "Ensure adequate sunlight and airflow between plants",
        ],
    },
    "Mostly Healthy": {
        "card_class": "",
        "icon": "🟢",
        "title": "Mostly healthy — only minor stress detected",
        "tips": [
            "Inspect the plant again in 3–5 days",
            "Check if the leaf is getting too much direct sun",
            "Avoid overwatering and keep soil moisture stable",
            "Remove only clearly damaged parts if needed",
        ],
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
        ],
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
        ],
    },
    "Mixed Stress": {
        "card_class": "warn",
        "icon": "⚠️",
        "title": "Mixed stress detected — monitor carefully",
        "tips": [
            "Check watering consistency first",
            "Inspect for pests, fungal spots, and leaf curling",
            "Reduce heat stress with partial shade if needed",
            "Re-scan the leaf under natural light for confirmation",
            "If symptoms spread, isolate the plant from others",
        ],
    },
}

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def safe_pie_values(values):
    arr = np.array(values, dtype=float)
    total = float(arr.sum())

    if total <= 0:
        return [34.0, 33.0, 33.0]

    if np.max(arr) / total >= 0.995:
        out = [0.0, 0.0, 0.0]
        out[int(np.argmax(arr))] = 100.0
        return out

    arr = np.maximum(arr, 0.5)
    arr = arr / np.sum(arr) * 100.0
    return arr.tolist()


def get_severity(result: str, confidence: float, condition: str):
    if result == "GOOD":
        if confidence >= 86:
            return "🟢 Low Risk", "sev-low"
        return "🟡 Monitor", "sev-medium"

    if condition == "Disease Detected" or confidence >= 82:
        return "🔴 High Risk", "sev-high"
    if confidence >= 68:
        return "🟠 Medium Risk", "sev-medium"
    return "🟡 Low Risk", "sev-low"


def analyze_leaf(image: Image.Image):
    """
    Stable leaf analysis using HSV:
    - reduces background noise
    - separates green / yellow / brown tones
    - returns stable pie values
    """
    img = np.array(image.convert("RGB")).astype(np.float32)

    rgb_norm = img / 255.0
    hsv = rgb_to_hsv(rgb_norm)
    h = hsv[:, :, 0] * 360.0
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    candidate = (s > 0.12) & (v > 0.18) & ((h <= 120) | (h >= 335))

    if candidate.mean() < 0.03:
        candidate = (s > 0.08) & (v > 0.15) & ((h <= 130) | (h >= 330))

    if candidate.mean() < 0.02:
        candidate = np.ones_like(h, dtype=bool)

    green_mask = candidate & (h >= 60) & (h <= 160) & (s > 0.18)
    yellow_mask = candidate & (h >= 22) & (h < 60) & (s > 0.15)
    brown_mask = candidate & (
        (((h < 22) | (h >= 335)) & (v < 0.90)) |
        ((s < 0.32) & (v < 0.75))
    )

    green_count = int(green_mask.sum())
    yellow_count = int(yellow_mask.sum())
    brown_count = int(brown_mask.sum())
    candidate_count = int(candidate.sum())

    unclassified = max(candidate_count - green_count - yellow_count - brown_count, 0)

    green_score = green_count + 0.55 * unclassified
    yellow_score = yellow_count + 0.25 * unclassified
    brown_score = brown_count + 0.20 * unclassified

    scores = np.array([green_score, yellow_score, brown_score], dtype=float)
    pie_values = safe_pie_values(scores)

    total_score = float(scores.sum())
    if total_score <= 0:
        green_ratio = yellow_ratio = brown_ratio = 1 / 3
    else:
        green_ratio = float(scores[0] / total_score)
        yellow_ratio = float(scores[1] / total_score)
        brown_ratio = float(scores[2] / total_score)

    brightness = float(np.mean(v[candidate])) if candidate.any() else float(np.mean(v))

    if green_ratio >= 0.62 and brown_ratio < 0.08 and yellow_ratio < 0.18:
        result = "GOOD"
        condition = "Healthy Leaf"
        confidence = 72 + 18 * green_ratio + 10 * brightness + 18 * (green_ratio - max(yellow_ratio, brown_ratio))
    elif brown_ratio >= 0.22:
        result = "BAD"
        condition = "Disease Detected"
        confidence = 65 + 25 * brown_ratio + 10 * (brown_ratio - green_ratio) + 5 * (1 - brightness)
    elif yellow_ratio >= 0.22:
        result = "BAD"
        condition = "Nutrient Deficiency"
        confidence = 62 + 25 * yellow_ratio + 12 * (yellow_ratio - green_ratio) + 5 * (1 - brightness)
    elif green_ratio >= 0.48:
        result = "GOOD"
        condition = "Mostly Healthy"
        confidence = 68 + 20 * green_ratio + 8 * (green_ratio - max(yellow_ratio, brown_ratio)) + 6 * brightness
    else:
        result = "BAD"
        condition = "Mixed Stress"
        confidence = 58 + 20 * max(yellow_ratio, brown_ratio) + 8 * (max(yellow_ratio, brown_ratio) - green_ratio) + 4 * (1 - brightness)

    confidence = round(float(np.clip(confidence, 50.0, 99.9)), 2)
    return result, confidence, condition, pie_values


def treatment_for_condition(condition: str):
    return TREATMENTS.get(condition, TREATMENTS["Mixed Stress"])


def make_pie_figure(values, colors, labels):
    fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor="#0f1a10")
    ax.set_facecolor("#0f1a10")

    values = safe_pie_values(values)

    wedges, _, autotexts = ax.pie(
        values,
        autopct=lambda p: f"{p:.1f}%" if p >= 4 else "",
        colors=colors,
        startangle=90,
        wedgeprops={"edgecolor": "#0f1a10", "linewidth": 2},
        pctdistance=0.72,
        labels=None,
    )

    legend = ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
    )

    for text in legend.get_texts():
        text.set_color("#d5e3f0")

    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(10)

    ax.axis("equal")
    return fig


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">🌿 AgroDetect AI</div>
    <div class="hero-sub">Smart Plant Health Intelligence</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────
tab_dashboard, tab_analytics, tab_history, tab_about = st.tabs(
    ["🏠  Dashboard", "📊  Analytics", "📁  History", "ℹ️  About"]
)

# ══════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════
with tab_dashboard:
    st.markdown("#### 🔎 Scan a leaf to detect plant health")

    source = st.radio(
        "Input source",
        ["📁 Upload Image", "📷 Use Camera"],
        horizontal=True,
        label_visibility="collapsed"
    )

    image = None
    uploaded_bytes = None

    if source == "📁 Upload Image":
        f = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if f:
            uploaded_bytes = f.getvalue()
            image = Image.open(io.BytesIO(uploaded_bytes))
    else:
        cam = st.camera_input("Point your camera at the leaf and press capture")
        if cam:
            uploaded_bytes = cam.getvalue()
            image = Image.open(io.BytesIO(uploaded_bytes))

    if image and uploaded_bytes:
        file_hash = hashlib.sha256(uploaded_bytes).hexdigest()
        result, confidence, condition, pie_values = analyze_leaf(image)
        severity_label, severity_class = get_severity(result, confidence, condition)
        t = treatment_for_condition(condition)

        col_img, col_result = st.columns([1, 1], gap="large")

        with col_img:
            st.image(image, use_container_width=True, caption="Scanned Leaf")

        with col_result:
            st.markdown("##### 🔬 Analysis Result")

            badge_class = "badge-good" if result == "GOOD" else "badge-bad"
            icon = "✅" if result == "GOOD" else "⚠️"
            st.markdown(
                f"<span class='{badge_class}'>{icon} {result}</span>"
                f"&nbsp;&nbsp;<span class='{severity_class}'>{severity_label}</span>",
                unsafe_allow_html=True,
            )
            st.write("")
            st.markdown(f"**Condition:** {condition}")
            st.progress(min(int(confidence), 100))
            st.caption(f"Confidence: **{confidence}%**")

            st.write("")
            p1, p2, p3 = st.columns(3)
            p1.markdown(
                f"<div class='metric-box'><div class='metric-num' style='color:#a5d6a7'>{pie_values[0]:.0f}%</div>"
                f"<div class='metric-label'>Healthy Tissue</div></div>",
                unsafe_allow_html=True,
            )
            p2.markdown(
                f"<div class='metric-box'><div class='metric-num' style='color:#ffcc80'>{pie_values[1]:.0f}%</div>"
                f"<div class='metric-label'>Warning Tissue</div></div>",
                unsafe_allow_html=True,
            )
            p3.markdown(
                f"<div class='metric-box'><div class='metric-num' style='color:#ef9a9a'>{pie_values[2]:.0f}%</div>"
                f"<div class='metric-label'>Damaged Tissue</div></div>",
                unsafe_allow_html=True,
            )

        st.write("---")

        tips_html = "".join(f"<li style='margin-bottom:6px'>{tip}</li>" for tip in t["tips"])
        card_class = f"treatment-card {t['card_class']}".strip()
        st.markdown(f"""
        <div class='{card_class}'>
            <b style='font-family:Sora,sans-serif;color:#e8f5e9;font-size:1rem'>
                {t["icon"]} {t["title"]}
            </b>
            <ul style='color:#c8e6c9;margin-top:10px;padding-left:18px'>
                {tips_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.write("---")

        st.markdown("#### 📊 Leaf Colour Composition")
        fig = make_pie_figure(
            pie_values,
            ["#4caf50", "#ffca28", "#8d6e63"],
            ["Green", "Yellow", "Brown"],
        )
        st.pyplot(fig)
        plt.close(fig)

        st.write("---")

        st.markdown("#### 💾 Save Result")
        leaf_name = st.text_input(
            "Leaf scan name",
            placeholder="e.g. Field-A Sample 1",
            key=f"leaf_name_{file_hash}_{st.session_state.save_nonce}",
        )

        if st.button("💾 Save to History"):
            if leaf_name.strip() == "":
                st.warning("Please enter a name before saving.")
            elif file_hash in st.session_state.saved_hashes:
                st.warning("This image is already saved.")
            else:
                st.session_state.history.append({
                    "name": leaf_name.strip(),
                    "result": result,
                    "confidence": confidence,
                    "condition": condition,
                    "severity": severity_label,
                    "pie_values": pie_values,
                    "image_bytes": uploaded_bytes,
                    "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "scan_hash": file_hash,
                })
                st.session_state.saved_hashes.append(file_hash)
                st.session_state.save_nonce += 1
                st.success(f"✅ '{leaf_name}' saved to history!")
                st.rerun()
    else:
        st.info("⬆️ Upload an image or use your camera above to scan a leaf.")

# ══════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════
with tab_analytics:
    st.markdown("#### 📊 Scan Analytics")

    if st.session_state.history:
        good_count = sum(1 for i in st.session_state.history if i["result"] == "GOOD")
        bad_count = sum(1 for i in st.session_state.history if i["result"] == "BAD")
        high_risk = sum(1 for i in st.session_state.history if "High" in i.get("severity", ""))
        total = len(st.session_state.history)

        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(
            f"<div class='metric-box'><div class='metric-num'>{total}</div><div class='metric-label'>Total Scans</div></div>",
            unsafe_allow_html=True,
        )
        m2.markdown(
            f"<div class='metric-box'><div class='metric-num' style='color:#a5d6a7'>{good_count}</div><div class='metric-label'>Healthy</div></div>",
            unsafe_allow_html=True,
        )
        m3.markdown(
            f"<div class='metric-box'><div class='metric-num' style='color:#ef9a9a'>{bad_count}</div><div class='metric-label'>Diseased / Deficient</div></div>",
            unsafe_allow_html=True,
        )
        m4.markdown(
            f"<div class='metric-box'><div class='metric-num' style='color:#ef5350'>{high_risk}</div><div class='metric-label'>High Risk</div></div>",
            unsafe_allow_html=True,
        )

        st.write("")
        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.markdown("##### Health Distribution")
            fig2, ax2 = plt.subplots(figsize=(4, 4), facecolor="#0f1a10")
            ax2.set_facecolor("#0f1a10")
            ax2.pie(
                [good_count, bad_count],
                labels=["GOOD", "BAD"],
                autopct="%1.1f%%",
                colors=["#4caf50", "#ef5350"],
                startangle=90,
                wedgeprops={"edgecolor": "#0f1a10", "linewidth": 2},
            )
            for tx in ax2.texts:
                tx.set_color("#c8e6c9")
            st.pyplot(fig2)
            plt.close(fig2)

        with col_bar:
            st.markdown("##### Confidence per Scan")
            names = [
                entry["name"][:12] if entry["name"] else f"Scan {i+1}"
                for i, entry in enumerate(st.session_state.history)
            ]
            confidences = [entry["confidence"] for entry in st.session_state.history]
            bar_colors = ["#4caf50" if entry["result"] == "GOOD" else "#ef5350" for entry in st.session_state.history]

            fig3, ax3 = plt.subplots(figsize=(5, 4), facecolor="#0f1a10")
            ax3.set_facecolor("#1a2b1c")
            ax3.bar(range(len(names)), confidences, color=bar_colors, edgecolor="#0f1a10")
            ax3.set_xticks(range(len(names)))
            ax3.set_xticklabels(names, rotation=30, ha="right", color="#c8e6c9", fontsize=9)
            ax3.set_ylabel("Confidence (%)", color="#c8e6c9", fontsize=9)
            ax3.set_ylim(0, 100)
            ax3.tick_params(colors="#c8e6c9")
            for spine in ax3.spines.values():
                spine.set_edgecolor("#2d4a2f")
            ax3.legend(
                handles=[
                    mpatches.Patch(color="#4caf50", label="GOOD"),
                    mpatches.Patch(color="#ef5350", label="BAD")
                ],
                facecolor="#1a2b1c",
                labelcolor="white",
                edgecolor="#2d4a2f"
            )
            st.pyplot(fig3)
            plt.close(fig3)

        st.write("")
        st.markdown("##### 🌡️ Severity Breakdown")

        sev_counts = {
            "Low Risk": sum(1 for i in st.session_state.history if "Low" in i.get("severity", "")),
            "Medium Risk": sum(1 for i in st.session_state.history if "Medium" in i.get("severity", "")),
            "High Risk": sum(1 for i in st.session_state.history if "High" in i.get("severity", "")),
        }

        fig4, ax4 = plt.subplots(figsize=(5, 2.5), facecolor="#0f1a10")
        ax4.set_facecolor("#1a2b1c")
        bars = ax4.barh(
            list(sev_counts.keys()),
            list(sev_counts.values()),
            color=["#4caf50", "#ffa726", "#ef5350"],
            edgecolor="#0f1a10",
            height=0.5,
        )
        ax4.set_xlabel("Count", color="#c8e6c9", fontsize=9)
        ax4.tick_params(colors="#c8e6c9")
        for spine in ax4.spines.values():
            spine.set_edgecolor("#2d4a2f")
        for bar, val in zip(bars, sev_counts.values()):
            ax4.text(
                bar.get_width() + 0.05,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center",
                color="white",
                fontsize=10,
            )
        st.pyplot(fig4)
        plt.close(fig4)
    else:
        st.info("No scan data yet. Upload and save leaf images from the Dashboard tab.")

# ══════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════
with tab_history:
    st.markdown("#### 📁 Scan History")

    if st.session_state.history:
        if st.button("🗑️ Clear All History"):
            st.session_state.history = []
            st.session_state.saved_hashes = []
            st.rerun()

        for idx, item in enumerate(st.session_state.history, 1):
            badge = "badge-good" if item["result"] == "GOOD" else "badge-bad"
            sev = item.get("severity", "")
            ts = item.get("timestamp", "—")
            sev_class = "sev-low" if "Low" in sev else ("sev-medium" if "Medium" in sev else "sev-high")
            t_data = treatment_for_condition(item.get("condition", "Mixed Stress"))
            tips_html = "".join(
                f"<li style='margin-bottom:4px;color:#a5c9a7;font-size:0.82rem'>{tip}</li>"
                for tip in t_data["tips"]
            )
            card_class = f"treatment-card {t_data['card_class']}".strip()

            st.markdown(f"""
            <div class='agro-card'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px'>
                    <b style='font-size:1rem;font-family:Sora,sans-serif;color:#e8f5e9'>
                        #{idx} — {item['name']}
                    </b>
                    <span class='ts-tag'>🕐 {ts}</span>
                </div>
                <br>
                <span class='{badge}'>{item['result']}</span>
                &nbsp;<span class='{sev_class}'>{sev if sev else "—"}</span>
                &nbsp;&nbsp;
                <span style='color:#a5c9a7'>Condition: {item['condition']}</span><br>
                <span style='color:#81c784;font-size:0.85rem'>Confidence: {item['confidence']}%</span>
                <br><br>
                <details>
                    <summary style='color:#81c784;cursor:pointer;font-size:0.85rem;
                                    font-family:Sora,sans-serif;font-weight:600'>
                        View Treatment Tips
                    </summary>
                    <div class='{card_class}' style='margin-top:10px'>
                        <b style='font-family:Sora,sans-serif;color:#e8f5e9;font-size:0.95rem'>
                            {t_data["title"]}
                        </b>
                        <ul style='padding-left:16px;margin-top:8px'>
                            {tips_html}
                        </ul>
                    </div>
                </details>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No history yet. Save scans from the Dashboard tab.")

# ══════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════
with tab_about:
    st.markdown("#### ℹ️ About AgroDetect AI")
    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("""
        <div class='agro-card'>
            <h4 style='margin-top:0;color:#a5d6a7'>🌿 What It Does</h4>
            AgroDetect AI analyses leaf images using colour-ratio intelligence to instantly
            detect plant health. Upload a photo for an instant GOOD / BAD classification,
            severity rating, treatment tips, and full timestamped history.
        </div>
        <div class='agro-card'>
            <h4 style='margin-top:0;color:#a5d6a7'>🚀 Features</h4>
            • Leaf health detection (Healthy / Disease / Deficiency)<br>
            • 🌡️ Severity meter — Low / Medium / High Risk<br>
            • 📷 File upload or camera capture<br>
            • 💡 Treatment suggestions per condition<br>
            • 📅 Timestamped scan history<br>
            • Analytics with severity breakdown chart
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div class='agro-card'>
            <h4 style='margin-top:0;color:#a5d6a7'>🔬 How It Works</h4>
            The model converts the image to HSV space and filters out background noise. It then
            measures green, yellow, and brown leaf tones to decide whether the leaf is healthy,
            under nutrient stress, or affected by disease.
        </div>
        <div class='agro-card'>
            <h4 style='margin-top:0;color:#a5d6a7'>🔮 Future Scope</h4>
            • Deep Learning model (CNN / Vision Transformer)<br>
            • Multi-class disease classification (30+ types)<br>
            • Weather and soil data integration<br>
            • Mobile app (Android / iOS)<br>
            • Geo-tagged field reports and crop mapping
        </div>
        """, unsafe_allow_html=True)
