# SessionConfig

SessionConfig — это простой набор конфигураций, который при передаче активирует встроенное middleware Ravyn.
Когда объект SessionConfig передается в экземпляр приложения, автоматически запускается `SessionMiddleware`.

!!! Tip
    Больше информации о HTTP сессиях
    <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Session" target='_blank'>тут</a>.

## SessionConfig и приложение

Для использования SessionConfig в экземпляре приложения.

```python hl_lines="4 7"
{!> ../../../docs_src/configurations/session/example1.py!}
```

Еще пример

```python hl_lines="4-5 8"
{!> ../../../docs_src/configurations/session/example2.py!}
```

## Параметры

Все параметры и значения по умолчанию доступны в [справочнике SessionConfig](../references/configurations/session.md).

## SessionConfig и настройки приложения

SessionConfig можно настроить напрямую через [создание экземпляра приложения](#sessionconfig-and-application), а также через настройки.

```python
{!> ../../../docs_src/configurations/session/settings.py!}
```

Это позволит вам поддерживать чистоту настроек и их разделение. Так же избегать перегруженного экземпляра **Ravyn**.

## Ravyn Sessions

Если вы не хотите использовать встроенную конфигурацию сессий и предпочитаете более кастомизированный
способ управления сессиями в Ravyn, существует официальный пакет [Ravyn Sessions](https://ravyn-sessions.dymmond.com/),
который поможет вам в этом, включая middleware.
