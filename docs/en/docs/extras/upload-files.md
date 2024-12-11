# Upload Files

Uploading files from your application is something extremely common.

Esmerald handles this by using the `UploadFile` datastructure object, serving as interface. To make
this work you will need to type your uploads accordingly.

## UploadFile

To access the `UploadFile` datastructrure.

```python
from esmerald.datastructures import UploadFile
```

or

```python
from esmerald import UploadFile
```

## Content Types

The [body](./body-fields.md) parameter plays a great role when it comes to use the
[UploadFile](#uploadfile). The reason for that is because of the parameter `media_type`.

The `media_type` allows to pass different encoding types for your uploads.

Esmerald `EncodingType` can be accessed via:

```python
from esmerald.enums import EncodingType
```

The current available `content-types` available in the `EncodingType` are:

* **application/x-www-form-urlencoded**
* **multipart/form-data**
* **application/json**

These types are the ones that shall be passed to `Body(media_type=...)`.

!!! Version notice
    From the version `0.8+`, Esmerald supports separate types to handle forms and file uploads
    independently but they will **always** derive from the `Body` parameter, which means, it is
    optional to use `File` and `Form` as the same result can be achieved by using
    `Body(media_type=...)`.

## Single file upload

Uploading a single file, you need to type the `data` as [UploadFile](#uploadfile).

```python
{!> ../../../docs_src/extras/upload/single_file.py !}
```

## List files upload

In a similar way, you can also access the files as a list.

```python
{!> ../../../docs_src/extras/upload/as_list.py !}
```

## Using the File

As mentioned above, `File` is now fully supported as parameter as well and since File inherits from
`Body`, means all the benefits are also there but is also cleaner as you don't need to specify
the `media_type=EncodingType.MULTI_PART` because it is already the default of `File`.

Let us see how it looks now using `File` instead of `Body` for the uploads.

### Single file upload

Uploading a single file, you need to type the `data` as [UploadFile](#uploadfile).

```python hl_lines="6"
{!> ../../../docs_src/extras/upload/single.py !}
```

### List files upload

In a similar way, you can also access the files as a list.

```python hl_lines="8"
{!> ../../../docs_src/extras/upload/file_as_list.py !}
```

### Important

Since `Body` or `Field` are Pydantic fields (sort of), that also means you can specify for instance,
the maximum number of items to be sent in a list for the upload.

```python hl_lines="8"
{!> ../../../docs_src/extras/upload/file_as_list_max.py !}
```

This means that the maximum number of files allowed for upload using the a list is three. If the
maximum is exceeded, it will raise a `ValidationErrorException` specifying the issues.

Using the `max_length` is just one attribute available inside `File` or `Body`. Since it is derived
from pydantic `FieldInfo`, that means you can also specify other parameters as well.

You can check [the list of available parameters default](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.FieldInfo)
as well.

### File from params

The file used with the [example](#single-file-upload-1) as param is not a datastructure but a `FieldInfo` so it cannot
be used to set and create a new `file` like the one from *File in datastructures*.

To import it:

```python
from esmerald.datastructures import File # datastructure

# or

from esmerald.params import File # param
```

## API Reference

Read more about the `UploadFile` in the [API Reference](../references/uploadfile.md)
