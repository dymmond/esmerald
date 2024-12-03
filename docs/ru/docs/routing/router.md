# Router

Router является главным объектом, который связывает Esmerald с [Gateway](./routes.md#gateway), [WebSocketGateway](./routes.md#websocketgateway)
и [handlers](./handlers.md).

## Класс Router

Класс Router состоит из множества атрибутов, которые по умолчанию заполняются в приложении. Однако Esmerald также позволяет
добавить дополнительные [пользовательские маршрутизаторы](#custom-router) или добавить приложение [ChildEsmerald](#child-esmerald-application).

```python
{!> ../../../docs_src/routing/router/router_class.py!}
```

Основной класс `Router` создается в приложении `Esmerald` с заданными маршрутами и приложение запускается.

!!! Info
    При добавлении другого маршрутизатора в приложение доступны два варианта: [пользовательские маршрутизаторы](#custom-router)
    и [ChildEsmerald](#child-esmerald-application). В данном случае пользовательские маршрутизаторы
    более ограничены, чем `ChildEsmerald`.

### Параметры

Все параметры и значения по умолчанию доступны в [Router](../references/routing/router.md).

!!! Warning
    `response_class`, `response_cookies`, `response_headers`, `tags` и `include_in_schema` не используются в
    [add_route](#add_route), только при использовании [ChildEsmerald](#child-esmerald-application).

## Пользовательский маршрутизатор

Предположим, что существуют определенные подмодули **customer** в файле `customers`, посвященном клиентам.
Существует три способа разделения маршрутов в приложении: с использованием [Include](./routes.md#include),
[ChildEsmerald](#child-esmerald-application) или созданием другого маршрутизатора. Давайте сосредоточимся на последнем варианте.

```python hl_lines="28-35" title="/application/apps/routers/customers.py"
{!> ../../../docs_src/routing/router/customers.py!}
```

Выше вы создали `/application/apps/routers/customers.py` с необходимой информацией. Он не обязательно должен быть в одном файле,
вы можете создать совершенно отдельный пакет, только для управления customer.

Теперь вам нужно добавить новый пользовательский маршрутизатор в основное приложение.

```python hl_lines="1 6" title="/application/app.py"
{!> ../../../docs_src/routing/router/app.py!}
```

Ваш маршрутизатор добавлен в основное приложение **Esmerald**.

## Child Esmerald Application

Что это такое? Мы называем его `ChildEsmerald`, но на самом деле это просто Esmerald, но под другим именем, в основном для удобства организации.

!!! Check
    Использование `ChildEsmerald` или `Esmerald` абсолютно одно и тоже, если вы хотите создать `sub application`
    и предпочитаете использовать другой класс вместо `Esmerald` для более удобной организации.

При организации маршрутов использование самого класса `Router` может быть немного ограничивающим, поскольку существуют определенные атрибуты,
которые при использовании в экземпляре или `Router` для передачи в [add_route](#add_route) не будут учтены.

Пример:

* `response_class`
* `response_cookies`
* `response_headers`
* `tags`
* `include_in_schema`

Это не ограничение и не ошибка, на самом деле это сделано намеренно, поскольку мы хотим сохранить целостность приложения.

### Как это работает

Давайте используем тот же пример, что и в [пользовательских маршрутизаторах](#custom-router) с маршрутами и правилами, специфичными для клиентов.

```python hl_lines="28-40" title="/application/apps/routers/customers.py"
{!> ../../../docs_src/routing/router/childesmerald/customers.py!}
```

Поскольку `ChildEsmerald` является представлением класса [Esmerald](../application/applications.md),
мы можем передать ранее ограниченные параметры в [пользовательском маршрутизаторе](#custom-router) и все параметры,
доступные для [Esmerald](../application/applications.md).

Вы можете добавить столько `ChildEsmerald`, сколько захотите, ограничений нет.

**Теперь в основном приложении:**

```python hl_lines="5" title="/application/app.py"
{!> ../../../docs_src/routing/router/childesmerald/app.py!}
```

**Добавление вложенных приложений**

```python hl_lines="9 13-14" title="/application/app.py"
{!> ../../../docs_src/routing/router/childesmerald/nested.py!}
```

Приведенный выше пример показывает, что вы даже можете добавить то же самое приложение внутри вложенных includes,
и для каждого include вы можете добавить уникальные [permissions](../permissions.md), [middlewares](../middleware/middleware.md),
[обработчики исключений](../exception-handlers.md) и [зависимости](../dependencies.md), которые доступны для каждого экземпляра `Include`.
Вариантов бесконечно много.

!!! Note
    С точки зрения организации, `ChildEsmerald` имеет чистый подход к изоляции обязанностей и позволяет
    рассматривать каждый модуль отдельно и просто добавлять его в основное приложение
    в форме [Include](./routes.md#include).

!!! Tip
    Рассматривайте `ChildEsmerald` как независимый экземпляр `Esmerald`.

!!! Check
    При добавлении приложения `ChildEsmerald` или `Esmerald` не забудьте добавить уникальный путь в базовый `Include`,
    таким образом вы можете быть уверены, что маршруты будут найдены правильно.

## Утилиты

Объект `Router` имеет ряд функций, которые могут быть полезны.

### add_route

```python
{!> ../../../docs_src/routing/router/add_route.py!}
```

#### Параметры

* **name** - Название маршрута.
* **include_in_schema** - Добавлять ли маршрут в схему OpenAPI.
* **[handler](./handlers.md#http-handlers)** - HTTP обработчик.
* **permissions** - Список [permissions](../permissions.md) для обслуживания входящих запросов приложения (HTTP и WebSockets).
* **middleware** - Список middleware выполняемых для каждого запроса. Middlewares из Include будут проверяться сверху вниз.
* **interceptors** - Список [interceptors](../interceptors.md) или <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a>,
поскольку они оба внутренне преобразуются. Узнайте больше о [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - Словарь строк и экземпляров [Inject](../dependencies.md), позволяющих внедрить зависимости на уровне приложения.
* **exception_handlers** - Словарь [типов исключений](../exceptions.md) (или пользовательских исключений) и функций-обработчиков на верхнем уровне приложения.
Вызываемые обработчики исключений должны иметь вид `handler(request, exc) -> response` и могут быть как синхронными, так и асинхронными функциями.

### add_websocket_route

```python
{!> ../../../docs_src/routing/router/add_websocket_route.py!}
```

#### Параметры

* **name** - Название маршрута.
* [Websocket handler](./handlers.md#websocket-handler) - Websocket обработчик.
* **permissions** - Список [permissions](../permissions.md) для обслуживания входящих запросов приложения (HTTP и WebSockets).
* **interceptors** - Список [interceptors](../interceptors.md).
* **middleware** - Список middleware выполняемых для каждого запроса. Middlewares из Include будут проверяться сверху вниз.
Или <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a>, поскольку они оба внутренне преобразуются.
Узнайте больше о [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - Словарь строк и экземпляров [Inject](../dependencies.md), позволяющих внедрить зависимости на уровне приложения.
* **exception_handlers** - Словарь [типов исключений](../exceptions.md) (или пользовательских исключений) и функций-обработчиков на верхнем уровне приложения.
Вызываемые обработчики исключений должны иметь вид `handler(request, exc) -> response` и могут быть как синхронными, так и асинхронными функциями.

### add_child_esmerald

```python
{!> ../../../docs_src/routing/router/add_child_esmerald.py!}
```

#### Параметры

* **path** - Путь для ChildEsmerald.
* **child** - Экземпляр [ChildEsmerald](#child-esmerald-application).
* **name** - Название маршрута.
* [Websocket handler](./handlers.md#websocket-handler) - Websocket обработчик.
* **permissions** - Список [permissions](../permissions.md) для обслуживания входящих запросов приложения (HTTP и WebSockets).
* **interceptors** - Список [interceptors](../interceptors.md).
* **middleware** - Список middleware выполняемых для каждого запроса. Middlewares из Include будут проверяться сверху вниз.
Или <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a>, поскольку они оба внутренне преобразуются.
Узнайте больше о [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - Словарь строк и экземпляров [Inject](../dependencies.md), позволяющих внедрить зависимости на уровне приложения.
* **exception_handlers** - Словарь [типов исключений](../exceptions.md) (или пользовательских исключений) и функций-обработчиков на верхнем уровне приложения.
Вызываемые обработчики исключений должны иметь вид `handler(request, exc) -> response` и могут быть как синхронными, так и асинхронными функциями.
* **include_in_schema** - Флаг, указывающий, следует ли включать ChildEsmerald в схему OpenAPI.
* **deprecated** - Флаг, указывающий, следует ли пометить ChildEsmerald как устаревший.
