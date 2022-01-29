## Sample Markdown File

This is a markdown file with a mix of *text and code*.

```
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
layout = dcc.Graph(figure=fig)
```