---
register_page:   
    order: 2
    title: "MarkdownAIO Style Options"
    description: "Dash Labs documentation"

MarkdownAIO:
    dangerously_use_exec: True  
---

## Style options 

### Code Syntax highlighting

The code highlighting is handled by highlight.js. By default, only certain languages are recognized, and there is only
one color scheme available. However, you can override this by adding custom styles as an external stylesheet or to a
.css file in the main app's `assets` folder.

1) Visit this website to select a code highlight style:  https://highlightjs.org/static/demo/  

2) Get the url for the stylesheet: https://cdnjs.com/libraries/highlight.js  

3) Add url to `external_stylesheets` and/or add it to a .css file in the  `assets/` folder.  

This app you are viewing uses a light theme like this:

```python dangerously_use_exec=False
# syntax highlighting
hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/stackoverflow-light.min.css"

app = Dash(
    __name__,
    plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.SPACELAB, hljs],
    suppress_callback_exceptions=True,
)

```

To change the theme, update the URL. Here is the URL for one of the dark themes:

```python dangerously_use_exec=False
hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/github-dark-dimmed.min.css"

```

Here is a sample code block with this dark theme:

![image](https://user-images.githubusercontent.com/72614349/150701421-44b1da68-8529-4185-8360-0c9fe895e698.png)


### More style examples coming soon