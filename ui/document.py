import streamlit as st
import requests

st.title("Documents")

# Initialization
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'



st.text_input("Your name", key="name")

# This exists now:
st.session_state.name


# Read
st.write(st.session_state.key)

product_data = {
    "Product": [
        ":material/devices: Widget Pro",
        ":material/smart_toy: Smart Device",
        ":material/inventory: Premium Kit",
    ],
    "Category": [":blue[Electronics]", ":green[IoT]", ":violet[Bundle]"],
    "Stock": ["🟢 Full", "🟡 Low", "🔴 Empty"],
    "Units sold": [1247, 892, 654],
    "Revenue": [125000, 89000, 98000],
}
st.table(product_data, border="horizontal")

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