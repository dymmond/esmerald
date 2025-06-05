from esmerald import Esmerald, EsmeraldSettings


class AppSettings(EsmeraldSettings):
    # default is False
    enable_scheduler: bool = True


app = Esmerald(routes=[...])
