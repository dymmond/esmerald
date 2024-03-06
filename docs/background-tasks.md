# Background Tasks

Like Starlette and any other Starlette based frameworks, in Esmerald you can define background
tasks to run **after** the returning response.

This can be useful for those operations that need to happen after the request without blocking the
client (the client doesn't have to wait to complete) from receiving that same response.

Example:

* Registering a user in the system and send an email confirming the registration.
* Processing a file that can take "some time". Simply return a HTTP 202 and process the file in the
background.


## How to use

As mentioned before, Esmerald uses the background tasks from Starlette and you can pass them in
different ways:

* Via [handlers](#via-handlers)
* Via [response](#via-response)

## Via handlers

When via handlers, this means passing a background task via get, put, post, delete or route.

There are also two ways of passing via handlers:

- [Background Tasks](#background-tasks)
    - [How to use](#how-to-use)
    - [Via handlers](#via-handlers)
        - [Using a single instance](#using-a-single-instance)
        - [Using a list](#using-a-list)
    - [Via response](#via-response)
        - [Using a single instance](#using-a-single-instance-1)
        - [Using a list](#using-a-list-1)
        - [Using the add\_task](#using-the-add_task)
    - [Technical information](#technical-information)
    - [API Reference](#api-reference)

### Using a single instance

This is probably the most common use case where you simply need to execute one bacground task upon
receiving the request, for example, sending an email notification.

```python hl_lines="18"
{!> ../docs_src/background_tasks/via_handlers.py !}
```

This is of course something quite small as an example but it illustrates how you could use the
handlers to pass a background task from there.

### Using a list

Of course there is also the situation where more than one background task needs to happen.

```python hl_lines="27-32"
{!> ../docs_src/background_tasks/via_list.py !}
```

## Via response

Adding tasks via response will be probably the way you will be using more often and the reson being
is that sometimes you will need some specific information that is only available inside your view.

That is achieved in a similar way as the [handlers](#via-handlers).

### Using a single instance

In the same way you created a singe background task for the handlers, in the response works in a
similar way.

```python hl_lines="22-26"
{!> ../docs_src/background_tasks/response/via_handlers.py !}
```

### Using a list

The same happens when executing more than one background task and when more than one operation is
needed.

```python hl_lines="30-39"
{!> ../docs_src/background_tasks/response/via_list.py !}
```

### Using the add_task

Another way of adding multiple tasks is by using the `add_tasks` function provided by the
`BackgroundTasks` object.

```python hl_lines="28-32"
{!> ../docs_src/background_tasks/response/add_tasks.py !}
```

The `.add_task()` receives as arguments:

* A task function to be run in the background (send_email_notification and write_in_file).
* Any sequence of arguments that should be passed to the task function in order (email, message).
* Any keyword arguments that should be passed to the task function.


## Technical information

The class `BackgroundTask` and `BackgroundTasks` come directly from `starlette.background`. This
means you can import directly from Starlette if you want.

Esmerald imports those classes and adds some extra typing information but without affecting the
overall functionality of the core.

You can use `def` or `async def` functions when declaring those functionalities to be passed to
the `BackgroundTask` and Esmerald will know how to handle those for you.

For more details about these objects, you can see in
[Starlette official docs for Background Tasks](https://www.lilya.dev/background/).

## API Reference

Learn more about the `BackgroundTask` by checking the [API Reference](http://localhost:8000/references/background/).
