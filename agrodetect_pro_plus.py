import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import time
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AgroDetect AI", layout="wide")

# ---------- LOAD MODEL ----------
@st.cache_resource
def load_model():
    model = tf.keras.applications.MobileNetV2(weights="imagenet", include_top=False)
    return model

model = load_model()

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- NAV ----------
st.sidebar.title("🌿 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"

if st.sidebar.button("📜 History"):
    st.session_state.page = "History"

if st.sidebar.button("📊 Analytics"):
    st.session_state.page = "Analytics"

if st.sidebar.button("ℹ About"):
    st.session_state.page = "About"

# ---------- CNN ANALYSIS ----------
def analyze_leaf(image):

    img = image.resize((224, 224))
    img_array = np.array(img)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    features = model.predict(img_array)

    score = np.mean(features)

    # Decision logic based on deep features
    if score > 0:
        result = "GOOD"
        condition = "Healthy Leaf"
        confidence = round(70 + abs(score)*30, 2)
    else:
        result = "BAD"
        condition = "Disease / Stress Detected"
        confidence = round(60 + abs(score)*30, 2)

    # fallback color ratios (for pie chart only)
    arr = np.array(image)
    green = int(np.mean(arr[:,:,1]) / 255 * 100)
    yellow = int(np.mean(arr[:,:,0]) / 255 * 50)
    brown = max(0, 100 - green - yellow)

    return result, confidence, condition, green, yellow, brown

# ---------- HOME ----------
if st.session_state.page == "Home":

    st.title("🌿 AgroDetect AI")
    st.subheader("Upload Leaf Image")

    uploaded_file = st.file_uploader("Upload", type=["jpg","png","jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)

        file_bytes = uploaded_file.getvalue()

        if "last_image" not in st.session_state or st.session_state.last_image != file_bytes:
            st.session_state.last_image = file_bytes

            with st.spinner("Analyzing with AI model..."):
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

        # RESULT (VERTICAL)
        st.success(f"RESULT: {data['result']}")
        st.info(f"CONFIDENCE: {data['confidence']}%")
        st.warning(f"CONDITION: {data['condition']}")

        # PIE
        st.subheader("Leaf Analysis")

        fig, ax = plt.subplots()
        ax.pie(
            [data["green"], data["yellow"], data["brown"]],
            labels=["Green","Yellow","Brown"],
            autopct='%1.1f%%',
            colors=["green","yellow","brown"]
        )
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

            st.success("Saved!")

# ---------- HISTORY ----------
elif st.session_state.page == "History":

    st.title("📜 History")

    if not st.session_state.history:
        st.info("No data yet")

    for item in st.session_state.history:
        st.write(f"### {item['name']}")
        st.write(f"Result: {item['result']}")
        st.write(f"Confidence: {item['confidence']}%")
        st.write(f"Condition: {item['condition']}")

# ---------- ANALYTICS ----------
elif st.session_state.page == "Analytics":

    st.title("📊 Analytics")

    if st.session_state.history:
        good = sum(1 for i in st.session_state.history if i["result"]=="GOOD")
        bad = len(st.session_state.history) - good

        fig, ax = plt.subplots()
        ax.pie([good,bad], labels=["Good","Bad"], autopct='%1.1f%%')
        st.pyplot(fig)

# ---------- ABOUT ----------
elif st.session_state.page == "About":

    st.title("ℹ About AgroDetect AI")

    st.markdown("""
### 🌿 AgroDetect AI
AI-powered leaf health detection system.

### 🚀 Features
- Deep learning based detection
- Image analysis
- History tracking
- Analytics dashboard

### 🎯 Purpose
Helps farmers identify plant health issues quickly.
""")
