# Password Hashers

For those familiar with other frameworks like Django, these password hashers will be very similar to you.

The password hashers, as the name suggests, are used to hash a given string into a salted string formated and therefore
making a possible password even more secure.

## Esmerald and password hashing

Esmerald supporting [Saffier](./databases/saffier/motivation.md) also means providing some of the features internally.

A lof of what is explained here is explained in more detail in the [Saffier orm support](./databases/saffier/motivation.md).

Esmerald already brings some pre-defined password hashers that are available in the
[Esmerald settings](./application/settings.md) and ready to be used.

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
[custom settings](./application/settings.md#custom-settings) and use your own.

```python
{!> ../../../docs_src/databases/saffier/hashers.py !}
```

## Current supported hashing

Currently `Esmerald` supports `PBKDF2` and `PBKDF2SHA1` password hashing but this does not mean that **only** supports
those. In fact, you can use your own completely from the scratch and use it within your application.

!!! Tip
    If you want to create your own password hashing, it is advisable to subclass the `BasePasswordHasher`.

    ```python
    from esmerald.contrib.auth.hashers import BasePasswordHasher
    ```
