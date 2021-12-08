
> ## Status: Multi-Page Dash App Plugin
> #### Under active development:  A plugin to simplify creating multi-page Dash apps. This is a preview of functionality that will be added to Dash 2.1.
> **[See the community announcement for details and discussion](https://community.plotly.com/t/introducing-dash-pages-dash-2-1-feature-preview/57775)**


# Multi-Page Dash App Examples

**Please see Chapter 08-MultiPageDashApp for an introduction to the Multi-Page Dash App Plugin**

If you would like to add an example, feel free to create a pull request! 

### Example: Social Media Meta Tags
  
One of the cool features when you use this method of creating mult-page apps, is that it automatically creates the meta 
tags used by social media sites like Facebook and Twitter.  These sites use the app title, description and image to create
the card that is displayed when you share a link to your site. 

Here is more info on social media meta tags:  https://css-tricks.com/essential-meta-tags-social-media/


The example below goes into detail about how to add an image to a page in dash.page_registry.  

See the code in `/demos/multi_page_images`

- `image`:
   The meta description image used by social media platforms.
   If not supplied, then it looks for the following images in `assets/`:
    - A page specific image: `assets/<title>.<extension>` is used, e.g. `assets/weekly_analytics.png`
    - A generic app image at `assets/app.<extension>`
    - A logo at `assets/logo.<extension>`

In the `assets` folder we have 4 jpeg images with the following file names:  
- app.jpeg
- birdhouse.jpeg
- birds.jpeg
- logo.jpeg


In the `pages` folder we have 3 simple pages to demonstrate the images feature. 

#### `a_page.py`
```python
import dash

dash.register_page(__name__)


def layout():
    return """    
    This page uses a generic image.  No image is specified and there is no image that matches
    the module name in the assets folder, so it uses `app.jpeg` or `logo.jpeg` if no `app.jpeg` exists.
        """
```

#### `birds.py`
```python
import dash

dash.register_page(__name__)


def layout():
    return """
    No image is specified but it's inferred from the module name.
    The module name is`birds.py` so it uses the `birds.jpeg` file in the assets folder.
    """
```

#### `home.py`
```python
import dash
from dash import html

dash.register_page(
    __name__,
    path="/",
    image="birdhouse.jpeg",
    title="(home) The title, headline or name of the page",
    description="(home) A short description or summary 2-3 sentences",
)

layout = html.Div("The image for the home page is specified as `birdhouse.jpeg'")

```

The `dash.page_registry` now has an `image` for each page.  Here is the `app.py` we use as the entry point to run the app:

```python
from dash import Dash, html, dcc
import dash
import dash_labs as dl

app = Dash(__name__, plugins=[dl.plugins.pages])


app.layout = html.Div(
    [
        html.H1("App Frame"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url(page["image"]),
                            height="40px",
                            width="60px",
                        ),
                        dcc.Link(f"{page['name']} - {page['path']}", href=page["path"]),
                    ],
                    style={"margin": 20},
                )
                for page in dash.page_registry.values()                
            ]
        ),
        dl.plugins.page_container,
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)

```
If you inspect the page, you will see the Twitter Data card and the Open Graph data (which is use by Facebook) has
automatically been added to the page.  Note that the title and description are as specified for each
app in the pages folder.

![image](https://user-images.githubusercontent.com/72614349/145254812-32b8db12-2833-4244-a7f8-6f51fec309ea.png)

