import dash_express as dx
import plotly.express as px
import dash

app = dash.Dash(__name__)

tips = px.data.tips()
all_columns = tips.columns.tolist()
numeric_columns = [
    col for col, dtype in tips.dtypes.items() if dtype.kind in ("i", "f", "u")
]

parameterized = dx.parameterize(
    app,
    inputs=dict(
        data_frame=dx.fixed(tips),
        x=all_columns,
        y=all_columns,
        size=numeric_columns,
        color=all_columns,
    ),
    optional=["size", "color"]
)(px.scatter)

app.layout = parameterized.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
