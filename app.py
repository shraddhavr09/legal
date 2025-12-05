import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(page_title="Meena - Legal Akka", page_icon="📜", layout="centered")

# Load API key
genai.configure(api_key=st.secrets["AIzaSyBAuJ3FRYpSHKOTEZilI1IoD9xAL4mje-Q"])

# Gemini Studio model
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------------
# SAFE TRANSLATE FUNCTION
# ------------------------------
def safe_translate(text, src, dest, translator):
    if src == dest:
        return text
    try:
        return translator(text, src=src, dest=dest)
    except:
        return text

# ------------------------------
# SIMPLE TRANSLATOR USING GOOGLE TTS + MODEL
# ------------------------------
def translate_text(text, target_lang):
    if target_lang == "English":
        return text
    
    prompt = f"Translate this into {target_lang}, without adding anything: {text}"
    out = model.generate_content(prompt)
    return out.text

# ------------------------------
# EXTRACT TEXT FROM PDF
# ------------------------------
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# ------------------------------
# INTERPRET LEGAL TEXT
# ------------------------------
def interpret_legal_text(text, user_prompt):
    prompt = f"""
You are Meena, a legal document interpreter.

RULES:
- ONLY interpret the uploaded document content.
- Do NOT use outside legal knowledge.
- DO NOT give legal advice.
- Summarize in simple language.
- Identify: obligations, rights, timelines, penalties, key entities.

USER QUESTION:
{user_prompt}

DOCUMENT CONTENT:
{text}
"""

    response = model.generate_content(prompt)
    return response.text

# ------------------------------
# UI
# ------------------------------
st.title("📜 Meena - Your Legal Akka")

# LANGUAGE SELECTOR
language = st.selectbox("Choose Language", 
                        ["English", "Hindi", "Kannada", "Tamil", "Malayalam", "Telugu"])

# FILE UPLOAD
uploaded = st.file_uploader("Upload a legal PDF document", type=["pdf"])

# USER QUESTION
st.subheader("Ask Meena")
user_prompt = st.text_area("Ask anything about the uploaded legal document:")

output = ""

# ------------------------------
# PROCESSING LOGIC
# ------------------------------
if uploaded and st.button("Interpret Document"):
    with st.spinner("Extracting and interpreting…"):
        extracted = extract_pdf_text(uploaded)
        interpreted = interpret_legal_text(extracted, user_prompt)
        output = translate_text(interpreted, language)

    st.subheader("🔍 Interpretation")
    st.write(output)

    # ------------------------------
    # READ ALOUD (AUDIO)
    # ------------------------------
    if st.button("🔊 Read Aloud"):
        with st.spinner("Generating audio…"):
            audio_response = model.generate_content(
                contents=[output],
                generation_config={"response_mime_type": "audio/mp3"}
            )
            st.audio(audio_response.audio, format="audio/mp3")

# END


    
