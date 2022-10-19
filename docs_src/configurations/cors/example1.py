from esmerald import CORSConfig, Esmerald

cors_config = CORSConfig(
    allow_origins=["example.com", "foobar.org"], allow_methods=["GET", "POST"]
)

app = Esmerald(cors_config=cors_config)
