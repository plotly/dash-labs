import dash_express as dx
import dash
import pandas as pd

app = dash.Dash(__name__, plugins=[dx.Plugin()])
# tp = dx.templates.DbcSidebar(title="DataTable output example")
tp = dx.templates.DdkSidebar(title="DataTable output example")

values = {"foo": 23, "bar": 12, "baz": 89}

df = pd.DataFrame({
    "Column 1": ["foo", "bar", "baz"], "Column 2": [23, 12, 89]
})


@app.callback(
    output=tp.datatable(df.iloc[:0], component_property=("data", "columns")),
    args=[
        tp.checklist(["foo", "bar", "baz"], label="Options"),
        tp.checklist(["Column 1", "Column 2"], value=["Column 1", "Column 2"], label="Columns"),
    ],
    template=tp,
)
def callback(checked, columns):
    checked = checked or []
    columns = columns or []

    selected_df = df[df["Column 1"].isin(checked)][columns]

    return tp.datatable(selected_df, component_property=("data", "columns"))


app.layout = callback.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
