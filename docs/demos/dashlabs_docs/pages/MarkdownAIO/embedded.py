from dash import dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash_labs import MarkdownAIO
import dash

dash.register_page(__name__, name="Dashdown embeded in layout")


layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    dcc.Markdown(
                        """
                    #### `MarkdownAIO` can be used in a .py file. 
                    This is convenient when only certain parts of a layout are easier to write as a Markdown file, like help text
                    or other narrative.
                     
                    In this example, the `sample.md` is displayed in a dbc.Collapse:
                    
                    ```python                    
                    app.layout = dbc.Container(
                        [
                            # other elements
                            
                            dbc.Collapse(
                                dbc.Card(MarkdownAIO("sample.md", dangerously_use_exec=True)),
                                id="collapse",
                                is_open=False,
                            ), 
                            
                            # other elements
                            
                        ], fluid=True
                    )
                                     
                    ```
                    click the "More Info" button to see the content.
                    
                    """,
                        className="mb-4",
                    ),
                    dbc.Button(
                        "More Info",
                        id="collapse-btn",
                        color="info",
                        className="m-4",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            MarkdownAIO(
                                "pages/MarkdownAIO/sample.md",
                                dangerously_use_exec=True,
                            )
                        ),
                        id="collapse",
                        is_open=False,
                    ),
                ]
            )
        )
    ],
    fluid=True,
)


@callback(
    Output("collapse", "is_open"),
    Input("collapse-btn", "n_clicks"),
    State("collapse", "is_open"),
)
def toggle(n, is_open):
    if n:
        return not is_open
    return is_open
