---
dash.register_page(
    __name__,
    name="Intro to multi-page apps",
    order=99,
    layout=MarkdownAIO(
        "pages/multi_page_apps/intro.md",
        exec_code=False,
    ),
)
---

## TODO

- describe the basics
- step by step guide on how to convert a group of single page apps into a multi-page app