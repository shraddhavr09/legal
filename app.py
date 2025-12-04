import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
from translate import Translator
import google.generativeai as genai

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Meena - Your Legal Akka")

# ----------------- LANGUAGES -----------------
languages = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Bengali": "bn",
    "Punjabi": "pa",
    "Odia": "or"
}

# ----------------- SELECT LANGUAGE -----------------
chosen_lang = st.sidebar.selectbox("Choose Language", list(languages.keys()))
lang_code = languages[chosen_lang]

translator = Translator(to_lang=lang_code)

# ----------------- SAFE TRANSLATION WRAPPER -----------------
def safe_translate(text):
    try:
        # If chosen language is English → don't translate
        if lang_code == "en":
            return text
        return translator.translate(text)
    except:
        # if translation fails → return original text
        return text

# ----------------- TITLE -----------------
st.title("📜 Meena - Your Legal Akka")
st.subheader(safe_translate("Upload a legal document and get a simplified interpretation:"))

# ----------------- API KEY -----------------
genai.configure(api_key="AIzaSyBAuJ3FRYpSHKOTEZilI1IoD9xAL4mje-Q")
model = genai.GenerativeModel("gemini-1.5-flash-latest")

model_behavior = """
You are a legal expert in Indian law.
Interpret uploaded legal documents clearly and simply.
Do NOT answer general legal questions.
Only interpret content inside the uploaded document.
"""

# ----------------- FILE INPUT -----------------
uploaded_file = st.file_uploader("Upload JPG, PNG, or PDF", type=["jpg", "png", "pdf"])
prompt = st.text_input(safe_translate("Enter your question or context for the document"))
submit = st.button(safe_translate("Upload & Interpret"))

# ----------------- HELPERS -----------------
def extract_text_from_pdf(uploaded_pdf):
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
        return "".join([page.get_text() for page in doc])

def get_image_bytes(uploaded_image):
    return {
        "mime_type": uploaded_image.type,
        "data": uploaded_image.getvalue()
    }

def get_response(content):
    response = model.generate_content([model_behavior, content])
    return response.text

# ----------------- MAIN PROCESS -----------------
if submit:
    if uploaded_file is None or prompt.strip() == "":
        st.error(safe_translate("Please upload a file and enter your prompt."))
    else:
        ext = uploaded_file.name.split(".")[-1].lower()

        # -------- IMAGE --------
        if ext in ["jpg", "png"]:
            st.image(Image.open(uploaded_file), caption="Uploaded Image", use_column_width=True)
            img_bytes = get_image_bytes(uploaded_file)

            full_prompt = {"image": img_bytes, "text": prompt}

            output = get_response(full_prompt)

        # -------- PDF --------
        elif ext == "pdf":
            st.info(safe_translate("PDF uploaded. Extracting and interpreting..."))

            extracted = extract_text_from_pdf(uploaded_file)
            full_prompt = f"Document:\n{extracted}\n\nUser Question:\n{prompt}"

            output = get_response(full_prompt)

        else:
            st.error(safe_translate("Unsupported file format."))
            st.stop()

        # -------- FINAL OUTPUT --------
        translated_output = safe_translate(output)

        st.subheader(safe_translate("Meena's Interpretation:"))
        st.write(translated_output)
