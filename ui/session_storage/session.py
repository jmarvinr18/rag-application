import streamlit as st



def store_messages(value):
    st.session_state.messages = []
    st.session_state.messages = value


def read_messages(key):
    return st.session_state.messages