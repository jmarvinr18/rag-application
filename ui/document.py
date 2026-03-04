import streamlit as st
import requests
from datetime import datetime, date
import numpy as np
import pandas as pd
from ui.session_storage.session import set_document_id


st.title("📄 Document Library")


st.set_page_config(layout="wide")

# -----------------------------
# MOCK DATA (replace with DB)
# -----------------------------
@st.cache_data
def load_documents():
    response = requests.get("http://localhost:5001/api/v1/documents")  
    data = response.json()
    return data


def delete_document():
    requests.delete(f"http://localhost:5001/api/v1/documents/{st.session_state.document_id}") 
    st.cache_data.clear()

    # return response.json()

# -----------------------------
# LOAD DATA
# -----------------------------
docs = load_documents()
df = pd.DataFrame(docs)


if docs:

    left_col, right_col = st.columns([1, 1], gap="large", vertical_alignment="center", width="stretch")
    with left_col:
        st.button("Delete", icon_position="right", on_click=delete_document )
    # -----------------------------
    # 🎨 FILE TYPE BADGE
    # -----------------------------
    def file_badge(file_type):
        colors = {
            "pdf": "🔴 PDF",
            "docx": "🔵 DOCX",
            "html": "🟢 HTML",
        }
        return colors.get(file_type.lower(), f"⚪ {file_type.upper()}")

    # df["doc_type"] = df["doc_type"].apply(file_badge)


    # -----------------------------
    # 📊 DISPLAY TABLE
    # -----------------------------

    event = st.dataframe(
        df[["title", "source", "doc_type", "created_at"]],
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={           
            "title": st.column_config.TextColumn("Title"),
            "source": st.column_config.TextColumn("Source"),
            "doc_type": st.column_config.TextColumn("Type"),
            # "created_at": st.column_config.DatetimeColumn(
            #     "Uploaded On",
            #     format="YYYY-MM-DD HH:mm",
            # ),
        },
    )

    def show_pdf_url(pdf_url: str):
        st.info(f"👀 PDF URL: {pdf_url}")
        st.markdown(
            f"""
            <iframe
                src="{pdf_url}"
                width="100%"
                height="950"
                style="border: none;">
            </iframe>
            """,
            unsafe_allow_html=True,
        )


    # -----------------------------
    # HANDLE ROW SELECTION
    # -----------------------------
    selected_rows = event.selection.rows

    if selected_rows:
        selected_index = selected_rows[0]
        selected_doc = df.iloc[selected_index]

        st.subheader(f"📄 Preview — {selected_doc['title']}")
        st.subheader(f"📄 Document ID — {selected_doc['id']}")
        set_document_id(selected_doc['id'])
        show_pdf_url(selected_doc["source"])



with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload data", accept_multiple_files=False)


if uploaded_file is not None:
    # To read file as bytes:
    # bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    files = {
        "title": uploaded_file.name,
        "source": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type),
        "doc_type": uploaded_file.type
    }    
    requests.post(
        "http://localhost:5001/api/v1/documents",
        files=files,
        timeout=120
    )
    st.cache_data.clear()
    load_documents()