import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__)

# Function to parameterize
@dx.parameterize(
    app,
    inputs=dict(
        fun=["sin", "cos", "exp"],

        # Style input using bootstrap classes
        figure_title=dbc.Input(
            type="text", value="Initial Title", style={"background-color": "crimson", "color": "white"}
        ),

        # Explicitly specify component property. Default is "value"
        phase=dbc.Select(
            options=[{"label": i, "value": i} for i in range(1, 10)],
            value=4,
        ),

        # Dropdown instead of default slider
        date=(dcc.DatePickerSingle(), "date")
    ),
    labels={
        "fun": "Function",
        "figure_title": "Figure Title",
        "phase": "Phase: {}",
        "date": "Measurement Date"
    }
)
def callback_components(fun, figure_title, phase, date):
    print(date, type(date))
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + int(phase))
    ).update_layout(title_text=figure_title + "-" + str(date)))


app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=9006)
