from esmerald import CORSConfig, Esmerald

cors_config = CORSConfig(
    allow_origins=["www.example.com", "foobar.org"],
    allow_methods=["GET", "POST"],
    allow_credentials=True,
)

app = Esmerald(cors_config=cors_config)
