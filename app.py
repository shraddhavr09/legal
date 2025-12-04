import streamlit as st
import google.generativeai as genai
import base64

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(
    page_title="Meena – Legal Document Interpreter",
    layout="wide",
)

# ------------------------------
# API KEY
# ------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ------------------------------
# HELPER: READ UPLOADED FILE
# ------------------------------
def read_file(uploaded_file):
    if uploaded_file is None:
        return None
    content = uploaded_file.read()
    try:
        return content.decode("utf-8")
    except:
        return content.decode("latin-1", errors="ignore")

# ------------------------------
# HELPER: INTERPRET DOCUMENT
# ------------------------------
def interpret_document(doc_text, lang):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are Meena — a legal document interpreter. 
You ONLY interpret the content given.  
You do NOT answer general law questions.
You do NOT give legal advice.
You ONLY explain the uploaded content in simple language.

OUTPUT MUST BE IN: {lang}

Document to interpret:
{doc_text}
"""

    response = model.generate_content(prompt)
    return response.text

# ------------------------------
# HELPER: TRANSLATE
# ------------------------------
def safe_translate(text, source_lang, target_lang):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
Translate the following text from {source_lang} to {target_lang}.
Only translate. Do not add or remove meaning.

Text:
{text}
"""

    response = model.generate_content(prompt)
    return response.text

# ------------------------------
# UI
# ------------------------------
st.title("Meena – Legal Document Interpreter")
st.write("Upload any legal document to get a clear, simple interpretation.")

# Language dropdown
lang = st.selectbox(
    "Choose output language:",
    ["English", "Hindi", "Kannada", "Tamil", "Malayalam", "Telugu", "Bengali"]
)

uploaded_file = st.file_uploader("Upload your legal document", type=["txt", "pdf", "docx"])

# ------------------------------
# PROCESS
# ------------------------------
if uploaded_file:
    st.success("File uploaded successfully!")
    doc_text = read_file(uploaded_file)

    if st.button("Interpret Document"):
        with st.spinner("Interpreting..."):
            interpreted = interpret_document(doc_text, lang)
            st.subheader("Interpreted Meaning:")
            st.write(interpreted)

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("""
<hr>
<div style='text-align:center; opacity:0.7'>
Made by Shraddha – Powered by Gemini
</div>
""", unsafe_allow_html=True)

