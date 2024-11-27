from esmerald.encoders import (
    ENCODER_TYPES,
    LILYA_ENCODER_TYPES,
)


def test_working_no_overwrite():
    encoders = LILYA_ENCODER_TYPES.get()
    assert encoders is ENCODER_TYPES
    assert type(encoders[0]).__name__ != "AttrsEncoder"
