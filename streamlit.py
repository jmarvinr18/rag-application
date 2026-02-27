import streamlit as st


pg = st.navigation([
    st.Page("ui/chat.py", title="Chat", icon="🔥"),
    st.Page("ui/document.py", title="Document", icon=":material/favorite:"),
])
pg.run()