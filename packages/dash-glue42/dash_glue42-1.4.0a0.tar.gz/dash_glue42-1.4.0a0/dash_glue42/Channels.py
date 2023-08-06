# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Channels(Component):
    """A Channels component.
A component exposing the Glue42 Channels API.

Keyword arguments:

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- all (list of strings; optional):
    A list of all Channel names.

- join (dict; optional):
    Property for joining a new channel by name. Leaves the current
    channel.

    `join` is a dict with keys:

    - name (string; required):
        The name of the channel to join.

- leave (dict; optional):
    Property for leaving the current channel.

- list (list; optional):
    A list of all Channel contexts.

- my (optional):
    Holds the current Channel context. Value will be None when not
    joined to a channel.

- publish (dict; optional):
    Property for publishing new data to a Channel.

    `publish` is a dict with keys:

    - data (boolean | number | string | dict | list; optional):
        Data object with which to update the channel context.

    - name (string; optional):
        The name of the channel to be updated. If not provided will
        update the current channel.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_glue42'
    _type = 'Channels'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, list=Component.UNDEFINED, all=Component.UNDEFINED, my=Component.UNDEFINED, publish=Component.UNDEFINED, join=Component.UNDEFINED, leave=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'all', 'join', 'leave', 'list', 'my', 'publish', 'setProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'all', 'join', 'leave', 'list', 'my', 'publish', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Channels, self).__init__(**args)
