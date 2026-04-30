import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from deep_translator import GoogleTranslator
import cv2
from gtts import gTTS

# ------------------ SESSION STATE ------------------
if "processed" not in st.session_state:
    st.session_state.processed = False

if "detected_text" not in st.session_state:
    st.session_state.detected_text = ""

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# ------------------ UI ------------------
st.set_page_config(page_title="VocalVision AI", layout="centered")

st.markdown("""
<style>
.main-title {
    text-align:center;
    font-size:30px;
    font-weight:bold;
    color:#00d4ff;
}
.sub {
    text-align:center;
    color:gray;
}
.stButton>button {
    background-color:#00d4ff;
    color:black;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 VocalVision AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Read • Translate • Speak from Images</div>', unsafe_allow_html=True)

st.markdown("---")

# ------------------ LANGUAGES ------------------
ocr_display = ["English", "Tamil", "Hindi"]
ocr_map = {
    "English": ['en'],
    "Tamil": ['en','ta'],
    "Hindi": ['en','hi']
}

translate_display = ["English", "Tamil", "Hindi", "French", "German"]
translate_map = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

ocr_choice = st.selectbox("📌 OCR Language", ocr_display)
target_choice = st.selectbox("🌍 Translate To", translate_display)

target_lang = translate_map[target_choice]

reader = easyocr.Reader(ocr_map[ocr_choice], gpu=False)

# ------------------ UPLOAD ------------------
uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg","png","jpeg"])

# ------------------ AUDIO ------------------
def speak(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("voice.mp3")

        audio_file = open("voice.mp3", "rb")
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.error(f"Audio Error: {e}")

# ------------------ PROCESS ------------------
if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="📷 Uploaded Image")

    if st.button("🚀 Process Image"):

        img = np.array(image)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2, fy=2)

        results = reader.readtext(resized)

        detected_text = ""

        for item in results:
            # FIX unpack error
            if len(item) == 3:
                bbox, text, prob = item
            else:
                bbox, text = item
                prob = 1.0

            if prob > 0.4:
                detected_text += text + " "

        try:
            translated = GoogleTranslator(
                source='auto',
                target=target_lang
            ).translate(detected_text)
        except:
            translated = "Translation failed"

        # SAVE STATE
        st.session_state.detected_text = detected_text
        st.session_state.translated_text = translated
        st.session_state.processed = True

# ------------------ DISPLAY ------------------
if st.session_state.processed:

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Original")
        st.write(st.session_state.detected_text)

    with col2:
        st.subheader("🌍 Translated")
        st.write(st.session_state.translated_text)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("🔊 Speak Original"):
            speak(st.session_state.detected_text, "en")

    with col4:
        if st.button("🔊 Speak Translated"):
            speak(st.session_state.translated_text, target_lang)