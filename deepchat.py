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
st.set_page_config(page_title="Enhanced Chatbot", layout="wide")
st.title("🤖 Havish Chatbot")
st.sidebar.title("Navigation")
st.sidebar.markdown("""
- 📂 **New Chat**
- 🔍 **Search Chats**
- 📚 **Library**
""")

# Initialize session state for chat history and editing
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None  # None means no question is being edited

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

# Sidebar: File Upload (Optional)
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
    submitted = st.form_submit_button("Send")

if submitted:
    # Add user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Generate response
    try:
        response = ask_openai(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    except Exception as e:
        response = f"⚠️ Error: {str(e)}"
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display Chat Messages with Edit and Copy Options
with chat_container:
    for idx, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            # Display user message
            col1, col2, col3 = st.columns([8, 1, 1])
            with col1:
                if st.session_state.editing_index == idx:
                    # Show input box for editing
                    edited_text = st.text_input(
                        "Edit your question:", value=message["content"], key=f"edit_{idx}"
                    )
                    save_button = st.button("Save", key=f"save_{idx}")
                    cancel_button = st.button("Cancel", key=f"cancel_{idx}")
                    if save_button:
                        # Update question and regenerate response
                        st.session_state.chat_history[idx]["content"] = edited_text
                        try:
                            updated_response = ask_openai(
                                edited_text, st.session_state.chat_history[:idx]
                            )
                            st.session_state.chat_history[idx + 1]["content"] = updated_response
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        st.session_state.editing_index = None
                    if cancel_button:
                        st.session_state.editing_index = None
                else:
                    st.markdown(f"**You:** {message['content']}")
            with col2:
                # Edit button
                edit_button = st.button("✏️", key=f"edit_button_{idx}")
                if edit_button:
                    st.session_state.editing_index = idx
            with col3:
                # Copy button
                copy_button = st.button("📋", key=f"copy_button_{idx}")
                if copy_button:
                    st.text_area("Copy Question:", value=message["content"], key=f"copy_{idx}")
        elif message["role"] == "assistant":
            # Display bot message
            st.markdown(f"**Bot:** {message['content']}")
