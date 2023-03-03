## Exceptions

All the levels are managed in a simple top-down approach where one takes priority over another as previously mentioned
but.

Pior to version 0.16.0, a `ChildEsmerald` was an independent instance that is plugged into a main `Esmerald` application but since
it is like another `Esmerald` instance that also means the ChildEsmerald didn't take priority over the top-level
application, instead, it was treating its own exception handlers and application levels independently from the main instance.

In other words, a `ChildEsmerald` did not take priority over the main instance but the rules of prioritization of the
levels inside a `ChildEsmerald` prevailed the same as for a normal `Esmerald` instance.
