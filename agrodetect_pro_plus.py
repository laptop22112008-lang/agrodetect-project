import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import io
import hashlib
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# ───────────────── CONFIG ─────────────────
st.set_page_config(page_title="AgroDetect AI", page_icon="🌿", layout="wide")

# ───────────────── SESSION ─────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "result_data" not in st.session_state:
    st.session_state.result_data = None

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

if "flash_message" not in st.session_state:
    st.session_state.flash_message = ""

if "saved_hashes" not in st.session_state:
    st.session_state.saved_hashes = []

# ───────────────── HELPERS ─────────────────
def safe_pie_values(values):
    arr = np.array(values, dtype=float)
    if np.sum(arr) <= 0:
        return [34, 33, 33]
    arr = np.maximum(arr, 0.5)
    arr = arr / np.sum(arr) * 100
    return arr.tolist()

def make_pie_figure(values):
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    values = safe_pie_values(values)

    ax.pie(
        values,
        labels=["Green", "Yellow", "Brown"],
        colors=["green", "yellow", "brown"],
        autopct=lambda p: f'{p:.1f}%' if p > 3 else "",
        startangle=90
    )

    ax.axis("equal")
    return fig

def build_pdf(item):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph(f"<b>{item['name']}</b>", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Result: {item['result']}", styles["Normal"]))
    story.append(Paragraph(f"Confidence: {item['confidence']}%", styles["Normal"]))
    story.append(Paragraph(f"Condition: {item['condition']}", styles["Normal"]))
    story.append(Spacer(1, 10))

    img = io.BytesIO(item["image_bytes"])
    story.append(RLImage(img, width=200, height=200))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ───────────────── MODEL (UNCHANGED) ─────────────────
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
        condition = "Mostly Healthy"
        confidence = round(65 + green_ratio * 20, 2)

    else:
        result = "BAD"
        condition = "Stress / Early Issue"
        confidence = round(55 + (yellow_ratio + brown_ratio) * 30, 2)

    return result, confidence, condition, green, yellow, brown

# ───────────────── NAV ─────────────────
st.sidebar.title("🌿 AgroDetect AI")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"
if st.sidebar.button("📁 History"):
    st.session_state.page = "History"
if st.sidebar.button("📊 Analytics"):
    st.session_state.page = "Analytics"
if st.sidebar.button("ℹ️ About"):
    st.session_state.page = "About"

# ───────────────── HOME ─────────────────
if st.session_state.page == "Home":

    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = ""

    st.title("🌿 AgroDetect AI")
    st.subheader("Upload Leaf Image")

    file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

    if file:
        image = Image.open(file)
        st.image(image, width=300)

        file_bytes = file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        if st.session_state.result_data is None or st.session_state.result_data.get("hash") != file_hash:
            time.sleep(0.5)
            result, confidence, condition, g, y, b = analyze_leaf(image)

            st.session_state.result_data = {
                "hash": file_hash,
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "green": g,
                "yellow": y,
                "brown": b,
                "image_bytes": file_bytes
            }

        data = st.session_state.result_data

        st.success(f"RESULT: {data['result']}")
        st.info(f"CONFIDENCE: {data['confidence']}%")
        st.warning(f"CONDITION: {data['condition']}")

        st.subheader("📊 Leaf Analysis")

        fig = make_pie_figure([data["green"], data["yellow"], data["brown"]])
        st.pyplot(fig)

        leaf_name = st.text_input("Leaf scan name")

        if st.button("Save to History"):
            if file_hash in st.session_state.saved_hashes:
                st.warning("Already saved!")
            else:
                st.session_state.history.append({
                    "name": leaf_name if leaf_name else "Leaf",
                    "result": data["result"],
                    "confidence": data["confidence"],
                    "condition": data["condition"],
                    "green": data["green"],
                    "yellow": data["yellow"],
                    "brown": data["brown"],
                    "image_bytes": data["image_bytes"]
                })
                st.session_state.saved_hashes.append(file_hash)
                st.session_state.flash_message = "Saved successfully!"
                st.session_state.result_data = None
                st.rerun()

# ───────────────── HISTORY ─────────────────
elif st.session_state.page == "History":

    st.title("📁 History")

    if not st.session_state.history:
        st.info("No history yet")
    else:
        for i, item in enumerate(st.session_state.history):

            st.image(item["image_bytes"], width=100)
            st.write(item["name"])
            st.write(item["result"], item["confidence"], item["condition"])

            pdf = build_pdf(item)

            st.download_button(
                "Download Report",
                pdf,
                file_name=f"{item['name']}.pdf",
                key=i
            )

# ───────────────── ANALYTICS ─────────────────
elif st.session_state.page == "Analytics":

    st.title("📊 Analytics")

    if st.session_state.history:
        good = sum(1 for i in st.session_state.history if i["result"]=="GOOD")
        bad = len(st.session_state.history) - good

        fig = make_pie_figure([good, bad, 0])
        st.pyplot(fig)

# ───────────────── ABOUT ─────────────────
elif st.session_state.page == "About":

    st.title("ℹ️ About AgroDetect AI")

    st.write("Leaf health detection system")
