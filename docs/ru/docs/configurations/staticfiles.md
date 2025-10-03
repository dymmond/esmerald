# StaticFilesConfig

StaticFilesConfig — это простой набор конфигураций, который при передаче активирует встроенные возможности Ravyn.
Когда объект StaticFilesConfig передается в экземпляр приложения, он включает поддержку обслуживания
статических файлов.

!!! Check
    StaticFiles считаются `app` и являются полноценным приложением Lilya, поэтому использование
    Lilya StaticFiles также будет работать с Ravyn.

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

Это позволит вам поддерживать чистоту настроек и их разделение. Так же избегать перегруженного экземпляра **Ravyn**.

## Множественные каталоги и пути (без перехода)

Предположим, у вас есть несколько каталогов, к которым вы хотели бы получить доступ, включая каталог `node_modules/`.
Это возможно сделать, передав несколько конфигураций `StaticFilesConfig`, как показано ниже:

```python
{!> ../../../docs_src/configurations/staticfiles/example_multiple.py!}
```
Преимущество этого метода - тонкая настройка. Можно установить различные опции и пакеты.

!!! Примечание
    Используется первый совпавший путь, и в настоящее время нет возможности перейти по ссылке в случае, если файл не найден,
    поэтому порядок очень важен.

## Множественные каталоги с переходом

Дизайнеры могут захотеть предоставить перезапись статическим файлам или иметь резервные варианты.
В [предыдущем примере](#multiple-directories-and-multiple-pathes-without-fallthrough) этого не было возможно.
Начиная с самой последней версии Lilya (0.11.5+), можно предоставить несколько каталогов lilya и получить такое поведение

```python
{!> ../../../docs_src/configurations/staticfiles/example_multiple_fallthrough.py!}
```

Оба способа можно смешивать.
