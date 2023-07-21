import pytest

from esmerald import CORSConfig, Esmerald
from esmerald.exceptions import ImproperlyConfigured
from esmerald.testclient import create_client


def test_raise_error_on_allow_origins(test_client_factory):
    cors_config = CORSConfig()

    with pytest.raises(ImproperlyConfigured):
        with create_client([], allow_origins=["*"], cors_config=cors_config):
            """ """


def test_raise_error_on_allow_origins_esmerald_object(test_client_factory):
    cors_config = CORSConfig()

    with pytest.raises(ImproperlyConfigured):
        Esmerald(allow_origins=["example.com"], cors_config=cors_config)
