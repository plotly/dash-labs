---
  
register_page:
    name: "Deploy a README.md with MarkdownAIO"
    title: "MarkdownAIO example-Deploy a README.md"
    description: "Dash Labs documentation"
    order: 99
    image: None

MarkdownAIO:
    side_by_side: True
    dangerously_use_exec: True
---

# Deploy a README.md file

This example uses `MarkdownAIO` to deploy a README.md file.  It will execute the code blocks contained
within the README.md  

Note that for security purposes, it's not possible to use an external URL to specify the file.
 The README.md file must exist on the server before thea app starts. 


The README.md file below is part of the README.md in the `dash-extentions` library.
Here is how it's added to this multi-page app:

```python  dangerously_use_exec=False
dash.register_page(
    __name__,
    name="Deploy a README.md with MarkdownAIO",
    order=99,
    layout=MarkdownAIO(
        "pages/MarkdownAIO/README.md",        
        side_by_side=True,
        dangerously_use_exec=True
    ),
)
```

Or you could run it as regular single page app like this:

```python  dangerously_use_exec=false

from dash import Dash
from dash_labs import MarkdownAIO

app = Dash(__name__)
app.layout = MarkdownAIO("README.md", dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
```

------------
--------------
# Dashdown Demo 

The following is an excerpt from the README.md file from: https://github.com/thedirtyfew/dash-extensions

-------------

## Dash Extension Components

The components listed here can be used in the `layout` of your Dash app. 

### EventListener

The `EventListener` component makes it possible to listen to (arbitrary) JavaScript events. Simply wrap the relevant components in an `EventListener` component, specify which event(s) to subscribe to, and what event properties to send back to Dash,

```python
from dash import Dash, html, Input, Output, State, callback
from dash_extensions import EventListener

# JavaScript event(s) that we want to listen to and what properties to collect.
event = {"event": "click", "props": ["srcElement.className", "srcElement.innerText"]}
# Create small example app
app = Dash()
app.layout = html.Div([
    EventListener(
        html.Div("Click here!", id="click_here", className="stuff"),
        events=[event], logging=True, id="el"
    ),
    html.Div(id="log")
])

@callback(Output("log", "children"), Input("el", "n_events"), State("el", "event"), prevent_initial_call=True)
def click_event(n_events, e):
    return ",".join(f"{prop} is '{e[prop]}' " for prop in event["props"]) + f" (number of clicks is {n_events})"

if __name__ == "__main__":
    app.run_server()
```

Note that if the relevant events are already exposed as properties in Dash, there is no benefit of using the `EventListener` component. The intended usage of the `EventListener` component is when this is _not_ the case. Say that you need to listen to double-click events, but the Dash component only exposes a (single) click property; or some data that you need is not propagated from the JavaScript layer. In this case, the `EventListener` component makes it possible to achieve the desired behaviour without editing the component source code (i.e. the JavaScript code).

### Purify

