# Приложения

Esmerald работает на основе Lilya и поэтому включает в себя класс приложения **Esmerald**,
который объединяет всю функциональность.

## Класс Esmerald

=== "In a nutshell"

    ```python
    {!> ../../../docs_src/application/app/nutshell.py !}
    ```

=== "Another way"

    ```python
    {!> ../../../docs_src/application/app/another_way.py!}
    ```

=== "With Include"

    ```python
    {!> ../../../docs_src/application/app/with_include.py!}
    ```

### Быстрая заметка

Поскольку возможности Swagger и ReDoc ограничены, например, при использовании
`username = request.path_params["username"]`, **вы не сможете протестировать это через документацию**.
**Наилучший способ сделать это — вызывать API напрямую через любой предпочитаемый клиент или браузер.**

Другими словами, параметр url может быть захвачен с помощью `Request.path_params`, но не может быть
протестирован через Swagger UI.

#### Тестирование с использованием curl или insomnia

С помощью cURL:

```shell
$ curl -X GET http://localhost:8000/user/esmerald
```

С помощью Insomnia:

<p align="center">
  <a href="https://res.cloudinary.com/dymmond/image/upload/v1669211317/esmerald/others/insomnia_phitug.png" target="_blank"><img src="https://res.cloudinary.com/dymmond/image/upload/v1669211317/esmerald/others/insomnia_phitug.png" alt='Insomnia'></a>
</p>

!!! Note
    Вы можете использовать что-то еще, кроме insomnia. Это было для примера.


### Инициализация приложения

Создание экземпляра приложения может быть выполнено разными способами, с большим преимуществом
использования [настроек](./settings.md) для более чистого подхода.

**Параметры**:

