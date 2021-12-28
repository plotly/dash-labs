#!/usr/bin/env python
# page_registry

"""
CHANGELOG:

RUXI (Dec 28, 2021) :
    1.0.1-patch

    Motivation for the re-write is to enable interactive
    dev work not at the package root. This was addressed
    by using absolute paths instead of relative paths
    when appropriate, and adding more options for users
    to set the path configuration

    ---------------------
    InstallPluginToModule
    ---------------------
    attaches plug-in methods either
    (i) directly to module (dash) - (original behaviour),
    or
    (ii) add namespace to module with methods - (new behaviour)

    i.e.

    example 1:
    InstallPluginToModule(dash, namespace = 'pages')  -(creates)->
        dash.pages
            |_ .register_pages
            |_ {registry}

    example 2:
    InstallPluginToModule(dash, namespace = None)  -(creates)->
        dash
            |_ .register_pages
            |_ {registry}

    rationale:
        easier to make namespace changes using a factory.

    ----------------------------------------------
    PageRegistryRecord & inject_record_to_registry
    ----------------------------------------------
    refactored `register_page`

    the task of creating registry records and
    injecting the data to the registry is decoupled
    for portability

    `PageRegistryRecord` is the dataclass schema
    `inject_record_to_registry` is a decorator

    ----------------
    AutoRegisterPage
    ----------------
    The auto-import function from `plug` was split off to
    `AutoRegisterPage`, added option to configure PAGES_PATH

    -----------
    other notes
    -----------
    _match_case_filename_image_table 
        requires py3.10 since it uses the new pattern matching syntax
        (did it for learning purposes)

Modified pages_plugin.py by AnnMarieW (plotly, dash-labs):

Reference:
 - https://github.com/plotly/dash-labs/blob/main/dash_labs/plugins/pages.py
 - https://github.com/plotly/dash-multi-page-app-plugin
"""


# require for PageRegistry
from pathlib import Path
import warnings
from collections import OrderedDict, namedtuple
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Callable
from types import ModuleType
import importlib
from types import SimpleNamespace
import functools
import sys
# require for plugin
import dash
from dash import callback, Output, Input, html, dcc
import os
# require for plug
import json
import flask
from textwrap import dedent
from urllib.parse import parse_qs
# use stdout instead of ic for debugging
try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = print


# create a namespace plugin target
dash.pages = SimpleNamespace(__name__="pages")

# ENVIRONMENT VARIABLES
PLUGIN_INSTALLATION_TARGET  = dash # variable name
PLUGIN_REGISTRY_NAME        = "page_registry"
PLUGIN_NAMESPACE            = None #"pages" # NONE
#PLUGIN_METHOD_REGISTER_NAME = "register_page"
PAGES_PATH = Path(Path(__file__).parent, 'pages')

_ID_CONTENT = '_pages_plugin_content'
_ID_LOCATION = '_pages_plugin_location'
_ID_DUMMY = '_pages_plugin_dummy'

page_container = html.Div([
    dcc.Location(id=_ID_LOCATION),
    html.Div(id=_ID_CONTENT),
    html.Div(id=_ID_DUMMY)
])


#=======================================+
# docorator to inject records
# generated from dataclass
# to a registry (dash.page_registry)
#=======================================+
def inject_record_to_registry(
    target: ModuleType ,
    registry_attr: str = 'registry',
    verbose = False
    ):
    """Decorator to inject records generated from dataclass to a target.registry

    parameters
    ----------
    function (docorated):
        dataclass with ._key and .__dict__ attributes

        Produces key-pair record from dict(._key:.__dict__)

    target (object):
        injection target which holds the registry attribute

    registry_attr (str):
        name of the registry attribute to be appended to the injection target

    verbose (bool, default: False): ics debugging statements
    """
    # inside the decorator factory
    registry_name = f"""{target.__name__}.{registry_attr}"""
    def create_registry(target, registry_attr: str):
        """assigns OrderDict as <target>.<registry>        """
        if not hasattr(target, registry_attr):
            setattr(target, registry_attr, OrderedDict())
            if verbose:
                ic(f'registry create: {registry_name}')

    def decorator_inject_record(function):
        @functools.wraps(function)
        def wrapper(*args, **kw):
            output = function(*args, **kw)
            # prepare record
            key = output._key
            value = output.__dict__
            record = {key:value}
            # creates registry
            create_registry(target, registry_attr)
            # inject record
            getattr(target, registry_attr)[key] = value
            ic(f'{key=} record injected to {registry_name}')
            return output # redundantly return dataclass after injecting
        return wrapper
    return decorator_inject_record

