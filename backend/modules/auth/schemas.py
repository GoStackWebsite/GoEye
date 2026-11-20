from pydantic import BaseModel


# Login request body
class LoginIn(BaseModel):
    email: str
    password: str


# Access token returned after a successful login
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
