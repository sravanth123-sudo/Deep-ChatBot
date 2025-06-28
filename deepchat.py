import streamlit as st
import requests
import os
import speech_recognition as sr
from io import BytesIO

# Load API key from Streamlit Secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]

# API Configuration
url = "https://openrouter.ai/api/v1/chat/completions"
model = "deepseek/deepseek-chat-v3-0324:free"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Streamlit Configuration
st.set_page_config(page_title="Enhanced Chatbot", layout="wide")
st.title("🤖 My Enhanced Chatbot")
st.sidebar.title("Navigation")
st.sidebar.markdown("""
- 📂 **New Chat**
- 🔍 **Search Chats**
- 📚 **Library**
""")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_response" not in st.session_state:
    st.session_state.file_response = None

# Helper Functions
def transcribe_audio(file):
    """Transcribe audio using SpeechRecognition."""
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(BytesIO(file.read()))
    with audio_file as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def ask_openai(question, chat_history):
    """Fetch response from OpenRouter AI."""
    payload = {
        "model": model,
        "messages": chat_history
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

# Sidebar: File Upload
st.sidebar.header("Upload Files")
uploaded_file = st.sidebar.file_uploader("Upload a File", type=["txt", "pdf", "docx", "csv"])
if uploaded_file:
    st.sidebar.info("📄 File uploaded! You can ask questions about its content.")

# Main Chat Layout
st.write("---")
chat_container = st.container()

# User Input Section
st.write("---")
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("Your Question:", placeholder="Type your question here...")
    voice_input = st.file_uploader("Upload Voice Question (MP3/WAV):", type=["mp3", "wav"])
    submitted = st.form_submit_button("Send")

if submitted:
    # Process User Input
    if voice_input:
        transcription = transcribe_audio(voice_input)
        user_input = f"[Voice Input] {transcription}"

    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # RAG Approach: Combine file content and user query
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        st.session_state.file_response = f"The uploaded file contains: {file_content[:200]}..."
        combined_context = f"{st.session_state.file_response}\n\nUser Query: {user_input}"
    else:
        combined_context = user_input

    # Query OpenRouter
    try:
        response = ask_openai(combined_context, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    except Exception as e:
        response = f"⚠️ Error: {str(e)}"
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display Chat Messages
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f"<div style='background-color: #e8f4ff; padding: 10px; border-radius: 10px; margin-bottom: 5px; text-align: right;'>"
                f"<b>You:</b> {message['content']}</div>",
                unsafe_allow_html=True
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 5px;'>"
                f"<b>Bot:</b> {message['content']}</div>",
                unsafe_allow_html=True
            )