#=======================================+
# dataclass to register page
# to get layout and metadata
#=======================================+
@inject_record_to_registry(
    target = PLUGIN_INSTALLATION_TARGET,
    registry_attr = PLUGIN_REGISTRY_NAME,
    verbose = True)
@dataclass
class PageRegistryRecord:
    """
    PageRegistryRecord is used by `pages_plugin` to set up the layouts as
    a multi-page Dash app. This includes the URL routing callbacks
    (using `dcc.Location`) and the HTML templates to include title,
    meta description, and the meta description image.

    package layout assumptions
    --------------------------
    src/ (optional)
        package/
            pages_plugin.py
            app.py
            assets/ (must be at same level as pages)
                app.png
                logo.png
                home-page.jpg

            pages/
                home-page.py

    Parameters
    ----------

    module (str): module.__name__
        The module path where this page's `layout` is defined.
        User supplies __name__ when registering page

        USAGE:  __name__
        SYNTAX: "<package>.pages.<module>"

    path (str, optional): URL path
        Format: `/` or `/home-page` relative to package root
        If not supplied, will be inferred from `module`.
        e.g. `pages.weekly_analytics` to `/weekly-analytics`

    name (str, optional): name of link
        If not supplied, will be inferred from `module`,
        e.g. `pages.weekly_analytics` to `Weekly analytics`

    order: (int, optional): order of the pages

    layout (str, optional):
        The Dash.layout function or component for this page.
        If not supplied, will scan for "layout" attribute in the module page

    image (str, optional. default: None): meta description of image
        If not supplied, will be inferred from `module`
        by pattern matching in directory `assets` directory

        matches:
            page image: assets/<title>.<extension>.
            app image:  assets/app.<extension>
            logo:       assets/logo.<extension>

        eg. assets/home_page.png

    title (str, optional): Name of page <title> that appears is browser
        If not supplied, will be inferred from `module`,
        e.g. `pages.weekly_analytics` to `Weekly analytics`

    description (str, optional. defaults: None):
        The <meta type="description"></meta>.

    redirect_from (list, optional):
        A list of paths that should redirect to this page.
        example: `redirect_from=['/v2', '/v3']`

    Properties
    ----------
    _filepath (str): absolute filepath to registered module page
                     taken from <package>.pages.<module>.__file__
                     format: /path/to/package/pages/module.py
    _assetpath (str): expected directory of media assets
                     format: /path/to/package/assets

    _key (str):       copy of .module
    """
    module: str
    urlpath: str = field(default = None)
    name: str = field(default = None)
    order: int = field(default = None)
    layout: str = field(default=None)
    image: str = field(default = None)
    title: str = field(default = None)
    description: str = field(default = None)
    redirect_from: list = field(default = None)
    _filepath: str = field(init=False)
    _module_instance: Any = field(init=False)
    _assetpath: str = field(init=False)
    _assetmodule: str = field(init=False)
    verbose: bool = True

    @property
    def _key(self):
        """copy of .module, used for injection"""
        return self.module

    def __post_init__(self):
        module = self.module
        if self.urlpath is None:
            self.urlpath = self._infer_urlpath(module)

        if self.name is None:
            self.name = self._infer_name(module)

        if self.title is None:
            self.title = self.name

        if self.layout is None:
            self.layout = self._infer_layout(module)

        # define absolute paths based on script location
        # makes assumptions on package layout
        instance = self._import_module(module)

        self._module_instance = instance
        self._filepath = instance.__file__
        self._assetpath = self._infer_asset_path(instance.__file__)
        self._assetmodule = self._infer_asset_module(module)
        if self.image is None:
            self.image = self._infer_image(self._assetpath, module)

        # key. used later for injection

    @staticmethod
    def _infer_urlpath(filename):
        return '/' + filename.split('.')[-1].replace('_', '-').lower()

    @staticmethod
    def _infer_name(filename):
        return filename.split('.')[-1].replace('_', ' ').capitalize()

    @staticmethod
    def _import_module(module):
        return importlib.import_module(module)

    @staticmethod
    def _infer_layout(module):
        module_instance = importlib.import_module(module)
        layout = module_instance.layout

        # is layout a function?
        if isinstance(layout, Callable):
            ic(f'layout is function in {module_instance}')
            return layout()
        return layout

    @staticmethod
    def parse_parent_dir_by_pattern_match(filename, pattern = 'pages', replace = "assets"):
        """tranverse filepath from child to root until pattern found
           then keep parent folder with optional replacement of pattern
        """
        parts = Path(filename).parts
        store_values = []
        keep_content = False
        for x in parts[::-1]:
            if keep_content:
                store_values.append(x)
            if x == 'pages':
                keep_content = True
                store_values.append('assets')
        new_parts = tuple(store_values[::-1])
        return Path(*new_parts)

    @classmethod
    def _infer_asset_path(cls, filepath):
        func = cls.parse_parent_dir_by_pattern_match
        new_path = func(filepath, pattern = 'pages', replace = "assets")
        return new_path.__str__()

    @staticmethod
    def _match_case_filename_image_table(filepath, page_pattern, verbose=False):
        """checks for pattern in filename
        cases:
            page: <page_pattern>.<ext>
            app:  app.<ext>
            logo: logo.<ext>

        Any ext, case-insensitive, "-" and "_" insensitive
        """
        source = Path(filepath).stem.lower().replace("-","_")
        page = SimpleNamespace(pattern = page_pattern)
        if verbose:
            ic(filepath)
            ic(f"{page.pattern=}")
        match source:
            case page.pattern:
                if verbose:
                    ic(f"page image found, {page.pattern=}")
                return dict(page=filepath.name)
            case "app":
                if verbose:
                    ic('app image found')
                return dict(app=filepath.name)
            case "logo":
                if verbose:
                    ic('logo image found')
                return dict(logo=filepath.name)
            case _:
                if verbose:
                    ic("none found")
                return {}

    @classmethod
    def _infer_image(cls, assetpath, module, return_dict=False):
        """
        looks for media in assetpath (/path/to/package/media)

        Return:
            (str): either,
                - PAGE :specific image: `assets/<title>.<extension>` is used,
                        e.g. `assets/weekly_analytics.png`
                - APP. : generic app image at `assets/app.<extension>`
                - LOGO
            In that priority order.

                - A page specific image: `assets/<title>.<extension>` is used,
                    e.g. `assets/weekly_analytics.png`
                - A generic app image at `assets/app.<extension>`
                - A logo at `assets/logo.<extension>`
        """
        match_case_table = cls._match_case_filename_image_table
        files_in_assets  = list(Path(assetpath).glob("*"))
        page_pattern     = module.split('.')[-1].lower().replace("-","_")

        results = {}
        for filename in files_in_assets:
            outcome = match_case_table(filename, page_pattern)
            results.update(**outcome)
        # return all image results
        if return_dict:
            return results
        # return image based on priority
        priority = ['page', 'app', 'logo']
        for key in priority:
            if key in results.keys():
                return results[key]
        return None

    @classmethod
    def _infer_asset_module(cls, module):
        func = cls.parse_parent_dir_by_pattern_match
        new_path = func(module.replace(".","/"), pattern = 'pages', replace = "assets")
        new_path = new_path.__str__().replace("/",".")
        return new_path

