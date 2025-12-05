import streamlit as st
import google.generativeai as genai
from translate import Translator
import pdfplumber
from PIL import Image
import io
import os

# --------------------------
# CONFIG
# --------------------------
st.set_page_config(page_title="Meena - Legal Akka", layout="centered")

# Your Gemini API Key (Studio)
GENAI_API_KEY = "YOUR_GEMINI_API_KEY"

genai.configure(api_key=GENAI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"  # VALID FOR GOOGLE AI STUDIO

model = genai.GenerativeModel(MODEL_NAME)

# --------------------------
# SAFE TRANSLATION WRAPPER
# --------------------------
def safe_translate(text, src, dest):
    if src == dest:
        return text

    try:
        translator = Translator(from_lang=src, to_lang=dest)
        return translator.translate(text)
    except Exception:
        return text

# --------------------------
# EXTRACT RAW TEXT FROM PDF
# --------------------------
def extract_pdf_text(uploaded_file):
    full_text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() or ""
    return full_text

# --------------------------
# EXTRACT TEXT FROM IMAGES
# --------------------------
def extract_image_text(uploaded_file):
    img = Image.open(uploaded_file)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")

    response = model.generate_content(
        ["Extract readable text from this image only:",
         {"image": buffered.getvalue()}]
    )
    return response.text

# --------------------------
# LEGAL INTERPRETER
# --------------------------
def interpret_legal_text(text):
    prompt = f"""
You are Meena, a legal document interpreter.

RULES:
- ONLY interpret uploaded content.
- NO legal advice.
- NO external law knowledge.
- Convert complex clauses into simple language.
- Identify: obligations, rights, timelines, penalties, entities.

TEXT TO INTERPRET:
{text}
"""

    response = model.generate_content(prompt)
    return response.text

# --------------------------
# UI LAYOUT
# --------------------------
st.markdown("<h2 style='text-align:center;'>📜 Meena - Your Legal Akka</h2>", unsafe_allow_html=True)

# Language selector
languages = [
    "English", "Hindi", "Kannada", "Malayalam", "Tamil", "Telugu",
    "Marathi", "Gujarati", "Bengali", "Punjabi"
]

st.subheader("Choose Language")
selected_lang = st.selectbox("Language", languages, index=0)

# --------------------------
# FILE UPLOAD
# --------------------------
uploaded_file = st.file_uploader("Upload Legal Document (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.name.lower()

    with st.spinner("Extracting content…"):
        if file_type.endswith(".pdf"):
            extracted = extract_pdf_text(uploaded_file)
        else:
            extracted = extract_image_text(uploaded_file)

    if not extracted.strip():
        st.error("No readable text found.")
    else:
        with st.spinner("Interpreting the legal document…"):
            interpreted = interpret_legal_text(extracted)

        # Translate to selected language
        output = safe_translate(interpreted, "English", selected_lang)

        st.subheader("Result")
        st.write(output)
