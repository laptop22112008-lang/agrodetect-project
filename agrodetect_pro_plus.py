import streamlit as st
from PIL import Image
import random
import time
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "view_index" not in st.session_state:
    st.session_state.view_index = None

# ---------------- NAVIGATION ----------------
st.sidebar.title("🌿 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"

if st.sidebar.button("📁 History"):
    st.session_state.page = "History"

if st.sidebar.button("📊 Analytics"):
    st.session_state.page = "Analytics"

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

        # 🔥 SMOOTH LOADING
        with st.spinner("Analyzing leaf..."):
            time.sleep(1.5)

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

        # 🔥 RESULT BOX
        if result == "GOOD":
            st.success(f"Result: GOOD\nConfidence: {confidence}%\nCondition: {condition}")
        else:
            st.error(f"Result: BAD\nConfidence: {confidence}%\nCondition: {condition}")

        # 🔥 PIE CHART
        labels = ["Green", "Yellow", "Brown"]
        sizes = [green, yellow, brown]
        colors = ["green", "yellow", "brown"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

        # 🔥 INPUT
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

            # 🔥 CLEAR INPUT
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

            # 👁 VIEW TOGGLE
            if st.button(f"View {i}"):

                if st.session_state.view_index == i:
                    st.session_state.view_index = None
                else:
                    st.session_state.view_index = i

            # 🔍 DETAIL VIEW
            if st.session_state.view_index == i:
                st.write("### Detailed View")
                st.image(item["image"], width=300)

            # 📄 PDF
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

    # 🔥 DOWNLOAD ALL (ONLY ONCE)
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

        st.write(f"Total Leaves: {total}")
        st.write(f"Good: {good}")
        st.write(f"Bad: {bad}")

        labels = ["Good", "Bad"]
        sizes = [good, bad]
        colors = ["green", "red"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

# ---------------- ABOUT ----------------
elif page == "About":

    st.subheader("About")

    st.write("""
    AgroDetect AI helps detect plant leaf conditions using AI.

    ✔ Detects healthy vs unhealthy leaves  
    ✔ Provides confidence score  
    ✔ Stores history  
    ✔ Downloadable reports  

    Future improvements:
    - Real AI model
    - Disease classification
    - Mobile app
    """)
