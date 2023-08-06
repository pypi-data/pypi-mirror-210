# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Glue42(Component):
    """A Glue42 component.
The Glue42 initializer component. The component should be placed at the root of the application.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (optional):
    The ID of this component. Used to identify Dash components in
    callbacks.  The ID must be unique across all components in an app.

- fallback (a list of or a singular dash component, string or number; optional):
    An optional component to display while initializing Glue42.

- glueReady (boolean; optional):
    Indicates whether Glue42 JS has initialized.

- isEnterprise (boolean; optional):
    Indicates whether the application is running in Glue42 Enterprise
    or Glue42 Core (browser).

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash in order to make them available for callbacks.

- settings (dict; default {    type: CoreApplicationTypes.Client,}):
    Optional. A \"settings\" object containing configuration objects
    for the Glue42 library.

    `settings` is a dict with keys:

    - desktop (dict; optional):
        Optional. An object with one property: config. The config
        property accepts a configuration object for the
        @glue42/desktop library used in Glue42 Enterprise.  You should
        define this object if your app is a Glue42 Enterprise app.

        `desktop` is a dict with keys:

        - config (dict; optional)

    - type (a value equal to: CoreApplicationTypes.Client, CoreApplicationTypes.Platform; optional):
        Optional. Accepts either \"platform\" or \"client\" as a
        value. Specifies whether this is a Main app or a Web Client in
        the context of Glue42 Core. The default is \"client\".

    - web (dict; optional):
        Optional. An object with one property: config. The config
        property accepts a configuration object for the Glue42 Web
        library.  You should define this object if your app is a Web
        Client.

        `web` is a dict with keys:

        - config (dict; optional)

    - webPlatform (dict; optional):
        Optional. An object with one property: config. The config
        property accepts a configuration object for the Web Platform
        library.  You should define this object if your app is a Main
        app in the context of Glue42 Core.

        `webPlatform` is a dict with keys:

        - config (dict; optional)"""
    _children_props = ['fallback']
    _base_nodes = ['fallback', 'children']
    _namespace = 'dash_glue42'
    _type = 'Glue42'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, isEnterprise=Component.UNDEFINED, settings=Component.UNDEFINED, fallback=Component.UNDEFINED, glueReady=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'fallback', 'glueReady', 'isEnterprise', 'setProps', 'settings']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'fallback', 'glueReady', 'isEnterprise', 'setProps', 'settings']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Glue42, self).__init__(children=children, **args)
