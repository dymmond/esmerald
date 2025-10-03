from myapp.encoders import AttrsEncoder

from ravyn import Ravyn

app = Ravyn(
    routes=[...],
)
app.register_encoder(AttrsEncoder)
