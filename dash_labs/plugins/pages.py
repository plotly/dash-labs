from dash import callback, Output, Input, html, dcc
import dash
import os
import importlib
from collections import OrderedDict
import flask
from os import listdir
from os.path import isfile, join
from textwrap import dedent
from urllib.parse import parse_qs
from keyword import iskeyword
import warnings


def warning_message(message, category, filename, lineno, line=None):
    return f"{category.__name__}:\n {message} \n"


warnings.formatwarning = warning_message

_ID_CONTENT = "_pages_plugin_content"
_ID_LOCATION = "_pages_plugin_location"
_ID_STORE = "_pages_plugin_store"
_ID_DUMMY = "_pages_plugin_dummy"

page_container = html.Div(
    [
        dcc.Location(id=_ID_LOCATION),
        html.Div(id=_ID_CONTENT),
        dcc.Store(id=_ID_STORE),
        html.Div(id=_ID_DUMMY),
    ]
)


def register_page(
    module,
    path=None,
    path_template=None,
    name=None,
    order=None,
    title=None,
    description=None,
    image=None,
    image_url=None,
    redirect_from=None,
    layout=None,
    **kwargs,
):
    """
    Assigns the variables to `dash.page_registry` as an `OrderedDict`
    (ordered by `order`).

    `dash.page_registry` is used by `pages_plugin` to set up the layouts as
    a multi-page Dash app. This includes the URL routing callbacks
    (using `dcc.Location`) and the HTML templates to include title,
    meta description, and the meta description image.

    `dash.page_registry` can also be used by Dash developers to create the
    page navigation links or by template authors.

    - `module`:
       The module path where this page's `layout` is defined. Often `__name__`.

    - `path`:
       URL Path, e.g. `/` or `/home-page`.
       If not supplied, will be inferred from the `path_template` or `module`,
       e.g. based on path_template: `/asset/<asset_id` to `/asset/none`
       e.g. based on module: `pages.weekly_analytics` to `/weekly-analytics`

    - `path_template`:
       Add variables to a URL by marking sections with <variable_name>. The layout function
       then receives the <variable_name> as a keyword argument.
       e.g. path_template= "/asset/<asset_id>"
            then if pathname in browser is "/assets/a100" then layout will receive **{"asset_id":"a100"}

    - `name`:
       The name of the link.
       If not supplied, will be inferred from `module`,
       e.g. `pages.weekly_analytics` to `Weekly analytics`

    - `order`:
       The order of the pages in `page_registry`.
       If not supplied, then the filename is used and the page with path `/` has
       order `0`

    - `title`:
       (string or function) The name of the page <title>. That is, what appears in the browser title.
       If not supplied, will use the supplied `name` or will be inferred by module,
       e.g. `pages.weekly_analytics` to `Weekly analytics`

    - `description`:
       (string or function) The <meta type="description"></meta>.
       If not supplied, then nothing is supplied.

    - `image`:
       The meta description image used by social media platforms.
       If not supplied, then it looks for the following images in `assets/`:
        - A page specific image: `assets/<title>.<extension>` is used, e.g. `assets/weekly_analytics.png`
        - A generic app image at `assets/app.<extension>`
        - A logo at `assets/logo.<extension>`
        When inferring the image file, it will look for the following extensions: APNG, AVIF, GIF, JPEG, PNG, SVG, WebP.

    - `image_url`:
       This will use the exact image url provided when sharing on social media.
       This is appealing when the image you want to share is hosted on a CDN.
       Using this attribute overrides the image attribute.

    - `redirect_from`:
       A list of paths that should redirect to this page.
       For example: `redirect_from=['/v2', '/v3']`

    - `layout`:
       The layout function or component for this page.
       If not supplied, then looks for `layout` from within the supplied `module`.

    - `**kwargs`:
       Arbitrary keyword arguments that can be stored

    ***

    `page_registry` stores the original property that was passed in under
    `supplied_<property>` and the coerced property under `<property>`.
    For example, if this was called:
    ```
    register_page(
        'pages.historical_outlook',
        name='Our historical view',
        custom_key='custom value'
    )
    ```
    Then this will appear in `page_registry`:
    ```
    OrderedDict([
        (
            'pages.historical_outlook',
            dict(
                module='pages.historical_outlook',

                supplied_path=None,
                path='/historical-outlook',

                supplied_name='Our historical view',
                name='Our historical view',

                supplied_title=None,
                title='Our historical view'

                supplied_layout=None,
                layout=<function pages.historical_outlook.layout>,

                custom_key='custom value'
            )
        ),
    ])
    ```

    """
    # COERCE
    # - Set the order
    # - Inferred paths
    page = dict(
        module=module,
        supplied_path=path,
        path_template=None
        if path_template is None
        else _validate_template(path_template),
        path=(path if path is not None else _infer_path(module, path_template)),
        supplied_name=name,
        name=(name if name is not None else _filename_to_name(module)),
    )
    page.update(
        supplied_title=title,
        title=(title if title is not None else page["name"]),
    )
    page.update(
        description=description if description else "",
        order=order,
        supplied_order=order,
        supplied_layout=layout,
        **kwargs,
    )
    page.update(
        image=(image if image is not None else _infer_image(module)),
        supplied_image=image,
        image_url=image_url
    )
    page.update(redirect_from=redirect_from)

    dash.page_registry[module] = page

    if layout is not None:
        # Override the layout found in the file set during `plug`
        dash.page_registry[module]["layout"] = layout

    # set home page order
    order_supplied = any(
        p["supplied_order"] is not None for p in dash.page_registry.values()
    )

    for p in dash.page_registry.values():
        p["order"] = (
            0 if p["path"] == "/" and not order_supplied else p["supplied_order"]
        )

    # sorted by order then by module name
    page_registry_list = sorted(
        dash.page_registry.values(),
        key=lambda i: (str(i.get("order", i["module"])), i["module"]),
    )

    dash.page_registry = OrderedDict([(p["module"], p) for p in page_registry_list])




