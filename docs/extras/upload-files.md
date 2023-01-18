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
    From the version `0.8+`, Esmerald will support separate types to handle forms and file uploads
    independently but they will **always** derive from the `Body` parameter, which means, it is
    optional to use `File` and `Form` as the same result can be achieved by using
    `Body(media_type=...)`.


## Single file upload

Uploading a single file, you need to type the `data` as [UploadFile](#uploadfile).

```python
{!> ../docs_src/extras/upload/single_file.py !}
```

## Multiple files upload

What if you need to upload multiple files? Well, that is also very much possible. Since Esmerald
uses pydantic, the way of doing it is by using that same power.

```python
{!> ../docs_src/extras/upload/multiple_files.py !}
```

## Dictionary files upload

You can also upload files as a dictionary if parsing and validation is not a concern.

```python
{!> ../docs_src/extras/upload/as_dict.py !}
```

## List files upload

In a similar way as the [dictionary](#dictionary-files-upload), you can also access the files
as a list.

```python
{!> ../docs_src/extras/upload/as_list.py !}
```
