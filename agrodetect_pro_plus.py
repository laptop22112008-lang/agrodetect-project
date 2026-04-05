import streamlit as st
from PIL import Image
import random
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- SIDEBAR ----------------
st.sidebar.title("🌿 Navigation")

page = st.sidebar.radio(
    "",
    ["Home", "History", "About"]
)

# ---------------- TITLE ----------------
st.title("🌿 AgroDetect AI")

# ---------------- HOME ----------------
if page == "Home":

    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Choose Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=250)

        # -------- FAKE MODEL (WORKING GOOD) --------
        result = random.choice(["GOOD", "BAD"])
        confidence = round(random.uniform(60, 99), 2)

        if result == "GOOD":
            condition = "Healthy Leaf"
            green = 100
            yellow = 0
            brown = 0
        else:
            condition = random.choice(["Disease Detected", "Nutrient Deficiency"])
            green = random.randint(20, 60)
            yellow = random.randint(10, 40)
            brown = 100 - (green + yellow)

        # -------- RESULT --------
        st.markdown("### Result")
        st.write(f"**Result:** {result}")
        st.write(f"**Confidence:** {confidence}%")
        st.write(f"**Condition:** {condition}")

        # -------- PIE --------
        st.markdown("### Leaf Analysis")
        st.write({
            "Green": green,
            "Yellow": yellow,
            "Brown": brown
        })

        # -------- NAME INPUT --------
        leaf_name = st.text_input("Enter Leaf Name")

        if st.button("Save to History"):

            record = {
                "name": leaf_name if leaf_name else f"Leaf {len(st.session_state.history)+1}",
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "image": uploaded_file.getvalue()
            }

            st.session_state.history.append(record)
            st.success("Saved!")

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

            # -------- PDF DOWNLOAD --------
            def create_pdf(data, index):
                file_name = f"report_{index}.pdf"

                doc = SimpleDocTemplate(file_name)
                styles = getSampleStyleSheet()

                story = []
                story.append(Paragraph(f"Leaf Name: {data['name']}", styles["Title"]))
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

            pdf_data = create_pdf(item, i)

            st.download_button(
                label="Download Report",
                data=pdf_data,
                file_name=f"{item['name']}.pdf"
            )

    # -------- DOWNLOAD ALL --------
    if st.button("Download All Reports"):
        st.warning("Download one by one for now (safe version)")

# ---------------- ABOUT ----------------
elif page == "About":

    st.subheader("About AgroDetect AI")

    st.write("""
    AgroDetect AI is an AI-powered system designed to help farmers analyze plant leaf health.

    Features:
    - Detect healthy vs unhealthy leaves
    - Provides confidence level
    - Gives condition details
    - Maintains history of reports
    - Downloadable PDF reports

    Future Scope:
    - Real AI model integration
    - Disease classification
    - Mobile app version

    Built using Streamlit.
    """)
