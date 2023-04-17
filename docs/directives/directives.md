# Directives

What are these directives? In simple terms, those are special `command-line` scripts that run special
pieces of code for **Esmerald**.

## Built-in Esmerald directives

Starting a project can be troublesome for some people mostly because there questions about the structure of the files
and folders and how to maintain the consistency. This was mentioned in the [Esmerald scaffold](../examples.md).

A lot of people cannot be bothered with running cookiecutters and go straight to their own design.

!!! Check
    **Esmerald is in no way, shape or form opinionated about the application structure** of any application but it
    provides some suggested options but it does not mean it should always be in that way. It simply serves as an
    option.

Currently there are two built-in directives.

* [createproject](#create-project) - Used to generate a scaffold for a project.
* [createapp](#create-app) - Used to generate a scaffold for an application.
* [show_urls](#show-urls) - Shows the information about the your esmerald application.

{! ../docs_src/_shared/envvars.md !}

## Create project

This is a simple directive that generates a folder structure with some files for your Esmerald project.

```shell
$ esmerald createproject <YOUR-PROJECT-NAME>
```

The directive will generate a tree of files and folders with some pre-populated files ready to be used.

**Example**:

```shell
$ esmerald createproject myproject
```

You should have a folder called `myproject` with a similar structure to this:

```shell
.
├── Makefile
└── myproject
    ├── __init__.py
    ├── apps
    │   └── __init__.py
    ├── configs
    │   ├── __init__.py
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```

A lot of files generated right? Yes but those are actually quite simple but let's talk about what is happening there.

* **Makefile** - This is a special file provided by the directive that contains some useful commands to run your
peoject locally, for example:
    * `make run` - Starts your project with the development settings.
    * `make test` - Runs your local tests with the testing settings.
    * `make clean` - Removes all the `*.pyc` from your project.
    
    !!! Info
        The tests are using [pytest](https://docs.pytest.org/) but you can change to whatever you want.

* **serve.py** - This file is simply a wrapper that is called by the `make run` and starts the local
development. **This should not be used in production**.
* **main.py** - The main file that builds the application path and adds it to the `$PYTHONPATH`. This file can also be
used to add extra configurations as needed.
* **urls.py** - Used as an *entry-point* for the application urls. This file is already being imported via
[Include](../routing/routes.md#include) inside the `main.py`.

### Apps

#### What is an app in the Esmerald context?

An app is another way of saying that is a python module that contains your code and logic for the application.

As mentioned before, this is merely suggestive and in no way, shape or form consitutes as the unique way of
building Esmerald applications.

The `apps` is a way that can be used to **isolate** your apis from the rest of the structure. This folder is already
added to the python path via `main.py`.

You can simply ignore this folder or used it as intended, **nothing is mandatory**, we simply believe that besides a
clean code, a clean structure makes everything more pleasant to work and maintain.

> So, you are saying that we can use the apps to isolate the apis and we can ignore it or use it.
Do you also provide any other directive that suggests how to design an app, just in case if we want?

**Actually, we do!** You can also use the [createapp](#create-app) directive to also generate a scaffold for an app.

## Create app

This is another directive that allows you to generate a scaffold for a possible app to be used within Esmerald.

```shell
$ esmerald createapp <YOUR-APP-NAME>
```

**Example**:

Using our previous example of [create project](#create-project), let's use the already created `myproject`.

```shell
$ cd myproject/apps/
$ esmerald createapp accounts
```

You should have a folder called `accounts` with a similar structure to this:

{!> ../docs_src/_shared/app_struct_example.md !}

As you can see, `myproject/apps` contains an app called `accounts`.

By default, the `createapp` generates a python module with a `v1` sub-module that contains:

* **schemas.py** - Empty file with a simple pydantic `BaseModel` import and where you can place any,
as the import suggests, pydantic model to be used with the `accounts/v1`.
* **urls.py** - You can place the urls of the views of your `accounts/v1`.
* **views.py** - You can place all the handlers and views of your `accounts/v1`.

A **tests** file is also generated suggesting that you could also add some specific application tests there.

!!! Check
    Using a version like `v1` will make it clear which version of APIs should be developed within that same
    module and for that reason a default `v1` is generated, but again, nothing is set in stone and you are free
    to simply ignore this.

## After generation

Once the project and apps are generated, executing `make run` will throw a `ImproperlyConfigured` exception. This
is because the `urls.py` expects to be populated with application details.

## Example

Let's do an example using exactly what we previously generated and put the application up and running.

**The current structure**:

{!> ../docs_src/_shared/app_struct_example.md !}

What are we going to do?

* Add a *view* to the accounts.
* Add the path to the `urls` of the accounts.
* Add the `accounts` urls to the application urls.
* Start the application.

### Create the view

```python title="myproject/apps/accounts/v1/views.py"
{!> ../docs_src/management/views.py !}
```

Create a view to return the message `Welcome home!`.

### Add the view to the urls

Now it is time to add the newly created view to the urls of the accounts.

```python title="myproject/apps/accounts/v1/urls.py"
{!> ../docs_src/management/urls.py !}
```

### Add the accounts urls to the application urls

Now that we have created the views and the urls for the accounts, it is time to add the accounts to the application
urls.

Let's update the `myproject/urls.py`.

```python title="myproject/urls.py"
{!> ../docs_src/management/app_urls.py !}
```

And that is it! The application is assembled and you can now [start the application](#start-the-application).

## Start the application

Remember that a `Makefile` that was also generated? Let's use it to start the application.

```shell
make run
```

What this command is actually doing is:

```shell
ESMERALD_SETTINGS_MODULE=myproject.configs.development.settings.DevelopmentAppSettings python -m myproject.serve
```

If you want another [settings](../application/settings.md#custom-settings) you can simply update the command to
run with your custom settings.

Once the application starts, you should have an output in the console similar to this:

```shell
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [4623] using WatchFiles
INFO:     Started server process [4625]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Access the OpenAPI documentation

You can also access the application OpenAPI documentation and validate what was created.

**Swagger**:

- [http://localhost:8000/docs/swagger](http://localhost:8000/docs/swagger)

<p align="center">
  <a href="https://res.cloudinary.com/dymmond/image/upload/v1667327131/esmerald/management/swagger_bxetrd.png" target="_blank"><img src="https://res.cloudinary.com/dymmond/image/upload/v1667327131/esmerald/management/swagger_bxetrd.png" alt='Swagger'></a>
</p>

**Redoc**:

- [http://localhost:8000/docs/redoc](http://localhost:8000/docs/redoc)

<p align="center">
  <a href="https://res.cloudinary.com/dymmond/image/upload/v1667327131/esmerald/management/redoc_xmllvv.png" target="_blank"><img src="https://res.cloudinary.com/dymmond/image/upload/v1667327131/esmerald/management/redoc_xmllvv.png" alt='Swagger'></a>
</p>

## Auto generated test files

The test files generated are using the EsmeraldTestClient, so make sure you run:

```shell
pip install esmerald[test]
```

Or you can jump this step if you don't want to use the EsmeraldTestClient at all.

## Show URLs

This is another built-in Esmerald application and it simply to show the information about the
URLs of your application via command line.

This command can be run like this:

**Using the --app parameter**

```shell
$ esmerald --app myproject.main:app show_urls
```

**Using the ESMERALD_DEFAULT_APP environment variable already exported**:

```shell
$ esmerald myproject.main:app show_urls
```
