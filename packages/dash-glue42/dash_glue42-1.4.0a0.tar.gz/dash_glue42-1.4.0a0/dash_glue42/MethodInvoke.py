# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MethodInvoke(Component):
    """A MethodInvoke component.
A component exposing the ability to invoke a Glue42 Interop method.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- invoke (dict; optional):
    Property for invoking an Interop method.

    `invoke` is a dict with keys:

    - argumentObj (dict; optional):
        Invocation arguments.

    - definition (string | dict; required):
        Method name or an object holding the method name, signature
        and other properties of the method.

    - invocationId (string; optional):
        An ID to correlate the method invocation to its result.

    - options (dict; optional):
        Property for specifying a timeout for discovering the invoked
        Interop method  and a timeout for receiving a response from
        the method.

        `options` is a dict with keys:

        - methodResponseTimeoutMs (number; optional):
            Timeout to wait for a method reply.

        - waitTimeoutMs (number; optional):
            Timeout to discover the method, if not immediately
            available.

    - target (string | dict | list of dicts; optional):
        Property for specifying a target Interop server.

- result (dict; optional):
    Property that returns a result or an error from a method
    invocation.

    `result` is a dict with keys:

    - error (dict; optional):
        An error for method invocation failure. Has a `None` value
        unless the invocation fails.

    - invocationId (string; optional):
        An ID to correlate the method invocation to its result.

    - invocationResult (dict; optional):
        The actual result from the method invocation. If the
        invocation fails, a `None` value is set.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'MethodInvoke'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, result=Component.UNDEFINED, invoke=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'invoke', 'result', 'setProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'invoke', 'result', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(MethodInvoke, self).__init__(**args)
