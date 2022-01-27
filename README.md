# Dash Labs tech preview

This repository contains a work-in-progress technical preview of potential future Dash features. 

> 🚧 Dash Labs features are not guaranteed to land in the official `dash` package. These features are also not officially supported by Plotly's Support Team or by Dash Enterprise. We recommend waiting for these features to land in `dash` before using them in a Production Environment. 🚧

## Documentation
The documentation for Dash Labs can be found in the [docs/](./docs/) directory.
  - [01-Overview.md](https://github.com/plotly/dash-labs/blob/main/docs/01-Overview.md)  

 _Archived in dash-labs v0.4.0:_
  - [02-CallbackEnhancements.md](https://github.com/plotly/dash-labs/blob/main/docs/02-CallbackEnhancements.md)
  - [03-TemplateLayoutSystem.md](https://github.com/plotly/dash-labs/blob/main/docs/03-TemplateLayoutSystem.md)
  - [04-PredefinedTemplates.md](https://github.com/plotly/dash-labs/blob/main/docs/04-PredefinedTemplates.md)
  - [05-ComponentPlugingPattern.md](https://github.com/plotly/dash-labs/blob/main/docs/05-ComponentPlugingPattern.md)
  - [06-TemplateIntegrationAndMigration.md](https://github.com/plotly/dash-labs/blob/main/docs/06-TemplateIntegrationAndMigration.md)
  - [07-LongCallback.md](https://github.com/plotly/dash-labs/blob/main/docs/07-LongCallback.md)


### Multi-Page App Docs 
_New in dash-labs>=1.0.0:_
  - [08-MultiPageDashApp.md](https://github.com/plotly/dash-labs/blob/main/docs/08-MultiPageDashApp.md)
    - Overview, quickstart apps, reference for the `pages` plug-in
  - [09-MultiPageDashApp-NestedFolders.md](https://github.com/plotly/dash-labs/blob/main/docs/09-MultiPageDashApp-NestedFolders.md)
    - Example of organizing app pages in nested folders within the `pages/` folder
  - [10-MultiPageDashApp-MetaTags.md](https://github.com/plotly/dash-labs/blob/main/docs/10-MultiPageDashApp-MetaTags.md)
    - Details on how the title, image, and description are used to create the meta tags which determine how your app looks when shared on social media.
  - [11-MultiPageDashApp-LayoutFunctions.md](https://github.com/plotly/dash-labs/blob/main/docs/11-MultiPageDashApp-LayoutFunctions.md)
    - Examples of when to make the `layout` a function - like when creating a custom menu by page, or using query strings.
  
### Multi-Page App Demos  
Examples and demos are located in the [docs/demos](https://github.com/plotly/dash-labs/tree/main/docs/demos) directory.
  - `multi_page_basics`
    - Minimal examples of all the features and basic quickstart apps. (see chapter 8 for details.)
  - `multi_page_example1`
    - A quickstart app using `dash-bootstrap-components` and some simple callbacks.
  - `multi_page_layout_functions`
    - An app that creates a sidebar menu for certain pages. (See chapter 11 for details.)
  - `multi_page_long_callback`
    - An example of how to use `@app.long_callback()` with `pages/`
  - `multi_page_meta_tags`
    - The example app used to show how the meta tags are generated. (See chapter 10 for details.)
  - `multi_page_nested_folders`
    - This is the example app used in chapter 9.
  - `multi_page_query_strings`
    - An example of using query strings in the URL to pass parameters from one page to another.

## Installation
To install the latest version of dash-labs:

```
$ pip install -U dash-labs
```

To install the archived version:
```
$ pip install dash-labs==0.4.0
```
We also recommend installing Pandas, which is required by Plotly Express and used in many of our examples.
