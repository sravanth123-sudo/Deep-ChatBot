import streamlit as st
import requests

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
st.set_page_config(page_title="Personal Chatbot", layout="centered")
st.title("🤖 Havish Chatbot")
st.markdown("Feel free to ask me anything! Let's chat.")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat UI
st.write("---")
chat_container = st.container()

# User Input Section
st.write("---")
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input(
        "Your Question:",
        placeholder="Type your question here and press Enter...",
        key="user_input"
    )
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # API Request Payload
    payload = {
        "model": model,
        "messages": st.session_state.chat_history
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        assistant_reply = data["choices"][0]["message"]["content"]

        # Add assistant response to history
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        assistant_reply = f"⚠️ Error: {str(e)}"
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

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
