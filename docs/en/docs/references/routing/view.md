# `View` class

This is the reference for the `View` that contains all the parameters,
attributes and functions.

The `View` server as the base of alll object oriented views of [Esmerald](../esmerald.md) such as
[`APIView`](#esmerald.APIView), [`SimpleAPIView`](#esmerald.SimpleAPIView) and all the generics.

::: esmerald.routing.apis.View
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: esmerald.APIView
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: esmerald.SimpleAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: esmerald.routing.apis.generics.CreateAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: esmerald.routing.apis.generics.ReadAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: esmerald.routing.apis.generics.DeleteAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: esmerald.routing.apis.generics.ListAPIView
    options:
        filters:
        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"