def _infer_image(module):
    """
    Return:
    - A page specific image: `assets/<title>.<extension>` is used, e.g. `assets/weekly_analytics.png`
    - A generic app image at `assets/app.<extension>`
    - A logo at `assets/logo.<extension>`
    """
    valid_extensions = ["apng", "avif", "gif", "jpeg", "png", "webp"]
    page_id = module.split(".")[-1]
    files_in_assets = []
    # todo need to check for app.get_assets_url instead?
    if os.path.exists("assets"):
        files_in_assets = [f for f in listdir("assets") if isfile(join("assets", f))]
    app_file = None
    logo_file = None
    for fn in files_in_assets:
        fn_without_extension, _, extension = fn.partition(".")
        if extension.lower() in valid_extensions:
            if (
                fn_without_extension == page_id
                or fn_without_extension == page_id.replace("_", "-")
            ):
                return fn

            if fn_without_extension == "app":
                app_file = fn

            if fn_without_extension == "logo":
                logo_file = fn

    if app_file:
        return app_file

    return logo_file


def _filename_to_name(filename):
    return filename.split(".")[-1].replace("_", " ").capitalize()


def _validate_template(template):
    template_segments = template.split("/")
    for s in template_segments:
        if "<" in s or ">" in s:
            if not (s.startswith("<") and s.endswith(">")):
                raise Exception(
                    f'Invalid `path_template`: "{template}"  Path segments with variables must be formatted as <variable_name>'
                )
            variable_name = s[1:-1]
            if not variable_name.isidentifier() or iskeyword(variable_name):
                warnings.warn(
                    f'`{variable_name}` is not a valid Python variable name in `path_template`: "{template}".',
                    stacklevel=2,
                )
    return template


def _infer_path(filename, template):
    if template is None:
        path = filename.replace("_", "-").replace(".", "/").lower().split("pages")[-1]
        path = "/" + path if not path.startswith("/") else path
        return path
    else:
        # replace the variables in the template with "none" to create a default path if no path is supplied
        path_segments = template.split("/")
        default_template_path = [
            "none" if s.startswith("<") else s for s in path_segments
        ]
        return "/".join(default_template_path)


def _import_layouts_from_pages(pages_folder):
    for (root, dirs, files) in os.walk(pages_folder):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                with open(os.path.join(root, file), encoding='utf-8') as f:
                    content = f.read()
                    if "register_page" not in content:
                        continue
            if file.startswith("_") or not file.endswith(".py"):
                continue
            page_filename = os.path.join(root, file).replace("\\", "/")
            _, _, page_filename = page_filename.partition("pages/")
            page_filename = page_filename.replace(".py", "").replace("/", ".")
            page_module = importlib.import_module(f"pages.{page_filename}")

            if f"pages.{page_filename}" in dash.page_registry:
                dash.page_registry[f"pages.{page_filename}"]["layout"] = getattr(
                    page_module, "layout"
                )


def _path_to_page(app, path_id):
    path_variables = None
    for page in dash.page_registry.values():
        if page["path_template"]:
            template_id = page["path_template"].strip("/")
            path_variables = _parse_path_variables(path_id, template_id)
            if path_variables:
                return page, path_variables
        if path_id == page["path"].strip("/"):
            return page, path_variables
    return {}, None


