# Overview
The chapter explains how Dash Labs templates can be used as small components of a larger app, how multiple templates can be combined in a single app, and what it looks like to migrate at app away from using templates at all.

# Getting started
We're going to start with a very simple app that uses plotly express to display a plot of the gapminder dataset, and provides a Dash slider to specify the year 

# Adding more controls
logx, continents checkboxes, opacity


# Switching template
The card is getting pretty tall. Switch to row, Switch to sidebar.

# Using multiple templates
Back to just year. Instead of adding more controls, add an additional dataset.

Place Gapminder and Tips row templates in separate DBC tabs.

# Migrate away from templates
Remove template from callbacks, extract dependency objects to variables.
```python
dropdown_input = Dbc.dropdown_input()
dropdown = dropdown_input.component_id
```

use dropdown_input in callback, arrange dropdown in your custom layout

# Remove all traces of templates
If you want to go a step further and remove all use of templates, manually define your components and ids. Callback still stays the same.
