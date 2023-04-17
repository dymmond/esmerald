# Custom Directives

Having [built-in directives](./directives.md) from Esmerald is great as it gives you a lot of
niceties for your project but having **custom directives** is what really powers up your
application and takes it to another level.

## What is a custom directive?

Before jumping into that, let us go back to the roots of python.

Python was and still is heavily used as a scripting language. The scripts are isolated pieces of
code and logic that can run on every machine that has python installed and execute without too
much trouble or hurdle.

Quite simple, right? 

So, what does this have to do with directives? Well, directives follow the same principle but
applied to your own project. What if you could create your own structured scripts inside your
project directly? What if you could build dependent or independent pieces of logic that could be
run using your own Esmerald application resources?

This is what a directive is.

!!! Tip
    If you are familiar with Django management commands, Esmerald directives follow the same
    principle. There is an [excelent article](https://simpleisbetterthancomplex.com/tutorial/2018/08/27/how-to-create-custom-django-management-commands.html)
    about those if you want to get familiar with.


{! ../docs_src/_shared/envvars.md !}

### Examples

Imagine you need to deploy a database that will contain all the information about specific user
accesses and will manage roles of your application.

Now, once that database is deployed with your application, usually would would need somehow to
connect to your production server and manually setup a user or run a specific script or command
to create that same super user. This can be time consuming and prone to errors, right?

You can use a [directive](#directive) to do that same job for you.

Or what if you need to create specific operations to run in the background by some ops that
does not require APIs, for example, update the role of a user? Directives solve that problem as
well.

There is a world of possibilities of what you can do with directives.

## Directive

This is the main object class for **every single custom directive** you want to implement. This
is a special object with some defaults that you can use.

Directives were inspired by the management commands of Django with extra flavours and therefore
the syntax is very similar.

### How to create a directive

To create a directive you **must inherit from the BaseDiretive** class and **must call Directive**
to your object.

```python
from esmerald.core.directives import BaseDirective
```

**Create the Directive class**

```python hl_lines="4 7"
{!> ../docs_src/directives/base.py !}
```

Every single custom directive created should be call **Directive** and **must inherit** from the
`BaseDiretive` class.

Internally `esmerald` looks for a `Directive` object and verifies if is a subclass of `BaseDirecitve`.
If one of this conditions fails, it will raise an `Impro
