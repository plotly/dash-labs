import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

# Function to parameterize
@app.callback(
    inputs=dict(
        fun=dx.Input(["sin", "cos", "exp"], label="Function"),

        # Style input using bootstrap classes
        figure_title=dx.Input(
            dbc.Input(
                type="text", value="Initial Title",
                style={"background-color": "crimson", "color": "white"}
            ),
            label="Figure Title",
        ),

        # Explicitly specify component property. Default is "value"
        phase=dx.Input(
            dbc.Select(
                options=[{"label": i, "value": i} for i in range(1, 10)], value=4
            ),
            label="Phase",
        ),

        # Dropdown instead of default slider
        date=dx.Input(dcc.DatePickerSingle(), "date", label="Measurement Date")
    ),
)
def callback_components(fun, figure_title, phase, date):
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + int(phase))
    ).update_layout(title_text=figure_title + "-" + str(date)))


app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
