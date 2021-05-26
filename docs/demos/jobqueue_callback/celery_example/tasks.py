from celery import Celery
import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import time

celery_app = Celery('tasks', backend='rpc://', broker='pyamqp://')

@celery_app.task(bind=True)
def add(self, x, y):
    for i in range(10):
        self.update_state(state="PROGRESS", meta={'current': i, 'total': 10})
        time.sleep(0.4)
    return x + y


app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app)

@app.callback(
    args=tpl.button_input("Click here"),
    template=tpl,
)
def callback(n_clicks):
    n_clicks = n_clicks or 0
    res = add.delay(-100, n_clicks)
    while True:
        print(res.state, res.info)
        time.sleep(0.1)
        if res.ready():
            break

    val = res.get()
    print(val)
    return f"Clicked {val} times"

app.layout = dbc.Container(
    tpl.children
)

if __name__ == "__main__":
    print(__name__)
    app.run_server(debug=True)
