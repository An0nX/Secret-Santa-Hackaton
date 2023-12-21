from fastapi.openapi.models import Info
from fastapi.responses import JSONResponse
from datetime import timedelta
from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from classes.data import User, Token, UserInDB, UserRegister
from functions.db import AuthHandler, fake_users_db
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()

auth_handler = AuthHandler()


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = auth_handler.authenticate_user(fake_users_db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    access_token = auth_handler.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/")
async def read_users_me(token: str = Cookie(default=None)):
    user = auth_handler.get_current_user(token=token)
    print(user)
    return JSONResponse(content=user, status_code=status.HTTP_200_OK)


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserRegister, Depends(auth_handler.get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.email}]


@app.post(
    "/register",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "User already exists"},
        500: {"description": "Internal server error"},
    },
)
async def register(user: UserRegister):
    if auth_handler.get_user(username=user.email) is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        hashed_password = auth_handler.get_password_hash(user.password)

        new_user = UserInDB(
            email=user.email,
            name=user.name,
            disabled=False,
            interests=user.interests,
            gift_preferences=user.gift_preferences,
            hashed_password=hashed_password,
        )

        access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
        access_token = auth_handler.create_access_token(
            data={"sub": new_user.email}, expires_delta=access_token_expires
        )

        response = {"message": "User registered successfully"}
        response_headers = {
            "Set-Cookie": f"token={access_token}; HttpOnly; Secure; SameSite=None; Max-Age=600"
        }
        return JSONResponse(content=response, headers=response_headers, status_code=201)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/auth/")
async def read_items(token: Annotated[str, Depends(auth_handler.oauth2_scheme)]):
    return JSONResponse(headers={"Set-Cookie": f"token={token}; Path=/;"})


if __name__ == "__main__":
    openapi_info = Info(
        title="Secret Santa API",
        version="1.0.0",
        description="API for the Secret Santa site",
    )
