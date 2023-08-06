# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Notifications(Component):
    """A Notifications component.
A component exposing the Glue42 Notifications API.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- maxActions (number; optional):
    The maximum number of actions supported by the UI toast.

- raise (dict; optional):
    Property to raise a new notification.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'Notifications'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, maxActions=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'maxActions', 'raise', 'setProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'maxActions', 'raise', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Notifications, self).__init__(**args)
