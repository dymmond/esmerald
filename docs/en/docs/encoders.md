# Encoders

Ravyn being built on top of Lilya, brings another level of flexibility, the **encoders**.

Pretty much like Lilya, an Encoder is what allows a specific type of object to be understood,
encoded and serialized by Ravyn without breaking the application.

An example of default existing encoders in Ravyn would be the support for **Pydantic** and **MsgSpec**.

!!! Warning
    The encoders came to Ravyn after the version **3.1.2**. If you are using a version prior
    to that, this won't be available.

## Benefits of encoders

The greatest benefit of supporting the encoders is that you don't need to rely on a specific framework
to support a specific library for you to use.

With Ravyn `Encoder` you can design it yourself and simply add it to Ravyn to be used making it
**future proof** and extremely dynamic.

## How to use it

To take advantage of the Encoders **you must subclass the Encoder from Ravyn and implement three mandatory functions**.

```python
from ravyn.encoders import Encoder
```

When subclassing the `Encoder`, the mandatory functions are:

* [`is_type()`](#is_type)
* [`serialize()`](#serialize)
* [`encode()`](#encode)

Ravyn extends the native functionality of Lilya regarding the encoders and adds some extra flavours to it.

The reasoning behind it its because Ravyn internally manages signatures and data validations that are
unique to Ravyn.

### is_type

This function might sound confusing but it is in fact something simple. This function is used to check
if the object of type X is an instance or a subclass of that same type.

!!! Danger
    Here is where it is different from Lilya. With Lilya you can use the `__type__` as well but
    **not in Ravyn. In Ravyn you must implement the `is_type` function.

#### Example

This is what currently Ravyn is doing for Pydantic and MsgSpec.

```python
{!> ../../../docs_src/encoders/is_type.py !}
```

As you can see, this is how we check and verify if an object of type `BaseModel` and `Struct` are
properly validated by Ravyn.

### serialize

This function is what tells Ravyn how to serialize the given object type into a JSON readable
format.

Quite simple and intuitive.

#### Example

```python
{!> ../../../docs_src/encoders/serialize.py !}
```

### encode

Finally, this functionality is what converts a given piece of data (JSON usually) into an object
of the type of the Encoder.

For example, a dictionary into Pydantic models or MsgSpec Structs.

#### Example

```python
{!> ../../../docs_src/encoders/encode.py !}
```

### The flexibility

As you can see, there are many ways of you building your encoders. Ravyn internally already brings
two of them out of the box but you are free to build your own [custom encoder](#custom-encoders) and
apply your own logic and validations.

You have 100% the power and control over any validator you would love to have in your Ravyn application.

### Custom Encoders

Well, this is where it becomes interesting. What if you actually want to build an Encoder that is not
currently supported by Ravyn natively, for example, the library `attrs`?

It is in fact very simple as well, following the previous steps and explanations, it would look
like this:

```python
{!> ../../../docs_src/encoders/custom.py !}
```

Do you see any differences compared to `Pydantic` and `MsgSpec`?

Well, the `is_type` does not check for an `isinstance` or `is_class_and_subclass` and the reason
for that its because when using `attrs` there is not specific object of type X like we have in others,
in fact, the `attrs` uses decorators for it and by default provides a `has()` function that is used
to check the `attrs` object types, so we can simply use it.

Every library has its own ways, object types and everything in between to check and
**this is the reason why the `is_type` exists, to make sure you have the control over the way the typing is checked**.

Now imagine what you can do with any other library at your choice.

### Register the Encoder

Well, building the encoders is good fun but it does nothing to Ravyn unless you make it aware those
in fact exist and should be used.

There are different ways of registering the encoders.

* Via [settings](#via-settings)
* Via [instance](#via-instance)

Ravyn also provides a function to register anywhere in your application but **it is not recommended**
to use it without understanding the ramifications, mostly if you have handlers relying on a given
object type that needs the encoder to be available before assembling the routing system.

```python
from ravyn.encoders import register_ravyn_encoder
```

#### Via Settings

Like everything in Ravyn, you can use the settings for basically everything in your application.

Let us use the example of the [custom encoder](#custom-encoders) `AttrsEncoder`.

```python
{!> ../../../docs_src/encoders/via_settings.py !}
```

#### Via Instance

Classic approach and also available in any Ravyn or ChildRavyn instance.

```python
{!> ../../../docs_src/encoders/via_instance.py !}
```

#### Adding an encoder via app instance function

This is also available in any Ravyn and ChildRavyn application. If you would like to add
an encoder after instantiation you can do it but again, **it is not recommended**
to use it without understanding the ramifications, mostly if you have handlers relying on a given
object type that needs the encoder to be available before assembling the routing system.

```python
{!> ../../../docs_src/encoders/via_func.py !}
```

### Notes

Having this level of flexibility is great in any application and Ravyn makes it easy for you but
it is also important to understand that this level of control also comes with risks, meaning, when
you build an encoder, make sure you test all the cases possible and more importantly, you implement
**all the functions** mentioned above or else your application will break.
