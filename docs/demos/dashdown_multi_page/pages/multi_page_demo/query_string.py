import dash
from dash import dcc, html

dash.register_page(__name__)


text = dcc.Markdown(
    """
## Query Strings

```python

dash.register_page(__name__)

```

Here's the layout:

```

def layout(velocity=None, **other_unknown_query_strings):
    return html.Div(
        [
            "Velocity",
            dcc.Input(id="velocity", value=velocity),            
            f"Other unknown query string {other_unknown_query_strings}"
        ]
    )

```

Note that the layout is a function.  In this example, the a variable named "velocity"
is entered into an input field. Any other variable from the query string will be in the "other_unknown_query_strings" dict.


Give it a try!  Add ?velocity=20  or ?day=Sun to the path in the browser.

"""
)


def layout(velocity=None, **other_unknown_query_strings):
    return html.Div(
        [
            text,
            html.Br(),
            "Velocity",
            dcc.Input(id="velocity", value=velocity),
            html.Br(),
            f"Other unknown query string {other_unknown_query_strings}",
        ]
    )
