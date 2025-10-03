from lilya._internal._encoders import DEFAULT_ENCODER_TYPES

from ravyn.encoders import LILYA_ENCODER_TYPES


def test_working_no_overwrite():
    encoders = LILYA_ENCODER_TYPES.get()
    # assert that it is not the default types
    assert encoders is not DEFAULT_ENCODER_TYPES
    assert type(encoders[0]).__name__ != "AttrsEncoder"
