from esmerald import Esmerald, EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    # default is False
    enable_scheduler: bool = True


app = Esmerald(routes=[...])
