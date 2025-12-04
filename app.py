import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
from translate import Translator
import google.generativeai as genai

# ----------------- FIXED: SAFE TRANSLATION -----------------
def safe_translate(translator, text):
    try:
        return translator.translate(text)
    except:
        return text

# ----------------- CONFIGURE PAGE -----------------
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
translator = Translator(to_lang=languages[chosen_lang])

# ----------------- TITLE -----------------
st.title("📜 Meena - Your Legal Akka")
st.subheader(safe_translate(translator,
    "Upload a legal document and get a simplified interpretation:"
))

# ----------------- API KEY -----------------
# If secrets is available on Render, use it.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = "AIzaSyBAuJ3FRYpSHKOTEZilI1IoD9xAL4mje-Q"

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

model_behavior = """
You are a legal expert in Indian law. Interpret uploaded legal documents clearly and simply.
Do not answer general legal questions. Respond only based on the uploaded content.
"""

# ----------------- FILE UPLOAD -----------------
uploaded_file = st.file_uploader("Upload JPG, PNG, or PDF", type=["jpg", "png", "pdf"])
prompt = st.text_input(safe_translate(translator, "Enter your question or context for the document"))
submit = st.button(safe_translate(translator, "Upload & Interpret"))

# ----------------- FUNCTIONS -----------------
def extract_text_from_pdf(uploaded_pdf):
    try:
        with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
            return "".join([page.get_text() for page in doc])
    except:
        return ""

def get_image_bytes(uploaded_image):
    return [{
        "mime_type": uploaded_image.type,
        "data": uploaded_image.getvalue()
    }]

def get_response(model, behavior, content):
    response = model.generate_content([behavior, content])
    return response.text

# ----------------- PROCESS -----------------
if submit:
    if uploaded_file is None or prompt.strip() == "":
        st.error(safe_translate(translator, "Please upload a file and enter your prompt."))
    else:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if file_ext in ["jpg", "png"]:
            st.image(Image.open(uploaded_file), caption="Uploaded Image", use_column_width=True)
            img = get_image_bytes(uploaded_file)[0]
            response_text = get_response(model, model_behavior, img)

        elif file_ext == "pdf":
            st.info(safe_translate(translator, "PDF uploaded. Extracting and interpreting..."))
            extracted = extract_text_from_pdf(uploaded_file)
            full_prompt = f"{extracted}\n\nUser Prompt: {prompt}"
            response_text = get_response(model, model_behavior, full_prompt)

        else:
            st.error(safe_translate(translator, "Unsupported file format."))
            response_text = ""

        translated = safe_translate(translator, response_text)

        st.subheader(safe_translate(translator, "Meena's Interpretation:"))
        st.write(translated)
