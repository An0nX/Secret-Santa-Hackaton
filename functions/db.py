from datetime import datetime, timedelta
from typing import Union
from fastapi import HTTPException, status
from classes.data import User, TokenData, UserInDB
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

fake_users_db = {"johndoe": {"username": "johndoe", "full_name": "John Doe", "email": "johndoe@example.com", "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", "disabled": False}}

class AuthHandler:
    def __init__(self):
        self.db = fake_users_db
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv('SECRET_KEY')
        self.algorithm = os.getenv('ALGORITHM')

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def get_user(self, email: str):
        if email in self.db:
            user_dict = self.db[email]
            return UserInDB(**user_dict)
        return None

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def get_current_user(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(username=email)
        except JWTError:
            raise credentials_exception
        user = self.get_user(token_data.email)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: User):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
