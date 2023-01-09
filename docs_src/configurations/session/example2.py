from esmerald import Esmerald, SessionConfig, settings

session_config = SessionConfig(
    secret_key=settings.secret_key,
    session_cookie="session",
)

app = Esmerald(session_config=session_config)
