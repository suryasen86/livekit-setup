from livekit import api

# Hardcoded API key and secret
API_KEY = "mykey"
API_SECRET = "mysecret"

# Hardcoded participant and room
IDENTITY = "test_user"
NAME = "My Name"
ROOM_NAME = "my-room"

# Create AccessToken
token = (
    api.AccessToken(API_KEY, API_SECRET)
    .with_identity(IDENTITY)
    .with_name(NAME)
    .with_grants(
        api.VideoGrants(
            room_join=True,
            room=ROOM_NAME
        )
    )
)

# Convert to JWT for client
jwt = token.to_jwt()
print("JWT token for client:", jwt)