def is_plugin_installed(
        PLUGIN_TARGET = PLUGIN_INSTALLATION_TARGET,
        PLUGIN_NAMESPACE = PLUGIN_NAMESPACE,
        PLUGIN_REGISTRY_NAME = "registry",
        verbose=False,
        raise_except=False
        ):
    """check if target has all pages plugin methods"""
    if PLUGIN_NAMESPACE is None:
        target = PLUGIN_TARGET
    else:
        target = getattr(PLUGIN_TARGET, PLUGIN_NAMESPACE)
        ic(getattr(PLUGIN_TARGET, PLUGIN_NAMESPACE))

    ic('check if target has expected methods...')
    ic(target)
    expected_methods = ['register_page', PLUGIN_REGISTRY_NAME]
    results = []
    for method in expected_methods:
        if raise_except:
            assert ic(hasattr(target, method))

        _, outcome = ic(method, hasattr(target, method))
        results.append(outcome)
    SUCCESS_INSTALL = all(results)
    ic(SUCCESS_INSTALL)
    return SUCCESS_INSTALL


class InstallPluginToModule:
    """InstallPluginToModule

    Instantiate to inject plugin to target module's namespace
    ----------
    parameters
    ----------
    PLUGIN_TARGET (SimpleNamespace or module):
        Supply a module or SimpleNamespace to install plugin

    PLUGIN_REGISTRY_NAME (str, default = 'registry'):
        where the records go

    PLUGIN_NAMESPACE (str or None, default = 'pages')
        adds attribute <PLUGIN_NAMESPACE> to target

        if none, directly adds plugin methods to target

        example 1:
        InstallPluginToModule(dash, namespace = 'pages')  -(creates)->
            dash.pages
                |_ .register_pages
                |_ {registry}

        example 2:
        InstallPluginToModule(dash, namespace = None)  -(creates)->
            dash
                |_ .register_pages
                |_ {registry}

    """
    _is_plugin_installed = is_plugin_installed
    register_page = PageRegistryRecord
    _plugin = None
    _logs = None
    def __init__(self,
        PLUGIN_TARGET: ModuleType,
        PLUGIN_NAMESPACE: str or None = "pages",
        PLUGIN_REGISTRY_NAME = "registry",
        verbose = False
        ):
        # assignments
        self.PLUGIN_TARGET = PLUGIN_TARGET
        self.PLUGIN_NAMESPACE = PLUGIN_NAMESPACE
        self.PLUGIN_REGISTRY_NAME = PLUGIN_REGISTRY_NAME
        self.verbose = verbose

        # do stuff
        self._logs, self._plugin = self.install_plugin()
        self.is_plugin_installed()


    @classmethod
    def plugin_class_factory(cls, namespace, registry_name):
        """factory for plugin object"""
        if namespace is None:
            namespace = 'plugin_methods'

        make_class_pages_plugin = \
            make_dataclass(namespace,[registry_name, "register_page"])

        kwargs = {
                registry_name: OrderedDict(),
                "register_page": cls.register_page
            }
        ic('creating plugin class')
        return ic(make_class_pages_plugin(**kwargs))


    @classmethod
    def _attach_plugin_to_target(cls, target, namespace, registry_name, verbose):
        plugin = cls.plugin_class_factory(namespace, registry_name)
        logs = []
        if namespace is not None:
            _, log = (setattr(target, namespace, plugin),
            ic(f"{target.__name__}.{namespace} attached with {plugin}"))
            return log, plugin
        # no namespace
        for method, value in plugin.__dict__.items():
            _, log = (setattr(target, method, value),
            ic(f".{method} added to {target.__name__}"))
            logs.append(log)
        return logs, plugin

    def install_plugin(self):
        return self._attach_plugin_to_target(
            target = self.PLUGIN_TARGET,
            namespace = self.PLUGIN_NAMESPACE,
            registry_name = self.PLUGIN_REGISTRY_NAME,
            verbose = self.verbose)

    def is_plugin_installed(self):
        ic('post-install check...')
        return is_plugin_installed(
            PLUGIN_TARGET = self.PLUGIN_TARGET,
            PLUGIN_REGISTRY_NAME = self.PLUGIN_REGISTRY_NAME,
            verbose = self.verbose,
            raise_except = False)

    @property
    def plugin(self):
        if self._plugin is None:
            namespace, registry_name = self.PLUGIN_NAMESPACE, self.PLUGIN_REGISTRY_NAME
            self._plugin = self.plugin_class_factory(
                namespace,
                registry_name)
        return self._plugin

