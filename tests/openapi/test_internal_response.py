from esmerald.openapi._internal import InternalResponse


def test_repr_internal_response():
    internal_response = InternalResponse(media_type="application/json", return_annotation=str)

    assert repr(internal_response) == "InternalResponse(annotation=application/json, default=None)"
