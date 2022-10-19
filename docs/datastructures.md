# Datastructures

Esmerald comes equipped with some datastructures. If you want to use the same as Starlette, feel free as they are
compatible and work out of the box.

## How to access them

As an example, let's import `Headers`.

```python
from esmerald.datastructures import Headers
```

The available datastructures to be imported from `Esmerald` are as follow.

* **Starlette**:
    * `URL`
    * `Address`
    * `FormData`
    * `Headers`
    * `MutableHeaders`
    * `QueryParams`
    * `UploadFule`
    * `URLPath`
* **Esmerald**:
    * `Secret`
    * `State`
    * `Cookie`
    * `File`
    * `Redirect`
    * `Stream`
    * `Template`

All the datastructures can be and are used across the codebase and can be applied by you anywhere.

!!! Note
    As mentioned before, all the Starlette datastructures are 100% compatible with `Esmerald`. You can use whatever
    it suits you.
