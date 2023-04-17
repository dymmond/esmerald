# Custom Directives

Having [built-in directives](./directives.md) from Esmerald is great as it gives you a lot of
niceties for your project but having **custom directives** is what really powers up your
application and takes it to another level.

## What is a custom directive?

Before jumping into that, let us go back to the roots of python.

Python was and still is heavily used as a scripting language. The scripts are isolated pieces of
code and logic that can run on every machine that has python installed and execute without too
much trouble or hurdle.

Quite simple, right? 

So, what does this have to do with directives? Well, directives follow the same principle but
applied to your own project. What if you could create your own structured scripts inside your
project directly? What if you could build dependent or independent pieces of logic that could be
run using your own Esmerald application resources?

This is what a directive is.

!!! Tip
    If you are familiar with Django management commands, Esmerald directives follow the same
    principle. There is an [excelent article](https://simpleisbetterthancomplex.com/tutorial/2018/08/27/how-to-create-custom-django-management-commands.html)
    about those if you want to get familiar with.


{! ../docs_src/_shared/envvars.md !}

### Examples

Imagine you need to deploy a database that will contain all the information about specific user
accesses and will manage roles of your application.

Now, once that database is deployed with your application, usually would would need somehow to
connect to your production server and manually setup a user or run a specific script or command
to create that same super user. This can be time consuming and prone to errors, right?

You can use a [directive](#directive) to do that same job for you.

Or what if you need to create specific operations to run in the background by some ops that
does not require APIs, for example, update the role of a user? Directives solve that problem as
well.

There is a world of possibilities of what you can do with directives.

## Directive

This is the main object class for **every single custom directive** you want to implement. This
is a special object with some defaults that you can use.

Directives were inspired by the management commands of Django with extra flavours and therefore
the syntax is very similar.

### How to run

The syntax is very simple for a custom directive:

**With the --app parameter**

```shell
$ esmerald --app <LOCATION> run --directive <DIRECTIVE-NAME> <OPTIONS>
```

Example:

```shell
esmerald --app myproject.main:app run --directive mydirective --name esmerald
```

**With the ESMERALD_DEFAULT_APP environment variable set**

```shell
$ export ESMERALD_DEFAULT_APP=myproject.main:app
$ esmerald run --directive <DIRECTIVE-NAME> <OPTIONS>
```

Example:

```shell
$ export ESMERALD_DEFAULT_APP=myproject.main:app
$ esmerald run --directive mydirective --name esmerald
```

The `run --directive` is **always** expecting the name of the file of your directive.

For example, you created a `createsuperuser` file with your `Directive` logic. The `--directive`
parameter will be `run --directive createsuperuser`.

Example:

```shell
$ export ESMERALD_DEFAULT_APP=myproject.main:app
$ esmerald run --directive createsuperuser --email example@esmerald.dev
```

### How to create a directive

To create a directive you **must inherit from the BaseDiretive** class and **must call Directive**
to your object.

```python
from esmerald.core.directives import BaseDirective
```

**Create the Directive class**

```python hl_lines="4 7"
{!> ../docs_src/directives/base.py !}
```

Every single custom directive created **should be called Directive** and **must inherit** from the
`BaseDiretive` class.

Internally `esmerald` looks for a `Directive` object and verifies if is a subclass of `BaseDirective`.
If one of this conditions fails, it will raise a `DirectiveError`.

### Where should directives be placed at?

All the custom directives created **must be** inside a `directives/operations` package in order to
be discovered. 

The place for the `directives/operations` can be anywhere in your application and
you can have **more than one** as well.

Example:

```shell hl_lines="10 16 22 36"
.
├── Makefile
└── myproject
    ├── __init__.py
    ├── apps
    │   ├── accounts
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── createsuperuser.py
    │   │   │       └── __init__.py
    │   ├── payroll
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── run_payroll.py
    │   │   │       └── __init__.py
    │   ├── products
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── createproduct.py
    │   │   │       └── __init__.py
    ├── configs
    │   ├── __init__.py
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    ├── directives
    │   ├── __init__.py
    │   └── operations
    │       ├── db_shell.py
    │       └── __init__.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```

As you can see from the previous example, we have four directives:

* **createsuperuser** - Inside `accounts/directives/operations`.
* **run_payroll** - Inside `payroll/directives/operations`.
* **createproduct** - Inside `products/directives/operations`.
* **db_shell** - Inside `./directives/operations`.

All of them, no matter where you put the directive, are inside a **directives/operations** where
esmerald always looks at.

### Directive functions

#### handle()

The `Diretive` logic is implemented inside a `handle` function that can be either `sync` or
`async`. 

When calling a `Directive`, `esmerald` will execute the `handle()` and run the all the logic.

=== "Sync"

    ```python hl_lines="15"
    {!> ../docs_src/directives/sync_handler.py !}
    ```

=== "Async"

    ```python hl_lines="15"
    {!> ../docs_src/directives/async_handler.py !}
    ```

As you can see, Esmerald Directives also allow `async` and `sync` type of functions. This can be
particularly useful for when you need to run specific tasks in async mode, for example.

#### add_arguments()

This is the place where you add any argument needed to run your custom directive. The arguments
are `argparse` related arguments so the syntax should be familiar.

```python
    {!> ../docs_src/directives/arguments.py !}
```

As you can see, the Directive has five parameters and all of them required.

```shell
esmerald --app teste.main:app run --directive mydiretive --first-name Esmerald --last-name Framework --email example@esmerald.dev --username esmerald --password esmerald      

```

## Order of priority

**This is very important to understand**. 

What happens if we have two custom directives with the same
name?

Let us use the following structure as example:

```shell hl_lines="10 32"
.
├── Makefile
└── myproject
    ├── __init__.py
    ├── apps
    │   ├── accounts
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── createsuperuser.py
    │   │   │       └── __init__.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── tests.py
    │   │   └── v1
    │   │       ├── __init__.py
    │   │       ├── schemas.py
    │   │       ├── urls.py
    │   │       └── views.py
    ├── configs
    │   ├── __init__.py
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    ├── directives
    │   ├── __init__.py
    │   └── operations
    │       ├── createsuperuser.py
    │       └── __init__.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```

This example is simulating a structure of an esmerald project with
**two custom directives with the same name**.

The first directive is inside `./directives/operations/` and the second inside
`./apps/accounts/directives/operations`.

Esmerald directives work on a **First Found First Executed** principle and that means if you have
two custom directives with the same name, esmerald will
**execute the first found directive with that given name**. 

In other words, if you want to execute the `createsuperuser` from the `accounts`, the first found
directive inside `./directives/operations/` **shall have a different name** or else it will execute
it instead of the intended from `accounts`.

