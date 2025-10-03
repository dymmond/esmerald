import pytest

from ravyn import CORSConfig, Ravyn
from ravyn.exceptions import ImproperlyConfigured
from ravyn.testclient import create_client


def test_raise_error_on_allow_origins(test_client_factory):
    cors_config = CORSConfig()

    with pytest.raises(ImproperlyConfigured):
        with create_client([], allow_origins=["*"], cors_config=cors_config):
            """ """


def test_raise_error_on_allow_origins_ravyn_object(test_client_factory):
    cors_config = CORSConfig()

    with pytest.raises(ImproperlyConfigured):
        Ravyn(allow_origins=["example.com"], cors_config=cors_config)
