# StaticFilesConfig

StaticFilesConfig is simple set of configurations that when passed enables the built-in middleware of Esmerald.
When a StaticFilesConfig object is passed to an application instance, it will automatically start the `SessionMiddleware`.

!!! Check
    StaticFiles are considereed an `app` and they are pure Starlette app so using Starlette StaticFiles
    will also work with Esmerald.

## StaticFilesConfig and application

To use the StaticFilesConfig in an application instance.

```python hl_lines="1 9"
{!> ../docs_src/configurations/staticfiles/example1.py!}
```

Another example

```python hl_lines="1 10"
{!> ../docs_src/configurations/staticfiles/example2.py!}
```

**With Packages and directory**:

```python hl_lines="1 10"
{!> ../docs_src/configurations/staticfiles/example3.py!}
```

## Parameters

* **path** - The path for the statics.

    <sup>Default: '/'</sup>

* **directory** - The directory for the statics in the format of a path like. E.g: `/static`.

    <sup>Default: 'None'</sup>

* **html** - Run in HTML mode. Automatically loads index.html for directories if such file exist.

    <sup>Default: 'False'</sup>

* **packages** - A list of strings or list of tuples of strings of python packages.

    <sup>Default: 'None'</sup>

* **check_dir** - Ensure that the directory exists upon instantiation.

    <sup>Default: 'True'</sup>

## StaticFilesConfig and application settings

The StaticFilesConfig can be done directly via [application instantiation](#staticfilesconfig-and-application)
but also via settings.

```python
{!> ../docs_src/configurations/staticfiles/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.
