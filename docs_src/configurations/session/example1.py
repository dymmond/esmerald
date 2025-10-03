from ravyn import Ravyn, SessionConfig, settings

session_config = SessionConfig(
    secret_key=settings.secret_key,
)

app = Ravyn(session_config=session_config)
