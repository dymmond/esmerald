from ravyn import Ravyn, RavynSettings


class AppSettings(RavynSettings):
    # default is False
    enable_scheduler: bool = True


app = Ravyn(routes=[...])
