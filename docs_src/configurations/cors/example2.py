from ravyn import CORSConfig, Ravyn

cors_config = CORSConfig(
    allow_origins=["https://www.example.com", "https://foobar.org"],
    allow_methods=["GET", "POST"],
    allow_credentials=True,
)

app = Ravyn(cors_config=cors_config)
