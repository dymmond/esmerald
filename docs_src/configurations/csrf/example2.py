from esmerald import CSRFConfig, Esmerald, settings

csrf_config = CSRFConfig(
    secret_key=settings.secret_key, session_cookie="csrftoken", header_name="x-csrftoken"
)

app = Esmerald(csrf_config=csrf_config)
