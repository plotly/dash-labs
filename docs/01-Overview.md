# Overview
Dash Labs is a project that we use to explore future enhancements to Dash. The goal is that the successful ideas from this project will migrate into future versions of Dash itself. And over time, new ideas will be added to this library.

We encourage you to join the discussion, raise issues, make pull requests, and take an active role in shaping the future of Dash.

## Initial Design Goals
Dash Labs began with several interdependent design goals:
 - Provide a more concise syntax for generating simple Dash apps that follow a variety of nice looking predefined templates.
 - Make it possible for third-party developers to make and distribute custom templates.
 - Ensure that there is a smooth continuum between concision, and the flexibility of "full Dash". A concise syntax should not be a dead-end, requiring the developer to rewrite the app in order to reach a certain level of sophistication.
 - Improve ability of users to encapsulate and reuse custom interactive component workflows, and make it possible for third-party developers to distribute these as plugins.  

You will find the result of these initial goals archived in dash-labs v0.4.0.  Many of the featured developed here made their way into Dash 2.0 and Dash 2.1.

### Dash Labs 1.0.0 Goals

Dash Labs is now set up to develop new features starting with `dash>=2.0` and `dash-bootstrap-components>=1.0`. The first new project we’ve added is the Dash `pages/` feature. We’ll be adding more new projects in the coming months.

## Documentation
Find the documentation for Dash Labs in the [docs/](./docs/) directory.
  - [01-Overview.md](https://github.com/plotly/dash-labs/blob/main/docs/01-Overview.md)  

 _Archived in dash-labs v0.4.0:_
  - [02-CallbackEnhancements.md](https://github.com/plotly/dash-labs/blob/main/docs/02-CallbackEnhancements.md)
  - [03-TemplateLayoutSystem.md](https://github.com/plotly/dash-labs/blob/main/docs/03-TemplateLayoutSystem.md)
  - [04-PredefinedTemplates.md](https://github.com/plotly/dash-labs/blob/main/docs/04-PredefinedTemplates.md)
  - [05-ComponentPlugingPattern.md](https://github.com/plotly/dash-labs/blob/main/docs/05-ComponentPlugingPattern.md)
  - [06-TemplateIntegrationAndMigration.md](https://github.com/plotly/dash-labs/blob/main/docs/06-TemplateIntegrationAndMigration.md)
  - [07-LongCallback.md](https://github.com/plotly/dash-labs/blob/main/docs/07-LongCallback.md)

_New in dash-labs v1.0.0:_
  - [08-MultiPageDashApp.md](https://github.com/plotly/dash-labs/blob/main/docs/08-MultiPageDashApp.md)
  - [09-MultiPageDashAppExamples.md](https://github.com/plotly/dash-labs/blob/main/docs/09-MultiPageDashAppExamples.md)
 
Find examples and demos in the [docs/demos](./docs/demos) directory.

## Installation
To install the latest version of dash-labs:

```
$ pip install -U dash-labs
```

To install the archived version:
```
$ pip install dash-labs==0.4.0
```

To use the demos  based on `dash-bootstrap-components`:

```
$ pip install -U dash-bootstrap-components 
```
 
# Activating Dash Labs Functionality
The Dash Labs functionality is enabled by specifying an instance of `dash_labs.Plugin` when instantiating a Dash app.

```python
from dash import Dash
import dash_labs as dl

app = Dash(__name__, plugins=[dl.plugins.pages])
```
