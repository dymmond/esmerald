# Models

In simple terms, models are a representation of a database table in the format of an object declared by the language
implementing.

## User models

Esmerald comes with some pre-defined models that helps the initial configuration of users.

1. `AbstractUser` - The base user class containing all the fields required a user.
2. `User` - An subsclass of `AbstractUser`

## User

Extenting the existing `User` model is as simple as this: 

```python
{!> ../docs_src/databases/tortoise/models.py !}
```

### User model fields

If you are familiar with Django then you are also aware of the way they have their users table and the way they
have the fields declared. Esmerald has a similar approach and provides the following.

* `first_name`
* `last_name`
* `username`
* `email`
* `password`
* `last_login`
* `is_active`
* `is_staff`
* `is_superuser`

### The functions available

Using simply this model it does not bring too much benefits as it si something you can do easily and fast but the
functionality applied to this model is already something that can be something that requires some extra time to
assemble.

**create_user**

```python
{!> ../docs_src/databases/tortoise/create_user.py !}
```

**create_superuser**

```python
{!> ../docs_src/databases/tortoise/create_superuser.py !}
```

### What happened

Although the way of using the `User` table was intentionally designed to be simple there is in fact a lot going
on behind the scenes.

When using the `create_user` and `create_superuser` behind the scenes it is not only creating that same record and
storing in the database but is also <a href='https://nordpass.com/blog/password-hash/' target='_blank'>hashing</a>
the password for you using the built-in Esmerald [password hashers](#password-hashers) and this is a life saving
time and implementation.

## Password Hashers

Esmerald already brings some pre-defined password hashers that are available in the
[Esmerald settings](../../application/settings.md) and ready to be used.

```python

@property
def password_hashers(self) -> List[str]:
    return [
        "esmerald.contrib.auth.hashers.PBKDF2PasswordHasher",
        "esmerald.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    ]

```

Esmerald uses <a href='https://passlib.readthedocs.io/en/stable/' target='_blank'>passlib</a> under the hood
in order to facilitate the process of hashing passwords.

You can always override the property `password_hashers` in your
[custom settings](../../application/settings.md#custom-settings) and use your own.

```python
{!> ../docs_src/databases/tortoise/hashers.py !}
```

## Migrations

You can use any migration tool as you see fit. Tortoise also developed one tool to help you out with simple
configurations, <a href='https://github.com/tortoise/aerich' target='_blank'>aerich</a>.

## General example

Totoise, as mentioned before and in their docs, is heavily inspired by Django and therefore for a lot of people this
will be very familiar.

Lets create a model using the supported models from Esmerald.

```python
{!> ../docs_src/databases/tortoise/general_example.py !}
```

For more detailed information/how to, please check the [tortoise documentation](https://tortoise.github.io/)
