# CORSConfig

CORS означает Cross-Origin Resource Sharing и является одним из встроенных middleware в Esmerald.
Когда объект `CORSConfig` передается экземпляру приложения, автоматически запускается `CORSMiddleware`.

!!! Tip
    Больше информации о CORS
    <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS" target='_blank'>тут</a>.

!!! Check
    Если `allowed_hosts` указан через экземпляр приложения или настройки, автоматически запускается
    `TrustedHostMiddleware`.


## CORSConfig и приложение

Для использования `CORSConfig` в экземпляре приложения.

```python hl_lines="4 7"
{!> ../../../docs_src/configurations/cors/example1.py!}
```

Еще пример

```python hl_lines="4-6 9"
{!> ../../../docs_src/configurations/cors/example2.py!}
```

## Параметры

Все параметры и значения по умолчанию доступны в [справочнике CORSConfig](../references/configurations/cors.md).

## CORSConfig и настройки приложения

`CORSConfig` можно задать напрямую при [создании приложения](#corsconfig-and-application), а также через настройки.

```python
{!> ../../../docs_src/configurations/cors/settings.py!}
```

Это поможет вам поддерживать настройки в чистоте, без перегруженного экземпляра **Esmerald**.
