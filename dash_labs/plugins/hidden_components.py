from types import MethodType


class HiddenComponents:
    def plug(self, app):
        app._extra_hidden_components = []
        app._layout_value = MethodType(_layout_value, app)


def _layout_value(self):
    layout = self._layout() if self._layout_is_function else self._layout

    # Add hidden components
    if hasattr(self, "_extra_hidden_components"):
        for c in self._extra_hidden_components:
            if c not in layout.children:
                layout.children.append(c)

    return layout
