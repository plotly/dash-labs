---
register_page:
    order: 4
    title: "MarkdownAIO Scope"
    description: "Dash Labs documentation"

MarkdownAIO:
    app_div_props: {"className": "mb-4 pb-4"}
    scope_creep: True
    dangerously_use_exec: True
  

---


# Scope and Scope Creep

This section will describe more about the following `MarkdownAIO` parameters:

- `dash_scope`: the default scope available when dangerously_use_executing code blocks

- `scope`: Adds scope to the code blocks. 

- `scope_creep`: Allows variables from one code block to be defined in the next code block.

## Stand-alone dash apps

When running code blocks in the Markdown file, you may include a complete Dash App.  This enables the user to copy the code
block and run it themselves as a stand-alone app on their own computer.  

For example, you could do this:

```python

from dash import Dash, dcc
import plotly.express as px

app = Dash(__name__)

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
app.layout = dcc.Graph(figure=fig)

if __name__ == "__main__":
    app.run_server(debug=True)


```



### `scope` and `dash_scope` parameters

You can produce the same output by simply doing this:

```python

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
layout = dcc.Graph(figure=fig)

```

In fact, you don't even need the `layout = ` 


```python 

dcc.Graph(figure=fig)

```



This is possible, because of the `dash_scope` parameter.  The default is True, so it adds the following to the scope
of the code bock:

```python dangerously_use_exec=False
scope = dict(
              dcc=dcc,
              html=html,
              Input=Input,
              Output=Output,
              State=State,
              dash_table=dash_table,
              px=px,
              plotly=plotly,
              dbc=dbc,
              **(scope or {}))

```

You can also add to the `dash_scope` using the `scope` parameter.  For example, the following will add pandas to the
scope.

Note:  If you are adding `app` to the scope in a multi-page app, you must call `dash.register_page` from within the main `app.py` file

```python dangerously_use_exec=False
import pandas as pd
MarkdownAIO("my_markdown_file.md", scope={"pd": pd})

```  

```python
import pandas as pd
data_url = 'https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv'
df = pd.read_csv(data_url)

layout = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("records"),
    page_size=5,
)

```

You may also add to the scope without using the `scope` parameter by importing the module in your codeblock.  Here
we include `import pandas as pd` in the code block:

```python dangerously_use_exec=False
import pandas as pd

data_url = 'https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv'
df = pd.read_csv(data_url)

layout = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("records"),
    page_size=5,
)

```


### `scope_creep` parameter

It's possible for `MarkdownAIO` to function like a notebook.  By setting `scope_creep=True` 
which allows variables from one code block to be defined in the next code block.

For example, let's start with this dataset:
```python 
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
layout = dcc.Graph(figure=fig)

```

Now using the same dataset from the previous codeblock, we can show a different figure 

```python


fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", marginal_y="violin",
           marginal_x="box", trendline="ols", template="simple_white")
app.layout=dcc.Graph(figure=fig)

```
