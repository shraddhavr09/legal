import os
import streamlit as st
import google.generativeai as genai
import base64
from translate import Translator
from PyPDF2 import PdfReader
from PIL import Image
import io

# ------------------------------------------------------------------------------
# STREAMLIT CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Meena – Legal Document Interpreter",
    layout="wide"
)

st.title("Meena – Legal Document Interpreter")

# ------------------------------------------------------------------------------
# GEMINI CONFIG (Render environment variable)
# ------------------------------------------------------------------------------
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------------------------------------------------------------
# LANGUAGES
# ------------------------------------------------------------------------------
languages = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Tamil": "ta",
    "Telugu": "te",
}

chosen_lang = st.selectbox("Choose your language", list(languages.keys()))
src = "en"
tgt = languages[chosen_lang]

translator = Translator(from_lang=src, to_lang=tgt)

# ------------------------------------------------------------------------------
# SAFE TRANSLATION WRAPPER
# ------------------------------------------------------------------------------
def safe_translate(text):
    try:
        if chosen_lang == "English":
            return text
        return translator.translate(text)
    except:
        return text  # fallback if translation fails

def t(text):
    return safe_translate(text)

# ------------------------------------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------------------------------------
uploaded = st.file_uploader(t("Upload a legal document"), type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_pdf(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text.strip()

def extract_text_from_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    prompt = f"Extract all text from this image.\n<image>{img_b64}</image>"
    
    result = model.generate_content(prompt)
    if hasattr(result, "text"):
        return result.text
    return ""

# ------------------------------------------------------------------------------
# INTERPRETATION LOGIC
# ------------------------------------------------------------------------------
def interpret_legal_text(raw_text):
    prompt = f"""
You are 'Meena', a legal document interpreter. 
You must *only* interpret uploaded content. Do NOT answer general law questions.

TASK:
- Simplify the legal language
- Explain meaning in normal words
- Provide bullet points
- Keep everything accurate
- No legal advice
- No external info

Document:
{raw_text}
"""

    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else "No response."

# ------------------------------------------------------------------------------
# MAIN LOGIC
# ------------------------------------------------------------------------------
if uploaded:
    file_bytes = uploaded.read()

    if uploaded.type == "application/pdf":
        extracted = extract_text_from_pdf(file_bytes)
    else:
        extracted = extract_text_from_image(file_bytes)

    if extracted.strip() == "":
        st.error(t("Could not extract readable text. Try a clearer file."))
    else:
        st.subheader(t("Extracted Text"))
        st.write(extracted)

        with st.spinner(t("Interpreting using AI...")):
            output = interpret_legal_text(extracted)

        st.subheader(t("Simplified Interpretation"))
        st.write(output)

else:
    st.info(t("Upload a legal document to get started."))
