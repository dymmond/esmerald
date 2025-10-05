from ravyn import CORSConfig, Ravyn

cors_config = CORSConfig(
    allow_origins=["https://example.com", "https://foobar.org"], allow_methods=["GET", "POST"]
)

app = Ravyn(cors_config=cors_config)
