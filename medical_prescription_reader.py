import streamlit as st
import cv2
import pytesseract
import tempfile
import spacy
from PIL import Image
import numpy as np

# Load SciSpacy model
@st.cache_resource
def load_model():
    return spacy.load("en_core_sci_md")  # Or use med7 if installed

nlp = load_model()

# Function to extract text using Tesseract
def extract_text(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thresh)
    return text

# Function to extract medicine-related entities
def extract_medicines(text):
    doc = nlp(text)
    medicines = []
    for ent in doc.ents:
        if ent.label_.lower() in ["drug", "chemical", "treatment"]:
            medicines.append((ent.text, ent.label_))
    return medicines

st.title("🩺 AI Prescription Reader (Open Source)")

uploaded_file = st.file_uploader("Upload a handwritten medical prescription image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Prescription", use_column_width=True)

    with st.spinner("🔍 Extracting text..."):
        text = extract_text(image)
        st.subheader("📜 Extracted Text")
        st.text(text)

        meds = extract_medicines(text)
        st.subheader("💊 Detected Medicines")
        if meds:
            for med in meds:
                st.markdown(f"- **{med[0]}** ({med[1]})")
        else:
            st.warning("No medicines detected. Try with a clearer image or use a typed prescription.")
