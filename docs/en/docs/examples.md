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

In the past, Esmerald had the [scaffold](https://github.com/dymmond/esmerald-scaffold) a good starting point but that
was before the [directives](./directives/index.md) were introduced.

It is strongly advised to use them if you want to create a nice structured project containing generated
files out of the box as well as, if you want, also deployment.

You can read more about [directives and how to use them](./directives/index.md) in the corresponding
section.

### How to quickly use them

Imagine you want a project containing also deployment files for a project called `my_project`.

#### Generate the application

```shell
$ esmerald createproject my_project --with-deployment
```

#### Generate an esmerald "app"

```shell
$ cd my_project/my_project/apps
$ esmerald createapp welcome
```

#### Add your welcome handler

Add the first `welcome` handler (endpoint) by changing the `controllers.py` inside `welcome/v1/controllers.py`.

Edit that file and add the following.

```python
from esmerald import JSONResponse, get


@get("/welcome")
async def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Esmerald!"})

```

#### Update the "app" urls

You can do this directly in the `urls.py` generated in the root of the project as well but we will
be adding first in the app to give a complete example.

Edit the `welcome/v1/urls.py` and add the following:

```python
from esmerald import Gateway

from .controllers import welcome

route_patterns = [
    Gateway(handler=welcome, name="welcome"),
]

```

#### Update the root urls

Now its time to update the generated `urls.py` from the root.

Edit the `my_project/urls.py` and add the following.

```python
from esmerald import Include

route_patterns = [Include(namespace="welcome.v1.urls")]
```

You are now ready to start the application. Since the files were generated, you can run inside the `my_project`
root the `make run`.

#### Check the documentation

You can now check `http://localhost:8000/docs/swager` and you can test your brand new API.


#### Final structure

You should now have a project similar to the following structure, containing also deployment files.

```shell
.
├── deployment
│   ├── docker
│   │   └── Dockerfile
│   ├── gunicorn
│   │   └── gunicorn_conf.py
│   ├── nginx
│   │   ├── nginx.conf
│   │   └── nginx.json-logging.conf
│   └── supervisor
│       └── supervisord.conf
├── Taskfile.yaml
├── my_project
│   ├── apps
│   │   ├── __init__.py
│   │   └── welcome
│   │       ├── directives
│   │       │   ├── __init__.py
│   │       │   └── operations
│   │       │       └── __init__.py
│   │       ├── __init__.py
│   │       ├── tests.py
│   │       └── v1
│   │           ├── controllers.py
│   │           ├── __init__.py
│   │           ├── schemas.py
│   │           └── urls.py
│   ├── configs
│   │   ├── development
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── testing
│   │       ├── __init__.py
│   │       └── settings.py
│   ├── __init__.py
│   ├── main.py
│   ├── serve.py
│   ├── tests
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   └── test_app.py
│   └── urls.py
└── requirements
    ├── base.txt
    ├── development.txt
    └── testing.txt
```
