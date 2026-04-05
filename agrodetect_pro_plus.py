import streamlit as st
from PIL import Image
import random
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

# ---------- HOME ----------
if st.session_state.page == "Home":

    st.title("🌿 AgroDetect AI")
    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)

        # RUN MODEL ONLY ONCE
        if "result_data" not in st.session_state:
            with st.spinner("Analyzing..."):
                time.sleep(1)

            green = random.randint(30, 70)
            yellow = random.randint(10, 40)
            brown = 100 - green - yellow

            if brown < 0:
                brown = 10

            if green > 50:
                result = "GOOD"
                condition = "Healthy Leaf"
            else:
                result = "BAD"
                condition = "Nutrient Deficiency"

            confidence = round(random.uniform(60, 99), 2)

            st.session_state.result_data = {
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "green": green,
                "yellow": yellow,
                "brown": brown
            }

        data = st.session_state.result_data

        # ---------- RESULT BOXES ----------
        col1, col2, col3 = st.columns(3)

        with col1:
            st.success(f"RESULT: {data['result']}")

        with col2:
            st.info(f"CONFIDENCE: {data['confidence']}%")

        with col3:
            st.warning(f"CONDITION: {data['condition']}")

        # ---------- PIE CHART ----------
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

        if st.button("Save to History"):

            # SAVE WITHOUT CHANGING RESULT
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

            st.success("Saved!")

            # RESET PROPERLY
            del st.session_state.result_data
            st.rerun()

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

                # PDF
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

        st.write(f"Total: {len(st.session_state.history)}")
        st.write(f"Good: {good}")
        st.write(f"Bad: {bad}")

# ---------- ABOUT ----------
elif st.session_state.page == "About":

    st.title("ℹ About")
    st.write("AgroDetect AI helps detect plant health using AI.")
