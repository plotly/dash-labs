---
register_page:   
    order: 2
    title: "MarkdownAIO Style Options"
    description: "Dash Labs documentation"

MarkdownAIO:
    dangerously_use_exec: False
---





## Style options 

There is a basic stylesheet you can use with MarkdownAIO. Here is how to include it as an external stylesheet:

```python

app = dash.Dash(__name__, external_stylesheets=[dl.css.markdownaio])
```

You can also include it in the `assets` folder by copying the content of the link to your own `.css` file in your
app's `assets` folder.  You can find the link like this:

print(dl.css.markdownaio)

It defines several class names that you can use to customize the style




You can customize each instance of `MarkdownAIO`

```python


app.layout = html.Div(
    [
    
        html.Div(MarkdownAIO("page1.md"), className="maio-dark"),
        html.Div(MarkdownAIO("page2.md"), className="maio")
    ], 
)

```

Or change for each element, either the code block, Markdown text, app container.  Here are example of
the classes defined within the `dl.css.markdownaio` stylesheet

### Code Syntax Highlighting 



Here is a sample code block with this dark theme:

![image](https://user-images.githubusercontent.com/72614349/150701421-44b1da68-8529-4185-8360-0c9fe895e698.png)
This example uses `code_markdown_props={"className": "maio"}`


### How to change the code syntax highlighting

The `MarkdownAIO` stylesheet defines a light and a dark theme, however you can change to other themes as well.

The code highlighting is handled by highlight.js. By default, only certain languages are recognized, and there is only
one color scheme available. However, you can override this by adding custom styles as an external stylesheet or to a
.css file in the main app's `assets` folder.

1) Visit this website to select a code highlight style:  https://highlightjs.org/static/demo/  

2) Get the url for the stylesheet: https://cdnjs.com/libraries/highlight.js  

3) Add url to `external_stylesheets` and/or add it to a .css file in the  `assets/` folder.  

Here is an example of using this link as an external stylesheet:

```python
# syntax highlighting
hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/stackoverflow-light.min.css"

app = Dash(
    __name__,
    plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.SPACELAB, hljs],
    suppress_callback_exceptions=True,
)

```
