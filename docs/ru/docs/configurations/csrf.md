# CSRFConfig

CSRF означает Cross-Site Request Forgery (межсайтовая подделка запроса) и является одним из встроенных
middleware в Esmerald. Когда объект `CSRFConfig` передается экземпляру приложения, автоматически запускается
`CSRFMiddleware`.

!!! Tip
    Больше информации о CSRF
    <a href="https://owasp.org/www-community/attacks/csrf" target='_blank'>тут</a>.

## CSRFConfig и приложение

Для использования `CSRFConfig` в экземпляре приложения.

```python hl_lines="4-5 8"
{!> ../../../docs_src/configurations/csrf/example1.py!}
```

Еще пример

```python hl_lines="4 7"
{!> ../../../docs_src/configurations/csrf/example2.py!}
```

## Параметры

Все параметры и значения по умолчанию доступны в [справочнике CSRFConfig](../references/configurations/csrf.md).

## CSRFConfig и настройки приложения

`CSRFConfig` можно задать напрямую при [создании приложения](#csrfconfig-and-application), а также через настройки.

```python
{!> ../../../docs_src/configurations/csrf/settings.py!}
```

Это поможет вам поддерживать настройки в чистоте, отделёнными и без перегруженного экземпляра **Esmerald**.
