import streamlit as st


pg = st.navigation([
    st.Page("streamlit/chat.py", title="Chat", icon="🔥"),
    st.Page("streamlit/document.py", title="Document", icon=":material/favorite:"),
])
pg.run()