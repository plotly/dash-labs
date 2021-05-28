import dash_bootstrap_components as dbc
from dash_bootstrap_components import Container, Form, FormGroup, Label, Col
import dash
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = Container(Form([
    FormGroup([
        Label('Hours per Day', width=6),
        Col(dbc.Input(id="hours-per-day", type="number", value=5))], row=True),
    FormGroup([
        Label('Rate per Hour', width=6),
        Col(dbc.Input(id="rate-per-hour", type="number", value=2))], row=True),
    FormGroup([
        Label('Amount', width=6),
        Label(id="amount", width=4)], row=True),
    FormGroup([
        Label('Amount per Week', width=6),
        Label(id="amount-per-week", width=6)], row=True),
]), style=dict(padding=20))


@app.callback(Output("amount", "children"), Input("hours-per-day", "value"), Input("rate-per-hour", "value"))
def amount(hours_per_day, rate_per_hour):
    return hours_per_day * rate_per_hour


@app.callback(Output("amount-per-week", "children"), Input("amount", "children"))
def amount_per_week(amount):
    return amount * 7


if __name__ == "__main__":
    app.run_server(debug=True)