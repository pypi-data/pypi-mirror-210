# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Contexts(Component):
    """A Contexts component.
A component exposing the Glue42 Contexts API.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- destroy (dict; optional):
    Destroys a context and all the data associated with it.

    `destroy` is a dict with keys:

    - name (string; required):
        Name of the context to be removed.

- set (dict; optional):
    Property for setting a new context value.  All properties of the
    specified context object will be removed and replaced with the
    ones supplied in the data property.  An object that will replace
    the context value completely.

    `set` is a dict with keys:

    - data (dict; optional):
        The object that will be applied to the context.

    - name (string; required):
        Name of the context to be replaced.

- setPath (dict; optional):
    Sets a path in the context to some value. Use this to update
    values that are not on top level in the context.

    `setPath` is a dict with keys:

    - data (boolean | number | string | dict | list; optional):
        The object that will be applied to the context.

    - name (string; required):
        Name of the context to be updated.

    - path (optional):
        Path to be updated. Path should be in the format
        \"prop1.prop2\".

- setPaths (dict; optional):
    Sets multiple paths in the context to some values in a single
    command.

    `setPaths` is a dict with keys:

    - name (string; required):
        Name of the context to be updated.

    - paths (list; required):
        Array of paths and their values to be updated.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks.

- update (dict; optional):
    Property for updating a shared context with the supplied object.
    Updates only the specified context properties. Any other existing
    context properties will remain intact.  If the context does not
    exist, the it will be created.

    `update` is a dict with keys:

    - data (dict; optional):
        The object that will be applied to the context.

    - name (string; required):
        Name of the context to be updated."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'Contexts'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, update=Component.UNDEFINED, set=Component.UNDEFINED, setPath=Component.UNDEFINED, setPaths=Component.UNDEFINED, destroy=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'destroy', 'set', 'setPath', 'setPaths', 'setProps', 'update']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'destroy', 'set', 'setPath', 'setPaths', 'setProps', 'update']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Contexts, self).__init__(**args)
