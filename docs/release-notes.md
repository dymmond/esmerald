# Release Notes

## 0.5.4

January 3, 2023

### Changed

- Updated version of asyncz to support 0.1.4.
- Fixed dependencies when installing Esmerald based on Asyncz requirements.
- Minor fixes.

## 0.5.3

January 2, 2023

### Changed

- Added support to httpx 0.23.2

## 0.5.2

December 30, 2022

### Changed

- Support for Asyncz 0.1.3

## 0.5.1

December 23, 2022

### Changed

- Add support for Asyncz 0.1.2

## 0.5.0

December 22, 2022

!!! Warning
    This changes might contain some backward incompatibilities if you are already using the
    previous scheduler.

## Changed

- **Deprecated** the integration with `APScheduler` in favour of [Asyncz](https://asyncz.tarsild.io).
- Upgraded the Esmerald official symbol.

!!! Warning
    If you are using the `@scheduler` with the `func` and `identifier` params, please check the
    [documentation](./scheduler/handler.md) to understand how to upgrade to the new scheduler.
    It is almost the same but with some minor changes to the parameters

## 0.4.2

December 16, 2022

### Changed

- Created `BaseModelExtra` parser removing repetition of code across transformers.

### Fix

- Configurations for scheduler being passed as params.
- Scheduler in the slots.

## 0.4.1

December 13, 2022

### Changed

- Added support for Starlette 0.23.1.

## 0.4.0

December 9, 2022

### Changed

- Updated support to Starlette 0.23.0
- Updated the EsmeraldTestClient to support headers.

### Fixed

- [Token](./configurations/jwt.md#token-model) parameters being passed to `python-jose`.
- Update internal references to the JWT.

## 0.3.1

November 28, 2022

### Added

- HashableBaseModel allowing the __hash__ to be done via pydantic BaseModels.

### Changed

- Update transformer model field and functions.

### Fixed

- Minor doc fixes.

## 0.3.0

November 27, 2022

### Changed

- Deprecated kwargs and signature to give place to Esmerald transformers.
- Code cleaning and improved performance by applying pure pydantic models internally.

## 0.2.11

November 21, 2022

### Fixed

- When instantiating an `Esmerald` object, `app_name` should be passed instead of `name`.

## 0.2.10

November 18, 2022

### Changed

- Supporting Starlette version 0.22.0.

### Fixed

- `max_age` from [SessionConfig](./configurations/session.md) allowing negative numbers being passed
and can be used for testing purposes or to clear a session.

## 0.2.9

November 15, 2022

### Fixed

- `redirect_slashes` property added to the main Esmerald object and settings options.

## 0.2.8

November 14, 2022

### Fixed

- `@router` allowing validation for Options for CORS middleware.

## 0.2.7

November 11, 2022

### Added

- Officially supporting python 3.11.

## 0.2.6

November 11, 2022

### Changed

- Removed [Tortoise ORM](./databases/tortoise/tortoise.md#how-to-use) dependency from the main package.
- Removed `asyncpg` from the main package as dependency.

## 0.2.5

November 9, 2022

### Changed

- Removed `auth.py` from security package as is no longer used. This was supposed to go in the release 0.2.4.

## 0.2.4

November 9, 2022

### Changed

- Removed `settings.py` from permissions as it is no longer used.

## 0.2.3

November 5, 2022

### Fixed

- OpenAPI documentation rendering for the same path with different http methods.

## 0.2.2

November 2, 2022.

### Added

- `httpx` and `itsdangerous` dependencies.

## 0.2.1

November 1, 2022.

### Changed

- Removed `archive`.
- Removed unnecessary comments.

### Fixed

- Generation of projects and apps using `esmerald-admin` by removing the clutter.

## 0.2.0

November 1, 2022.

### Added

- `esmerald-admin` entrypoint allowing generating projects and apps via [directives](./management/directives.md).

### Fixed

- Namespace conflicts when importing the `Include` and the `include` internal function.

## 0.1.3

October 26, 2022.

### Changed

- `add_route` - Fixed the way the add_route was managing the paths and import to OpenAPI docs.


## 0.1.2

October 26, 2022.

### Changed

- `add_routes` - Fixed the way the add_route was managing the paths and import to OpenAPI docs.

## 0.1.1

October 25, 2022.

### Changed

- `pyproject.toml` - Added missing dependencies.

## 0.1.0

October 25, 2022.

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
- **Tortoise ORM**: Native support for [Tortoise ORM](./databases/tortoise/tortoise.md).
- **APIView**: Class Based endpoints for your beloved OOP design.
- **JSON serialization/deserialization**: Both UJSON and ORJON support.
- **Lifespan**: Support for the newly lifespan and on_start/on_shutdown events.
- **Dependency Injection**: Like any other great framework out there.
- **Scheduler**: Yes, that's right, it comes with a scheduler for those automated tasks.
- **Simplicity from settings**: Yes, we have a way to make the code even cleaner by introducing settings
based systems.
