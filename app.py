import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import os
from translate import Translator
import google.generativeai as genai

# ----------------- CONFIGURE PAGE -----------------
st.set_page_config(page_title="Meena - Your Legal Akka")

# ----------------- ALLOW ALL ORIGINS (SAFE MODE) -----------------
from streamlit.web.server.websocket_headers import _get_websocket_headers

def allow_all_origins():
    def patched_get_headers():
        headers = _get_websocket_headers()
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "*"
        return headers

    st.web.server.websocket_headers._get_websocket_headers = patched_get_headers

allow_all_origins()

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
    "Odia": "or",
}

# ----------------- LANGUAGE SELECTOR -----------------
chosen_lang = st.sidebar.selectbox("Choose Language", list(languages.keys()))
translator = Translator(to_lang=languages[chosen_lang])

# ----------------- SAFE TRANSLATOR WRAPPER -----------------
def safe_translate(translator, text):
    try:
        return translator.translate(text)
    except:
        return text  # fallback if same language or API error

# Shortcut: t("text") will always be safe
def t(text):
    if chosen_lang == "English":
        return text
    return safe_translate(_

