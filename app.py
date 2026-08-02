import uuid
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Customer Support Bot", page_icon="🤖")
st.title("🤖 Customer Support")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Sidebar: session info + reset
st.sidebar.write(f"**Session:** `{st.session_state.thread_id[:8]}…`")
if st.sidebar.button("Start new conversation"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("category") and msg["category"] != "GENERAL":
            st.caption(f"category: {msg['category']}")

# Handle new input
if query := st.chat_input("How can we help?"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(API_URL, json={
                    "query": query,
                    "thread_id": st.session_state.thread_id,
                }, timeout=120)
                data = r.json()
                reply, category = data["response"], data.get("category")
            except Exception as e:
                reply, category = f"⚠️ Backend error: {e}", None
        st.write(reply)
        if category and category != "GENERAL":
            st.caption(f"category: {category}")

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "category": category})