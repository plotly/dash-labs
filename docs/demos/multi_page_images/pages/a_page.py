import dash

dash.register_page(
    __name__,
    title="(a_page) The title, headline or name of the page",
    description="(a_page) A short description or summary 2-3 sentences",
)


def layout():
    return """    
    This page uses a generic image.  No image is specified and there is no image that matches
    the module name in the assets folder, so it uses `app.jpeg` or `logo.jpeg` if no `app.jpeg` exists.
        """
