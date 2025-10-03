from ravyn import Ravyn
from ravyn.core.datastructures import State

app = Ravyn()

app.state = State({"ADMIN_EMAIL": "admin@example.com"})
