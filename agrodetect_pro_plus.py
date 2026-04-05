import streamlit as st
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- NAVIGATION ----------
st.sidebar.title("🌿 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"

if st.sidebar.button("📜 History"):
    st.session_state.page = "History"

if st.sidebar.button("📊 Analytics"):
    st.session_state.page = "Analytics"

if st.sidebar.button("ℹ About"):
    st.session_state.page = "About"

# ---------- IMPROVED MODEL ----------
def analyze_leaf(image):

    img = np.array(image)

    r = img[:,:,0].astype(float)
    g = img[:,:,1].astype(float)
    b = img[:,:,2].astype(float)

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

    # texture
    gray = np.mean(img, axis=2)
    variance = np.var(gray)

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

    # -------- BALANCED DECISION (FINAL FIX) --------
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
# ---------- HOME ----------
if st.session_state.page == "Home":

    st.title("🌿 AgroDetect AI")
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

        # RESULT
        st.success(f"RESULT: {data['result']}")
        st.info(f"CONFIDENCE: {data['confidence']}%")
        st.warning(f"CONDITION: {data['condition']}")

        # PIE SAFE
        st.subheader("Leaf Analysis")

        values = [data["green"], data["yellow"], data["brown"]]

        if sum(values) == 0:
            values = [34, 33, 33]

        fig, ax = plt.subplots()
        ax.pie(values, labels=["Green","Yellow","Brown"],
               autopct='%1.1f%%',
               colors=["green","yellow","brown"])
        ax.axis('equal')
        st.pyplot(fig)

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

# ---------- HISTORY ----------
elif st.session_state.page == "History":

    st.title("📜 History")

    if not st.session_state.history:
        st.info("No data yet")

    else:
        for i, item in enumerate(st.session_state.history):

            col1, col2 = st.columns([1,3])

            with col1:
                st.image(item["image"], width=100)

            with col2:
                st.write(f"**Name:** {item['name']}")
                st.write(f"Result: {item['result']}")
                st.write(f"Confidence: {item['confidence']}%")
                st.write(f"Condition: {item['condition']}")

                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()

                content = []
                content.append(Paragraph(f"Leaf Name: {item['name']}", styles["Normal"]))
                content.append(Spacer(1, 10))
                content.append(Paragraph(f"Result: {item['result']}", styles["Normal"]))
                content.append(Paragraph(f"Confidence: {item['confidence']}%", styles["Normal"]))
                content.append(Paragraph(f"Condition: {item['condition']}", styles["Normal"]))

                doc.build(content)

                st.download_button(
                    "Download Report",
                    buffer.getvalue(),
                    file_name=f"{item['name']}.pdf",
                    key=f"download_{i}"
                )

        # -------- DOWNLOAD ALL --------
        st.markdown("---")
        if st.button("Download All Reports"):
            st.success("Download individual reports above")

# ---------- ANALYTICS ----------
elif st.session_state.page == "Analytics":

    st.title("📊 Analytics")

    if st.session_state.history:
        good = sum(1 for i in st.session_state.history if i["result"]=="GOOD")
        bad = len(st.session_state.history) - good

        fig, ax = plt.subplots()
        ax.pie([good,bad], labels=["Good","Bad"], autopct='%1.1f%%')
        st.pyplot(fig)

        st.write(f"Total Images: {len(st.session_state.history)}")
        st.write(f"Good: {good}")
        st.write(f"Bad: {bad}")

# ---------- ABOUT ----------
elif st.session_state.page == "About":

    st.title("ℹ About AgroDetect AI")

    st.markdown("""
### 🌿 AgroDetect AI

AgroDetect AI is a smart plant leaf analysis system.

### 🚀 Features
- Detects plant health condition
- Confidence-based prediction
- Visual analysis with pie charts
- History tracking
- Downloadable reports

### 🎯 Purpose
Helps farmers and students identify plant health issues quickly.

### 🔮 Future Scope
- Deep learning integration
- Disease-specific classification
- Mobile optimization
""")
