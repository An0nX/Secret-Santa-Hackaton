from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str

class RegisterForm(User):
    name: str
    gift_preferences: str
    address: str
    is_student: bool
