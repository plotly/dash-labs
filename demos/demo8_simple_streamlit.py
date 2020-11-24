import streamlit as st

if st.checkbox("First Checkbox"):
    st.write("Checked")
    if st.checkbox("First Optional checkbox"):
        st.write("Nested checkbox checked")
else:
    st.write("Unchecked")
    dropdown_val = st.selectbox(label="", options=["First", "Second", "Third"])
    st.write(f"You selected {dropdown_val}")
