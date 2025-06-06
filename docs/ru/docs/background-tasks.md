# Background Tasks

Как и в Lilya, в Esmerald вы можете определять фоновые задачи для выполнения **после** возвращения ответа.

Это может быть полезно для тех операций, которые должны происходить после запроса, не блокируя клиента (клиенту не нужно
ждать завершения) для получения того же ответа.

Примеры:

* Регистрация пользователя в системе и отправка электронного письма с подтверждением регистрации.
* Обработка файла, которая может занять "некоторое время". Просто верните HTTP 202 и обработайте файл в фоновом режиме.

## Как использовать

Как уже упоминалось, Esmerald использует фоновые задачи из Lilya, и вы можете передавать их различными способами:

* Через [обработчики](#через-handlers)
* Через [ответ](#через-response)

## Через handlers

Это означает передачу фоновой задачи через get, put, post, delete или route.

Существует также два способа передачи через обработчики.

### Использование одного экземпляра

Это, вероятно, наиболее распространенный случай, когда вам нужно выполнить одну фоновую задачу при получении запроса,
например, отправка уведомления по электронной почте.

```python hl_lines="18"
{!> ../../../docs_src/background_tasks/via_handlers.py !}
```

Этот пример довольно простой, но он иллюстрирует, как вы могли бы использовать обработчики
для передачи фоновой задачи.

### Использование списка

Конечно, есть также ситуации, когда нужно выполнить более одной фоновой задачи.

```python hl_lines="27-32"
{!> ../../../docs_src/background_tasks/via_list.py !}
```

## Через response

Добавление задач через response, вероятно, будет тем способом, который вы будете использовать чаще всего,
иногда вам понадобится какая-то конкретная информация, которая доступна только внутри вашего представления.

Это достигается аналогичным образом, как и в [handlers](#через-handlers).

### Использование одного экземпляра

Таким же образом, как вы создавали одну фоновую задачу для handlers, в response это работает аналогично.

```python hl_lines="22-26"
{!> ../../../docs_src/background_tasks/response/via_handlers.py !}
```

### Использование списка

То же самое происходит при выполнении более одной фоновой задачи и когда требуется более одной операции.

```python hl_lines="30-39"
{!> ../../../docs_src/background_tasks/response/via_list.py !}
```

### Использование add_task

Другой способ добавления нескольких задач - использование функции `add_task`, предоставляемой объектом `BackgroundTasks`.

```python hl_lines="28-32"
{!> ../../../docs_src/background_tasks/response/add_tasks.py !}
```

Функция `.add_task()` принимает в качестве аргументов:

* Функцию задачи, которая должна быть выполнена в фоновом режиме (send_email_notification и write_in_file).
* Любую последовательность аргументов (*args), которые должны быть переданы функции задачи (email, message).
* Любые именованные аргументы (**kwargs), которые должны быть переданы функции задачи.

## Техническая информация

Классы `BackgroundTask` и `BackgroundTasks` приходят напрямую из `lilya.background`. Это означает, что вы можете импортировать
их напрямую из Lilya, если хотите.

Esmerald импортирует эти классы и добавляет некоторую дополнительную информацию о типах, но не влияет на общую функциональность ядра.

Вы можете использовать функции `def` или `async def` при объявлении этих функций для передачи в `BackgroundTask`,
Esmerald будет знать, как обработать их.

Для получения дополнительной информации об этих объектах вы можете ознакомиться с [официальной документацией Lilya по фоновым задачам](https://www.lilya.dev/tasks/).

## Справочник API

Узнайте больше о `BackgroundTask`, ознакомившись со [Справочником API](./references/background.md).
