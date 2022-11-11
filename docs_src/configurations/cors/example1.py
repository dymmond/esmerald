from esmerald import CORSConfig, Esmerald

cors_config = CORSConfig(
    allow_origins=["https://example.com", "https://foobar.org"], allow_methods=["GET", "POST"]
)

app = Esmerald(cors_config=cors_config)
