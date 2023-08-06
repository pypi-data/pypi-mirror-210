# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MethodRegister(Component):
    """A MethodRegister component.
A component exposing the ability to register a Glue42 Interop method.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- definition (string | dict; optional):
    Method name or an object holding the method name, signature and
    other properties of the method.

- error (dict; optional):
    An error to return in case the method registration fails.

- invoke (dict; optional):
    Property for invoking an Interop method handler.

    `invoke` is a dict with keys:

    - args (dict; optional):
        Invocation arguments.

    - caller (dict; optional):
        The Interop client which has invoked the method.

    - invocationId (string; optional):
        An ID to correlate the method invocation to its result.

- loading_state (dict; optional):
    Dash-assigned prop holding the loading state object coming from
    `dash-renderer`.

    `loading_state` is a dict with keys:

    - is_loading (boolean; optional):
        Determines whether the component is loading or not.

- methodResponseTimeoutMs (number; default 30000):
    Timeout to wait for the handler to reply. Set this prop to
    configure how much time the component should wait for a response
    from the Dash backend.  Default is 30000 ms.

- result (dict; optional):
    Property for returning a result or an error to the caller.

    `result` is a dict with keys:

    - error (dict; optional):
        Holds the returned error when the method invocation has
        failed.

    - invocationId (string; optional):
        An ID to correlate the method invocation to its result.

    - invocationResult (dict; optional):
        The actual result from the method invocation.

- returns (boolean; default False):
    Specify whether the method is void or returns a result.  Default
    is `False`.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'MethodRegister'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, loading_state=Component.UNDEFINED, definition=Component.UNDEFINED, methodResponseTimeoutMs=Component.UNDEFINED, error=Component.UNDEFINED, returns=Component.UNDEFINED, result=Component.UNDEFINED, invoke=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'definition', 'error', 'invoke', 'loading_state', 'methodResponseTimeoutMs', 'result', 'returns', 'setProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'definition', 'error', 'invoke', 'loading_state', 'methodResponseTimeoutMs', 'result', 'returns', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(MethodRegister, self).__init__(**args)
