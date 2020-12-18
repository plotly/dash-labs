import dash
import dash_express as dx
import plotly.express as px
from px_builder import px_builder

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar("Dashlit Example")
# template = dx.templates.DdkSidebar("Dashlit Example")
# template = dx.templates.DccCard("Dashlit Example")

df = px.data.tips()
layout = px_builder(app, df, template)

app.layout = layout

if __name__ == "__main__":
    app.run_server(port=9043, debug=True)
