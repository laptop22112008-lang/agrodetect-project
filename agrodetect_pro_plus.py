import streamlit as st
from PIL import Image
import random
import io
import time
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "predicted" not in st.session_state:
    st.session_state.predicted = False

if "data" not in st.session_state:
    st.session_state.data = {}

# ---------------- NAVIGATION ----------------
st.sidebar.title("🌿 Navigation")

page = st.sidebar.radio("", ["Home", "History", "Analytics", "About"])

# ---------------- MODEL (KEEP SAME LOGIC STYLE) ----------------
def predict():
    green = random.randint(40, 80)
    yellow = random.randint(10, 40)
    brown = max(0, 100 - green - yellow)

    if green > 60:
        result = "GOOD"
        condition = "Healthy Leaf"
        confidence = random.uniform(90, 99)
    else:
        result = "BAD"
        condition = "Nutrient Deficiency"
        confidence = random.uniform(60, 85)

    return result, confidence, condition, green, yellow, brown

# ---------------- PDF ----------------
def generate_pdf(item):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"Leaf Name: {item['name']}", styles["Title"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Result: {item['result']}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence: {item['confidence']:.2f}%", styles["Normal"]))
    elements.append(Paragraph(f"Condition: {item['condition']}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------- HOME ----------------
if page == "Home":

    st.title("🌿 AgroDetect AI")

    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:

        image = Image.open(uploaded_file)
        st.image(image, width=250)

        # RUN MODEL ONLY ONCE
        if not st.session_state.predicted:
            result, confidence, condition, g, y, b = predict()

            st.session_state.data = {
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "green": g,
                "yellow": y,
                "brown": b
            }

            st.session_state.predicted = True

        data = st.session_state.data

        # ---------------- RESULT ----------------
        st.subheader("Result")
        st.write(f"Result: {data['result']}")
        st.write(f"Confidence: {data['confidence']:.2f}%")
        st.write(f"Condition: {data['condition']}")

        # ---------------- ANALYSIS ----------------
        st.subheader("Leaf Analysis")
        st.write({
            "Green": data["green"],
            "Yellow": data["yellow"],
            "Brown": data["brown"]
        })

        # ---------------- INPUT ----------------
        leaf_name = st.text_input("Enter Leaf Name", key="leaf_input")

        # ---------------- SAVE ----------------
        if st.button("Save to History"):

            if leaf_name.strip() != "":

                st.session_state.history.append({
                    "name": leaf_name,
                    "result": data["result"],
                    "confidence": data["confidence"],
                    "condition": data["condition"],
                    "green": data["green"],
                    "yellow": data["yellow"],
                    "brown": data["brown"]
                })

                st.success("Saved Successfully!")

                # RESET SAFE
                st.session_state.predicted = False
                st.session_state.data = {}

                time.sleep(1)
                st.rerun()

# ---------------- HISTORY ----------------
elif page == "History":

    st.title("📜 History")

    if not st.session_state.history:
        st.info("No data yet")

    for item in st.session_state.history:
        st.write(f"### {item['name']}")
        st.write(f"Result: {item['result']}")
        st.write(f"Confidence: {item['confidence']:.2f}%")
        st.write(f"Condition: {item['condition']}")

        pdf = generate_pdf(item)

        st.download_button(
            "Download Report",
            pdf,
            file_name=f"{item['name']}.pdf"
        )

    # DOWNLOAD ALL (simple)
    if st.session_state.history:
        st.button("Download All Reports")

# ---------------- ANALYTICS ----------------
elif page == "Analytics":

    st.title("📊 Analytics")

    total = len(st.session_state.history)
    good = sum(1 for i in st.session_state.history if i["result"] == "GOOD")
    bad = total - good

    st.metric("Total Uploads", total)
    st.metric("Healthy", good)
    st.metric("Diseased", bad)

# ---------------- ABOUT ----------------
elif page == "About":

    st.title("ℹ About")

    st.write("""
    AgroDetect AI is a simple leaf analysis system.

    Features:
    - Detect plant condition
    - Show confidence score
    - Save history
    - Generate reports
    - Analytics overview

    Built using Streamlit 🌿
    """)
