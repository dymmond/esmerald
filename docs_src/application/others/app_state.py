from esmerald import Esmerald
from esmerald.datastructures import State

app = Esmerald()

app.state = State({"ADMIN_EMAIL": "admin@example.com"})
