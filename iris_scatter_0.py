import dash_express as dx
import plotly.express as px
import dash_core_components as dcc

df = px.data.iris()
feature_cols = [col for col in df.columns if "species" not in col]

@dx.interact(
    dx.layouts.dbc.DbcSidebarLayout(title="Iris Features")
)
def iris(x=feature_cols, y=feature_cols):
    return dcc.Graph(
        figure=px.scatter(df, x=x, y=y, color="species"),
    )

if __name__ == "__main__":
    iris.run_server(debug=True)
