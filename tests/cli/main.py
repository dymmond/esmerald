import os

import pytest

from ravyn import Ravyn
from ravyn.conf import settings

database, models = settings.registry

pytestmark = pytest.mark.anyio

basedir = os.path.abspath(os.path.dirname(__file__))

app = Ravyn(routes=[], on_startup=[database.connect], on_shutdown=[database.disconnect])
