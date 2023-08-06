# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Context(Component):
    """A Context component.
A component exposing the ability to subscribe, set and update a Glue42 Shared Context.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.
    The ID is used as the context name to subscribe for.

- context (dict; optional):
    Holds the latest context update.

    `context` is a dict with keys:

    - data (dict; optional):
        Current context data.

    - delta (dict; optional)

    - extraData (dict; optional):
        Extra information about this context.

        `extraData` is a dict with keys:

        - isMineUpdate (boolean; optional):
            A flag to indicate whether the current Interop instance
            has updated the context.

        - updaterId (string; optional):
            The peer id of the updating Interop instance.

    - removed (list of strings; optional)

- contextName (string; optional):
    Name of the context to which you want to subscribe. This property
    takes precedence over the component ID.  Use this property if the
    context's name contains the characters '.' or '{' as they are not
    allowed in component IDs.

- set (dict; optional):
    Property for setting a new context value.  All properties of the
    specified context object will be removed and replaced with the
    ones supplied in the data property.  An object that will replace
    the context value completely.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks.

- update (dict; optional):
    Property for updating a shared context with the supplied object.
    Updates only the specified context properties. Any other existing
    context properties will remain intact.  If the context does not
    exist, then it will be created."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'Context'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, contextName=Component.UNDEFINED, context=Component.UNDEFINED, update=Component.UNDEFINED, set=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'context', 'contextName', 'set', 'setProps', 'update']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'context', 'contextName', 'set', 'setProps', 'update']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Context, self).__init__(**args)
