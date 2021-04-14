# Overview
Unlike other Plotly projects, `dash-labs` does **not** adhere to semantic versioning. This project is intended to make it easier to discuss and iterate on new ideas before they are incorporated into Dash itself. As such, maintaining backward compatibility within the `dash-labs` package is explicitly a non-goal.

## 0.1.0

This is the initial release of `dash-labs` which includes:
 - The `dash_labs.plugins.FlexibleCallbacks` plugin which enables advanced `@app.callback` functionality like property grouping and the ability to provide components in place of component ids.
 - A new template system that aims to make it easier to quickly create a variety of simple, nice looking, Dash apps with less code.
 - A new component plugin system that makes it possible to bundle components and callback functionality into composable classes. Several demonstration component plugins are included as well.
