import dash
import dash_express as dx
import numpy as np
import plotly.express as px


df = px.data.gapminder()

years = sorted(list(df.year.drop_duplicates()))
size_max = float(df["pop"].max())
print("size_max", size_max)
app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")
# template = dx.templates.FlatDiv()


@dx.parameterize(
    app,
    inputs=dict(
        year=years,
    ),
    template=template,
    labels={
        "year": "Year: {}",
    },
)
def callback_components(year):

    fig = px.scatter_geo(
        df.query(f"year == {year}"), locations="iso_alpha", color="continent",
        hover_name="country", size="pop", size_max=size_max,
        projection="natural earth"
    ).update_layout(title_text=str(year))

    return fig

app.layout = callback_components.layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9067)
