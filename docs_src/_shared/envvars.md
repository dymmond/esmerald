### Environment variables

When using some of the custom directives or built-in directives, Esmerald
**expects at least one environment variable to be present**.

* **ESMERALD_DEFAULT_APP** - The Esmerald application to run the directives against.

The reason for this is because every Emerald application might differ in structure and design.
Esmerald not being opinionated in the way you should assemble the application needs to know,
**at least where the entry-point is going be**.

Also, gives a clean design for the time where it is needed to go to production as the procedure is
very likely to be done using environment variables.

So to save time you can simply do:

```
$ export ESMERALD_DEFAULT_APP=myproject.main:app
```

Or whatever location you have.

Alternatively, you can simply pass `--app` as a parameter with the location of your application
instead.

Example:

```shell
$ esmerald --app myproject.main:app show_urls
```