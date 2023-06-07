# Release Notes

## 1.2.4

### Changed

- Updated pyproject.toml keywords.
- Updated to the latest [Starlette 0.28.0](https://www.starlette.io/release-notes/).
- Exception handler logic refactored.

## 1.2.3

### Fixed

- Upgrade Starlette version to >=0.27.0 for a security release. Details on [Starlette's security](https://github.com/encode/starlette/security/advisories/GHSA-v5gw-mw7f-84px)

## 1.2.2

### Fixed

- Exception handler message when `run` directive does not find custom directive properly.

## 1.2.1

### Fixed

- Lifespan generator for the `run` directive.

## 1.2.0

### Changed

- Updated native requirements of the project.
- Removed old core management in favour of click.
- Deprecated `management` package in favour of `directives`. [#83](https://github.com/dymmond/esmerald/pull/83).
- Deprecate `esmerald-admin`. Now you can simply call `esmerald` with the same directives
as before. Simplification via command line [#86](https://github.com/dymmond/esmerald/pull/86).
	- Example:
		- `esmerald createproject <NAME>`
		- `esmerald createpapp <NAME>`

### Added

- Support for Ruff.
- New esmerald core admin management directives [#83](https://github.com/dymmond/esmerald/pull/83).
- New directives client.
- Added rich for command line colours, tables.
- New native directives:
	- [directives](./directives/directives.md#list-available-directives).
	- [runserver](./directives/directives.md#runserver).
	- [show_urls](./directives/directives.md#show-urls).

### Fixed

- Linting and formatting issues with Ruff.

## 1.1.0

### Changed

- Updated support for Starlette 0.26.1
- Updated support for Lifespan [./lifespan.md] events
- Requests url_for parsing the URL type to return string on parsing [#69](https://github.com/dymmond/esmerald/pull/69).
- Esmerald official documentation also available on https://esmerald.dev [#70](https://github.com/dymmond/esmerald/pull/70).
- Updated Github CI to deploy also to https://esmerald.dev [#73](https://github.com/dymmond/esmerald/pull/73)

### Added

- Internal implementation of on_startup and on_shutdown. [#74](https://github.com/dymmond/esmerald/pull/74).
- Added new internal implementation of on_event and add_event_handler functions. [#74](https://github.com/dymmond/esmerald/pull/74).
- Missing documentation about the background tasks [#71](https://github.com/dymmond/esmerald/pull/71)
- Documentation for lifespan events [#72](https://github.com/dymmond/esmerald/pull/72)
- Added condition to allow cached_properties from the EsmeraldAPISettings and in the settings without raising an Exception.
- New handlers. OPTIONS, HEAD and TRACE. Check out the  [handlers](./routing/handlers.md) for more details.

### Fixed

- New Starlette Lifespan [#75](https://github.com/dymmond/esmerald/pull/75). This is now also available to be done in the same way Starlette does. Internally Esmerald also implements the on_startup and on_shutdown but that is an unique implementation. This implementation follows the same pattern as the official [Starlette Bridge](https://starlette-bridge.tarsild.io/)

## 1.0.0

### Changed

- ChildEsmerald now supports the parent which means it can share middlewares and interceptors
across main application and children.

    !!! Note
        Prior to version 1.0.0, sharing resources between Esmerald and ChildEsmerald was not allowed
        and it needed to be treated as completely isolated application. In the version 1.0.0 you can
        still isolate them but you can also share resources.


## 0.15.0

### Added

-  Esmerald [Pluggables](./pluggables.md) [#60](https://github.com/dymmond/esmerald/pull/60).

	This is the feature for the esmerald ecosystem that allows you to create plugins and extensions for any application
	as well as distribute them as installable packages.

- New [add_child_esmerald](./routing/router.md#add_child_esmerald) allowing adding via function, ChildEsmerald [#61](https://github.com/dymmond/esmerald/pull/61).

	Add child esmeralds via functions once the application is created and dynamically.


## 0.14.0

### Added

- Brand new support for [Saffier](https://saffier.tarsild.io). A brand new ORM running
on the top of SQLAlchemy in an async fashion.
- New `base_user` and `middleware` support for Saffier with Esmerald.
- New docs regarding the [Saffier](https://esmerald.dymmond.com/databases/saffier/motivation/) integration.
Those include also an example how to use it.

### Changed

- **Breaking change** - Removed support for python 3.7. This was blocking the technology from
evolving at a normal pace and blocking security patches from being properly applied.

### Fixed

- Old package versioning conflicts.

## 0.13.0

### Changed

- Added support for Starlette 0.25.0

### Fixed

- Internal mapping types [#45](https://github.com/dymmond/esmerald/pull/56)

## 0.12.0

### Changed

- Added support for Starlette 0.24.0.

### Fixed

- `debug` parameter regression.

## 0.11.2

### Changed

- Code clean for responses and encoders.
- JWTConfig leeway parameter to accept int and str.

### Fixed

- `ujson` dumps parameter error.

## 0.11.1

### Changed

- Improved `OrJSON`, `UJSON`, `ORJSONResponse` and `UJSONResponse` when importing dependency.

## 0.11.0

### Added

To make esmerald more optional and feature modular, this release brings some backwards
incompatibilities that should be addressed when moving to this version. Check out
the dcumentation for more details if this release notes doesn't cover it all.

### Changed

- Moved `UJSON`, `UJSONResponse`, `OrJSON` and `ORJSONResponse` to be optional dependencies [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `ORJSONResponse` to `from esmerald.responses.encoders import ORJSONResponse` [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `UJSONResponse` to `from esmerald.responses.encoders import UJSONResponse` [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `OrJSON` to `from esmerald.datastructures.encoders import OrJSON` [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `UJSON` to `from esmerald.datastructures.encoders import UJSON` [#45](https://github.com/dymmond/esmerald/pull/45).
- Moved the scheduler to optional installation with `pip install esmerald[schedulers]` [#45](https://github.com/dymmond/esmerald/pull/45).

#### Backwards compatibility
This is only applied for those who have esmerald prior to `0.11.0`.
If you already had template configurations, jwt, schedulers or all the features you need to update the imports to:

- **TemplateConfig**:
    ```python
    from esmerald.config.template import TemplateConfig
    ```

- **JWTConfig**:
    ```python
    from esmerald.config.jwt import JWTConfig
    ```
- Scheduler class is now imported directly from `asyncz`:
    ```python
    from asyncz.schedulers import AsyncIOScheduler # for the Scheduler class
    from asyncz.contrib.esmerald.decorator import scheduler # for the decorator
    ```

## 0.10.0

### Added

- `add_apiview` to the Esmerald class.
- [JSON](./responses.md#json), [OrJSON](./responses.md#orjson) and [UJSON](./responses.md#ujson) responses [#44](https://github.com/dymmond/esmerald/pull/44).

### Changed

- `Template` now accepts an extra `alternative_template` for the cases of raising TemplateNotFound [#44](https://github.com/dymmond/esmerald/pull/44).
- Removed `handle_status_code` internal functionality as it is no longer used.

### Fixed

- `handler` type for Gateway and WebsocketGateway.
- The split bytes intead of b''.

## 0.9.0

### Added

- `DirectInjects` object for the direct dependency injection without using Inject and `dependencies` from the handler [#42](https://github.com/dymmond/esmerald/pull/42).

### Fixed

- `include_in_schema` on a Gateway level for OpenAPI specification [#42](https://github.com/dymmond/esmerald/pull/42).
- `redirect_slashes` when instantiating an Esmerald/ChildEsmerald application wasn't
validating the value properly.
- TemplateNotFound raised when a template is not found [#42](https://github.com/dymmond/esmerald/pull/42).
- jinja2 Environment to have autoescape by default [#43](https://github.com/dymmond/esmerald/pull/43)

## 0.8.1

### Added

- Added Template and Redirect to app imports.
This was supposed to go in the release 0.8.0 but somehow it was missed.

## 0.8.0

January 22, 2023

### Added

- New `File` and `Form` params to Esmerald.
- Add new `Injects` as parameter function.
- Add new `ArbitraryHashableBaseModel` to handle the `Inject` with arbitrary types.
- Add new [settings_config](./application/settings.md#the-settings_config) parameter. [#40](https://github.com/dymmond/esmerald/pull/40).

### Changed

- Removed unused internal parameters for old functions.
- `scheduler_class` is now a property in the EsmeraldSettings. This allows to override fields
without issues.
- Deprecate `settings` parameter from `RequestSettingsMiddleware`.

### Fixed

- Error messages being thrown.
- Fix `enable_openapi` boolean for ChildEsmerald and submodules and `include_in_schema` for Include [#37](https://github.com/dymmond/esmerald/pull/37)
- Fix types for OpenAPI for applications that are subclasses of Esmerald or ChildEsmerald [#38](https://github.com/dymmond/esmerald/pull/38)

## 0.7.0

### Added

- New [RequestSettingsMiddleware](./middleware/middleware.md#requestsettingsmiddleware) allowing accessing the settings of the application
from the request.
- Settings resolution for the whole application [#30](https://github.com/dymmond/esmerald/issues/30).

### Changed

- Request now has a `settings` property that can be accessed upon the installation
of the [RequestSettingsMiddleware](./middleware/middleware.md#requestsettingsmiddleware).

### Fixed

- `license` reference upon instantiation from the settings.

## 0.6.2

### Changed

- Add support for kwargs in the Dao and AsyncDAO [#28](https://github.com/dymmond/esmerald/issues/28)

### Fixed

- Mypy references for the Gateway and WebsocketGateway being added to the handler.
- References to the Esmerald types causing the IDE to misread them.

## 0.6.1

### Changed

- Include now supports its own middleware handling and loading [#26](https://github.com/dymmond/esmerald/pull/26).
This hange make sure that the parent level doesn't get affected and do not influence the middleware
of other includes.
- [JWTConfig](./configurations/jwt.md) `api_key_header` now defaults to `X_API_TOKEN`.

### Fixed

- JWT Token encoding and decoding [#26](https://github.com/dymmond/esmerald/pull/26).
- JWT middleware handling the headers

## 0.6.0

### Added

- Added support to the new [Interceptors](./interceptors.md). [#25](https://github.com/dymmond/esmerald/pull/25)

### Changed

- Added support to httpx 0.23.3
- Updated document references pointing to [Interceptors](./interceptors.md).

### Fixed

- `JWTAuthMiddleware` from `esmerald.contrib.auth.tortoise.middleware` raising exception
on invalid token.
- Fixed code references to the `Void`.

## 0.5.4

### Changed

- Updated version of asyncz to support 0.1.4.
- Fixed dependencies when installing Esmerald based on Asyncz requirements.
- Minor fixes.

## 0.5.3

### Changed

- Added support to httpx 0.23.2

## 0.5.2

### Changed

- Support for Asyncz 0.1.3

## 0.5.1

### Changed

- Add support for Asyncz 0.1.2

## 0.5.0

!!! Warning
    This changes might contain some backward incompatibilities if you are already using the
    previous scheduler.

## Changed

- **Deprecated** the integration with `APScheduler` in favour of [Asyncz](https://asyncz.tarsild.io).
[#15](https://github.com/dymmond/esmerald/pull/15)
- Upgraded the Esmerald official symbol.

!!! Warning
    If you are using the `@scheduler` with the `func` and `identifier` params, please check the
    [documentation](./scheduler/handler.md) to understand how to upgrade to the new scheduler.
    It is almost the same but with some minor changes to the parameters

## 0.4.2

### Changed

- Created `BaseModelExtra` parser removing repetition of code across transformers.

### Fix

- Configurations for scheduler being passed as params.
- Scheduler in the slots.

## 0.4.1

### Changed

- Added support for Starlette 0.23.1.

## 0.4.0

### Changed

- Updated support to Starlette 0.23.0
- Updated the EsmeraldTestClient to support headers.

### Fixed

- [Token](./configurations/jwt.md#token-model) parameters being passed to `python-jose`.
- Update internal references to the JWT.

## 0.3.1

### Added

- HashableBaseModel allowing the __hash__ to be done via pydantic BaseModels.

### Changed

- Update transformer model field and functions.

### Fixed

- Minor doc fixes.

## 0.3.0

### Changed

- Deprecated kwargs and signature to give place to Esmerald transformers.
- Code cleaning and improved performance by applying pure pydantic models internally.

## 0.2.11

### Fixed

- When instantiating an `Esmerald` object, `app_name` should be passed instead of `name`.

## 0.2.10

### Changed

- Supporting Starlette version 0.22.0.

### Fixed

- `max_age` from [SessionConfig](./configurations/session.md) allowing negative numbers being passed
and can be used for testing purposes or to clear a session.

## 0.2.9

### Fixed

- `redirect_slashes` property added to the main Esmerald object and settings options.

## 0.2.8

### Fixed

- `@router` allowing validation for Options for CORS middleware.

## 0.2.7

### Added

- Officially supporting python 3.11.

## 0.2.6

### Changed

- Removed [Tortoise ORM](./databases/tortoise/motivation.md#how-to-use) dependency from the main package.
- Removed `asyncpg` from the main package as dependency.

## 0.2.5

### Changed

- Removed `auth.py` from security package as is no longer used. This was supposed to go in the release 0.2.4.

## 0.2.4

### Changed

- Removed `settings.py` from permissions as it is no longer used.

## 0.2.3

### Fixed

- OpenAPI documentation rendering for the same path with different http methods.

## 0.2.2

### Added

- `httpx` and `itsdangerous` dependencies.

## 0.2.1

### Changed

- Removed `archive`.
- Removed unnecessary comments.

### Fixed

- Generation of projects and apps using `esmerald` by removing the clutter.

## 0.2.0

### Added

- `esmerald` entrypoint allowing generating projects and apps via [directives](./directives/directives.md).

### Fixed

- Namespace conflicts when importing the `Include` and the `include` internal function.

## 0.1.3

### Changed

- `add_route` - Fixed the way the add_route was managing the paths and import to OpenAPI docs.


## 0.1.2

### Changed

- `add_routes` - Fixed the way the add_route was managing the paths and import to OpenAPI docs.

## 0.1.1

### Changed

- `pyproject.toml` - Added missing dependencies.

## 0.1.0

This release is the first release of Esmerald and it contain all the essentials to start a project from the simplest
version to the most advanced.

### Added

- **Fluid and Fast**: Thanks to Starlette and Pydantic.
- **Fast to develop**: Thanks to the simplicity of design, the development times can be reduced exponentially.
- **Intuitive**: If you are used to the other frameworks, Esmerald is a no brainer to develop.
- **Easy**: Developed with design in mind and easy learning.
- **Short**: With the OOP available natively there is no need for code duplication. SOLID.
- **Ready**: Get your application up and running with production-ready code.
- **OOP and Functional**: Design APIs in any desired way. OOP or Functional is available.
- **Async and Sync**: Do you prefer sync or async? You can have both.
- **Middleware**: Apply middlewares on the application level or API level.
- **Exception Handlers**: Apply exception handlers on any desired level.
- **Permissions**: Apply specific rules and permissions on each API.
- **DAO and AsyncDAO**: Avoid database calls directly from the APIs. Use business objects instead.
- **Tortoise ORM**: Native support for [Tortoise ORM](./databases/tortoise/motivation.md).
- **APIView**: Class Based endpoints for your beloved OOP design.
- **JSON serialization/deserialization**: Both UJSON and ORJON support.
- **Lifespan**: Support for the newly lifespan and on_start/on_shutdown events.
- **Dependency Injection**: Like any other great framework out there.
- **Scheduler**: Yes, that's right, it comes with a scheduler for those automated tasks.
- **Simplicity from settings**: Yes, we have a way to make the code even cleaner by introducing settings
based systems.
