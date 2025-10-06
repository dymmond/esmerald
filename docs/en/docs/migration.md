---
hide:
  - navigation
---

# Migration from Esmerald to Ravyn

You are probably wondering why you should migrate from Esmerald to Ravyn. Well, its simple, **Esmerald is now Ravyn with a fresh new look**.
Is the migration process hard? No, its actually very simple, you just need to change a few things in your codebase.

This guide will help you to migrate your Esmerald project to Ravyn, if something is missing, please open an issue or a
pull request to fixed and help us.

## The imports from `esmerald` to `ravyn`

Probably for the most part of your codebase, you will need to change the imports from `esmerald` to `ravyn`.

**Before:**

```python
# Before
from esmerald import Esmerald, Gateway, get

app = Esmerald(...)
```

**After:**

```python
# After
from ravyn import Ravyn, Gateway, get

app = Ravyn(...)
```

The rest, remains exactly the same.

## The exceptions

Before we had `EsmeraldException`, now we have `RavynException`.

**Before:**

```python
# Before
from esmerald.exceptions import EsmeraldAPIException
raise EsmeraldAPIException(detail="This is an exception")
```

**After:**

```python
# After
from ravyn.exceptions import RavynAPIException
raise RavynAPIException(detail="This is an exception")
```

## The settings module

If you were using the `EsmeraldSettings` class, now you need to use the `RavynSettings` class.

**Before:**

```python
# Before
from esmerald import EsmeraldSettings

class Settings(EsmeraldSettings):
    ...
```

**After:**

```python
# After
from ravyn import RavynSettings

class Settings(RavynSettings):
    ...
```

## Directives and commands

Before we had `esmerald` as the package name, now we have `ravyn`.

**Before:**

```bash
# Before
esmerald run
```

**After:**

```bash
# After
ravyn run
```

The imports are the same as reflected in [The imports from `esmerald` to `ravyn`](#the-imports-from-esmerald-to-ravyn).

## Notes

Migrating from Esmerald to Ravyn should be a smooth process, if you encounter any issues, please open an issue or a
pull request to help us improve the migration process.

99% of the code remains the same, so you should not have any major issues and its minor import changes.
