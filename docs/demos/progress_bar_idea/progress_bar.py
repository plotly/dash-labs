import time
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_express as dx
from docs.demos.progress_bar_idea.background_callback import background_callback
from flask_caching import Cache

app = dash.Dash(__name__, plugins=[dx.Plugin()])
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem', 'CACHE_DIR': './cache'
})
tp = dx.templates.FlatDiv()

iris = px.data.iris()
features = ["sepal_length",  "sepal_width",  "petal_length",  "petal_width"]

@background_callback(
    app, cache,
    args=[dx.Input(
        dcc.Dropdown(
            options=[{"value": i, "label": i} for i in features],
            value=features[0],
            clearable=False,
        ), label="Iris Feature"
    )],
    output=tp.graph(),
    template=tp,
)
def background_callback(set_progress, feature):
    print("start calculation")
    total = 10
    for i in range(total):
        time.sleep(0.5)
        set_progress(i, total)

    return dcc.Graph(figure=px.histogram(
        iris, x=feature
    ).update_layout(title_text=f"Histogram of {feature}"))


app.layout = tp.layout(app)


if __name__ == "__main__":
    cache.clear()
    app.run_server(debug=True, port=8081)
