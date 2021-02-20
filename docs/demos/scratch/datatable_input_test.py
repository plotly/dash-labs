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
    output=tp.markdown(),
    args=tp.datatable(df, kind=dx.Input, label="Data Entry"),
    template=tp,
)
def callback(data):
    if data:
        input_df = pd.DataFrame(data)
    else:
        input_df = df.iloc[:0]

    c1 = [str(v) for v in input_df["Column 1"].dropna()]
    c2 = [str(v) for v in input_df["Column 2"].dropna()]

    result = (
        "### Entered\n" +
        "  - Columns 1: " + ", ".join(c1) + "\n" +
        "  - Columns 2: " + ", ".join(c2) + "\n"
    )
    return result


app.layout = callback.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
