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

# ----------------- SELECT LANGUAGE -----------------
chosen_lang = st.sidebar.selectbox("Choose Language", list(languages.keys()))
translator = Translator(to_lang=languages[chosen_lang])

# ----------------- TITLE -----------------
st.title("📜 Meena - Your Legal Akka")
st.subheader(
    translator.translate(
        "Upload a legal document and get a simplified interpretation:"
    )
)

# ----------------- API KEY -----------------
# Replace this with your key
genai.configure(api_key="AIzaSyBAuJ3FRYpSHKOTEZilI1IoD9xAL4mje-Q")

model = genai.GenerativeModel("gemini-1.5-flash-latest")

model_behavior = """
You are a legal expert in Indian law.
Interpret uploaded legal documents clearly and simply.
Do NOT answer general legal questions.
Only interpret what is inside the uploaded document.
"""

# ----------------- FILE UPLOAD -----------------
uploaded_file = st.file_uploader("Upload JPG, PNG, or PDF", type=["jpg", "png", "pdf"])
prompt = st.text_input(translator.translate("Enter your question or context for the document"))
submit = st.button(translator.translate("Upload & Interpret"))

# ----------------- FUNCTIONS -----------------
def extract_text_from_pdf(uploaded_pdf):
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
        return "".join([page.get_text() for page in doc])


def get_image_bytes(uploaded_image):
    return {
        "mime_type": uploaded_image.type,
        "data": uploaded_image.getvalue()
    }


def get_response(content):
    response = model.generate_content(
        [model_behavior, content]
    )
    return response.text


# ----------------- PROCESS -----------------
if submit:
    if uploaded_file is None or prompt.strip() == "":
        st.error(translator.translate("Please upload a file and enter your prompt."))
    else:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        response_text = ""

        # ----------------- IMAGE -----------------
        if file_ext in ["jpg", "png"]:
            st.image(Image.open(uploaded_file), caption="Uploaded Image", use_column_width=True)
            img_data = get_image_bytes(uploaded_file)

            full_prompt = {
                "image": img_data,
                "text": prompt
            }

            response_text = get_response(full_prompt)

        # ----------------- PDF -----------------
        elif file_ext == "pdf":
            st.info(translator.translate("PDF uploaded. Extracting and interpreting..."))

            extracted_text = extract_text_from_pdf(uploaded_file)

            full_prompt = f"""
Document Text:
{extracted_text}

User Question:
{prompt}
"""

            response_text = get_response(full_prompt)

        else:
            st.error(translator.translate("Unsupported file format."))
            st.stop()

        translated_output = translator.translate(response_text)

        st.subheader(translator.translate("Meena's Interpretation:"))
        st.write(translated_output)
