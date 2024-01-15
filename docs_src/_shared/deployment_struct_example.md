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
├── Makefile
└── myproject
    ├── apps
    │   └── __init__.py
    ├── configs
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── __init__.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    ├── __init__.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```
