from ..fixtures import app, test_template


# Helpers
def num_stylesheets(app):
    return sum("test_stylesheet" in url for url in app.config.external_stylesheets)


def num_css_class_entries(app):
    return app.index_string.count(".test-css-class")


def test_configure_app_resources(app, test_template):
    # Check that custom stylesheet is not present initially
    assert num_stylesheets(app) == 0

    # Check stylesheet added upon template.layout
    test_template._configure_app(app)
    assert num_stylesheets(app) == 1

    # Check that configuration is idempotent
    test_template._configure_app(app)
    assert num_stylesheets(app) == 1


def test_configure_app_inline_css(app, test_template):
    # Check that special css class is not present initially
    assert num_css_class_entries(app) == 0

    # Check inline css added upon template.layout
    test_template._configure_app(app)
    assert num_css_class_entries(app) == 1

    # Check that adding inline css is idempotent
    test_template._configure_app(app)
    assert num_css_class_entries(app) == 1


def test_configure_app_with_none_css(app, test_template):
    # Check that special css class is not present initially
    assert num_css_class_entries(app) == 0

    # Blank out inline css
    original_index_string = app.index_string
    type(test_template)._inline_css = None

    # Check that nothing crashes and css is not modified
    test_template._configure_app(app)
    assert num_css_class_entries(app) == 0
    assert app.index_string == original_index_string
