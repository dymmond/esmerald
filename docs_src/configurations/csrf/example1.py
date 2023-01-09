from esmerald import CSRFConfig, Esmerald, settings

csrf_config = CSRFConfig(
    secret=settings.secret_key,
    cookie_name="csrftoken",
)

app = Esmerald(csrf_config=csrf_config)
