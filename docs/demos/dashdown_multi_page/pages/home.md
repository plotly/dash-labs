---
register_page:
    title: "Dash Labs Home"
    description: "Dash Labs documentation"

MarkdownAIO: 
    exec: False
    text_markdown_props: {"style": {"maxWidth":970}}
    side_by_side: True
---

# Dash Labs Overview
Dash Labs is a project that we use to explore future enhancements to Dash. The goal is that the successful ideas from this project will migrate into future versions of Dash itself. And over time, new ideas will be added to this library.

We encourage you to join the discussion, raise issues, make pull requests, and take an active role in shaping the future of Dash.


## New in Dash Labs:

- `pages/  ` The new, better way to make multi-page apps

- `MarkdownAIO`  Markdown that runs the code!  _Comming Soon to dash-labs_.  See the feature preview here.

__The documentation you are now viewing was created with `pages/` and `MarkdownAIO`. You can find the code [here]().__



## Initial Design Goals
Dash Labs began with several interdependent design goals:
 - Provide a more concise syntax for generating simple Dash apps that follow a variety of nice looking predefined templates.
 - Make it possible for third-party developers to make and distribute custom templates.
 - Ensure that there is a smooth continuum between concision, and the flexibility of "full Dash". A concise syntax should not be a dead-end, requiring the developer to rewrite the app in order to reach a certain level of sophistication.
 - Improve ability of users to encapsulate and reuse custom interactive component workflows, and make it possible for third-party developers to distribute these as plugins.  

You will find the result of these initial goals archived in dash-labs v0.4.0.  Many of the featured developed here made their way into Dash 2.0 and Dash 2.1.

## Dash Labs 1.0.0 Goals

Dash Labs is now set up to develop new features starting with `dash>=2.0` and `dash-bootstrap-components>=1.0`. 

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
 