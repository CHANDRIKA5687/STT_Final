import streamlit as st
import speech_recognition as sr
from io import BytesIO
from docx import Document
from moviepy.editor import *
import os
import tempfile

# Function to convert speech to text
def speech_to_text(audio_data, timeout=60):
    recognizer = sr.Recognizer()
    with audio_data as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            st.error("Speech recognition timed out. Please try again.")
            return ""
    return text

# Function to convert video to audio
def extract_audio(video_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    video = VideoFileClip(temp_file_path)
    audio_file_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_file_path)
    
    # Close the audio file to ensure it's fully written and closed
    video.close()

    # Delete the temporary video file
    os.unlink(temp_file_path)

    return audio_file_path

# Function to generate Word document
def generate_word_document(text):
    doc = Document()
    doc.add_paragraph(text)
    return doc

# Function for live transcription
def live_transcription():
    st.write("Live Transcription")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Speak something...")
        audio_data = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio_data)
        st.success("Live Transcription Result: " + text)
    except sr.UnknownValueError:
        st.error("Could not understand audio")
    except sr.RequestError as e:
        st.error("Could not request results; {0}".format(e))

def main():
    st.title("Speech to Text Converter")

    option = st.radio("Select transcription option:", ("Upload File", "Live Transcription"))

    if option == "Upload File":
        file_type = st.radio("Select file type:", ("Audio", "Video"))

        if file_type == "Audio":
            file_uploader_label = "Upload an audio file"
            file_types = ["mp3", "wav"]
        else:
            file_uploader_label = "Upload a video file"
            file_types = ["mp4"]

        audio_file = st.file_uploader(file_uploader_label, type=file_types)

        if audio_file:
            if file_type == "Audio":
                st.audio(audio_file, format="audio/wav")
                audio_file_path = audio_file
            else:
                st.video(audio_file)
                audio_file_path = extract_audio(audio_file)

            if st.button("Transcribe"):
                audio_data = sr.AudioFile(audio_file_path)
                text = speech_to_text(audio_data)
                st.text_area("Transcribed Text", value=text, height=200)

                if st.button("Download Word Document"):
                    doc = generate_word_document(text)
                    doc_io = BytesIO()
                    doc.save(doc_io)
                    doc_io.seek(0)
                    st.download_button(
                        label="Download Word Document", data=doc_io, file_name="transcription.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

    elif option == "Live Transcription":
        live_transcription()

if __name__ == "__main__":
    main()
