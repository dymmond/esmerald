from myapp.encoders import AttrsEncoder

from esmerald import Esmerald

app = Esmerald(
    routes=[...],
    encoders=[AttrsEncoder],
)
