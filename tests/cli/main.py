import os

import pytest

from esmerald import Esmerald
from esmerald.conf import settings

database, models = settings.registry

pytestmark = pytest.mark.anyio

basedir = os.path.abspath(os.path.dirname(__file__))

app = Esmerald(routes=[], on_startup=[database.connect], on_shutdown=[database.disconnect])
