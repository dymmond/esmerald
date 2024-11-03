# TemplateConfig

TemplateConfig — это простой набор конфигураций, который при передаче активирует движок шаблонов.

!!! info
    В настоящее время Esmerald поддерживает `Jinja2` и `Mako`.

Важно понимать, что вам не обязательно использовать предоставляемые Esmerald `JinjaTemplateEngine` или `MakoTemplateEngine`
в рамках `TemplateConfig`.

Вы вольны создать свой собственный движок шаблонов и передать его в `TemplateConfig`.
Таким образом, вы можете разрабатывать по своему усмотрению.

!!! Tip
    Esmerald, построенный на основе Lilya и использует `JinjaTemplateEngine` из Lilya.
    Вы можете ознакомиться с [Jinja2Template](https://www.lilya.dev/templates/#jinja2template)
    в документации Lilya, чтобы понять параметры и их использование.

    Вы также можете создать свой собственный движок jinja2 и передать его в параметре `engine` конфигурации
    `TemplateConfig`.

    Вы заметите, что имена параметров в `TemplateConfig` совпадают с большинством реализаций jinja2.

!!! Warning
    Движок `Mako` имеет ограниченную интеграцию в Esmerald. В будущем это изменится.

## TemplateConfig и приложение

Для использования TemplateConfig в экземпляре приложения.

```python hl_lines="4-5 9"
{!> ../../../docs_src/configurations/template/example1.py!}
```

Другой пример

```python hl_lines="4-5 9"
{!> ../../../docs_src/configurations/template/example2.py!}
```

## Параметры

Все параметры и значения по умолчанию доступны в [справочнике TemplateConfig](../references/configurations/template.md).

## TemplateConfig и настройки приложения

TemplateConfig можно настроить напрямую через [создание экземпляра приложения](#templateconfig-and-application), а также через настройки.

```python
{!> ../../../docs_src/configurations/template/settings.py!}
```

Это позволит вам поддерживать чистоту настроек и их разделение. Так же избегать перегруженного экземпляра **Esmerald**.

## `url_for`

Esmerald автоматически предоставляет `url_for` при использовании системы шаблонов jinja,
это означает, что вы можете делать что-то вроде этого:


```jinja
{!> ../../../docs_src/_shared/jinja.html!}
```

## Как использовать

Просто верните `Template` (из esmerald), а не `TemplateResponse`, с параметром `name`,
указывающим на относительный путь к шаблону.
Вы можете передать дополнительные данные, передав параметр `context` в словарь, содержащий дополнительные данные.

Чтобы выбрать тип возвращаемого значения (txt, html), вам нужно называть файлы так: `foo.html.jinja`.
