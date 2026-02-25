import streamlit as st

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