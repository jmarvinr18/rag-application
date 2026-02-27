import streamlit as st
import time
import pandas as pd
import requests
from io import StringIO
from ui.session_storage.session import store_messages,read_messages
# Streamed response emulator
def response_generator(response):
    for word in response.splitlines(keepends=True):
        yield word
        time.sleep(0.5)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    response = requests.post(
        "http://localhost:5001/api/v1/messages",json={
            "content": prompt,
            "conversation_id": "0ac1707a-115a-4182-a6c3-4ad807ff5293",
            "role": "user"
        }
    )    
    data = response.json()
    ai_text = data["ai"]    

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(ai_text))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


def get_conversation_thread(conversation_id):
    # st.write(conversation_id)
    # st.write(st.session_state.messages)
    response = requests.get(
        f"http://localhost:5001/api/v1/messages/conversation/{conversation_id}") 

    store_messages(response.json())

    messages = read_messages(conversation_id)
    
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg)
            st.markdown(msg["content"])


    

def get_conversations():
    response = requests.get("http://localhost:5001/api/v1/conversations")     
    return response.json()

with st.sidebar:
    st.subheader("Conversations", divider="gray")
    conversations = get_conversations()
    title = ""
    for con in conversations:

        # st.write(con)
        if con["title"]:
            title = con["title"]
        else:
            title = "No title yet"
        
        st.button(label=title, key=f"conv_btn_{con['id']}", on_click=get_conversation_thread, args=(con["id"],),type="tertiary")

