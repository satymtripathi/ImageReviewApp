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

st.set_page_config(page_title="🩺 Corneal Image Review", layout="wide")
st.title("🩺 Corneal Image Review System")

# ---------------- Reviewer ----------------
reviewer = st.text_input("Enter your name or ID:")
if not reviewer:
    st.warning("Please enter your name or ID to begin.")
    st.stop()

# Reviewer-specific file
REVIEWER_FILE = DATA_FOLDER / f"reviews_{reviewer}.csv"

# ---------------- Load Images ----------------
images = list(IMAGE_FOLDER.glob("*.*"))
images.sort()  # stable order

# ---------------- Load Previous Reviews Safely ----------------
if REVIEWER_FILE.exists():
    try:
        reviewed = pd.read_csv(REVIEWER_FILE)
        if reviewed.empty or "ImageName" not in reviewed.columns:
            reviewed = pd.DataFrame(columns=["Reviewer", "ImageName", "Condition", "Confidence", "MarginOfErrorNote", "Feedback"])
    except Exception as e:
        st.warning(f"⚠️ Could not read your previous file. Starting fresh.\n\nError: {e}")
        reviewed = pd.DataFrame(columns=["Reviewer", "ImageName", "Condition", "Confidence", "MarginOfErrorNote", "Feedback"])
else:
    reviewed = pd.DataFrame(columns=["Reviewer", "ImageName", "Condition", "Confidence", "MarginOfErrorNote", "Feedback"])

reviewed_images = reviewed["ImageName"].tolist()
remaining_images = [img for img in images if img.name not in reviewed_images]
total_images = len(images)
completed = len(reviewed_images)
remaining = len(remaining_images)

# ---------------- Sidebar Navigation ----------------
st.sidebar.header("🔍 Navigation & Actions")
mode = st.sidebar.radio(
    "Select Mode:",
    ["Review New Images", "Edit Previous Reviews"]
)

# ---------------- Progress ----------------
st.sidebar.write(f"**Reviewer:** {reviewer}")
st.sidebar.progress(completed / total_images if total_images > 0 else 0)
st.sidebar.write(f"✅ Completed: {completed} / {total_images}")
st.sidebar.write(f"🕒 Remaining: {remaining}")

# ---------------- Review New Images ----------------
if mode == "Review New Images":
    if not remaining_images:
        st.success("🎉 All images reviewed! You can switch to *Edit Mode* to update past results.")
        st.stop()

    current_image = remaining_images[0]
    st.image(Image.open(current_image), caption=current_image.name, use_container_width=True)

    with st.form(key="review_form"):
        st.markdown(f"### Reviewing: `{current_image.name}`")

        condition = st.radio("Condition:", ["Normal", "Scar", "Edema", "Infection", "Others"], horizontal=True)
        confidence = st.radio("Confidence in your assessment:", ["Low", "Moderate", "High"], horizontal=True)

        st.markdown("🧠 *If there is any overlap or acceptable margin of error, describe briefly:*")
        margin_note = st.text_area(
            "Example: 'Scar with mild edema – acceptable if labeled as Edema.'",
            placeholder="Write margin of acceptable misclassification or notes (optional)",
            height=80
        )

        feedback = st.text_area(
            "💬 Any feedback about image quality, visibility, or clinical ambiguity (optional):",
            placeholder="Example: 'Image slightly blurred – visibility reduced.'",
            height=80
        )

        submit = st.form_submit_button("✅ Submit Review")

        if submit:
            new_data = {
                "Reviewer": reviewer,
                "ImageName": current_image.name,
                "Condition": condition,
                "Confidence": confidence,
                "MarginOfErrorNote": margin_note.strip() if margin_note else "",
                "Feedback": feedback.strip() if feedback else ""
            }

            df_new = pd.DataFrame([new_data])
            df_new.to_csv(REVIEWER_FILE, mode='a', header=not REVIEWER_FILE.exists(), index=False)
            df_new.to_csv(MASTER_FILE, mode='a', header=not MASTER_FILE.exists(), index=False)

            st.success(f"✅ Saved review for `{current_image.name}`")
            st.rerun()

# ---------------- Edit Previous Reviews ----------------
else:
    if reviewed.empty:
        st.info("No reviews found yet. Please review some images first.")
        st.stop()

    st.markdown("### ✏️ Edit or Update Your Previous Reviews")

    selected_image = st.selectbox(
        "Select an image to edit:",
        reviewed["ImageName"].tolist()
    )

    prev = reviewed[reviewed["ImageName"] == selected_image].iloc[0]

    st.image(Image.open(IMAGE_FOLDER / selected_image), caption=selected_image, use_container_width=True)

    with st.form(key="edit_form"):
        condition = st.radio(
            "Condition:",
            ["Normal", "Scar", "Edema", "Infection", "Others"],
            horizontal=True,
            index=["Normal", "Scar", "Edema", "Infection", "Others"].index(prev["Condition"])
        )

        confidence = st.radio(
            "Confidence in your assessment:",
            ["Low", "Moderate", "High"],
            horizontal=True,
            index=["Low", "Moderate", "High"].index(prev["Confidence"])
        )

        margin_note = st.text_area(
            "Margin of acceptable misclassification:",
            value=prev.get("MarginOfErrorNote", ""),
            height=80
        )

        feedback = st.text_area(
            "Feedback or comments:",
            value=prev.get("Feedback", ""),
            height=80
        )

        update = st.form_submit_button("💾 Update Review")

        if update:
            idx = reviewed[reviewed["ImageName"] == selected_image].index[0]
            reviewed.loc[idx, ["Condition", "Confidence", "MarginOfErrorNote", "Feedback"]] = [
                condition, confidence, margin_note.strip(), feedback.strip()
            ]

            reviewed.to_csv(REVIEWER_FILE, index=False)
            # Rebuild master file to stay consistent
            all_files = list(DATA_FOLDER.glob("reviews_*.csv"))
            merged = pd.concat([pd.read_csv(f) for f in all_files if f.name != "reviews_master.csv"], ignore_index=True)
            merged.to_csv(MASTER_FILE, index=False)

            st.success(f"✅ Updated review for `{selected_image}`")
            st.rerun()
