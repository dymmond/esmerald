from ravyn import CSRFConfig, Ravyn, settings

csrf_config = CSRFConfig(
    secret_key=settings.secret_key, session_cookie="csrftoken", header_name="x-csrftoken"
)

app = Ravyn(csrf_config=csrf_config)
