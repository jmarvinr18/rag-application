import streamlit as st



def store_messages(value):
    st.session_state.messages = value

def read_messages(key):
    return st.session_state.messages

def store_conversation_id(session_id):
    st.session_state.current_conversation = session_id

def get_current_conversation():
    return st.session_state.current_conversation