from esmerald import Esmerald
from esmerald.core.datastructures import State

app = Esmerald()

app.state = State({"ADMIN_EMAIL": "admin@example.com"})
