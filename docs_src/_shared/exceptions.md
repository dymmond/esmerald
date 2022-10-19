## Exceptions

All the levels are managed in a simple top-down approach where one takess precent over another as previously mentioned
but when implementing a [ChildEsmerald](./routing/router.md#child-esmerald-application) that is not the case.

A `ChildEsmerald` is an independent instance that is plugged into a main `Esmerald` application but since
it is like another `Esmerald` instance that also means the ChildEsmerald doesn't take precedent over the top-level
application, instead, treats its own exception handlers and application levels independently from the main instance.

In other words, a `ChildEsmerald` does not take precedent over the main instance but the rules of precedence of the
levels inside a `ChildEsmerald` prevail the same as for a normal `Esmerald` instance.