def REGISTRY_LOC(
    target = PLUGIN_INSTALLATION_TARGET,
    namespace = PLUGIN_NAMESPACE,
    registry_name = PLUGIN_REGISTRY_NAME,
    ):
    """get instance of pages registry

    example:
        dash.<pages>.<registery>
    """
    if namespace is None:
        return getattr(target, registry_name)
    container = getattr(target, namespace)
    return getattr(container, registry_name)


def plug(app):

    REGISTRY_CONTAINER = REGISTRY_LOC()

    @app.server.before_first_request
    def router():
        @callback(
            Output(_ID_CONTENT, 'children'),
            Input(_ID_LOCATION, 'pathname'),
            Input(_ID_LOCATION, 'search'),
            prevent_initial_call=True
        )
        def update(pathname, search):
            path_id = app.strip_relative_path(pathname)
            query_parameters = _parse_query_string(search)

            layout = None
            for module in REGISTRY_CONTAINER:
                page = REGISTRY_CONTAINER[module]
                if path_id == app.strip_relative_path(page['path']):
                    layout = page['layout']

            if layout is None:
                if 'pages.not_found_404' in REGISTRY_CONTAINER:
                    layout = REGISTRY_CONTAINER['pages.not_found_404']['layout']
                else:
                    layout = html.H1('404')

            if callable(layout):
                ic('Calling...')
                ic(query_parameters)
                return layout(**query_parameters)
            else:
                return layout


        # Set validation_layout and prefix component IDs and callbacks with module name
        for module in REGISTRY_CONTAINER:

            app.validation_layout = html.Div([
                page['layout']() if callable(page['layout']) else page['layout']
                for page in REGISTRY_CONTAINER.values()
            ] + [app.layout])

        # Update the page title on page navigation
        path_to_title = {
            page['path']: page['title']
            for page in REGISTRY_CONTAINER.values()
        }
        path_to_description = {
            page['path']: page['description']
            for page in REGISTRY_CONTAINER.values()
        }
        path_to_image = {
            page['path']: page['image']
            for page in REGISTRY_CONTAINER.values()
        }

        app.clientside_callback(
            f"""
            function(path) {{
                document.title = {json.dumps(path_to_title)}[path] || 'Dash'
            }}
            """,
            Output(_ID_DUMMY, 'children'),
            Input(_ID_LOCATION, 'pathname')
        )

        # Set index HTML for the meta description and page title on page load
        def interpolate_index(**kwargs):

            image = path_to_image.get(flask.request.path, '')
            if '/' not in image:
                image = app.get_asset_url(image)

            return dedent(
                '''
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>{title}</title>
                        <meta name="description" content="{description}" />

                        <!-- Twitter Card data -->
                        <meta property="twitter:card" content="{description}">
                        <meta property="twitter:url" content="https://metatags.io/">
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
                '''
            ).format(
                metas=kwargs['metas'],
                description=path_to_description.get(flask.request.path, ''),
                title=path_to_title.get(flask.request.path, 'Dash'),
                image=image,
                favicon=kwargs['favicon'],
                css=kwargs['css'],
                app_entry=kwargs['app_entry'],
                config=kwargs['config'],
                scripts=kwargs['scripts'],
                renderer=kwargs['renderer']
        )

        app.interpolate_index = interpolate_index

        def create_redirect_function(redirect_to):
            def redirect():
                return flask.redirect(redirect_to, code=301)
            return redirect

        # Set redirects
        for module in REGISTRY_CONTAINER:
            page = REGISTRY_CONTAINER[module]
            if page['redirect_from'] and len(page['redirect_from']):
                for redirect in page['redirect_from']:
                    # TODO - Use pathname prefix
                    app.server.add_url_rule(
                        redirect,
                        redirect,
                        create_redirect_function(page['path'])
                    )


