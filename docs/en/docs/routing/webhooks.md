# Webhooks

OpenAPI Webhooks are those cases where you want to tell your API users that your application
could/should/would call **their** own application, for example, sending a request with specific
bits of data, usually to **notify** them of some type of event.

This also means that instead of your users sending requests to your APIs, it is your application
**sendind requests** to their application.

This process is called **webhook**.

## Esmerald webhooks

Esmerald provides a way of declaring these webhooks in the OpenAPI specification. It is very, very
similar to the way the [Gateway](routes.md#gateway) is declared but **dedicated to webhooks**.

The process usually is that you define in your code, as normal, what is the message that you will
send, in other words, **the body of the request**.

You also define in some way at which moments your app will send those requests or events.

Your users on the other hand, define some way (web dashboard, for instance) the URL where your
application should send those requests.

The way the logic how to register the URLs for the webhooks and the code to performs the said
actions is entirely up to you.

## Documenting Esmerald webhooks with OpenAPI

As mentioned before, the way of doing it is very similar to the way you declare
[Gateway](routes.md#gateway) but for this purpose, webhooks have a **special dedicated** object or
objects to do make it happen, the [WebhookGateway](#webhookgateway).

Also, the webhooks **are not *hooked* into the application routing system**, instead, they are
placed in the `webhooks` list.

```python hl_lines="3"
from esmerald import Esmerald

app = Esmerald(webhooks=[...])
```

### WebhookGateway

As the name indicated, the `WebhookGateway` is the main object where you declare the hooks for
the OpenAPI specification and **unlike the Gateway**, it does not declare a `path` (example, `/event`),
instead, it only needs to receive the **name** of the action.

Like the Gateway, the **WebhookGateway** also expects a [handler](#handlers) but
**not the same handler as you usually use for the routes**, a special **webhook handler**.

#### How to import it

You can import them directly:

```python
from esmerald import WebhookGateway
```

Or you can use the full path.

```python
from esmerald.routing.gateways import WebhookGateway
```

#### Parameters

All the parameters and defaults are available in the [WebhookGateway Reference](../references/routing/websocketgateway.md).

### Handlers

The handlers for the **webhooks** are pretty much similar to the normal handlers used for routing
but **dedicated** only to the **WebhookGateway**. The available handlers are:

* **whget** - For the `GET`.
* **whpost** - For the `POST`.
* **whput** - For the `PUT`.
* **whpatch** - For the `PATCH`.
* **whdelete** - For the `DELETE`.
* **whhead** - For the `HEAD`.
* **whoptions** - For the `OPTION`.
* **whtrace** - For the `TRACE`.
* **whroute** - Used to specificy for which `http verbs` is available. This handler has the special
`methods` attribute. E,g.:

    ```python
    from esmerald import whroute

    @whroute(methods=["GET", "POST"])
    ...
    ```

As you can already see, the handlers are very similar to the [routing handler](./handlers.md) but
dedicated to this purpose and **all of them start with `wh`**.

The `wh` at the beginning of each handler means **W**eb**H**ook.

#### How to import them

You can import them directly:

```python
from esmerald import (
    whdelete,
    whhead,
    whget,
    whoptions,
    whpatch,
    whpost,
    whput,
    whroute,
    whtrace
)
```

Or via full path.

```python
from esmerald.routing.webhooks.handlers import (
    whdelete,
    whhead,
    whget,
    whoptions,
    whpatch,
    whpost,
    whput,
    whroute,
    whtrace
)
```

## An Esmerald application with webhooks

When you create an **Esmerald** application, as mentioned before, there is a `webhooks` attribute
that you use to define your application `webhooks`, in a similar way you define the `routes`.

```python hl_lines="6 21 16 28"
{!> ../../../docs_src/routing/webhooks/example.py !}
```

Note how the `whpost` and `post` are declared inside the `webhooks` and `routes` respectively,
**similar but not the same** and how the `whpost` **does not require** the `/` for the path.

The webhooks you define **will end up** in the **OpenAPI** schema automatically.

### Using the APIView to generate webhooks

Since Esmerald supports class based views, that also means you can also use them to generate
webhooks.

```python
{!> ../../../docs_src/routing/webhooks/cbv.py !}
```

## Important

Notice that with webhooks you are actually not declaring a path (like `/user`). The text you pass
there is just a `name` or an **identifier** of the webhook (name of the event).

This happens because it is expected that your users would actually define the proper URL path where
they want to receive the webhook in some way.

## Check out the docs

Let us see how it would look like in the docs if we were declaring the webhooks from the examples.

**First example, no Class Based Views**

<img src="https://res.cloudinary.com/dymmond/image/upload/v1690305100/esmerald/webhooks/first-example_szu28y.png" title="First example" />

**Second example, with Class Based Views**

<img src="https://res.cloudinary.com/dymmond/image/upload/v1690305101/esmerald/webhooks/second-example_hdqsif.png" title="First example" />