def plug(app):
    dash.page_registry = OrderedDict()

    pages_folder = os.path.join(flask.helpers.get_root_path(app.config.name), "pages")
    if os.path.exists(pages_folder):
        _import_layouts_from_pages(pages_folder)
    else:
        warnings.warn("A folder called `pages` does not exist.", stacklevel=2)

    @app.server.before_first_request
    def router():
        @callback(
            Output(_ID_CONTENT, "children"),
            Output(_ID_STORE, "data"),
            Input(_ID_LOCATION, "pathname"),
            Input(_ID_LOCATION, "search"),
            prevent_initial_call=True,
        )
        def update(pathname, search):
            # updates layout on page navigation
            # updates the stored page title which will trigger the clientside callback to update the app title

            query_parameters = _parse_query_string(search)
            page, path_variables = _path_to_page(app, app.strip_relative_path(pathname))

            # get layout
            if page == {}:
                if "pages.not_found_404" in dash.page_registry:
                    layout = dash.page_registry["pages.not_found_404"]["layout"]
                    title = dash.page_registry["pages.not_found_404"]["title"]
                else:
                    layout = html.H1("404")
                    title = app.title
            else:
                layout = page["layout"]
                title = page["title"]

            if callable(layout):
                layout = (
                    layout(**path_variables, **query_parameters)
                    if path_variables
                    else layout(**query_parameters)
                )
            if callable(title):
                title = title(**path_variables) if path_variables else title()

            return layout, {"title": title}

        # check for duplicate pathnames
        path_to_module = {}
        for page in dash.page_registry.values():
            if page["path"] not in path_to_module:
                path_to_module[page["path"]] = [page["module"]]
            else:
                path_to_module[page["path"]].append(page["module"])

        for modules in path_to_module.values():
            if len(modules) > 1:
                raise Exception(f"modules {modules} have duplicate paths")

        # Set validation_layout
        app.validation_layout = html.Div(
            [
                page["layout"]() if callable(page["layout"]) else page["layout"]
                for page in dash.page_registry.values()
            ]
            + [app.layout() if callable(app.layout) else app.layout]
        )

        # Update the page title on page navigation
        app.clientside_callback(
            f"""
            function(data) {{
                document.title = data.title || 'Dash'
            }}
            """,
            Output(_ID_DUMMY, "children"),
            Input(_ID_STORE, "data"),
        )

        # Set index HTML for the meta description and page title on page load
        def interpolate_index(**kwargs):
            # The flask.request.path doesn't include the pathname prefix
            # when inside DE Workspaces or deployed environments,
            # so we don't need to call `app.strip_relative_path` on it.
            start_page, path_variables = _path_to_page(
                app, flask.request.path.strip("/")
            )

            image = start_page.get("image", "")
            if image:
                image = app.get_asset_url(image)
            assets_image_url = (
                "".join([flask.request.url_root, image.lstrip("/")]) if image else None
            )
            # get the specified url or create it based on the passed in image
            supplied_image_url = start_page.get("image_url")
            image_url = supplied_image_url if supplied_image_url else assets_image_url

            title = start_page.get("title", app.title)
            if callable(title):
                title = title(**path_variables) if path_variables else title()

            description = start_page.get("description", "")
            if callable(description):
                description = (
                    description(**path_variables) if path_variables else description()
                )

            return dedent(
                """
                <!DOCTYPE html>
                <html>
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>{title}</title>
                        <meta name="description" content="{description}" />
                        <!-- Twitter Card data -->
                        <meta property="twitter:card" content="summary_large_image">
                        <meta property="twitter:url" content="{url}">
                        <meta property="twitter:title" content="{title}">
                        <meta property="twitter:description" content="{description}">
                        <meta property="twitter:image" content="{image}">
                        <!-- Open Graph data -->
                        <meta property="og:title" content="{title}" />
                        <meta property="og:type" content="website" />
                        <meta property="og:description" content="{description}" />       
                        <meta property="og:image" content="{image}">
                        {metas}
                        {favicon}
                        {css}
                    </head>
                    <body>
                        {app_entry}
                        <footer>
                            {config}
                            {scripts}
                            {renderer}
                        </footer>
                    </body>
                </html>
                """
            ).format(
                metas=kwargs["metas"],
                description=description,
                url=flask.request.url,
                title=title,
                image=image_url,
                favicon=kwargs["favicon"],
                css=kwargs["css"],
                app_entry=kwargs["app_entry"],
                config=kwargs["config"],
                scripts=kwargs["scripts"],
                renderer=kwargs["renderer"],
            )

        app.interpolate_index = interpolate_index

        def create_redirect_function(redirect_to):
            def redirect():
                return flask.redirect(redirect_to, code=301)

            return redirect

        # Set redirects
        for module in dash.page_registry:
            page = dash.page_registry[module]
            if page["redirect_from"] and len(page["redirect_from"]):
                for redirect in page["redirect_from"]:
                    fullname = app.get_relative_path(redirect)
                    app.server.add_url_rule(
                        fullname, fullname, create_redirect_function(page["path"])
                    )


def _parse_query_string(search):
    if search and len(search) > 0 and search[0] == "?":
        search = search[1:]
    else:
        return {}

    parsed_qs = {}
    for (k, v) in parse_qs(search).items():
        v = v[0] if len(v) == 1 else v
        parsed_qs[k] = v
    return parsed_qs


def _parse_path_variables(pathname, path_template):
    """
    creates the dict of path variables passed to the layout
    e.g. path_template= "/asset/<asset_id>"
         if pathname provided by the browser is "/assets/a100"
         returns **{"asset_id": "a100"}
    """
    path_segments = pathname.split("/")
    template_segments = path_template.split("/")

    if len(path_segments) != len(template_segments):
        return None

    path_vars = {}
    for path_segment, template_segment in zip(path_segments, template_segments):
        if template_segment.startswith("<"):
            path_vars[template_segment[1:-1]] = path_segment
        elif template_segment != path_segment:
            return None
    return path_vars
