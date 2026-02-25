import streamlit as st
import time
import pandas as pd
import requests
from io import StringIO

# Streamed response emulator
def response_generator(response):
    for word in response.splitlines(keepends=True):
        yield word
        time.sleep(0.5)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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



with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload data", accept_multiple_files=False)

    # ## Uncomment this if accepting multiplie_files is True
    # for uploaded_file in uploaded_files:
    #     files = {
    #         "title": uploaded_file.name,
    #         "source": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type),
    #         "doc_type": uploaded_file.type
    #     }    
    #     response = requests.post(
    #         "http://localhost:5001/api/v1/documents",
    #         files=files,
    #         timeout=120
    #     )

if uploaded_file is not None:
    # To read file as bytes:
    # bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    files = {
        "title": uploaded_file.name,
        "source": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type),
        "doc_type": uploaded_file.type
    }    
    response = requests.post(
        "http://localhost:5001/api/v1/documents",
        files=files,
        timeout=120
    )