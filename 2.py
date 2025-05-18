import os

# Avoid MKL duplicate error
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import streamlit as st
import cv2
import easyocr
from gtts import gTTS
from playsound import playsound
from googletrans import Translator
import speech_recognition as sr
import tempfile


# Language dictionary
LANG_DICT = {
    'english': 'en', 'hindi': 'hi', 'french': 'fr', 'german': 'de',
    'spanish': 'es', 'italian': 'it', 'chinese (simplified)': 'zh-cn',
    'bengali': 'bn', 'tamil': 'ta', 'telugu': 'te', 'japanese': 'ja',
    'korean': 'ko', 'russian': 'ru', 'arabic': 'ar', 'urdu': 'ur',
    'marathi': 'mr', 'gujarati': 'gu', 'malayalam': 'ml', 'punjabi': 'pa',
    # Add more as needed...
}

translator = Translator()

# ---------------------- Core Functions ---------------------- #

def translate_text(text, dest_lang_code):
    return translator.translate(text, dest=dest_lang_code).text

def speak_text(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
        tts.save(tmp_file.name)
        playsound(tmp_file.name)
        os.remove(tmp_file.name)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙 Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand the audio.")
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition.")
    return ""

def recognize_text_from_image(image):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image)
    return ' '.join([text for _, text, score in results if score > 0.25])

def annotate_image(img):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img)
    for (bbox, text, score) in results:
        if score > 0.25:
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(img, text, (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    return img

# ---------------------- Camera Handler ---------------------- #

def use_camera(dest_lang):
    cap = cv2.VideoCapture(0)
    st.write("📸 Press 'Capture' to take a photo.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Failed to grab frame.")
            break

        st.image(frame, channels="BGR")

        if st.button("📷 Capture"):
            recognized_text = recognize_text_from_image(frame)
            if recognized_text:
                translated = translate_text(recognized_text, LANG_DICT[dest_lang])
                speak_text(translated, LANG_DICT[dest_lang])
                st.success("✅ OCR Completed")
                st.write("📝 Recognized Text:", recognized_text)
                st.write("🌐 Translated Text:", translated)
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------------------- Main Streamlit App ---------------------- #

def main():
    st.set_page_config(page_title="Multilingual Translator", layout="centered")
    st.title("🌍 Multilingual Translator")
    mode = st.sidebar.radio("Choose Mode:", ["Translate Text", "Translate Speech", "Use Camera"])
    
    if mode == "Translate Text":
        input_text = st.text_area("Enter text to translate:")
        dest_lang = st.selectbox("Select target language:", list(LANG_DICT.keys()))
        
        if st.button("Translate"):
            translated = translate_text(input_text, LANG_DICT[dest_lang])
            speak_text(translated, LANG_DICT[dest_lang])
            st.success("✅ Translation Complete")
            st.write("🌐 Translated Text:", translated)

    elif mode == "Translate Speech":
        dest_lang = st.selectbox("Select target language:", list(LANG_DICT.keys()))
        
        if st.button("🎤 Start Recording"):
            spoken_text = recognize_speech()
            if spoken_text:
                translated = translate_text(spoken_text, LANG_DICT[dest_lang])
                speak_text(translated, LANG_DICT[dest_lang])
                st.success("✅ Speech Translation Complete")
                st.write("🗣 You Said:", spoken_text)
                st.write("🌐 Translated Text:", translated)

    elif mode == "Use Camera":
        dest_lang = st.selectbox("Select target language:", list(LANG_DICT.keys()))
        if st.button("📷 Start Camera"):
            use_camera(dest_lang)

if __name__ == "__main__":
    main()
