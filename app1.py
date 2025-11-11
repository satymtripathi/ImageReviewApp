import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import random

# ---------------- CONFIG ----------------
IMAGE_FOLDER = Path(r"C:\Users\satyam.tripathi\Desktop\ImageReviewApp\images")
DATA_FOLDER = Path(r"C:\Users\satyam.tripathi\Desktop\ImageReviewApp\data")
OUTPUT_FILE = DATA_FOLDER / "reviews.csv"

DATA_FOLDER.mkdir(exist_ok=True)

st.set_page_config(page_title="Corneal Image Review", layout="centered")
st.title("🩺 Corneal Image Review System")

# ---------------- Reviewer ----------------
reviewer = st.text_input("Enter your name or ID:")
if not reviewer:
    st.warning("Please enter your name or ID to begin.")
    st.stop()

# ---------------- Load Images ----------------
images = list(IMAGE_FOLDER.glob("*.*"))
images.sort()  # stable order for all reviewers

# ---------------- Load Previous Reviews ----------------
if OUTPUT_FILE.exists():
    reviewed = pd.read_csv(OUTPUT_FILE)
    reviewed_images = reviewed.loc[reviewed["Reviewer"] == reviewer, "ImageName"].tolist()
else:
    reviewed_images = []

remaining_images = [img for img in images if img.name not in reviewed_images]
total_images = len(images)
completed = len(reviewed_images)
remaining = len(remaining_images)

# ---------------- Progress Display ----------------
st.markdown(f"**Reviewer:** {reviewer}")
st.progress(completed / total_images if total_images > 0 else 0)
st.write(f"✅ Completed: {completed} / {total_images}")
st.write(f"🕒 Remaining: {remaining}")

if not remaining_images:
    st.success("🎉 All images reviewed! Great job.")
    st.stop()

# ---------------- Current Image ----------------
current_image = remaining_images[0]
st.image(Image.open(current_image), caption=current_image.name, use_container_width=True)

# ---------------- Review Form ----------------
with st.form(key="review_form"):
    st.markdown(f"### Reviewing: {current_image.name}")
    condition = st.radio("Condition:", ["Normal", "Scar", "Edema", "Infection", "Others"], horizontal=True)
    confidence = st.radio("Confidence Level:", ["Low", "Medium", "High"], horizontal=True)
    submit = st.form_submit_button("✅ Submit Review")

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
        
        st.success(f"Saved review for {current_image.name}")
        st.rerun()
