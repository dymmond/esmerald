---
hide:
  - navigation
---

# Esmerald

<p align="center">
  <a href="https://esmerald.dev"><img src="https://res.cloudinary.com/dymmond/image/upload/v1673619342/esmerald/img/logo-gr_z1ot8o.png" alt='Esmerald'></a>
</p>

<p align="center">
    <em>🚀 Масштабируемость, производительность, легкость в изучении и написании кода, подходит для любого приложения. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/dymmond/esmerald/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/dymmond/esmerald/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/esmerald" target="_blank">
    <img src="https://img.shields.io/pypi/v/esmerald?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/esmerald" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/esmerald.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Документация**: [https://esmerald.dev](https://www.esmerald.dev) 📚

**Исходный код**: [https://github.com/dymmond/esmerald](https://github.com/dymmond/esmerald)

---
Esmerald — это современный, мощный, гибкий и высокопроизводительный веб-фреймворк, созданный для построения
не только API, но и полноценных масштабируемых приложений — от самых малых до уровня крупных компаний.

Esmerald разрабатывался для Python 3.9+ и использует стандартные подсказки типов (type hints) Python,
основан на широко
известном [Lilya](https://github.com/dymmond/lilya) и [Pydantic](https://github.com/samuelcolvin/pydantic)/[msgspec](https://jcristharif.com/msgspec/).

!!! Success
    **Официально поддерживается только последняя выпущенная версия**.

## Мотивация

Существуют отличные фреймворки такие, как FastAPI, Flama, Flask, Django и другие, решающие большинство
повседневных задач для 99% приложений, но оставляющие тот 1%, который обычно связан со структурой и
бизнес-логикой, без особых решений.

Esmerald черпает вдохновение в этих фреймворках и обладает всеми их известными возможностями,
но также учитывает потребности бизнеса.
Например, Starlite вдохновил на создание трансформеров и моделей Signature, что помогло интеграции с Pydantic.
FastAPI вдохновил дизайн API, Django — систему разрешений, Flask — простоту,
NestJS — контроллеры и многое другое.

Для качественной работы всегда требуется как драйвер, так и источник вдохновения.

## Требования

* Python 3.9+

Esmerald не был бы возможен без следующих двух компонентов:

* <a href="https://lilya.dev/" class="external-link" target="_blank">Lilya</a>
* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>

## Установка

```shell
$ pip install esmerald
```

Для работы в продакшене также потребуется ASGI сервер, рекомендуем [Uvicorn](https://www.uvicorn.org), но выбор остается за вами.

```shell
$ pip install uvicorn
```

**Поддержка встроенного планировщика:**:

```shell
$ pip install esmerald[schedulers]
```

**Поддержка JWT, используемого внутри Esmerald:**:

```shell
$ pip install esmerald[jwt]
```

**Для использования клиента тестирования Esmerald:**:

```shell
$ pip install esmerald[test]
```

**Для использования оболочки Esmerald:**:

Подробнее [здесь](./directives/shell.md) по теме в [документации](./directives/shell.md).

```shell
$ pip install esmerald[ipython] # default shell
$ pip install esmerald[ptpython] # ptpython shell
```

### Начало проекта с использованием директив

!!! Warning
    Директивы рассчитаны на опытных пользователей, которые уже знакомы с Esmerald (или Python в целом),
    или если использование директив не вызывает затруднений. Если пока не чувствуете уверенности, продолжайте
    изучать документацию и знакомиться с Esmerald.

Чтобы начать Esmerald проект с простой предложенной структурой, выполните:

```shell
esmerald createproject <YOUR-PROJECT-NAME> --simple
```

Это создаст каркас проекта с некоторыми предопределенными файлами для простого запуска приложения Esmerald.

Также будет создан файл для тестов с использованием EsmeraldTestClient, так что выполните:

```shell
$ pip install esmerald[test]
```

Эту часть можно пропустить, если не хотите использовать EsmeraldTestClient.

Подробная [информация](./directives/directives.md) об этой директиве и примерах ее использования.

!!! Warning
    Запуск этой [директивы](./directives/directives.md) создает только каркас проекта, и для его
    запуска потребуются дополнительные данные.
    Этот каркас лишь предоставляет структуру файлов для начала работы, **но не является обязательным**.

## Основные функции
* **Быстрый и эффективный**: Благодаря Lilya и Pydantic/msgpec.
* **Быстрое развитие**: Простота дизайна значительно сокращает время разработки.
* **Интуитивно понятный**: Если знакомы с другими фреймворками, работать с Esmerald не составит труда.
* **Простота**: Создан с учетом удобства и легкости в изучении.
* **Компактный**: Благодаря встроенной поддержке ООП нет необходимости дублировать код. Поддержка SOLID.
* **Готовый к работе**: Приложение запускается с готовым к продакшену кодом.
* **ООП и функциональный стиль**: Проектируйте API любым удобным способом, поддержка ООП и функционального стиля.
* **Асинхронный и синхронный**: Поддерживает как синхронный, так и асинхронный режимы.
* **Middleware**: Применяйте middleware на уровне приложения или API.
* **Обработчики исключений**: Применяйте обработчики на любом уровне.
* **Permissions**: Применяйте правила и permissions для каждого API.
* **Interceptors**: Перехватывайте запросы и добавляйте логику перед обработкой.
* **Плагины**: Создавайте плагины для Esmerald и интегрируйте их в любое приложение, или опубликуйте свой пакет.
* **DAO и AsyncDAO**: Избегайте вызовов базы данных напрямую из API, используйте бизнес-объекты.
* **Поддержка ORM**: Поддержка [Saffier][saffier_orm] и [Edgy][_orm].
* **Поддержка ODM**: Поддержка [Mongoz][mongoz_odm].
* **APIView**: Контроллеры в виде классов.
* **JSON сериализация/десериализация**: Поддержка UJSON и ORJSON.
* **Lifespan**: Поддержка lifespan Lilya.
* **Внедрение зависимостей**: Как в любом хорошем фреймворке.
* **Планировщик**: Поддержка задач в фоне.
* **Настройки**: Поддержка системы настроек для чистоты кода.
* **msgspec** — поддержка `msgspec`.

## Отношение к Lilya и другим фреймворкам

Esmerald использует Lilya. Это решение обусловлено высокой производительностью и отсутствием проблем с маршрутизацией.

Esmerald поощряет стандартные практики и подходы к дизайну, что позволяет использовать его как для малых,
так и для крупных приложений, не испытывая проблем с масштабируемостью.

## Быстрый старт

Пример как быстро начать работу с Esmerald.
Для быстрого старта используйте `uvicorn`.

```python
#!/usr/bin/env python
import uvicorn

from esmerald import Esmerald, Gateway, JSONResponse, Request, get


@get()
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Esmerald"})


@get()
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


@get()
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


app = Esmerald(
    routes=[
        Gateway("/esmerald", handler=welcome),
        Gateway("/esmerald/{user}", handler=user),
        Gateway("/esmerald/in-request/{user}", handler=user_in_request),
    ]
)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

Затем вы можете получить доступ к endpoints.

### Использование Esmerald в качестве декоратора

Чтобы быстро начать работу с Esmerald, вы также можете использовать его как декоратор. Вот как это
сделать на примере с `uvicorn`.


```python
#!/usr/bin/env python
import uvicorn

from esmerald import Esmerald, Gateway, JSONResponse, Request, get


app = Esmerald()


@app.get("/esmerald")
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Esmerald"})


@app.get("/esmerald/{user}")
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


@app.get("/esmerald/in-request/{user}")
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

## Настройки

Как и в любом другом фреймворке, при запуске приложения множество [настроек](./application/settings.md)
можно или необходимо передать главному объекту, что иногда выглядит сложно и неудобно для поддержки и восприятия.

Esmerald изначально учитывает [настройки](./application/settings.md). Набор параметров по умолчанию можно
изменить, используя собственный модуль настроек, но при этом вы также можете использовать классический подход,
передавая все параметры непосредственно при создании экземпляра Esmerald.

**Пример классического подхода**:

```python
from example import ApplicationObjectExample

# ExampleObject — это экземпляр другого приложения,
# и он служит только в качестве примера

app = ApplicationObjectExample(setting_one=..., setting_two=..., setting_three=...)

```

Вдохновленный замечательным [Django](https://www.djangoproject.com/) и используя pydantic,
Esmerald предоставляет объект по умолчанию, готовый к использованию сразу «из коробки».

**Esmerald**:

```python
from esmerald import Esmerald


app = Esmerald()

```

И это все! **Все настройки по умолчанию загружаются автоматически**! Почему?
Потому что **приложение ищет переменную окружения `ESMERALD_SETTINGS_MODULE` для запуска**,
и если она не найдена, используются глобальные настройки приложения. Это просто, но можно ли
переопределить их внутри объекта? Да, конечно.

```python
from esmerald import Esmerald

app = Esmerald(app_name='My App', title='My title')

```

То же самое, что и классический подход.

Давайте поговорим о [модуле настроек Esmerald](#esmerald-settings-module).

### Модуль настроек Esmerald

При запуске приложения система ищет переменную окружения
`ESMERALD_SETTINGS_MODULE`. Если переменная не указана, система по умолчанию использует настройки
`EsmeraldAPISettings` и запускается.

### Пользовательские настройки

В наше время важно разделять настройки по окружениям и стандартных настроек Esmerald будет недостаточно
для любого приложения.

Настройки соответствуют стандарту pydantic и, следовательно, совместимы с Esmerald.
Система предоставляет несколько значений по умолчанию, которые можно использовать сразу, хотя это необязательно.
Окружение по умолчанию — **production**.

```python
from esmerald import EsmeraldAPISettings
from esmerald.conf.enums import EnvironmentType


class Development(EsmeraldAPISettings):
    app_name: str = 'My app in dev'
    environment: str = EnvironmentType.DEVELOPMENT

```

**Загрузка настроек в ваше приложение Esmerald**:

Предположим, ваше приложение Esmerald находится в файле `src/app.py`.

=== "MacOS & Linux"

    ```console
    ESMERALD_SETTINGS_MODULE='myapp.settings.Development' python -m src.app.py
    ```

=== "Windows"

    ```console
    $env:ESMERALD_SETTINGS_MODULE="myapp.settings.Development"; python -m src.app.py
    ```

## Gateway, WebSocketGateway и Include

Lilya предлагает классы `Path` для простых назначений путей, но это также очень ограничивает,
если у вас есть что-то более сложное. Esmerald расширяет эту функциональность и добавляет немного
'стиля', улучшая её с помощью [Gateway](./routing/routes.md#gateway),
[WebSocketGateway](./routing/routes.md#websocketgateway) и [Include](./routing/routes.md#include).

Эти специальные объекты позволяют происходить всей магии Esmerald.


**Для классического, прямого подхода в одном файле**:

=== "In a nutshell"

    ```python title='src/app.py'
    from esmerald import Esmerald, Gateway, JSONResponse, Request, Websocket, WebSocketGateway, get, status


    @get(status_code=status.HTTP_200_OK)
    async def home() -> JSONResponse:
        return JSONResponse({
            "detail": "Hello world"
        })


    @get()
    async def another(request: Request) -> dict:
        return {
            "detail": "Another world!"
        }


    @websocket(path="/{path_param:str}")
    async def world_socket(socket: Websocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()


    app = Esmerald(routes=[
        Gateway(handler=home),
        Gateway(handler=another),
        WebSocketGateway(handler=world_socket),
    ])

    ```

## Дизайн маршрутов

Хороший дизайн всегда приветствуется и Esmerald позволяет создавать сложные маршруты на любом
[уровне](./application/levels.md).

### Обработчики (контроллеры)

```python title="src/myapp/accounts/controllers.py"
{!> ../../../docs_src/routing/routes/include/controllers.py!}
```

Если `path` не указан, по умолчанию используется `/`.

### Gateways (urls)

```python title="myapp/accounts/urls.py" hl_lines="5-10"
from esmerald import Gateway, WebSocketGateway
from .controllers import home, another, world_socket, World


route_patterns = [
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]

```

Если `path` не указан, по умолчанию используется `/`.

### Include

Это специальный объект, который позволяет `импортировать` любой маршрут из любого места в приложении.

`Include` принимает импорт через `namespace` или через список `routes`, но не оба одновременно.

При использовании `namespace` `Include` будет искать список объектов по умолчанию `route_patterns` в
импортированном пространстве имен, если не указано другое.

!!! note
    Шаблон (route_patterns) работает только в том случае, если импорт выполнен через `namespace`, а не через `routes`.

=== "Importing using namespace"

    ```python title='src/urls.py' hl_lines="3"
    {!> ../../../docs_src/routing/routes/include/app/urls.py!}
    ```

=== "Importing using routes"

    ```python title='src/myapp/urls.py' hl_lines="5"
    {!> ../../../docs_src/routing/routes/include/routes_list.py!}
    ```

Если `path` не указан, по умолчанию используется `/`.

#### Using a different pattern

```python title="src/myapp/accounts/urls.py" hl_lines="5"
{!> ../../../docs_src/routing/routes/include/different_pattern.py!}
```

=== "Importing using namespace"

    ```python title='src/myapp/urls.py' hl_lines="3"
    {!> ../../../docs_src/routing/routes/include/namespace.py!}
    ```

## Include и Esmerald

`Include` может быть очень полезен, особенно когда цель — избежать множества импортов и огромного списка объектов,
которые нужно передать в один единственный объект. Это может быть особенно полезно для создания экземпляра Esmerald.

**Пример**:

```python title='src/urls.py' hl_lines="3"
{!> ../../../docs_src/routing/routes/include/app/urls.py!}
```

```python title='src/app.py' hl_lines="3"
{!> ../../../docs_src/routing/routes/include/app/app.py!}
```

## Запуск приложения

Как уже упоминалось, мы рекомендуем использовать uvicorn в производственной среде, но это не обязательно.

**Использование uvicorn**:

```shell
uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Запуск приложения с пользовательскими настройками

**Использование uvicorn**:

=== "MacOS & Linux"

    ```shell
    ESMERALD_SETTINGS_MODULE=myapp.AppSettings uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:ESMERALD_SETTINGS_MODULE="myapp.AppSettings"; uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

## Документация OpenAPI

Esmerald также имеет встроенную документацию OpenAPI.

Esmerald автоматически запускает документацию OpenAPI, внедряя настройки OpenAPIConfig по умолчанию
и предоставляет вам элементы Swagger, ReDoc и Stoplight "из коробки".

Чтобы получить доступ к OpenAPI, просто запустите вашу локальную разработку и перейдите по адресу:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.
* **Stoplight Elements** - `/docs/elements`.
* **Rapidoc** - `/docs/rapidoc`.

В этой документации есть более подробная информация о том, как настроить OpenAPIConfig [здесь](./configurations/openapi/config.md).

Также представлено хорошее объяснение о том, как использовать [OpenAPIResponse](./responses.md#openapi-responses).

## Заметки

Это всего лишь очень общее демонстрационное описание того, как быстро начать и что может предложить Esmerald.
Существует множество других возможностей, которые вы можете использовать с Esmerald. Наслаждайтесь! 😊

## Спонсоры

В настоящее время у Esmerald нет спонсоров, но вы можете финансово помочь и поддержать автора через
[GitHub sponsors](https://github.com/sponsors/tarsil) и стать **Особенным** или **Легендой**.

[saffier_orm]: ./databases/saffier/motivation.md
[edgy_orm]: ./databases/edgy/motivation.md
[mongoz_odm]: ./databases/mongoz/motivation.md
