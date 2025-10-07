# `View` class

This is the reference for the `View` that contains all the parameters,
attributes and functions.

The `View` server as the base of alll object oriented views of [Ravyn](../ravyn.md) such as
[`Controller`](#ravyn.Controller), [`SimpleAPIView`](#ravyn.SimpleAPIView) and all the generics.

::: ravyn.routing.controllers.View
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.Controller
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.SimpleAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.routing.controllers.generics.CreateAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.routing.controllers.generics.ReadAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: ravyn.routing.controllers.generics.DeleteAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: ravyn.routing.controllers.generics.ListAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"
