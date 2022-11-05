# Release Notes

## 0.2.3

November 5, 2022

### Fixed

- OpenAPI documenation rendering for the same path with differnt http methods.

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
