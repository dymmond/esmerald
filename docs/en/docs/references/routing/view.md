# `View` class

This is the reference for the `View` that contains all the parameters,
attributes and functions.

The `View` server as the base of alll object oriented views of [Ravyn](../ravyn.md) such as
[`APIView`](#ravyn.APIView), [`SimpleAPIView`](#ravyn.SimpleAPIView) and all the generics.

::: ravyn.routing.apis.View
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.APIView
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

::: ravyn.routing.apis.generics.CreateAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.routing.apis.generics.ReadAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: ravyn.routing.apis.generics.DeleteAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: ravyn.routing.apis.generics.ListAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"
