import streamlit as st
from PIL import Image
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------------- SIDEBAR (BOX STYLE) ----------------
st.sidebar.title("🌿 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"

if st.sidebar.button("📁 History"):
    st.session_state.page = "History"

if st.sidebar.button("ℹ️ About"):
    st.session_state.page = "About"

page = st.session_state.page

# ---------------- TITLE ----------------
st.title("🌿 AgroDetect AI")

# ---------------- HOME ----------------
if page == "Home":

    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Choose Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=250)

        # -------- MODEL --------
        result = random.choice(["GOOD", "BAD"])
        confidence = round(random.uniform(60, 99), 2)

        if result == "GOOD":
            condition = "Healthy Leaf"
            green, yellow, brown = 90, 5, 5
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

        # -------- INPUT --------
        leaf_name = st.text_input("Enter Leaf Name")

        if st.button("Save to History"):

            st.session_state.history.append({
                "name": leaf_name if leaf_name else f"Leaf {len(st.session_state.history)+1}",
                "result": result,
                "confidence": confidence,
                "condition": condition,
                "image": uploaded_file.getvalue()
            })

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

            # -------- PDF --------
            def create_pdf(data, index):
                file_name = f"report_{index}.pdf"

                doc = SimpleDocTemplate(file_name)
                styles = getSampleStyleSheet()

                story = []
                story.append(Paragraph(f"{data['name']}", styles["Title"]))
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

            st.download_button(
                "Download Report",
                pdf,
                file_name=f"{item['name']}.pdf"
            )

    # ✅ SHOW ONLY IF HISTORY EXISTS
    if len(st.session_state.history) > 0:
        st.markdown("---")
        st.button("Download All Reports")

# ---------------- ABOUT ----------------
elif page == "About":

    st.subheader("About")

    st.write("""
    AgroDetect AI helps detect plant leaf conditions.

    ✔ Detects healthy vs unhealthy leaves  
    ✔ Shows confidence  
    ✔ Stores history  
    ✔ Downloadable reports  

    Future:
    - Real AI model
    - Mobile app
    - Disease classification
    """)
