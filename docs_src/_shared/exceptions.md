## Exceptions

All the levels are managed in a simple top-down approach where one takes priority over another as previously mentioned
but.

Pior to version 1.0.0, a `ChildRavyn` was an independent instance that is plugged into a main `Ravyn` application but since
it is like another `Ravyn` instance that also means the ChildRavyn didn't take priority over the top-level
application.

In other words, a `ChildRavyn` did not take priority over the main instance but the rules of prioritization of the
levels inside a `ChildRavyn` prevailed the same as for a normal `Ravyn` instance.

Some exceptions are still applied. For example, for dependencies and exception handlers, the rule
of isolation and priority is still applied.