def _parse_query_string(search):
    if search and len(search) > 0 and search[0] == '?':
        search = search[1:]
    else:
        return {}

    parsed_qs = {}
    for (k, v) in parse_qs(search).items():
        first = v[0]  # ignore multiple values
        try:
            first = json.loads(first)
        except:
            pass

        parsed_qs[k] = first
    return parsed_qs


#------------------------------------
# scans /pages and auto-import
#-------------------------------------
@dataclass
class AutoRegisterPage:
    """Automatically register layouts to dash from module pages

    tranverses /pages folder for <scripts>.py to import to sys.modules

    the imported scripts must have ```dash.register_page(__name__)``` line

    parameters
    ----------
    pages_dir (str): path/to/pages
        /pages contains <script>.py

        #<script>.py must include:

            # code to register page
            dash.register_page(__name__)

            # layout for parse
            layout = dash.html.H1('home page')
    """
    pages_dir: str
    default_modulename: str = "Pages"
    registry: dict = field(init = False, default_factory = list)


    def __post_init__(self):
        self.registry = self.autoimport(self.pages_dir)

    @staticmethod
    def _import_module_by_path(key, filepath):
        spec = importlib.util.spec_from_file_location(key, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return spec, module

    @classmethod
    def autoimport(cls, pages_dir="pages" ):
        import_module = cls._import_module_by_path
        page_paths = []
        blacklist = ["__init__.py"]
        # screen for valid modules
        for x in  list(Path(pages_dir).rglob("*.py")):
            if x.suffix != ".py":
                continue
            if x.name in blacklist:
                continue
            page_paths.append(x)

        # import module
        registry = {}
        for filename in page_paths:
            key = str(pages_dir.stem)+"."+Path(filename).stem
            #datum = import_module(key, filename)
            registry[key] = {}
            registry[key]['filename'] = filename
            registry[key]['module'] = key

            # try to import
            try:
                instance = import_module(key, filename)
                registry[key]['module_instance'] = instance
                ic(f"""{key} imported  from {filename}""")
            except:
                ic(f"""{key} failed to import""")
        return registry


# INSTANTIATE

# if __name__ == '__main__':
#ic(f"{PAGES_PATH=}")
plugin = InstallPluginToModule(
    PLUGIN_TARGET = PLUGIN_INSTALLATION_TARGET,
    PLUGIN_NAMESPACE = PLUGIN_NAMESPACE,
    PLUGIN_REGISTRY_NAME = PLUGIN_REGISTRY_NAME
    ).plugin

AutoRegisterPage(PAGES_PATH)
