# Overview
Dash Labs is a project that will be used to explore future enhancements to Dash. The goal is that the successful ideas from this project will migrate into future versions of Dash itself. And over time, new ideas will be added to this library.

## Initial Design Goals
Dash Labs began with several interdependent design goals:
 - Provide a more concise syntax for generating simple Dash apps that follow a variety of nice looking predefined templates.
 - Make it possible for third-party developers to make and distribute custom templates.
 - Ensure that there is a smooth continuum between concision, and the flexibility of "full Dash". A concise syntax should not be a dead-end, requiring the developer to rewrite the app in order to reach a certain level of sophistication.
 - Improve ability of users to encapsulate and reuse custom interactive component workflows, and make it possible for third-party developers to distribute these as plugins.
 
# Installation
Dash Labs can be installed using `pip` with

```
$ pip install -U dash-labs
```

To use the templates based on `dash-bootstrap-components`, a few additional packages are required:

```
$ pip install -U dash-bootstrap-components spectra colormath requests tinycss2
```
 
# Activating Dash Labs Functionality
The Dash Labs functionality is enabled by specifying an instance of `dash_labs.Plugin` when instantiating a Dash app.

```python
import dash
import dash_labs as dl

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
```

> Note: it is recommended to import `dash_labs` as `dl`, and this is the convention that will be used throughout this document.
