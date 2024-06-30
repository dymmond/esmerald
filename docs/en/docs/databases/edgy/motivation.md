# Edgy

Everyone uses in one way or another an ORM while working with SQLDatabases.

Django, for example, is widely used by a lot of companies and people out there, the ORM it is simply
amazing and simplistic in the way you can simply focus on what it matters to you and not in the
small details.

SQL Alchemy is another one widely used and loved by the majority of the python community.

[Edgy](https://edgy.tarsild.io) is from the same autor of Esmerald so is expected to be
supported (not natively) by the framework by providing some out-of-the-box built-in that can simply
be used

!!! Tip
    Although Esmerald supports out of the box some integrations with Edgy it does not necessarily mean the framework
    is only coupled with it. You are entirely free to use a completely different ORM or even ignore this section and
    implement your own Edgy integration.

## Motivation

* **100% Pydantic**
* Declaring tables
* Querying models
* Declaring relationships
* Managers
* Asynchronous
* Fast
* SQL Alchemy core


## How to use

To use Edgy with Esmerald you should install some requirements first.

It will depend of each flavour you want.

### Postgres

```shell
$ pip install edgy[postgres]
```

### MySQL/MariaDB

```shell
$ pip install edgy[mysql]
```

### SQLite

```shell
$ pip install edgy[sqlite]
```

### MSSQL

```shell
$ pip install edgy[mssql]
```

## Documentation and more details

Since Esmerald supports Edgy, the best place to understand how to use all the powerful features given by it you can simply
use its [documentation](https://edgy.tarsild.io/) and learn more how to leverage it.
