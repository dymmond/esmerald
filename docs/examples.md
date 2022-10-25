# Examples & Scaffolds

Starting a project can be a bit tricky mostly because some decisions need to be made regarding maintenance and
structure of a project. Usually is something like:

1. How should you structure the folders.
2. Where should I place X files.
3. Where should the settings be.

And some others.

**Bear in mind this is simply one example how to structure and does not constitute any opinionated option.**
**You are free to ignore this section and do it in your own way**.

## Esmerald scaffold

To help you out with some of those decisions, we developed a [scaffold](https://github.com/dymmond/esmerald-scaffold)
with some examples how to jump start a project quickly without wasting a lot of time and presenting one folder option
for the project.

### What does it bring

* `deployment` folder - Where some deployment files are placed. This is based on a previous doc about
[docker](./deployment/docker.md). Feel free to ignore.
* `README.md` - Auto generated readme file with instructions how to run.
* `Makefile` - Classic UNIX like Makefile with some pre-defined commands used within the scaffold.
* The project itself - The source code for the scaffold.
    * `apps` - Where the scaffold apps live.
    * `core` - Containing core common files, such as settings.
    * `tests` - Some already made tests for the scaffold views.
    * `main` - Containing the application logic to start.
    * `serve` - A personal touch. Based on Django `manage.py`, we thought it would be nice to have a similar file
that helps you out with the startup of a project. **Should only be used for development purposes**.
    * `urls` - Containing urls of the application.

!!! Note
    The auto-generated `README.md` of the scaffold contains some instructions how to run it quick and simple using
    the `Makefile` commands.

### How to use it

To use the [scaffold](https://github.com/dymmond/esmerald-scaffold) you will need to have installed:

* Python 3.7+
* [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/)

And to install, run:

```shell
$ cookiecutter https://github.com/dymmond/esmerald-scaffold <NAME_OF_YOUR_PROJECT>
```

Once the project is generated you should have a folder structure similar to this:

```shell
.
├── Dockerfile # similar Dockerfile.conf from the docker examples
├── Makefile
├── README.md
├── deployment
│   ├── nginx.conf # similar nginx.conf from the docker examples
│   └── supervisor.conf # similar supervisor.conf from the docker examples
├── requirements.txt
└── src # or the name given by you when generating the project
    ├── __init__.py
    ├── apps
    │   ├── __init__.py
    │   └── welcome
    │       ├── __init__.py
    │       └── v1
    │           ├── __init__.py
    │           ├── urls.py
    │           └── views.py
    ├── core
    │   ├── __init__.py
    │   │   └── __init__.cpython-39.pyc
    │   └── configs
    │       ├── __init__.py
    │       ├── development
    │       │   ├── __init__.py
    │       │   └── settings.py
    │       └── testing
    │           ├── __init__.py
    │           └── settings.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```

### The welcome app

The way the [scaffold](https://github.com/dymmond/esmerald-scaffold) was designed was not to replace any possible
design, instead, it was conceived with the idea of facilitating your life when starting a project.

The `welcome` app located inside `/apps/` contains two examples of views. One as function based view and another
using classes and [permissions](./permissions.md).

The tests are running against those views so if you delete them, the tests are expected to fail.

### The URLs

The `urls` were structured to show you how powerful the [Include](./routing/routes.md#include) is and how clean
an instance of Esmerald can be when starting a project containing a log of urls as you can see from the `main.py`.

### Settings

The [settings](./application/settings.md) where placed inside a `config` folder and separated by enviroment also to
show you what Esmerald means by **Simplicity from settings**.

### Makefile

Contains all available commands that can be used within the [scaffold](https://github.com/dymmond/esmerald-scaffold)
and if you want to list them all simply run:

```shell
$ make # Lists all available commands
```

The `Makefile` contains two very important commands. The `make run` and the `make test`.

As you can probably notice, the `make run` runs with the `DevelopmentSettings` module and the `make test` with
`TestingSettings` module.

**Both development and testing settings are passev via ESMERALD_SETTINGS_MODULE**.

We hope this scaffold can help you clearing out some ideas or even giving you new ones for your applications.
