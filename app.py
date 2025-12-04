import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
from translate import Translator
import google.generativeai as genai

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

# ----------------- LANGUAGE SELECT -----------------
chosen_lang = st.sidebar.selectbox("Choose Language", list(languages.keys()))
translator = Translator(to_lang=languages[chosen_lang])

# ----------------- TITLE -----------------
st.title("📜 Meena - Your Legal Akka")
st.subheader(
    translator.translate("Upload a legal document and get a simplified interpretation:")
)

# ----------------- API KEY + MODEL -----------------
genai.configure(api_key="AIzaSyBAuJ3FRYpSHKOTEZilI1IoD9xAL4mje-Q")

# FIXED MODEL (This prevents your 404 error)
model = genai.GenerativeModel("models/gemini-1.5-flash-001")

model_behavior = """
You are a legal expert in Indian law.
Interpret ONLY the uploaded legal document clearly and simply.
Do not answer general legal questions.
Respond based strictly on the provided document text.
"""

# ----------------- FILE INPUT -----------------
uploaded_file = st.file_uploader("Upload JPG, PNG, or PDF", type=["jpg", "png", "pdf"])
prompt = st.text_input(translator.translate("Enter your question or context for the document"))
submit = st.button(translator.translate("Upload & Interpret"))

# ----------------- FUNCTIONS -----------------
def extract_text_from_pdf(file_obj):
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return "\n".join(pages)

def get_image_bytes(img):
    return {
        "mime_type": img.type,
        "data": img.getvalue()
    }

def get_response(model, behavior, content):
    response = model.generate_content([behavior, content])
    return response.text

# ----------------- MAIN PROCESS -----------------
if submit:

    if uploaded_file is None:
        st.error(translator.translate("Please upload a file."))
        st.stop()

    if prompt.strip() == "":
        st.error(translator.translate("Please enter your prompt."))
        st.stop()

    file_ext = uploaded_file.name.split(".")[-1].lower()
    response_text = ""

    # ----------------- IMAGE INPUT -----------------
    if file_ext in ["jpg", "png"]:
        st.image(Image.open(uploaded_file), caption="Uploaded Image", use_column_width=True)
        img_data = get_image_bytes(uploaded_file)
        content = {
            "type": "input_image",
            "image": img_data
        }
        response_text = get_response(model, model_behavior, content)

    # ----------------- PDF INPUT -----------------
    elif file_ext == "pdf":
        st.info(translator.translate("PDF uploaded. Extracting and interpreting..."))
        extracted_text = extract_text_from_pdf(uploaded_file)
        full_prompt = f"Document:\n{extracted_text}\n\nUser Prompt:\n{prompt}"
        response_text = get_response(model, model_behavior, full_prompt)

    else:
        st.error(translator.translate("Unsupported file format."))
        st.stop()

    # ----------------- OUTPUT -----------------
    translated = translator.translate(response_text)
    st.subheader(translator.translate("Meena's Interpretation:"))
    st.write(translated)


