from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class ShowUser(BaseModel):
    username: str


class TokenScheme(BaseModel):
    user_id: int
    token: str
