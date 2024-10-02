# TemplateConfig

TemplateConfig is a simple set of configurations that when passed enables the template engine.

!!! info
    Currently Esmerald supports `Jinja2` and `Mako`.

It is important to understand that you don't need to use the provided `JinjaTemplateEngine` or `MakoTemplateEngine`
from Esmerald within the `TemplateConfig`.

You are free to build your own and pass it to the `TemplateConfig`. This way you can design however you see fit.

!!! Tip
    Esmerald being built on top of Lilya, uses the `JinjaTemplateEngine` from it which means you can read
    the [Jinja2Template](https://www.lilya.dev/templates/#jinja2template) from Lilya to understand
    the parameters and how to use them.

    You can also create your own jinja2 engine and pass it in the `engine` parameter of the `TemplateConfig`.

    You will notice the name of the parameters in the `TemplateConfig` match maority of the jinja2 implementation.

!!! Warning
    The mako engine has a quite limited integration. This will change in future.

## Requirements

This section requires `jinja` or `mako` to be installed. You can do it so by running:

```shell
$ pip install esmerald[templates]
```

## TemplateConfig and application

To use the TemplateConfig in an application instance.

```python hl_lines="4-5 9"
{!> ../../../docs_src/configurations/template/example1.py!}
```

Another example

```python hl_lines="4-5 9"
{!> ../../../docs_src/configurations/template/example2.py!}
```

## Parameters

All the parameters and defaults are available in the [TemplateConfig Reference](../references/configurations/template.md).

## TemplateConfig and application settings

The TemplateConfig can be done directly via [application instantiation](#templateconfig-and-application)
but also via settings.

```python
{!> ../../../docs_src/configurations/template/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

## `url_for`

Esmerald automatically provides the `url_for` when using the jinja template system, that means
you can do something like this:

```jinja
{!> ../../../docs_src/_shared/jinja.html!}
```

## How to use

Simply return `Template` (of esmerald) not `TemplateResponse` with a `name` parameter pointing to the relative path of the template.
You can pass extra data via setting the `context` parameter to a dictionary containing the extra data.
