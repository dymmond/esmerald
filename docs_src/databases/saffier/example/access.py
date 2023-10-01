import httpx

# The password is automatically encrypted when using the
# User model provided by Esmerald
user_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@doe.com",
    "username": "john.doe",
    "password": "johnspassword1234@!",
}

# Create a user
# This returns a 201
async with httpx.AsyncClient() as client:
    client.post("/create", json=user_data)

# Login the user
# Returns the response with the JWT token
user_login = {"email": user_data["email"], "password": user_data["password"]}

async with httpx.AsyncClient() as client:
    response = client.post("/login", json=user_login)

# Access the home '/' endpoint
# The default header for the JWTConfig used is `X_API_TOKEN``
# The default auth_header_types of the JWTConfig is ["Bearer"]
access_token = response.json()["access_token"]

async with httpx.AsyncClient() as client:
    response = client.get("/", headers={"X_API_TOKEN": f"Bearer {access_token}"})

print(response.json()["message"])
# hello john@doe.com
