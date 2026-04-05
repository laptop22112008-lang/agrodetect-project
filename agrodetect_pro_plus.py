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

# ---------- MODEL (COLOR BASED) ----------
def analyze_leaf(image):
    img = np.array(image)

    r = np.mean(img[:,:,0])
    g = np.mean(img[:,:,1])
    b = np.mean(img[:,:,2])

    # normalize
    total = r + g + b
    r /= total
    g /= total
    b /= total

    green = int(g * 100)
    yellow = int((r + g)/2 * 100 - green//2)
    brown = max(0, 100 - green - yellow)

    if g > r and g > b:
        result = "GOOD"
        condition = "Healthy Leaf"
    else:
        result = "BAD"
        condition = "Unhealthy / Diseased"

    confidence = round(max(g, r, b) * 100, 2)

    return result, confidence, condition, green, yellow, brown

# ---------- HOME ----------
if st.session_state.page == "Home":

    st.title("🌿 AgroDetect AI")
    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)

        file_bytes = uploaded_file.getvalue()

        # RUN ONLY ON NEW IMAGE
        if "last_image" not in st.session_state or st.session_state.last_image != file_bytes:
            st.session_state.last_image = file_bytes

            with st.spinner("Analyzing..."):
                time.sleep(1)

            result, confidence, condition, green, yellow, brown = analyze_leaf(image)

            st.session_state.result_data = {
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "green": green,
                "yellow": yellow,
                "brown": brown
            }

        data = st.session_state.result_data

        # ---------- RESULT (VERTICAL FIXED) ----------
        st.success(f"RESULT: {data['result']}")
        st.info(f"CONFIDENCE: {data['confidence']}%")
        st.warning(f"CONDITION: {data['condition']}")

        # ---------- PIE ----------
        st.subheader("Leaf Analysis")

        labels = ['Green', 'Yellow', 'Brown']
        sizes = [data["green"], data["yellow"], data["brown"]]
        colors = ['green', 'yellow', 'brown']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

        # ---------- INPUT ----------
        leaf_name = st.text_input("Enter Leaf Name", key="leaf_input")

        # ---------- SAVE ----------
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

    if len(st.session_state.history) == 0:
        st.info("No data yet")

    else:
        for item in st.session_state.history:

            col1, col2 = st.columns([1, 3])

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
                    file_name=f"{item['name']}.pdf"
                )

# ---------- ANALYTICS ----------
elif st.session_state.page == "Analytics":

    st.title("📊 Analytics")

    if len(st.session_state.history) == 0:
        st.info("No data available")

    else:
        good = sum(1 for i in st.session_state.history if i["result"] == "GOOD")
        bad = sum(1 for i in st.session_state.history if i["result"] == "BAD")

        fig, ax = plt.subplots()
        ax.pie([good, bad], labels=["Good", "Bad"], autopct='%1.1f%%')
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
- Detects leaf health condition
- Shows confidence level
- Visual pie chart analysis
- Stores history of images
- Downloadable reports

### 🎯 Purpose
Helps farmers and students quickly identify plant health issues.

### 🔮 Future Scope
- Deep learning integration
- Disease-specific detection
- Mobile optimization
""")
