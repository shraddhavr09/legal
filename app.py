import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import io # Added for in-memory file handling
import wave # Added for WAV file creation
import struct # Added for handling raw PCM bytes

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(page_title="Meena - Your Legal Advisor", page_icon="📜", layout="centered")

# ------------------------------
# LOAD API KEY FROM ENV VARIABLE
# ------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # Ensure the error message is visible if the key is missing
    st.error("API Key not found. Please set the GEMINI_API_KEY environment variable.")
    # Exit script early if no key is found to prevent further errors
    st.stop()
else:
    genai.configure(api_key=API_KEY)

# Gemini Model for TEXT/CHAT/TRANSLATION
# FIX: Changed the model from "models/gemini-1.5-flash-001" to the currently supported alias "gemini-2.5-flash".
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# TTS Model Configuration
TTS_MODEL_NAME = "gemini-2.5-flash-preview-tts"
TTS_VOICE = "Kore" # A clear, firm voice
SAMPLE_RATE = 16000 # Sample rate for the PCM data

# ------------------------------
# TRANSLATION USING GEMINI
# ------------------------------
def translate_text(text, target_lang):
    if target_lang == "English":
        return text
    
    # Using the fixed global model variable
    prompt = f"Translate this into {target_lang}, without adding anything: {text}"
    out = model.generate_content(prompt)
    return out.text

# ------------------------------
# EXTRACT TEXT FROM PDF
# ------------------------------
def extract_pdf_text(uploaded_file):
    """Extracts text content from an uploaded PDF file."""
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

# ------------------------------
# INTERPRET LEGAL TEXT
# ------------------------------
def interpret_legal_text(text, user_prompt):
    """Generates an interpretation of the legal text based on the user's prompt."""
    prompt = f"""
You are Meena, a legal document interpreter.

RULES:
- ONLY interpret the uploaded document.
- Do NOT add external legal knowledge.
- Do NOT give legal advice.
- Summarize in simple language.
- Extract obligations, rights, timelines, penalties, key entities.

USER QUESTION:
{user_prompt}

DOCUMENT CONTENT:
{text}
"""
    # Using the fixed global model variable
    response = model.generate_content(prompt)
    return response.text

# ------------------------------
# TTS GENERATION (Read Aloud)
# ------------------------------
def generate_tts_audio(text):
    """Generates TTS audio from raw PCM and converts it to WAV format."""
    try:
        # Use a new model instance for the dedicated TTS model
        tts_model = genai.GenerativeModel(TTS_MODEL_NAME)
        
        # API request configuration for AUDIO modality
        config = genai.types.GenerateContentConfig(
            response_modalities=['AUDIO'],
            speech_config=genai.types.SpeechConfig(
                voice_config=genai.types.VoiceConfig(
                    prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                        voice_name=TTS_VOICE
                    )
                )
            )
        )
        
        # Call the TTS model
        response = tts_model.generate_content(
            contents=[text],
            config=config
        )
        
        # Find the part containing audio data (mimeType audio/L16 for signed PCM 16-bit)
        audio_part = next((
            part for part in response.candidates[0].content.parts 
            if part.inline_data and part.inline_data.mime_type.startswith('audio/L16')
        ), None)

        if not audio_part:
            st.error("Could not find expected PCM audio data in the response.")
            return None

        # The SDK decodes the base64 data to raw bytes
        pcm_bytes = audio_part.inline_data.data
        
        # Unpack raw signed 16-bit PCM bytes into an array of short integers
        num_samples = len(pcm_bytes) // 2
        # Use little-endian '<' signed short 'h' format
        pcm_data = struct.unpack(f'<{num_samples}h', pcm_bytes)
        
        # Convert PCM to WAV format using an in-memory buffer
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1) # Mono
                wav_file.setsampwidth(2) # 16-bit PCM
                wav_file.setframerate(SAMPLE_RATE)
                # Write the raw 16-bit signed PCM data back into the WAV file structure
                wav_file.writeframes(b''.join(struct.pack('<h', sample) for sample in pcm_data))
            
            # Return the complete WAV file bytes
            return wav_io.getvalue()

    except Exception as e:
        st.error(f"Error generating audio: {e}")
        # In case of an API error (e.g., rate limit, invalid voice), show it.
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            st.error(f"API Debug Info: {e.response.text}")
        return None


# ------------------------------
# UI
# ------------------------------
st.title("📜 Meena - Your Legal Akka")

# LANGUAGE SELECTOR
language = st.selectbox(
    "Choose Language",
    ["English", "Hindi", "Kannada", "Tamil", "Malayalam", "Telugu"]
)

# FILE UPLOAD
uploaded = st.file_uploader("Upload a legal PDF document", type=["pdf"])

# USER QUESTION
st.subheader("Ask Meena")
user_prompt = st.text_area("Ask anything about the uploaded legal document:")

# Initialize output state so the Read Aloud button can access it after interpretation
if 'output' not in st.session_state:
    st.session_state.output = ""

# ------------------------------
# PROCESSING LOGIC
# ------------------------------
if uploaded and st.button("Interpret Document"):
    if not user_prompt:
        st.warning("Please enter a question for Meena to interpret the document.")
    else:
        with st.spinner("Extracting and interpreting…"):
            extracted = extract_pdf_text(uploaded)
            interpreted = interpret_legal_text(extracted, user_prompt)
            st.session_state.output = translate_text(interpreted, language)

        st.subheader("🔍 Interpretation")
        st.markdown(st.session_state.output)

# ------------------------------
# READ ALOUD BUTTON
# ------------------------------
# Show the Read Aloud button only if interpretation has successfully run
if st.session_state.output:
    if st.button("🔊 Read Aloud"):
        with st.spinner(f"Generating audio in {language} using voice {TTS_VOICE}..."):
            # Use the stored output
            wav_bytes = generate_tts_audio(st.session_state.output)
            
            if wav_bytes:
                # st.audio can play the in-memory WAV bytes
                st.audio(wav_bytes, format='audio/wav')

# ------------------------------
# ADDITIONAL NOTES
# ------------------------------
st.sidebar.markdown("""
---
**Note on Model:**
The model name
