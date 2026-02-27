import streamlit as st
import time
import pandas as pd
import requests
from io import StringIO
from ui.session_storage.session import store_messages,read_messages,store_conversation_id,get_current_conversation


st.title("Ask Van (VanGPT)")
def response_generator(response):
    for word in response.splitlines(keepends=True):
        yield word
        time.sleep(0.5)

if "current_conversation" not in st.session_state:
    st.write("No stored conversation yet.")
else:
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        # st.markdown(st.session_state.messages)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        # st.write(st.session_state.messages)
        # Display user message in chat message container
        
        messages = read_messages("conversation_id")
        for msg in messages:
            # with st.chat_message("user"):            
            with st.chat_message(msg["role"]):
                # st.write(msg)
                st.markdown(msg["content"])

        conversation_id = st.session_state.current_conversation

        response = requests.post(
            "http://localhost:5001/api/v1/messages",json={
                "content": prompt,
                "conversation_id": conversation_id,
                "role": "user"
            }
        )  
        data = response.json()
        ai_text = data["ai"]["content"]

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(ai_text))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def show_chat_board():
    # Accept user input
    # st.write(st.session_state)
    if "current_conversation" not in st.session_state:
        st.write("No stored conversation yet.")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []




def get_conversation_thread(conversation_id):
    # st.write(conversation_id)
    # st.write(st.session_state.messages)

    show_chat_board()
    response = requests.get(
        f"http://localhost:5001/api/v1/messages/conversation/{conversation_id}") 

    store_messages(response.json())

    messages = read_messages(conversation_id)
    store_conversation_id(conversation_id)
    
    for msg in messages:
        with st.chat_message(msg["role"]):
            # st.write(msg)
            st.markdown(msg["content"])


def create_new_conversation():
    st.session_state.current_conversation = None
    st.session_state.messages = []
    response = requests.post(
        "http://localhost:5001/api/v1/conversations",json={})
    
    st.write(f"NEW CHAT ID: {response.json()["id"]}")
    
    store_conversation_id(response.json()["id"])
    show_chat_board()
    

def get_conversations():
    response = requests.get("http://localhost:5001/api/v1/conversations")     
    return response.json()

with st.sidebar:
    st.button(label="➕ New Conversation",type="tertiary", on_click=create_new_conversation)
    st.subheader("Conversations", divider="gray")
    conversations = get_conversations()
    
    for con in conversations:

        if con["title"] is not None:
            title = con["title"]
            st.button(label=title, key=f"conv_btn_{con['id']}", on_click=get_conversation_thread, args=(con["id"],),type="tertiary")

