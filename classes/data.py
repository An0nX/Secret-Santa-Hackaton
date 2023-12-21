from pydantic import BaseModel
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None


class User(BaseModel):
    email: str
    name: str
    disabled: bool = False
    interests: str
    gift_preferences: str

class UserRegister(BaseModel):
    email: str
    name: str
    password: str
    interests: str
    gift_preferences: str


class UserInDB(User):
    hashed_password: str
