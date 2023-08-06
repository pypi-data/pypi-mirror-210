# Changelog

## [1.4.0a0] - 2023-05-27

### Added

- Exposed a library settings object via the global object glue42dash (window.glue42dash.libSettings), which enables apps to override factory functions and provide a list of glue libraries which will be initiated internally and provide access to specific functionalities.
- Enable the Glue42 component to render children without real Glue42 JS initialization when a fake glue object is returned from the factory function with a property "skipInit".
- Added "glueReady" prop to the Glue42 component.
- Added "contextName" prop to the Context component. The new prop is meant to target a limitation of component IDs to contain '.' and '{' characters.

## [1.3.0a0] - 2023-05-02

### Added

- Attach glueInstancePromise to the global glue42dash object.

## [1.2.0a1] - 2023-05-02

### Changed

- Updated @glue42/react-hooks package.

## [1.2.0a0] - 2023-03-30

### Added

- Attach glue42dash object to the global window object which includes lib version and glueInstance.

## [1.1.0a0] - 2023-02-14

### Added

- Add extra info to Channels and Context to indicate Interop updater instance.

## [1.0.0a3] - 2022-11-17

### Changed

- Updated Dash to version 2.
- Updated @glue42/react-hooks packages.

## [1.0.0a2] - 2022-11-16

### Changed

- Updated Glue42 component PropTypes.

## [1.0.0a1] - 2022-08-24

### Changed

- Updated components PropTypes.

## [1.0.0a0] - 2021-08-27

### Changed

- Breaking changes. See official documentation - https://docs.glue42.com/getting-started/how-to/glue42-enable-your-app/dash/index.html.

## [0.0.3] - 2020-08-20

### Changed

- Improved error handing in the `methodInvoke` and `methodRegister` components.
- The `definition` property type of `methodRegister` accepts either a string or an object.
- Added more reference comments to the component properties.

## [0.0.2] - 2020-07-31

### Added

- Leaving the current Channel.
- Joining a Channel.
- Getting the list of available Channels.

### Changed

- Raising notifications through the Glue42 Notifications API.

## [0.0.1] - 2020-07-29

### Added

- Invoking Interop methods.
- Registering Interop methods.
- Window opening.
- GNS notification raising.
- Glue42 Contexts - subscribing and updating a shared context.
- Glue42 Channels - subscribing to a Channel and publishing data to the current Channel.
