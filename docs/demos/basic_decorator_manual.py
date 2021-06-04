import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import plotly.express as px
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcRow(app, title="Manual Update", theme=dbc.themes.SOLAR)


@app.callback(
    args=dict(
        fun=tpl.new_dropdown(["sin", "cos", "exp"], label="Function", kind=dl.State),
        figure_title=tpl.new_textbox(
            "Initial Title", label="Figure Title", kind=dl.State
        ),
        phase=tpl.new_slider(1, 10, label="Phase", kind=dl.State),
        amplitude=tpl.new_slider(1, 10, value=3, label="Amplitude", kind=dl.State),
        n_clicks=tpl.new_button("Update", label=None),
    ),
    template=tpl,
)
def greet(fun, figure_title, phase, amplitude, n_clicks):
    print(fun, figure_title, phase, amplitude)
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(
        figure=px.line(x=xs, y=getattr(np, fun)(xs + phase) * amplitude).update_layout(
            title_text=figure_title
        )
    )


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
