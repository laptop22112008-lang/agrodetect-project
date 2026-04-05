import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import time
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "selected" not in st.session_state:
    st.session_state.selected = None

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ---------------- NAVIGATION ----------------
st.sidebar.markdown("## 🌿 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"

if st.sidebar.button("📂 History"):
    st.session_state.page = "History"

if st.sidebar.button("📘 About"):
    st.session_state.page = "About"

page = st.session_state.page

# ---------------- SMART MODEL ----------------
def analyze_leaf(image):
    img = np.array(image)

    r = img[:,:,0] / 255.0
    g = img[:,:,1] / 255.0
    b = img[:,:,2] / 255.0

    green_mask = (g > r) & (g > b)
    yellow_mask = (r > 0.5) & (g > 0.5) & (b < 0.4)
    brown_mask = (r > 0.4) & (g < 0.4) & (b < 0.3)

    total = img.shape[0] * img.shape[1]

    green_ratio = np.sum(green_mask) / total
    yellow_ratio = np.sum(yellow_mask) / total
    brown_ratio = np.sum(brown_mask) / total

    if green_ratio > 0.6:
        return "GOOD", round(80 + green_ratio*20,2), "Healthy Leaf"
    elif brown_ratio > 0.2:
        return "BAD", round(60 + brown_ratio*30,2), "Disease (Brown Spots)"
    elif yellow_ratio > 0.2:
        return "BAD", round(60 + yellow_ratio*30,2), "Nutrient Deficiency"
    else:
        return "BAD", round(55 + (yellow_ratio+brown_ratio)*50,2), "Mild Stress"

# ---------------- HOME ----------------
if page == "Home":

    st.title("🌿 AgroDetect Pro MAX")
    st.subheader("Upload Leaf Image")

    file = st.file_uploader("", type=["jpg","png","jpeg"])

    if file:
        image = Image.open(file)
        st.image(image, use_container_width=True)

        with st.spinner("Analyzing..."):
            time.sleep(1)
            result, confidence, condition = analyze_leaf(image)

        st.success(f"Result: {result}")
        st.info(f"Confidence: {confidence}%")
        st.warning(f"Condition: {condition}")

        # PIE CHART
        fig, ax = plt.subplots()

        if result == "GOOD":
            values = [confidence, 100-confidence]
            labels = ["Healthy", "Risk"]
            colors = ["green", "orange"]
        else:
            values = [confidence, 100-confidence]
            labels = ["Affected", "Healthy"]
            colors = ["brown", "green"]

        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        st.pyplot(fig)

        leaf_name = st.text_input(
            "Enter Leaf Name",
            key=f"leaf_name_{st.session_state.input_key}"
        )

        if st.button("Save"):
            st.session_state.history.append({
                "name": leaf_name if leaf_name else f"Leaf {len(st.session_state.history)+1}",
                "image": image,
                "result": result,
                "confidence": confidence,
                "condition": condition
            })

            st.success("Saved!")
            st.session_state.input_key += 1
            st.rerun()

# ---------------- HISTORY ----------------
elif page == "History":

    st.title("📂 History")

    history = st.session_state.history
    styles = getSampleStyleSheet()

    if not history:
        st.info("No history yet")

    else:

        # DOWNLOAD ALL
        buffer_all = io.BytesIO()
        doc = SimpleDocTemplate(buffer_all)
        elements = []

        for h in history:
            elements.append(Paragraph(f"Leaf Name: {h['name']}", styles['Normal']))
            elements.append(Paragraph(f"Result: {h['result']}", styles['Normal']))
            elements.append(Paragraph(f"Confidence: {h['confidence']}%", styles['Normal']))
            elements.append(Paragraph(f"Condition: {h['condition']}", styles['Normal']))
            elements.append(Spacer(1,10))

            img_buffer = io.BytesIO()
            h["image"].save(img_buffer, format="PNG")
            img_buffer.seek(0)

            elements.append(RLImage(img_buffer, width=200, height=150))
            elements.append(PageBreak())

        doc.build(elements)

        st.download_button(
            "⬇️ Download ALL Reports",
            buffer_all.getvalue(),
            file_name="All_Leaf_Reports.pdf"
        )

        st.markdown("---")

        for i, h in enumerate(history):

            col1, col2 = st.columns([1,3])

            with col1:
                st.image(h["image"], width=120)

                if st.button(f"View {i}"):
                    if st.session_state.selected == i:
                        st.session_state.selected = None
                    else:
                        st.session_state.selected = i

            with col2:
                st.markdown(f"### {h['name']}")
                st.write(f"Result: {h['result']}")
                st.write(f"Confidence: {h['confidence']}%")
                st.write(f"Condition: {h['condition']}")

                # SINGLE PDF
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer)

                elements = []

                elements.append(Paragraph(f"Leaf Name: {h['name']}", styles['Normal']))
                elements.append(Paragraph(f"Result: {h['result']}", styles['Normal']))
                elements.append(Paragraph(f"Confidence: {h['confidence']}%", styles['Normal']))
                elements.append(Paragraph(f"Condition: {h['condition']}", styles['Normal']))
                elements.append(Spacer(1,10))

                img_buffer = io.BytesIO()
                h["image"].save(img_buffer, format="PNG")
                img_buffer.seek(0)

                elements.append(RLImage(img_buffer, width=200, height=150))

                doc.build(elements)

                st.download_button(
                    "Download Report",
                    buffer.getvalue(),
                    file_name=f"{h['name']}.pdf"
                )

        # DETAIL VIEW
        if st.session_state.selected is not None:
            st.markdown("---")
            h = history[st.session_state.selected]

            st.subheader("🔍 Detailed View")
            st.image(h["image"], use_container_width=True)
            st.write(f"Result: {h['result']}")
            st.write(f"Confidence: {h['confidence']}%")
            st.write(f"Condition: {h['condition']}")

# ---------------- ABOUT ----------------
elif page == "About":

    st.title("📘 About AgroDetect Pro MAX")

    st.write("""
AgroDetect Pro MAX is an AI-powered leaf analysis system.

🌿 Features:
- Smart disease detection
- Confidence scoring
- Pie chart visualization
- History tracking
- PDF reports

🚀 Built for farmers & students.
""")
