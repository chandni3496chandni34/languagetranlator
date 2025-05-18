import os

# Avoid MKL duplicate error
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import streamlit as st
import cv2
import easyocr
from gtts import gTTS
from playsound import playsound
from googletrans import LANGUAGES,Translator
import speech_recognition as sr


translator = Translator()
dic = {
    'albanian':'sq',  
       'amharic': 'am','arabic': 'ar', 
       'armenian': 'hy', 'azerbaijani': 'az',  
       'basque': 'eu', 'belarusian': 'be', 
       'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 
       'bg', 'catalan': 'ca', 'cebuano': 
       'ceb', 'chichewa': 'ny', 'chinese (simplified)': 
       'zh-cn', 'chinese (traditional)': 
       'zh-tw', 'corsican': 'co', 'croatian':'hr', 
       'czech': 'cs', 'danish': 'da', 'dutch': 
       'nl', 'english': 'en', 'esperanto': 'eo',  
       'estonian': 'et', 'filipino': 'tl', 'finnish': 
       'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 
       'gl', 'georgian': 'ka', 'german': 
       'de', 'greek': 'el', 'gujarati': 'gu', 
       'haitian creole': 'ht', 'hausa': 'ha', 
       'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 
       'hi', 'hmong': 'hmn', 'hungarian': 
       'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian':  
       'id', 'irish': 'ga', 'italian': 
       'it', 'japanese': 'ja', 'javanese': 'jw', 
       'kannada': 'kn', 'kazakh': 'kk', 'khmer': 
       'km', 'korean': 'ko', 'kurdish (kurmanji)':  
       'ku', 'kyrgyz': 'ky', 'lao': 'lo', 
       'latin': 'la', 'latvian': 'lv', 'lithuanian':
       'lt', 'luxembourgish': 'lb', 
       'macedonian': 'mk', 'malagasy'
        :'mg', 'malay':
       'ms', 'malayalam': 'ml', 'maltese': 
       'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 
       'mn', 'myanmar (burmese)': 'my', 
       'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 
       'pashto': 'ps', 'persian': 'fa', 
       'polish': 'pl', 'portuguese': 'pt', 'punjabi': 
       'pa', 'romanian': 'ro', 'russian': 
       'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 
       'serbian': 'sr', 'sesotho': 'st', 
       'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 
       'slovak': 'sk', 'slovenian': 'sl', 
       'somali': 'so', 'spanish':'es', 'sundanese':
       'su', 'swahili': 'sw', 'swedish': 
       'sv', 'tajik': 'tg', 'tamil': 'ta', 'telugu':
       'te', 'thai': 'th', 'turkish': 
       'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 
       'ug', 'uzbek':  'uz', 
       'vietnamese': 'vi', 'welsh':'cy', 'xhosa': 'xh', 
       'yiddish': 'yi', 'yoruba': 
       'yo', 'zulu': 'zu'
}
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        st.write("Recognizing...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.write("Sorry, I could not understand your speech.")
        return ""
    except sr.RequestError:
        st.write("Sorry, I am unable to process your request at the moment.")
        return ""

import tempfile

def speak_text(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    # Save the audio to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_file_path = temp_file.name
        tts.save(temp_file_path)
    # Play the audio
    playsound(temp_file_path)
    os.remove(temp_file_path)

def translate_text(input_text, dest_language):
    translation = translator.translate(input_text, dest=dest_language)
    return translation.text

def recognize_text(img):
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR with English language
    results = reader.readtext(img)
    
    recognized_text = ''
    for (bbox, text, score) in results:
        if score > 0.25:
            recognized_text += text + ' '  # Concatenate recognized text
    
    return recognized_text

def use_camera():
    dest_language = st.selectbox('Select target language', list(dic.keys()))
    cap = cv2.VideoCapture(0)
    
    if st.button("Start Camera"):
        ret, frame = cap.read()
        if ret:
            img_path = 'captured_image.jpg'
            cv2.imwrite(img_path, frame)
            recognized_text = recognize_text(frame)
            if recognized_text:
                translated_text = translate_text(recognized_text, dic[dest_language])
                speak_text(translated_text, dic[dest_language])
                st.write("Recognized Text:", recognized_text)
                st.write("Translated Text:", translated_text)
                # Display the captured image with annotations
                annotated_img = annotate_image(frame, recognized_text)
                st.image(annotated_img, channels="BGR", caption="Annotated Image")


    cap.release()
    cv2.destroyAllWindows()
def annotate_image(img, text):
    # Annotate the image with recognized text and bounding boxes
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img)
    
    for (bbox, text, score) in results:
        if score > 0.25:
            top_left = tuple(bbox[0])
            bottom_right = tuple(bbox[2])
            cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(img, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    return img

def main():
    st.title("Language Translator and Text Recognizer")
    operation_mode = st.sidebar.radio("Select operation mode:", ["Translate Text", "Translate Speech", "Use Camera"])
    #operation_mode = st.sidebar.radio("Select operation mode:", ["Translate Text", "Use Camera"])

    if operation_mode == "Translate Text":
        input_text = st.text_area('Enter text to translate')
        dest_language = st.selectbox('Select target language', list(dic.keys()))

        if st.button('Translate'):
            translated_text = translate_text(input_text, dic[dest_language])
            speak_text(translated_text, dic[dest_language])
            st.write('Translated text:', translated_text)
    elif operation_mode == "Translate Speech":
        dest_language = st.selectbox('Select target language', list(dic.keys()))

        if st.button("Start Recording"):
            input_text = recognize_speech()
            if input_text:
                translated_text = translate_text(input_text, dest_language)
                speak_text(translated_text, dic[dest_language])  # Speak the translated text
                st.write("You said:", input_text)
                st.write("Translated text:", translated_text)

    elif operation_mode == "Use Camera":
        use_camera()

if __name__ == '__main__':
    main()
