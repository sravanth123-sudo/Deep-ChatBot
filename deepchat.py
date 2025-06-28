import streamlit as st
import requests
import tempfile
import os
import whisper

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
st.set_page_config(page_title="Personal Chatbot", layout="wide")
st.title("🤖 My Enhanced Chatbot")
st.sidebar.title("Navigation")
st.sidebar.markdown("""
- 📂 **New Chat**
- 🔍 **Search Chats**
- 📚 **Library**
""")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_response" not in st.session_state:
    st.session_state.file_response = None

# Helper Functions
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

def transcribe_audio(file_path):
    """Transcribe audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

# Left Sidebar: Features
st.sidebar.header("Features")
uploaded_file = st.sidebar.file_uploader("Upload a File", type=["txt", "pdf", "docx", "csv"])
if uploaded_file:
    st.sidebar.info("📄 File uploaded! You can ask questions about its content.")

# Main Chat Layout
st.write("---")
chat_container = st.container()

# User Input Section
st.write("---")
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input(
        "Your Question:",
        placeholder="Type your question here...",
        key="user_input"
    )
    voice_input = st.file_uploader("Upload Voice Question (MP3/WAV):", type=["mp3", "wav"])
    submitted = st.form_submit_button("Send")

if submitted:
    # Process User Input
    if voice_input:
        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(voice_input.read())
            voice_path = temp_audio.name

        user_input = transcribe_audio(voice_path)
        os.remove(voice_path)
        st.session_state.chat_history.append({"role": "user", "content": f"[Voice Input] {user_input}"})
    else:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Process File Content (if any)
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        st.session_state.file_response = f"The uploaded file contains: {file_content[:200]}..."

    # RAG Approach
    if st.session_state.file_response:
        combined_context = f"{st.session_state.file_response}\n\nUser Query: {user_input}"
    else:
        combined_context = user_input

    # Query OpenAI
    try:
        response = ask_openai(combined_context, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    except Exception as e:
        response = f"⚠️ Error: {str(e)}"
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display Chat Messages
with chat_container:
    for idx, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.markdown(
                f"<div style='background-color: #e8f4ff; padding: 10px; border-radius: 10px; margin-bottom: 5px; text-align: right;'>"
                f"<b>You:</b> {message['content']} "
                f"<button onclick='editQuestion({idx})'>Edit</button>"
                f"<button onclick='copyQuestion({idx})'>Copy</button>"
                "</div>",
                unsafe_allow_html=True
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 5px;'>"
                f"<b>Bot:</b> {message['content']}</div>",
                unsafe_allow_html=True
            )
