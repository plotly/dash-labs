from dashlit import st_callback
import dash_express as dx
import dash

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar("Dashlit Example")
# template = dx.templates.DdkRow("Dashlit Example")
# template = dx.templates.DccCard("Dashlit Example")


def build_app(st):
    if st.checkbox("First Checkbox", role="input"):
        st.write("**Checked Separator**", role="input")
        st.write("Checked", role="output")
        if st.checkbox("First Optional checkbox", role="output"):
            st.write("Nested checkbox checked", role="output")
    else:
        st.write("**Unchecked Separator**", role="input")
        st.write("Unchecked", role="output")
        dropdown_val = st.dropdown(options=["First", "Second", "Third"], optional=True, role="input")
        st.write(f"You selected {dropdown_val}", role="output")

    st.write("""
    
    ## And some more
    More content
    """, role="output")


layout = st_callback(app, build_app, template=template)
app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9010)
