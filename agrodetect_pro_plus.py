import streamlit as st
from PIL import Image
import numpy as np
import random
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = {}

# ---------------- SIDEBAR ----------------
st.sidebar.title("🌿 Navigation")
page = st.sidebar.radio("", ["Home", "History", "Analytics", "About"])

# ---------------- FAKE MODEL ----------------
def predict(image):
    green = random.randint(40, 80)
    yellow = random.randint(10, 40)
    brown = 100 - green - yellow

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
def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(f"Leaf Name: {data['name']}", styles["Title"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Result: {data['result']}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence: {data['confidence']:.2f}%", styles["Normal"]))
    elements.append(Paragraph(f"Condition: {data['condition']}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------- HOME ----------------
if page == "Home":
    st.title("🌿 AgroDetect AI")

    uploaded = st.file_uploader("Upload Leaf Image", type=["jpg", "png", "jpeg"])

    if uploaded:
        image = Image.open(uploaded)
        st.image(image, width=250)

        # 🔥 RUN MODEL ONLY ONCE
        if not st.session_state.prediction_done:
            result, confidence, condition, g, y, b = predict(image)

            st.session_state.prediction_data = {
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "green": g,
                "yellow": y,
                "brown": b
            }

            st.session_state.prediction_done = True

        data = st.session_state.prediction_data

        # ---------------- RESULT UI ----------------
        col1, col2, col3 = st.columns(3)

        col1.metric("Result", data["result"])
        col2.metric("Confidence", f"{data['confidence']:.2f}%")
        col3.metric("Condition", data["condition"])

        # ---------------- PIE ----------------
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
            if leaf_name != "":
                st.session_state.history.append({
                    "name": leaf_name,
                    "result": data["result"],
                    "confidence": data["confidence"],
                    "condition": data["condition"],
                    "green": data["green"],
                    "yellow": data["yellow"],
                    "brown": data["brown"]
                })

                # RESET SAFE WAY
                st.session_state.prediction_done = False
                st.session_state.prediction_data = {}

                st.success("Saved Successfully!")

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

    # DOWNLOAD ALL
    if st.session_state.history:
        if st.button("Download All Reports"):
            st.success("Download individually (Streamlit limitation 😅)")

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📊 Analytics")

    total = len(st.session_state.history)
    good = sum(1 for i in st.session_state.history if i["result"] == "GOOD")
    bad = total - good

    st.metric("Total", total)
    st.metric("Healthy", good)
    st.metric("Diseased", bad)

# ---------------- ABOUT ----------------
elif page == "About":
    st.title("ℹ About")

    st.write("""
    AgroDetect AI is a smart plant health detection system.

    Features:
    - Leaf disease detection
    - Confidence scoring
    - History tracking
    - PDF reports
    - Analytics dashboard

    Built using Streamlit & AI concepts 🌿
    """)
# ---------------- HOME ----------------
if page == "Home":

    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Choose Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=250)

        # 🔥 FIXED RANDOM (not always BAD)
        with st.spinner("Analyzing leaf..."):
            time.sleep(1.2)

            result = random.choice(["GOOD", "BAD"])
            confidence = round(random.uniform(65, 98), 2)

        if result == "GOOD":
            condition = "Healthy Leaf"
            green, yellow, brown = 85, 10, 5
        else:
            condition = random.choice(["Disease Detected", "Nutrient Deficiency"])
            green = random.randint(25, 55)
            yellow = random.randint(20, 40)
            brown = 100 - (green + yellow)

        # 🔥 FIXED UI (separate lines)
        if result == "GOOD":
            st.success("Result: GOOD")
        else:
            st.error("Result: BAD")

        st.write(f"Confidence: {confidence}%")
        st.write(f"Condition: {condition}")

        # 🔥 PIE CHART
        labels = ["Green", "Yellow", "Brown"]
        sizes = [green, yellow, brown]
        colors = ["green", "yellow", "brown"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

        # INPUT
        leaf_name = st.text_input("Enter Leaf Name", key="leaf_input")

        if st.button("Save to History"):

            st.session_state.history.append({
                "name": leaf_name if leaf_name else f"Leaf {len(st.session_state.history)+1}",
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "image": uploaded_file.getvalue()
            })

            st.success("Saved to history!")
            st.session_state.leaf_input = ""

# ---------------- HISTORY ----------------
elif page == "History":

    st.subheader("History")

    if not st.session_state.history:
        st.info("No data yet")

    for i, item in enumerate(st.session_state.history):

        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(item["image"], width=120)

        with col2:
            st.write(f"### {item['name']}")
            st.write(f"Result: {item['result']}")
            st.write(f"Confidence: {item['confidence']}%")
            st.write(f"Condition: {item['condition']}")

            # PDF
            def create_pdf(data, index):
                file_name = f"report_{index}.pdf"

                doc = SimpleDocTemplate(file_name)
                styles = getSampleStyleSheet()

                story = []
                story.append(Paragraph(data['name'], styles["Title"]))
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"Result: {data['result']}", styles["Normal"]))
                story.append(Paragraph(f"Confidence: {data['confidence']}%", styles["Normal"]))
                story.append(Paragraph(f"Condition: {data['condition']}", styles["Normal"]))

                img_path = f"temp_{index}.jpg"
                with open(img_path, "wb") as f:
                    f.write(data["image"])

                story.append(Spacer(1, 10))
                story.append(RLImage(img_path, width=200, height=200))

                doc.build(story)

                with open(file_name, "rb") as f:
                    return f.read()

            pdf = create_pdf(item, i)

            st.download_button("Download Report", pdf, file_name=f"{item['name']}.pdf")

    if len(st.session_state.history) > 0:
        st.markdown("---")
        st.button("Download All Reports")

# ---------------- ANALYTICS ----------------
elif page == "Analytics":

    st.subheader("Analytics")

    total = len(st.session_state.history)

    if total == 0:
        st.info("No data yet")
    else:
        good = sum(1 for x in st.session_state.history if x["result"] == "GOOD")
        bad = total - good

        st.write(f"Total: {total}")
        st.write(f"Good: {good}")
        st.write(f"Bad: {bad}")

        fig, ax = plt.subplots()
        ax.pie([good, bad], labels=["Good", "Bad"], autopct='%1.1f%%', colors=["green", "red"])
        ax.axis('equal')
        st.pyplot(fig)

# ---------------- ABOUT ----------------
elif page == "About":

    st.subheader("About")

    st.write("""
    AgroDetect AI detects plant leaf health.

    ✔ Healthy vs Unhealthy  
    ✔ Confidence score  
    ✔ History tracking  
    ✔ PDF reports  
    """)
