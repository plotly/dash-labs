# Overview
Unlike other Plotly projects, `dash-labs` does **not** adhere to semantic versioning. This project is intended to make it easier to discuss and iterate on new ideas before they are incorporated into Dash itself. As such, maintaining backward compatibility within the `dash-labs` package is explicitly a non-goal.

## 1.0.4 - May 4, 2022
### Fixed 
- added encoding='utf-8' to open function

## 1.0.3 - March 21, 2022

### Added
- [#86](https://github.com/plotly/dash-labs/pull/86)  Allow title and description to be a function so that meta data and title can be updated dynamically when using path variables. [issue #74](https://github.com/plotly/dash-labs/issues/74)
 
### Fixed 
- [#86](https://github.com/plotly/dash-labs/pull/86) Made the pages folder relative to the root directory of the app, rather than the cwd. [issue #84](https://github.com/plotly/dash-labs/issues/84)


## 1.0.2 - January 26, 2022

### Added
 - [#61](https://github.com/plotly/dash-labs/pull/61).  New feature for handling variables in the URL.
### Fixed
 - [#73](https://github.com/plotly/dash-labs/pull/73).  Allow for multiple values in query strings.
 - [#78](https://github.com/plotly/dash-labs/pull/78). Fix `/pages` for Dash Enterprise.

## 1.0.1

### Fixed
 - [#59](https://github.com/plotly/dash-labs/pull/59) Fixed bug that prevented order prop from changing the order of the modules in dash.page_registry
 - [#55](https://github.com/plotly/dash-labs/pull/55) Fixed bug that prevented multipage apps from working in windows: Fixed bug #52. Transitioned function away from the glob library to the os library to ensure functionality with windows. 

## 1.0.0

### Added
 - Added Dash Pages: A plug-in to simplify building multi-page apps.
 - Added documentation: 08-MultiPageDashApp.md and 09-MultiPageDashAppExamples.md.
 - Added demos:  examples of multi-page apps using the Dash Pages plug-in.

### Removed
 - removed code, tests, and demos for projects documented in chapter 02 through 07.

## Changes
 - updated documentation to include status of projects in chapters 02 through 07.

## 0.4.0

### Added
 - Added Windows support for the `@app.long_callback` decorator ([#32](https://github.com/plotly/dash-labs/pull/32))
 - Added caching support to the `@app.long_callback` decorator using the `cache_by` argument ([#32](https://github.com/plotly/dash-labs/pull/32))
 - Add support for updating arbitrary component properties while a long_callback is running using the `set_progress` function. 

### Changes
 - To enable Windows support, the FlaskCaching backend to `@app.long_callback` has been replaced by a backend based on the `daskcache` library


## 0.3.0

### Added
 - Added Dash app plugins to support a new `@app.long_callback` decorator to support long-running callback functions ([#24](https://github.com/plotly/dash-labs/pull/24)).

### Changes
 - Replace use of "role" with "location" throughout the templates API ([#25](https://github.com/plotly/dash-labs/pull/25)).
 - Remove `_input`/`_output` suffix from template component builders, and replace with `new_` prefix ([#25](https://github.com/plotly/dash-labs/pull/25)). 


## 0.2.0

### Changes
 - Replaced `tpl.layout(app)` method with `tpl.children` property ([#20](https://github.com/plotly/dash-labs/pull/20))

### Documentation
 - Added documentation chapter with additional examples of template usage


## 0.1.0

This is the initial release of `dash-labs` which includes:
 - The `dash_labs.plugins.FlexibleCallbacks` plugin which enables advanced `@app.callback` functionality like property grouping and the ability to provide components in place of component ids.
 - A new template system that aims to make it easier to quickly create a variety of simple, nice looking, Dash apps with less code.
 - A new component plugin system that makes it possible to bundle components and callback functionality into composable classes. Several demonstration component plugins are included as well.
