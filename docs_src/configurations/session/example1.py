from esmerald import Esmerald, SessionConfig, settings

session_config = SessionConfig(
    secret_key=settings.secret,
)

app = Esmerald(session_config=session_config)
