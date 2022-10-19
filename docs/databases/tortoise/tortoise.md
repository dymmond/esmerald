# Tortoise ORM

Typically 99% of applications have some sort of underlying database used to store whatever information the requirements
demand and with that in mind **Esmerald** decided to give support to a very good one,
the <a href='https://tortoise.github.io/' target='_blank'>Tortoise-ORM</a>.

!!! Tip
    Although Esmerald supports out of the box some integrations with Tortoise it doesn't necessarily mean the framework
    is only coupled with it. You are entirely free to use a completely different ORM or even ignore this section and
    implement your own Tortoise integration.

## Motivation

There are great ORMs out there like <a href='https://www.sqlalchemy.org/' target='_blank'>SQL Alchemy</a>
and <a href='https://piccolo-orm.com/' target='_blank'>Piccolo</a> and many others
that can be used with Esmerald but the reasoning behind the support for Tortoise came from the simplicity.

Tortoise was heavily inspired by the way Django ORM was designed.

* Declaring tables.
* Querying models.
* Declaring relationships.
* Managers.
* **Asynchronous**

When starting a project the initial configurations can take majority of the time and this can come with costs for the
business, hence the support for Tortoise to make sure that same time can be saved.

## Documentation and more details

Since we support Tortoise, the best place to understand how to use all the powerful features given by it you can simply
use their [documentation](https://tortoise.github.io/) and learn more how to leverage it.