* **debug** - Логическое значение, указывающее, должны ли возвращаться трассировки отладки при ошибках. В основном, режим отладки, очень полезен для разработки.
* **title** - Заголовок для приложения. Используется для OpenAPI.
* **app_name** - Название приложения. Также используется для OpenAPI.
* **description** - Описание приложения. Используется для OpenAPI.
* **version** - Версия приложения. Используется для OpenAPI.
* **contact** - Контактные данные администратора. Используется для OpenAPI.
* **terms_of_service** - Условия использования приложения. Используется для OpenAPI.
* **license** - Информация о лицензии. Используется для OpenAPI.
* **servers** - Серверы в формате словаря. Используется для OpenAPI.
* **secret_key** - Секретный ключ, используемый для внутреннего шифрования (например, пароли пользователей).
* **allowed_hosts** - Список разрешенных хостов. Включает встроенный middleware для разрешенных хостов.
* **allow_origins** - Список разрешенных источников. Включает встроенный middleware CORS. Может быть только `allow_origins` или объект [CORSConfig](../configurations/cors.md), но не оба.
* **routes** - Список маршрутов для обслуживания входящих HTTP и WebSocket запросов. Список [Gateway](../routing/routes.md#gateway), [WebSocketGateway](../routing/routes.md#websocketgateway) или [Include](../routing/routes.md#include).
* **interceptors** - Список [interceptors](../interceptors.md) для обслуживания входящих запросов приложения (HTTP и WebSocket).
* **permissions** - Список [permissions](../permissions.md) для обслуживания входящих запросов приложения (HTTP и WebSocket).
* **middleware** - Список middleware, которые будут выполняться для каждого запроса. Приложение Esmerald всегда будет включать middleware из переданных конфигураций (CSRF, CORS, JWT...) и пользовательских middleware. Middleware может быть подклассом [MiddlewareProtocol](../protocols.md) или <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a>. Узнайте больше о [протоколах Python](https://peps.python.org/pep-0544/).
* **dependencies** - Словарь строк и экземпляров [Inject](.././dependencies.md), позволяющий внедрение зависимостей на уровне приложения.
* **exception_handlers** - Словарь типов [исключений](../exceptions.md) (или пользовательских исключений) и функций-обработчиков на верхнем уровне приложения. Обработчики исключений должны быть в форме `handler(request, exc) -> response` и могут быть как стандартными функциями, так и асинхронными функциями.
* **csrf_config** - Если установлен [CSRFConfig](../configurations/csrf.md), это включит middleware CSRF.
* **openapi_config** - Если установлен [OpenAPIConfig](../configurations/openapi/config.md), это переопределит настройки документации OpenAPI по умолчанию.
* **cors_config** - Если установлен [CORSConfig](../configurations/cors.md), это включит middleware CORS.
* **static_files_config** - Если установлен [StaticFilesConfig](../configurations/staticfiles.md), это включит конфигурацию статических файлов приложения.
* **template_config** - Если установлен [TemplateConfig](../configurations/template.md), это включит шаблонный движок.
* **session_config** - Если установлен [SessionConfig](../configurations/session.md), это включит middleware для сессий.
* **response_class** - Пользовательский подкласс [Response](../responses.md), который будет использоваться в качестве класса ответа приложения.
* **response_cookies** - Список объектов cookie.
* **response_headers** - Словарь объектов заголовков.
* **scheduler_config** - Класс [SchedulerConfig](../configurations/scheduler.md), используемый для планировщика приложения. Дополнительные конфигурации [задач планировщика](../scheduler/handler.md).
* **timezone** - Часовой пояс по умолчанию для приложения. По умолчанию `UTC`.
* **on_shutdown** - Список вызываемых функций при завершении работы приложения. Обработчики завершения работы не принимают никаких аргументов и могут быть как синхронными функциями, так и асинхронными функциями.

* **on_startup** - Список вызываемых функций при запуске приложения. Обработчики запуска не принимают никаких аргументов и могут быть как синхронными функциями, так и асинхронными функциями.
* **lifespan** - Функция контекста жизненного цикла - это более новый стиль, который заменяет обработчики on_startup / on_shutdown. Используйте один из них, а не оба.
* **tags** - Список тегов для включения в схему OpenAPI.
* **include_in_schema** - Логический флаг, указывающий, следует ли включать в схему или нет.
* **deprecated** - Логический флаг для устаревания. Используется для OpenAPI.
* **security** - Определение безопасности приложения. Используется для OpenAPI.
* **enable_openapi** - Флаг для включения/выключения документации OpenAPI. По умолчанию включено.
* **redirect_slashes** - Флаг для включения/выключения перенаправления слешей для обработчиков. По умолчанию включено.

## Настройки приложения

Настройки - это еще один способ управления параметрами, переданными объекту
[Esmerald при создании](#instantiating-the-application). Ознакомьтесь с [настройками](./settings.md)
для получения дополнительных сведений о том, как использовать их для улучшения вашего приложения.

Для доступа к настройкам приложения существует несколько способов:

=== "Внутри запроса приложения"

    ```python hl_lines="6"
    {!> ../../../docs_src/application/settings/within_app_request.py!}
    ```

=== "Из глобальных настроек"

    ```python hl_lines="1 6"
    {!> ../../../docs_src/application/settings/global_settings.py!}
    ```

=== "Из настроек конфигурации"

    ```python hl_lines="2 7"
    {!> ../../../docs_src/application/settings/conf_settings.py!}
    ```

### Состояние и экземпляр приложения

Вы можете хранить произвольное дополнительное состояние в экземпляре приложения, используя экземпляр State.

Пример:

```python hl_lines="6"
{!> ../../../docs_src/application/others/app_state.py!}
```

## Доступ к экземпляру приложения

К экземпляру приложения можно получить доступ через `request`, когда он доступен.

Пример:

```python hl_lines="6"
{!> ../../../docs_src/application/others/access_app_instance.py!}
```

## Доступ к состоянию из экземпляра приложения

Состояние можно получить из `request`, когда он доступен.

Пример:

```python hl_lines="7 11"
{!> ../../../docs_src/application/others/access_state_from_app.py!}
```
