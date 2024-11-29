# StaticFilesConfig

StaticFilesConfig is simple set of configurations that when passed enables the built-in of Esmerald.
When a StaticFilesConfig object is passed to an application instance, it will enable the static files serving.

!!! Check
    StaticFiles are considered an `app` and they are pure Lilya app, so using Lilya StaticFiles
    will also work with Esmerald.

## StaticFilesConfig and application

To use the StaticFilesConfig in an application instance.

```python hl_lines="3 9"
{!> ../../../docs_src/configurations/staticfiles/example1.py!}
```

Another example

```python hl_lines="3 10"
{!> ../../../docs_src/configurations/staticfiles/example2.py!}
```

**With Packages and directory**:

```python hl_lines="3 9"
{!> ../../../docs_src/configurations/staticfiles/example3.py!}
```

## Parameters

All the parameters and defaults are available in the [StaticFilesConfig Reference](../references/configurations/static_files.md).

## StaticFilesConfig and application settings

The StaticFilesConfig can be done directly via [application instantiation](#staticfilesconfig-and-application)
but also via settings.

```python
{!> ../../../docs_src/configurations/staticfiles/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

## Multiple directories and multiple pathes (without fallthrough)

Imagine, for example, you have multiple directories you would like to access including a `node_modules/` one.
This is possible do do it by passing multiple `StaticFilesConfig` configurations and shown below:

```python
{!> ../../../docs_src/configurations/staticfiles/example_multiple.py!}
```
The advantage is a fine granular configuration. Different options and packages can be set.

!!! Note
    The first path match is used and there is currently no fallthrough in case no file is found, so the order is very important.


## Multiple directories with fallthrough

Designers may want to provide overwrites to static files or have fallbacks. In the [former example](#multiple-directories-and-multiple-pathes-without-fallthrough) this wasn't possible.
For **newer** lilya versions it is possible to provide multiple directories to lilya and get such a behavior

```python
{!> ../../../docs_src/configurations/staticfiles/example_multiple_fallthrough.py!}
```

Both ways can be mixed.