The `Purify` component makes it possible to render HTML, MathML, and SVG. Typically, such rendering is prone to XSS vulnerabilities. These risks are mitigated by sanitizing the html input using the [DOMPurify](https://github.com/cure53/DOMPurify) library. Here is a minimal example,

```python
from dash import Dash
from dash_extensions import Purify

app = Dash()
app.layout = Purify("This is <b>html</b>")

if __name__ == "__main__":
    app.run_server()
```

### Mermaid

The `Mermaid` component is a light wrapper of [react-mermaid2](https://github.com/e-attestations/react-mermaid2), which makes it possible to [draw flow diagrams](https://github.com/mermaid-js/mermaid). Here is a small example,

```python
from dash import Dash
from dash_extensions import Mermaid

chart = """
graph TD;
A-->B;
A-->C;
B-->D;
C-->D;
"""
app = Dash()
app.layout = Mermaid(chart=chart)

if __name__ == "__main__":
    app.run_server()
```

### DeferScript

The `DeferScript` component makes it possible to defer the loading of javascript code, which is often required to render dynamic content. One such example is [draw.io](https://app.diagrams.net/),

```python
from dash import Dash, html
from html import unescape
from dash_extensions import DeferScript


mxgraph = r'{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;app.diagrams.net\&quot; modified=\&quot;2021-06-07T06:06:13.695Z\&quot; agent=\&quot;5.0 (Windows)\&quot; etag=\&quot;4lPJKNab0_B4ArwMh0-7\&quot; version=\&quot;14.7.6\&quot;&gt;&lt;diagram id=\&quot;YgMnHLNxFGq_Sfquzsd6\&quot; name=\&quot;Page-1\&quot;&gt;jZJNT4QwEIZ/DUcToOriVVw1JruJcjDxYho60iaFIaUs4K+3yJSPbDbZSzN95qPTdyZgadm/GF7LAwrQQRyKPmBPQRzvktidIxgmwB4IFEaJCUULyNQvEAyJtkpAswm0iNqqegtzrCrI7YZxY7Dbhv2g3r5a8wLOQJZzfU4/lbByoslduPBXUIX0L0cheUrugwk0kgvsVojtA5YaRDtZZZ+CHrXzukx5zxe8c2MGKntNgknk8bs8fsj3+KtuDhxP+HZDVU5ct/RhatYOXgGDbSVgLBIG7LGTykJW83z0dm7kjklbaneLnEnlwFjoL/YZzb93WwNYgjWDC6EEdkuC0cZEO7p3i/6RF1WutL8nxmnkxVx6UcUZJIy/LgP49622mO3/AA==&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}'
app = Dash(__name__)
app.layout = html.Div([
    html.Div(className='mxgraph', style={"maxWidth": "100%"}, **{'data-mxgraph': unescape(mxgraph)}),
    DeferScript(src='https://viewer.diagrams.net/js/viewer-static.min.js')
])

if __name__ == '__main__':
    app.run_server()
```

### BeforeAfter

The `BeforeAfter` component is a light wrapper of [react-before-after-slider](https://github.com/transitive-bullshit/react-before-after-slider/), which makes it possible to [highlight differences between two images](https://transitive-bullshit.github.io/react-before-after-slider/). Here is a small example,

```python
from dash import Dash, html
from dash_extensions import BeforeAfter

app = Dash()

image2 = "https://user-images.githubusercontent.com/72614349/128908946-bb42a9e1-5380-45be-a7b0-130b9b9ec087.jpeg"
image1 = "https://user-images.githubusercontent.com/72614349/128908948-b1fe64c7-2102-410c-ab94-eebf8bb37209.jpeg"

app.layout = html.Div([
    BeforeAfter(before=image1, after=image2, width=400, height=600)
])

if __name__ == '__main__':
    app.run_server()
```

### Ticker

The `Ticker` component is a light wrapper of [react-ticker](https://github.com/AndreasFaust/react-ticker), which makes it easy to show [moving text](https://andreasfaust.github.io/react-ticker/). Here is a small example,

```python
from dash import Dash, html
from dash_extensions import Ticker

app = Dash(__name__)
app.layout = html.Div(Ticker([html.Div("Some text")], direction="toRight"))

if __name__ == '__main__':
    app.run_server()
```

### Lottie

The `Lottie` component makes it possible to run Lottie animations in Dash. Here is a small example,

```python
from dash import Dash, html
import dash_extensions as de

# Setup options.
url = "https://assets9.lottiefiles.com/packages/lf20_YXD37q.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))
# Create example app.
app = Dash(__name__)

app.layout = html.Div(de.Lottie(options=options, width="25%", height="25%", url=url))

if __name__ == '__main__':
    app.run_server()
```


### Keyboard

The `Keyboard` component makes it possible to capture keyboard events at the document level. Here is a small example,

```python


import json
from dash import Dash, html, Output, Input, State, callback
from dash_extensions import Keyboard

app = Dash()
app.layout = html.Div([Keyboard(id="keyboard"), html.Div(id="output")])

@callback(
    Output("output", "children"), 
    [Input("keyboard", "n_keydowns")],
    [State("keyboard", "keydown")],
    prevent_initial_call=True
)
def keydown(n_keydowns, event):
    return json.dumps(event)


if __name__ == '__main__':
    app.run_server()

```

### Monitor

The `Monitor` component makes it possible to monitor the state of child components. The most typical use case for this component is bi-directional synchronization of component properties. Here is a small example,

```python

from dash import Dash, html, dcc, no_update, Input, Output, callback
from dash.exceptions import PreventUpdate
from dash_extensions import Monitor

app = Dash()
app.layout = html.Div(Monitor([
    dcc.Input(id="deg-fahrenheit", autoComplete="off", type="number"),
    dcc.Input(id="deg-celsius", autoComplete="off", type="number")],
    probes=dict(deg=[dict(id="deg-fahrenheit", prop="value"), 
                     dict(id="deg-celsius", prop="value")]), id="monitor")
)

@callback([Output("deg-fahrenheit", "value"), Output("deg-celsius", "value")], 
              [Input("monitor", "data")],prevent_initial_call=True)
def sync_inputs(data):
    # Get value and trigger id from monitor.
    try:
        probe = data["deg"]
        trigger_id, value = probe["trigger"]["id"], float(probe["value"])
    except (TypeError, KeyError):
        raise PreventUpdate
    # Do the appropriate update.
    if trigger_id == "deg-fahrenheit":
        return no_update, (value - 32) * 5 / 9
    elif trigger_id == "deg-celsius":
        return value * 9 / 5 + 32, no_update


if __name__ == '__main__':
    app.run_server(debug=False)
```


### Burger

The `Burger` component is a light wrapper of [react-burger-menu](https://github.com/negomi/react-burger-menu), which enables [cool interactive burger menus](https://negomi.github.io/react-burger-menu/). Here is a small example,

```python dangerously_use_exec=False


from dash import Dash, html
from dash_extensions import Burger


def link_element(icon, text):
    return html.A(children=[html.I(className=icon), html.Span(text)], href=f"/{text}",
                  className="bm-item", style={"display": "block"})


# Example CSS from the original demo.
external_css = [
    "https://negomi.github.io/react-burger-menu/example.css",
    "https://negomi.github.io/react-burger-menu/normalize.css",
    "https://negomi.github.io/react-burger-menu/fonts/font-awesome-4.2.0/css/font-awesome.min.css"
]
# Create example app.
app = Dash(external_stylesheets=external_css)
app.layout = html.Div([
    Burger(children=[
        html.Nav(children=[
            link_element("fa fa-fw fa-star-o", "Favorites"),
            link_element("fa fa-fw fa-bell-o", "Alerts"),
            link_element("fa fa-fw fa-envelope-o", "Messages"),
            link_element("fa fa-fw fa-comment-o", "Comments"),
            link_element("fa fa-fw fa-bar-chart-o", "Analytics"),
            link_element("fa fa-fw fa-newspaper-o", "Reading List")
        ], className="bm-item-list", style={"height": "100%"})
    ], id="slide"),
    html.Main("Hello world!", style={"width": "100%", "height": "100vh"}, id="main")
], id="outer-container", style={"height": "100%"})

if __name__ == '__main__':
    app.run_server()
```