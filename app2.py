import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import random

# ---------------- CONFIG ----------------
IMAGE_FOLDER = Path(r"C:\Users\satyam.tripathi\Desktop\ImageReviewApp\images")
DATA_FOLDER = Path(r"C:\Users\satyam.tripathi\Desktop\ImageReviewApp\data")
MASTER_FILE = DATA_FOLDER / "reviews_master.csv"

DATA_FOLDER.mkdir(exist_ok=True)

st.set_page_config(page_title="🩺 Corneal Image Review", layout="centered")
st.title("🩺 Corneal Image Review System")

# ---------------- Reviewer ----------------
reviewer = st.text_input("Enter your name or ID:")
if not reviewer:
    st.warning("Please enter your name or ID to begin.")
    st.stop()

# reviewer-specific file
REVIEWER_FILE = DATA_FOLDER / f"reviews_{reviewer}.csv"

# ---------------- Load Images ----------------
images = list(IMAGE_FOLDER.glob("*.*"))
images.sort()  # keep stable order for consistent review assignment

# ---------------- Load Previous Reviews Safely ----------------
if REVIEWER_FILE.exists():
    try:
        reviewed = pd.read_csv(REVIEWER_FILE)
        if not reviewed.empty and "ImageName" in reviewed.columns:
            reviewed_images = reviewed["ImageName"].tolist()
        else:
            reviewed_images = []
    except Exception as e:
        st.warning(f"⚠️ Review file for {reviewer} is corrupted or unreadable. Starting fresh.\n\nError: {e}")
        reviewed_images = []
else:
    reviewed_images = []

remaining_images = [img for img in images if img.name not in reviewed_images]
total_images = len(images)
completed = len(reviewed_images)
remaining = len(remaining_images)

# ---------------- Progress Display ----------------
st.markdown(f"**Reviewer:** `{reviewer}`")
st.progress(completed / total_images if total_images > 0 else 0)
st.write(f"✅ **Completed:** {completed} / {total_images}")
st.write(f"🕒 **Remaining:** {remaining}")

if not remaining_images:
    st.success("🎉 All images reviewed! Great job.")
    st.stop()

# ---------------- Current Image ----------------
current_image = remaining_images[0]
st.image(Image.open(current_image), caption=current_image.name, use_container_width=True)

# ---------------- Review Form ----------------
with st.form(key="review_form"):
    st.markdown(f"### Reviewing: `{current_image.name}`")

    # 1️⃣ Primary classification
    condition = st.radio(
        "Condition:",
        ["Normal", "Scar", "Edema", "Infection", "Others"],
        horizontal=True
    )

    # 2️⃣ Confidence in classification
    confidence = st.radio(
        "Confidence in your assessment:",
        ["Low", "Moderate", "High"],
        horizontal=True
    )

    # 3️⃣ Acceptable misclassification note
    st.markdown("🧠 *If there is any overlap or acceptable margin of error, describe briefly:*")
    margin_note = st.text_area(
        "Example: 'Scar with mild edema – acceptable if labeled as Edema.'",
        placeholder="Write margin of acceptable misclassification or notes (optional)",
        height=80
    )

    # 4️⃣ Feedback about the image
    feedback = st.text_area(
        "💬 Any feedback about image quality, visibility, or clinical ambiguity (optional):",
        placeholder="Example: 'Image slightly blurred – visibility reduced.'",
        height=80
    )

    submit = st.form_submit_button("✅ Submit Review")

    if submit:
        data = {
            "Reviewer": reviewer,
            "ImageName": current_image.name,
            "Condition": condition,
            "Confidence": confidence,
            "MarginOfErrorNote": margin_note.strip() if margin_note else "",
            "Feedback": feedback.strip() if feedback else ""
        }

        df = pd.DataFrame([data])

        # Save to reviewer-specific file
        df.to_csv(REVIEWER_FILE, mode='a', header=not REVIEWER_FILE.exists(), index=False)

        # Also append to master file (combined data)
        df.to_csv(MASTER_FILE, mode='a', header=not MASTER_FILE.exists(), index=False)

        st.success(f"✅ Saved review for `{current_image.name}`")
        st.rerun()
