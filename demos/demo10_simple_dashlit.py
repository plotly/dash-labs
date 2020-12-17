from dashlit import st_callback
import dash_express as dx
import dash

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar("Dashlit Example")


def build_app(st):
    if st.checkbox("First Checkbox"):
        st.write("Checked")
        if st.checkbox("First Optional checkbox"):
            st.write("Nested checkbox checked")
    else:
        st.write("Unchecked")
        dropdown_val = st.dropdown(options=["First", "Second", "Third"])
        st.write(f"You selected {dropdown_val}")


layout = st_callback(app, build_app, template=template)
app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9010)
