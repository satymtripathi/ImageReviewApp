import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import random

# ---------------- CONFIG ----------------
IMAGE_FOLDER = Path(r"C:\Users\satyam.tripathi\Desktop\ImageReviewApp\images")
DATA_FOLDER = Path(r"C:\Users\satyam.tripathi\Desktop\ImageReviewApp\data")
OUTPUT_FILE = DATA_FOLDER / "reviews.csv"

DATA_FOLDER.mkdir(exist_ok=True)  # ensure folder exists

st.set_page_config(page_title="Corneal Image Review", layout="centered")
st.title("🩺 Corneal Image Review System")

# ---------------- Reviewer ----------------
reviewer = st.text_input("Enter your name or ID:")
if not reviewer:
    st.warning("Please enter your name or ID to begin.")
    st.stop()

# ---------------- Load Images ----------------
images = list(IMAGE_FOLDER.glob("*.*"))
random.shuffle(images)

# ---------------- Load Previous Reviews ----------------
if OUTPUT_FILE.exists():
    reviewed = pd.read_csv(OUTPUT_FILE)
    reviewed_images = reviewed.loc[reviewed["Reviewer"] == reviewer, "ImageName"].tolist()
else:
    reviewed_images = []

remaining_images = [img for img in images if img.name not in reviewed_images]

if not remaining_images:
    st.success("✅ You have reviewed all assigned images.")
    st.stop()

current_image = remaining_images[0]
st.image(Image.open(current_image), caption=current_image.name, use_container_width =True)

# ---------------- Review Form ----------------
with st.form(key="review_form"):
    condition = st.radio("Condition:", ["Normal", "Scar", "Edema", "Infection", "Others"])
    confidence = st.radio("Confidence Level:", ["Low", "Medium", "High"])
    submit = st.form_submit_button("Submit Review")

    if submit:
        data = {
            "Reviewer": reviewer,
            "ImageName": current_image.name,
            "Condition": condition,
            "Confidence": confidence
        }
        df = pd.DataFrame([data])
        if OUTPUT_FILE.exists():
            df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(OUTPUT_FILE, index=False)
        
        st.success(f"✅ Saved review for {current_image.name}")
        st.rerun()

