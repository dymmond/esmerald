# StaticFilesConfig

StaticFilesConfig — это простой набор конфигураций, который при передаче активирует встроенные возможности Esmerald.
Когда объект StaticFilesConfig передается в экземпляр приложения, он включает поддержку обслуживания
статических файлов.

!!! Check
    StaticFiles считаются `app` и являются полноценным приложением Lilya, поэтому использование
    Lilya StaticFiles также будет работать с Esmerald.

## StaticFilesConfig и приложение

Для использования StaticFilesConfig в экземпляре приложения.

```python hl_lines="5-7 9"
{!> ../../../docs_src/configurations/staticfiles/example1.py!}
```

**С пакетами и директорией**:

```python hl_lines="6 9"
{!> ../../../docs_src/configurations/staticfiles/example3.py!}
```

## Параметры

Все параметры и значения по умолчанию доступны в [справочнике StaticFilesConfig](../references/configurations/static_files.md).

## StaticFilesConfig и настройки приложения

StaticFilesConfig можно настроить напрямую через [создание экземпляра приложения](#staticfilesconfig-and-application), а также через настройки.

```python
{!> ../../../docs_src/configurations/staticfiles/settings.py!}
```

Это позволит вам поддерживать чистоту настроек и их разделение. Так же избегать перегруженного экземпляра **Esmerald**.
