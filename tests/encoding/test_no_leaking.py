from esmerald.encoders import (
    LILYA_ENCODER_TYPES,
)


def test_working_no_overwrite():
    encoders = LILYA_ENCODER_TYPES.get()
    assert encoders is LILYA_ENCODER_TYPES.monkay_original
    assert type(encoders[0]).__name__ != "AttrsEncoder"
