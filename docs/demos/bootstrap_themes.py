import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

df = px.data.gapminder()
years = sorted(df.year.drop_duplicates())

# css_url = "https://bootswatch.com/4/cerulean/bootstrap.css"
# css_url = "https://bootswatch.com/4/cosmo/bootstrap.css"
# css_url = "https://bootswatch.com/4/cyborg/bootstrap.css"
# css_url = "https://bootswatch.com/4/darkly/bootstrap.css"
# css_url = "https://bootswatch.com/4/flatly/bootstrap.css"
# css_url = "https://bootswatch.com/4/journal/bootstrap.css"
# css_url = "https://bootswatch.com/4/litera/bootstrap.css"
# css_url = "https://bootswatch.com/4/lumen/bootstrap.css"
# css_url = "https://bootswatch.com/4/lux/bootstrap.css"
# css_url = "https://bootswatch.com/4/materia/bootstrap.css"
# css_url = "https://bootswatch.com/4/minty/bootstrap.css"
# css_url = "https://bootswatch.com/4/pulse/bootstrap.css"
# css_url = "https://bootswatch.com/4/sandstone/bootstrap.css"
# css_url = "https://bootswatch.com/4/simplex/bootstrap.css"
# css_url = "https://bootswatch.com/4/sketchy/bootstrap.css"
# css_url = "https://bootswatch.com/4/slate/bootstrap.css"
# css_url = "https://bootswatch.com/4/solar/bootstrap.css"
# css_url = "https://bootswatch.com/4/spacelab/bootstrap.css"
# css_url = "https://bootswatch.com/4/superhero/bootstrap.css"
# css_url = "https://bootswatch.com/4/united/bootstrap.css"
css_url = "https://bootswatch.com/4/yeti/bootstrap.css"

tpl = dl.templates.DbcSidebar(app, title="Dash Labs App", theme=css_url)


@app.callback(
    args=dict(
        size=tpl.dropdown_input(["pop", "gdpPercap", "lifeExp"], label="Size"),
        color=tpl.dropdown_input(
            ["continent", "pop", "gdpPercap", "lifeExp"], label="Color"
        ),
        figure_title=tpl.textbox_input("Life Expectency", label="Figure Title"),
        year=tpl.slider_input(
            years[0], years[-1], step=5, value=years[-1], label="Year"
        ),
        logs=tpl.checklist_input(
            ["log(x)", "log(y)"], value="log(x)", label="Axis Scale"
        ),
    ),
    output=tpl.graph_output(),
    template=tpl,
)
def callback(size, figure_title, year, color, logs):
    logs = logs or []

    # Let parameterize infer output component
    year_df = df[df.year == year]
    if not len(year_df):
        return go.Figure()

    return (
        px.scatter(
            year_df,
            x="gdpPercap",
            y="lifeExp",
            size=size,
            color=color,
            hover_name="country",
            log_x="log(x)" in logs,
            log_y="log(y)" in logs,
            size_max=60,
        )
        .update_layout(
            title_text=f"{figure_title} ({year})", margin=dict(l=0, r=0, b=0)
        )
        .update_traces(marker_opacity=0.8)
    )


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=False)
