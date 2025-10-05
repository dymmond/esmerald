from ravyn import CSRFConfig, Ravyn, settings

csrf_config = CSRFConfig(
    secret=settings.secret_key,
    cookie_name="csrftoken",
)

app = Ravyn(csrf_config=csrf_config)
