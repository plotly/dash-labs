from dashlit import st_callback
import dash

app = dash.Dash(__name__)

@st_callback(app)
def build_app(st):
    if st.checkbox("First Checkbox"):
        st.write("Checked")
        if st.checkbox("First Optional checkbox"):
            st.write("Nested checkbox checked")
    else:
        st.write("Unchecked")
        dropdown_val = st.dropdown(options=["First", "Second", "Third"])
        st.write(f"You selected {dropdown_val}")

if __name__ == "__main__":
    app.run_server(debug=True, port=9010)
