# Protocols

These are unique to `Esmerald` and are used to help having some structure in your application.

Protocols are the equivalent of *interfaces* in other languages and very helpful when it comes to establish some
sort of *contracts* among systems communicating with each other.

!!! Notes
    More information and examples about Protocols and how to use them, we recommend this
    [very simple yet great article](https://andrewbrookins.com/technology/building-implicit-interfaces-in-python-with-protocol-classes/).

## Esmerald protocols

In this documentation, the protocols were mentioned when talking [middleware](./middleware/middleware.md) and the whole
reason behind it but there are two more protocols that we classify as [business oriented](#business-oriented).

## Business oriented

**What does it mean being business oriented protocols? **

A lot of companies nowadays use frameworks or microframeworks to build APIs quickly and with just a few lines of code.

The problem we have identified is that usually these frameworks don't have a business scope in mind and that
does not mean it is not possible, because of course it is!

When `Esmerald` means business oriented protocols is in fact referring to the separation between the data logic,
where the database models and connections are and the **business objects** where as the name suggests, manages the
business logic of an application.

### Why the separation

It is better to explain by using an example.

Let's imagine you need one handler that manages the creation of a user. Your application will have:

* `Database connections`. Let's use the current supported [tortoise](./databases/tortoise/tortoise.md).
* `Database models`. What is used to map python classes and database obbjects.
* `The handler`. What you will be calling.

```python
{!> ../docs_src/protocols/example1.py !}
```

!!! Check
    Since we are using tortoise, all the database connections and configurations are handled by our settings.

In this example, the handler manages to check if there is a user already with these details and creates if not but all
of this is managed in the handler itself. Sometimes is ok when is this simple but sometimes you might want to extend
the functionality to do something else, for example, send an email confirming the creation of the record to the user,
update external sources with the signal that the user has been created or even trigger another completely independent
pipeline once the data is in.

Again, all of this can be done inside the handler but,
**what if you want to separate the logic of creation from the view** and isolate *all things user* in one place?

Enters the [DAO/AyncDAO](#dao).

## DAO

DAO extends for Data Access Object and it is used to separate the low level data accessing the API or operations
from the high level business services.

```python
from esmerald import DaoProtocol, AsyncDAOProtocol
```

The DAO is nothing too special alone but it is used to grant good pratices of separation of responsabilities.

Esmerald `DAO`/`AsyncDAO` comes with five operations that must be implemented when subclassing.

* `get`
* `get_all`
* `update`
* `delete`
* `create`

Let's see how it would look if you were using a `DAO`.

```python
{!> ../docs_src/protocols/syncdao.py !}
```

Although it looks like "more work", in fact you are separating what the handler should be doing from what a business
object should be also doing.

In the example, simple CRUD was used but from there you can extend the functionality to, for instance, send emails,
call external services... With a big difference. From now one, all of your `User` operations will be managed by
that same `DAO` and not by the view. 

Advantage? You have **one single source of truth** and not too many handlers
across the codebase doing similar `User` operations and increasing the probability of getting more errors and
also increasing the level of maintenance.

DAO/AsyncDAO are your friends.

!!! Info
    DAO and AsyncDAO are fundamentally the same but one is for `sync` and the other supports `async`.

## Notes

Implementing the DAO/AsyncDAO protocol is as simple as subclassing it and implement the methods but this does not mean
that you are only allowed to use those methods. No! 

In fact, that only means that when extending the DAO/AsyncDAO
you need **at least** to have those methods but you can have whatever you need for your business objects to operate.
