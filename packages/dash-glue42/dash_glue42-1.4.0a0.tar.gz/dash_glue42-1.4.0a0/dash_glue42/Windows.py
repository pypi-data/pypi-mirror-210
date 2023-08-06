# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Windows(Component):
    """A Windows component.
A component exposing the Glue42 Window Management API.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- open (dict; optional):
    Property to open a new Glue42 Window.

    `open` is a dict with keys:

    - name (string; required):
        A unique window name.

    - options (dict; optional):
        Options for creating a window.

    - url (string; required):
        The window URL.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'Windows'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, open=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'open', 'setProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'open', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Windows, self).__init__(**args)
